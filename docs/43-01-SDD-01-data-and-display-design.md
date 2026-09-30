# Data and display detailed design

Status: working draft / focused detailed design

Software item: **SI-01 — Timing Point Application**

This SDD explains **how the data flows inside SI-01**: how LogBook entries are
recorded, when a TimingData record is committed, how restart/recovery works, and
how queries, prepare-team data and display data use that state.

The SSD still defines the architecture. IF-05 still defines the TimingData
record/file format. SDD-02 chooses the concrete Java classes, queues and worker
threads.

The first version does **not** need an embedded database. Committed LogBook
entries are written as append-only IF-05 TimingData. After a restart, SI-01 can
read those records back and rebuild the LogBook. Other state, such as RaceData or
prepare-team state, can use its own simpler backup/sync mechanism.

Identifiers and known ranges come from `03-domain-baseline.md`. This SDD only
describes how SI-01 uses them.

## Design scope and data ownership

### Two traceable information models

Two information flows must not be conflated:

1. **registration stream/ledger** — timing and operational entries that are synchronised as an ordered source stream;
2. **prepare-team registry history/state** — keypad/operator actions that prepare/remove teams and drive current display state.

Both need traceability and persistence, but they have different semantics and sequence scopes.

### TimingNode source and location identity

Every `TimingNode` has a `TimingNodeId`.

Known source classes are:

```text
normal registration systems   A..I
reserve registration systems  1..4 (exact identifier representation TBD)
virtual registration systems  exist; exact identifier representation TBD
```

Every physical location has:

```text
LocationID = 1..25
```

A registration entry is associated with both its source and its location.

`TimingNodeId`, `LocationID` and `AntennaId` are separate namespaces. I/O configuration relates antenna observations to TimingNodes; code must not infer one identity from another.

### LogBook versus IF-05 TimingData

The runtime `LogBook` stores 0..N `LogBookItem` entries used by SI-01.
A `LogBookItem` does not have to look exactly like the IF-05 record written to
file or sent elsewhere.

The system-owned **IF-05 TimingData Interchange** contract is defined by
`32-05-IDD-timingdata-interchange.md`. That IDD is authoritative for
`TimingDataRecord` field semantics, record kinds, `RegistrationIdentity`,
record keys/sequences, versioning and canonical file encoding.

This SDD does not repeat the IF-05 field table. It only explains how SI-01 gets
from a LogBook change to a committed IF-05 record.

The runtime `LogBook` remains free to use a different internal representation.
A `TimingDataProvider` is an edge translation mechanism and does not move
external/proprietary wire/file semantics into the SI-01 domain model.

### Tag, team and registration identity resolution

Decoded team numbers are in the known range:

```text
TeamNumber = 0..999
```

A decoded physical RFID identity contains:

```text
prefix + number + postfix
```

The registration path normalises it to:

```text
RegistrationTag = prefix + number
```

The postfix/copy suffix, when present, is deliberately removed from the
registration identity; the prefix is retained so normal and reserve tags remain
distinguishable. Finish-side tag representations are allowed to have no postfix,
so parsing/normalisation shall not require one globally.

All participant registrations are committed with one canonical
`RegistrationIdentity`.

Automatic path:

```text
TagIdentity
  normal  -> deterministic registration-identity translation
  reserve -> RaceData-backed reserve translation
       -> RegistrationIdentity
```

Manual path:

```text
TeamIdentity
  -> UI/application registration-identity translation
  -> RegistrationIdentity
```

The canonical `RegistrationIdentity` type/number values, ranges and location
compatibility are defined by IF-05. SI-01 identity-resolution code consumes that
contract; it does not maintain a second independent type table.

A proprietary translator may map the IF-05 identity to/from its external split
representation, but external one-character codes remain outside SI-01 domain
semantics.

Reserve transponders remain a `TagIdentity` concern and resolve to an IF-05
canonical `RegistrationIdentity`; they do not add another public registration
identity type.

Source identities such as `TagIdentity` may be retained/exposed separately when
an interface needs provenance or diagnostics; they are not substitutes for the
canonical registration identity stored by TimingData.

## LogBook recording and TimingData persistence

### Producers and LogBookEntryCandidate

RFID is only one producer of traceable LogBook facts. Manual registration,
TimingNode lifecycle handling and later start/penalty/correction logic use the
same commit boundary.

The common pre-commit hand-off is conceptually a `LogBookEntryCandidate`:

```text
LogBookEntryCandidate
  timingNodeId
  locationId              immutable location snapshot for this fact
  semantic kind / domain data
  effectiveTime

  no sequenceNumber
  no recordedAt
  not yet committed
```

The producer owns the business meaning and captures the TimingNode/location
context applicable to the fact before enqueue. The commit path owns sequence,
`recordedAt`, LogBookItem creation, IF-05 conversion and durability.

For a revocation candidate, the producer carries the original registration's
location, effective time, registration identity, origin and time source as
required by IF-05 rather than using a newer/current TimingNode configuration.

Current and expected producers include:

| Producer | Example LogBook fact | Status |
| --- | --- | --- |
| `TagProcessor` | automatic participant registration | first v1 slice |
| manual registration command path | manual participant registration/revocation | first v1 slice |
| TimingNode lifecycle handling | OPEN/CLOSED state fact | first v1 slice |
| start procedure/domain logic | start-related fact | later record family |
| penalty/correction domain logic | penalty/correction fact | later record family |

A producer shall not assign the persistent sequence, write the TimingData file,
publish an uncommitted fact or depend on the physical IF-05 representation.

![LogBook producers and durable TimingData commit path](../../../raw/prod/docs/assets/architecture/timingdata-producer-pipeline.svg)

*Figure SDD01-TD01 — Multiple producers converge on one ordered LogBook commit path; IF-05 TimingData is the durable/interchange representation.*

### Ordered durable commit

The first implementation uses one serial record lane per TimingNode. The
**TimingNode owns that lane**: its bounded queue, its asynchronous record worker
and the ordered commit step. Producers such as `TagProcessor` submit a
`LogBookEntryCandidate` to their owning TimingNode and return without waiting
for file I/O.

Conceptually:

```java
boolean submit(LogBookEntryCandidate candidate) {
    return logBookQueue.offer(candidate);
}

void runRecordWorker() {
    while (running) {
        LogBookEntryCandidate candidate = logBookQueue.take();
        commitCandidate(candidate);
    }
}

CommittedLogBookItem commitCandidate(LogBookEntryCandidate candidate) {
    long sequence = sequenceState.peekNext(candidate.timingNodeId());
    TimingTimestamp recordedAt = timeSource.now();

    LogBookItem item =
        logBookItemFactory.create(candidate, sequence, recordedAt);

    TimingDataRecord record = timingData.toRecord(item);

    timingDataStore.append(record);   // durable IF-05 append
    sequenceState.commit(sequence);   // sequence now consumed
    logBook.commit(item);             // operational Domain state now visible
    committedSinks.publish(record);   // non-blocking hand-off only

    return new CommittedLogBookItem(item, record);
}
```

This does not require separate architectural components called
`LogBookRecorder` or `LogBookCommitter`. If small private helper methods or
classes later make the Java code easier to maintain, SDD-02 may introduce them
as implementation details without changing TimingNode ownership.

`recordedAt` is captured immediately before the definitive record is encoded
for the append attempt; it is metadata rather than the durability marker.

If the durable append fails, sequence state and LogBook state do not advance and
a later candidate may not overtake the failed one. A partial failed append is
repaired/truncated to the last complete IF-05 line boundary before retry.

This separates the two representations without introducing a second domain
history component:

```text
LogBookItem       internal operational Domain representation
TimingDataRecord  persistent/interchange IF-05 representation
```

### Asynchronous execution and query isolation

The first Pi-oriented implementation needs only **one mandatory asynchronous
queue** in the LogBook commit path, and that queue belongs to the TimingNode:

```text
TagProcessor / command / lifecycle / later producer
                    |
                    | submit LogBookEntryCandidate
                    v
                TimingNode
                    |
                    | async enqueue
                    v
        internal bounded ArrayBlockingQueue
                    |
                    | next candidate
                    v
        TimingNode record worker
              /           \
             /             \
            v               v
   TimingDataStore       LogBook
   file persistence      Domain state
   / recovery
            |               |
            |               +----> short read/capture ----> query/ranking task
            |
            +----> CommittedTimingDataSink
                       |
                       +----> async signalling / upstream worker
```

There is no second queue between durable commit and LogBook state. The LogBook
update is short and synchronous after the IF-05 append succeeds.

A long-running query does not run on the TimingNode record worker and does not
require a deep copy of the complete LogBook. It captures only the small immutable
references/index/version boundary required by the real query, releases any short
synchronisation, and performs expensive calculation elsewhere.

Slow network signalling/retry is different: it may block independently and
therefore sits behind its own capability-specific bounded queue or outbox.

![TimingNode asynchronous ownership and query isolation](../../../raw/prod/docs/assets/architecture/timingdata-async-ownership.svg)

*Figure SDD01-TD02 — The TimingNode owns one bounded ingress queue and record worker; queries and external delivery execute independently.*

### Runtime flows

Each flow below has a compact UML-style sequence overview followed by the more
precise developer pseudocode. The diagram is for quickly seeing participants and
async/sync boundaries; the text block underneath carries the method and commit
details.

#### Automatic RFID registration

![Automatic RFID registration sequence](../../../raw/prod/docs/assets/architecture/timingdata-sequence-auto-registration.svg)

*Figure SDD01-TD03 — TagProcessor hands a candidate to its TimingNode, which queues it and later performs the durable commit.*

```text
RFID adapter       TagProcessor        TimingNode        internal queue       TimingDataStore       LogBook
    |                   |                  |                   |                      |                  |
    | observation       |                  |                   |                      |                  |
    |------------------>|                  |                   |                      |                  |
    |                   | normalize/resolve|                   |                      |                  |
    |                   | buildCandidate() |                   |                      |                  |
    |                   | submit(candidate)|                   |                      |                  |
    |                   |----------------->|                   |                      |                  |
    |                   |                  | enqueue           |                      |                  |
    |                   |                  |------------------>|                      |                  |
    |                   |<-----------------| accepted          |                      |                  |
    |                   |                  |                   |                      |                  |
    |                   |                  |<------------------| next candidate       |                  |
    |                   |                  | create item/record|                      |                  |
    |                   |                  | append(record)    |                      |                  |
    |                   |                  |----------------------------------------->|                  |
    |                   |                  |<-----------------------------------------| durable          |
    |                   |                  | commit(item)      |                      |                  |
    |                   |                  |----------------------------------------------------------->|
```

The RFID callback is free after enqueue. File latency therefore does not occupy
the antenna/`TagProcessor` execution context.

#### Manual registration

![Manual registration sequence](../../../raw/prod/docs/assets/architecture/timingdata-sequence-manual-registration.svg)

*Figure SDD01-TD04 — IF-03 hands operator input to the TimingNode; acceptance returns after enqueue, before durable file handling.*

```text
Client          IF-03/CommandHandler        TimingNode        internal queue       TimingDataStore       LogBook
  |                       |                    |                    |                      |                  |
  | TeamIdentity + time   |                    |                    |                      |                  |
  |---------------------->|                    |                    |                      |                  |
  |                       | register(...)      |                    |                      |                  |
  |                       |------------------->|                    |                      |                  |
  |                       |                    | resolve identity   |                      |                  |
  |                       |                    | build candidate    |                      |                  |
  |                       |                    | enqueue            |                      |                  |
  |                       |                    |------------------->|                      |                  |
  |                       |<-------------------| accepted           |                      |                  |
  |<----------------------| accepted           |                    |                      |                  |
  |                       |                    |<-------------------| next candidate       |                  |
  |                       |                    | append IF-05 record                       |                  |
  |                       |                    |------------------------------------------>|                  |
  |                       |                    |<------------------------------------------| durable          |
  |                       |                    | commit LogBookItem  |                      |                  |
  |                       |                    |----------------------------------------------------------->|
```

The client supplies operator input; the TimingNode resolves the canonical IF-05
`RegistrationIdentity`. Automatic and manual paths therefore differ before the
candidate is enqueued but share the same TimingNode-owned queue and ordered
commit semantics afterwards.

#### Long query while registrations continue

![LogBook query isolation sequence](../../../raw/prod/docs/assets/architecture/timingdata-sequence-query-isolation.svg)

*Figure SDD01-TD05 — A query can continue while another registration is queued and committed by the TimingNode record worker.*

```text
Query task              LogBook         Registration producer       TimingNode       internal queue
   |                       |                     |                       |                  |
   | capture read view     |                     |                       |                  |
   |---------------------->|                     |                       |                  |
   |<----------------------| view                |                       |                  |
   | calculate...          |                     | submit candidate      |                  |
   |                       |                     |---------------------->|                  |
   | calculate...          |                     |                       | enqueue          |
   |                       |                     |                       |----------------->|
   |                       |                     |<----------------------| accepted         |
   | calculate...          |                     |                       |<-----------------| next candidate
   |                       |<--------------------------------------------| commit item      |
   | calculate...          |                     |                       |                  |
   | return result         |                     |                       |                  |
```

The calculation does not keep a long LogBook lock and does not require a deep
copy of all registrations. The exact compact read/index strategy is selected
when the first real ranking/query implementation is built and measured on the
target Raspberry Pi.

#### Later producers

![Generic LogBook producer sequence](../../../raw/prod/docs/assets/architecture/timingdata-sequence-generic-producer.svg)

*Figure SDD01-TD06 — Later start, penalty and correction logic submit candidates to the same TimingNode-owned queue and commit path.*

Start-procedure and penalty/correction logic follow the same pattern:

```text
domain-specific business logic
          |
          | LogBookEntryCandidate
          v
      TimingNode
          |
          v
internal bounded queue
          |
          v
TimingNode record worker
          |
          +--> TimingDataStore (file persistence / recovery)
          +--> LogBook
```

Their exact LogBookItem/IF-05 record families remain deferred until the
applicable requirements are promoted.

#### Thread/ownership responsibilities

| Execution role | May block on | Must not block |
| --- | --- | --- |
| producer/caller | short domain work + bounded TimingNode enqueue policy | durable file I/O, long query, network delivery |
| TimingNode record worker | ordered local durable append | long query, client rendering, network retry |
| TimingNode commit step | short in-memory mutation after durable append | long report/ranking calculation |
| query worker/caller | its own calculation/read workload | TimingNode record progress |
| signalling/upstream worker | its own delivery/retry policy | TimingNode commit |

For the first one-TimingNode application each TimingNode owns one bounded queue
and one dedicated record worker. A later multi-node implementation may share
worker infrastructure only if it preserves independent FIFO commit order per
TimingNode.

## TimingData persistence and recovery

### Recovering the next sequence

We do not need a separate sequence-counter file in the first implementation.
The TimingData file already tells us the last committed sequence:

```text
no committed records       -> nextSequence = 1
last committed sequence N  -> nextSequence = N + 1
```

At startup:

- read complete IF-05 records in order;
- check that the file belongs to one TimingNode;
- check that the committed sequence increases without duplicates or unexpected gaps;
- ignore/remove only a half-written final record that has no complete line ending;
- never reuse a committed `(TimingNodeId, SequenceNumber)`.

A half-written **last** record after power loss is recoverable: truncate back to
the last complete record and continue from there.

A corrupt **complete** record, duplicate sequence or gap is different. Do not
silently skip or renumber it. Stop recovery for that TimingNode and report the
problem so support/operator tooling can see it.

If we later add a cached sequence-counter file for faster startup, it is only a
cache. The committed TimingData file remains the source used to check/rebuild it.

### What must survive a restart

TimingData has the strongest persistence rule:

- a timing record counts as committed only after the complete IF-05 record has
  been written successfully;
- only then is its sequence consumed and the matching LogBook item made visible;
- the TimingData file is used to rebuild the LogBook after restart.

Other state can use simpler mechanisms:

- prepare-team/NextUpTeams may use a small snapshot or its own history;
- StageStartTimes and RaceData may cache the last accepted external version;
- display/read data can normally be rebuilt and does not need its own durable copy.

Implementation hints to verify on the target Pi:

- what exact flush/fsync call is needed before we call a record durable;
- what happens if power disappears halfway through the final line;
- whether truncating the incomplete tail is atomic/safe on the target filesystem;
- how we report a corrupt file instead of quietly starting with empty state;
- when files need rotation/retention so they do not grow forever.

We do not need a database just to solve these cases.

Status should eventually show useful support information such as:

```text
TimingData file / recovery health
last committed sequence per TimingNode
LogBook ingress queue depth/high-water
last LogBook rebuild result
reference-data synchronisation time/version
other-state backup/recovery health
```

### Startup flow

The first startup flow is intentionally straightforward:

```text
start process
   |
   v
load configuration
   |
   v
open TimingData file for each configured TimingNode
   |
   v
read and validate complete IF-05 records
   |
   +--> half-written final line: truncate to last complete record + report
   |
   +--> corrupt complete record / duplicate / gap: recovery error, do not append
   |
   v
nextSequence = last committed sequence + 1
   |
   v
rebuild LogBook
   |
   v
load other saved/reference state
   |
   v
start interfaces/devices
   |
   v
connect/synchronise upstream when available
```

A new/empty TimingData file starts at sequence 1.

Rebuilding the LogBook does **not** automatically reopen a TimingNode. For
example, if the last historical state record says `OPEN`, a process restart must
not start accepting new observations merely because that old record exists. The
open/closed restart policy belongs to lifecycle/control requirements.

If prepare-team or reference-data backup is corrupt, report that explicitly too;
do not silently present the system as healthy.

## Prepare-team and reference data

### Prepare-team registry

Keypad input indicates which teams should prepare at the timing node/exchange point. A keypad action is not itself a passage/start/penalty registration.

The keypad can:

```text
add team to prepare registry
remove team from prepare registry
```

Those actions must remain traceable so operator history is auditable and the registry can be recovered after restart.

Conceptually:

```text
PrepareTeamRegistry
  current teams to prepare: [456]

  internal traceable history:
    501  TEAM_ADDED     123
    502  TEAM_ADDED     456
    503  TEAM_REMOVED   123
```

The registry owns both:

- **current state** — which teams must currently prepare at the timing node/exchange point;
- **traceable history** — the keypad/operator add/remove mutations needed for audit and restore.

The history is an internal persistence/state aspect of the registry, not a separate architecture component.

Illustrative internal history record:

```java
final class PrepareTeamEvent {
    private long sequenceNumber;
    private TimingNodeId timingNodeId;
    private PrepareTeamEventType type; // ADDED / REMOVED
    private TeamNumber teamNumber;
    private Instant createdAt;
    private InputSource source;         // keypad / UI / API / test
}
```

The prepare-team history sequence is a separate design question from the `TimingNodeId`-scoped sequence. It may use its own internal registry sequence or later a broader operational-event sequence, but it must not accidentally consume/alter a `TimingNodeId` registration sequence unless requirements explicitly make a prepare-team action a registration-stream entry.

### Start-time and reserve-tag synchronisation

Start times and reserve-tag mappings are backoffice-owned reference data that must also be available locally.

The start-time semantic model must remain compatible with sources that define a race/stage start as **time-of-day only**. An optional date/race-day value may be carried when available, but consumers shall not require it. Accepted registration observations remain absolute `TimingTimestamp` values. For elapsed-time calculation, a time-only start is resolved in the configured event/race time zone to the most recent valid occurrence not after the registration timestamp, so a midnight crossing is handled as the next civil day rather than as a negative elapsed time.

The application maintains local in-memory repositories and synchronises accepted data from the backoffice.

A useful model is snapshot/version based:

```text
Backoffice
   |
   | ReferenceDataSnapshot(version, entries)
   v
Backoffice adapter
   |
   v
TimingSystem/application message queue
   |
   v
ReferenceDataService
   |
   +--> validate version/content
   +--> replace/update repositories
   +--> write simple backup file
   +--> publish status/data-changed event
```

Pseudocode:

```java
void handle(StartTimeSnapshotReceived message) {
    StartTimeSnapshot incoming = message.getSnapshot();

    if (!startTimeValidator.accept(incoming, startTimes.snapshot())) {
        status.referenceData().recordRejectedUpdate(incoming.getVersion());
        return;
    }

    startTimes.replace(incoming);
    referenceBackup.save(referenceData.snapshot());
    status.referenceData().recordStartTimesSynced(incoming.getVersion());
    displayService.referenceDataChanged();
}
```

The same pattern applies to reserve-tag conversion data. Full-snapshot versus delta updates, version identifiers and correction semantics still need requirements/IDD design.

### Keypad behaviour

The CAN keypad can both add and remove team numbers from prepare-team registry.

Possible incoming messages:

```text
KeypadTeamAddRequested(teamNumber)
KeypadTeamRemoveRequested(teamNumber)
```

Both enter the normal serialized state-change path. The handler mutates `PrepareTeamRegistry`; the registry records the traceable mutation and updates its current set atomically from the application/domain point of view. The handler then rebuilds/publishes display data.

```java
void handle(KeypadTeamAddRequested command) {
    prepareTeams.add(
        command.getTeamNumber(),
        KEYPAD,
        clock.instant());

    backupCoordinator.prepareTeamsChanged(prepareTeams);
    displayService.prepareTeamsChanged(prepareTeams.currentTeams());
}
```

Removing a team follows the same path with `REMOVED`.

The application, not the keypad, remains authoritative for current prepare-team registry. Duplicate-add, remove-not-present, ordering and capacity behaviour need explicit requirements.

## Display data

### Display model

Display data is derived from **current state**, not by forwarding keypad history directly.

```text
PrepareTeamRegistry         StageStartTimeRegistry
      |                          |
      +--------------------------+
      |                          |
      +----> DisplayModelBuilder <+
                    |
                    v
              DisplayModel
              /          \
             v            v
      V1 CAN adapter    V2 data session
```

![In-memory data, backup and V1/V2 display behaviour](../../../raw/prod/docs/assets/architecture/data-display-flow.svg)

A conceptual model might contain:

```java
final class DisplayModel {
    private List<TeamDisplayData> prepareTeams;
    private Instant generatedAt;
    private long revision;
}

final class TeamDisplayData {
    private TeamNumber teamNumber;
    private StartTime startTime;
    private Duration elapsedTime;
    private LocalRank rank;
}
```

Fields are illustrative. The display IDD will ultimately define the system contract.

### Display V1 — passive CAN display

Display V1 is relatively passive and must be actively driven by the timing application.

V1 does not reconstruct add/remove history. The application derives the **current prepare-team list** and writes the appropriate complete/current display state.

```java
void refreshV1() {
    DisplayModel current = displayModelService.current();
    canDisplayV1.apply(current);
}
```

Implications:

- `TEAM_ADDED` updates `PrepareTeamRegistry`, then triggers a refreshed current list;
- `TEAM_REMOVED` updates `PrepareTeamRegistry`, then triggers a refreshed current list;
- after discovery/reconnect/reset, send a full refresh from current state;
- a V1 reset does not destroy application prepare-team registry;
- status distinguishes discovered/reachable/last successfully updated.

### Display V2 — smart Wi-Fi display

Display V2 is a smarter network client. The timing application communicates domain/display **data**, while V2 owns presentation/rendering behaviour.

Intended connection direction:

1. timing application advertises an mDNS service;
2. V2 discovers the service;
3. V2 connects to the timing application;
4. application sends current ready-team/reference/result data;
5. application and V2 keep data synchronised while connected.

The data can be represented as a revisioned snapshot/model even though V2 renders it differently from V1.

```java
void onDisplayV2Connected(DisplaySession session) {
    session.send(displayModelService.current());
}
```

A later optimisation may send deltas, but reconnect must always be recoverable through a complete current snapshot.

### Registration versus ready-team display state

These flows remain separate:

```text
RFID / manual / lifecycle / later start / penalty logic
          |
          v
 LogBookEntryCandidate
          |
          v
      LogBook commit
          |
          +--> StageTiming / ranking inputs
          +--> IF-05 TimingData / downstream integration

keypad/UI prepare/remove team
          |
          v
    PrepareTeamRegistry
      current state + internal history
          |
          +--> V1 current list
          +--> V2 synchronised data
```

A team can be ready for display without having produced a registration, and a registration can exist independently from whether that team is currently ready.

Later interactions (for example automatically removing a team after a successful start/passage) must be explicit domain requirements rather than accidental display side effects.

## Rules when implementing IF-05

The TimingData record/file contract is not re-specified here. SI-01 design shall
conform to **IF05-REQ-001..015** in
`32-05-IDD-timingdata-interchange.md`.

The following temporary design constraints cover only the internal realisation
needed around that interface:

### Record pipeline

- **CAND-PIPE-001** — Traceable domain/application producers shall hand an
  immutable `LogBookEntryCandidate` to the owning TimingNode, which shall place
  it on its bounded internal LogBook queue; durable file I/O shall not execute
  on RFID/device/operator ingress callbacks.
- **CAND-PIPE-002** — The record-commit path shall publish an IF-05 record to
  downstream consumers only after the complete local record is durably appended
  and its sequence is committed.
- **CAND-PIPE-003** — After durable IF-05 append, the commit path shall apply the
  corresponding `LogBookItem` synchronously to the owning TimingNode LogBook
  before external publication.
- **CAND-PIPE-004** — Potentially long queries and network delivery/retry shall
  execute outside the TimingNode record worker; only slow external delivery
  requires an additional asynchronous queue/outbox boundary.

### Identity resolution before IF-05 commit

- **CAND-ID-001** — The RFID path shall normalise physical tag input to the
  `TagIdentity` form required for registration-identity resolution.
- **CAND-ID-002** — The RFID path shall distinguish normal versus reserve-tag
  semantics before creating a LogBook entry candidate.
- **CAND-ID-003** — A normal `TagIdentity` shall resolve deterministically to
  the IF-05 `RegistrationIdentity`; a reserve `TagIdentity` shall resolve
  through locally available race/reference mapping data.
- **CAND-ID-004** — Manual registration shall resolve operator-supplied
  `TeamIdentity` to the same IF-05 `RegistrationIdentity` used by automatic
  registrations.
- **CAND-ID-005** — Physical tag postfix/copy detail, when present, shall not be
  carried into IF-05 `RegistrationIdentity`; parsing shall not require a
  postfix globally.

### Local data and backup

- **CAND-DATA-001** — The initial implementation shall maintain committed
  LogBook state, ready-team state and reference state in typed application data
  structures without requiring an external database engine.
- **CAND-DATA-002** — The per-TimingNode LogBook shall own operational committed
  history/state; the append-only IF-05 TimingData file shall provide its durable
  recovery representation and sequence-recovery source.
- **CAND-DATA-003** — TimingData recovery faults and other persistent-state
  backup/restore failures shall be represented explicitly in system status.
- **CAND-DATA-004** — The local start-time data set shall be synchronisable from the backoffice and remain available after loss of live backoffice connectivity.
- **CAND-DATA-005** — The system shall track enough reference-data synchronisation metadata to determine whether local data is current/stale relative to the latest accepted update.

### Ready-team/keypad data

- **CAND-READY-001** — The system shall maintain prepare-team registry logically separate from timing/registration records.
- **CAND-READY-002** — Adding or removing a team from prepare-team registry shall create a traceable persisted ready-team event.
- **CAND-READY-003** — Ready-team events shall be processed through the normal controlled state-change path.
- **CAND-READY-004** — Prepare-team registry state shall be recoverable after application restart from locally persisted information.
- **CAND-READY-005** — The keypad shall be able to request both addition and removal of a team number.

### Displays

- **CAND-DISP-004** — The application shall derive display data from current timing/reference/prepare-team registry rather than requiring displays to reconstruct operational event history.
- **CAND-DISP-005** — Display V1 shall be actively controlled by the application and shall receive current ready-team display state/list after relevant changes or reconnect.
- **CAND-DISP-006** — Display V2 shall consume synchronised timing/ready-team/reference data from the application and shall own local presentation/rendering behaviour.
- **CAND-DISP-007** — When Display V2 connects or reconnects, the application shall be able to provide a complete current data snapshot independent of previously delivered incremental updates.
- **CAND-DISP-008** — Display data shall support a revision/version mechanism or equivalent means of detecting stale/missed state.

## Open questions

- What exact identifiers represent reserve registration systems `1..4` in software/wire formats?
- What exact identifiers represent virtual registration systems?
- Is each physical producer configured with exactly one `TimingNodeId`, and how are reserve/virtual TimingNodes associated with registration hardware?
- What exact filesystem durability primitive/policy is required before a completed append is considered durable on each deployment platform?
- Which additional producer/domain paths should emit future IF-05 record families after their requirements are promoted?
- Should ready-team events use their own sequence stream or a broader operational event sequence?
- Should ready-team recovery use an append persistent file, a current-state snapshot, or both?
- How frequently may simple backup files be written without unnecessary SD-card wear?
- Should reference data use one combined backup snapshot or separate files per data set?
- Is start-time synchronisation always a full snapshot, or can the backoffice send deltas/corrections?
- What is the keypad protocol for distinguishing add versus remove?
- What should happen on duplicate add or removal of a team that is not ready?
- Is ready-team ordering significant and, if so, is it insertion order, start-time order, or another rule?
- How many teams can be ready concurrently?
- Should a successful start/passage automatically affect the prepare-team list, or must that always be an explicit action?
- Does V1 retain any useful state across reconnect/power interruption or must every connection be treated as blank/unknown?
- What exact data fields does V2 need, and which presentation decisions belong exclusively inside V2?

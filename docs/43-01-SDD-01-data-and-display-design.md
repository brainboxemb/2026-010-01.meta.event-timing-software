# Data and display detailed design

Status: working draft / non-authoritative

Software item: **01 — Headless Timing Application**

This document refines SI-01 data ownership and runtime processing for TimingData,
prepare-team state, reference data and the two display generations.

The initial design does **not** require a conventional embedded database.
Committed LogBook state is persisted through the append-only IF-05 TimingData
representation and rebuilt from that durable representation after restart. Other
operational/reference state uses its own persistence or synchronisation
mechanism as defined below.

Domain identifiers and known ranges are captured in `03-domain-baseline.md`. This SDD translates those facts into software/data-design direction.

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

The runtime `LogBook` owns operational state as 0..N `LogBookItem` values.
Those items are domain state and do not have to be shaped like the representation
used outside the LogBook.

The system-owned **IF-05 TimingData Interchange** contract is defined by
`32-05-IDD-timingdata-interchange.md`. That IDD is authoritative for
`TimingDataRecord` field semantics, record kinds, `RegistrationIdentity`,
record keys/sequences, versioning and canonical file encoding.

This SDD deliberately does **not** repeat that external/file contract. It defines
how SI-01 produces and commits IF-05 records internally.

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

The first implementation uses one serial commit lane per TimingNode. The
`TagProcessor` and other producers only enqueue candidates.

Conceptually:

```java
void submit(LogBookEntryCandidate candidate) {
    logBookQueue.add(candidate);
}

CommittedLogBookItem commitNext(LogBookEntryCandidate candidate) {
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
queue** in the LogBook commit path:

```text
TagProcessor / manual / lifecycle / later producers
                    |
                    | LogBookEntryCandidate
                    v
        bounded ArrayBlockingQueue
                    |
                    v
             LogBookRecorder
             worker thread
                    |
                    v
             LogBookCommitter
              /           \
             /             \
            v               v
   TimingDataStore       LogBook
   durable IF-05         Domain state
            |               |
            |               +----> short read/capture ----> query/ranking worker
            |
            +----> CommittedTimingDataSink
                       |
                       +----> async signalling / upstream worker
```

There is no second queue between durable commit and LogBook state. The LogBook
update is short and synchronous after the IF-05 append succeeds.

A long-running query does not run on the recorder worker and does not require a
deep copy of the complete LogBook. It captures only the small immutable
references/index/version boundary required by the real query, releases any short
synchronisation, and performs expensive calculation elsewhere.

Slow network signalling/retry is different: it may block independently and
therefore sits behind its own capability-specific bounded queue or outbox.

![LogBook asynchronous ownership and query isolation](../../../raw/prod/docs/assets/architecture/timingdata-async-ownership.svg)

*Figure SDD01-TD02 — One bounded ingress queue isolates producers from durable commit; queries and external delivery do not occupy the LogBook recorder worker.*

### Runtime flows

The following text sequences are intentionally kept in the SDD instead of being
turned into separate pictures. At this level the method/ownership detail is more
useful in source form and remains directly reviewable in Git.

#### Automatic RFID registration

```text
RFID adapter          TagProcessor          LogBookRecorder       LogBookCommitter       TimingDataStore       LogBook
    |                      |                       |                     |                       |                  |
    | onObservation(obs)   |                       |                     |                       |                  |
    |--------------------->|                       |                     |                       |                  |
    |                      | normalizeTag()        |                     |                       |                  |
    |                      | resolveIdentity()     |                     |                       |                  |
    |                      | buildCandidate()      |                     |                       |                  |
    |                      | submit(candidate)     |                     |                       |                  |
    |                      |---------------------->|                     |                       |                  |
    |                      | returns immediately   |                     |                       |                  |
    |                      |                       | take()              |                       |                  |
    |                      |                       |-------------------->|                       |                  |
    |                      |                       |                     | create LogBookItem()  |                  |
    |                      |                       |                     | toTimingDataRecord()  |                  |
    |                      |                       |                     | append(record + LF)   |                  |
    |                      |                       |                     |---------------------->|                  |
    |                      |                       |                     |<----------------------| durable          |
    |                      |                       |                     | commit(item)          |                  |
    |                      |                       |                     |------------------------------------------>|
```

The RFID callback is free after enqueue. File latency therefore does not occupy
the antenna/`TagProcessor` execution context.

#### Manual registration

```text
Client             IF-03/CommandHandler      Manual registration       LogBookRecorder       LogBookCommitter
  |                         |                         |                        |                    |
  | TeamIdentity + time     |                         |                        |                    |
  |------------------------>|                         |                        |                    |
  |                         | validate command        |                        |                    |
  |                         |------------------------>|                        |                    |
  |                         |                         | resolve RegistrationIdentity                |
  |                         |                         | determine origin/timeSource/effectiveTime    |
  |                         |                         | buildCandidate()       |                    |
  |                         |                         | submit(candidate)      |                    |
  |                         |                         |----------------------->|                    |
  |                         |<------------------------| accepted               |                    |
  |<------------------------| accepted                |                        |                    |
  |                         |                         |                        | take()             |
  |                         |                         |                        |------------------->|
  |                         |                         |                        |   same durable commit path...
```

The client supplies operator input; SI-01 resolves the canonical IF-05
`RegistrationIdentity`. Automatic and manual paths therefore differ before the
candidate is enqueued but share the same ordered commit semantics afterwards.

#### Long query while registrations continue

```text
Client/query thread                 LogBook                    LogBookRecorder/Committer
       |                               |                                  |
       | acquire small read view       |                                  |
       |------------------------------>|                                  |
       |<------------------------------| refs/index + sequence boundary   |
       |                               |                                  |
       | calculate/rank...             |             next candidate       |
       |--------------------           |                                  |
       |                               |<---------------------------------|
       | calculate/rank...             |             durable commit       |
       |                               |<---------------------------------|
       | calculate/rank...             |                                  |
       | return result                 |                                  |
```

The calculation does not keep a long LogBook lock and does not require a deep
copy of all registrations. The exact compact read/index strategy is selected
when the first real ranking/query implementation is built and measured on the
target Raspberry Pi.

#### Later producers

Start-procedure and penalty/correction logic follow the same pattern:

```text
domain-specific business logic
          |
          v
LogBookEntryCandidate
          |
          v
bounded LogBook queue
          |
          v
same LogBookCommitter + IF-05 persistence
```

Their exact LogBookItem/IF-05 record families remain deferred until the
applicable requirements are promoted.

#### Thread/ownership responsibilities

| Execution role | May block on | Must not block |
| --- | --- | --- |
| producer task | short domain work + bounded enqueue policy | durable file I/O, long query, network delivery |
| LogBook recorder worker | ordered local durable append | long query, client rendering, network retry |
| LogBook commit/update | short in-memory mutation after durable append | long report/ranking calculation |
| query worker/caller | its own calculation/read workload | LogBook recorder progress |
| signalling/upstream worker | its own delivery/retry policy | LogBook commit |

For the first one-TimingNode application the LogBook recorder owns one dedicated
worker thread. A later multi-node implementation may share workers only if it
preserves independent FIFO commit order per TimingNode.

## TimingData persistence and recovery

### Sequence recovery from the TimingData file

Sequence allocation is a domain consistency mechanism, not merely an in-memory
counter.

For the first append-only implementation, the authoritative per-TimingNode
TimingData file is also sufficient to recover the committed sequence state:

```text
no committed records       -> nextSequence = 1
last committed sequence N  -> nextSequence = N + 1
```

Recovery rules:

- scan only complete line-terminated IF-05 records;
- validate that the file contains one TimingNode stream and a contiguous,
  increasing committed sequence;
- an unterminated trailing record is not committed;
- before normal appends resume, truncate/repair that incomplete tail back to the
  last complete committed line boundary so a retry cannot be concatenated onto
  partial bytes;
- an invalid complete record, duplicate, regression or unexpected sequence gap
  in the authoritative local source file is an explicit recovery fault; do not
  silently skip/renumber it and then continue writing as if the stream were
  healthy;
- never reuse a committed `(TimingNodeId, SequenceNumber)`;
- expose source + last committed sequence in support/status data so
  synchronization can diagnose gaps;
- corrections/revocations keep their stable earlier IF-05 record reference.

A separate persisted allocator metadata file is therefore **not required** for
the first implementation merely to know the next sequence. If an optimization
later adds such metadata, it is secondary/cached state and must be reconciled
against the authoritative committed TimingData stream rather than overriding it.

### Persistence policy by state family

TimingData has a stronger persistence rule than ordinary cache/reference state:

- a TimingData record is committed only after its complete IF-05 line is durably
  appended;
- its sequence is consumed only by that successful commit;
- the LogBook remains the Domain owner of operational timing history/state;
- the persistent IF-05 TimingData file is the durable recovery representation
  and sequence-recovery source;
- optional later snapshots may accelerate LogBook rebuild but are cache state and
  must reconcile to the persistent TimingData file.

Other state families remain separate:

- prepare-team/NextUpTeams state requires its own traceable persistence/recovery
  policy;
- StageStartTimes and RaceData are externally sourced reference data and may use
  versioned local snapshots for offline availability;
- display/read models are reconstructable state and need not become an
  alternative TimingData authority.

The exact filesystem durability primitive, file naming, rotation/retention and
snapshot cadence still need platform/verification evidence. Correctness and
recoverability take priority over introducing a database engine.

Status should eventually expose at least:

```text
persistent IF-05 TimingData file / recovery health
last committed sequence per TimingNode
LogBook ingress queue depth/high-water
last LogBook rebuild/recovery result
reference-data synchronisation time/version
other-state backup/recovery health
```

### Startup recovery

The first TimingData-oriented startup recovery flow is:

```text
start process
   |
   v
load configuration
   |
   v
open each configured TimingNode persistent file
   |
   v
validate IF-05 records + single source identity + contiguous committed sequence
   |
   +--> incomplete tail: truncate to last committed line boundary + diagnose
   |
   +--> invalid complete record/gap/regression: recovery fault; do not append
   |
   v
derive nextSequence = last committed sequence + 1
   |
   v
rebuild LogBook from committed TimingData records
   |
   v
load other operational/reference snapshots
   |
   v
start interfaces/devices
   |
   v
connect/synchronise with upstream when available
```

A new/empty TimingData file starts with next sequence 1.

Replay reconstructs TimingData-derived history and effective business state. It
does **not** by itself define the post-restart operational lifecycle policy. In
particular, a historical last `TIMING_NODE_STATE = OPEN` record is not a
sufficient reason to start accepting new timing observations automatically after
a process/power restart; that recovery/open policy belongs to the lifecycle
requirements and control design.

For prepare-team state, restoration can independently restore a snapshot or
replay its own traceable persistent file. Reference-data recovery likewise restores the
latest locally accepted snapshot/version. Corrupt/inconsistent persistent state
must produce explicit status rather than silently looking healthy.

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

## IF-05 realisation constraints

The TimingData record/file contract is not re-specified here. SI-01 design shall
conform to **IF05-REQ-001..015** in
`32-05-IDD-timingdata-interchange.md`.

The following temporary design constraints cover only the internal realisation
needed around that interface:

### Record pipeline

- **CAND-PIPE-001** — Traceable domain/application producers shall hand an
  immutable `LogBookEntryCandidate` to the bounded LogBook ingress queue;
  durable file I/O shall not execute on RFID/device/operator ingress callbacks.
- **CAND-PIPE-002** — The record-commit path shall publish an IF-05 record to
  downstream consumers only after the complete local record is durably appended
  and its sequence is committed.
- **CAND-PIPE-003** — After durable IF-05 append, the commit path shall apply the
  corresponding `LogBookItem` synchronously to the owning TimingNode LogBook
  before external publication.
- **CAND-PIPE-004** — Potentially long queries and network delivery/retry shall
  execute outside the LogBook recorder worker; only slow external delivery
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

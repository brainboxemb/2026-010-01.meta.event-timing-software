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

Every `TimingNode` has a `TimingNodeId`. A registration fact also captures
the applicable configured `LocationID`.

`TimingNodeId`, `LocationID` and `AntennaId` are separate namespaces. I/O
configuration relates observations to TimingNodes; code must not infer one
identity from another.

Concrete production source identifiers, source classes, allowed LocationID sets
and source-to-node mappings are deployment/provider information and are not
defined by this public SDD.

### LogBook and IF-05 TimingData

The runtime `LogBook` stores committed canonical `TimingDataRecord` values.
The current design does not add a second logbook-specific timing-record type.

That choice is deliberate. The old/reference software already treats one LBR
record as both the logged timing fact and the object consumers read. The new
design keeps that useful property while giving the file format a clear IF-05
contract.

The system-owned **IF-05 TimingData Interchange** contract is defined by
`32-05-IDD-timingdata-interchange.md`. It owns record kinds,
`RegistrationIdentity`, sequence/key semantics, versioning and canonical file
encoding.

The same immutable `TimingDataRecord` object can therefore be:

- appended by `TimingDataStore`;
- added to `LogBook` after that append is durable;
- read by runtime consumers;
- offered to downstream/upstream delivery.

A `TimingDataProvider` may translate to or from another external representation,
but that translation does not introduce a second SI-01 timing-record model.

### Registration identity resolution

All participant registrations are committed with one canonical
`RegistrationIdentity` owned by IF-05.

Input/provider-specific identities and operator/reference-data identities are
resolved to that canonical value before the definitive TimingData record is
created:

```text
source/provider identity -----\
                               +--> RegistrationIdentity
operator/reference identity --/
```

The resolution may use current `RaceData` when reference data is required.
Concrete source encoding, categories, ranges and mapping tables remain outside
this public SDD. A provider may translate an external representation, but it does
not redefine `RegistrationIdentity` semantics.

## TimingNode serial execution and timing-data commit

### Active-object boundary

A `TimingNode` is the active serialization boundary for all mutable state that
belongs to one timing point. The contained state objects stay passive:

```text
TimingNode  <<active object>>
  +-- bounded serial work queue
  +-- one serial worker (first implementation)
  |
  +-- LogBook           passive, committed TimingDataRecord history
  +-- NextUpTeams       passive
  +-- StageStartTimes   passive
  +-- RaceData          passive
  +-- lifecycle/location state
  |
  +-- TimingDataStore
  +-- NextUpTeamsStore
  +-- StageStartTimesStore
  +-- RaceDataStore
```

The Active Object wording describes the behaviour, not a required Java base
class. SDD-02 uses composition for the first implementation.

Public/application calls stay ordinary Java methods such as
`register(teamIdentity, time)`. Crossing the TimingNode's asynchronous boundary
requires a small immutable internal work item so the caller may return while the
node processes the operation later. That internal item is not a public Command
Pattern object, is not persisted and does not become another domain model.

The single TimingNode worker gives one clear order across registrations,
NextUpTeams changes, reference-data updates and lifecycle changes. No producer
lock is required around sequence allocation because only this worker performs
the commit step.

### TimingData commit and sequence

For a registration, the decision that a registration shall be recorded has
already been made before the asynchronous hand-off. The worker does not approve
the registration again. It may still perform deterministic resolution or
enrichment that depends on the node's current serialized state, such as resolving
a reserve tag through the current `RaceData`.

Only when the worker is ready to commit does it ask the LogBook for the next
sequence. Sequence is therefore not assigned when work is placed on the queue.

Conceptually:

```java
void processRegistration(RegistrationInput input) {
    long sequence = logBook.nextSequence();

    TimingDataRecord record =
        timingDataFactory.registration(input, sequence, timeSource.now());

    timingDataStore.append(record);   // returns after durable append
    logBook.add(record);              // consumer visibility point
    committedSinks.publish(record);   // non-blocking hand-off only
}
```

`LogBook.nextSequence()` is based on committed state:

```text
empty LogBook                  -> 1
last committed sequence = N    -> N + 1
```

Calling `nextSequence()` does not consume the number. If persistence fails,
the record is not added to LogBook and the next attempt still uses the same
sequence. A later work item may not overtake the failed timing-data commit.

The important ordering is:

```text
TimingNode worker
  -> choose next sequence
  -> create immutable TimingDataRecord
  -> TimingDataStore.append(record)
  -> durable
  -> LogBook.add(record)            <-- visible to consumers from here
  -> publish/notify downstream
```

There is no direct producer-to-store path and no second TimingNode serial worker.

![TimingNode producers and durable TimingData commit path](../../../raw/prod/docs/assets/architecture/timingdata-producer-pipeline.svg)

*Figure SDD01-TD01 — State-changing input enters the TimingNode serial boundary; a TimingData record becomes visible only after durable persistence.*

### Other TimingNode state and per-type stores

Not every state type has the same durability semantics.

`TimingDataStore` is special: successful durable append is part of the timing
record commit. The LogBook is rebuilt from committed TimingData after restart.

`NextUpTeamsStore`, `StageStartTimesStore` and `RaceDataStore` serve a
different first purpose: preserve accepted state changes/snapshots for
post-event analysis. Their stored data lets engineers later answer questions
such as which teams were next-up or which stage-start times/reference data were
known when a timing decision was made.

Those files are not automatically the runtime source after reboot. For example,
StageStartTimes can be sent again when the node is opened. Keeping its historical
file is still valuable for later analysis.

All state changes are ordered by the TimingNode worker. The first implementation
may also perform these small/infrequent store writes on that worker. If target
measurements show an analysis-store write can delay registration unacceptably,
the immutable snapshot can later be handed to a bounded persistence executor.
That optimization must not change TimingNode state ordering and must not
introduce an unbounded hidden queue.

### Query/consumer visibility

Consumers only see committed timing records. A query that starts before a new
record is added may finish against its earlier view; a later query sees the new
record.

A long query must not occupy the TimingNode worker or hold the LogBook lock for
its whole calculation. With the expected LogBook size of roughly 1200–1500
records, immutable TimingDataRecord objects make a shallow reference snapshot
cheap. Copying 1500 references is roughly 6 KiB with 4-byte compressed
references or 12 KiB with 8-byte references.

To avoid turning even that small copy into repeated garbage, a consumer may own
a reusable destination buffer:

```java
int count = logBook.copyTo(reusableBuffer);  // short synchronized copy
calculate(reusableBuffer, count);            // no LogBook lock
```

The exact collection/array implementation and measured copy time remain SDD-02
implementation/verification details. The architectural point is that a consumer
gets a stable view without a second LogBook thread.

![TimingNode asynchronous ownership and query isolation](../../../raw/prod/docs/assets/architecture/timingdata-async-ownership.svg)

*Figure SDD01-TD02 — One TimingNode serial worker owns mutation order; passive state and consumers do not receive their own workers.*

### Runtime flows

The sequence diagrams below are intentionally high-level. They show method calls,
the TimingNode asynchronous boundary, persistence and visibility. SDD-02 owns the
concrete Java worker mechanism.

#### Automatic RFID registration

![Automatic RFID registration sequence](../../../raw/prod/docs/assets/architecture/timingdata-sequence-auto-registration.svg)

*Figure SDD01-TD03 — An antenna callback submits work to the TimingNode and returns; the TimingNode worker later persists and exposes the record.*

#### Manual registration

![Manual registration sequence](../../../raw/prod/docs/assets/architecture/timingdata-sequence-manual-registration.svg)

*Figure SDD01-TD04 — CommandHandler makes a normal TimingNode registration call; no Command object is implied by the interface.*

#### Long query while registrations continue

![LogBook query isolation sequence](../../../raw/prod/docs/assets/architecture/timingdata-sequence-query-isolation.svg)

*Figure SDD01-TD05 — A query works on a stable LogBook view while the TimingNode worker can commit later records.*

#### Later producers

![Generic TimingNode producer sequence](../../../raw/prod/docs/assets/architecture/timingdata-sequence-generic-producer.svg)

*Figure SDD01-TD06 — Later start, penalty and correction operations use the same TimingNode serial boundary.*

#### Thread/ownership responsibilities

| Execution role | May block on | Must not block |
| --- | --- | --- |
| ingress/caller | short validation + bounded TimingNode submission | durable file I/O, long query, network retry |
| TimingNode serial worker | ordered domain state change; required local persistence | long query, client rendering, slow network retry |
| query worker/caller | its own calculation on a stable read view | TimingNode state progress |
| signalling/upstream worker | its own delivery/retry policy | TimingNode commit |

For the first one-node implementation, one dedicated worker is the simplest
mechanism. A later multi-node runtime may share executor threads only if each
TimingNode still processes at most one work item at a time and preserves FIFO
order.

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

### Persistence roles

TimingData has the strongest rule:

- a TimingData record is committed only after its complete IF-05 representation
  is durably appended;
- only then is the same `TimingDataRecord` added to LogBook and visible to
  runtime consumers;
- the TimingData file is used to rebuild LogBook after restart.

Other per-node stores have a different first purpose:

- `NextUpTeamsStore` preserves accepted next-up state/history for analysis;
- `StageStartTimesStore` preserves accepted start-time snapshots for analysis;
- `RaceDataStore` preserves accepted reference-data snapshots/versions for
  analysis.

Those historical stores do not automatically restore live state after reboot.
The live protocol may resend the current data, for example when a TimingNode is
opened. Recovery semantics can be promoted later if an operational requirement
needs them.

Implementation points to verify on the target Pi:

- what exact flush/fsync call makes a TimingData append durable;
- what happens if power disappears halfway through the final line;
- whether truncating the incomplete tail is safe on the target filesystem;
- how a corrupt complete record is reported instead of silently ignored;
- file rotation/retention for TimingData and analysis stores;
- whether any non-critical store write needs asynchronous offload after
  measurement.

We do not need a database just to solve these cases.

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

### Reference-data synchronisation

Start-time and participant/reference mappings supplied by an external system may also need to be available locally.

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

The same pattern can be used for other participant/reference mappings. Full-snapshot versus delta updates, version identifiers and correction semantics still need requirements/IDD design.

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
      TimingNode
   bounded serial work
          |
          v
    TimingDataRecord
          |
          +--> TimingDataStore (durable)
          +--> LogBook (visible after durable append)
          +--> StageTiming / ranking inputs
          +--> downstream integration

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

### TimingNode state and record pipeline

- **CAND-PIPE-001** — Each TimingNode shall provide one bounded serial execution
  boundary for its mutable per-node state. Contained state objects such as
  LogBook, NextUpTeams, StageStartTimes and RaceData shall remain passive.
- **CAND-PIPE-002** — Registration sequence shall be selected by the TimingNode
  worker immediately before commit, not when ingress work is queued.
- **CAND-PIPE-003** — A TimingData record shall become visible in LogBook only
  after `TimingDataStore` reports the complete append durable.
- **CAND-PIPE-004** — The LogBook shall hold the same canonical
  `TimingDataRecord` values used by the TimingData persistence/interchange
  boundary; no second logbook-specific timing-record type is required.
- **CAND-PIPE-005** — Potentially long queries and network delivery/retry shall
  execute outside the TimingNode serial worker.
- **CAND-PIPE-006** — Consumers needing a stable LogBook view shall use a short
  read/copy operation and perform long calculations after releasing LogBook
  synchronization; implementations should avoid unnecessary per-query garbage.

### Identity resolution before IF-05 commit

- **CAND-ID-001** — Source/provider-specific participant identities shall resolve
  to the canonical IF-05 `RegistrationIdentity` before the definitive TimingData
  record is created.
- **CAND-ID-002** — Operator/reference-data registration paths shall resolve to
  the same canonical `RegistrationIdentity` used by automatic/source-driven
  registrations.
- **CAND-ID-003** — Concrete source encodings, category/range rules and mapping
  tables shall stay behind their provider/reference-data boundary unless a public
  interface requirement explicitly promotes them.

### Local data and per-type stores

- **CAND-DATA-001** — The initial implementation shall maintain committed
  LogBook state, next-up state and reference state in typed in-memory objects
  without requiring an external database engine.
- **CAND-DATA-002** — `TimingDataStore` shall be the durable/recovery source
  for committed TimingData.
- **CAND-DATA-003** — NextUpTeams, StageStartTimes and RaceData shall each use a
  type-specific store when their accepted state/snapshots are preserved for
  analysis; these stores shall not be treated as runtime recovery authority
  unless a requirement explicitly says so.
- **CAND-DATA-004** — TimingData recovery faults and analysis-store failures
  shall be visible in system status/diagnostics.
- **CAND-DATA-005** — The system shall track enough reference-data
  synchronisation metadata to determine whether local data is current/stale
  relative to the latest accepted update.

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

- What exact identifiers represent virtual registration systems?
- How are physical producers mapped to one or more `TimingNodeId` values in deployment configuration?
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

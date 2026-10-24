<!-- Generated review/output copy. Edit the source document, not this copy. -->

# Data and display detailed design

Status: working draft / focused detailed design

Software item: **SI-01 — Timing Point Application**

## Purpose

This SDD explains **how the data flows inside SI-01**: how LogBook entries are
recorded, when a TimingData record is committed, how persisted TimingData is loaded after restart, how an interrupted final write is repaired, and
how queries, prepare-team data and display data use that state.

## Terms and abbreviations

- **SDD** — Software Design Description
- **SSD** — Software Specification Document
- **SI** — Software Item
- **IF-05** — TimingData Interchange


## Relationship to other documents

This SDD refines the SI-01 SSD for internal data/runtime behaviour. It consumes the
SI-01 architecture and applicable interface contracts, especially IF-05. SDD-02 then
maps this design to concrete Java components, packages, queues and threads.

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
the applicable configured `LocationId`.

`TimingNodeId`, `LocationId` and `AntennaId` are separate namespaces. I/O
configuration relates observations to TimingNodes; code must not infer one
identity from another.

The shared `LocationId` Java value type owns only the common positive numeric
representation. Concrete event/profile LocationId meaning, allowed sets and
source-to-node mappings are deployment/reference information and are not defined
by this public SDD.

### LogBook and IF-05 TimingData

The runtime `LogBook` stores committed immutable `TimingData` values.
The current design does not add a second logbook-specific timing-data type.

That choice is deliberate. The old/reference software already treats one LBR
record as both the logged timing fact and the object consumers read. The new
design keeps that useful property while giving the file format a clear IF-05
contract.

The system-owned **IF-05 TimingData Interchange** contract is defined by
`32-05-ISD-timingdata-interchange.md`. It owns the common TimingData semantics, shared `LocationId` and
`RegistrationId` value representations, sequence/key semantics and compatibility
rules. The configured event/profile/reference model owns the concrete identifier
domains, while the configured TimingData profile owns its concrete classes and
matching representation/codec. The default/reference JSON + JSON Lines representation is described separately by `33-05-IDD-timingdata-interchange.md`.

The same immutable `TimingData` object can therefore be:

- appended by `TimingDataPersistence`;
- added to `LogBook` after that append is durable;
- read by runtime consumers;
- offered to downstream/upstream delivery.

A `TimingDataProvider` supplies the configured concrete TimingData factory and
codec. Different profiles may return different concrete classes while SI-01
continues to use the common TimingData interfaces.

### Registration identity resolution

All participant registrations are committed with one shared `RegistrationId`
representation defined by IF-05. The concrete RegistrationId domain and meaning
may be event/profile-specific.

The automatic and manual source paths share the canonical RegistrationId boundary but do
not require the same resolver:

```text
TagObservation
  TagId + RSSI + time
        |
        v
   TagProcessor
        |
        v
TagRegistrationMapper -------------------------\
                                                +--> RegistrationId
TeamId -> team/reference resolution -----------/
```

`TagId` belongs to the RFID/tag input path. `TeamId` belongs to the
team/reference-data/manual path. Only the resolved `RegistrationId` is passed
to the TimingData factory.

The tag mapper is an EventData/profile policy boundary. It may perform a
deterministic transformation, provider/profile-specific conversion or a
RaceData/reference-data lookup. A lookup table is not the generic design.

The public default/reference EventData profile uses a deterministic convention.
For a four-digit positive number NNNN from 0001 through 9999, TagIds
`TT-A-NNNN-1` and `TT-A-NNNN-2` both resolve to RegistrationId
`RT-A-NNNN`, which resolves directly to TeamId `NNNN`. Reserve TagIds
`TT-R-NNNN-1` and `TT-R-NNNN-2` both resolve to RegistrationId
`RT-R-NNNN`; that reserve RegistrationId requires reserve-assignment reference
data to resolve a TeamId. The numeric value 0000 is invalid.

The final tag suffix identifies the physical member of a two-tag set and is not
part of the logical RegistrationId. Live RaceData reserve assignments may
override stable EventData reference relationships where applicable.

This convention belongs to the default/reference EventData profile. Other
providers may define different TagId, RegistrationId and TeamId semantics. The
generic IF-05 RegistrationId therefore remains opaque outside the selected
profile.

## TimingNode lane ownership and timing-data commit

### Data Lane and Task Lane boundaries

A `TimingNode` is the top-level component boundary for one timing point.
Mutable responsibilities are split over two bounded serial lanes; contained data
objects remain passive:

```text
TimingNode
  +-- LogBookProcessor / Data Lane
  |     +-- lifecycle/location
  |     +-- TimingData sequence + durable commit
  |     +-- LogBook
  |     +-- TimingDataPersistence
  |
  +-- NodeTaskProcessor / Task Lane
        +-- RaceDataState
        |     +-- TeamAssignments
        |     +-- StageStartTimes
        +-- UniqueTeamRegistrations
        +-- StageTiming
        +-- UpstreamHandler / protocol state
```

The Active Object pattern is implemented by composition; neither processor
requires an inheritance hierarchy or a dedicated physical thread. The two
logical lanes may use the same Runtime-owned worker.

Public/application calls stay ordinary methods. The TimingNode hides the
asynchronous hand-off used by its Active Object implementation.

For a state-dependent operation such as `open(locationId)`, `close()` or a
consistency-sensitive status query, the public call does not
report success merely because work entered the queue. The TimingNode queues an
internal work item, executes it later against the then-current ordered state and
returns the processed result to the caller. A Java implementation may connect
those two moments with an internal `Future`; that Future is not part of the
caller-facing domain API.

Submission-only ingress is a separate contract. A device callback may need only
to know whether bounded work was admitted so that the callback thread can
continue immediately. In that case `ACCEPTED` means only accepted for later
processing.

The contained state objects are passive but not globally readable. TimingNode
owns current lifecycle/location state and serializes its changes with registration
admission. LogBook mutation remains on the Data Lane. RaceData and derived timing
mutations occur only on the Task Lane. TimingData sequence allocation therefore
needs no producer lock because only the Data Lane performs the commit step.
Cross-lane information is immutable and bounded: initial-load/commit facts flow
Data -> Task; LogBook replay requests/results flow Task -> Data.

### TimingData commit and sequence

A producer may have completed work that belongs before the TimingNode boundary,
such as device decoding/filtering or translation into a semantic registration
request. That does not let the producer decide state-dependent TimingNode
conditions from outside the node.

When the work item reaches the serial lane, the TimingNode checks the current
state needed by that operation. Examples include whether the node is open, which
location is active and which current reference data is needed. Only then does the
worker create/commit the resulting TimingData.

For a caller that waits for a registration result, successful return therefore
means the registration operation has reached its defined commit/visibility point;
for submission-only device ingress there is no synchronous caller waiting for
that later result.


OPEN/CLOSE runtime state and lifecycle TimingData have different ownership.
For a real `CLOSED -> OPEN` transition, TimingNode applies the requested
LocationId and OPEN state at its registration-admission boundary. For
`OPEN -> CLOSED`, it applies CLOSED while retaining the current LocationId.
That runtime transition immediately determines whether later registrations may
be admitted.

While holding the same admission boundary, TimingNode submits the corresponding
NODE_OPEN or NODE_CLOSE command to the LogBook Data Lane. This gives one clear
source order:

- a registration admitted before CLOSE is queued before NODE_CLOSE;
- after CLOSED is applied, later antenna observations cannot admit a registration;
- after OPEN is applied, the NODE_OPEN command is submitted before a later
  automatic registration can be admitted.

The lifecycle-history command is fire-and-forget from the OPEN/CLOSE caller's
perspective. Queue rejection or later persistence/commit failure is reported as a
LogBook/persistence problem but does not roll back the already applied runtime
state. Consequently STATUS_CHANGED and TIMING_DATA_COMMITTED are separate facts;
their delivery order is not used to define current lifecycle state.

`ALREADY_OPEN` and `ALREADY_CLOSED` do not submit another lifecycle record.
There is no second lifecycle-event store or lifecycle-specific sequence owner.

Manual registration ADD uses the same TimingNode-owned commit path. The
Presentation/Application caller supplies the resolved RegistrationId, effective
registration time and AUTO/MAN time-source classification. AUTO means the client
selected/captured that time automatically; MAN means the operator entered or edited it.
TimingNode does not substitute server current time for an AUTO-classified manual
registration.

Registration REV uses the same append-only commit path. The caller supplies the
registration family plus the Registration ID and original effective time; for a
manual registration it also supplies the original AUTO/MAN time-source
classification. TimingNode assigns only the new record sequence/recorded-at
context and commits the resulting REV record.

TimingNode and LogBook carry absolute timing values internally as UTC epoch-millisecond
scalars. The default IF-05 profile applies its field-specific canonical precision at the
TimingRecord commit boundary: effective `time` is canonicalized to centiseconds
(10 ms), while newly sampled record-creation time retains full millisecond precision for
`recTime`. Registration effective time remains caller/observation-supplied timing
information; the 10 ms canonicalization is a default IF-05 representation rule rather
than a generic TimingData/Timestamp storage model.

LogBook and this commit boundary are bookkeeping, not the owner of interpreted
registration business state. They do not search prior history to decide whether
an ADD is currently active, whether a matching REV already exists or whether a
requested revoke is meaningful. Higher processing/application logic may interpret
ADD/REV history and decide what operation to request.

Only when the worker is ready to commit does it ask the LogBook for the next
sequence. Sequence is therefore not assigned when work is placed on the queue.

Conceptually:

```java
void processRegistration(RegistrationInput input) {
    long sequence = logBook.nextSequence();

    TimingDataFactory.Context context =
        timingDataContext(sequence, activeLocationId, input.effectiveTime(), timeSource.now());

    RegistrationId registrationId = raceData.resolveRegistrationId(input);

    TimingData data;
    if (input.isAutomatic()) {
        data = timingDataFactory.createAutomaticRegistration(context, registrationId);
    } else {
        data = timingDataFactory.createManualRegistration(
                context, registrationId, input.timeSource());
    }

    timingDataStore.append(data);     // returns after durable append
    logBook.add(data);                // consumer visibility point
    timingDataCommittedEvent.emit(data);
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
  -> build typed immutable registration TimingData through configured factory
  -> TimingDataPersistence.append(record)
  -> durable
  -> LogBook.add(record)            <-- committed domain state
  -> timingDataCommittedEvent.emit(record)
  -> subscribed listeners are notified
```

There is no direct producer-to-store path and no second TimingNode serial worker.

![TimingNode producers and durable TimingData commit path](../assets/architecture/timingdata-producer-pipeline.svg)

*Figure SDD01-TD01 — State-changing input enters the TimingNode serial boundary; the concrete TimingData value created by the configured factory becomes visible only after durable persistence.*

### Other TimingNode state and per-type stores

Not every state type has the same durability semantics.

`TimingDataPersistence` is special: successful durable append is part of the timing
record commit. The LogBook is rebuilt from committed TimingData after restart.

`NextUpTeamsStore`, `StageStartTimesStore` and `RaceDataStore` serve a
different purpose: preserve accepted state changes/snapshots for
post-event analysis. Their stored data lets engineers later answer questions
such as which teams were next-up or which stage-start times/reference data were
known when a timing decision was made.

Those files are not automatically the runtime source after reboot. For example,
StageStartTimes can be sent again when the node is opened. Keeping its historical
file is still valuable for later analysis.

State-changing operations execute on the lane that owns the state. TimingData,
LogBook and lifecycle/location changes are ordered by the Data Lane. RaceData,
TeamAssignments, StageStartTimes, UniqueTeamRegistrations and derived timing
changes are ordered by the Task Lane. Small/infrequent analysis-store writes
may execute during the owning lane turn only when measured latency permits it;
otherwise an immutable snapshot may be handed to a bounded persistence executor.
That optimization must not change lane ownership or introduce an unbounded
hidden queue.

### Query/consumer visibility

Consumers do not read mutable TimingNode-owned objects directly.

An ORDERED query enters the lane that owns the queried mutable state. LogBook
history and lifecycle/status ordering use the Data Lane; RaceData and derived
StageTiming queries use the Task Lane. If a read requires expensive calculation,
only the short ordered capture/traversal step runs on the owning lane; longer
calculation continues outside it.

A CURRENT query may instead read a safely published immutable representation of
completed TimingNode state without entering the lane. CURRENT is therefore not a
weaker implementation of ORDERED: it answers a different question and may legitimately
precede work that has been accepted but has not completed yet.

Conceptually:

```text
CURRENT query
  -> published immutable completed state

ORDERED query
  -> owning TimingNode lane (Data or Task)
       -> read/capture state after earlier accepted work on that lane
       -> return immutable view/result
  -> optional long calculation outside lane
```

For LogBook history, the read strategy may use direct bounded traversal or a
shallow immutable reference view because `TimingData` values are immutable.
The exact representation and allocation strategy belong to SDD-02 and
measurement evidence. A reusable internal buffer is acceptable only if callers cannot observe
it being mutated/reused after the query returns.

An ORDERED query before a new commit may legitimately see the earlier state;
an ORDERED query after that commit sees the new state. A CURRENT status query
returns the latest safely published completed state at the time of the read and
does not wait for merely accepted work. Neither form makes the underlying mutable
state globally readable.

![TimingNode asynchronous ownership and query isolation](../assets/architecture/timingdata-async-ownership.svg)

*Figure SDD01-TD02 — Process/execution refinement of TimingNode: the Data Lane owns TimingData/LogBook/persistence; the Task Lane owns RaceData, derived timing and protocol state. Both may share one physical worker. This is not the logical component diagram (SI01-01).*

### Runtime flows

The sequence diagrams below show the different caller contracts explicitly.
They deliberately distinguish queue admission from the domain result produced
when work executes against current TimingNode state. SDD-02 owns the concrete
Java queue, Future and worker mechanism.

#### Automatic RFID registration

![Automatic RFID registration sequence](../assets/architecture/timingdata-sequence-auto-registration.svg)

*Figure SDD01-TD03 — A device callback receives only bounded admission status and returns; later TimingNode processing uses current state and has no synchronous callback waiting for the domain result.*

#### Manual registration

![Manual registration sequence](../assets/architecture/timingdata-sequence-manual-registration.svg)

*Figure SDD01-TD04 — A presentation-driven registration call waits for its actual processed/committed result while the Future remains internal to TimingNode.*

#### Long query while registrations continue

![LogBook query isolation sequence](../assets/architecture/timingdata-sequence-query-isolation.svg)

*Figure SDD01-TD05 — The query captures its read view on the TimingNode lane and performs longer calculation outside the lane; it does not read LogBook directly.*

#### Additional producer paths

![Generic TimingNode producer sequence](../assets/architecture/timingdata-sequence-generic-producer.svg)

*Figure SDD01-TD06 — Additional state-dependent operations use the same TimingNode ownership/ordering boundary; their caller contract must still state whether they wait for a result or are submission-only.*

#### State-dependent OPEN waits for its processed result

![TimingNode OPEN sequence](../assets/architecture/timingnode-sequence-open.svg)

*Figure SDD01-TD07 — `open(locationId)` returns only after the queued operation has executed against current TimingNode state; the internal Future is not exposed to the caller.*

#### Concurrent OPEN and CLOSE are ordered by the TimingNode

![TimingNode OPEN / CLOSE ordering sequence](../assets/architecture/timingnode-sequence-open-close.svg)

*Figure SDD01-TD08 — State-dependent validation happens when each operation reaches the serial lane; callers do not decide validity from a pre-queue state read.*

#### Timeout means outcome unknown, not rollback

![TimingNode timeout sequence](../assets/architecture/timingnode-sequence-timeout.svg)

*Figure SDD01-TD09 — A caller timeout stops waiting but does not cancel already accepted work; the caller re-queries state before deciding what happened.*

#### Thread/ownership responsibilities

| Execution role | May block on | Must not do |
| --- | --- | --- |
| presentation caller waiting for a state-dependent result | bounded TimingNode operation wait | read/mutate TimingNode-owned state directly |
| device/callback ingress | short validation + bounded submission | wait for durable commit, run long domain work, read node state directly |
| Data Lane turn | TimingData/lifecycle operation; required local persistence; short LogBook read/capture | mutate Task Lane RaceData/derived state, client rendering, slow network retry |
| Task Lane turn | RaceData/protocol/derived-state operation; short task-owned query | mutate LogBook/persistence, synchronously wait for Data Lane work |
| query caller/worker | bounded wait for its owning lane; long calculation on immutable view | retain a mutable internal buffer or bypass TimingNode ownership |
| signalling/upstream worker | its own delivery/retry policy | mutate lane-owned state directly or block TimingData commit |

Each TimingNode has two bounded logical serial lanes. Physical worker threads may
be shared across both lanes and across nodes. FIFO/one-at-a-time ordering is
guaranteed within each lane; cross-lane ordering is expressed only through the
explicit immutable handoffs defined above.

## TimingData persistence and startup loading

This design implements `SI01-REQ-045..048` together with the applicable IF-05
semantics and the reference representation in
`33-05-IDD-timingdata-interchange.md`.

### Loading persisted TimingData and determining the next sequence

No separate sequence-counter file is required.
The TimingData file already tells us the last committed sequence:

```text
no committed records       -> nextSequence = 1
last committed sequence N  -> nextSequence = N + 1
```

At startup, `LogBookProcessor` queues this load as the **first ordered Data Lane task**.
`NodeTaskProcessor` has an independent lifecycle: its Task Lane may already be running
while the persisted TimingData is being read. The initial loaded-data snapshot is input
to Task-owned derived timing state; it is not a precondition for Task Lane activation:

- read complete IF-05 records in order;
- check that the file belongs to one TimingNode;
- check that the committed sequence increases without duplicates or unexpected gaps;
- ignore/remove only a half-written final record that has no complete line ending;
- rebuild the node-owned LogBook/state before publishing CURRENT status;
- never reuse a committed `(TimingNodeId, SequenceNumber)`.

The lane ownership is about ordering and single-writer semantics, not physical
parallelism. Multiple TimingNode lanes may share one physical TimingNode worker,
so startup file reads may intentionally execute one at a time.

A half-written **last** record after power loss can be repaired: truncate back to
the last complete record and continue from there. This tail repair is recovery behaviour;
the normal act of reading existing complete records is not.

A corrupt **complete** record, duplicate sequence or gap is different. Do not
silently skip or renumber it. Stop the startup load for that TimingNode and report the
problem so support/operator tooling can see it.

If a cached sequence-counter file is introduced for faster startup, it is only a
cache. The committed TimingData file remains the source used to check/rebuild it.

### Persistence roles

TimingData has the strongest rule:

- a TimingData record is committed only after writing its complete reference
  representation to the configured local store has completed successfully;
- only then is the same concrete `TimingData` value added to LogBook, published
  as a committed live event or returned as a successful commit result;
- the TimingData file is used to rebuild LogBook after restart.

Other per-node stores have a different purpose:

- `NextUpTeamsStore` preserves accepted next-up state/history for analysis;
- `StageStartTimesStore` preserves accepted start-time snapshots for analysis;
- `RaceDataStore` preserves accepted reference-data snapshots/versions for
  analysis.

Those historical stores do not automatically restore live state after reboot.
The live protocol may resend the current data, for example when a TimingNode is
opened. Those stores do not restore live state unless an operational requirement
explicitly defines such recovery semantics.

The successful write above is the software commit boundary. The stronger
guarantee against sudden power loss depends on the concrete filesystem and flush
primitive and remains a target-specific design/verification point.

Implementation points to verify on the target Pi:

- what exact flush/fsync call provides the required power-loss durability level;
- what happens if power disappears halfway through the final line;
- whether truncating the incomplete tail is safe on the target filesystem;
- how a corrupt complete record is reported instead of silently ignored;
- file rotation/retention for TimingData and analysis stores;
- whether any non-critical store write needs asynchronous offload after
  measurement.

We do not need a database just to solve these cases.

### Operational TimingData and LogBook logging

TimingData/LogBook logging is part of this detailed design because the useful
level depends on the domain commit and startup-load semantics above. The generic
level meanings remain defined by Java design rule DR-09.

The normal INFO stream is intended to reconstruct meaningful timing operation
without becoming a raw RFID trace. In particular, a durable TimingData commit is
logged only after both persistence append and LogBook visibility have succeeded.

| Event/fact | Level | Design intent |
| --- | --- | --- |
| TimingData load starts | INFO | show node startup loading progress |
| TimingData load completes | INFO | include TimingNodeId, loaded record count and tail-repair flag |
| incomplete final record tail repaired | WARN | startup load succeeded after repairing evidence of an interrupted previous write |
| one tag passage/semantic automatic-registration candidate selected | INFO | include RegistrationId plus selected TagId/RSSI/time; this is one passage decision, not every raw observation |
| successful TimingData commit | INFO | emit only after durable append + LogBook add; include node, sequence, type and relevant registration/location/time provenance |
| raw TagObservation | TRACE | potentially high rate; never normal INFO |
| unmapped TagId / duplicate suppression / filter decision | DEBUG | useful for diagnosis without polluting normal operation logs |
| ordinary LogBook range/latest/count query | no INFO | query traffic is not an operational state transition; DEBUG only when diagnosis specifically needs it |
| recoverable queue/admission or automatic-repair anomaly | WARN | operation is degraded/rejected but component may continue |
| TimingData load/validation or persistence failure that makes the node unreliable | ERROR | node cannot safely continue its TimingData role |

Two distinct INFO facts may therefore appear for the automatic RFID path:

```text
Tag passage selected
    -> TimingNode registration command
    -> durable TimingData append
    -> LogBook.add
TimingData committed
```

The first proves that the passage/filter produced a semantic registration
candidate. The second proves that the resulting record crossed the durable
commit/LogBook visibility boundary. They must not be collapsed into one premature
"written" message.

The LogBook and TimingData file remain authoritative. Logs are a human-readable
operational narrative and must not be used to rebuild runtime state.

The same commit boundary owns the generic committed-TimingData event. `LogBook`
emits that fact only after durable persistence and committed in-memory visibility have
succeeded. Startup reconstruction does not replay persisted records through the new-data
event; instead, `LogBook` publishes one immutable initial-history fact for consumers that
need to rebuild derived state. Upstream delivery, post-processing and presentation remain
optional consumers and do not participate in commit success.

### Startup flow

Lifecycle activation and persisted-data loading are deliberately separate. TimingNode
starts with independent values: functional state `CLOSED`, no LocationId and
operational state `INIT`:

```text
start process
   |
   v
load configuration / compose components
   |
   v
construct TimingNode
   |
   +--> functionalState = CLOSED
   +--> locationId = none
   +--> operationalState = INIT
   |
   v
TimingNode activation
   |
   +--> activate NodeService
   |       +--> start Task Lane
   |
   +--> activate LogBook
   |       +--> start Data Lane
   |       +--> queue persisted-TimingData load as first Data Lane task
   |
   +--> activate TagProcessor
   +--> return; other components may continue activation
   |
   +------------------------------+
                                  |
Data Lane                         | other application startup may continue
   |                              |
   v                              v
read and validate complete    other nodes / interfaces / devices activate
IF-05 records
   |
   +--> half-written final line: truncate to last complete record + report repair
   |
   +--> corrupt complete record / duplicate / gap: record recovery failure
   |
   v
rebuild committed LogBook history
   |
   +--> publish immutable initial TimingData history to Task Lane consumers
   |
   +--> publish LogBook recovery result
   |
   v
later ordered LogBook commands continue
```

The persisted-data load is the first ordered Data Lane task, so later ordered commands
naturally wait behind it. A caller does not perform a separate LogBook-readiness check.
TimingNode functional state remains readable as `CLOSED` with no LocationId during
loading, while operational state remains `INIT`. Successful recovery changes only
operational state to `OK`; failed recovery changes only operational state to `ERROR`
with problem detail. Later operations that need the LogBook fail through the normal
TimingNode operation-failure contract.

A new/empty TimingData file starts at sequence 1.

Rebuilding the LogBook does **not** automatically reopen a TimingNode. Even when
the last historical state record says `OPEN`, a process restart starts the node
as `CLOSED` with no LocationId. New observations are not accepted for timing
until an explicit new `open(...)` operation succeeds.

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

The start-time semantic model uses the same project-owned `TimingTimestamp` value at protocol boundaries while allowing the source to provide only the information it actually knows. A race/stage source may therefore provide **time-of-day only**; a date may be present when known, and an already absolute timestamp is also representable. Consumers shall not invent missing date/zone context. SI-01 normalizes accepted stage starts once to a compact UTC long while preserving whether a date was present: time-only uses `HHmmsscc`, dated values use `yyyyMMddHHmmsscc`. For elapsed-time calculation, a time-only start is matched against the absolute registration passage using same/previous UTC-day rollover and is accepted only when the unique result is within `0 <= elapsed < 12 hours`; ambiguous values remain unresolved and do not rank.

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

The same pattern can be used for other participant/reference mappings. Full-snapshot versus delta updates, version identifiers and correction semantics still need requirements/ISD design.

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

![In-memory data, backup and V1/V2 display behaviour](../assets/architecture/data-display-flow.svg)

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

Fields are illustrative. The display ISD will ultimately define the system contract; a separate IDD is needed only if concrete design deserves its own baseline.

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

Delta delivery is an allowed optimisation, but reconnect must always be recoverable through a complete current snapshot.

### Registration versus ready-team display state

These flows remain separate:

```text
RFID / manual / lifecycle / start / penalty logic
          |
          v
      TimingNode
   bounded serial work
          |
          v
    TimingData
          |
          +--> TimingDataPersistence (durable)
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
conform to **IF05-REQ-001..007** in
`32-05-ISD-timingdata-interchange.md`.

The following temporary design constraints cover only the internal realisation
needed around that interface:

### TimingNode state and record pipeline

- **CAND-PIPE-001** — Each TimingNode shall provide two bounded logical serial
  execution boundaries: Data Lane for TimingData/LogBook/persistence and Task
  Lane for RaceData/derived timing/protocol state. Contained state objects such
  as LogBook, TeamAssignments and StageStartTimes remain passive.
- **CAND-PIPE-002** — Registration sequence shall be selected by the TimingNode
  worker immediately before commit, not when ingress work is queued.
- **CAND-PIPE-003** — A TimingData record shall become visible in LogBook only
  after `TimingDataPersistence` reports the complete append durable.
- **CAND-PIPE-004** — The LogBook shall hold the same canonical
  immutable `TimingData` values used by the TimingData persistence/interchange
  boundary; no second logbook-specific timing-record type is required.
- **CAND-PIPE-005** — Potentially long queries and network delivery/retry shall
  execute outside the TimingNode serial worker.
- **CAND-PIPE-006** — Consumers needing a stable LogBook view shall use a short
  read/copy operation and perform long calculations after releasing LogBook
  synchronization; implementations should avoid unnecessary per-query garbage.

### Identity resolution before IF-05 commit

- **CAND-ID-001** — An automatic/tag registration shall resolve its `TagId`
  to the canonical IF-05 `RegistrationId` before the definitive TimingData
  value is created.
- **CAND-ID-002** — A manual/reference-data registration shall resolve its
  `TeamId` to the same canonical `RegistrationId` concept before TimingData
  creation.
- **CAND-ID-003** — Concrete source encodings, category/range rules and mapping
  tables shall stay behind their provider/reference-data boundary unless a public
  interface requirement explicitly promotes them.

### Local data and per-type stores

- **CAND-DATA-001** — The initial implementation shall maintain committed
  LogBook state, next-up state and reference state in typed in-memory objects
  without requiring an external database engine.
- **CAND-DATA-002** — `TimingDataPersistence` shall be the durable source used to rebuild LogBook after restart
  for committed TimingData.
- **CAND-DATA-003** — NextUpTeams, StageStartTimes and RaceData shall each use a
  type-specific store when their accepted state/snapshots are preserved for
  analysis; these stores shall not be treated as runtime recovery authority
  unless a requirement explicitly says so.
- **CAND-DATA-004** — TimingData startup-load/validation faults and analysis-store failures
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

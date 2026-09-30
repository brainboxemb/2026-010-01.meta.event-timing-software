# Data and display detailed design

Status: working draft / non-authoritative

Software item: **01 — Headless Timing Application**

This document refines local data ownership, backup/restore, traceable registration streams, ready-team behaviour, reference data, and the two display generations.

The initial design does **not** require a conventional embedded database. Runtime state is held in typed Java data structures/repositories and is backed up to simple files so the application can restore its state after restart.

Domain identifiers and known ranges are captured in `03-domain-baseline.md`. This SDD translates those facts into software/data-design direction.

## Core distinction: two traceable information models

Two information flows must not be conflated:

1. **registration stream/ledger** — timing and operational entries that are synchronised as an ordered source stream;
2. **prepare-team registry history/state** — keypad/operator actions that prepare/remove teams and drive current display state.

Both need traceability and persistence, but they have different semantics and sequence scopes.

## Registration-source identity

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

## LogBook and TimingData

The runtime `LogBook` owns operational state as 0..N `LogBookItem` values.
Those items are domain state and do not have to be shaped like the representation
used outside the LogBook.

`TimingData` defines the framework-owned canonical semantic protocol and
persistent/interchange record model. `TimingDataRecord` is the semantic record
used at storage, API and upstream boundaries. TimingData owns record kinds, field
meaning, validation, protocol versioning and the canonical public/reference
encoding.

External/proprietary formats are translations at the edge. A
`TimingDataProvider` may decode such a representation into `TimingDataRecord`
and encode records back when required, but it does not own or change the public
record schema.


### TimingData v1 — first registration slice

This section is the consolidated first-slice TimingData contract. Later record
types may extend it compatibly; they shall not silently redefine these meanings.

#### Common record envelope

Every committed v1 record has:

```text
TimingDataRecord
  version = 1
  timingNodeId
  sequenceNumber
  locationId
  recordType
  effectiveTime
  recordedAt
  type-specific data
```

Rules:

- `timingNodeId + sequenceNumber` is the stable record key;
- a new TimingNode stream starts at sequence **1**;
- sequence **0 is reserved** and is never a normal committed record;
- sequence ordering is per `TimingNodeId`, independent of `LocationID`;
- `locationId` is captured on the record and does not change when the
  TimingNode is reconfigured later;
- `effectiveTime` is when the represented timing fact applies;
- `recordedAt` is when this record/fact was committed by SI-01;
- records are append-only historical facts.

#### Record types in v1

```text
TIMING_NODE_STATE
  state = OPEN | CLOSED

REGISTRATION
  registrationIdentity
  origin = AUTOMATIC | MANUAL
  timeSource = OBSERVED | SYSTEM_ASSIGNED | OPERATOR_ENTERED

REGISTRATION_REVOKED
  registrationIdentity
  reference = TimingDataRecordKey of original REGISTRATION
  origin/timeSource = semantics of referenced registration
```

For `REGISTRATION_REVOKED`:

- the original record remains unchanged;
- the revocation receives its own sequence number and `recordedAt`;
- `effectiveTime` is equal to the effective time of the referenced
  registration, not the time at which the revocation command is entered;
- `reference` identifies the registration that the revocation concerns.

TimingData does not itself maintain a derived "currently active registrations"
list. Domain/application business logic may reconstruct effective registration
state from the append-only stream and shall honour revocations when performing
calculations such as classification, ranking or other race-result logic.

Presentation remains separate: a client may hide the registration, strike it
through, mark it revoked, or apply another visual representation without changing
the underlying TimingData facts. Handling of a dangling reference in a
partial/imported stream is a consumer/application policy rather than a reason for
the codec to rewrite history.

#### Registration identity in v1

```text
RegistrationIdentity
  type = STANDARD | WOMEN | MEN
  number = 1..350
```

Location compatibility:

```text
STANDARD  -> LocationID 1..23
WOMEN     -> LocationID 24
MEN       -> LocationID 25
```

A reserve transponder is not a `RegistrationIdentity.type`. It is an input
`TagIdentity` that resolves through reserve mapping data to a canonical
`RegistrationIdentity`.

Automatic and manual input paths therefore converge before commit:

```text
TagIdentity  -----\
                 +--> RegistrationIdentity --> REGISTRATION
TeamIdentity -----/
```

The public v1 contract does not yet define legacy/unknown-team identity classes;
those are deferred until their required business semantics are verified.

#### Canonical reference file encoding

The public/reference v1 file codec is append-only UTF-8 JSON Lines:

- one complete TimingData record per line;
- canonical writer line ending is LF (`0x0A`);
- a reader may accept CRLF input for interoperability;
- every line is independently decodable;
- a trailing incomplete line after interrupted/power-loss write is not a
  committed record;
- valid complete records before such an incomplete tail remain readable and
  sequence consistency is checked during recovery.

This canonical file encoding is part of the public/reference implementation.
A proprietary provider may use a different external representation, including a
fixed-field format and CRLF, while translating to/from the same v1 semantic
records.

The registration ledger contains timing/registration-domain and traceable operational records. The first concretely promoted operational record is a **TimingNode lifecycle/state-change record**:

```text
state = OPEN
state = CLOSED
```

Opening and closing are traceable TimingData facts, not merely transient status
changes. The public model deliberately does not prescribe a legacy characteristic
code, one fixed-column record layout or transport-specific status character.

A concrete `TimingDataProvider` may translate these semantic records to/from a
deployment-specific/proprietary representation while the framework-owned
TimingData protocol remains unchanged. Any additional status invented by
a higher-level system to describe synchronisation state is not automatically a
TimingNode lifecycle value.

The next promoted TimingData concept is participant registration. The public
protocol separates dimensions that legacy/proprietary formats may encode in one
compact field:

1. **entry origin** — how the registration entered SI-01;
2. **time source** — how its effective registration time was obtained.

Initial semantic values are:

```text
entryOrigin
  AUTOMATIC        normal electronic/observation path
  MANUAL           explicit operator/client registration

timeSource
  OBSERVED         time supplied by the accepted automatic observation
  SYSTEM_ASSIGNED  time assigned automatically when a manual registration is entered
  OPERATOR_ENTERED time explicitly entered by the operator
```

The dimensions are intentionally independent. In particular, a manual
registration may use a system-assigned current time or an operator-entered
effective time. Provider-specific one-character codes are not part of the public
protocol.

Record action is also explicit:

- `REGISTRATION` — creates one effective participant registration;
- `REGISTRATION_REVOKED` — appends a new record that revokes one earlier
  registration without modifying or deleting that historical record.

A revocation shall carry an explicit reference to the stable
`TimingDataRecordKey` of the registration being revoked. Its effective
registration/race time is the **same effective time as the referenced
registration**, not the wall-clock time at which the operator performs the
revocation. The revocation semantically retains the referenced registration's
entry-origin and time-source; these values are obtained from the referenced
record rather than reinterpreted from current operator input. A
separate record/commit timestamp records when the revocation fact itself was
created.

Conceptually:

```text
REGISTRATION
  origin = AUTOMATIC | MANUAL
  effectiveTime = accepted registration/race time

REGISTRATION_REVOKED
  reference = (TimingNodeId, SequenceNumber)
  effectiveTime = referenced registration effectiveTime
  recordedAt = time at which the revocation record was committed
```

This preserves the append-only history needed for audit and synchronisation:
the original registration remains present and the later revocation is another
ordered fact that references it. Any derived effective registration state belongs to consuming
domain/application business logic, while its visual representation belongs to
the client/presentation layer; neither changes the TimingData record model.

A proprietary TimingData translator may map these generic semantics to its own
legacy fields (for example add/remove markers), but those external encodings are
not part of the framework-owned protocol.

Additional record types such as starts, penalties and penalty revocations are
introduced only when their domain requirements are promoted.

Records are historical facts and are not silently overwritten when corrected or revoked.

## Registration sequence and stable record key

The registration sequence is **monotonically increasing per `TimingNodeId` / timing node**.

A new source stream starts with sequence **1**. Sequence **0 is reserved** and
shall not identify a normal committed TimingData record.

It is not scoped by location and it is not one global sequence across all registration systems.

Conceptually:

```text
TimingDataRecordKey = (TimingNodeId, SequenceNumber)
```

Example:

```text
source A:  1041, 1042, 1043, 1044, ...
source B:   551,  552,  553, ...
```

The location remains explicit data on each record:

```text
source=A  sequence=1042  location=7   type=REGISTRATION ...
source=A  sequence=1043  location=7   type=TIMING_NODE_STATE state=CLOSED ...
```

If the source is later associated with another location, the source sequence does not implicitly restart. This preserves one consistent source stream for higher-level synchronisation.

A receiving/upstream system can use the sequence for ordering and gap detection. Receiving `1041`, `1042`, `1044` from source `A` makes the missing `1043` visible.

![Registration traceability — sequence per timing node](../../../raw/prod/docs/assets/architecture/registration-stream-identity.svg)

### Illustrative TimingData record model

The Java shape below is illustrative. The architectural boundary is that
`TimingData` owns the public semantic record/protocol and its compatibility
rules; `LogBookItem` remains free to use a different internal shape and
proprietary providers only translate at the boundary.

```java
final class TimingDataRecord {
    private int version;                         // v1 = 1
    private TimingNodeId timingNodeId;
    private long sequenceNumber;
    private LocationID locationId;
    private TimingDataRecordType type;
    private TimingTimestamp effectiveTime;
    private TimingTimestamp recordedAt;
    private RegistrationOrigin origin;            // AUTOMATIC | MANUAL when applicable
    private RegistrationTimeSource timeSource;     // OBSERVED | SYSTEM_ASSIGNED | OPERATOR_ENTERED
    private RegistrationIdentity registrationIdentity; // canonical stored participant identity
    private TimingDataRecordKey reference;         // revocation/correction target
    private TimingDataRecordPayload payload;       // type-specific semantic data
}

final class TimingDataRecordKey {
    private TimingNodeId timingNodeId;
    private long sequenceNumber;
}
```

Names are illustrative; the important design is the TimingNode-scoped sequence,
explicit location association, append-only correction/revocation model, and the
distinction between an event's effective time and the time at which a later
record such as a revocation is committed.

### Sequence allocation

A sequence allocator is owned per `TimingNode`:

```java
interface RegistrationSequence {
    long next(TimingNodeId timingNodeId);
}
```

Conceptual processing:

```java
void acceptRegistration(RegistrationCandidate candidate) {
    TimingNodeId timingNode = candidate.timingNodeId();
    long sequence = registrationSequence.next(timingNode);

    LogBookItem item = logBookItemFactory.create(
        sequence,
        candidate.locationId(),
        candidate);

    logBook.append(item);

    TimingDataRecord record = timingData.toRecord(timingNode, item);
    storage.append(timingData.encode(record));
    upstream.enqueue(record);
}
```

The serialized timing node application path is a natural place to coordinate committed records, while sequence allocation remains scoped independently by `TimingNodeId`.

## Sequence persistence and synchronisation

Sequence allocation is a domain consistency mechanism, not a storage implementation detail.

Required direction:

- never reuse a committed `(TimingNodeId, SequenceNumber)` after restart;
- preserve monotonic order independently for each `TimingNode`;
- persist enough allocator state that restore cannot accidentally restart a source sequence;
- expose source + sequence in synchronisation/support data;
- support upstream gap/consistency detection;
- corrections/revocations refer to a stable earlier record key rather than mutating history.

Backup metadata should therefore be source-keyed, for example:

```text
registration.nextSequence.A  = 1045
registration.nextSequence.B  = 554
registration.nextSequence.R1 = ...   # exact reserve identifier form TBD
```

Whether sequence gaps are allowed is still a formal requirement question. **No reuse and monotonicity** are already known; contiguity across failed/aborted persistence still needs definition.

## Prepare-team registry

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

## Team and tag identities

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

`RegistrationIdentity` supports a semantic type discriminator plus number. The
first supported values are:

```text
STANDARD   number 1..350   allowed at LocationID 1..23
WOMEN      number 1..350   allowed at LocationID 24
MEN        number 1..350   allowed at LocationID 25
```

A proprietary translator may map these to/from its external split representation,
but external one-character codes are not public TimingData values.

Reserve transponders remain a `TagIdentity` concern and resolve to one of these
canonical registration identities; they do not add another
`RegistrationIdentity.type`.

Source identities such as `TagIdentity` may be retained/exposed separately when
an interface needs provenance or diagnostics; they are not substitutes for the
canonical registration identity stored by TimingData.

## In-memory authoritative state with file backup

The initial implementation direction is:

```text
live application
    |
    +-- TimingSystem (1..N)
    |     +-- UpstreamProtocol      sync/reconcile/ping semantics
    |     +-- TimingNode (1..N)
    |           +-- LogBook         0..N LogBookItem in memory
    |           +-- RegistrationState
    |           +-- NextUpTeams
    |           +-- StageStartTimes
    |           +-- RaceData
    |           +-- RegistrationSequenceState
    |
    +-- TimingData                  canonical record + codec contract
    |
    +-- simple file backup / restore
```

The application operates on typed in-memory structures rather than repeatedly parsing files during normal operation. `LogBookItem` is the LogBook's internal state shape; `TimingDataRecord` is produced through the TimingData contract when data crosses the persistence, Web or upstream interchange boundary. Files provide persistence/recovery, not the primary domain API.

Possible interfaces:

```java
interface LogBook {
    void append(LogBookItem item);
    List<LogBookItem> snapshot();
}

interface PrepareTeamRegistry {
    void add(TeamNumber team, InputSource source, Instant createdAt);
    void remove(TeamNumber team, InputSource source, Instant createdAt);
    List<TeamNumber> currentTeams();
    List<PrepareTeamEvent> history();
}

interface StageStartTimeRegistry {
    void replace(StartTimeSnapshot snapshot);
    StartTime find(TeamNumber teamNumber);
    StartTimeSnapshot snapshot();
}
```

Concrete implementations can use collections/maps appropriate to lookup patterns.

## Backup policy

The exact write policy still needs evidence and requirements. Candidates include:

- persist every accepted traceable event before acknowledging it;
- keep an append recovery journal plus periodic snapshots;
- atomically write current-state/reference snapshots using temporary-file + rename/replace;
- keep all source sequence allocator state in the same recoverable persistence set.

For the initial implementation, correctness and recoverability are more important than introducing a database engine.

Status should eventually expose at least:

```text
backup state
last successful backup time
last restore result
last registration sequence per timing node
last ready-team sequence
last reference-data synchronisation time/version
```

## Startup restore

A possible startup sequence is:

```text
start process
   |
   v
load configuration
   |
   v
load trace journals / snapshots / timing node sequence metadata
   |
   v
reconstruct in-memory repositories and derived state
   |
   v
load reference-data backup
   |
   v
validate sequence state against restored records
   |
   v
start interfaces/devices
   |
   v
connect/synchronise with backoffice when available
```

For ready teams, restoration can restore a snapshot or replay the journal:

```java
PrepareTeamRegistry prepareTeams = restorePrepareTeamRegistry(backup.prepareTeamRegistry());
```

A missing/corrupt backup or inconsistent sequence metadata must result in explicit status rather than silently looking healthy.

## Start-time and reserve-tag synchronisation

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

## Keypad behaviour

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

## Display model

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

## Display V1 — passive CAN display

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

## Display V2 — smart Wi-Fi display

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

## Registration versus ready-team display state

These flows remain separate:

```text
RFID/manual/start/penalty/system-open
          |
          v
 RegistrationLedger
          |
          +--> local results/ranking
          +--> backoffice outbox

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

## Synchronisation and threading

Registration records, ready-team events, reference-data updates and UI/device commands enter through controlled serialized state-change boundaries so in-memory transitions are deterministic.

File writes/network sends should not stall those boundaries indefinitely. Durability semantics need explicit requirements, particularly for traceable registration records whose source sequence is used for upstream consistency checking.

One possible pattern is:

```text
serial handler
   |
   +-- allocate source sequence
   +-- append in-memory ledger
   +-- update derived state
   +-- create immutable persistence work
   +-- schedule durable file write
   +-- create downstream backoffice work
```

However, because upstream systems depend on the sequence stream, formal requirements must decide when a sequence/record is considered committed and which failure gaps are legal.

## Candidate requirements

Temporary identifiers only; these are not yet formal requirements.

### Registration identity and traceability

- **CAND-REG-001** — Each registration system/source shall have a stable `TimingNodeId`.
- **CAND-REG-002** — Each physical location shall have a unique `LocationID` in the known domain range `1..25`.
- **CAND-REG-003** — Each committed registration entry shall contain both `TimingNodeId` and `LocationID`.
- **CAND-REG-004** — Each committed registration entry shall receive a monotonically increasing sequence number scoped to its `TimingNodeId`; a new stream starts at 1 and sequence 0 is reserved.
- **CAND-REG-005** — The stable registration record identity shall include `TimingNodeId` and sequence number so upstream systems can order records and detect gaps per timing node.
- **CAND-REG-006** — Registration sequence allocation shall survive restart/restore and shall not reuse previously committed sequence numbers for a source.
- **CAND-REG-007** — Opening and closing a TimingNode shall each create a traceable TimingData state-change record with generic semantic state `OPEN` or `CLOSED`; provider-specific encodings belong to the selected TimingData implementation.
- **CAND-REG-008** — Registration corrections and revocations shall remain traceable to earlier record identity and shall not silently overwrite historical records.
- **CAND-REG-009** — Participant registrations shall distinguish automatic versus manual entry origin without using different record-identity rules.
- **CAND-REG-010** — Manual registrations shall distinguish a system-assigned effective time from an operator-entered effective time.
- **CAND-REG-011** — A participant-registration revocation shall be represented as a new append-only record that references the original registration record key; TimingData shall not prescribe the consuming client's visibility/presentation behaviour for that registration.
- **CAND-REG-012** — A registration-revocation record shall retain the effective registration/race time, entry origin and time source of the referenced registration while separately recording when the revocation record itself was committed.

### Tag/team identity

- **CAND-TAG-001** — The registration path shall use a normalised RFID identity consisting of prefix plus decoded number.
- **CAND-TAG-002** — Tag decoding shall distinguish normal versus reserve-tag prefix semantics.
- **CAND-TAG-003** — The physical tag postfix/copy identifier shall be removed from the canonical registration identity.
- **CAND-TAG-004** — A normalised `TagIdentity` shall resolve to the canonical `RegistrationIdentity`; normal tags resolve deterministically while reserve tags use locally available backoffice-synchronised mapping data.
- **CAND-TAG-005** — A manual registration shall resolve its operator-supplied `TeamIdentity` to the same canonical `RegistrationIdentity` used by automatic registrations.
- **CAND-TAG-006** — `RegistrationIdentity` shall support semantic types `STANDARD`, `WOMEN` and `MEN` plus registration/team number without exposing proprietary one-character type codes in the public protocol.
- **CAND-TAG-007** — `STANDARD` registrations shall use numbers 1..350 at locations 1..23; `WOMEN` registrations shall use numbers 1..350 at location 24; `MEN` registrations shall use numbers 1..350 at location 25.
- **CAND-TAG-008** — Reserve transponders shall remain reserve `TagIdentity` values and resolve to a canonical `RegistrationIdentity`; reserve shall not become a separate RegistrationIdentity type.
- **CAND-TAG-009** — RFID normalisation shall not require a physical postfix on every tag; when a postfix is present it is physical tag-copy detail and shall not form part of `RegistrationIdentity`.

### Local data and backup

- **CAND-DATA-001** — The initial implementation shall maintain active registration, ready-team and reference state in application data structures without requiring an external database engine.
- **CAND-DATA-002** — The system shall back up locally required traceable history/state to simple persistent files and shall be able to restore that information during startup.
- **CAND-DATA-003** — Backup/restore failures shall be represented in system status.
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
- Are sequence gaps acceptable after failed/aborted persistence provided committed numbers are never reused?
- Which durability point makes a source sequence/record committed and eligible for backoffice transmission?
- What sequence numeric width/wraparound policy is required?
- Which public clients/interfaces, if any, need source `TagIdentity` provenance in addition to the canonical `RegistrationIdentity`?
- Verify the legacy "unknown team" registration semantics before deciding whether the public model needs an explicit unknown-registration identity/state; do not promote legacy location-specific codes directly.
- Which operational events besides the promoted TimingNode `OPEN` / `CLOSED` state-change records belong in the registration stream?
- Which additional generic fields, if any, are required on a lifecycle/state-change record beyond its normal TimingData identity/location/sequence/time fields and semantic state?
- Should ready-team events use their own sequence stream or a broader operational event sequence?
- Which state must survive restart: all registration history, all ready-team history, current ready-team snapshot, start times, reserve tags, display revision, outbox, or all of these?
- Is snapshot-only backup sufficient for registrations/ready-team events, or should traceable changes use an append journal plus periodic snapshot?
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

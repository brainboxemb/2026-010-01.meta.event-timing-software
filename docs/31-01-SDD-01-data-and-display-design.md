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

Every waypoint system/system has a `UniqueID`.

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

`Waypoint` identity, `LocationID`, hardware `RegistrationAssetId` and logical `UniqueID` are separate namespaces. Deployment configuration relates them; code must not infer one identity from another.

## Registration ledger

The registration ledger contains timing/registration-domain and traceable operational records such as:

```text
SYSTEM_OPEN
PASSAGE
START
MANUAL_REGISTRATION
PENALTY
PENALTY_REVOKED
```

`SYSTEM_OPEN` is explicitly part of the registration stream: opening a location/waypoint is not merely a transient status change; it produces a synchronisable traceable entry.

Additional operational record types may be added only when domain requirements justify them.

Records are historical facts and are not silently overwritten when corrected or revoked.

## Registration sequence and stable record key

The registration sequence is **monotonically increasing per `UniqueID` / waypoint**.

It is not scoped by location and it is not one global sequence across all registration systems.

Conceptually:

```text
RegistrationRecordKey = (UniqueID, SequenceNumber)
```

Example:

```text
source A:  1041, 1042, 1043, 1044, ...
source B:   551,  552,  553, ...
```

The location remains explicit data on each record:

```text
source=A  sequence=1042  location=7   type=PASSAGE  ...
source=A  sequence=1043  location=7   type=SYSTEM_OPEN ...
```

If the source is later associated with another location, the source sequence does not implicitly restart. This preserves one consistent source stream for higher-level synchronisation.

A receiving/upstream system can use the sequence for ordering and gap detection. Receiving `1041`, `1042`, `1044` from source `A` makes the missing `1043` visible.

![Registration traceability — sequence per waypoint](../../../raw/prod/docs/assets/architecture/registration-stream-identity.svg)

### Illustrative record model

```java
final class RegistrationRecord {
    private UniqueID uniqueID;
    private long sequenceNumber;
    private LocationID locationId;
    private RegistrationType type;
    private Instant observedAt;
    private Instant createdAt;
    private RegistrationOrigin origin;
    private TeamNumber teamNumber;              // when applicable
    private RegistrationRecordKey reference;    // corrections/revocations
    private RegistrationPayload payload;         // type-specific data
}

final class RegistrationRecordKey {
    private UniqueID uniqueID;
    private long sequenceNumber;
}
```

Names are illustrative; the important design is the waypoint-scoped sequence and explicit location association.

### Sequence allocation

A sequence allocator is owned per waypoint system:

```java
interface RegistrationSequence {
    long next(UniqueID waypointId);
}
```

Conceptual processing:

```java
void acceptRegistration(RegistrationCandidate candidate) {
    UniqueID waypoint = candidate.uniqueID();
    long sequence = registrationSequence.next(waypoint);

    RegistrationRecord record = registrationFactory.create(
        source,
        sequence,
        candidate.locationId(),
        candidate);

    registrationRepository.append(record);
    registrationState.apply(record);
    backupCoordinator.registrationChanged(registrationRepository.snapshot());
    outbox.enqueue(RegistrationCommitted.from(record));
}
```

The serialized waypoint application path is a natural place to coordinate committed records, while sequence allocation remains scoped independently by `UniqueID`.

## Sequence persistence and synchronisation

Sequence allocation is a domain consistency mechanism, not a storage implementation detail.

Required direction:

- never reuse a committed `(UniqueID, SequenceNumber)` after restart;
- preserve monotonic order independently for each waypoint system;
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

Keypad input indicates which teams should prepare at the waypoint/exchange point. A keypad action is not itself a passage/start/penalty registration.

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

- **current state** — which teams must currently prepare at the waypoint/exchange point;
- **traceable history** — the keypad/operator add/remove mutations needed for audit and restore.

The history is an internal persistence/state aspect of the registry, not a separate architecture component.

Illustrative internal history record:

```java
final class PrepareTeamEvent {
    private long sequenceNumber;
    private WaypointId waypointId;
    private PrepareTeamEventType type; // ADDED / REMOVED
    private TeamNumber teamNumber;
    private Instant createdAt;
    private InputSource source;         // keypad / UI / API / test
}
```

The prepare-team history sequence is a separate design question from the `UniqueID`-scoped sequence. It may use its own internal registry sequence or later a broader operational-event sequence, but it must not accidentally consume/alter a `UniqueID` registration sequence unless requirements explicitly make a prepare-team action a registration-stream entry.

## Team and tag identities

Decoded team numbers are in the known range:

```text
TeamNumber = 0..999
```

An RFID tag identity ultimately contains:

```text
prefix + team number + postfix
```

Known semantics:

- a dedicated prefix indicates a reserve tag;
- two physical tags exist for the same team/identity;
- the postfix distinguishes those two physical tag copies;
- exact encoded prefix/postfix values and encryption/protocol format are not defined in this public design.

Reserve-tag identities are resolved through locally available backoffice-synchronised mapping data before normal participant/team processing.

## In-memory authoritative state with file backup

The initial implementation direction is:

```text
live application
    |
    +-- WaypointJournal             source-ordered registration/history in memory
    +-- RegistrationState           current/derived registration views
    |
    +-- PrepareTeamRegistry   current teams-to-prepare + traceable mutation history
    |
    +-- StageStartTimeRegistry      stage start-time reference data in memory
    +-- RaceData                    participant/team/tag reference data in memory
    |
    +-- RegistrationSequenceState   next sequence per UniqueID
    |
    +-- simple file backup / restore
```

The application operates on typed in-memory structures rather than repeatedly parsing files during normal operation. Files provide persistence/recovery, not the primary domain API.

Possible interfaces:

```java
interface WaypointJournal {
    void append(RegistrationRecord record);
    List<RegistrationRecord> snapshot();
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
last registration sequence per waypoint
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
load trace journals / snapshots / waypoint sequence metadata
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

- **CAND-REG-001** — Each registration system/source shall have a stable `UniqueID`.
- **CAND-REG-002** — Each physical location shall have a unique `LocationID` in the known domain range `1..25`.
- **CAND-REG-003** — Each committed registration entry shall contain both `UniqueID` and `LocationID`.
- **CAND-REG-004** — Each committed registration entry shall receive a monotonically increasing sequence number scoped to its `UniqueID`.
- **CAND-REG-005** — The stable registration record identity shall include `UniqueID` and sequence number so upstream systems can order records and detect gaps per waypoint.
- **CAND-REG-006** — Registration sequence allocation shall survive restart/restore and shall not reuse previously committed sequence numbers for a source.
- **CAND-REG-007** — Opening a location/waypoint shall create a traceable registration-stream entry.
- **CAND-REG-008** — Registration corrections and revocations shall remain traceable to earlier record identity and shall not silently overwrite historical records.

### Tag/team identity

- **CAND-TAG-001** — Decoded team numbers shall support the known range `0..999`.
- **CAND-TAG-002** — Tag decoding shall distinguish normal versus reserve-tag prefix semantics.
- **CAND-TAG-003** — Tag decoding shall retain the postfix/copy identity needed to distinguish the two physical tags associated with one team identity.
- **CAND-TAG-004** — Reserve tags shall be resolvable using locally available mapping data synchronised from the backoffice.

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
- Is each physical producer configured with exactly one `UniqueID`, and how are reserve/virtual waypoint systems associated with registration hardware?
- At what value does a new source sequence start?
- Are sequence gaps acceptable after failed/aborted persistence provided committed numbers are never reused?
- Which durability point makes a source sequence/record committed and eligible for backoffice transmission?
- What sequence numeric width/wraparound policy is required?
- Which operational events besides `SYSTEM_OPEN` belong in the registration stream?
- What payload is required on a `SYSTEM_OPEN` entry?
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

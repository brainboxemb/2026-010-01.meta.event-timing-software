# Data and display architecture detail

Status: working draft / non-authoritative

This document refines the initial timing-system architecture for local data ownership, backup/restore, keypad behaviour, traceable records, and the two display generations.

The initial design does **not** require a conventional embedded database. Runtime state is held in typed Java data structures/repositories and is backed up to simple files so the application can restore its state after restart.

A second important distinction is that **timing/registration records** and **teams prepared through the keypad** are two different information models. Both need traceability/persistence, but they have different meaning and different current-state projections.

## Two traceable data flows

### 1. Registration ledger

The registration ledger contains actual timing/registration-domain records such as:

```text
PASSAGE
START
MANUAL_REGISTRATION
PENALTY
PENALTY_REVOKED
```

These records are traceable history. They are not silently overwritten when something is corrected or revoked.

Each accepted registration record shall receive a unique sequence number so its creation/order is traceable.

Conceptually:

```text
RegistrationLedger
  1001  PASSAGE            team 123  10:14:03.421
  1002  PENALTY            team 123  code ...
  1003  PENALTY_REVOKED    ref 1002
  1004  MANUAL_REGISTRATION team 456 ...
```

The exact uniqueness scope still needs a formal requirement. A practical first design is a monotonically increasing `long` sequence **per logical TimingSystem**, with `(timingSystemId, sequenceNumber)` forming the stable trace reference.

Illustrative model:

```java
final class RegistrationRecord {
    private long sequenceNumber;
    private TimingSystemId timingSystemId;
    private RegistrationType type;
    private Instant observedAt;
    private Instant createdAt;
    private RegistrationSource source;
    private TeamId teamId;
    private Long referencedSequenceNumber;
}
```

The serialized `TimingSystem` execution path is a natural place to allocate this sequence because it already owns ordering.

```java
void acceptRegistration(RegistrationCandidate candidate) {
    long sequence = registrationSequence.next();
    RegistrationRecord record = registrationFactory.create(sequence, candidate);

    registrationRepository.append(record);
    registrationState.apply(record);
    backupCoordinator.registrationChanged(registrationRepository.snapshot());
    outbox.enqueue(RegistrationCommitted.from(record));
}
```

### 2. Ready-team journal and current queue

Keypad input has a different purpose. It indicates which team numbers should be **prepared/ready** for local operation/display. A keypad action is not itself a passage/start/penalty registration.

The keypad can:

```text
add team to ready list
remove team from ready list
```

Those actions must still be registered/stored so the operational history is traceable and the state can be recovered.

Conceptually:

```text
ReadyTeamJournal
  501  TEAM_ADDED     123
  502  TEAM_ADDED     456
  503  TEAM_REMOVED   123
          |
          | apply/replay
          v
ReadyTeamState
  [456]
```

This gives two useful representations:

- **journal/history** — what operators/keypad did and in what order;
- **current state** — which teams are currently ready.

A possible record is:

```java
final class ReadyTeamEvent {
    private long sequenceNumber;
    private TimingSystemId timingSystemId;
    private ReadyTeamEventType type; // ADDED / REMOVED
    private TeamNumber teamNumber;
    private Instant createdAt;
    private InputSource source;       // keypad / UI / API / test
}
```

The ready-team sequence may use its own sequence stream, or later we may decide to use one timing-system-wide operational sequence across several journals. That choice should be explicit in the formal requirements/data design.

## In-memory authoritative state with file backup

The initial implementation direction is:

```text
live application
    |
    +-- RegistrationRepository      history / ledger in memory
    +-- RegistrationState           current derived registration view
    |
    +-- ReadyTeamEventRepository    keypad/operator history in memory
    +-- ReadyTeamState              current ready-team queue/list
    |
    +-- StartTimeRepository         backoffice reference data in memory
    +-- ReserveTagRepository        backoffice reference data in memory
    |
    +-- simple file backup / restore
```

The application should operate on typed in-memory structures rather than repeatedly parsing files during normal operation.

Files provide persistence/recovery, not the primary domain API.

Possible interfaces:

```java
interface RegistrationRepository {
    void append(RegistrationRecord record);
    List<RegistrationRecord> snapshot();
}

interface ReadyTeamEventRepository {
    void append(ReadyTeamEvent event);
    List<ReadyTeamEvent> snapshot();
}

interface ReadyTeamState {
    void apply(ReadyTeamEvent event);
    List<TeamNumber> currentTeams();
}

interface StartTimeRepository {
    void replace(StartTimeSnapshot snapshot);
    StartTime find(TeamId teamId);
    StartTimeSnapshot snapshot();
}
```

The concrete implementations can use collections/maps appropriate to the lookup patterns.

## Traceability and sequence allocation

Sequence allocation is not just a storage detail. It is part of the traceability model.

Desired properties:

- never reuse a sequence number after restart;
- preserve ordering of accepted events within its defined sequence scope;
- persist enough sequence metadata that restoring from backup does not restart numbering at zero;
- corrections/revocations refer to earlier records rather than mutating their history;
- UI/API/logging can show sequence numbers for support and reconciliation.

Example backup metadata:

```text
registration.nextSequence = 1005
readyTeam.nextSequence    = 504
```

Whether sequence numbers must be contiguous is a separate question. Usually **unique and monotonically increasing** is more important than guaranteeing no gaps, especially around failed writes/recovery.

## Backup policy

The exact write policy still needs evidence and requirements. Candidates include:

- persist every accepted traceable event before acknowledging it;
- keep an append recovery journal plus periodic snapshots;
- atomically write current-state/reference snapshots using temporary-file + rename/replace;
- keep sequence allocator state in the same recoverable persistence set.

For the initial implementation, correctness and recoverability are more important than introducing a database engine.

Status should eventually expose at least:

```text
backup state
last successful backup time
last restore result
last registration sequence
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
load trace journals / snapshots / sequence metadata
   |
   v
reconstruct in-memory repositories and derived state
   |
   v
load reference-data backup
   |
   v
start interfaces/devices
   |
   v
connect/synchronise with backoffice when available
```

For ready teams, restoration can either restore a snapshot or replay the journal:

```java
ReadyTeamState readyTeams = new InMemoryReadyTeamState();
for (ReadyTeamEvent event : readyTeamEvents.snapshot()) {
    readyTeams.apply(event);
}
```

A missing/corrupt backup must result in explicit status rather than silently looking healthy.

## Start-time data synchronisation

Start times are backoffice-owned reference data that must also be available locally.

The timing application maintains a local in-memory start-time repository and synchronises it from the backoffice.

A useful synchronisation model is snapshot/version based:

```text
Backoffice
   |
   | StartTimeSnapshot(version, entries)
   v
Backoffice adapter
   |
   v
TimingSystem message queue
   |
   v
ReferenceDataService
   |
   +--> validate version/content
   +--> replace/update StartTimeRepository
   +--> update ReferenceDataSnapshot
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

The same pattern can be used for reserve-tag conversion data.

Open questions include full-snapshot versus delta updates, version identifiers, correction semantics, and whether updates are per timing system or runtime-wide.

## Keypad behaviour

The CAN keypad can both add and remove team numbers from the ready-team state.

Possible incoming messages:

```text
KeypadTeamAddRequested(teamNumber)
KeypadTeamRemoveRequested(teamNumber)
```

Both enter the normal `TimingSystem` queue. The handler creates a traceable `ReadyTeamEvent`, stores it, applies it to current state, and then rebuilds/publishes display data.

```java
void handle(KeypadTeamAddRequested command) {
    ReadyTeamEvent event = new ReadyTeamEvent(
        readyTeamSequence.next(),
        timingSystemId,
        ADDED,
        command.getTeamNumber(),
        clock.instant(),
        KEYPAD);

    readyTeamEvents.append(event);
    readyTeams.apply(event);
    backupCoordinator.readyTeamsChanged(readyTeamEvents.snapshot());
    displayService.readyTeamsChanged(readyTeams.currentTeams());
}
```

Removing a team follows the same path with `REMOVED`.

The application, not the keypad, remains authoritative for the current ready-team list.

Duplicate-add, remove-not-present, ordering and capacity behaviour need explicit requirements.

## Display model

Display data is derived from **current state**, not by forwarding keypad history directly.

The preferred direction is:

```text
ReadyTeamJournal          StartTimeRepository
      |                          |
      v                          |
ReadyTeamState ------------------+
      |                          |
      +----> DisplayModelBuilder <+
                    |
                    v
              DisplayModel
              /          \
             v            v
      V1 CAN adapter    V2 data session
```

A conceptual model might contain:

```java
final class DisplayModel {
    private List<TeamDisplayData> readyTeams;
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

Fields are illustrative. The display IDD will ultimately define the contract.

## Display V1 — passive CAN display

Display V1 is relatively passive. It must be actively driven by the timing application.

Crucially, V1 does not need to reconstruct add/remove actions. The application derives the **current ready-team list** and actively writes the appropriate complete/current display state.

```java
void refreshV1() {
    DisplayModel current = displayModelService.current();
    canDisplayV1.apply(current);
}
```

The V1 adapter translates the model into the CAN protocol/device commands needed to keep the physical display correct.

Implications:

- `TEAM_ADDED` updates `ReadyTeamState`, then triggers a refreshed current list;
- `TEAM_REMOVED` updates `ReadyTeamState`, then triggers a refreshed current list;
- after V1 discovery/reconnect, send a full refresh from current state;
- a V1 reset does not destroy the application's ready-team state;
- status should distinguish discovered/reachable/last successfully updated.

## Display V2 — smart Wi-Fi display

Display V2 is a smarter network client. The timing application communicates domain/display **data**, while V2 owns its presentation/rendering behaviour.

The intended connection direction remains:

1. timing application advertises an mDNS service;
2. V2 discovers the service;
3. V2 connects to the timing application;
4. application sends current ready-team/reference/result data;
5. application and V2 keep the data synchronised while connected.

The data can still be represented as a revisioned snapshot/model even though V2 is free to render it differently from V1.

```java
void onDisplayV2Connected(DisplaySession session) {
    session.send(displayModelService.current());
}
```

A later optimisation may send deltas, but a reconnect must always be recoverable through a complete current snapshot.

## Registration versus ready-team display state

These flows must remain separate:

```text
RFID/manual/start/penalty
          |
          v
 RegistrationLedger
          |
          +--> local results/ranking
          +--> backoffice outbox

keypad/UI prepare/remove team
          |
          v
  ReadyTeamJournal
          |
          v
    ReadyTeamState
          |
          +--> V1 current list
          +--> V2 synchronised data
```

A team can therefore be ready for display without having produced a registration, and a registration can exist independently from whether that team is currently in the ready list.

The application may later define interactions between the two (for example automatically removing a team after a successful start/passage), but that must be an explicit domain requirement rather than an accidental display side effect.

## Synchronisation and threading

Registration records, ready-team events, reference-data updates and UI/device commands all enter through the timing-system serialized execution boundary so their in-memory state transitions are deterministic.

File writes/network sends should not stall that boundary indefinitely. Durability semantics need explicit requirements, particularly for traceable registration/ready-team events.

One likely pattern is:

```text
serial handler
   |
   +-- allocate sequence
   +-- append in-memory journal
   +-- update derived state
   +-- create immutable persistence snapshot/event
   +-- schedule durable file write
   +-- create downstream display/backoffice work
```

For safety-critical traceability we may instead require durable persistence acknowledgement before considering the event committed. That remains to be decided.

## Candidate requirements

Temporary identifiers only; these are not yet formal requirements.

### Registration traceability

- **CAND-REG-001** — Each accepted registration-domain record shall receive a unique monotonically increasing sequence number within its defined sequence scope.
- **CAND-REG-002** — Registration corrections and revocations shall remain traceable to the original registration record and shall not silently overwrite historical records.
- **CAND-REG-003** — Registration sequence allocation shall remain consistent across application restart/restore and shall not reuse previously allocated committed sequence numbers.

### Local data and backup

- **CAND-DATA-001** — The initial implementation shall maintain active registration, ready-team and reference state in application data structures without requiring an external database engine.
- **CAND-DATA-002** — The system shall back up locally required traceable history/state to simple persistent files and shall be able to restore that information during startup.
- **CAND-DATA-003** — Backup/restore failures shall be represented in system status.
- **CAND-DATA-004** — The local start-time data set shall be synchronisable from the backoffice and remain available after loss of live backoffice connectivity.
- **CAND-DATA-005** — The system shall track enough start-time synchronisation metadata to determine whether the local data is current/stale relative to the latest accepted update.

### Ready-team/keypad data

- **CAND-READY-001** — The system shall maintain a ready-team state that is logically separate from timing/registration records.
- **CAND-READY-002** — Adding or removing a team from the ready-team state shall create a traceable persisted event.
- **CAND-READY-003** — Ready-team events shall be processed through the normal timing-system state-change queue.
- **CAND-READY-004** — The ready-team state shall be recoverable after application restart from locally persisted information.
- **CAND-READY-005** — The keypad shall be able to request both addition and removal of a team number.

### Displays

- **CAND-DISP-004** — The application shall derive display data from current timing/reference/ready-team state rather than requiring displays to reconstruct operational event history.
- **CAND-DISP-005** — Display V1 shall be actively controlled by the application and shall receive the current ready-team display state/list after relevant changes or reconnect.
- **CAND-DISP-006** — Display V2 shall consume synchronised timing/ready-team/reference data from the application and shall own its local presentation/rendering behaviour.
- **CAND-DISP-007** — When Display V2 connects or reconnects, the application shall be able to provide a complete current data snapshot independent of previously delivered incremental updates.
- **CAND-DISP-008** — Display data shall support a revision/version mechanism or equivalent means of detecting stale/missed state.

## Open questions

- Is the registration sequence unique per `TimingSystem`, per running application, or globally across devices/events?
- Should ready-team events use their own sequence stream or one common operational event sequence?
- Are sequence-number gaps acceptable after failures, provided numbers are never reused?
- Which traceable events must be durably written before the operator/device receives acknowledgement?
- Which state must survive restart: all registration history, all ready-team history, current ready-team snapshot, start times, reserve tags, display revision, outbox, or all of these?
- Is snapshot-only backup sufficient for registrations/ready-team events, or should traceable changes use an append journal plus periodic snapshot?
- How frequently may simple backup files be written without unnecessary SD-card wear?
- Should reference data use one combined backup snapshot or separate files per data set?
- Is start-time synchronisation always a full snapshot, or can the backoffice send deltas/corrections?
- What is the keypad protocol for distinguishing add versus remove?
- What should happen on duplicate add or removal of a team that is not ready?
- Is ready-team ordering significant and, if so, is it insertion order, start-time order, or another rule?
- How many teams can be ready concurrently?
- Should a successful start/passage automatically affect the ready-team list, or must that always be an explicit action?
- Does V1 retain any useful state across reconnect/power interruption or must every connection be treated as blank/unknown?
- What exact data fields does V2 need, and which presentation decisions belong exclusively inside V2?

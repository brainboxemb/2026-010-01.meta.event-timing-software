# Data and display architecture detail

Status: working draft / non-authoritative

This document refines the initial timing-system architecture for local data ownership, backup/restore, keypad behaviour, and the two display generations.

The important correction is that the initial design does **not** require a conventional embedded database. Runtime state is held in Java data structures/repositories and is backed up to simple files so the application can restore its state after restart.

## In-memory authoritative state with file backup

The initial implementation direction is:

```text
live application
    |
    +-- RegistrationRepository   (Java data structures)
    +-- StartTimeRepository      (Java data structures)
    +-- ReserveTagRepository     (Java data structures)
    +-- DisplayModel             (Java data structures)
    |
    +-- simple file backup / restore
```

The application should operate on typed in-memory data structures rather than repeatedly querying/parsing files during normal operation.

Files provide persistence/recovery, not the primary domain API.

Possible interfaces:

```java
interface RegistrationRepository {
    void add(Registration registration);
    List<Registration> findAll();
}

interface StartTimeRepository {
    void replace(StartTimeSnapshot snapshot);
    StartTime find(TeamId teamId);
    StartTimeSnapshot snapshot();
}

interface ReferenceDataBackup {
    void save(ReferenceDataSnapshot snapshot);
    ReferenceDataSnapshot load();
}
```

The concrete in-memory implementation can use collections/maps appropriate to the lookup patterns.

### Backup policy

The exact write policy still needs evidence and requirements. Candidates include:

- save after every accepted state-changing operation;
- coalesce several rapid changes and write shortly afterwards;
- maintain an append-oriented recovery log plus occasional snapshot;
- write snapshots atomically using temporary-file + rename/replace.

For the initial simple implementation, correctness and recoverability are more important than introducing a database engine.

Status should eventually expose at least:

```text
backup state
last successful backup time
last restore result
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
load local backup files
   |
   v
construct in-memory repositories
   |
   v
start interfaces/devices
   |
   v
connect/synchronise with backoffice when available
```

Pseudocode:

```java
ReferenceDataSnapshot localReferenceData = referenceBackup.load();
StartTimeRepository startTimes = new InMemoryStartTimeRepository();
ReserveTagRepository reserveTags = new InMemoryReserveTagRepository();

startTimes.replace(localReferenceData.getStartTimes());
reserveTags.replace(localReferenceData.getReserveTags());
```

A missing/corrupt backup must result in explicit status rather than silently looking healthy.

## Start-time data synchronisation

Start times are backoffice-owned reference data that must also be available locally.

The timing application therefore maintains a local in-memory start-time repository and synchronises it from the backoffice.

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
    eventPublisher.publish(new StartTimesChanged(incoming.getVersion()));
}
```

The same pattern can be used for reserve-tag conversion data.

Open questions include full-snapshot versus delta updates, version identifiers, correction semantics, and whether updates are per timing system or runtime-wide.

## Keypad behaviour

The CAN keypad can both add and remove team numbers.

The application should therefore treat keypad input as state-changing commands rather than only as a one-way `TeamNumberEntered` event.

Possible messages:

```text
TeamAdded(teamNumber)
TeamRemoved(teamNumber)
```

or, if the keypad protocol provides lower-level button actions:

```text
KeypadTeamAddRequested(teamNumber)
KeypadTeamRemoveRequested(teamNumber)
```

Both enter the normal `TimingSystem` queue before mutating application state.

```text
CAN frame
  -> KeypadAdapter
  -> TeamAdded / TeamRemoved
  -> TimingSystem ingress queue
  -> TeamSelectionService
  -> DisplayModel changed
  -> DisplayService
```

The application, not the keypad, remains authoritative for the current selected/visible team set.

Example model:

```java
final class TeamSelection {
    private final LinkedHashSet<TeamNumber> teams;

    void add(TeamNumber team) {
        teams.add(team);
    }

    void remove(TeamNumber team) {
        teams.remove(team);
    }

    List<TeamNumber> orderedTeams() {
        return new ArrayList<TeamNumber>(teams);
    }
}
```

The actual ordering/duplicate rules need requirements.

## Display model

Because Display V1 and Display V2 have different intelligence, the application should avoid exposing only low-level imperative display commands as the domain-facing abstraction.

The preferred direction is:

```text
TimingSystem state
   |
   v
DisplayService
   |
   v
DisplayModel
   |
   +------> V1 CAN adapter -> active device commands
   |
   +------> V2 data session -> model/data synchronisation
```

A conceptual model might contain:

```java
final class DisplayModel {
    private List<TeamDisplayData> teams;
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

The model should carry a revision/version so clients can detect stale or missed updates.

## Display V1 — passive CAN display

Display V1 is relatively passive. It must be actively driven by the timing application.

The V1 adapter translates `DisplayModel` changes into the CAN protocol/device commands required to keep the display correct.

```java
final class CanDisplayV1Adapter implements DisplaySink {
    public void apply(DisplayModel model) {
        CanDisplayFrameSet frames = renderer.render(model);
        for (CanFrame frame : frames.frames()) {
            canPort.send(frame);
        }
    }
}
```

This adapter owns transport/protocol rendering. The timing-system domain does not know individual CAN display commands.

Implications:

- when a team is added, the application explicitly drives the changed display state;
- when a team is removed, the application explicitly clears/updates the relevant display content;
- after V1 is rediscovered/reconnected, the adapter may need a **full refresh** because the display cannot be assumed to retain correct state;
- status should distinguish `discovered`, `reachable`, and `last successfully updated` where possible.

## Display V2 — smart Wi-Fi display

Display V2 is a smarter network client. The timing application does not render/drive its presentation at the same low level; it communicates the required data/model and V2 decides how to present it.

The intended connection direction remains:

1. timing application advertises an mDNS service;
2. V2 discovers the service;
3. V2 connects to the timing application;
4. application sends a full current data snapshot;
5. application and display keep that data synchronised while connected.

```text
Timing application
   |
   | mDNS: service available
   v
local Wi-Fi network
   ^
   | discover + connect
Display V2
   |
   | request/current revision
   v
Timing application
   |
   | full snapshot / later updates
   v
Display V2 local presentation logic
```

Pseudocode:

```java
void onDisplayV2Connected(DisplaySession session) {
    session.send(displayModelService.currentSnapshot());
}

void onDisplayModelChanged(DisplayModel model) {
    for (DisplaySession session : v2Sessions.connectedSessions()) {
        session.send(model);
    }

    displayV1.apply(model);
}
```

A later optimisation may send deltas, but a reconnect must always be recoverable through a complete snapshot.

The application remains the authority for timing/team data; V2 is authoritative only for its own presentation/rendering behaviour.

## Start times and display data

Because start times are held locally, both display generations can continue to receive useful data even when live internet/backoffice connectivity is temporarily unavailable.

A typical flow is:

```text
Backoffice start-time synchronisation
          |
          v
StartTimeRepository (memory)
          |
          +-- simple backup file
          |
          v
TimingCalculationService
          |
          v
DisplayModel
          |
          +--> V1: rendered into CAN commands
          +--> V2: synchronised as data
```

This means display state is derived from the same locally available domain/reference data used for local elapsed-time/ranking calculations.

## Synchronisation and threading

Reference-data updates, keypad add/remove operations, and display-relevant timing changes must follow the same ordering rules as other timing-system state changes.

They should therefore become messages processed by the `TimingSystem` serialized execution boundary.

Potential blocking file writes and network sends should not stall that boundary indefinitely.

One possible pattern is:

```java
void handle(TeamAdded message) {
    teamSelection.add(message.getTeam());
    DisplayModel snapshot = displayModelService.rebuild(stateSnapshot());

    backupCoordinator.requestBackup(stateSnapshot());
    displayPublisher.publish(snapshot);
}
```

`requestBackup()` and `publish()` may hand immutable snapshots to I/O workers. Completion/failure events can come back through the queue and update status.

Durability semantics — especially whether a registration must be written before downstream display/backoffice publication — need explicit requirements.

## Candidate requirements

Temporary identifiers only; these are not yet formal requirements.

### Local data and backup

- **CAND-DATA-001** — The initial implementation shall maintain active registration/reference/display state in application data structures without requiring an external database engine.
- **CAND-DATA-002** — The system shall back up the locally required state to simple persistent files and shall be able to restore that state during startup.
- **CAND-DATA-003** — Backup/restore failures shall be represented in system status.
- **CAND-DATA-004** — The local start-time data set shall be synchronisable from the backoffice and remain available after loss of live backoffice connectivity.
- **CAND-DATA-005** — The system shall track enough start-time synchronisation metadata to determine whether the local data is current/stale relative to the latest accepted update.

### Keypad

- **CAND-KEYPAD-001** — The CAN-connected keypad shall be able to request addition of a team number to the current timing/display state.
- **CAND-KEYPAD-002** — The CAN-connected keypad shall be able to request removal of a team number from the current timing/display state.
- **CAND-KEYPAD-003** — Keypad-originated changes shall pass through the normal timing-system state-change queue rather than mutate display state directly.

### Displays

- **CAND-DISP-004** — The application shall maintain a transport-independent display data/model representation derived from timing-system state.
- **CAND-DISP-005** — Display V1 shall be actively controlled by the application through its CAN adapter and shall support explicit refresh after discovery/reconnection.
- **CAND-DISP-006** — Display V2 shall consume synchronised timing/display data from the application and shall own its local presentation/rendering behaviour.
- **CAND-DISP-007** — When Display V2 connects or reconnects, the application shall be able to provide a complete current display-data snapshot independent of previously delivered incremental updates.
- **CAND-DISP-008** — Display data shall support a revision/version mechanism or equivalent means of detecting stale/missed state.

## Open questions

- Which in-memory collections/indexes are needed for registrations and start-time lookup on the Pi Zero?
- Which state must survive restart: registrations, start times, reserve tags, selected teams, display revision, outbox, or all of these?
- Is a full snapshot file sufficient for registrations, or is an append journal safer for power-loss recovery?
- How frequently may simple backup files be written without unnecessary SD-card wear?
- Should reference data use one combined backup snapshot or separate files per data set?
- Is start-time synchronisation always a full snapshot, or can the backoffice send deltas/corrections?
- What is the keypad protocol for distinguishing add versus remove?
- Is team ordering significant on the display and, if so, what determines it?
- How many teams can be displayed/selected concurrently?
- Does V1 retain any useful state across reconnect/power interruption or must every connection be treated as blank/unknown?
- What exact data fields does V2 need, and which presentation decisions belong exclusively inside V2?
- Should V2 receive full snapshots only initially/reconnect and deltas thereafter, or are full snapshots small enough to use for every change?

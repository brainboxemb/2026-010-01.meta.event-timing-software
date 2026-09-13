# Software engineering document set

Generated review/output book containing the current domain baseline, use cases, planning, requirements, development-environment, architecture, deferred design notes, interfaces and verification documents.

The numbered source documents on the source branch remain authoritative.

## Contents

- [Domain baseline](./03-domain-baseline.md)
- [System use cases](./04-UC-system-use-cases.md)
- [Software Development Plan (SDP)](./10-SDP-software-development-plan.md)
- [Software Implementation Planning (SIP)](./11-SIP-software-implementation-planning.md)
- [Software Development Environment (SDE)](./12-SDE-software-development-environment.md)
- [Java Build and Test Toolchain (SDE)](./13-SDE-java-build-test-toolchain.md)
- [Timing Application Requirements (SRD)](./20-01-SRD-timing-application-requirements.md)
- [Software System Architecture Document (SSAD)](./30-SSAD-software-system-architecture.md)
- [Timing Application Architecture (SAD)](./31-01-SAD-timing-application-architecture.md)
- [Java component, package and artifact detailed design](./31-01-SDD-02-java-component-design.md)
- [GUI Application Architecture (SAD)](./31-02-SAD-gui-application-architecture.md)
- [Web Operator Application Architecture (SAD)](./31-03-SAD-web-operator-application-architecture.md)
- [Data and display detailed design](./31-01-SDD-01-data-and-display-design.md)
- [Backoffice transport detailed design](./31-01-SDD-03-backoffice-transport-design.md)
- [Application Control and Status Interface (IDD)](./40-01-IDD-application-control-status.md)
- [Software Verification Plan (SVP)](./50-SVP-software-verification-plan.md)

---

## Domain baseline

**Source document:** [03-domain-baseline.md](./03-domain-baseline.md)

Status: working domain knowledge / non-authoritative requirements

This document captures stable domain facts and terminology supplied during the initial architecture work. It is intentionally separate from formal requirements: it records what the system domain looks like so later requirements, IDDs, architecture and code use the same concepts consistently.

Concrete production asset names, external registration-system IDs, source mappings and deployment inventories are intentionally **not** recorded in this public repository. They are deployment/proprietary information. Public documents describe the structure and semantics using generic identifiers only.

### Runtime and total system instances

One running headless timing application must be able to host **multiple complete logical system instances** at the same time.

The working software term is `TimingSystemInstance` for one such complete logical system.

This is required for both normal composition flexibility and test/simulation use. In particular, one application should be able to simulate the behaviour of a complete field of multiple system instances towards the backoffice.

Conceptually:

```text
TimingApplication
  +-- TimingSystemInstance 1
  +-- TimingSystemInstance 2
  +-- TimingSystemInstance 3
  +-- ...
```

A `TimingSystemInstance` is not the same thing as a physical registration asset or a registration source.

### Registration assets and registration sources

The domain contains two separate identities that must not be conflated.

#### Registration asset

A `RegistrationAsset` represents the real/configured registration box or logical equipment asset.

An asset has a stable configured identity/name for inventory, status, configuration and optional physical labelling. The concrete production asset names are deployment/proprietary information and stay outside this public repository.

A `TimingSystemInstance` can contain one or more registration assets.

#### Registration source

A `RegistrationSource` represents one ordered registration stream towards storage/backoffice semantics.

Each source has an external/domain system identifier. `RegistrationSystemId` remains the working name for that external/source identifier where it appears in records and protocol contracts.

Important structural rules:

- one registration asset can expose one or more registration sources;
- some sources can be virtual rather than corresponding one-to-one with a physical box;
- reserve and normal source classes exist;
- the exact production names, IDs, ranges and mappings are proprietary/deployment data and are not documented here;
- every source owns its own monotonic registration sequence and source-specific registration persistence.

Conceptually:

```text
TimingSystemInstance
  +-- RegistrationAsset asset-01
  |     +-- RegistrationSource source-01
  |     +-- RegistrationSource source-02   # may be virtual
  |
  +-- RegistrationAsset asset-02
        +-- RegistrationSource source-03
```

This separation allows a real asset name to remain useful for operations without forcing that name to equal the external registration-system identifier.

### RFID antenna ownership and routing

A registration asset can have **one or more RFID antennas**.

Conceptually:

```text
TimingSystemInstance
  +-- RegistrationAsset asset-01
        +-- Antenna RS-<asset-key>-ANT1
        +-- Antenna RS-<asset-key>-ANT2
        +-- RegistrationSource source-01
        +-- RegistrationSource source-02
```

An RFID observation must retain enough antenna/asset context for the software to route an accepted observation to the correct registration-source stream or streams.

The antenna therefore belongs primarily to the **asset**, not inherently to one source. Source selection/routing is a configurable/domain policy because one asset can expose multiple registration sources.

The exact hardware distinction between reader, antenna, power controller and protocol endpoint remains implementation-specific and still needs to be documented for the selected production hardware.

#### Antenna identifiers

The current antennas are not necessarily physically labelled. The software nevertheless needs a stable configuration identity for each antenna.

Preferred public naming template:

```text
RS-<asset-key>-ANT<n>
```

Use an explicit numeric suffix even when an asset currently has only one antenna, so adding a second antenna does not require renaming the first.

A future physical label may use the same `AntennaId`. The real `<asset-key>` values used in production remain deployment data and should not be copied into this public repository.

### Configurable topology

The relationship between application instances, registration assets, registration sources and antennas should be externally configurable through settings rather than hard-coded in application source.

The configuration needs to be able to describe at least:

```text
TimingApplication
  1..X TimingSystemInstance
    1..X RegistrationAsset
      1..X Antenna
      1..X RegistrationSource
        external RegistrationSystemId mapping
        source-specific sequence/persistence
```

The concrete configuration file format is not yet selected.

Production configuration may contain proprietary asset names/source IDs and therefore can live in a private deployment/integration repository or external deployment configuration. Public examples must use placeholder identities.

The same topology mechanism should support both real hardware adapters and stub/simulated adapters so a single application can model multiple total systems for integration/backoffice testing.

### Locations

Each physical event location has a unique numeric identifier:

```text
LocationId = 1..25
```

A registration record is associated with both:

```text
RegistrationSystemId
LocationId
```

The exact configuration ownership of `LocationId` still needs to be made explicit. A likely model is that the containing `TimingSystemInstance` provides the normal location context, while every persisted registration still carries the location explicitly for traceability and synchronisation.

### Registration sequence

Every registration stream has a monotonically increasing sequence number **per registration source**.

Conceptually:

```text
RegistrationRecordKey = (RegistrationSystemId, SequenceNumber)
```

The `LocationId`, `RegistrationAssetId` and `AntennaId` may provide useful context, but none of them changes the sequence scope.

Generic example:

```text
source-01:  1041, 1042, 1043, 1044, ...
source-02:   551,  552,  553, ...
```

This allows receiving/upstream systems to reason about stream consistency independently for every source. For example, receiving `1041`, `1042`, `1044` from one source makes a missing `1043` detectable.

Important intended properties:

- the number is monotonic per registration source;
- a committed number must not be reused after restart/recovery;
- higher-level synchronisation can use it for ordering and gap/consistency detection;
- moving/changing location must not implicitly reset the source sequence;
- multiple sources inside one asset or total system keep independent sequence streams;
- the exact rules for allowed gaps, wraparound and sequence persistence still need formal requirements.

### Per-source persistence

Each registration source has its **own registration file**.

The active application model may remain in memory, but registration persistence/recovery must preserve the source boundary so one source stream and its sequence state can be recovered and synchronised independently.

Conceptually:

```text
RegistrationSource source-01
  in-memory ledger/state
  source-specific sequence
  source-specific registration file

RegistrationSource source-02
  in-memory ledger/state
  source-specific sequence
  source-specific registration file
```

The exact file names, external IDs and deployment mappings are configuration/private data. The file format, append/snapshot policy, atomicity and durability rules still need detailed design and formal requirements.

### Registration entries

A registration entry is not limited to participant RFID passage data. Operational events can also be persisted as registration entries when they must participate in the traceable/synchronised stream.

Known example:

- opening a location/waypoint is itself a registration entry.

A working minimal envelope is therefore conceptually:

```text
RegistrationRecord
  registrationSystemId
  locationId
  sequenceNumber
  recordType
  observed/event time
  created time
  record-specific payload
```

Asset and antenna context may additionally be retained where useful for diagnostics/audit, but the exact storage/wire schema is not yet fixed.

### Time semantics

Recorded event time and start-time data need one unambiguous absolute-time meaning independent of how a local clock is displayed.

The working dedicated software value name is `TimingTimestamp`. At domain boundaries it represents an absolute point on the time line rather than a local date/time with an implicit time zone. Local time-zone and daylight-saving conversion are presentation/configuration concerns unless a future business rule explicitly depends on a local civil time.

A timestamp is **not** the source-ordering mechanism. Registration source sequence numbers remain the stable ordering/consistency mechanism even if an operating-system wall clock is corrected forwards or backwards.

The SI-01 SAD owns the implementation architecture for `TimingTimestamp`, injectable clock/time sources, monotonic duration measurement and the risk created by wall-clock corrections.

### Team number

The decoded participant/team identity contains a team number in the range:

```text
TeamNumber = 0..999
```

### RFID tag identity structure

The tag ultimately represents a structured identity containing:

```text
prefix + team number + postfix
```

Known semantics:

- `team number` is `0..999`;
- prefix semantics distinguish at least normal, reserve and test tag classes;
- a dedicated prefix indicates that a tag is a reserve tag;
- a dedicated prefix indicates that a tag is a test tag;
- there are two physical tags for a team/identity;
- a postfix distinguishes the two tag copies.

The exact encoded prefix/postfix values, encryption details and protocol representation are proprietary and are not defined here.

A working public semantic representation should preserve the tag class after decoding rather than immediately flattening every tag into one normal participant identity. The exact class/type API remains an implementation/design decision.

### Reserve tags

Reserve tags require conversion/mapping data supplied by the backoffice.

The local timing application therefore needs to be able to resolve a decoded reserve-tag identity through locally synchronised reference data before treating it as the intended team identity.

The mapping must remain available locally when live backoffice connectivity is temporarily unavailable, subject to later freshness/validity requirements.

### Test tags

Test tags are a separate RFID tag class identified by their prefix. They are **not** the same concept as software test doubles, stub adapters or synthetic test tooling.

After decoding, SI-01 must be able to distinguish a test tag from both a normal tag and a reserve tag so test-specific behaviour can be applied deliberately. A test tag must not be silently treated as a normal participant tag merely because its decoded payload also contains a team-like number.

The exact behaviour is intentionally not fixed in this domain baseline. It belongs in operational use cases and later requirements, including whether a test tag creates a registration record, affects calculations, is synchronised to backoffice, is allowed in all lifecycle states, and how it is made visible to an operator.

### Start-time reference data

Start times are supplied/synchronised from the backoffice and retained locally.

They support local calculations such as elapsed time and ranking without requiring every calculation to make a live backoffice request.

### Full-field simulation

A single SI-01 application must be capable of running enough configured `TimingSystemInstance` objects to represent the complete field behaviour required for backoffice integration testing.

For this use case:

- each total system instance remains separately addressable;
- each configured registration asset can expose one or more source streams;
- each source retains its configured external/source-like identity and independent sequence stream;
- antennas/devices may be stubbed or simulated through the normal adapter contracts;
- registrations still follow the same normal queue, source-sequence, persistence and backoffice paths as production data;
- simulation must not require a special bypass around the application/domain model;
- public test scenarios use generic identities, while a private integration configuration may map to the actual production inventory/protocol IDs.

Resource limits for the original Raspberry Pi Zero and larger desktop/integration-test deployments are different concerns. The architecture should permit the same logical model to run with different configured scale and adapter sets.

### Public/private domain-data boundary

This repository can document structural facts and generic ranges required for reusable framework design, but it must not become an inventory of the live/real deployment.

Keep the following outside the public repository unless deliberately approved for publication:

- actual registration-box/asset names;
- concrete external registration-system/source IDs and their real mappings;
- exact virtual/reserve-source assignments;
- exact production topology/inventory;
- proprietary protocol field values;
- encryption keys or secrets.

Public examples should use names such as `asset-01`, `source-01`, `system-01`, and `RS-<asset-key>-ANT1`.

### Traceability implications

The combination of source identity and monotonically increasing sequence is a domain-level consistency mechanism, not merely an implementation convenience.

Later requirements/design must therefore preserve at least:

```text
source identity
sequence order
registration-asset context where useful
containing total-system context
location association
antenna context where relevant
record type/payload
record time
source-specific persistence/recovery without sequence reuse
synchronisation/gap detection
```

Corrections/revocations should remain traceable rather than silently rewriting earlier records; the exact record model remains under design.

### Open domain questions

- Does each `TimingSystemInstance` always correspond to exactly one `LocationId`, or are there valid cases where one instance contains multiple location contexts?
- How is an accepted RFID observation routed when one registration asset exposes multiple registration sources: one selected source, several streams, or a policy determined by operation/configuration?
- Does sequence numbering start at a defined value for a new registration source?
- Are sequence-number gaps allowed after failed/aborted persistence, provided numbers are never reused?
- What happens if the numeric sequence reaches its maximum representation?
- Which operational events besides `OPEN` must be part of a registration stream (for example close/reinitialisation/configuration changes)?
- What exact data must an `OPEN` registration entry contain?
- Are normal, reserve and virtual registration sources treated identically by backoffice synchronisation once their source identity is known?
- What exact operational behaviour is required for test tags, and which parts deliberately differ from normal and reserve tags?


---

## System use cases

**Source document:** [04-UC-system-use-cases.md](./04-UC-system-use-cases.md)

Status: working draft / non-authoritative

This document captures system-level operational use cases that explain how operators, devices, external systems and test tooling use the event-timing software system.

Use cases are intentionally placed between the domain baseline and formal requirements. They describe **desired externally meaningful behaviour and goals**, not implementation details. Later system requirements, IDDs, software-item SRDs and verification cases may reference these use cases.

The public repository uses generic/synthetic identities. Real deployment asset names, external registration-source IDs, broker topology and proprietary protocol details remain outside this repository.

### Relationship to other documents

```text
03 Domain baseline
      |
      v
04 System use cases
      |
      +--> system requirements / IDDs
      |          |
      |          v
      |      software-item SRDs
      |          |
      |          v
      |       SAD / SDD
      |
      +--> SVP / ST-* verification scenarios
```

A use case is not a test case. One use case may be verified by several unit, interface, system, fault-injection and hardware tests.

### Use-case format

Each use case should eventually contain:

```text
ID
Name / goal
Primary actor(s)
Supporting actor(s)
Preconditions
Trigger
Main flow
Alternative / failure flows
Postconditions / observable result
Relevant interfaces
Derived requirements (later)
Verification references (later)
```

The current catalogue starts lightweight and can be expanded as requirements are promoted.

### Use-case catalogue

| ID | Name | Primary actor | Goal |
| --- | --- | --- | --- |
| UC-001 | Start and prepare a timing-system instance | Operator | Bring one configured timing-system instance into a usable operational state. |
| UC-002 | Open a timing-system instance | Operator | Start accepting/processing normal timing operation and create the required traceable open event(s). |
| UC-003 | Register a participant through RFID | RFID subsystem | Turn valid filtered/decrypted RFID observations into traceable source-specific registration records. |
| UC-004 | Recover or reinitialise RFID equipment | Operator / system | Restore an RFID device after startup, heartbeat or protocol failure without losing committed timing state. |
| UC-005 | Manage ready teams through keypad/operator input | Operator / keypad | Add or remove team numbers from the ready-team state and preserve the change history. |
| UC-006 | Drive a passive display from current system state | Timing application | Keep a passive Display V1 aligned with the authoritative current ready-team/display model. |
| UC-007 | Synchronise a smart display | Smart display | Connect to the advertised service and receive current/synchronised display data without moving domain authority out of SI-01. |
| UC-008 | Operate SI-01 through a desktop GUI | Operator | View status/data and execute permitted commands while SI-01 may run on a remote Raspberry Pi. |
| UC-009 | Operate SI-01 through the browser/iPad application | Operator | Download the web application and use HTTP/WebSocket for status, registration data and operator commands. |
| UC-010 | Synchronise reference data from backoffice | Backoffice | Deliver start times, reserve-tag mappings and other required reference data for local use. |
| UC-011 | Synchronise registration-source data to backoffice | Timing application / backoffice | Deliver committed source streams while preserving source identity, ordering and recoverability. |
| UC-012 | Continue local operation during backoffice outage | Operator / timing application | Continue required local timing behaviour while external synchronisation is unavailable, retaining data for later recovery. |
| UC-013 | Restart and restore local state | Operator / platform | Restore source sequences, registration state, ready-team/reference state and status after process/device restart. |
| UC-014 | Run multiple complete system instances in one process | Test/operator tooling | Run several independently addressed system instances and source streams in one SI-01 process. |
| UC-015 | Simulate a complete field toward backoffice | Test tooling | Exercise normal multi-instance/source behaviour without real production hardware or private deployment identities. |
| UC-016 | Replace real devices with controllable stubs | Test tooling | Drive normal application paths with simulated RFID/CAN/display/backoffice components and fault injection. |
| UC-017 | Use an alternative backoffice transport for loop testing | Test tooling / simulator | Exercise source-aware backoffice semantics across a real socket/process boundary without requiring RabbitMQ. |
| UC-018 | Verify production-shaped messaging through RabbitMQ | Test tooling / backoffice adapter | Exercise source-specific consumers/publishing, broker recovery and outbox behaviour against a real disposable broker. |
| UC-019 | Process a test RFID tag | RFID subsystem / operator | Recognise a test-tag identity and apply explicit test-tag behaviour without silently treating it as a normal or reserve participant tag. |

### UC-001 — Start and prepare a timing-system instance

**Goal:** bring one configured `TimingSystemInstance` into a known usable state.

**Primary actor:** operator or automated startup policy.

**Preconditions:**

- SI-01 has loaded and validated configuration;
- the target instance exists;
- required local state has been restored or an explicit restore fault is visible.

**Main flow:**

1. The actor selects/addresses a timing-system instance.
2. SI-01 reports current instance and subsystem status.
3. Required devices are started according to configuration/policy.
4. RFID equipment that is required for the instance goes through power-on and initialisation.
5. SI-01 reports individual device/subsystem readiness rather than hiding startup progress behind one boolean.
6. The instance becomes ready for the operator to open when required operational prerequisites are satisfied.

**Alternative/failure flows:**

- an RFID device does not boot or initialise;
- a CAN device is not discovered;
- required reference data is unavailable/stale;
- persistence/restore is unhealthy;
- network/backoffice is unavailable while local operation may still remain possible.

**Relevant interfaces:** IF-01/02/03, IF-07, IF-08, status model.

### UC-002 — Open a timing-system instance

**Goal:** enter normal timing operation in a traceable way.

**Primary actor:** operator.

**Main flow:**

1. The operator issues `open` through an authorised operator interface.
2. The command is translated to the shared application command boundary.
3. The addressed `TimingSystemInstance` processes the command through its serialized state boundary.
4. The lifecycle becomes `OPEN` if preconditions are met.
5. The required operational open event is written as a traceable registration-stream entry for the applicable source(s) according to the final requirements.
6. Status/event consumers receive the new lifecycle state.

**Alternative/failure flows:**

- invalid lifecycle transition;
- required persistence cannot commit the open event;
- degraded devices exist but policy still permits open;
- duplicate/open-again command.

### UC-003 — Register a participant through RFID

**Goal:** create a valid traceable registration from RFID observations without treating the first raw observation as automatically authoritative.

**Primary actor:** RFID subsystem.

**Main flow:**

1. The RFID adapter captures raw tag data, antenna identity and observation time.
2. SI-01 routes the observation to the configured `RegistrationAsset` / `TimingSystemInstance` context.
3. Proprietary/private decoding/decryption translates the raw tag into a public semantic identity representation while retaining whether the tag is normal, reserve or test-class.
4. Filtering/observation accumulation determines whether the observation is accepted.
5. Reserve-tag resolution is applied when applicable using locally available reference data.
6. A test-tag identity branches to the explicit test-tag behaviour in UC-019 rather than silently continuing as a normal participant registration.
7. Source-routing policy selects the applicable `RegistrationSource` stream(s).
8. Each committed source record receives the next monotonic source sequence number.
9. The record is persisted in that source's registration file/repository.
10. Derived local state/calculations and status are updated.
11. Outbound synchronisation is queued independently from local commit.

**Alternative/failure flows:**

- decryption/validation fails;
- tag is observed but filtering does not yet accept it;
- reserve mapping is unavailable;
- a test-tag policy does not permit the requested/observed operation;
- source routing is ambiguous/invalid;
- local persistence fails;
- backoffice is unavailable after local commit.

### UC-004 — Recover or reinitialise RFID equipment

**Goal:** allow explicit operator/system recovery of an RFID device while keeping timing-system state and committed registrations intact.

**Primary actor:** operator, supported by health/recovery logic.

**Main flow:**

1. SI-01 detects/reports an RFID startup, heartbeat or protocol problem.
2. The operator sees the exact affected asset/antenna state.
3. The operator requests reinitialisation, reconnect, reset or power-cycle according to supported recovery policy.
4. The adapter performs the hardware/protocol recovery operation.
5. Device state returns through `INITIALISING` to `READY`, or remains in an explicit error state.
6. Existing committed registration/source sequence state is not reset or rewritten by device recovery.

### UC-005 — Manage ready teams through keypad/operator input

**Goal:** maintain the current ready-team list while keeping add/remove history traceable.

**Primary actor:** keypad or operator client.

**Main flow:**

1. A team-number add/remove action enters through a normal input adapter.
2. SI-01 routes the command to the applicable timing-system instance.
3. A `ReadyTeamEvent` is appended to the ready-team journal.
4. `ReadyTeamState` is updated from the event.
5. Display state is rebuilt/updated from the authoritative current ready-team state.
6. Operator/status clients can observe the resulting state.

The ready-team journal is separate from participant/timing `RegistrationRecord` streams.

### UC-006 — Drive a passive display from current system state

**Goal:** ensure Display V1 shows the current authoritative ready-team/display model.

**Primary actor:** SI-01.

**Main flow:**

1. SI-01 derives a current `DisplayModel` from application state.
2. The passive-display adapter translates that model into CAN/device commands.
3. On state change, reconnect or rediscovery, SI-01 actively refreshes the display as required.
4. The display itself does not become authoritative for ready-team/domain state.

### UC-007 — Synchronise a smart display

**Goal:** provide a smarter network display with data/state while SI-01 remains authoritative.

**Primary actor:** smart display.

**Main flow:**

1. SI-01 advertises the configured service through mDNS.
2. The display discovers and connects to SI-01.
3. SI-01 provides a full current snapshot/data set.
4. Subsequent updates are synchronised over the selected network protocol.
5. After reconnect, the display can recover from a fresh authoritative snapshot.

### UC-008 — Operate SI-01 through a desktop GUI

**Goal:** operate/observe a timing application running locally or on another host such as a Raspberry Pi.

**Primary actor:** operator.

**Main flow:**

1. SI-02 connects through the system-defined application-control/status interface.
2. It retrieves current application/instance/subsystem state.
3. The operator performs permitted commands such as open/close/device recovery and later registration-related operations.
4. SI-02 shows command outcome and live/stale/disconnected status explicitly.
5. No authoritative timing state is stored solely in the GUI.

### UC-009 — Operate SI-01 through the browser/iPad application

**Goal:** provide local browser/iPad operation without requiring a separately installed native client.

**Primary actor:** operator.

**Main flow:**

1. The browser loads the compiled React application from SI-01 over HTTP.
2. The application obtains initial state/registration data via HTTP/query endpoints.
3. Live state/registration changes arrive over WebSocket.
4. Operator actions such as open/close/start are submitted through the same shared application semantics as other clients.
5. Disconnection/stale state is visible to the operator.

### UC-010 — Synchronise reference data from backoffice

**Goal:** make required reference data available locally even when later backoffice connectivity is interrupted.

**Primary actor:** backoffice.

**Main flow:**

1. Source-aware inbound backoffice communication receives a reference-data update.
2. The transport adapter translates private/wire representation into public semantic data.
3. SI-01 validates and applies the update.
4. Start times/reserve-tag mappings and related metadata are stored in in-memory repositories.
5. Backup/restore state is updated according to persistence policy.
6. Status exposes version/freshness/health where required.

### UC-011 — Synchronise registration-source data to backoffice

**Goal:** deliver committed ordered source streams without coupling domain logic to one transport technology.

**Primary actors:** SI-01 and backoffice.

**Main flow:**

1. A source record is committed locally with `(RegistrationSystemId, SequenceNumber)` identity.
2. A corresponding outbound item becomes pending in the outbox/synchronisation state.
3. The selected `BackofficeTransportPort` sends the semantic message through its configured transport.
4. RabbitMQ production-shaped transport may map the source to its configured exchange/routing endpoint; a test socket adapter may use a simpler synthetic framing.
5. Successful acknowledgement/reconciliation advances the pending state according to the final protocol.
6. Source ordering and gap detection remain possible at higher levels.

### UC-012 — Continue local operation during backoffice outage

**Goal:** preserve required local timing functionality and traceability while external connectivity is unavailable.

**Primary actor:** operator / SI-01.

**Main flow:**

1. SI-01 detects loss of internet/broker/backoffice connectivity and exposes the appropriate status layer.
2. Local device operation, registration and calculations continue where required local configuration/reference data is available.
3. New committed source records remain locally durable.
4. Outbound items remain pending.
5. After transport recovery, synchronisation resumes without inventing/reusing committed sequence numbers.

### UC-013 — Restart and restore local state

**Goal:** recover a coherent timing application after restart/power interruption.

**Primary actor:** platform/operator.

**Main flow:**

1. SI-01 starts and loads configuration.
2. Source-specific registration files and sequence state are restored/validated.
3. Ready-team/reference/other recoverable state is restored according to the design.
4. The runtime reconstructs configured system instances/assets/sources/adapters.
5. Status reports restore health/errors before normal operation is presented as healthy.
6. Backoffice/outbox recovery resumes independently from local startup.

### UC-014 — Run multiple complete system instances in one process

**Goal:** host multiple complete logical system instances while preserving independent lifecycle, state and source streams.

**Primary actor:** configuration/test/operator tooling.

**Main flow:**

1. Settings describe several `TimingSystemInstance` objects.
2. Each instance receives its own logical serialized state boundary.
3. Each contains one or more configured registration assets/sources.
4. Runtime-wide infrastructure may be shared without sharing mutable instance state.
5. Public interfaces can address each instance explicitly.

### UC-015 — Simulate a complete field toward backoffice

**Goal:** exercise realistic multi-instance/multi-source behaviour from one test application.

**Primary actor:** automated/system test tooling.

**Main flow:**

1. A synthetic configuration creates enough timing-system instances/assets/sources to represent the required test scale.
2. Stub devices inject observations/faults through normal adapter boundaries.
3. SI-01 follows the same queues, routing, source sequences, persistence and backoffice-port paths as production composition.
4. A backoffice simulator or broker fixture observes all source streams.
5. Tests validate isolation, ordering, recovery and status across the simulated field.

### UC-016 — Replace real devices with controllable stubs

**Goal:** make hardware-dependent application behaviour testable without duplicating business logic.

**Primary actor:** test tooling.

**Main flow:**

1. Composition selects stub adapters through normal public contracts.
2. Test control injects reads, device discovery, disconnects, failures or recoveries through the adapter surface.
3. The application processes those events through normal queues/domain handlers.
4. Tests observe behaviour only through supported state/interfaces/evidence points.

### UC-017 — Use an alternative backoffice transport for loop testing

**Goal:** test real process/network communication and source routing without RabbitMQ.

**Primary actors:** backoffice simulator and test tooling.

**Main flow:**

1. SI-01 is configured with a simple socket-based `BackofficeTransportPort` implementation.
2. A simulator connects over a real TCP/socket boundary.
3. Generic public `BackofficeEnvelope` messages are framed with explicit source context.
4. Several source streams can share the connection.
5. Disconnect/reconnect and malformed-message behaviour can be injected cheaply.
6. SI-01's domain/outbox/source behaviour remains identical to the RabbitMQ composition.

This use case is intentionally protocol-neutral and does not reproduce private production RabbitMQ message schemas.

### UC-018 — Verify production-shaped messaging through RabbitMQ

**Goal:** verify broker/client lifecycle and source-specific messaging using a real disposable broker.

**Primary actors:** automated test tooling and SI-01 RabbitMQ adapter.

**Main flow:**

1. A Docker/Compose test environment starts a RabbitMQ broker with synthetic topology/credentials.
2. SI-01 establishes the configured broker connection(s).
3. Each registration source requiring inbound traffic establishes its source-specific queue consumer/channel.
4. Outbound source messages use source-specific routing configuration.
5. Tests exercise inbound/outbound behaviour and source isolation.
6. The broker is stopped/restarted to exercise reconnect, consumer restoration and pending-outbox resume.

Production names, source IDs, schemas and credentials remain outside the public fixture.

### UC-019 — Process a test RFID tag

**Goal:** recognise a test-tag observation and apply deliberate test-specific behaviour without allowing the tag to masquerade as a normal or reserve participant tag.

**Primary actors:** RFID subsystem and operator.

**Preconditions:**

- the tag has been decoded sufficiently to identify its semantic tag class;
- the configured timing-system instance can identify that the tag is a test tag.

**Main flow:**

1. The RFID adapter captures the observation through the same normal ingress path used for other tags.
2. Decoding preserves the semantic tag class as `test` rather than flattening the identity to a normal participant identity.
3. Any common validation/filtering that also applies to test tags is performed according to the final requirements.
4. SI-01 applies the configured/test-tag policy instead of the normal or reserve-tag path.
5. The resulting action and operator-visible state remain explicitly distinguishable as test-tag behaviour.
6. If any record is persisted or synchronised, its semantics remain distinguishable from a normal participant registration.

**Behaviour still to define:**

- whether a test tag creates a registration-stream record at all;
- whether it uses a dedicated record type and/or source-routing rule;
- whether it may affect elapsed-time/ranking/other derived calculations;
- whether it is synchronised to backoffice, and if so with what semantics;
- in which lifecycle states a test tag is accepted;
- what an operator sees when a test tag is detected/accepted/rejected;
- whether test-tag handling requires an explicit enable/configuration mode.

This use case is about a real semantic RFID tag class. It is separate from UC-015/016 software simulation and stub-device testing.

### Cross-cutting alternative/failure scenarios

The following scenarios should be associated with applicable use cases rather than becoming isolated implementation details:

- RFID power/boot/heartbeat failure;
- invalid/decryption/filtering failure;
- missing/stale reserve-tag or start-time data;
- test-tag detection while test-tag behaviour is disabled or not valid in the current lifecycle state;
- CAN device disappearance;
- passive display reset/reconnect;
- smart-display reconnect;
- local LAN versus internet versus backoffice loss;
- source persistence/backup failure;
- process restart after committed events;
- source sequence continuity/gap detection;
- operating-system wall-clock correction forwards or backwards while observations are being captured;
- local daylight-saving-time transition or other local-time ambiguity;
- queue pressure/backpressure;
- GUI/browser disconnect/stale state;
- socket transport disconnect/reconnect;
- RabbitMQ broker/channel/consumer recovery.

### Traceability direction

When requirements are promoted, prefer explicit references such as:

```text
UC-003
  -> SYS-REG-xxx
  -> IDD-... where external behaviour applies
  -> SI01-SRD-...
  -> SDD registration/RFID/source-routing elements
  -> VC-... / ST-1, ST-2, ST-3, HIL evidence
```

This allows one operational goal to remain visible even when implementation responsibilities are distributed over several software items/components.

### Open use-case questions

- Which use cases are required during normal operation versus maintenance/service-only operation?
- What exact preconditions are required before a timing-system instance may be opened?
- Which subsystem failures should block `OPEN`, and which should only mark the instance degraded?
- Which operational events besides `OPEN` must become registration-stream records?
- Does one timing-system instance always represent one location context at a time?
- What operator roles/authorisation distinctions will exist for local, desktop and web clients?
- Which reference-data updates are automatically accepted versus requiring operator acknowledgement?
- What exact local behaviour is required if reference data is stale but backoffice is unavailable?
- Which source-routing cases can intentionally create records in multiple virtual/source streams from one accepted RFID event?
- Which UC-019 test-tag behaviours are part of normal operational verification versus maintenance/service-only behaviour?


---

## Software Development Plan (SDP)

**Source document:** [10-SDP-software-development-plan.md](./10-SDP-software-development-plan.md)

Status: working draft / non-authoritative

This Software Development Plan describes the **high-level development strategy** for the software system: objectives, development approach, major phases/workstreams, resources, dependencies, risks and important unknowns.

It deliberately does **not** contain the detailed implementation sequence. That belongs in `11-SIP-software-implementation-planning.md`.

### Document boundaries

Use the project documents as follows:

```text
SDP  high-level development strategy, phases, risks, resources and assumptions
SIP  concrete implementation steps, deliverables, demonstrations and exit evidence
SDE  development environment, repositories, GitHub workflow, tooling and artifact conventions
SVP  verification strategy, levels, system-test profiles and evidence model
SSAD/SAD/SDD  software architecture and design
```

The SDP should remain understandable without knowing implementation details. When a phase requires detailed tasks, technology setup or commands, the SDP points to the SIP, SDE, SVP or architecture documents rather than duplicating them.

### Development objectives

The development effort should produce a reusable software system that:

- supports reliable event timing and time registration;
- runs on the mandatory original Raspberry Pi Zero / Zero W target;
- separates the headless timing runtime from desktop and browser/iPad presentation clients;
- supports multiple logical timing-system instances in one application process;
- supports configurable registration assets, registration sources and device mappings;
- remains locally useful when external/backoffice connectivity is unavailable;
- keeps traceable registration data and recovery state;
- can be tested extensively without requiring all production hardware or proprietary components;
- allows proprietary implementations to plug into public contracts without forking public framework source;
- provides reproducible build, test, documentation and target-deployment automation early in development.

### Development strategy

#### Incremental vertical development

Develop in small, demonstrable increments rather than attempting the complete timing system in one integration step.

Each increment should reduce a meaningful risk and end in a concrete deliverable. Detailed increment definitions and demonstrations belong in the SIP.

#### Release-backed completion baselines

A SIP implementation step is not complete merely because its planned activities are marked done. Each completed step should leave a stable, identifiable baseline that can be reviewed and rebuilt later.

When a step produces a meaningful software baseline, that closure baseline should normally be a **normal software release**, not a planning-only tag. The release should have a non-snapshot software version, a matching `vX.Y.Z` Git tag, a dated CHANGELOG entry, retained release artifacts/evidence, and a build/test run from the tagged revision itself.

Before such a SIP step moves to `completed`, the project should:

- merge the accepted in-scope implementation/documentation work;
- ensure build/test tooling that forms part of the release baseline is itself released or otherwise deliberately versioned and reproducibly consumable;
- verify the required CI and generated evidence on the accepted repository state;
- prepare the release version and CHANGELOG through the normal reviewed workflow;
- verify the release candidate on the accepted main branch;
- create the matching immutable release tag on that verified revision;
- rebuild/test the tagged revision rather than relying only on pre-merge or pre-tag evidence;
- verify that produced artifacts report the expected software version, source revision and build identity;
- retain the release artifacts and verification evidence;
- record the closure evidence in the coordination repository;
- only then mark the SIP step `completed` and activate the next step.

A release version is consumed once its normal candidate tag has been created. If verification of the tagged revision fails, preserve the failed candidate as `vX.Y.Z-failed` on the same commit, verify that archival tag, remove the normal `vX.Y.Z` tag, and do not publish or retain it as a valid release. Record the failed version in the CHANGELOG as `FAILED DURING RELEASE BUILD`; the next release attempt advances the patch version rather than reusing the failed version. `-failed` tags are historical evidence only and must not trigger or represent normal releases.

A planning/documentation step that does not produce releasable software does not need an artificial software version. Its SIP definition may instead identify an appropriate immutable documentation/planning baseline. This exception should not be used to avoid releasing software when the step has produced a meaningful software maturity level.

After a software release, normal development should move to the next planned `-SNAPSHOT` version before new capability work begins. The SIP owns the concrete closure checklist and release meaning for each step. The SDE/tooling documentation owns the mechanics for release/tag-triggered builds, artifact retention and version/provenance verification.

#### Architecture before irreversible coupling

Define the important system/software-item boundaries, interface ownership, public/private extension model, threading/state model and persistence direction before production implementations make those choices expensive to change.

Architecture remains a tool for implementation, not an excuse to postpone executable software indefinitely.

#### Early executable and early target automation

First prove the headless application on a normal development environment, primarily Windows. Once the first useful executable exists, establish automated Raspberry Pi image generation and application update deployment early.

The intent is to prevent manual SD-card preparation or ad-hoc target setup from becoming normal development practice.

#### Automation-first engineering

Use GitHub Actions and repository automation from the first implementation repositories for build, test, generated evidence and later target-image/update workflows.

AI-assisted development is part of the development approach, but AI follows the same issue/branch/pull-request/test/review discipline as human development. Detailed repository and AI working rules belong in the SDE and repository `AGENTS.md` files.

#### Progressive test realism

Start with deterministic unit/application tests and progressively add process/network boundaries, broker integration and real target/hardware verification.

The exact verification levels and `ST-*` system-test profiles belong in the SVP. The SDP only requires that test realism grows with implementation risk rather than replacing fast tests with only expensive end-to-end testing.

#### Public/private separation

Keep reusable framework contracts, testkit/stubs and reference applications public where appropriate. Keep production-specific/proprietary protocol implementations, real deployment identities/mappings and secrets in private repositories or external configuration.

Prove the extension boundary early, before substantial proprietary implementation accumulates.

### High-level development phases

The detailed step numbering, deliverables and demonstrations are maintained in the SIP. These SDP phases are intentionally broader.

#### Phase A — Architecture and engineering baseline

Establish the project/document model, domain baseline, use cases, software-item boundaries, system interfaces, development/verification strategy and public/private boundary.

Outcome: implementation can begin without inventing foundational conventions inside the first coding PRs.

#### Phase B — Framework and first executable

Create the public Java/Maven framework structure and a minimal SI-01 headless executable on the development environment.

Prove shared version/status behaviour, public application boundaries, basic concurrency/testability direction and CI.

#### Phase C — Target deployment foundation

Prove the mandatory Raspberry Pi Zero target early.

Establish reproducible image creation, pinned runtime provisioning, automatic service startup, repeatable application updates and the first target resource baseline.

This is a development foundation, not final deployment hardening.

#### Phase D — Client and external-consumer proofs

Introduce a separate desktop GUI software item and an external public reference/test project.

Use these to prove that software-item interfaces and public Maven/API/SPI boundaries work outside the framework reactor and across a real network boundary.

Also prove that private/proprietary implementations can replace public stubs through supported contracts.

#### Phase E — Timing-domain and operator capability growth

Implement registration/source state, ready-team state, reference data, local persistence/recovery and meaningful operational behaviour.

Introduce the browser/iPad operator application when sufficient domain capability exists to make it useful.

#### Phase F — Device and backoffice integration

Integrate controlled stubs first, then representative production RFID/CAN/display implementations and backoffice communication.

Maintain the same core behaviour and public contracts while replacing test adapters with real implementations.

#### Phase G — Operational maturity

Harden target deployment, update/rollback, secrets/configuration handling, diagnostics, long-running verification, hardware-in-the-loop testing and measured resource budgets.

The goal is to mature automation introduced earlier, not to introduce deployment automation only at the end.

### Planning cadence and indicative horizon

The current working planning assumption is approximately **one focused project day per week**.

Effort is estimated in **project days**, not ordinary calendar days. This is useful for a part-time/learning project because a five-project-day task means roughly five focused working sessions even when those sessions are spread across several weeks.

Detailed per-step estimates are maintained as working SIP-roadmap data in `docs/_data/sip-roadmap.json` and are rendered into the generated SIP roadmap. They are planning aids, not commitments or formal requirements.

The current baseline contains approximately **51 focused project days** from the remaining architecture work through deployment hardening. At one project day per week this gives a theoretical baseline of roughly one year. A **25% planning reserve** is currently shown for learning, integration surprises, hardware availability, target-image tooling and proprietary/backoffice unknowns.

The resulting high-level horizon is approximately:

| SDP phase | Indicative target at 1 project day/week | Planning meaning |
| --- | --- | --- |
| Phase A — Architecture and engineering baseline | September 2026 | Architecture/document baseline ready to start implementation. |
| Phase B — Framework and first executable | October 2026 | Public framework skeleton and first SI-01 behaviour running on the development host. |
| Phase C — Target deployment foundation | November 2026 | Reproducible Pi Zero image, service startup and normal application-update path demonstrated. |
| Phase D — Client and external-consumer proofs | December 2026 – January 2027 | Desktop GUI, external reference project and initial private-extension proof available. |
| Phase E — Timing-domain and operator capability growth | February – March 2027 | Local registration/state/recovery behaviour and first useful browser/iPad operator flow available. |
| Phase F — Device and backoffice integration | April – July 2027 | Stub hardware, representative real devices and backoffice integration progressively demonstrated. |
| Phase G — Operational maturity | August – September 2027 | Deployment/update/diagnostic lifecycle hardened against a representative system. |
| Planning reserve | Q4 2027 | Capacity for learning, rework, hardware/protocol uncertainty and slippage without pretending the baseline is a fixed deadline. |

These dates should be reforecast when evidence materially changes the estimate of a SIP step. The roadmap should therefore show both **estimated project days** and **baseline target dates**, while remaining a deliverable/capability roadmap rather than becoming a classical Gantt chart.

A cadence of one project day per week also creates a context-switching risk: work can lose momentum when a difficult investigation spans several weeks. Where possible, steps should therefore remain small enough to reach a demonstrable result within a limited number of focused sessions.

### Development resources and environments

The project should plan explicitly for the environments needed to develop and verify the system.

#### Development workstation

At least one normal development workstation is required. The initial development environment is expected to be Windows because that is the primary convenient development host.

It should be capable of:

- Java/Maven development;
- running SI-01 and SI-02 locally;
- running Python project tooling;
- executing normal unit/application/system tests;
- running Docker/Compose when required for integration services such as RabbitMQ, if supported by the selected workstation setup.

#### Mandatory target hardware

At least one original Raspberry Pi Zero / Zero W is required for target validation because ARMv6 runtime behaviour cannot be inferred reliably from desktop development alone.

Target use includes:

- validating the selected Java runtime;
- booting generated images;
- measuring startup/memory/CPU/thread behaviour;
- validating service startup and application updates;
- later device/network/hardware integration.

#### Possible separate integration/test host

A second PC, Linux host or more capable Raspberry Pi may be useful for:

- hosting RabbitMQ/Docker integration services;
- running backoffice simulators/test drivers while the Pi Zero runs SI-01;
- running longer system tests;
- keeping load from the test infrastructure off the constrained target;
- acting as a reproducible local integration server.

This is currently a **planning option**, not yet a mandatory resource.

An explicit early question is whether the normal development workstation plus one standalone Pi Zero are sufficient for the first phases, or whether a dedicated integration host materially improves repeatability and test realism.

#### Representative hardware later

Production-device phases require representative RFID, CAN, keypad and display hardware. These do not need to block the first framework/application phases because stubs/testkit components are part of the strategy.

### Dependencies and assumptions

Current planning assumptions include:

- original Raspberry Pi Zero / Zero W remains a mandatory SI-01 target;
- Java 8 is the initial baseline until an explicit evidence-backed decision changes it;
- Maven is the Java build/dependency baseline;
- GitHub and GitHub Actions remain available for source control and automation;
- public and private repositories can share versioned public contracts/artifacts;
- production secrets and deployment mappings can be provided outside public source control;
- representative hardware and backoffice access will become available when their integration phases begin;
- local operation must not be designed around permanent internet/backoffice availability.

When an assumption proves false, the SDP and affected SIP/architecture material should be revised explicitly.

### Risks and unknowns

The following risks/unknowns should remain visible at SDP level because they can affect overall approach, schedule or feasibility.

| Risk / unknown | Development response |
| --- | --- |
| ARMv6 Java runtime availability/support may constrain dependencies and maintenance. | Pin and test an explicit Java 8 runtime early; retain Java 11 only as an evidence-driven future option. |
| Pi Zero CPU/RAM may make apparently convenient libraries or thread models too heavy. | Measure target resources from the first target image and keep adapters/domain architecture lightweight. |
| Image generation/update automation may be more complex than expected on legacy Pi Zero support. | Introduce it early as its own SIP increment rather than deferring deployment risk. |
| Public/private API boundaries may be wrong or too coupled. | Create external reference and private-extension proofs before proprietary implementation becomes large. |
| Threading/order/timestamp errors could corrupt timing semantics. | Keep mutable state behind controlled serialized boundaries and verify source timestamps/order deterministically. |
| Offline/reconnect behaviour may become complex across persistence and backoffice synchronisation. | Separate local authority/outbox/transport semantics and test disconnect/recovery progressively. |
| Real RFID filtering/decryption/hardware behaviour may differ from simulations. | Keep production adapters replaceable and add HIL evidence once hardware is available. |
| Backoffice/RabbitMQ protocol details may constrain public interfaces. | Keep semantic backoffice ports transport-independent and isolate proprietary protocol mapping. |
| Full-field simulation may stress the runtime differently from normal Pi deployment. | Support configurable multi-instance/source simulations and measure scaling independently from target topology. |
| A single development PC + Pi Zero may be insufficient for repeatable integration/HIL tests. | Evaluate a separate integration host as test infrastructure needs become concrete. |
| One-day-per-week cadence may create context-switching overhead and stretch difficult investigations. | Keep increments demonstrable and reforecast project-day estimates when learning/integration evidence changes uncertainty. |
| AI-assisted development can create large/fast changes that are difficult to review. | Require the same PR-first workflow, tests, generated evidence and source-of-truth discipline for AI work. |

This table is expected to evolve as evidence replaces uncertainty.

### Key development decisions still to be made

Examples of decisions that remain below SDP level but may materially affect the plan include:

- exact ARMv6 Java 8 distribution/runtime;
- Raspberry Pi image-builder technology;
- application-update/rollback mechanism;
- final Java logging/test libraries;
- HTTP/WebSocket/remote-shell technology compatible with Java 8 and Pi Zero;
- exact configuration file format and secret injection model;
- public/private Maven artifact publication mechanism;
- whether a dedicated integration/test host is required;
- when Java 11 evidence is mature enough to reconsider the baseline.

Detailed resolution belongs in the SIP, SDE, architecture or implementation PR depending on the topic.

### Planning and control

The SDP controls **direction**, not day-to-day implementation tasks.

- Use the **SIP** for the ordered implementation steps, deliverables, demonstrations and exit evidence.
- Use the **SDE** for repository structure, GitHub workflow, development tooling, generated-output conventions and environment setup.
- Use the **SVP** for verification levels, test profiles and evidence expectations.
- Use **SSAD/SAD/SDD/IDD/SRD** documents for architecture, interfaces, design and formal requirements.
- Use active pull requests for implementation detail and step-specific evidence.

The SDP should be reviewed when a major assumption, resource need, risk or overall phase strategy changes.


---

## Software Implementation Planning (SIP)

**Source document:** [11-SIP-software-implementation-planning.md](./11-SIP-software-implementation-planning.md)

Status: working draft / non-authoritative

This document is the concrete software implementation sequence derived from `docs/10-SDP-software-development-plan.md`.

The SDP defines the higher-level development approach and phased evolution. This SIP turns that direction into ordered implementation steps, scope, concrete deliverables, demonstrations and exit evidence.

Detailed implementation decisions, tests and evidence for an active step belong in that step's pull request.

Software-item identifiers are stable across the document set:

```text
SI-01  Headless Timing Application
SI-02  Desktop GUI Application
SI-03  Web Operator Application
```

### Step-completion model

Every implementation step should end in something concrete that can be shown, used or reviewed.

Use the following distinction:

- **Goal** — why the step exists;
- **Scope** — what work belongs in the step;
- **Deliverable** — the tangible result that exists when the step is complete;
- **Demonstration** — a short, repeatable walkthrough showing what is newly possible;
- **Evidence / exit criteria** — objective evidence that the result is not merely a successful demo.

The demonstration is deliberately stakeholder-friendly. A manager, developer or reviewer should be able to answer:

> What can the system do now that it could not do before this step?

A demonstration does not replace verification. Automated tests, CI results, measurements and review evidence remain required where applicable.

#### Closing a software-producing step

When an implementation step produces a meaningful software maturity level, the normal closure baseline is a **software release**. Do not mark the step complete merely because its activities are done or because a PR/main build is green.

Use this closure sequence unless the step explicitly defines a different non-software baseline:

1. merge the accepted implementation, documentation and verification work;
2. verify that required build/test tooling is itself released or deliberately versioned and reproducibly consumable;
3. prepare the product release through a normal reviewed PR, including the non-snapshot software version and dated CHANGELOG entry;
4. verify the release candidate on the accepted `main` revision;
5. create the matching immutable `vX.Y.Z` tag on that verified revision;
6. run the build/test/smoke evidence again from the tagged revision itself;
7. verify released artifacts report the expected software version, source revision and build identity;
8. retain the release artifacts, checksums and applicable verification evidence;
9. record the closure evidence in the coordination repository;
10. move normal development to the next planned `-SNAPSHOT` version before new capability work starts;
11. only then mark the SIP step `completed` and activate the next step.

A release version is consumed once its normal candidate tag has been created. If verification of that tagged revision fails, archive the candidate as `vX.Y.Z-failed` on the same commit, verify the archival tag, remove the normal `vX.Y.Z` tag and do not treat it as a valid release. Record the failed version in the CHANGELOG as `FAILED DURING RELEASE BUILD`; the next attempt advances the patch version rather than reusing the failed version. A `-failed` tag is historical evidence only and must never trigger or represent a normal release.

A planning/documentation step that produces no releasable software does not need an artificial software version. Such a step may define another immutable baseline appropriate to its deliverable. That exception must not be used to avoid a normal release when the step has produced a meaningful software baseline.

### Step 1 — Architecture baseline

Status: completed

#### Goal

Define enough software-system/component architecture to start the framework repository deliberately.

#### Current scope and outputs

- `docs/03-domain-baseline.md`;
- `docs/04-UC-system-use-cases.md`;
- `docs/30-SSAD-software-system-architecture.md`;
- `docs/31-01-SAD-timing-application-architecture.md`;
- `docs/31-01-SDD-01-data-and-display-design.md`;
- `docs/31-01-SDD-02-java-component-design.md`;
- `docs/31-01-SDD-03-backoffice-transport-design.md`;
- `docs/31-02-SAD-gui-application-architecture.md`;
- `docs/31-03-SAD-web-operator-application-architecture.md`;
- `docs/50-SVP-software-verification-plan.md`;
- software-item register and system interface catalogue;
- generated architecture/state-model diagrams on `dev/pr-<N>/docs`;
- Maven as accepted build tooling;
- Java 8 as accepted initial baseline for the mandatory original Raspberry Pi Zero target;
- Java 11 as a later evidence-driven upgrade candidate;
- `TimingSystemInstance` as logical total-system isolation boundary;
- registration assets and registration sources as separate concepts;
- serialized execution/threading direction;
- first-class status model;
- fault/recovery architecture direction;
- Pi Zero resource-baseline strategy;
- platform/device ports;
- public/private extension strategy;
- registration and ready-team traceability as separate capabilities;
- in-memory active state with simple file backup/restore;
- transport-independent backoffice boundary with socket and RabbitMQ adapter directions;
- layered system-test strategy (`ST-1` through `ST-4`).

#### Deliverable

A reviewable **software architecture baseline package** in GitHub consisting of the domain baseline, use cases, SSAD, software-item SAD/SDDs, SDE/SVP and generated architecture document set.

This package is sufficient to create the first implementation repository without inventing its fundamental boundaries during coding.

#### Demonstration

Walk through the generated `dev/pr-<N>/docs` documentation and demonstrate, using the diagrams and documents, that a reviewer can answer at least:

1. What are SI-01, SI-02 and SI-03?
2. How can one SI-01 process host multiple total-system instances?
3. How do registration assets, registration sources and antennas relate?
4. Where are mutable state and threading controlled?
5. How can public stubs and private production implementations use the same contracts?
6. How do console/GUI/web clients reach the same application behaviour?
7. How can backoffice communication use a lightweight socket transport for tests and RabbitMQ for production-shaped integration?
8. What is tested at unit, application, socket-loop, RabbitMQ and hardware levels?

No executable product behaviour is claimed in this step.

#### Evidence / exit criteria

- SI-01, SI-02 and SI-03 responsibilities are understandable;
- principal system interfaces are catalogued and future IDD ownership is clear;
- system, runtime, core, adapter and client responsibilities are understandable;
- Maven module/package direction is clear enough to create the framework skeleton;
- registration versus ready-team ownership is explicit;
- registration asset versus registration source ownership is explicit;
- status/lifecycle/fault concepts are separated cleanly;
- public contracts can support stubs and private implementations;
- a verification strategy exists before implementation begins;
- use cases provide an operational bridge toward formal requirements;
- unresolved decisions remain visible rather than being silently assumed;
- generated diagrams and documentation are successfully built and reviewable in GitHub.

### Step 2 — Framework repository skeleton

Status: completed

#### Goal

Complete the public SI-01 framework/application repository baseline and prove that it can be bootstrapped, built, tested and run independently.

#### Scope

- Maven parent/reactor with the current artifact baseline:
  - `framework/` -> `event-timing-framework.jar`;
  - `app/` -> `event-timing-app.jar`;
- Java 8 compiler/runtime baseline;
- responsibility/package boundaries inside the framework without mapping every architecture layer to a separate Maven artifact;
- version/build identity source;
- logging baseline;
- unit-test framework;
- GitHub Actions build/test;
- architecture/dependency checks where useful;
- minimal runnable headless startup/shutdown lifecycle;
- repository baseline from the SDE (`README.md`, `AGENTS.md`, `CHANGELOG.md`);
- shared `tool.git-project` / `tool.java-project` project-file bootstrap and reusable workflow conventions.

Externalised application settings/configuration become active in Step 3, where a real `TimingSystemInstance` and public application interfaces exist to consume them. Step 2 does not add a placeholder configuration model solely to satisfy planning text.

No production device/backoffice protocols yet.

#### Deliverable

A clean public Java/Maven repository that can be cloned, bootstrapped, built and tested independently and produces both the reusable framework JAR and a minimal runnable headless application JAR.

#### Demonstration

From a clean checkout, bootstrap the pinned tooling, run the canonical Maven verify/build, produce the framework and app artifacts, start the app, show build/version identity, and shut it down cleanly.

```text
bootstrap project tooling
    -> exact pinned tooling revisions are restored

run the canonical Maven verify/build
    -> framework and app compile
    -> automated checks pass
    -> framework and runnable app artifacts are produced

run the app artifact
    -> application starts
    -> build/version identity is visible
    -> application shuts down cleanly
```

#### Evidence / exit criteria

- clean checkout/project bootstrap succeeds on supported development environments;
- GitHub Actions is green;
- Java 8 source/bytecode baseline is enforced;
- `framework/` remains reusable and `app/` owns executable composition;
- package/dependency direction follows the documented architecture;
- concrete device/network libraries are not required by domain/application responsibility packages unless their boundary role explicitly requires them;
- minimal startup/shutdown is covered by automated tests where practical;
- framework and app artifacts are produced with traceable build/version identity;
- a readable unit-test summary is retained together with the raw Surefire evidence;
- the released `tool.java-project` baseline is independently proven by `template.java-project` and then consumed by the product repository using the corresponding exact immutable tooling revision;
- README explains bootstrap/build/run/test;
- repository contains the required SDE baseline files;
- final Step-2 closure is release `0.1.0`, with a matching `v0.1.0` tag, independently green tag build/test/smoke evidence and verified artifact build identity.

#### Step-2 release closure

Release `0.0.1` was used successfully as an end-to-end **release-process trial**. It proved release preparation, tag creation, independent tag verification, build identity, release artifact publication and post-release return to a snapshot version. It is not the Step-2 software baseline.

The accepted Step-2 software baseline is **release `v0.1.0`**:

- release commit: `3a42e5683ce97dff2ef17caf2ec543e96a54cbd9`;
- `v0.1.0` points to that exact commit;
- main release verification run **#67** is green and published `prod/bld` from that commit;
- independent tag verification run **#68** is green;
- Linux canonical build, independent Windows build and execution on Windows of the exact Linux-built application JAR are green;
- the readable Surefire summary reports **13 tests, 0 failures, 0 errors and 0 skipped**;
- `prod/bld` contains `event-timing-framework-0.1.0.jar` and `event-timing-app-0.1.0.jar` with traceable source identity;
- the GitHub Release retains both JARs, SHA-256 sums and the release-evidence archive;
- `tool.java-project v0.1.0` is the released Java project-tooling baseline and is separately proven by its own tag self-test, `template.java-project`, and the real framework consumer.

This evidence satisfies the Step-2 release/identity proof. Normal development advances to `0.2.0-SNAPSHOT` before Step-3 capability work begins.

### Step 3 — Minimal version/status application on development host (SI-01)

Status: active

#### Goal

Prove the public runtime/application boundary with deliberately small behaviour on the primary development environment before introducing target-image complexity.

Windows is the first concrete execution target for this step. Linux-host execution may also be included through CI or developer testing, but Raspberry Pi deployment is deliberately separated into Step 4.

#### Scope

- one central version source;
- central application/status model;
- version/status readable through:
  1. local console/shell;
  2. remote terminal/shell;
  3. HTTP/JSON API;
- minimal WebSocket status/event stream;
- minimal configurable `TimingSystemInstance`;
- transport adapters do not own application state;
- application handlers can run synchronously in unit tests;
- logging and externalised settings are active;
- first `ST-1 Application Behaviour` black-box tests through the public application interface;
- GitHub Actions verifies fast tests;
- repeatable Windows execution from built artifacts.

#### Deliverable

The first useful SI-01 executable for the development environment: a headless Java application with one shared version/status model exposed through multiple interfaces and a repeatable black-box test path.

#### Demonstration

On a Windows development machine, start SI-01 from the built artifact and show:

```text
local console  -> version + status
remote shell   -> same version + equivalent status
HTTP/JSON      -> same version/status model
WebSocket      -> receive a status/event update
```

Then run the `ST-1` black-box scenario against that process.

A useful stakeholder statement is:

> We now have the real headless application running as a separate process and can inspect the same live state through all initial public interfaces.

#### Evidence / exit criteria

- automated tests verify shared application behaviour rather than duplicating behaviour in each transport;
- `ST-1` demonstrates the running process through public interfaces;
- GitHub Actions is green;
- Windows execution from produced artifacts is repeatable;
- Linux-host execution is smoke-tested where practical;
- lifecycle/status architecture is not coupled to one client transport;
- no Raspberry Pi-specific code is required to run the application behaviour;
- Step 3 closes through the release-backed completion model, with the current development line targeting `0.2.0` unless implementation evidence deliberately replans the release version.

### Step 4 — Raspberry Pi Zero image, target run and update automation

Status: not started

#### Goal

Move the already-working SI-01 executable to the mandatory original Raspberry Pi Zero / Zero W using reproducible automation rather than a hand-built target.

This step deliberately introduces target deployment early. It should establish both **clean-device provisioning** and a **fast application-update path** before the rest of the product grows.

#### Scope

##### Reproducible target image

- select and pin the supported Raspberry Pi OS/base-image baseline;
- select and pin the ARMv6-capable Java 8 runtime;
- automated construction/customisation of a complete flashable Pi image;
- install SI-01 artifact and required runtime files;
- install service definition/startup configuration;
- include safe default/public configuration only;
- keep deployment secrets and real/proprietary configuration out of the public image source;
- record image/source/application/runtime versions for traceability.

The concrete image technology remains an implementation choice. Candidates may include a Raspberry Pi image-generation toolchain or deterministic customisation of a pinned base image. The requirement is reproducibility, not a specific image builder.

##### Application update path

Normal SI-01 changes should not require reflashing the complete SD image.

Introduce a versioned update artifact/process capable of at least:

- transferring/installing a new SI-01 application build onto an existing prepared Pi;
- stopping/restarting the service safely;
- reporting the running application version;
- preserving configuration/data that should survive an application update;
- supporting an initial rollback/recovery direction.

Full-image rebuilding remains appropriate for OS, Java runtime or image-layout changes.

##### Target verification

- boot the generated image on an original Pi Zero / Zero W;
- automatically start SI-01 as a service;
- run version/status checks over the network;
- establish the first real Pi Zero resource baseline;
- capture startup time, RSS/heap behaviour, CPU, thread count and response latency;
- exercise the application-update path on the same target.

#### Deliverable

Two concrete build/deployment artifacts:

1. a **reproducibly generated, flashable Raspberry Pi Zero image** containing the pinned Java runtime and SI-01 service;
2. a **versioned SI-01 application-update artifact/process** for updating an already provisioned target without reflashing the whole image.

The image/update artifacts should be produced by CI or an equally reproducible automated build path rather than committed as source files to normal Git branches.

#### Demonstration

Starting from generated artifacts:

1. flash the generated image to an SD card;
2. boot an original Raspberry Pi Zero / Zero W;
3. show that SI-01 starts automatically as a service;
4. query version/status over HTTP from another computer;
5. show the pinned OS/application/Java build identity;
6. record the first Pi Zero resource measurements;
7. build a newer SI-01 version;
8. apply the application update **without reflashing the SD card**;
9. show that the service restarts and reports the new version;
10. demonstrate the initial rollback/recovery route where implemented.

A useful stakeholder statement is:

> We can generate a complete target image automatically, boot it on the weakest supported hardware, and deploy a new application version without rebuilding the device by hand.

#### Evidence / exit criteria

- complete image construction is scripted/reproducible from documented inputs;
- image provenance includes OS/base image, Java runtime and SI-01 version/commit;
- the resulting image boots on real original Pi Zero hardware;
- SI-01 starts automatically through the target service manager;
- HTTP version/status is reachable remotely after boot;
- the first Pi Zero resource baseline from the SVP is recorded;
- application update can be repeated without manual file-copy guesswork or full-image reflashing;
- persistent configuration/data required across app updates is preserved;
- no secrets or real proprietary deployment mappings are embedded in the public image recipe;
- CI/build artifacts are retained sufficiently for review/reproduction.

### Step 5 — First Desktop GUI client (SI-02)

Status: not started

#### Goal

Prove a separate software item can consume the system-defined application control/status interface, including when SI-01 runs on a different host such as a Raspberry Pi.

#### Scope

- connect/disconnect;
- configure/select SI-01 endpoint;
- display application version;
- display application, timing-system and subsystem status;
- show disconnected/stale state;
- no direct dependency on internal SI-01 runtime classes or filesystem;
- verify local development connection and remote Pi connection.

This step is deliberately early because it validates the network/interface boundary before the domain becomes large.

#### Deliverable

A separately runnable desktop GUI application that connects to SI-01 only through the defined network interface.

#### Demonstration

Run SI-02 on a workstation and:

1. connect to SI-01 running locally;
2. show live version/status;
3. stop SI-01 and show clear disconnected/stale state;
4. reconnect;
5. change the configured endpoint to the Step-4 SI-01 image running on a Raspberry Pi;
6. show the same information without changing GUI business logic.

#### Evidence / exit criteria

- GUI and SI-01 build independently;
- GUI contains no direct dependency on SI-01 implementation classes;
- automated interface tests cover connect/status/disconnect where practical;
- local and remote-Pi demonstrations both work;
- the interface model is sufficient to support a genuinely separate client.

### Step 6 — External reference/test project

Status: not started

#### Goal

Create a separate public consumer/template project that builds against framework Maven artifacts and becomes the primary integration-learning environment.

#### Scope

- complete runnable composition using public/stub adapters;
- deterministic integration scenarios;
- use of `timing-testkit`;
- console/remote/API/WebSocket system tests;
- `ST-1 Application Behaviour` scenarios;
- lightweight `ST-2 Socket Loop` transport and backoffice simulator;
- configurable multiple system instances/assets/sources;
- fault injection through stubs/test-control;
- documentation proving external consumer setup;
- CI that builds without relying on framework-reactor internals.

#### Deliverable

A separate public reference repository that consumes published/local Maven framework artifacts exactly as an external project would and can run a fully synthetic timing environment.

#### Demonstration

From the reference project only:

1. resolve the framework artifacts;
2. start one SI-01 composition with stub devices;
3. control it through the normal application interface (`ST-1`);
4. start a simple socket backoffice simulator (`ST-2`);
5. configure at least two synthetic registration sources;
6. exchange source-aware messages over the socket boundary;
7. disconnect/reconnect the simulator and show status/recovery;
8. optionally scale the configuration to several `TimingSystemInstance` objects.

#### Evidence / exit criteria

- reference project builds without framework reactor internals;
- no framework source copy/fork is required;
- public APIs/SPIs are sufficient to compose the application;
- `ST-1` and `ST-2` run automatically in CI where practical;
- multi-source routing is deterministic;
- test controls exercise normal adapters/queues rather than mutating domain state directly;
- documentation is sufficient for a new consumer to run the project.

### Step 7 — Proprietary extension proof

Status: not started

#### Goal

Prove one private implementation can replace a public stub through the same API/SPI contract.

#### Scope

Preferred early candidate:

- production RFID antenna adapter shell and/or proprietary tag protocol/decryption component.

#### Deliverable

A private component/application composition that replaces at least one public stub using only the supported public framework contracts.

#### Demonstration

Run the same reference/application scenario twice:

```text
composition A -> public stub implementation
composition B -> private implementation
```

Demonstrate that the higher-level application behaviour and test interface remain the same and that no public framework source change is required to select the private component.

#### Evidence / exit criteria

- public framework source remains unchanged;
- reference and private applications use the same public contract;
- private Maven/dependency consumption works through the chosen secure mechanism;
- private code is not required to compile/test the public framework;
- public verification remains meaningful without exposing proprietary protocol details;
- private identifiers/protocol data do not leak into public repository fixtures.

### Step 8 — Timing-system data/state foundation (SI-01)

Status: not started

#### Goal

Implement deterministic local domain behaviour without production hardware.

#### Scope

##### Registration

- registration assets and registration sources;
- per-source monotonic sequence number;
- per-source registration ledger/file;
- passage, start, manual, penalty and revocation records;
- traceable correction/revocation relationships;
- local derived result/ranking views.

##### Ready-team

- separate ready-team event journal;
- add/remove actions;
- current ready-team state projection;
- current ordered list for display logic;
- traceable persisted history.

##### Reference data

- start-time repository;
- reserve-tag conversion repository;
- synchronisation/version metadata.

##### Persistence

- in-memory repositories as application API;
- simple file backup/restore;
- source sequence-state recovery;
- explicit backup/restore status;
- fault-injection tests for failed/corrupt backup/restore paths.

##### State/recovery

- explicit `OPEN`/`CLOSED` lifecycle independent from subsystem health;
- RFID lifecycle/recovery model available to the domain/status layer;
- explicit stale/degraded/error status where relevant;
- bounded queue/backpressure behaviour designed and verified before representative load testing.

Promote mature candidate requirements before implementation.

#### Deliverable

A locally complete, deterministic timing-domain core that can maintain registrations, source sequences, ready-team state and reference data through public application commands and survive a process restart through the initial persistence mechanism.

#### Demonstration

Using only synthetic data and public/test interfaces:

1. start an instance with at least two synthetic registration sources;
2. open the timing-system instance and show the traceable open record;
3. create registrations on both sources and show independent source sequences;
4. add and remove ready-team numbers and show current state plus history;
5. load synthetic start-time/reference data and show a local derived timing/ranking result;
6. stop the application;
7. restart it;
8. demonstrate recovered state and continued source sequences without number reuse;
9. show an injected backup/recovery fault in status.

#### Evidence / exit criteria

- deterministic unit tests cover domain/state transitions;
- source sequence and gap/identity rules are tested;
- registration and ready-team stores remain separate;
- backup/restore/restart tests are automated;
- state can be driven without production hardware;
- fault/status behaviour is explicit rather than silent.

### Step 9 — Web/iPad operator application (SI-03)

Status: not started

#### Goal

Provide the React-based operational client over the existing HTTP/WebSocket system interface.

#### Scope

- SI-01 serves the compiled React bundle;
- show registrations/status;
- open/close timing-system instance;
- start procedure control;
- show/manage ready-team state;
- later manual registrations/penalties where authorised;
- clear stale/disconnected representation;
- reconnect obtains a complete current state before normal live updates continue;
- verify representative iPad/Safari use;
- local browser operation does not require live internet/backoffice when SI-01 remains locally reachable.

Business rules remain server-side in SI-01.

#### Deliverable

A browser/iPad operator application served by SI-01 that performs useful timing operations over HTTP/WebSocket without containing authoritative domain logic.

#### Demonstration

On an iPad/browser connected to the local network:

1. navigate to SI-01 and download the React application;
2. view current application/system status and registrations;
3. open/close a system instance;
4. perform a start-procedure command;
5. add/remove ready-team entries where in scope;
6. observe live WebSocket updates;
7. interrupt the connection and show stale/disconnected state;
8. reconnect and show a fresh complete snapshot followed by live updates.

#### Evidence / exit criteria

- representative Safari/iPad flow works;
- application remains usable on local LAN without internet where required;
- UI actions use the public SI-01 interface;
- reconnect/stale-state behaviour is verified;
- business rules remain server-side.

### Step 10 — Stub-controlled hardware integration

Status: not started

#### Goal

Exercise complete device and recovery flows deterministically before production adapters are integrated.

#### Scope

Stub/test-control scope may include:

- RFID power/lifecycle and raw reads;
- RFID health/heartbeat;
- RFID boot/reinitialise/error paths;
- encrypted/decrypted test pipeline inputs at appropriate public boundaries;
- CAN bus and discovery;
- keypad team add/remove;
- V1 display discovery/control/reconnect;
- V2 display connection/data synchronisation/reconnect;
- local network/internet/backoffice failures and recovery;
- queue pressure scenarios.

Injected events must follow the same normal application paths as real adapters.

#### Deliverable

A controllable synthetic hardware environment capable of driving the complete SI-01 device lifecycle and fault/recovery behaviour through supported adapter contracts.

#### Demonstration

Run an automated/manual scenario such as:

```text
RFID initially OFF
-> operator powers RFID on
-> simulate boot delay
-> READY
-> inject several raw observations
-> filtering accepts one registration
-> simulate heartbeat loss
-> status becomes degraded
-> reinitialise RFID
-> READY again

CAN scanner discovers synthetic Display V1
keypad adds/removes teams
Display V1 receives current ready-team list
Display V2 connects, receives snapshot, disconnects and reconnects
```

#### Evidence / exit criteria

- scenarios are repeatable without real hardware;
- injected faults enter through normal adapter boundaries;
- timing/domain state is never directly manipulated by test code;
- lifecycle/recovery/status tests are automated where practical;
- same contracts remain suitable for production adapters.

### Step 11 — Production RFID/CAN/display integration

Status: not started

#### Goal

Replace proven stubs with real implementations.

#### Scope

- private RFID antenna/control adapter;
- proprietary RFID decrypt/protocol implementation;
- RFID filtering/tuning;
- production CAN adapter;
- periodic device scanner;
- keypad protocol;
- V1 passive CAN display driver;
- V2 mDNS/network data interface;
- status/heartbeat/recovery behaviour;
- hardware-in-the-loop verification from the SVP.

#### Deliverable

A hardware-capable SI-01 deployment in which the previously demonstrated synthetic device flows work with representative real RFID, CAN, keypad and display hardware.

#### Demonstration

On representative hardware:

1. start SI-01;
2. power/initialise the RFID subsystem and observe health/status;
3. present representative tags and observe filtered registrations;
4. discover supported CAN devices;
5. enter/remove team numbers through the physical keypad and observe Display V1;
6. connect a Display V2 through the network/mDNS path and show data synchronisation;
7. force at least one recoverable device failure/reconnect and demonstrate recovery.

#### Evidence / exit criteria

- HIL scenarios from the SVP pass;
- production adapters replace stubs without changing core/domain behaviour;
- proprietary implementation remains private;
- device status/recovery is observable;
- Pi Zero resource behaviour remains viable for representative production topology.

### Step 12 — Backoffice/reference-data integration

Status: not started

#### Goal

Connect local operation to the real backoffice while retaining offline capability and validate the production-shaped RabbitMQ transport independently from application semantics.

#### Scope

- system-level IDD(s);
- transport-independent backoffice semantic boundary retained;
- RabbitMQ adapter;
- per-source inbound queue consumers;
- per-source outbound routing endpoints;
- start-time synchronisation;
- reserve-tag mapping synchronisation;
- registration outbox/delivery;
- retry/reconnect/idempotency/reconciliation;
- network/link/internet/broker status;
- `ST-3 RabbitMQ Integration` using a disposable Docker/Compose broker with synthetic topology;
- private/production protocol implementation where required;
- fault/recovery verification with network/internet/broker failures separated.

#### Deliverable

A backoffice-integrated SI-01 implementation with offline-safe local operation, source-aware inbound/outbound synchronisation and a reproducible RabbitMQ integration-test environment.

#### Demonstration

First with the public/synthetic `ST-3` environment:

1. start the RabbitMQ Docker/Compose broker;
2. start SI-01 with at least two synthetic sources;
3. show two independent inbound source consumers over shared broker infrastructure;
4. inject reference data and show local update;
5. create registrations and show source-specific outbound routing;
6. stop RabbitMQ while local registration continues;
7. show pending outbox/status;
8. restart RabbitMQ;
9. show consumer restoration and pending delivery/reconciliation.

Where permitted, repeat the applicable interface scenario with the private/real backoffice configuration without exposing those details in public evidence.

#### Evidence / exit criteria

- Docker/Compose RabbitMQ integration suite is automated in CI where practical;
- source isolation/routing is verified;
- local data is not lost during broker outage;
- reconnect restores configured consumers and pending delivery;
- actual proprietary mappings/protocol remain outside the public repository;
- IDD and software-item implementation remain traceable.

### Step 13 — Deployment hardening and operationalisation

Status: not started

#### Goal

Turn the early Step-4 image/update automation into a production-supportable deployment lifecycle once the application, devices and backoffice integration are representative.

#### Scope

- harden/review the Raspberry Pi image-generation pipeline;
- service startup/restart and watchdog/recovery policy;
- configuration and secret provisioning;
- application update policy and artifact retention;
- rollback/recovery after failed update;
- OS/runtime/image update policy;
- diagnostic/support export;
- longer-running integration and hardware-in-the-loop tests;
- `ST-4 Target / Full-system` scenarios;
- resource budgets promoted from measured baselines where evidence supports useful limits.

#### Deliverable

A reproducibly deployable and supportable Raspberry Pi operational environment with documented clean provisioning, configuration, service management, normal application updates, image-level updates, diagnostics and recovery procedures.

#### Demonstration

Using the automated deployment pipeline established in Step 4:

1. create/flash a clean target image;
2. provision environment-specific configuration and secrets through the supported mechanism;
3. boot and show automatic service startup;
4. connect SI-02 and/or SI-03 and show normal operation;
5. perform a normal application update;
6. demonstrate rollback/recovery from a deliberately failed update;
7. demonstrate the documented image/OS/runtime upgrade path where applicable;
8. produce a diagnostic/support export;
9. run the representative `ST-4`/HIL operational scenario.

#### Evidence / exit criteria

- provisioning and update pipelines are repeatable from documented automation;
- service survives reboot/restart as required;
- configuration/secrets are not embedded in public source or generic image artifacts;
- update/rollback/recovery paths are verified;
- artifacts and versions remain traceable;
- resource measurements remain within accepted/promoted budgets;
- operational diagnostics provide enough information to investigate common faults.

### Java 11 checkpoint

Status: future / evidence-driven

Do not block early development on Java 11.

When the application is representative enough, compare Java 11 with the working Java 8 baseline on the same Pi Zero hardware/workload for runtime availability, deployment, startup, memory, threads, CPU, responsiveness, library compatibility and maintenance support.

#### Deliverable

A short evidence-backed architecture decision: retain Java 8, move to Java 11, or defer the decision.

#### Demonstration

Run the same representative workload on the same Pi Zero class using the known Java 8 baseline and candidate Java 11 runtime and show the measured comparison.

#### Evidence / exit criteria

Only an explicit architecture decision with target-hardware evidence may supersede the Java 8 baseline.

### Planning rules

- Every implementation step should end with a concrete deliverable and repeatable demonstration.
- A successful demonstration is not by itself sufficient evidence for completion.
- A software-producing step normally closes with a normal verified software release; do not substitute an arbitrary planning tag for a meaningful release baseline.
- A failed tagged release candidate is archived as `vX.Y.Z-failed`, consumes that version, and the next release attempt advances the patch version.
- Prefer demonstrations that exercise the same public interfaces/adapters intended for normal operation instead of special demo-only bypasses.
- Establish target-image and application-update automation early; do not let manual Pi provisioning become the normal development workflow.
- Prefer fast application updates for ordinary SI-01 changes; rebuild/reflash complete images when OS/runtime/image-level inputs change.
- Do not start a later software step merely because an abstraction already exists.
- Keep fast unit/build checks suitable for normal pull requests.
- Separate longer integration/hardware/deployment pipelines when needed.
- Keep system-level IDDs authoritative for interfaces; software-item SRDs reference them where applicable.
- Keep implementation/evidence details in the active implementation PR.
- Keep registration and ready-team models distinct unless an explicit later requirement defines an interaction.
- Keep registration asset identity, registration-source identity and external deployment mapping distinct.
- Prefer public contracts plus composition over subclass-based/private-source coupling.
- Measure Pi Zero resource behaviour from the first target image and avoid invented numeric budgets without evidence.
- Keep lifecycle state, subsystem health and connectivity status separate concepts.


---

## Software Development Environment (SDE)

**Source document:** [12-SDE-software-development-environment.md](./12-SDE-software-development-environment.md)

Status: working draft / non-authoritative

This Software Development Environment document defines the **concrete engineering environment and repository conventions** used to develop, build, test, document and review the software system.

The SDE is project/software-system level and applies across software items and implementation repositories unless a repository documents a justified exception.

### Document boundary

The SDE is not the high-level development plan and it is not the detailed implementation sequence.

Use the documents as follows:

```text
SDP  why/how the project is developed at high level: strategy, phases, risks, resources, assumptions
SIP  what is implemented next: concrete steps, deliverables, demonstrations and exit evidence
SDE  where/how engineering work is performed: repositories, tooling, GitHub flow, CI, artifacts, local environments
SVP  how the product is verified: levels, profiles, verification cases and evidence
```

The SDE may define detailed mechanisms that support the SDP/SIP/SVP, but should not duplicate their planning or verification content.

### Purpose

The development environment should make work:

- reproducible;
- reviewable;
- traceable from issue through implementation and verification;
- usable by both human developers and AI agents;
- consistent across public and private repositories;
- suitable for generated documentation and build artifacts;
- easy to reconstruct on a new workstation or CI runner;
- simple enough for a small project without losing engineering discipline.

### Development hosts and execution environments

The high-level need for development/test hardware belongs in the SDP. This SDE defines how those environments are used once selected.

Expected environment classes are:

```text
Developer workstation
  primary interactive development
  initially Windows
  Java/Maven/Python/Git
  optional Docker/Compose

GitHub-hosted CI
  build/unit/system/integration automation where supported
  generated documentation/artifacts

Raspberry Pi Zero target
  generated target image
  pinned ARMv6-compatible Java runtime
  SI-01 service
  target/resource/HIL verification

Optional integration host
  broker/test services
  test drivers/simulators
  longer integration workloads
```

Exact host provisioning scripts and image tooling are introduced by the relevant SIP steps and implementation repositories.

### Primary development services and tools

Current baseline:

- **GitHub** — source control, issues, pull requests and review history;
- **GitHub Actions** — automated build, test, generated documentation and later image/deployment workflows;
- **Git** — source/version control;
- **Maven** — Java build/dependency-management baseline;
- **Java 8** — initial SI-01 language/API/runtime baseline;
- **Python** — lightweight project tooling/document generation where appropriate;
- **draw.io + generated SVG** — editable and GitHub-readable diagrams;
- **Docker / Docker Compose** — reproducible external integration services such as RabbitMQ where a real service materially improves verification.

Individual repositories may add tools, but system-wide additions should be deliberate and documented.

### Repository baseline

Every implementation or coordination repository is expected to contain at least:

```text
README.md
AGENTS.md
CHANGELOG.md
```

#### `README.md`

The human entry point. It should normally contain:

- repository purpose;
- relationship to the wider software system;
- build/run/test entry points or links;
- important document/navigation links;
- generated-output links where applicable.

#### `AGENTS.md`

Persistent repository-specific instructions for AI/coding agents, including:

- repository purpose and boundaries;
- sources of truth;
- workflow rules;
- files that must be read before work;
- public/private boundaries;
- build/test expectations;
- scope/plan discipline.

AI follows the same controlled engineering workflow as human development.

#### `CHANGELOG.md`

Records notable repository changes. It does not replace Git history, issue history or PR evidence.

### Repository content layout

Exact source trees differ by repository, but use predictable top-level locations where applicable.

Typical coordination/documentation repository:

```text
README.md
AGENTS.md
CHANGELOG.md
.github/
  workflows/
docs/
reference/
tools/
bld/                 local/generated build output; normally ignored in source
```

Typical Java implementation repository may evolve toward:

```text
README.md
AGENTS.md
CHANGELOG.md
.github/
  workflows/
docs/
<module>/
  src/main/...
  src/test/...
tools/
integration/         integration fixtures/config where useful
bld/ or target/      generated output, not hand-maintained source
pom.xml
```

Do not create directories merely to satisfy a template. Introduce them when the repository has content that belongs there.

#### Source versus generated versus reference material

Keep these categories distinct:

- **source** — hand-maintained code/config/documentation on normal branches;
- **generated output** — CI/build artifacts, generated documents/images/packages/images;
- **reference material** — preserved external/source documents used for research or traceability;
- **runtime/deployment data** — environment-specific configuration, secrets and mutable operational data; not normal public source.

Generated output should not be manually edited as if it were source.

### Documentation layout

Use predictable numbered document families in the meta/engineering documentation where applicable:

```text
00-09  working context, brainstorm, use cases and domain baseline
10-19  development planning/environment
20-29  requirements / SRDs
30-39  architecture and detailed design
40-49  system-level IDDs
50-59  verification planning
```

Established abbreviations include `SDP`, `SIP`, `SDE`, `SRD`, `SSAD`, `SAD`, `SDD`, `IDD`, `SVP` and `UC`.

Software-item numbers remain stable across requirement/design documents.

### GitHub issue → branch → pull-request workflow

Normal development follows a PR-first workflow:

```text
issue / work item
      ↓
feature branch
      ↓
draft pull request
      ↓
implementation + discussion + tests + evidence
      ↓
ready-for-review
      ↓
merge
```

#### Issue/work-item creation

Use a GitHub issue when useful to reserve/identify work and provide a stable work number.

#### Feature branch

Create from the intended target branch using:

```text
feature/pr-<N>-<short-slug>
```

Do not perform normal work directly on `main`.

#### Draft PR as active work container

Create/promote the draft PR early. It carries:

- scope;
- change-specific design discussion;
- implementation commits;
- tests/results;
- generated evidence;
- deviations and deferred scope;
- review conversation.

Long-term planning documents should not become detailed activity logs when the PR can carry that evidence.

#### Review and merge

Before merge:

- required checks are green;
- generated outputs have been inspected where relevant;
- important evidence is recorded;
- documentation/changelog updates are included where required;
- deferred or unresolved scope is explicit.

### Branch protection direction

Expected default-branch policy:

- require pull requests for normal merges;
- prevent force pushes;
- restrict deletion;
- allow zero required approving reviewers where appropriate for a solo-maintainer project;
- require meaningful stable CI checks once available;
- delete merged feature branches where appropriate.

Do not introduce merge queues or similarly heavy process unless there is a concrete need.

### Generated-output branches

Build outputs may be published separately from source branches.

General pattern:

```text
source PR/branch
      |
      | CI
      v
dev/pr-<N>/<output-type>
      |
      | merged main
      v
prod/<output-type>
```

Current documentation example:

```text
dev/pr-<N>/docs
prod/docs
```

Rules:

- generated branches are build output;
- the normal source branch is authoritative;
- generated PR branches exist so human/AI reviewers can inspect the real generated result before merge;
- corresponding `dev/pr-N/...` branches should be removed when the PR closes;
- `prod/...` represents output generated from merged/default-branch source.

The same approach can later be used for target images/packages when it provides useful review/release separation.

### Generated documentation

Source documentation remains Markdown plus project-controlled diagram-generator source.

The generated documentation set may contain:

- complete GitHub-readable Markdown copies;
- local SVG assets;
- editable draw.io files;
- combined review books;
- source commit/provenance metadata.

Generated documents are for review/publication. Their source Markdown remains authoritative.

### AI-assisted development environment

AI is an engineering tool inside the repository process, not an alternative process.

Before substantial work an agent should:

1. read `AGENTS.md`;
2. read handoff/active plan where present;
3. inspect the current open/draft PR;
4. inspect predecessor PR context when relevant;
5. identify the active SIP/AP scope;
6. work within that scope unless a plan correction is necessary.

An agent must not:

- bypass PR-first development;
- treat brainstorm material as approved requirements automatically;
- silently promote major architecture decisions;
- copy proprietary/private information into public source;
- edit generated branches as hand-maintained source;
- claim test/build/hardware evidence that was not actually produced.

### AI/session handoff environment

A new session should reconstruct current state from repository artifacts rather than requiring hidden conversation state.

Preferred sources include:

```text
AGENTS.md
current open/draft PR
relevant predecessor PR
active SIP/AP material
requirements / architecture / IDDs
README.md
CHANGELOG.md
```

Active implementation evidence belongs mainly in the PR. Persistent rules belong in `AGENTS.md`; development strategy belongs in the SDP; implementation ordering belongs in the SIP.

### Build and CI environment

Implementation repositories should introduce CI from the first useful increment.

Environment expectations include:

- Maven build/test entry points that also work locally;
- Java source/bytecode baseline enforced in build configuration;
- fast checks suitable for normal PRs;
- separate integration jobs where external services make tests slower;
- target/HIL workflows separated from hosted-runner-only tests;
- generated artifacts retained or published when they improve review/traceability;
- CI configuration kept in source under `.github/workflows/`.

Which behaviours belong to unit, ST-1, ST-2, ST-3 or ST-4 is defined by the SVP; the SDE only defines the environment mechanisms that make those profiles executable.

### Test-support environment

The engineering environment should support progressively more realistic verification without forcing every developer/test to require all infrastructure.

Expected mechanisms include:

- in-process/direct fakes for unit/component work;
- executable SI-01 plus external test driver for application/system testing;
- lightweight native socket simulator for network-loop tests;
- Docker/Compose service fixtures for RabbitMQ-specific integration;
- real Pi Zero / hardware environment for target/HIL testing.

Do not make Docker a prerequisite for fast tests that do not need an external service.

### Containerized integration services

Docker/Compose is appropriate for real external dependencies with meaningful connection/protocol/recovery behaviour.

RabbitMQ is the first identified example.

Environment rules:

- synthetic/public test topology and credentials only;
- no real queue/source/deployment names or secrets;
- intentionally pinned image versions/tags;
- health/readiness checks;
- same basic environment usable locally and in GitHub Actions where practical;
- simple teardown/cleanup;
- restart/failure control where recovery is under test.

Detailed verification scenarios belong in the SVP and relevant SDD, not in this SDE.

### Raspberry Pi build/deployment environment

Once the relevant SIP step begins, the implementation environment should provide reproducible automation for:

- downloading/selecting a pinned compatible base OS image;
- provisioning the pinned Java runtime;
- installing SI-01 and service files;
- embedding only safe/default public configuration;
- producing a versioned flashable image artifact;
- recording source/build provenance;
- installing a versioned application update on an existing target without requiring a full reflash;
- preserving runtime data/configuration according to the application design.

The SDE defines the automation/environment expectations; the SIP defines when these are delivered and demonstrated; detailed scripts/tool choices belong in the implementation repository.

### Public and private repository environment

Public/private separation must be enforceable by normal build structure:

- public framework repositories build/test without private source;
- private implementations consume public APIs/artifacts;
- private Maven/repository credentials use secure CI/developer credential mechanisms;
- proprietary protocols and real deployment mappings remain private;
- public integration fixtures use synthetic identities;
- public reference projects prove external consumption independently from private code.

### Secrets and configuration

Credentials, tokens, encryption keys and environment-specific secrets are not committed to source control.

Use GitHub environment/repository secrets and runtime configuration mechanisms appropriate to each target.

Public example configuration uses placeholders/synthetic values.

Exact application configuration semantics remain architecture/SDD/IDD concerns.

### Tooling reproducibility

Start with the simplest adequate reproducible mechanism:

- pinned/action-versioned CI actions;
- Maven for Java;
- Python standard library where sufficient;
- native/simple socket tooling where sufficient;
- Docker/Compose for meaningful external service dependencies;
- dedicated custom build containers only when they isolate a substantial toolchain or solve a real reproducibility problem.

Do not introduce a custom Docker image merely because a small script exists.

### Repository-specific extensions

Each repository may extend this SDE via its own `AGENTS.md`, README, workflows, build files and local development documentation.

Repository-specific rules may add constraints but should not silently weaken system-level traceability/workflow rules. Material deviations should be documented.

### Open SDE topics

Environment/convention decisions still to resolve include:

- exact developer-machine JDK provisioning;
- exact ARMv6 Java runtime provisioning mechanism;
- Maven public/private artifact repository and credential setup;
- standard Java formatting/static-analysis toolchain;
- standard unit/integration-test libraries;
- reusable repository bootstrap/template conventions;
- exact ruleset/branch-protection template;
- release/version/artifact naming conventions;
- image-builder tooling and artifact-storage mechanism;
- application-update transport/install mechanism;
- generated package/image branch/release conventions;
- exact local integration-host setup if a separate host becomes necessary;
- whether generated documentation later also produces PDF/HTML.


---

## Java Build and Test Toolchain (SDE)

**Source document:** [13-SDE-java-build-test-toolchain.md](./13-SDE-java-build-test-toolchain.md)

Status: working baseline / AP-2

This document refines the system-level Software Development Environment for Java repositories. It defines the **engineering toolchain roles, build/test matrix, artifact flow and reusable-tool boundary** needed before the first SI-01 implementation repository is bootstrapped.

It does not define SI-01 product behaviour. Product requirements remain in the SRD/IDD/SAD/SDD documents, and verification intent remains owned by the SVP.

### Why this document exists

A Java repository alone is not yet a reproducible engineering environment. Before creating the first implementation repository the project needs a deliberate answer to:

- which environments build and test Java code;
- which operating systems are verified;
- how Maven itself is provisioned;
- which JDK/API baseline is authoritative;
- which job produces the canonical application artifact;
- how that same artifact is exercised on other platforms;
- which parts are generic enough to reuse across future Java repositories;
- when a dedicated/self-hosted machine is actually justified.

This document exists because those decisions are cross-repository SDE policy rather than SI-01 application design.

### Engineering roles are not physical machines

The toolchain defines **roles/environments** first. One physical computer or hosted runner can fulfil more than one role.

Initial roles:

```text
Windows developer workstation
  interactive development and demonstrations
  local Maven Wrapper build/test
  local application execution

GitHub-hosted Linux CI
  canonical CI build
  compile + unit/component verification
  package canonical Java artifact
  provenance/build metadata
  fast system-test jobs when available

GitHub-hosted Windows CI
  Windows compatibility build/test
  Windows execution/smoke verification
  later ST-1 compatibility execution

Raspberry Pi Zero target
  target execution only after the target/deployment SIP increment
  ARMv6-compatible Java 8 runtime
  resource/ST-4/HIL evidence

Optional integration/test controller
  not required initially
  later Docker/RabbitMQ services
  longer-running tests
  target/HIL orchestration when hosted CI is insufficient
```

A separate physical build server or Java test server is therefore **not an initial requirement**.

### Initial platform matrix

| Environment | Build source? | Unit/component tests | Runs canonical artifact | Main purpose |
| --- | --- | --- | --- | --- |
| Windows developer workstation | yes | yes | yes | interactive development and stakeholder demo |
| GitHub Ubuntu runner | **yes — canonical** | **yes** | yes | authoritative CI build/package path |
| GitHub Windows runner | yes, compatibility | yes | **yes** | detect Windows-specific build/runtime problems |
| Original Raspberry Pi Zero / Zero W | no normal source build required | selected target tests | **yes** | target viability/resource/HIL evidence |
| Optional Linux integration host | optional | integration/system | yes | external services and longer test orchestration |

The matrix can grow only when there is evidence that another environment materially improves verification or deployment.

### Java baseline

The first SI-01 baseline remains **Java SE 8** because the original Raspberry Pi Zero / Zero W is mandatory.

Toolchain implications:

- the canonical compile runs with a Java 8 JDK, not merely a newer JDK configured with `source=8`;
- Maven compiler/source/target settings must enforce Java 8 bytecode/source compatibility;
- the CI job records the actual JDK vendor/version used;
- source code remains vendor-neutral at the Java SE/API boundary;
- the Pi may use a different ARMv6-capable Java 8 runtime vendor from hosted CI without changing the application artifact;
- Java 11 remains a later evidence-driven compatibility/upgrade checkpoint, not part of the first canonical build.

The exact hosted-CI JDK distribution and patch version should be pinned/configured in the reusable workflow when that workflow is implemented. The exact Pi runtime is selected by the target-image SIP increment after ARMv6 evidence.

### Maven Wrapper policy

Every Java consumer/implementation repository should carry the Maven Wrapper:

```text
mvnw
mvnw.cmd
.mvn/wrapper/...
```

Normal commands are therefore repository-owned:

```text
Linux/macOS/CI:
  ./mvnw verify

Windows:
  mvnw.cmd verify
```

This avoids requiring every workstation or runner to install an independently managed Maven version.

Rules:

- the wrapper pins the Maven distribution used by the repository;
- CI invokes the wrapper rather than a runner-global `mvn` installation;
- wrapper files are source-controlled and reviewed;
- changing Maven version is a deliberate repository/toolchain change;
- the JDK remains an environment prerequisite and is provisioned explicitly by CI/developer setup.

### Canonical build and artifact model

The normal Java application artifact should be platform-neutral where the code/dependencies permit it.

Preferred flow:

```text
source commit
    |
    v
GitHub Linux canonical build
  pinned JDK 8 policy
  Maven Wrapper
  ./mvnw verify
    |
    +--> test reports
    +--> build/provenance manifest
    +--> canonical Java artifact(s)
                 |
                 +--> Linux execution/smoke
                 +--> Windows execution/smoke
                 +--> later Pi Zero execution
```

The project should **not** produce a separate Windows JAR, Linux JAR and Pi JAR merely because those operating systems are different.

A platform-specific artifact is justified only when a genuine native/platform dependency makes it necessary. Such a dependency must remain behind an appropriate adapter/module boundary rather than silently making core Java code platform-specific.

### Canonical versus compatibility builds

Two related questions need evidence:

1. can the source build/test correctly on an environment?
2. can the **same produced artifact** execute on another supported environment?

The toolchain should eventually verify both.

Initial CI direction:

```text
linux-canonical
  checkout
  set up JDK 8
  ./mvnw verify
  collect reports
  create/upload canonical artifact
  record build metadata

windows-compatibility
  checkout
  set up JDK 8
  mvnw.cmd verify

windows-artifact-smoke (when runnable app exists)
  download canonical artifact from linux-canonical
  java -jar ...
  execute first public smoke/ST-1 check
```

A Linux artifact-smoke job may use the same canonical artifact as an additional packaging sanity check.

### Build provenance

A produced artifact should be traceable without relying on a developer's workstation memory.

The build/release evidence should record at least:

```text
repository
source commit SHA
source ref/tag where applicable
project/application version
build timestamp or reproducible-build epoch policy
JDK vendor/version
Maven version from Wrapper
workflow/toolchain version
OS/runner class used for canonical build
```

Where practical, the application should embed enough non-secret build identity to answer its public version query without reading CI logs.

Reproducible-JAR settings such as a controlled Maven build output timestamp should be considered when the first Maven reactor is created.

### Test execution responsibility

The toolchain executes tests; the SVP defines what the tests mean.

Initial allocation:

#### Linux canonical CI

- compile all modules;
- unit tests;
- deterministic component/module tests that need no platform-specific behaviour;
- architecture/dependency checks;
- package artifacts;
- later fast ST-1 tests where practical;
- publish reports/artifacts.

#### Windows compatibility CI

- compile/test with the same Java source/API baseline;
- catch path, shell, filesystem and process-launch differences;
- run the canonical application artifact once it exists;
- later run a compact ST-1 compatibility subset.

#### Raspberry Pi Zero

- do not use the Pi as the normal project build machine;
- run the already-produced canonical artifact;
- verify ARMv6 runtime compatibility;
- collect startup/RSS/CPU/thread/latency evidence;
- run selected target/ST-4 scenarios.

#### Optional integration host

Introduce only when needed for capabilities that are awkward or inappropriate on hosted runners, for example:

- long-running RabbitMQ/recovery tests;
- hardware access;
- Pi image deployment/orchestration;
- CAN/RFID/display HIL;
- multi-target endurance testing.

### Docker policy

Docker is **not** part of the basic Java compile/unit-test toolchain.

Use Docker/Compose when a real external service materially improves verification, for example RabbitMQ in ST-3.

This keeps:

```text
normal Java verify
  JDK + Maven Wrapper
```

independent from:

```text
integration service fixture
  Docker/Compose + RabbitMQ/etc.
```

### Reusable `tool.java-project` boundary

Working repository name:

```text
tool.java-project
```

The name is provisional until that repository is created.

The reusable tool repository should own **generic Java-project engineering behaviour**, not product behaviour.

Good candidates:

```text
.github/workflows/
  reusable-java-verify.yml
  reusable-java-artifact.yml
  later reusable-integration entrypoints

templates/ or examples/
  minimal consumer workflow
  Maven Wrapper/bootstrap guidance

scripts/ (only when a script is genuinely reused)
  build/provenance collection
  project/toolchain validation

docs/
  supported inputs/outputs
  versioning/release policy
  consumer migration notes
```

Potential later candidates, only after repeated need is proven:

- a reusable Maven parent/convention artifact;
- a Maven plugin for project-specific convention checks;
- shared test-support tooling that is not timing-domain-specific.

Do **not** put the following in `tool.java-project`:

- SI-01 module layout as a hard-coded product assumption;
- timing-domain requirements;
- RFID/CAN/display behaviour;
- proprietary/private protocols or credentials;
- real deployment identities;
- Raspberry Pi image content that is specific to SI-01;
- RabbitMQ topology that belongs to a product/integration contract.

### Relationship to existing reusable tooling pattern

The existing SCAD tooling separates reusable project workflow from its runtime/toolchain and from consumer projects. The Java toolchain should preserve the same responsibility discipline without copying implementation mechanisms blindly.

In particular:

- Java consumers should normally use versioned/released reusable workflows rather than depend on an unversioned branch;
- Maven Wrapper remains local to each Java repository;
- a Git submodule is **not** assumed to be the Java reuse mechanism;
- reusable CI should be referenced by an immutable commit or a deliberately managed release tag/version;
- consumer projects must still be buildable/testable locally without requiring the reusable GitHub workflow repository at runtime.

### Toolchain release/use direction

A reusable toolchain change should be testable before consumers adopt it.

Target model:

```text
tool.java-project change
       |
       v
its own CI + reference consumer tests
       |
       v
versioned release/tag
       |
       v
consumer workflow pins/adopts that version
```

Consumer updates can then be reviewed as normal dependency/tooling changes rather than silently changing every project when `main` moves.

### First consumer expectation

The eventual SI-01 implementation repository becomes the first real consumer and validation project.

A clean checkout should require no globally managed Maven installation:

```text
Windows developer
  JDK 8 + Git
  mvnw.cmd verify

Linux CI
  provision JDK 8
  ./mvnw verify

Windows CI
  provision JDK 8
  mvnw.cmd verify
```

Once the application artifact exists, the exact artifact produced by the canonical Linux build should also be run by the Windows compatibility job and later by the Pi target step.

### Dedicated build/test hardware decision

Initial decision: **do not create a dedicated self-hosted build server yet**.

Rationale:

- GitHub-hosted Linux and Windows runners cover the first cross-platform build/test need;
- the developer workstation provides interactive Windows evidence;
- the Pi Zero provides target evidence;
- a self-hosted machine introduces patching, credentials, runner security and availability work before it solves a demonstrated problem.

Revisit this decision when external services, HIL, endurance or target orchestration need a stable local controller.

### Initial deliverable boundary

Before the SI-01 implementation repository is bootstrapped, the engineering baseline should be able to answer:

1. What command builds/tests a clean Java checkout on Windows and Linux?
2. Which environment is the canonical artifact producer?
3. What Java/Maven versions/policies are recorded and controlled?
4. How are test reports and artifacts retained?
5. How do we prove the canonical artifact is portable to Windows and later the Pi?
6. Which workflow/tooling logic is generic and belongs in a reusable tool repository?
7. Which configuration remains consumer/product-specific?

The next implementation increment may create the reusable tool repository and a minimal reference/fixture consumer before SI-01 adopts it.

### Open AP-2 decisions

- exact JDK 8 distribution/version used on GitHub Linux/Windows runners;
- exact Maven Wrapper/Maven version to pin initially;
- exact reusable-workflow inputs/outputs;
- whether canonical artifact publication initially uses workflow artifacts only or also a package/release channel;
- naming/version policy for `tool.java-project` releases;
- whether a minimal generic reference consumer lives inside the tool repository or as a separate template/test repository;
- when repeated Maven configuration justifies a reusable parent/convention artifact;
- exact checks used to prove the canonical JAR remains platform-neutral.


---

## Timing Application Requirements (SRD)

**Source document:** [20-01-SRD-timing-application-requirements.md](./20-01-SRD-timing-application-requirements.md)

Status: review candidate / AP-1 first-executable slice

Software item: **SI-01 — Headless Timing Application**

### Purpose

This Software Requirements Document captures only the SI-01 requirements needed for the **first executable slice** covered by the current framework-skeleton and minimal version/status SIP increments.

It is intentionally incomplete for the future product. RFID, CAN, displays, registration-domain behaviour, ready-team behaviour and production backoffice integration remain outside this requirement baseline until their SIP increments approach implementation.

The goal is to make the first executable implementable without forcing the implementation repository to invent externally visible behaviour.

### Inputs

This first slice is derived from:

- `04-UC-system-use-cases.md`, especially the status/control aspects of UC-001, UC-008 and UC-009;
- `11-SIP-software-implementation-planning.md`, the framework-skeleton and minimal version/status increments;
- `30-SSAD-software-system-architecture.md`;
- `31-01-SAD-timing-application-architecture.md`;
- `50-SVP-software-verification-plan.md`, especially ST-1.

Interface semantics for IF-03 are owned by `40-01-IDD-application-control-status.md`. This SRD references that interface rather than duplicating its protocol contract.

### Requirement identifier convention

Requirements in this slice use:

```text
SI01-REQ-<number>
```

Identifiers in this review candidate are intended to remain stable. A later capability should add requirements without renumbering these merely for document neatness.

### First-executable requirements

#### Process lifecycle and configuration

**SI01-REQ-001 — Start from external configuration**  
SI-01 shall start using externally supplied configuration rather than requiring production/deployment values to be compiled into application code.

**SI01-REQ-002 — Clean process shutdown**  
SI-01 shall support a controlled shutdown path that terminates the first-executable runtime without requiring forced process termination during normal operation/testing.

**SI01-REQ-003 — Minimal timing-system composition**  
The first executable shall support configuration of at least one `TimingSystemInstance` with a stable instance identifier that can be represented in application status.

Detailed registration assets/sources/devices are not required by this first slice.

#### Build and version identity

**SI01-REQ-010 — Single application build identity**  
A running SI-01 process shall expose one authoritative application build/version identity derived from the produced application artifact/build.

**SI01-REQ-011 — Consistent identity across interfaces**  
The build/version identity exposed through supported first-executable operator/application interfaces shall represent the same underlying build identity rather than interface-specific copies.

The public representation and required fields are defined by IF-03.

#### Status

**SI01-REQ-020 — Authoritative current status snapshot**  
SI-01 shall maintain an authoritative current application status model that is separate from log output.

**SI01-REQ-021 — Minimum first-executable status content**  
The first-executable status shall expose enough information to determine at least:

- application/build identity;
- application state;
- configured `TimingSystemInstance` identity/identities;
- the current minimal lifecycle state represented for those instances;
- explicit degraded/error information for first-executable configuration/startup failures that remain observable while the process can continue serving status.

The concrete IF-03 schema is defined by `40-01-IDD-application-control-status.md`.

**SI01-REQ-022 — Equivalent status semantics across first interfaces**  
Local console, remote-shell and IF-03 application-control/status representations shall be derived from the same application status semantics. A transport adapter shall not maintain a separate authoritative status model.

**SI01-REQ-023 — Status-change publication**  
SI-01 shall publish first-executable status-change information through IF-03 WebSocket/event delivery from the same authoritative status model used for status queries.

On connection/reconnection the client shall be able to recover a complete authoritative snapshot according to the IF-03 contract.

#### Application boundary and testability

**SI01-REQ-030 — Shared application behaviour**  
Transport-specific adapters shall invoke shared SI-01 application commands/queries rather than implementing independent copies of version/status behaviour.

**SI01-REQ-031 — Externally testable executable**  
The produced SI-01 application shall support ST-1 verification as a separate running process through its public application interface without direct test mutation of internal application/domain state.

**SI01-REQ-032 — Safe default network exposure**  
The first-executable IF-03 service shall default to local/loopback-only access. Non-loopback listening shall require explicit configuration until a later security/interface baseline defines production exposure and authentication policy.

**SI01-REQ-033 — Compatible first API evolution**  
SI-01 shall implement IF-03 `v1` such that compatible additions can be made without requiring clients to understand every newly added JSON member or event type; breaking interface semantics shall not silently redefine the existing `v1` contract.

### First-executable lifecycle interpretation

The first executable is not yet an operational timing implementation.

Therefore:

- application state may move through `STARTING`, `RUNNING`, `DEGRADED` and `STOPPING` according to IF-03;
- at least one configured minimal `TimingSystemInstance` is represented;
- that instance reports lifecycle `CLOSED` in this slice;
- operational open/close commands and resulting registration-stream events remain deferred to the later domain increment.

This prevents the first version/status executable from inventing partial operational semantics merely to make a demo look more complete.

### Explicitly deferred requirements

The following areas are intentionally not made concrete by this SRD slice:

- RFID power/read/filter/decryption behaviour;
- registration and source-sequence behaviour beyond any minimal topology placeholder needed for configuration;
- ready-team/start/penalty behaviour;
- CAN/keypad/Display V1;
- smart Display V2;
- persistence/backup of operational timing data;
- backoffice semantic/protocol behaviour;
- RabbitMQ-specific behaviour;
- target-image/update/rollback requirements beyond what the later Pi deployment increment needs;
- production authentication/authorisation and final security policy;
- browser-specific CORS/origin policy.

These areas remain governed by the working architecture/use cases until a later SIP/document-maturity gate requires formalisation.

### Traceability view

| Requirement | Current source | Interface/design allocation | Planned verification |
| --- | --- | --- | --- |
| SI01-REQ-001/002 | SIP framework/version-status increments | SI-01 composition/runtime | build/start/stop + ST-1 process control |
| SI01-REQ-003 | UC-001; SSAD runtime topology | SI-01 runtime registry/configuration | `VC-ST1-001` status inspection |
| SI01-REQ-010/011 | UC-008/009; SIP first executable | IF-01/02/03; shared query boundary | V2/V3 + `VC-ST1-001` |
| SI01-REQ-020/021/022 | UC-001/008/009; SSAD/SAD status model | Status service/model + IF-01/02/03 | V1/V2 + `VC-ST1-001` |
| SI01-REQ-023 | first executable live status need | IF-03 WebSocket/event adapter | V2/V3 + `VC-ST1-001` |
| SI01-REQ-030/031 | SAD testability; SVP ST-1 | shared application boundary | architecture/component checks + `VC-ST1-001` |
| SI01-REQ-032 | AP-1 controlled development exposure | IF03-REQ-002/009 | configuration/interface verification |
| SI01-REQ-033 | AP-1 interface evolution policy | IF03-REQ-010 | contract/component verification |

### AP-1 decisions resolved by this baseline

The following are now fixed for the first-executable contract:

- build/version identity fields are owned by IF-03: `application`, `version`, `revision`, `buildTime`, `apiVersion`;
- minimal application status/lifecycle semantics are defined in IF-03 and the lifecycle interpretation above;
- IF-03 HTTP resources are `/api/v1/version` and `/api/v1/status`;
- IF-03 WebSocket endpoint is `/api/v1/events`;
- WebSocket connect/reconnect starts with a complete status snapshot;
- first-executable change events carry complete current status rather than a patch/replay protocol;
- explicit JSON error responses and initial HTTP status mapping are defined in the IDD;
- authentication/authorisation is explicitly deferred for the first executable while default network binding remains loopback-only;
- verification-case identifiers use `VC-<profile>-<number>` for the first baseline;
- no separate remote-shell IDD is required by AP-1 because that adapter reuses shared version/status semantics and is not yet a stable software-to-software contract.

### Remaining implementation/toolchain choices

The following do **not** block this requirement baseline and belong in the implementation/toolchain increments:

- concrete Java HTTP/WebSocket library;
- concrete remote-shell implementation;
- JSON/configuration/logging libraries;
- Maven/JDK provisioning details;
- concrete code/package classes implementing the shared status model;
- exact mechanism used to cause the first deterministic status transition in `VC-ST1-001`.

A chosen implementation technology must satisfy this SRD and IF-03 rather than redefining them.


---

## Software System Architecture Document (SSAD)

**Source document:** [30-SSAD-software-system-architecture.md](./30-SSAD-software-system-architecture.md)

Status: working draft / non-authoritative

This document defines the architecture of the software system as a whole. Its purpose is to show the software items, their responsibilities and relationships, the system-owned interfaces, deployment relationships and constraints that apply across software-item boundaries.

It deliberately does **not** define the internal threading, messaging, persistence, package structure, device processing or implementation technology of SI-01. Those concerns belong in the applicable software-item SAD and, only where justified later, a focused detailed-design document.

Stable working domain facts and terminology are consolidated in `03-domain-baseline.md` and should not be silently reinterpreted here.

### Document role

The intended architecture hierarchy is:

```text
system/domain source knowledge
        |
        v
system requirements + system interfaces
        |
        v
30-SSAD  software-system architecture
        |
        +--> 31-01-SAD  SI-01 Timing Application Architecture
        +--> 31-02-SAD  SI-02 Desktop GUI Application Architecture
        +--> 31-03-SAD  SI-03 Web Operator Application Architecture
                    |
                    +--> focused SDD only when separate detailed design is useful
```

The SSAD answers questions such as:

- which software items exist and what does each own;
- how the software items communicate;
- which external systems/devices form system boundaries;
- where the software items execute;
- which architectural constraints must remain consistent across software items.

The software-item SADs answer how each software item is internally structured and implemented.

### Architecture drivers

The software-system architecture is driven by these system-level concerns:

- SI-01 remains the authoritative local timing/registration runtime;
- desktop and browser operator clients are separate software items and communicate with SI-01 over a system-defined network boundary;
- local timing/device operation must not depend on a connected desktop or browser client;
- external devices and backoffice systems are explicit system interfaces rather than hidden implementation dependencies;
- public framework/reference code and private/proprietary implementations must meet common supported contracts without private source leaking into public code;
- deployments must support constrained field hardware as well as development/test hosts;
- system interfaces and software-item ownership should remain stable even when internal implementation technology changes;
- IP-based system interfaces must not require a particular router or Wi-Fi topology merely to exercise the interface.

### Software-item register

The second-level number used in SRD/SAD/SDD filenames identifies the software item.

| Software item | Name | Current status | Primary responsibility | Expected deployment |
| --- | --- | --- | --- | --- |
| **SI-01** | Headless Timing Application | working architecture | Authoritative local timing/registration runtime, device integration, local state, status, persistence and backoffice synchronisation | Raspberry Pi Zero/Zero W; Linux/Windows development/test/runtime |
| **SI-02** | Desktop GUI Application | working architecture | Desktop operator client for status and control through the system interface | Operator workstation/laptop |
| **SI-03** | Web Operator Application | working architecture | Browser/iPad operator client using the SI-01 network interface | Browser/iPad on an available IP path to SI-01 |

Supporting framework modules, adapters, testkits/reference projects and private implementation repositories are engineering components, not automatically separate product software items.

### System context

```text
                         Operator
                       /          \
                      v            v
             SI-02 Desktop GUI   SI-03 Web/iPad
                      \            /
                       \          /
                        v        v
                    SI-01 Timing Application
                    /      |       \
                   v       v        v
             field devices local   Backoffice
             RFID / CAN     state   integration
             / displays
```

The desktop GUI and browser clients may disconnect without transferring authoritative timing-domain ownership away from SI-01.

![Software items and principal system interfaces](../assets/architecture/software-item-system-overview.svg)

### Software-item relationships

#### SI-01 ↔ SI-02

SI-02 is an IP network client of SI-01. It presents operator status and control but does not access SI-01 memory, files or Java objects directly. The logical IF-03 relationship does not require a Wi-Fi router: a direct, same-host, point-to-point or normal LAN/Wi-Fi IP path may carry the interface.

#### SI-01 ↔ SI-03

SI-03 is a browser-based IP client. SI-01 exposes the system-defined control/status/event interface required by the browser application. As with SI-02, the interface is defined between endpoints rather than through a particular router topology.

#### SI-01 ↔ backoffice

SI-01 exchanges race/reference data, registration information, status and reconciliation information with the backoffice through a system-owned semantic interface. The concrete transport, codec and network route are SI-01/integration design concerns unless they change the external system contract.

#### SI-01 ↔ field devices

RFID, CAN, keypad and display equipment are external device boundaries of SI-01. Device semantics belong in system/device interfaces; internal adapter lifecycle, threads and processing pipelines belong in the SI-01 architecture/design.

### System interface catalogue

This catalogue identifies system-owned boundaries before all individual IDDs are mature. IDs are working identifiers but should remain stable once promoted.

| Interface | Parties | Current transport/direction | Purpose | Planned documentation |
| --- | --- | --- | --- | --- |
| **IF-01 Local Operator Console** | Operator ↔ SI-01 | local console/shell | Local version, status and operator commands | operator/application interface material |
| **IF-02 Remote Shell** | Operator/service tool ↔ SI-01 | remote terminal/shell, technology TBD | Remote status and commands using shared semantics | IDD candidate |
| **IF-03 Application Control & Status** | SI-02/SI-03 ↔ SI-01 | HTTP/JSON + WebSocket over an available IP path | Network command/query/status/event boundary | `40-01-IDD-application-control-status.md` candidate |
| **IF-04 Desktop Operator HMI** | Operator ↔ SI-02 | desktop GUI | Desktop screens, controls and operator feedback | GUI/HMI IDD candidate |
| **IF-05 Web Operator HMI** | Operator ↔ SI-03 | browser/iPad | Browser screens, controls and feedback | Web HMI IDD candidate |
| **IF-06 Backoffice Integration** | SI-01 ↔ Backoffice | transport implementation below semantic boundary | Race/reference-data sync, registrations, reconciliation/status | system IDD; proprietary wire details may remain private |
| **IF-07 RFID Integration** | SI-01 ↔ RFID subsystem | hardware/protocol adapter | RFID observations, lifecycle and health | device/semantic contract candidate |
| **IF-08 CAN Device Integration** | SI-01 ↔ CAN bus/devices | CAN | Discovery, Display V1 and keypad interaction | system/device IDD candidate |
| **IF-09 Smart Display V2** | SI-01 ↔ Display V2 | IP path; direct or LAN/Wi-Fi deployment | Synchronised display/domain data | system IDD candidate |
| **IF-10 Test Control** | test/reference tooling ↔ public stubs | development-only | Inject device/network/fault behaviour through supported boundaries | SDE/SVP/test design |

System-level IDDs own interface semantics. Software-item SRDs and SADs reference those obligations rather than redefining the wire/system contract independently.

### Cross-software-item interaction principles

The following rules apply across software-item boundaries:

- operator behaviour exposed through console, desktop and browser should converge on shared system semantics rather than implementing different business rules per client;
- network clients observe and control SI-01 but do not become the authority for timing state;
- loss of SI-02 or SI-03 must not by itself stop local SI-01 operation;
- IF-03 and IF-09 are endpoint-to-endpoint logical interfaces and must not make a physical Wi-Fi router an architectural prerequisite;
- development and automated integration verification may use loopback, same-host or direct IP connectivity while exercising the same system interface semantics;
- interface versioning and compatibility must be explicit once interfaces become authoritative;
- transport-specific implementation detail should not leak into the semantic system interface unless that transport is itself part of the external contract;
- system status must distinguish local IP availability, configured network-infrastructure state, external reachability and backoffice/session health where those distinctions affect operator decisions.

### System deployment view

The principal device/interface relationships are a **software-system concern** because they show where SI-01, the operator software items, external field devices and backoffice meet. The lines in this view are logical system-interface relationships: they deliberately do not force traffic through a router node.

![System device and logical interface topology](../assets/architecture/system-device-network-topology.svg)

Representative relationships are:

```text
Field host
  SI-01 Headless Timing Application
    |
    +-- IF-07 --> RFID subsystem
    +-- IF-08 --> CAN devices / keypad / Display V1
    +-- local persistent state

SI-02 Desktop GUI
  +-- IF-03 over available IP path --> SI-01

SI-03 Web Operator Application
  +-- IF-03 over available IP path --> SI-01

Smart Display V2
  +-- IF-09 over available IP path --> SI-01

Backoffice
  +-- IF-06 over configured external path --> SI-01
```

An available IP path may be direct/point-to-point, same-host or loopback during development/test, or may run over normal LAN/Wi-Fi infrastructure in a field deployment. A Wi-Fi router/access point is therefore **optional deployment infrastructure**, not part of the semantic definition of IF-03 or IF-09.

#### Connectivity and reachability state

Network health is not one boolean and should not be modeled as one mandatory chain. The system needs to expose separately observable states because they answer different operational questions.

![Network connectivity status — separate observations](../assets/architecture/system-connectivity-status.svg)

At minimum distinguish:

- **local IP connectivity** — SI-01 network interface/link and ability to communicate with local peers;
- **configured router/AP connectivity** — whether the deployment is connected/associated with the configured local router or access point; this may legitimately be **N/A** for direct/development/test compositions;
- **external network reachability** — whether connectivity beyond the local network is available;
- **backoffice connectivity** — whether the configured backoffice endpoint/transport/session is healthy.

These states must not be conflated. For example, local timing and direct local clients may remain fully operational while the router, external uplink or backoffice is unavailable. Conversely, a configured field deployment may need to report that it has lost its expected router/AP even before external reachability is tested.

The exact process/thread topology, internal runtime cardinality, queueing model, service composition, connectivity probing mechanism and adapter implementation are intentionally outside this SSAD.

### Cross-system architectural constraints

#### Authority and disconnected operation

SI-01 owns authoritative local operational state. GUI/browser availability and temporary loss of external connectivity must not silently transfer that authority or fabricate healthy synchronisation.

#### Public/private implementation boundary

System contracts used by public framework/reference code must allow private production implementations to plug in without public code depending on private source or proprietary identities.

#### Interface-first separation

Software-item interaction is defined in terms of system-owned semantics. Internal implementation choices such as RabbitMQ libraries, HTTP servers, logging frameworks, executors or file formats are owned by the relevant software-item architecture unless the choice becomes part of an external contract.

#### Deployment portability

The architecture must support constrained field deployment and normal Linux/Windows development/test environments without changing the software-item boundaries. Automated integration verification must be able to exercise network interfaces without provisioning a physical Wi-Fi router unless the test explicitly targets router/AP behaviour.

### Relationship to software-item architecture

The SI-01 SAD owns, among other things:

- layered application responsibilities;
- `TimingSystemInstance`, registration asset/source and other internal runtime abstractions;
- threading/concurrency and internal messaging;
- status architecture and lifecycle handling;
- persistence and restore strategy;
- logging/configuration/composition choices;
- Java/framework/library decisions;
- RFID/CAN/display adapter architecture behind the system device interfaces;
- backoffice transport implementation behind IF-06;
- resource-budget implications of those choices.

The SI-02 and SI-03 SADs similarly own their internal architectures while conforming to the system interfaces defined here and in applicable IDDs.

### Architecture review model

The project uses the 4+1 architectural view model as a review aid, not as a requirement for five documents. At system level, the SSAD primarily provides system context and deployment/relationship views. The software-item SADs provide the coherent logical, process, development and deployment views of each item and reference selected use cases as scenarios.

Reference: `reference/README.md`.

### Open system-architecture questions

- final system interface/IDD breakdown and ownership;
- authentication, authorisation and secure transport requirements across software-item boundaries;
- compatibility/versioning policy for IF-03 and IF-06;
- final deployment ownership for serving SI-03 assets;
- which device semantics require system-level IDDs versus software-item-only design;
- required behaviour when local IP, configured router/AP, external network or backoffice connectivity is unavailable;
- final system-level availability/recovery requirements.


---

## Timing Application Architecture (SAD)

**Source document:** [31-01-SAD-timing-application-architecture.md](./31-01-SAD-timing-application-architecture.md)

Status: working draft / non-authoritative

Software item: **SI-01 — Headless Timing Application**

This Software Architecture Document describes the architecture of software item 01: the headless Java timing application. It sits below `30-SSAD-software-system-architecture.md` and is the primary technical design document for SI-01 at the current project stage.

The SAD is expected to contain concrete architecture decisions such as threading, concurrency, internal messaging, framework/library choices, logging, configuration, persistence, composition and integration structure. A separate SDD is created only when a topic genuinely needs implementation detail that would make this SAD harder to use.

### Document relationship

```text
30-SSAD  Software-system architecture
    |
    v
31-01-SAD  SI-01 Timing Application Architecture
    |
    +-- focused SDD only when separate detailed design is useful
    +-- system IDDs for externally owned interface semantics
    +-- SVP/test material for verification strategy and evidence
```

At this stage the intended bias is **towards one coherent SAD rather than early SDD decomposition**.

### Architecture drivers

SI-01 architecture is driven by these concerns:

- run on the original Raspberry Pi Zero / Zero W as a mandatory constrained target;
- remain usable on Linux/Windows development and test hosts;
- keep authoritative timing/domain state local to SI-01;
- support one or more logical timing-system instances without state leakage;
- preserve deterministic ordering of state-changing work;
- isolate external I/O concurrency from application/domain state mutation;
- preserve unambiguous time semantics across local time zones, daylight-saving transitions and wall-clock corrections;
- remain testable without production RFID, CAN, backoffice or proprietary implementations;
- expose one coherent command/query/status/event model to local and network presentation adapters;
- support local persistence/recovery and disconnected operation;
- keep public framework/reference code independent of private production source;
- avoid framework complexity that is not justified on the constrained target.

### +1 scenarios used to validate the architecture

The existing use cases in `04-UC-system-use-cases.md` are the scenario source. The SAD should not create a second competing use-case catalogue.

Representative architecture-validation scenarios include:

1. start SI-01, load configuration, expose version/status and shut down cleanly;
2. accept an operator command through local or network presentation and route it to the correct logical timing-system instance;
3. accept a device observation from an external callback without allowing that callback thread to mutate authoritative application state directly;
4. persist accepted operational state and recover it after restart;
5. continue local operation while a GUI/browser or backoffice connection is unavailable;
6. host several timing-system instances in a development/simulation composition without state leakage;
7. substitute public stubs for production devices/transports while exercising the same application/domain paths;
8. capture and process observations correctly when local civil time crosses a daylight-saving transition or the operating-system wall clock is corrected forwards/backwards.

These scenarios are used to check the logical, process, development and deployment views below.

### Logical view

#### Layered application architecture

The primary logical view is a responsibility/layer view. It describes semantic ownership and dependency direction; it does **not** prescribe one Maven artifact per layer.

![SI-01 layered architecture](../assets/architecture/layered-architecture.svg)

The source for this view is `docs/_diagrams/layered-architecture.yaml`.

#### Presentation

Presentation exposes SI-01 behaviour and current state to external clients through concerns such as:

```text
HTTP / JSON
WebSocket
local console
remote shell
protocol/DTO mapping for those interfaces
```

Presentation translates external requests into application commands/queries and application status/events into external representations. It does not own running application state.

#### Application

The application responsibility owns running mutable application state and coordinates use cases. Representative concerns include:

```text
TimingSystemInstance state
registration/source ledgers and current runtime state
commands / queries / workflows
status management and aggregation
immutable status snapshots
single-system or multi-system application coordination
```

The application responsibility invokes domain services and coordinates persistence/integration ports without moving transport/protocol details into domain behaviour.

#### Domain

The domain responsibility owns reusable timing rules, services, entities and value semantics. Representative services currently include:

```text
RegistrationService
StartTimeService
ReadyTeamService
RaceDataService
```

`RaceDataService` is specifically the domain capability for race/event data in the sporting-event sense: participant/team data, tag-reference lookup and reserve-tag mapping semantics. It is deliberately not named `EventDataService`, because software events are a separate architecture concept. Start-time state remains owned by `StartTimeService`, ready-team state by `ReadyTeamService`, and registrations by `RegistrationService`.

Representative concepts include timing-system identity/value concepts, `RegistrationAsset`, `RegistrationSource`, registration observations/results, `TimingTimestamp`, start-time values, ready-team values, tag-class values and race/participant/tag-reference values.

Decoded RFID identity must preserve whether a tag is normal, reserve or test-class until the applicable domain/use-case policy has been applied. A test tag is therefore not silently normalised into a normal participant identity at an adapter boundary.

Product/deployment-specific policy does not automatically belong in the reusable domain model.

#### Core runtime support

Core runtime support provides reusable execution mechanics that let application/domain behaviour run predictably, for example:

```text
serialized execution
lifecycle mechanics
routing primitives
scheduling
command/event dispatch mechanics
```

Core runtime support is not a second owner of domain behaviour or application state.

#### Infrastructure / integration

Integration implementations connect SI-01 to external systems/devices and persistence mechanisms, including:

```text
persistence / file backup and restore
backoffice socket / RabbitMQ integration
RFID integration
CAN integration
display integration
```

#### Platform

Platform abstractions isolate execution-environment and low-level facilities such as clock/time source, filesystem/path primitives, executor/thread primitives, process/runtime information and network/OS facilities.

Platform is not a catch-all location for HTTP, RabbitMQ or device/domain protocols.

#### Cross-cutting concerns

Logging, configuration, diagnostics, metrics where useful and build/version identity cross several responsibilities without becoming owners of domain/application state.

### Principal runtime abstractions

A `TimingSystemInstance` is the primary logical isolation and ordering boundary inside SI-01. One application process may host one or more independently addressed instances.

```text
TimingApplicationRuntime
    |
    +-- TimingSystemInstance system-01
    |      +-- 1..X RegistrationAsset
    |              +-- 1..X antenna/device bindings
    |              +-- 1..X RegistrationSource
    |
    +-- TimingSystemInstance system-02
           +-- ...
```

A `RegistrationAsset` represents a configured physical/logical equipment unit. A `RegistrationSource` represents one ordered registration stream with a stable external/domain source identity, monotonic source sequence and source-specific registration state.

Source routing occurs after asset/device resolution; an antenna identity is therefore not assumed to be identical to one registration-source identity.

Runtime-wide infrastructure may be shared where that does not leak mutable timing-system state. Candidates include backing executors, logging infrastructure, HTTP server infrastructure, backoffice connection infrastructure, configuration loading and network monitoring.

![SI-01 configurable runtime topology](../assets/architecture/runtime-registration-topology.svg)

Stable domain facts behind this topology are maintained in `03-domain-baseline.md`; this SAD owns their software-architecture composition and execution implications.

### Command, query and event model

All presentation transports should converge on one shared application model.

```text
local console -------+
remote shell --------+
HTTP/JSON -----------+--> typed command/query boundary --> application runtime
WebSocket <-----------+<-- typed status/events -------------------+
```

Working rules:

- commands request state changes;
- queries read current state/snapshots without becoming alternate owners of state;
- events report facts/results that have occurred;
- external protocol DTOs are mapped at the presentation/integration boundary rather than used as the internal domain model;
- messages crossing thread/process boundaries should be immutable where practical;
- a generic event-bus framework is **not** assumed to be necessary.

The initial architecture uses explicit typed routing because the flow is easier to reason about, test and keep lightweight on the Pi Zero. A third-party messaging/event framework should only be introduced when it solves a demonstrated problem better than explicit routing and JDK concurrency primitives.

### Process view: threading and concurrency

External libraries may create callbacks/threads for HTTP/WebSocket, shell, RFID, CAN, RabbitMQ, timers and network sessions. Those threads must not directly mutate authoritative timing-system state.

The intended processing path is:

1. capture externally meaningful `TimingTimestamp` values immediately where timing matters;
2. attach stable instance/device/source context;
3. convert input into an immutable command/event;
4. route it to the addressed `TimingSystemInstance`;
5. serialize state-changing handling for that instance;
6. keep blocking hardware/network/file operations outside the serialized state path;
7. return relevant completion/failure into the state path as commands/events when required.

```text
adapter callbacks / operator endpoints / timers
                    |
                    v
        immutable ingress message
                    |
                    v
         TimingSystemDispatcher
             /              \
            v                v
 SerialExecutor A      SerialExecutor B
    system-01             system-02
            \                /
             \              /
              v            v
          shared backing ExecutorService
```

![SI-01 runtime dispatch process](../assets/architecture/runtime-dispatch-process.svg)

The source for this process view is `docs/_diagrams/runtime-dispatch-process.yaml`. Boxes show state/execution ownership and arrows show the principal dispatch, execution and published-snapshot relationships rather than a complete call graph.

#### Per-instance serialized state lane

Every `TimingSystemInstance` owns one logical serialized state lane implemented by a small project-owned `SerialExecutor` abstraction.

Required semantics:

- messages accepted for one instance execute in FIFO enqueue order;
- at most one state-changing handler for an instance is active at a time;
- the serial executor does **not** own a dedicated operating-system thread;
- each serial executor delegates runnable work to a shared backing `ExecutorService`;
- different timing-system instances may execute concurrently when the backing executor has more than one worker;
- increasing backing parallelism must never allow two state handlers of the same instance to overlap.

The design follows the standard `Executor` composition pattern rather than introducing an actor/reactive framework. The constrained field profile should start with one backing state worker; larger development/integration compositions may configure more workers after measurement. This allows the same logical model to run conservatively on a Pi Zero and with parallel independent instances on a desktop test host.

A direct/synchronous executor remains a supported test composition so handlers can be exercised deterministically without real threads.

#### Dispatcher and ingress ownership

A `TimingSystemDispatcher` is the application/runtime routing boundary from externally concurrent producers to per-instance state lanes.

The dispatcher resolves a stable timing-system identity to the applicable serial executor and submits the typed message. It does not implement domain rules itself.

Ingress rules:

- adapter callbacks do the minimum synchronous work needed to capture timestamp/context and validate framing;
- callback threads must not call mutable domain/application state directly;
- device/source ordering guarantees provided by an adapter must be preserved before dispatch;
- the dispatcher does not sort messages by wall-clock timestamp;
- when multiple producer threads concurrently submit to the same instance, the state lane processes the order in which submissions are accepted into that lane;
- source sequence numbers are assigned according to domain/source commit semantics, not inferred from callback thread identity or timestamp ordering.

#### Snapshot reads and consistency-sensitive queries

Not every read needs to occupy the serialized state lane.

The application should publish immutable current-state/status snapshots that can be read safely by presentation/status consumers without mutating the instance. A lightweight atomic publication mechanism may be used for the current snapshot.

Queries that require a state-consistent calculation against mutable authoritative state enter the same serialized lane as state-changing work. The API must make the difference between a potentially slightly stale published snapshot and a consistency-sensitive query explicit rather than hiding it behind one generic getter.

#### Blocking I/O and asynchronous completion

Blocking file, network and device operations must not run while holding the per-instance state lane.

The preferred pattern is:

```text
serialized state handler
      |
      +--> request adapter / I/O work
                |
                v
       I/O executor / external callback
                |
                v
       typed completion/failure event
                |
                +--> dispatcher --> same instance state lane
```

If a use case requires durable I/O completion before a domain transition is considered committed, the application state represents that pending/commit boundary explicitly and finishes the transition when the completion message returns. The exact persistence commit protocol remains a persistence-design decision; blocking the state lane on file/network latency is not the default mechanism.

Scheduled timers follow the same ownership rule: scheduler callbacks submit typed messages to the instance rather than mutating instance state directly.

#### Queue bounds, overload and failure containment

An unbounded ingress queue is not an acceptable field default on the constrained target.

Working rules:

- each instance state lane has a bounded/configurable pending-work capacity;
- queue saturation must never silently discard a command, observation or completion;
- rejected/overloaded submissions produce explicit diagnostics/status/counters and a visible failure path to the calling adapter/interface;
- an adapter may apply protocol-specific backpressure or its own bounded buffering where the external protocol supports it, but that policy remains outside the generic dispatcher;
- queue depth/high-water information should be observable for diagnostics;
- one handler exception must not permanently stall the serial executor; handler failure is contained/reported and scheduling of subsequent accepted work continues unless the application deliberately transitions the instance to a failed/stopped state.

Exact capacities and the final overload reaction for timing-critical device ingress require workload evidence. They are configuration/verification decisions, not permission to use an unbounded queue meanwhile.

#### Lifecycle and shutdown

Normal shutdown should preserve executor ownership explicitly:

1. stop accepting new external/operator ingress;
2. stop or quiesce device/network adapters;
3. allow accepted instance-lane work to drain within a configured timeout;
4. complete required persistence/outbox shutdown handling;
5. shut down scheduler/I/O executors and the shared state executor;
6. expose failure if the bounded graceful-shutdown window cannot complete.

#### Concurrency technology baseline

The selected baseline is:

- JDK `java.util.concurrent` (`Executor`, `ExecutorService`, `ThreadPoolExecutor`, `ScheduledExecutorService`, futures where justified);
- a small explicit project-owned `SerialExecutor` abstraction per timing-system instance;
- one shared configurable state backing executor;
- separate I/O/scheduler execution where blocking or delayed work requires it;
- no Akka/reactive-stream/event-bus framework in the initial architecture;
- controllable/direct executors in unit tests.

Do not use convenience executor factories that hide unbounded queues where a bounded field queue is required; construct/configure the relevant executor explicitly.

### Time and clock architecture

Time is an explicit architecture concern rather than an incidental use of `Date`, `Calendar`, `LocalDateTime`, Java/SQL timestamp classes or raw millisecond values throughout the codebase.

#### `TimingTimestamp` value

SI-01 uses one dedicated immutable application/domain class named `TimingTimestamp` for externally meaningful absolute event times such as observations, registrations, start times and persisted/synchronised event timestamps.

Working semantics:

- `TimingTimestamp` represents an absolute point on a UTC-based time line;
- it does not contain an implicit local time zone or daylight-saving state;
- conversion to/from local civil time happens at explicit presentation/configuration/integration boundaries;
- its precision and external serialisation are explicit rather than inherited accidentally from a Java API or wire codec;
- domain/application APIs pass `TimingTimestamp` rather than arbitrary `long`, `Date`, generic Java timestamp classes or local-date/time values where an absolute event time is intended.

The dedicated class may internally delegate to a suitable Java primitive such as `Instant`, but its public semantic contract remains project-owned. Protocol-specific formatting/parsing, time-only strings and deployment-specific zone conversion belong in boundary adapters/codecs rather than in `TimingTimestamp` itself. This keeps the domain type independent of one protocol, storage format or deployment time zone.

#### Time sources

Code that needs the current absolute time receives it through an injectable time-source/clock abstraction. Production composition can use the operating-system wall clock; deterministic tests can supply a controlled clock that can be advanced or stepped explicitly.

Elapsed durations, retry intervals, filtering windows, scheduling delays and timeout measurements should use a **monotonic time source** where their semantics are duration-based. On Java 8 this can be backed by `System.nanoTime()` behind a small platform abstraction. A monotonic mark is process-local and is not a persisted event timestamp.

The distinction is therefore:

```text
TimingTimestamp / wall-clock source
  absolute event time
  persistence / synchronisation / external semantics

monotonic time source
  elapsed duration
  timeout / retry / filtering windows
  process-local only

RegistrationSource SequenceNumber
  stable source ordering / gap detection
```

A source sequence is not derived from a timestamp. Two registrations may have equal timestamps, and a wall-clock correction may even make a later observation carry an earlier absolute timestamp; source ordering must remain recoverable from source sequence semantics.

#### Architecture risk — wall-clock discontinuity and local-time ambiguity

This is an explicit architecture risk because timing software can produce plausible but incorrect results when local civil time and elapsed time are conflated.

| Risk | Possible consequence | Architectural mitigation / open work |
| --- | --- | --- |
| daylight-saving transition repeats or skips local civil times | ambiguous/non-existent local timestamps and wrong ordering if local time is persisted as authority | persist/use absolute `TimingTimestamp`; perform local-zone conversion only at explicit boundaries; add DST transition tests |
| NTP, manual correction or platform synchronisation steps wall clock backwards/forwards | negative/large elapsed differences; a later observation can have an earlier wall-clock timestamp | use monotonic time for durations; source sequence for ordering; expose/inject wall clock; define correction/health policy |
| clock offset/drift differs between SI-01 and external systems | incorrect elapsed/race-time calculations or reconciliation disagreement | define clock synchronisation/offset acceptance requirements and verification before timing accuracy is accepted |
| restart loses monotonic origin | process-local duration marks cannot be compared across restart | never persist monotonic marks as event timestamps; restore from absolute `TimingTimestamp` plus domain/source state |

Daylight-saving time by itself does **not** change UTC/absolute time; the ambiguity appears when a local civil time is treated as if it were an absolute timestamp. Conversely, using an absolute `TimingTimestamp` does not make the operating-system clock monotonic: a wall-clock correction can still cause newly captured absolute timestamps to move backwards.

Before physical timing behaviour is accepted, the project must decide how an active timing system reacts to a material clock correction: whether it is merely diagnosed, blocks/marks the system degraded, records an audit event, or uses an explicit correction/offset mechanism. That policy needs requirements and verification evidence rather than being hidden inside the `TimingTimestamp` class.

### Internal messaging direction

Internal messaging exists at asynchronous/ownership boundaries; it is **not** a requirement to turn ordinary in-lane Java calls into messages.

Working semantic categories are:

```text
TimingCommand
  request an application/domain state change

TimingEvent
  report an observation, fact, adapter completion or failure

TimingQuery<R>
  request a consistency-sensitive result from authoritative instance state
```

The exact Java interface/generic signatures remain implementation detail, but the semantic distinction should stay visible.

Working rules:

- presentation/device/integration boundaries convert external input into typed immutable application-facing messages;
- `TimingSystemDispatcher` performs explicit instance routing rather than reflection/topic-based event-bus discovery;
- messages crossing the state-lane boundary carry the stable instance/device/source/correlation context they need explicitly;
- once executing inside the instance state lane, application/domain services normally call one another directly rather than publishing another message for every method call;
- adapter/I/O completion returns as a typed event because it crosses back into the state-ownership boundary;
- published status/domain notifications may fan out to presentation consumers, but those consumers cannot use the notification channel to mutate authoritative state behind the command boundary;
- RabbitMQ is an external integration transport and is not reused as an in-process message bus.

A command/query endpoint may expose a Java-8 `CompletionStage`/future-style result where asynchronous completion is useful, but the exact API shape should be selected with the first real consumers rather than building a generic messaging framework up front.

### Status and diagnostics architecture

Status is a first-class current-state model and is distinct from logging.

Status should allow presentation and diagnostics to observe application, timing-system and subsystem health without parsing log text. Representative areas include:

- application version / uptime / overall health;
- timing-system lifecycle;
- registration asset/source state;
- state-lane queue depth/high-water/overload health;
- RFID power/startup/protocol/heartbeat;
- CAN/device availability;
- persistence/backup state;
- race-data freshness;
- local clock/time-source health where relevant to timing validity;
- network/backoffice connectivity;
- inbound/outbound synchronisation state.

Status snapshots exposed to consumers should be immutable from the consumer perspective.

Logging records diagnostic/history information; status represents current operational state. One must not be used as a substitute for the other.

### Logging architecture

Logging is a SAD-level technology decision because it affects almost every component, operational diagnostics, footprint and public/private integration.

The baseline logging architecture is:

```text
framework/application code
        |
        v
      SLF4J API
        |
        v
provider selected by executable composition
        |
        +-- initial default: slf4j-jdk14
                         |
                         v
                  java.util.logging
```

Working decisions:

- reusable framework code logs through the SLF4J API;
- `event-timing-framework.jar` depends on `slf4j-api` only and must not impose a provider/backend on consumers;
- the executable composition selects exactly one provider;
- the initial Java-8/Pi-Zero application composition uses `slf4j-jdk14`, delegating to the JDK `java.util.logging` backend;
- Logback/reload4j or another backend is not part of the baseline unless later operational requirements justify it;
- another executable/private consumer may choose a different compatible provider without changing framework/domain source;
- log calls use parameterised messages where practical so disabled diagnostic logging does not require avoidable string construction;
- high-frequency observations should not automatically produce one INFO record per observation; detailed per-observation diagnostics belong at controlled diagnostic levels while current health/counters remain part of status/metrics;
- stable timing-system/source/device/correlation identifiers should be represented consistently in diagnostic messages/context, without making logging context the owner of application state;
- logging is not the mechanism for application status, registration history, audit/domain records or backoffice synchronisation state.

The exact field handlers, console/file split, rotation, retention and default level policy remain deployment/runtime configuration choices. They must be measured on the Pi Zero before being treated as accepted field defaults.

SLF4J 2.0.x is compatible with the Java-8 baseline; the implementation repository should pin the API/provider patch version together through Maven dependency management.

### Configuration and composition architecture

Configuration describes deployment/composition rather than domain behaviour hard-coded in source.

Representative structure:

```text
application
  timing-system instances
    location/context
    registration assets
      antenna/device bindings
      registration sources
  presentation endpoints
  persistence locations
  backoffice transport selection
  platform/device adapter settings
```

Working direction:

- load external configuration into typed validated configuration objects;
- keep secrets/credentials out of committed configuration;
- perform explicit application composition at startup;
- prefer straightforward manual composition initially rather than adding a dependency-injection framework without a demonstrated need;
- keep configuration file syntax/library selection open until the required model is sufficiently stable.

### Data and persistence architecture

The initial architecture uses typed in-memory authoritative state/repositories with simple file-based persistence/restore rather than requiring an embedded database.

Keep these concepts distinct:

1. ingress/ordering — concurrency ownership;
2. registration ledger/source sequence — traceable domain/operational history;
3. ready-team journal/current projection — separate operational capability;
4. race/reference data — locally available participant/team/tag-reference input received from external sources;
5. absolute event time — project-owned `TimingTimestamp` semantics independent of local display time;
6. local backup/restore — restart/power-loss recovery;
7. backoffice outbox/synchronisation — pending external delivery/reconciliation.

Registration identity remains source-scoped; the current stable conceptual key is `(RegistrationSystemId, SequenceNumber)`.

Persistence durability semantics, file format, atomic-write strategy and corruption/recovery rules remain open decisions and may justify a focused data/persistence SDD only when implementation reaches that complexity.

### Integration architecture

The **external device and network topology is owned by the SSAD**, because RFID/CAN devices, local LAN clients, displays and backoffice are system-level deployment/interface relationships. This SAD starts at the SI-01 boundary and explains how SI-01 realises those system interfaces internally through ports, adapters, callbacks, status handling and transport implementations.

#### Backoffice

RabbitMQ is not the application-level backoffice API. SI-01 depends on semantic source-aware ports and local synchronisation/outbox behaviour.

```text
application/domain
    semantic backoffice ports
            |
            +--> stub/in-memory adapter
            +--> lightweight socket test adapter
            +--> RabbitMQ adapter
            +--> private/proprietary codec/mapping where required
```

The socket implementation exists to test a real process/network boundary without requiring the production broker. RabbitMQ is the intended production-shaped broker transport. Exact connection/channel topology, routing keys and retry mechanics are adapter-level decisions and should be detailed when that implementation is active.

#### RFID

RFID integration is an adapter boundary. Raw callbacks/protocol data do not directly mutate application state. The adapter is responsible for protocol/device interaction and turns accepted observations/health changes into typed application-facing messages.

Decoding must retain public semantic tag classification (normal/reserve/test) even if proprietary prefix/encryption details stay in a private codec. Reserve resolution and test-tag policy are domain/use-case concerns rather than reasons for the adapter to silently rewrite every decoded tag to one normal identity.

Power/startup/recovery lifecycle and filtering semantics are architectural concerns where they affect application behaviour; exact protocol commands, crypto/proprietary codecs and retry sequences remain implementation/private detail.

#### CAN, keypad and displays

CAN/device integrations follow the same rule: device/protocol callbacks enter SI-01 through integration boundaries and application-facing messages. Display state remains owned by SI-01 rather than by the display device.

Display V1 is a CAN-based integration. Display V2 is a network client that discovers the SI-01 service on the local network and connects for synchronised display data. Exact protocol/session details remain deferred until implementation requires them.

#### Connectivity

Status must distinguish at least local network reachability from external/backoffice session health where those distinctions affect operator decisions. Temporary external connectivity loss must not silently invalidate otherwise available local operation.

### Development view

#### Maven artifact boundary

The current implementation baseline deliberately starts with one reusable framework library and one executable application:

```text
event-timing-parent
framework/ -> event-timing-framework.jar
app/       -> event-timing-app.jar
```

Architecture layers/packages are **not automatically Maven artifacts**. A new artifact is justified by an actual consumer, reuse, dependency, lifecycle, deployment, public/private or release boundary.

#### Package direction

Likely package responsibilities may evolve toward areas such as:

```text
application
domain
core
presentation
integration
platform
```

Do not rename/split packages simply to make the source tree mirror the architecture picture. Package structure should become more explicit as real classes make ownership and dependency rules enforceable.

#### Public/private extension model

Private repositories may provide production RFID control, encrypted/proprietary protocol implementations, deployment mappings and production backoffice codecs. Public framework code defines supported contracts and must compile/test without those private implementations.

### Technology decision register

This table intentionally lives in the SAD because these choices shape the whole SI-01 architecture.

| Concern | Current direction | Status / next evidence |
| --- | --- | --- |
| Java baseline | Java SE 8 initially because original Pi Zero/ARMv6 is mandatory | accepted baseline; pin/verify reference runtime |
| Build | Maven | accepted |
| Concurrency | one project-owned `SerialExecutor` per instance over shared configurable JDK executors; constrained profile starts with one state worker | architecture baseline selected; verify queue capacities, overload behaviour and worker-count evidence |
| Internal messaging | typed immutable command/event/query objects only at async/ownership boundaries + explicit `TimingSystemDispatcher`; direct calls inside state lane | architecture baseline selected; refine first consumer API signatures during implementation |
| Time model | dedicated project-owned immutable `TimingTimestamp` + injectable absolute clock + separate monotonic duration source | working direction; define precision/serialisation, sync and clock-correction policy |
| Dependency injection | explicit/manual composition initially | working direction; add framework only if complexity justifies it |
| Logging | SLF4J API in reusable framework; initial executable provider `slf4j-jdk14` / `java.util.logging` | architecture baseline selected; pin compatible 2.0.x API/provider and measure field logging on Pi Zero |
| Configuration | external typed/validated configuration | file format/library still open |
| Persistence | typed in-memory state + simple file persistence/restore | durability/file mechanics still open |
| HTTP/WebSocket | embedded Java-8-compatible technology | selection still open |
| Remote shell | shared command semantics, transport technology open | selection still open |
| Backoffice | semantic ports + socket test adapter + RabbitMQ production-shaped adapter | architecture direction established; implementation detail deferred |
| Test doubles | public controllable stubs through the same supported ports | established direction |

A technology should not be selected solely because it is common in unconstrained server applications. Pi Zero compatibility, memory/thread footprint, testability and operational simplicity are architecture criteria.

### Physical/deployment view

Representative SI-01 deployments are:

```text
Production field host
  Raspberry Pi Zero / Zero W
    one SI-01 process
      one or more configured TimingSystemInstance objects
      local devices + local files
      optional network/backoffice connectivity

Development/test host
  Linux or Windows
    same SI-01 framework/application behaviour
    real or stub adapters
    may host larger multi-instance simulation topology
```

The architecture should not require a different domain implementation for simulation. Different compositions select different adapters/topologies around the same application/domain behaviour. The system-level placement of SI-01 relative to devices, operator clients, LAN/Wi-Fi and backoffice is defined in the SSAD rather than duplicated here.

### Testability and failure/recovery architecture

Testability is an architecture property. Application/domain code should where practical:

- avoid uncontrolled threads and global mutable state;
- receive absolute time through an injectable abstraction;
- receive duration/timeout measurements through a controllable monotonic abstraction where needed;
- include tests that step the wall clock forwards/backwards and cross representative DST/local-time transitions;
- exercise `SerialExecutor` ordering, same-instance non-overlap, cross-instance parallelism and bounded-queue rejection deterministically;
- depend on semantic ports rather than concrete device/network libraries;
- keep protocol parsing in adapters;
- use deterministic handlers that can run synchronously in unit tests;
- expose observable status for degraded/failure conditions;
- avoid `Thread.sleep()` as a domain timing mechanism.

Fault handling should preserve local authority, traceability and explicit status. Exact retry counts, timeouts and durability guarantees belong to requirements or focused implementation design when evidence exists.

Detailed verification strategy belongs in `50-SVP-software-verification-plan.md`.

### When a separate SDD is justified

A separate SDD should be introduced or retained only when at least one of these is true:

- the topic has enough algorithm/state-machine/configuration detail that it obscures the architecture in this SAD;
- several implementation alternatives need a focused design/review;
- a component has an independently meaningful lifecycle, contract or complexity;
- the detail is needed directly by implementation/reviewers but is not useful to a reader trying to understand SI-01 architecture as a whole.

Examples that may eventually justify focused SDDs include exact persistence/restore mechanics or exact RabbitMQ connection/retry/topology behaviour. Threading, messaging, logging and the main runtime topology remain SAD concerns unless their implementation becomes substantially more complex.

### Detailed-design document disposition

This architecture review deliberately reduced and renumbered the current SDD set. At this project stage SDD numbers are working document identifiers, so removing a document also closes the numbering gap rather than preserving obsolete sequence numbers.

- `31-01-SDD-01-data-and-display-design.md`: **deferred working note**. It is excluded from the architecture book while persistence/data mechanics are still too early for a dedicated active SDD.
- `31-01-SDD-02-java-component-design.md`: **active focused SDD** because artifact/package/composition decisions already affect the implementation repository.
- `31-01-SDD-03-backoffice-transport-design.md`: **deferred working note**. Detailed transport design should mature just in time with backoffice implementation and is excluded from the architecture book for now.

The former timing-system detailed design and runtime-topology/configuration detailed design were retired after their useful architecture was consolidated into this SAD or the domain baseline. Their historical filenames and content remain available through Git history rather than reserving gaps in the current SDD numbering.

No new SDD should be created during this cleanup unless a clear separate detailed-design purpose is demonstrated.

### Open architecture decisions

The next useful architecture work is to resolve concrete implementation choices, not create more document layers:

- state-lane queue capacities, overload policy per ingress class and backing-worker count based on Pi-Zero/integration-test measurements;
- field logging handlers, level defaults, rotation/retention and Pi-Zero resource evidence;
- embedded HTTP/WebSocket technology compatible with Java 8 and Pi Zero constraints;
- remote-shell technology;
- first concrete command/query submission/result API signatures;
- `TimingTimestamp` representation/precision/serialisation and equality/comparison semantics;
- wall-clock synchronisation, correction detection and the operational policy for a material forward/backward clock step;
- configuration format, validation library and override/secrets model;
- persistence commit/durability/atomic-write/recovery policy;
- reference ARMv6 Java 8 runtime/vendor/version;
- status/health vocabulary and publication model;
- exact public API/SPI boundaries as real consumers appear;
- RabbitMQ connection/channel/retry strategy when that integration becomes active;
- evidence threshold and timing for a later Java 11 migration.


---

## Java component, package and artifact detailed design

**Source document:** [31-01-SDD-02-java-component-design.md](./31-01-SDD-02-java-component-design.md)

Status: working draft / non-authoritative

Software item: **SI-01 — Headless Timing Application**

This SDD has one focused purpose: refine the SI-01 architecture into Java package, Maven artifact, composition and contract-placement rules that are already relevant to the implementation repository.

The application architecture itself — including runtime hierarchy, threading, messaging, integration, configuration and technology direction — is owned by `31-01-SAD-timing-application-architecture.md`.

### Why this SDD exists

This detail is kept separate because artifact/package choices already affect source layout, dependency checks, public/private composition and release boundaries in the implementation repository.

The central rule is:

> **An architecture layer or Java package is not automatically a Maven artifact.**

Keep these concepts distinct:

1. **Architecture responsibility** — semantic ownership and dependency direction, defined by the SAD.
2. **Java package** — cohesive source organisation and enforceable dependency discipline.
3. **Maven artifact** — reusable library or deployable application with a concrete consumer/lifecycle reason to exist.
4. **Application composition** — assembly of framework code and selected implementations into an executable.
5. **Contract/port** — semantic boundary placed with the responsibility that owns its meaning.

A separate artifact is justified only by a real consumer, reuse, dependency, lifecycle, deployment, ownership, public/private, release or versioning boundary.

### Initial Maven reactor

The current implementation deliberately proves only one reusable library and one executable application:

```text
event-timing-framework/
├── pom.xml                  event-timing-parent
├── framework/
│   └── pom.xml              event-timing-framework.jar
└── app/
    └── pom.xml              event-timing-app.jar
```

Working coordinates:

```text
groupId: io.github.brainboxemb.eventtiming

parent:     event-timing-parent
library:    event-timing-framework
executable: event-timing-app
```

The root parent POM is build/aggregation metadata, not a deployed product component.

### Package direction

The SAD responsibility model is finer-grained than the current artifact model.

The first framework skeleton contains marker packages such as `domain`, `core`, `platform` and `comm`. Those packages proved the framework-to-application artifact boundary; they are not a commitment that every architectural responsibility maps one-to-one to those four names.

As real implementation classes appear, package responsibilities may evolve toward areas such as:

```text
io.github.brainboxemb.eventtiming.application
io.github.brainboxemb.eventtiming.domain
io.github.brainboxemb.eventtiming.core
io.github.brainboxemb.eventtiming.presentation
io.github.brainboxemb.eventtiming.integration
io.github.brainboxemb.eventtiming.platform
```

Capability-oriented subpackages may exist beneath those responsibilities.

Do not rename or split packages merely to make the source tree match an architecture diagram. Refine package layout when real classes make semantic ownership and dependency direction testable.

### Contract placement

Do not collect every interface into one generic top-level `api` package/module.

Place contracts with the responsibility that owns their semantics. For example:

```text
presentation
  endpoint/wire-facing contracts and DTO mapping

application
  commands, queries and application-level ports

domain
  domain service/model contracts and semantic domain ports

core
  runtime/execution contracts

integration
  concrete external-system/device/persistence implementations

platform
  execution-environment abstractions
```

A dedicated public API/SPI artifact can be introduced later when an external Java consumer requires a stable independently versioned contract.

### Internal dependency direction

Java/package dependencies should preserve the ownership defined by the SAD.

Working rules:

- presentation depends inward on application contracts and does not own application state;
- application owns running mutable application state and coordinates domain/core/integration contracts;
- domain services/rules do not depend on presentation or concrete integrations;
- core supplies reusable runtime mechanics without becoming a second owner of application/domain behaviour;
- concrete integrations depend inward on application/domain ports and may use platform facilities;
- platform packages do not depend on event-timing application/domain behaviour;
- executable composition may depend on the complete supported framework surface and selected external libraries.

Circular package dependencies are not an acceptable substitute for choosing semantic ownership.

### Logging dependency placement

Logging follows the same library-versus-executable composition boundary.

```text
event-timing-framework.jar
  -> slf4j-api only

 event-timing-app.jar / runtime composition
  -> selects exactly one SLF4J provider
  -> initial provider: slf4j-jdk14
  -> backend: java.util.logging
```

Working rules:

- framework code may compile against the SLF4J API but must not force a concrete provider/backend on consumers;
- the executable application chooses the provider as part of runtime composition;
- the initial Java-8/Pi-Zero baseline uses `slf4j-jdk14` so the provider delegates to the JDK `java.util.logging` backend without introducing Logback into the baseline;
- another executable/private consumer may select another compatible provider later without changing framework source;
- exactly one provider should be present in a runtime composition;
- provider/backend versions are pinned centrally by Maven dependency management rather than scattered through modules.

This keeps logging technology replaceable at the executable boundary while giving reusable framework code one consistent facade.

### Default executable application

`event-timing-app` is the first executable consumer of the framework library.

Its package root remains:

```text
io.github.brainboxemb.eventtiming.app
```

The executable stays primarily a composition/startup boundary:

```text
main()
  -> load settings
  -> select/construct concrete integrations/platform implementations
  -> create reusable application/domain/core objects
  -> wire presentation endpoints
  -> configure runtime logging provider/backend
  -> start lifecycle
  -> install shutdown handling
```

Reusable application behaviour should not migrate into the executable merely because the architectural responsibility is called `application`.

### Derived consumers

The framework is deliberately not tied to one executable topology. Plausible consumers include:

```text
single-system application
multi-system / simulation application
public reference/test application
private/product application
```

These are consumer possibilities, not modules to create now.

### Public/private composition

Expected private/product-specific areas may include:

- production RFID control/protocol details;
- product-specific integration/protocol implementations;
- production asset/source inventory and mappings;
- production backoffice schemas/codecs where sensitive;
- deployment-specific composition/policies.

Prefer normal composition and constructor/factory injection. Do not introduce runtime plugin discovery unless a real requirement appears.

### Possible future artifacts

Create future artifacts only when a real boundary requires them. Candidates might eventually include:

- RabbitMQ integration;
- Linux/Raspberry-Pi platform integration;
- public/private RFID/CAN implementations;
- stable Java API/SPI;
- reusable test support.

Splitting later is preferred over speculative libraries, provided package/responsibility boundaries remain clean enough to extract.

### Architecture/dependency checks

Useful automated rules may include:

- presentation packages do not own or persist application state;
- domain services do not reference presentation or concrete integration classes;
- platform packages do not depend on event-timing application/domain behaviour;
- wire/protocol classes stay with their presentation/integration capability;
- semantic contracts are not moved into transport packages merely because transport code uses them;
- public code contains no real deployment mappings or proprietary values;
- the executable consumes `event-timing-framework` rather than copying/forking framework source;
- the framework artifact does not carry a concrete SLF4J provider/backend transitively;
- an executable runtime contains exactly one intended SLF4J provider.

### Open detailed-design decisions

- exact package granularity after real application/domain classes exist;
- final package naming where capability-oriented packages prove clearer than layer names;
- exact reusable boundary between single-instance runtime mechanics and multi-system application orchestration;
- how applications select/inject presentation/integration/platform implementations;
- private Maven artifact publication/consumption mechanism;
- version alignment between public framework and private implementations;
- which integrations eventually deserve independent artifacts;
- whether and when a dedicated public Java API/SPI artifact becomes justified;
- exact field logging configuration/rotation/retention policy in the default executable.


---

## GUI Application Architecture (SAD)

**Source document:** [31-02-SAD-gui-application-architecture.md](./31-02-SAD-gui-application-architecture.md)

Status: working draft / non-authoritative

Software item: **02 — Desktop GUI Application**

This Software Architecture Document describes the initial architecture direction for the desktop operator GUI. The GUI is a separate software item from the headless timing application and communicates with it through system-defined network interfaces.

### Purpose

The GUI provides an operator-facing desktop application for monitoring and controlling the timing application.

The GUI must be able to connect to a timing application running:

- locally during development;
- in a public reference/test application;
- remotely on a Raspberry Pi target;
- remotely on another Windows/Linux host where applicable.

It must not depend on in-process Java calls, internal runtime classes or direct access to timing-application files.

### Software-item relationship

```text
Software item 02
Desktop GUI Application
        |
        | system-defined application-control/status interface
        | HTTP/JSON + WebSocket are current architecture candidates
        v
Software item 01
Headless Timing Application
        |
        +-- local development host
        +-- Raspberry Pi Zero target
        +-- Windows/Linux target
```

The transport and message contracts ultimately belong in a system-level IDD rather than being owned by either software item.

### First increment

The first GUI increment should remain deliberately small and validate the software-item/interface boundary:

- configure/select a timing-application endpoint;
- connect/disconnect;
- query/display application version;
- show connection state;
- show central application status;
- show available `TimingSystem` status;
- show stale/disconnected state explicitly;
- reconnect cleanly after temporary network loss.

This is enough to verify that the GUI can operate against a timing application running on a Raspberry Pi before adding operational timing controls.

### Later operator capabilities

As system requirements and IDDs mature, the GUI may add:

- open/close a timing system;
- RFID power and reinitialisation controls;
- start procedure control;
- registration overview;
- manual registration;
- penalty registration/revocation;
- ready-team overview/control;
- device/network/backoffice status and diagnostics.

These operations remain authoritative in the headless timing application. The GUI sends commands and presents state; it does not duplicate timing-domain business rules.

### GUI IDD as system input

The graphical user interface should be treated as a **system-level interface** rather than allowing the implementation to invent screens ad hoc.

A system-level GUI IDD can define items such as:

- screen/navigation structure;
- information that must be visible;
- operator actions and control availability;
- status/state representations;
- warnings/errors/confirmation behaviour;
- update/staleness behaviour;
- terminology and identifiers;
- interaction flows for open/close/start/RFID recovery and later registration operations.

The future **SRD for software item 02** can reference the applicable GUI-IDD clauses as requirements instead of copying the interface definition into the software-item requirements.

### Software-to-software interface IDD

A separate system-level IDD should define the communication interface between software item 02 and software item 01.

Current direction:

- HTTP/JSON for commands, queries and initial snapshots;
- WebSocket for live status/data events;
- explicit versioning/compatibility of the interface;
- connection/reconnection semantics;
- authentication/authorisation when defined;
- stale-data behaviour;
- errors/result semantics.

The same interface should be usable by test tools and, where suitable, the browser/iPad software item.

### Internal GUI layering

A possible GUI structure is:

```text
GUI bootstrap
    |
    +-- presentation / views
    |
    +-- presentation models / view models
    |
    +-- GUI application services
    |      connection state
    |      status subscriptions
    |      command execution
    |
    +-- timing-application client port
           |
           +-- HTTP/WebSocket implementation
           +-- fake/stub implementation for GUI tests
```

Views should depend on presentation/application models rather than directly on HTTP/WebSocket libraries. This allows most GUI behaviour to be unit tested without a live timing application.

### Testability

The GUI should support at least three test levels:

1. **unit tests** using a fake timing-application client;
2. **integration tests** against the public reference/test application;
3. **system tests** against a real timing application, including one running on a Raspberry Pi.

The fake client should be able to produce version/status changes, disconnects, stale state and command results deterministically.

### Technology choices still open

- desktop GUI toolkit/framework;
- packaging/distribution model;
- HTTP/WebSocket client library compatible with the selected GUI runtime;
- whether the GUI uses the same Java baseline as software item 01 or can use a newer runtime;
- configuration storage for known endpoints;
- authentication/credential storage;
- update mechanism.

The Raspberry Pi Java-8 constraint applies to the headless timing application. It does **not automatically require** the desktop GUI to use Java 8; that should be a separate software-item decision.


---

## Web Operator Application Architecture (SAD)

**Source document:** [31-03-SAD-web-operator-application-architecture.md](./31-03-SAD-web-operator-application-architecture.md)

Status: working draft / non-authoritative

Software item: **03 — Web Operator Application**

This Software Architecture Document describes the React-based browser/iPad operator application as a separate software item. The application is delivered by the headless Timing Application over HTTP but executes in the browser and communicates with the timing system only through system-defined interfaces.

### Responsibility

Software item 03 provides a browser-based operational user interface for a timing system.

Expected responsibilities include:

- load and run in a modern browser/iPad Safari environment;
- connect to software item 01 over HTTP/WebSocket;
- show application/timing-system/subsystem status;
- show registration data and relevant local timing information;
- open and close a logical timing system when authorised;
- initiate the local start procedure when authorised;
- show/manage ready-team state where applicable;
- later support manual registration and penalty operations where authorised;
- make disconnected/stale state visible to the operator.

It does **not** own authoritative registration or timing-domain state.

### Deployment model

The compiled React application is intended to be served as static content by software item 01:

```text
Timing Application (SI-01)
   |
   | HTTP: HTML/JS/CSS bundle
   v
browser / iPad
Web Operator Application (SI-03)
   |
   | HTTP commands/queries
   | WebSocket status/events
   v
Timing Application (SI-01)
```

Serving the bundle from SI-01 simplifies local deployment and ensures the browser can reach the same endpoint even when the wider internet/backoffice is unavailable.

The exact JavaScript/React build toolchain and browser-support baseline remain open.

### Interface boundary

The web application consumes the same system-level application command/query/event semantics as other external clients where practical.

HTTP is the current direction for:

- loading the application;
- initial state/query retrieval;
- operator commands;
- explicit request/response operations.

WebSocket is the current direction for:

- live status updates;
- registration/event updates;
- ready-team/data updates;
- connection/staleness indication.

The browser must not bypass SI-01 by accessing its files or internal Java classes directly.

### State ownership

The web application may maintain presentation/cache state, but SI-01 remains authoritative.

On connect/reconnect the web application should be able to obtain a complete current state/snapshot before applying subsequent live updates.

This is especially important after:

- browser refresh;
- Wi-Fi interruption;
- iPad sleep/wake;
- WebSocket reconnect;
- SI-01 restart.

### Offline and degraded behaviour

The browser client itself is not required to become a second autonomous timing system.

When its connection to SI-01 is lost it should:

- clearly show disconnected/stale state;
- stop presenting cached operational data as current without indication;
- avoid pretending commands succeeded when acknowledgement was not received;
- reconnect/resynchronise when the timing application becomes reachable again.

The timing application may continue local RFID/CAN/registration operation while the browser is disconnected.

### Security boundary

Authentication, authorisation and transport security need system-level requirements/IDD definition.

The web application should not contain long-lived secrets that are inappropriate for browser delivery. Operator permissions should be enforced by SI-01 rather than trusted only to disabled/hidden UI controls.

### Relationship to system IDDs and SRD

A future software-item requirements document is expected under the software-item-03 requirement family, for example:

```text
20-03-SRD-web-operator-application-requirements.md
```

Likely system-level interface inputs include:

- application control/status interface IDD between SI-03 and SI-01;
- WebSocket/live-event portions of that interface;
- operator/HMI IDD describing required information and operator actions.

The SRD should reference those system-owned interface obligations rather than duplicate them.

### Verification direction

Early verification should prove at least:

- bundle can be served by SI-01;
- application can load on a normal desktop browser and representative iPad/Safari environment;
- version/status can be displayed from SI-01;
- disconnect/stale state is visible;
- reconnect obtains a complete fresh state before normal live updates resume;
- commands use the system interface and receive explicit success/failure responses;
- browser operation does not require live backoffice/internet connectivity when SI-01 remains locally reachable.

### Open architecture questions

- React/build-tool/version baseline;
- supported browser/iPad versions;
- authentication/session model;
- HTTP/API technology and resource model;
- WebSocket event envelope and revision/sequence semantics;
- whether desktop and browser clients share generated client models or only the system IDD;
- how static assets are versioned/cached across SI-01 upgrades;
- whether the web application is built in the framework/reference repository or a dedicated repository;
- detailed operator screen/navigation design.


---

## Data and display detailed design

**Source document:** [31-01-SDD-01-data-and-display-design.md](./31-01-SDD-01-data-and-display-design.md)

Status: working draft / non-authoritative

Software item: **01 — Headless Timing Application**

This document refines local data ownership, backup/restore, traceable registration streams, ready-team behaviour, reference data, and the two display generations.

The initial design does **not** require a conventional embedded database. Runtime state is held in typed Java data structures/repositories and is backed up to simple files so the application can restore its state after restart.

Domain identifiers and known ranges are captured in `03-domain-baseline.md`. This SDD translates those facts into software/data-design direction.

### Core distinction: two traceable information models

Two information flows must not be conflated:

1. **registration stream/ledger** — timing and operational entries that are synchronised as an ordered source stream;
2. **ready-team journal/state** — keypad/operator actions that prepare/remove teams and drive current display state.

Both need traceability and persistence, but they have different semantics and sequence scopes.

### Registration-source identity

Every registration source/system has a `RegistrationSystemId`.

Known source classes are:

```text
normal registration systems   A..I
reserve registration systems  1..4 (exact identifier representation TBD)
virtual registration systems  exist; exact identifier representation TBD
```

Every physical location has:

```text
LocationId = 1..25
```

A registration entry is associated with both its source and its location.

The exact mapping between the architecture concept `TimingSystem` and domain concept `RegistrationSystemId` still needs confirmation. Code should not rely on those being identical until that mapping is explicitly decided.

### Registration ledger

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

### Registration sequence and stable record key

The registration sequence is **monotonically increasing per `RegistrationSystemId` / source**.

It is not scoped by location and it is not one global sequence across all registration systems.

Conceptually:

```text
RegistrationRecordKey = (RegistrationSystemId, SequenceNumber)
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

![Registration traceability — sequence per source](../assets/architecture/registration-stream-identity.svg)

#### Illustrative record model

```java
final class RegistrationRecord {
    private RegistrationSystemId registrationSystemId;
    private long sequenceNumber;
    private LocationId locationId;
    private RegistrationType type;
    private Instant observedAt;
    private Instant createdAt;
    private RegistrationOrigin origin;
    private TeamNumber teamNumber;              // when applicable
    private RegistrationRecordKey reference;    // corrections/revocations
    private RegistrationPayload payload;         // type-specific data
}

final class RegistrationRecordKey {
    private RegistrationSystemId registrationSystemId;
    private long sequenceNumber;
}
```

Names are illustrative; the important design is the source-scoped sequence and explicit location association.

#### Sequence allocation

A sequence allocator is owned per registration source:

```java
interface RegistrationSequence {
    long next(RegistrationSystemId sourceId);
}
```

Conceptual processing:

```java
void acceptRegistration(RegistrationCandidate candidate) {
    RegistrationSystemId source = candidate.registrationSystemId();
    long sequence = registrationSequence.next(source);

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

The serialized application path is a natural place to allocate/order records, but the exact relationship between executor ownership and multiple `RegistrationSystemId` streams remains part of the `TimingSystem` mapping decision.

### Sequence persistence and synchronisation

Sequence allocation is a domain consistency mechanism, not a storage implementation detail.

Required direction:

- never reuse a committed `(RegistrationSystemId, SequenceNumber)` after restart;
- preserve monotonic order independently for each registration source;
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

### Ready-team journal and current state

Keypad input has a different purpose. It indicates which teams should be prepared/ready for local operation/display. A keypad action is not itself a passage/start/penalty registration.

The keypad can:

```text
add team to ready list
remove team from ready list
```

Those actions still need to be stored so operational history is traceable and state can be recovered.

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

This provides:

- **journal/history** — what keypad/operator did and in what order;
- **current state** — which teams are currently ready.

Illustrative record:

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

The ready-team sequence is a separate design question from the registration-source sequence. It may use its own journal sequence or later a broader operational-event sequence, but it must not accidentally consume/alter a `RegistrationSystemId` registration sequence unless requirements explicitly make a ready-team action a registration-stream entry.

### Team and tag identities

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

### In-memory authoritative state with file backup

The initial implementation direction is:

```text
live application
    |
    +-- RegistrationRepository      source-ordered history in memory
    +-- RegistrationState           current/derived registration views
    |
    +-- ReadyTeamEventRepository    keypad/operator history in memory
    +-- ReadyTeamState              current ready-team queue/list
    |
    +-- StartTimeRepository         backoffice reference data in memory
    +-- ReserveTagRepository        backoffice reference data in memory
    |
    +-- RegistrationSequenceState   next sequence per RegistrationSystemId
    |
    +-- simple file backup / restore
```

The application operates on typed in-memory structures rather than repeatedly parsing files during normal operation. Files provide persistence/recovery, not the primary domain API.

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
    StartTime find(TeamNumber teamNumber);
    StartTimeSnapshot snapshot();
}
```

Concrete implementations can use collections/maps appropriate to lookup patterns.

### Backup policy

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
last registration sequence per source
last ready-team sequence
last reference-data synchronisation time/version
```

### Startup restore

A possible startup sequence is:

```text
start process
   |
   v
load configuration
   |
   v
load trace journals / snapshots / source sequence metadata
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
ReadyTeamState readyTeams = new InMemoryReadyTeamState();
for (ReadyTeamEvent event : readyTeamEvents.snapshot()) {
    readyTeams.apply(event);
}
```

A missing/corrupt backup or inconsistent sequence metadata must result in explicit status rather than silently looking healthy.

### Start-time and reserve-tag synchronisation

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

### Keypad behaviour

The CAN keypad can both add and remove team numbers from ready-team state.

Possible incoming messages:

```text
KeypadTeamAddRequested(teamNumber)
KeypadTeamRemoveRequested(teamNumber)
```

Both enter the normal serialized state-change path. The handler creates a traceable `ReadyTeamEvent`, stores it, applies it to current state and then rebuilds/publishes display data.

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

The application, not the keypad, remains authoritative for current ready-team state. Duplicate-add, remove-not-present, ordering and capacity behaviour need explicit requirements.

### Display model

Display data is derived from **current state**, not by forwarding keypad history directly.

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

![In-memory data, backup and V1/V2 display behaviour](../assets/architecture/data-display-flow.svg)

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

Fields are illustrative. The display IDD will ultimately define the system contract.

### Display V1 — passive CAN display

Display V1 is relatively passive and must be actively driven by the timing application.

V1 does not reconstruct add/remove history. The application derives the **current ready-team list** and writes the appropriate complete/current display state.

```java
void refreshV1() {
    DisplayModel current = displayModelService.current();
    canDisplayV1.apply(current);
}
```

Implications:

- `TEAM_ADDED` updates `ReadyTeamState`, then triggers a refreshed current list;
- `TEAM_REMOVED` updates `ReadyTeamState`, then triggers a refreshed current list;
- after discovery/reconnect/reset, send a full refresh from current state;
- a V1 reset does not destroy application ready-team state;
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
  ReadyTeamJournal
          |
          v
    ReadyTeamState
          |
          +--> V1 current list
          +--> V2 synchronised data
```

A team can be ready for display without having produced a registration, and a registration can exist independently from whether that team is currently ready.

Later interactions (for example automatically removing a team after a successful start/passage) must be explicit domain requirements rather than accidental display side effects.

### Synchronisation and threading

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

### Candidate requirements

Temporary identifiers only; these are not yet formal requirements.

#### Registration identity and traceability

- **CAND-REG-001** — Each registration system/source shall have a stable `RegistrationSystemId`.
- **CAND-REG-002** — Each physical location shall have a unique `LocationId` in the known domain range `1..25`.
- **CAND-REG-003** — Each committed registration entry shall contain both `RegistrationSystemId` and `LocationId`.
- **CAND-REG-004** — Each committed registration entry shall receive a monotonically increasing sequence number scoped to its `RegistrationSystemId`.
- **CAND-REG-005** — The stable registration record identity shall include `RegistrationSystemId` and sequence number so upstream systems can order records and detect gaps per source.
- **CAND-REG-006** — Registration sequence allocation shall survive restart/restore and shall not reuse previously committed sequence numbers for a source.
- **CAND-REG-007** — Opening a location/waypoint shall create a traceable registration-stream entry.
- **CAND-REG-008** — Registration corrections and revocations shall remain traceable to earlier record identity and shall not silently overwrite historical records.

#### Tag/team identity

- **CAND-TAG-001** — Decoded team numbers shall support the known range `0..999`.
- **CAND-TAG-002** — Tag decoding shall distinguish normal versus reserve-tag prefix semantics.
- **CAND-TAG-003** — Tag decoding shall retain the postfix/copy identity needed to distinguish the two physical tags associated with one team identity.
- **CAND-TAG-004** — Reserve tags shall be resolvable using locally available mapping data synchronised from the backoffice.

#### Local data and backup

- **CAND-DATA-001** — The initial implementation shall maintain active registration, ready-team and reference state in application data structures without requiring an external database engine.
- **CAND-DATA-002** — The system shall back up locally required traceable history/state to simple persistent files and shall be able to restore that information during startup.
- **CAND-DATA-003** — Backup/restore failures shall be represented in system status.
- **CAND-DATA-004** — The local start-time data set shall be synchronisable from the backoffice and remain available after loss of live backoffice connectivity.
- **CAND-DATA-005** — The system shall track enough reference-data synchronisation metadata to determine whether local data is current/stale relative to the latest accepted update.

#### Ready-team/keypad data

- **CAND-READY-001** — The system shall maintain ready-team state logically separate from timing/registration records.
- **CAND-READY-002** — Adding or removing a team from ready-team state shall create a traceable persisted ready-team event.
- **CAND-READY-003** — Ready-team events shall be processed through the normal controlled state-change path.
- **CAND-READY-004** — Ready-team state shall be recoverable after application restart from locally persisted information.
- **CAND-READY-005** — The keypad shall be able to request both addition and removal of a team number.

#### Displays

- **CAND-DISP-004** — The application shall derive display data from current timing/reference/ready-team state rather than requiring displays to reconstruct operational event history.
- **CAND-DISP-005** — Display V1 shall be actively controlled by the application and shall receive current ready-team display state/list after relevant changes or reconnect.
- **CAND-DISP-006** — Display V2 shall consume synchronised timing/ready-team/reference data from the application and shall own local presentation/rendering behaviour.
- **CAND-DISP-007** — When Display V2 connects or reconnects, the application shall be able to provide a complete current data snapshot independent of previously delivered incremental updates.
- **CAND-DISP-008** — Display data shall support a revision/version mechanism or equivalent means of detecting stale/missed state.

### Open questions

- What exact identifiers represent reserve registration systems `1..4` in software/wire formats?
- What exact identifiers represent virtual registration systems?
- Is one architecture `TimingSystem` exactly one `RegistrationSystemId`, or can a TimingSystem host/coordinate multiple registration sources?
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
- Should a successful start/passage automatically affect the ready-team list, or must that always be an explicit action?
- Does V1 retain any useful state across reconnect/power interruption or must every connection be treated as blank/unknown?
- What exact data fields does V2 need, and which presentation decisions belong exclusively inside V2?


---

## Backoffice transport detailed design

**Source document:** [31-01-SDD-03-backoffice-transport-design.md](./31-01-SDD-03-backoffice-transport-design.md)

Status: working draft / non-authoritative

Software item: **SI-01 — Headless Timing Application**

This SDD defines the transport-independent backoffice boundary and two intended communication implementations:

- a lightweight **socket implementation** for automated loop/network system tests;
- a **RabbitMQ implementation** for production-shaped integration and deployment.

The application/domain model must not depend on RabbitMQ classes, socket classes, broker names, or the proprietary production message format.

Concrete production broker endpoint names, credentials, queue/exchange names, routing keys, external source IDs and message schemas are deployment/proprietary information and are intentionally excluded from this public repository.

Package/artifact placement follows `31-01-SDD-02-java-component-design.md`: a transport implementation can initially live under the framework `comm` packages and becomes a separate Maven library only when independent reuse, dependencies, lifecycle, ownership or release boundaries justify that split.

### Architectural goal

Backoffice semantics and transport are separate responsibilities:

```text
Timing/domain behaviour
       |
       v
Backoffice semantic boundary
  source-aware messages
  status
  outbox
       |
       +-----------------------+
       |                       |
       v                       v
SocketBackoffice           RabbitMqBackoffice
system-test transport      production-shaped transport
       |                       |
       v                       v
socket test peer           RabbitMQ broker
```

Both implementations must preserve the same logical `RegistrationSource` identity and feed the same serialized application/domain path.

### Semantic backoffice boundary

The reusable framework/domain side should work with semantic source-aware messages, not transport destinations.

Illustrative contracts:

```java
interface BackofficePublisherPort {
    void publish(RegistrationSourceKey source, BackofficeEnvelope message);
}

interface BackofficeInboundListener {
    void onMessage(RegistrationSourceKey source, BackofficeEnvelope message);
}
```

`BackofficeEnvelope` is a reusable/public semantic envelope or test representation. It must not force proprietary production serialization into the public framework.

These semantic contracts belong with the domain/backoffice responsibility that owns their meaning. Transport/session/wire types belong under `comm`.

The final system-level backoffice IDD can define the semantic obligations that both sides must fulfil while transport-specific/private specifications define their actual encoding where required.

### Registration-source separation

Every configured `RegistrationSource` has its own logical inbound and outbound backoffice path.

Conceptually:

```text
source-01
  inbound semantic stream
  outbound semantic stream

source-02
  inbound semantic stream
  outbound semantic stream
```

This logical separation remains the same regardless of whether the selected transport is an in-memory stub, socket connection, or RabbitMQ.

### Transport selection and composition

Backoffice transport is selected through settings/application composition rather than compiled into domain code.

Pseudo-configuration:

```yaml
backoffice:
  transport: socket-test   # or rabbitmq
```

The executable application resolves this selection to a concrete communication implementation. A public reference/test application can use `socket-test` or a stub. A private/product application can select RabbitMQ plus private mappings/codecs where required.

This selection does not imply a separate Maven artifact for every transport. Initial implementations may coexist in the framework library while their boundaries are being tested.

### Socket test transport

#### Purpose

The socket implementation provides a lightweight real communication boundary without requiring RabbitMQ or Docker.

It is intended for automated system tests that need to prove:

- SI-01 runs as a real process;
- source-aware messages cross a real TCP/socket boundary;
- inbound and outbound routing works for several sources;
- connect/disconnect/reconnect behaviour is observable;
- tests can run quickly and locally without production infrastructure.

It is not intended to define or expose the production backoffice protocol.

#### Test topology

```text
System test driver / backoffice simulator
             |
             | simple TCP socket
             v
SocketBackoffice
             |
             v
Backoffice semantic boundary
             |
             v
framework domain/core
```

One connection can multiplex several logical registration sources because every test message includes a generic source key.

#### Test framing

The exact framing remains an implementation choice. A simple public test protocol could use a length-prefixed or line-delimited synthetic envelope such as:

```text
sourceKey
messageType
payload
```

The socket test protocol must use only synthetic/public fields and must not copy proprietary production serialization.

The important contract is deterministic framing, source identity, reconnect behaviour and unambiguous message boundaries.

#### Socket-loop scenarios

Candidate scenarios include:

- connect a backoffice simulator to a real application process;
- inject source-01 and source-02 messages over one connection;
- verify they reach the correct source path;
- trigger application behaviour through the normal application interface;
- observe outbound source messages at the simulator;
- drop the socket and verify status/reconnect behaviour;
- reconnect and continue without changing committed registration-sequence identity;
- exercise one or multiple `TimingSystemInstance`/asset/source combinations according to the selected executable topology.

### RabbitMQ transport

RabbitMQ is a concrete communication implementation beneath the same semantic boundary.

![RabbitMQ shared connection with per-source consumers and controlled publishing](../assets/architecture/rabbitmq-source-topology.svg)

#### RabbitMQ terminology

Receiving and sending are intentionally modelled differently:

- a consumer reads/delivers messages from a RabbitMQ **queue**;
- a publisher normally publishes to an **exchange** with a **routing key**;
- RabbitMQ routes that publication to one or more queues according to broker bindings.

The working source configuration is therefore:

```text
RabbitMqSourceMessagingConfig
  inboundQueue
  outboundExchange
  outboundRoutingKey
```

If production uses the default exchange or a direct-to-queue convention, the implementation can represent that through the same outbound-endpoint abstraction.

#### RabbitMQ connection topology

The preferred initial architecture is one RabbitMQ connection manager per executable process using that transport:

```text
application
  RabbitMqConnectionManager
        |
        +-- source-01 inbound consumer/channel
        +-- source-02 inbound consumer/channel
        +-- ...
        |
        +-- controlled outbound publisher/channel(s)
```

Several source-specific queues can therefore be consumed over one physical broker connection.

A later implementation may use separate consumer and publisher connections if fault-isolation, channel/thread ownership, broker-client behaviour or measured Pi Zero evidence justifies it. That refinement must not change the semantic source interface.

#### RabbitMQ threading

RabbitMQ callbacks are external I/O callbacks and must not directly mutate timing-domain state.

```text
RabbitMQ consumer callback
      |
      v
source-aware BackofficeInboundMessage
      |
      v
resolve TimingSystemInstance / RegistrationSource
      |
      v
serialized framework/domain boundary
```

Each consumer must have controlled channel ownership. Arbitrary domain threads must not publish directly on shared RabbitMQ channels.

#### RabbitMQ source-specific settings

Pseudo-configuration only:

```yaml
backoffice:
  transport: rabbitmq
  rabbitmq:
    host: ${BROKER_HOST}
    port: ${BROKER_PORT}
    virtualHost: ${BROKER_VHOST}
    credentials: external-secret-reference

systemInstances:
  - id: system-01
    registrationAssets:
      - id: asset-01
        sources:
          - key: source-01
            externalId: ${PRIVATE_SOURCE_ID_01}
            messaging:
              inboundQueue: ${PRIVATE_SOURCE_01_IN_QUEUE}
              outboundExchange: ${PRIVATE_SOURCE_01_OUT_EXCHANGE}
              outboundRoutingKey: ${PRIVATE_SOURCE_01_OUT_KEY}
          - key: source-02
            externalId: ${PRIVATE_SOURCE_ID_02}
            messaging:
              inboundQueue: ${PRIVATE_SOURCE_02_IN_QUEUE}
              outboundExchange: ${PRIVATE_SOURCE_02_OUT_EXCHANGE}
              outboundRoutingKey: ${PRIVATE_SOURCE_02_OUT_KEY}
```

For two configured sources, two inbound consumers exist even if they share one physical RabbitMQ connection.

### Outbox and delivery

Local commitment and external transport are deliberately separated.

```text
RegistrationSource
  committed record
       |
       v
local outbox / sync state
       |
       v
BackofficePublisherPort
       |
       +--> SocketBackoffice
       |
       +--> RabbitMqBackoffice
```

A locally committed registration must not disappear because a transport is unavailable.

Working direction:

1. commit registration locally according to the final persistence rule;
2. represent it as pending in local outbox/synchronisation state;
3. selected transport attempts delivery;
4. transport acknowledgement/reconciliation advances pending state;
5. failure remains pending and visible through status.

The exact acknowledgement, retry, duplicate/idempotency and reconciliation rules belong to later requirements/IDD/detail design.

### Status model

Transport status and source status remain separately observable.

```text
BackofficeStatus
  selectedTransport
  connection/session state

  source-01
    inbound
      configured
      active
      lastMessage
    outbound
      pendingCount
      lastPublish
      lastFailure

  source-02
    ...
```

For RabbitMQ, connection status can additionally expose broker/authentication/recovery information. For socket testing, it can expose connected/disconnected peer state.

### Java package and future artifact placement

Working package direction inside the reusable framework:

```text
io.github.brainboxemb.eventtiming.domain.backoffice
    semantic backoffice contracts/state/outbox concepts

io.github.brainboxemb.eventtiming.comm.socket
    socket session/framing/test transport

io.github.brainboxemb.eventtiming.comm.rabbitmq
    RabbitMQ connection/channel/consumer/publisher implementation
```

This does **not** require three Maven libraries.

A future `event-timing-comm-rabbitmq` (or similarly named) artifact becomes useful when, for example:

- several applications need RabbitMQ independently;
- the RabbitMQ client dependency should be optional and excluded from non-RabbitMQ applications;
- lifecycle/release ownership needs an independent boundary;
- public/private implementation ownership requires extraction.

Until such evidence exists, clean package boundaries are sufficient and make later extraction straightforward.

### Public/private boundary

Public framework/test code may define:

- transport-independent semantic ports;
- generic `RegistrationSourceKey`;
- generic/test `BackofficeEnvelope`;
- socket-test communication implementation/protocol;
- RabbitMQ connection/consumer infrastructure if proprietary production codec details remain separate;
- synthetic RabbitMQ topology for integration tests.

Private components/configuration may provide:

- actual external source-ID mappings;
- actual broker topology names;
- proprietary message schemas/codecs;
- authentication details;
- production-specific retry/reconciliation protocol details where sensitive.

### Automated system-test profiles

The transport abstraction supports progressively more realistic automated system tests.

#### ST-1 — Application behaviour

Goal: validate application behaviour through its public control/status interface while external dependencies are controlled stubs.

```text
System-test driver
      |
      | public application control/status interface
      v
real application process
      |
      +-- stub RFID/CAN/display
      +-- in-memory/stub backoffice port
```

This is the fastest system-level feedback loop and does not require a network backoffice service.

#### ST-2 — Socket loop/network

Goal: add a real communication/process boundary with minimal infrastructure.

```text
application test driver --> real application process
backoffice simulator <----> simple socket implementation
```

This profile verifies source multiplexing/routing, network session state, disconnect/reconnect and outbound/inbound semantics without RabbitMQ.

#### ST-3 — RabbitMQ integration

Goal: verify the production-shaped broker transport with a real disposable broker.

```text
system-test driver
      |
      +--> application interface
      |
      +--> RabbitMQ test broker (Docker Compose)
```

This verifies broker connection/channel/consumer behaviour, source-specific queues/routing, outbox recovery and broker restart scenarios.

These profiles complement unit/component tests and Pi Zero/hardware-in-the-loop verification; they do not replace them.

### Docker-based RabbitMQ test environment

RabbitMQ is a good candidate for a containerised integration dependency because it is a real external service with meaningful connection and recovery behaviour.

A future implementation/reference application can provide a small Compose environment:

```text
compose.yaml
  rabbitmq-test
```

The broker must use synthetic/public queue names and credentials.

Typical lifecycle:

```text
start RabbitMQ container
wait for health
start application
exercise several source consumers + publisher
stop/restart broker
verify consumer restoration + pending delivery
clean up
```

Docker remains optional for ST-1 and ST-2 so most behaviour can be tested without container startup cost.

### Candidate requirements

Temporary identifiers only.

- **CAND-BO-001** — SI-01 backoffice semantics shall be independent from the concrete communication transport.
- **CAND-BO-002** — The backoffice transport shall be selectable through external configuration/composition.
- **CAND-BO-003** — A lightweight socket transport shall be available for automated system/integration testing without requiring RabbitMQ.
- **CAND-BO-004** — The socket test protocol shall support multiple logical registration sources over a real communication boundary.
- **CAND-BO-005** — RabbitMQ shall support a source-specific inbound queue configuration for each configured registration source.
- **CAND-BO-006** — RabbitMQ shall support source-specific outbound routing configuration for each configured registration source.
- **CAND-BO-007** — Multiple RabbitMQ source consumers shall be able to share one physical broker connection.
- **CAND-BO-008** — External transport callbacks shall not directly mutate timing-domain state.
- **CAND-BO-009** — Transport connection status and per-source inbound/outbound status shall be observable independently.
- **CAND-BO-010** — Loss of external backoffice transport shall not discard locally committed registration data.
- **CAND-BO-011** — Reconnection shall restore configured source communication and resume pending outbound synchronisation.
- **CAND-BO-012** — Production broker/source topology, protocol details and credentials shall remain external/private configuration or implementation.
- **CAND-BO-013** — A disposable RabbitMQ broker shall be available for automated ST-3 integration tests.

### Open questions

- What exact semantic messages belong in the public backoffice IDD?
- What minimal public socket-test framing should be used: length-prefixed binary, line-delimited JSON, or another simple representation?
- Should the socket implementation use one bidirectional connection or separate inbound/outbound sockets?
- Is one RabbitMQ connection sufficient in production, or should consumer and publisher traffic use separate connections?
- Are RabbitMQ queues/exchanges pre-provisioned or should the application declare/bind any topology?
- At what point does RabbitMQ deserve its own Maven library rather than a `comm` package inside the framework artifact?
- What is the production acknowledgement/reconciliation protocol?
- Which outbound items require durable local outbox persistence versus rebuildable state?
- What publisher-confirm/retry policy is required?
- How are duplicates/redeliveries detected and handled?
- What broker/client settings are appropriate on the Raspberry Pi Zero memory/CPU budget?


---

## Application Control and Status Interface (IDD)

**Source document:** [40-01-IDD-application-control-status.md](./40-01-IDD-application-control-status.md)

Status: review candidate / AP-1 first-executable slice

System interface: **IF-03 — Application Control & Status**

### Purpose

This Interface Design/Description Document owns the system-level software-to-software contract between SI-01 and network clients such as SI-02, SI-03 and automated ST-1 test tooling.

For AP-1 it defines only the first-executable subset needed to expose build/version identity, current status and status-change events. Later operator commands and domain data are deliberately deferred until their SIP increments require them.

### Parties

```text
client side
  SI-02 Desktop GUI
  SI-03 Web Operator Application
  ST-1 / integration test driver
        |
        | IF-03
        v
SI-01 Headless Timing Application
```

SI-01 owns the authoritative application/status state. Clients observe/query that state and later submit permitted commands; they do not become authoritative merely by caching a response.

### Transport baseline

The first-executable transport contract is:

- HTTP with JSON for request/response queries;
- WebSocket for live status/event delivery;
- API major version represented in the resource path as `/api/v1`;
- network boundary usable when SI-01 and the client run on different hosts;
- the same semantic application model may also be represented through local console/remote-shell adapters, but those transports are not owned by this IDD.

The contract must remain compatible with Java 8 and the mandatory Raspberry Pi Zero target, but this IDD does not select a concrete Java HTTP/WebSocket library.

### First-executable resources

```text
GET /api/v1/version
GET /api/v1/status
WS  /api/v1/events
```

Only `GET` is required for the two HTTP resources in this slice. Later application commands may add other methods/resources without changing the ownership principle.

### Common compatibility rules

- JSON member names defined by this first slice are stable within API major version `v1`.
- Clients shall tolerate additional/unknown JSON members so the status model can grow compatibly.
- A breaking representation/semantic change requires a new API major path such as `/api/v2` or an explicitly documented compatible migration mechanism.
- Unknown event types shall not corrupt client state; a client may ignore/log an event type it does not understand and can always re-query `/status`.
- UTF-8 is used for JSON text.
- timestamps in the public contract use ISO-8601 UTC text form.

### Build/version identity

The stable first-executable build identity is:

```json
{
  "application": "timing-application",
  "version": "<project-version>",
  "revision": "<source-revision>",
  "buildTime": "<ISO-8601 UTC>",
  "apiVersion": "1"
}
```

Field semantics:

- `application` — stable application identity for SI-01;
- `version` — project/application version from the produced build;
- `revision` — source revision used to produce the running artifact, normally the Git commit SHA;
- `buildTime` — build provenance timestamp according to the build/toolchain policy;
- `apiVersion` — IF-03 major API version represented by this contract.

The build/toolchain may later strengthen reproducible-build timestamp policy without changing these semantic fields.

### Status snapshot

The first-executable status representation is:

```json
{
  "apiVersion": "1",
  "build": {
    "application": "timing-application",
    "version": "<project-version>",
    "revision": "<source-revision>",
    "buildTime": "<ISO-8601 UTC>",
    "apiVersion": "1"
  },
  "application": {
    "state": "RUNNING",
    "startedAt": "<ISO-8601 UTC>"
  },
  "timingSystems": [
    {
      "id": "<configured-instance-id>",
      "lifecycle": "CLOSED"
    }
  ],
  "problems": []
}
```

First-executable application states are:

```text
STARTING
RUNNING
DEGRADED
STOPPING
```

`DEGRADED` means the process remains capable of serving status while one or more first-executable startup/configuration problems are observable. Fatal configuration errors that prevent the HTTP service from starting may still terminate the process and are verified separately through process exit/log evidence.

The first executable does not yet implement operational open/close commands. A configured minimal `TimingSystemInstance` therefore reports `CLOSED`; later SIP increments may add additional lifecycle values while preserving the field/ownership model.

Problem entries use:

```json
{
  "code": "<stable-machine-code>",
  "severity": "WARNING|ERROR",
  "message": "<human-readable-summary>"
}
```

Clients must not make business decisions by parsing the human-readable `message`; `code` and structured status fields are the machine-readable contract.

### First-executable semantic operations

#### IF03-OP-001 — Get build/version identity

HTTP mapping:

```text
GET /api/v1/version
```

Successful response:

- HTTP `200`;
- `application/json`;
- body is the build/version identity defined above.

Semantics:

- returns the authoritative application build/version identity;
- does not derive a separate client-specific version value;
- remains stable for the lifetime of one running application build;
- is equivalent in meaning to version identity shown by first-executable console/remote-shell views.

#### IF03-OP-002 — Get current status snapshot

HTTP mapping:

```text
GET /api/v1/status
```

Successful response:

- HTTP `200`;
- `application/json`;
- body is one coherent status snapshot using the schema above.

Later subsystem/device/backoffice fields may extend the model without changing the ownership principle.

#### IF03-OP-003 — Subscribe to status/event updates

WebSocket mapping:

```text
/api/v1/events
```

After the WebSocket connection is established SI-01 shall immediately send a complete `STATUS_SNAPSHOT` event before normal change events are relied upon.

Event envelope:

```json
{
  "apiVersion": "1",
  "eventType": "STATUS_SNAPSHOT",
  "occurredAt": "<ISO-8601 UTC>",
  "payload": {}
}
```

First-executable event types:

```text
STATUS_SNAPSHOT
STATUS_CHANGED
```

For `STATUS_SNAPSHOT`, `payload` contains the complete current status representation.

For `STATUS_CHANGED`, `payload` also contains a complete current status representation in the first executable. This deliberately avoids introducing partial-patch/replay semantics before they are needed. Later compatible optimisation may add more event types while `/status` remains the authoritative resynchronisation operation.

WebSocket transport ordering is sufficient for first-executable events; no durable cross-connection event sequence is introduced in AP-1.

### Reconnect and resynchronisation

Reconnect semantics are intentionally simple:

1. client reconnects to `/api/v1/events`;
2. SI-01 sends a new complete `STATUS_SNAPSHOT` event;
3. the client replaces its cached status with that snapshot;
4. subsequent `STATUS_CHANGED` events are applied in WebSocket delivery order;
5. the client may call `GET /api/v1/status` at any time to explicitly recover current authoritative state.

No event replay across disconnected sessions is required by the first executable.

### Error responses

HTTP failures use a JSON envelope:

```json
{
  "apiVersion": "1",
  "error": {
    "code": "<stable-machine-code>",
    "message": "<human-readable-summary>"
  }
}
```

Initial status mapping:

| HTTP status | Meaning in first executable |
| --- | --- |
| `400` | malformed request where applicable |
| `404` | unknown resource |
| `405` | unsupported HTTP method on a known resource |
| `500` | unexpected internal interface failure |

A normal application degradation represented by `/status` is not converted into HTTP `500` merely because the application reports a problem.

### Network access and first-executable security policy

Authentication/authorisation is explicitly **deferred** for the first executable development baseline. This is a deliberate scope decision, not an assumption that the final product is unauthenticated.

Until a later security/interface increment defines authentication:

- the default IF-03 listen address shall be loopback/local-only;
- non-loopback binding must require explicit configuration;
- remote first-executable demonstrations shall run only on a trusted development/test network;
- deployment/prod exposure outside that controlled environment is out of scope;
- CORS/browser-origin policy is deferred until SI-03/browser work requires it.

This allows ST-1 and SI-02 development without prematurely inventing production security while preventing accidental default exposure.

### First-executable contract rules

**IF03-REQ-001 — Shared semantics**  
HTTP/JSON and WebSocket representations shall map to the shared SI-01 application/status semantics rather than implement independent business/status state in the transport adapter.

**IF03-REQ-002 — Remote-host operation**  
The interface shall support operation across a normal IP network boundary when non-loopback access is explicitly configured, so a client can run on a workstation while SI-01 runs on another host such as a Raspberry Pi.

**IF03-REQ-003 — Version query**  
The interface shall provide `GET /api/v1/version` representing `IF03-OP-001`.

**IF03-REQ-004 — Status query**  
The interface shall provide `GET /api/v1/status` representing `IF03-OP-002`.

**IF03-REQ-005 — Live status/event delivery**  
The interface shall provide WebSocket `/api/v1/events` representing `IF03-OP-003` for the first executable.

**IF03-REQ-006 — Reconnect to authoritative state**  
A client that connects/reconnects shall receive a complete current status snapshot before relying on subsequent live events.

**IF03-REQ-007 — Machine-readable representation**  
The HTTP query representation shall be machine-readable JSON suitable for SI-02/SI-03 and automated ST-1 verification.

**IF03-REQ-008 — Explicit failure response**  
Unsupported or invalid HTTP requests shall produce the explicit JSON failure outcome defined in this IDD rather than a successful response containing silently invalid data.

**IF03-REQ-009 — Safe default listen scope**  
Without explicit configuration the first-executable IF-03 service shall bind only to a local/loopback interface.

**IF03-REQ-010 — Compatible extension**  
Clients shall be able to ignore unknown response members/event types within API major version `v1`; breaking contract changes shall not silently redefine existing `v1` semantics.

### Relationship to SI-01 SRD

| IDD obligation | SI-01 requirement(s) |
| --- | --- |
| IF03-REQ-001 | SI01-REQ-022, SI01-REQ-030 |
| IF03-REQ-002 | SI01-REQ-031 |
| IF03-REQ-003 | SI01-REQ-010, SI01-REQ-011 |
| IF03-REQ-004 | SI01-REQ-020, SI01-REQ-021, SI01-REQ-022 |
| IF03-REQ-005/006 | SI01-REQ-023 |
| IF03-REQ-007/008 | SI01-REQ-031 |
| IF03-REQ-009 | SI01-REQ-032 |
| IF03-REQ-010 | SI01-REQ-033 |

The SRD references this contract instead of duplicating transport schema details.

### First AP-1 verification case

Verification-case identifiers use `VC-<profile>-<number>` for this baseline.

#### VC-ST1-001 — Query and resynchronise first-executable status

Trace target:

```text
UC-001 / UC-008
  -> SI01-REQ-010/011/020/021/022/023/031/032/033
  -> IF03-REQ-001..010 as applicable
  -> SI-01 status/application boundary from SAD/SDD
  -> VC-ST1-001
```

Procedure:

1. start SI-01 as a separate process with a synthetic configuration containing at least one `TimingSystemInstance`;
2. wait for the configured local IF-03 endpoint to become available;
3. call `GET /api/v1/version` and verify the required identity fields are present;
4. call `GET /api/v1/status` and verify the same build identity and configured instance identity are represented;
5. connect to `/api/v1/events` and verify the first application message is a complete `STATUS_SNAPSHOT`;
6. cause one supported first-executable observable status transition through normal application/process/configuration behaviour and verify a `STATUS_CHANGED` event is received;
7. disconnect the WebSocket client;
8. reconnect and verify a new complete `STATUS_SNAPSHOT` is received before further change events are relied upon;
9. call `/status` once more and verify it is semantically consistent with the latest snapshot;
10. shut the SI-01 process down through the supported controlled shutdown path.

The test driver shall not mutate internal Java objects or inspect private implementation state to obtain the pass/fail result.

### Remote shell scope

The first executable may expose equivalent version/status semantics through a remote-shell adapter as required by the SIP, but AP-1 does **not** introduce a separate system IDD for that transport.

Reason:

- the public software-to-software contract needed by SI-02/SI-03/ST-1 is IF-03;
- remote-shell technology is an implementation/support adapter concern at this stage;
- it must reuse the shared version/status application queries and must not own a separate authoritative model.

If the remote shell later becomes a stable externally consumed system interface, it should receive an appropriate IDD then.

### Deferred interface scope

The following IF-03 capabilities are visible in later use cases/architecture but intentionally outside this AP-1 baseline:

- open/close timing-system commands;
- start procedure;
- RFID power/reinitialisation commands;
- ready-team add/remove;
- manual registration/penalty/revocation;
- registration/history queries;
- reference-data administration;
- backoffice controls;
- detailed diagnostics/support export;
- production authentication/role-based authorisation;
- browser CORS/origin policy beyond later SI-03 needs.

They should be added when their corresponding SIP capability approaches implementation.

### Remaining AP-1 implementation choices

The following are implementation/toolchain selections rather than unresolved interface semantics and may be chosen in the implementation repository/toolchain step:

- concrete Java HTTP/WebSocket library;
- concrete remote-shell library/technology;
- concrete JSON library;
- concrete configuration library;
- exact JDK/Maven/toolchain provisioning.

Changing one of these libraries must not silently change the contract defined above.


---

## Software Verification Plan (SVP)

**Source document:** [50-SVP-software-verification-plan.md](./50-SVP-software-verification-plan.md)

Status: working draft / non-authoritative

This Software Verification Plan defines the initial verification strategy for the software system. It is intentionally introduced early because testability, fault handling, interface boundaries, and Raspberry Pi Zero resource constraints are architectural concerns rather than end-of-project activities.

The SVP applies across software items unless a software-item-specific verification document later adds more detail.

### Verification objectives

Verification should provide evidence that:

- requirements and interface contracts are implemented correctly;
- software-item boundaries remain usable independently;
- domain behaviour is deterministic and unit-testable;
- application behaviour can be tested automatically through its public interface;
- real and stub/proprietary adapters conform to the same public contracts;
- backoffice semantics remain correct across stub, socket and RabbitMQ transports;
- faults and reconnect/recovery paths behave deliberately;
- local operation remains available where required during backoffice/network outages;
- multiple registration assets/sources remain isolated and correctly routed;
- the mandatory original Raspberry Pi Zero target remains viable;
- public framework code can be consumed by external reference and private integration projects;
- generated documentation and build artifacts are reproducible and reviewable.

### Traceability direction

The intended traceability chain is:

```text
system requirement
      |
      +--> system-level IDD requirement/section where applicable
      |
      v
software-item requirement (SRD)
      |
      v
SAD / SDD design element
      |
      v
implementation
      |
      v
verification case + evidence
```

An IDD remains software-system-owned. A software-item requirement references the relevant IDD obligation rather than duplicating the interface definition.

Verification identifiers and exact requirement-reference syntax are still to be defined.

### Verification levels

The `V*` levels describe **what scope is being verified**. Separate `ST-*` profiles below describe concrete automated system-test compositions.

#### V1 — Unit verification

Purpose: verify deterministic application/domain behaviour without external processes or real hardware.

Typical techniques:

- direct/synchronous execution instead of production thread scheduling;
- `FakeClock` rather than wall-clock waiting;
- in-memory repositories;
- fake/stub RFID, CAN, display and backoffice ports;
- deterministic state-machine and filtering tests;
- source-routing and sequence/traceability tests;
- restore/replay tests for local state.

Examples:

- first RFID observation does not automatically create a registration;
- `OPEN` / `CLOSED` transition rules;
- ready-team add/remove projection;
- registration-source sequence allocation;
- registration asset/source routing does not use hard-coded production IDs;
- penalty revocation references the original record;
- full Display V1 state is rebuilt from current ready-team state;
- Display V2 reconnect receives a complete current snapshot;
- status snapshots reflect subsystem state changes.

#### V2 — Component/module verification

Purpose: verify one concrete adapter or component against its contract while controlling the surrounding system.

Examples:

- file backup/restore adapter;
- HTTP/JSON adapter;
- WebSocket status/event stream;
- remote shell adapter;
- simple socket backoffice adapter and framing;
- CAN scanner with simulated CAN traffic;
- public stub devices;
- RabbitMQ adapter against a controlled broker fixture;
- proprietary RFID implementation in its private repository.

#### V3 — Interface verification

Purpose: verify system-level interface contracts/IDDs between software items or external systems.

Expected examples:

- local console returns the same application version/status model as other clients;
- remote shell returns the same version/status semantics;
- Desktop GUI (SI-02) connects to Timing Application (SI-01) across a real network boundary;
- Web Operator Application (SI-03) loads over HTTP and communicates through HTTP/WebSocket;
- backoffice semantic exchange through both socket-test and RabbitMQ adapters;
- Display V2 mDNS discovery and subsequent data/session protocol;
- CAN keypad/display interactions.

These tests should verify externally observable behaviour rather than internal class structure.

#### V4 — Integration/system verification

Purpose: verify multiple real components together with realistic process/network boundaries.

Candidate scenarios:

- SI-01 + test driver through the public application-control interface;
- SI-01 + simple socket backoffice simulator;
- SI-01 + RabbitMQ test broker with multiple configured source consumers/publishers;
- SI-01 + SI-02 over localhost;
- SI-01 on Raspberry Pi + SI-02 on another computer;
- SI-01 + browser/iPad client;
- stub RFID + real domain pipeline + local persistence;
- CAN scanner + keypad + Display V1 stub/real hardware;
- backoffice disconnect/reconnect with local outbox;
- restart/restore followed by synchronisation;
- multiple `TimingSystemInstance` objects, assets and source streams in one runtime;
- full-field simulation using synthetic identities against the same normal backoffice path.

#### V5 — Hardware-in-the-loop verification

Purpose: verify behaviour that cannot be adequately represented by normal automated test doubles.

Likely scope:

- original Raspberry Pi Zero runtime behaviour;
- RFID reader power/boot/reinitialisation;
- real RFID read/filter behaviour;
- real CAN bus/device discovery;
- Display V1 physical behaviour;
- Display V2 network discovery/session behaviour;
- power-cycle/restart recovery where practical.

Hardware tests should be separated from the fast normal pull-request path when they are slow, scarce, or environment-specific.

#### V6 — Operational/resource verification

Purpose: verify that the implementation remains viable on the weakest mandatory target and under representative failure/load conditions.

Measure at least:

- process startup time;
- resident memory / RSS;
- configured/max heap and observed heap behaviour;
- idle CPU usage;
- representative active CPU usage;
- application/thread count;
- timing-system queue backlog/latency under representative input;
- registration-source count and source-scaling overhead;
- socket/RabbitMQ connection count and resource cost where enabled;
- RabbitMQ channel/consumer count and their resource cost;
- HTTP/status response latency;
- backup/write behaviour and SD-card write rate where relevant;
- reconnect/recovery timings;
- long-running stability.

Initial tests establish a baseline. Numeric acceptance budgets should be introduced only when evidence is sufficient; this document deliberately does not invent values before measurement.

### Automated system-test profiles

The `ST-*` profiles provide a progressive set of reusable system-test compositions. A test case can exist at one or more profiles depending on the behaviour being verified.

#### ST-1 — Application behaviour profile

Purpose: fast automated verification of **application behaviour through the public application interface**.

Composition:

```text
System-test driver
      |
      | public application control/status interface
      v
SI-01 real application process
      |
      +-- stub RFID/CAN/display adapters
      +-- in-memory/stub backoffice adapter
      +-- test configuration
```

Characteristics:

- real SI-01 process and composition;
- no direct mutation of domain state from the test;
- test actions enter through the same public application interface intended for GUI/automation clients;
- external devices/backoffice can be deterministic stubs;
- no Docker required;
- suitable for frequent PR execution.

Typical cases:

- start application and query version/status;
- open/close a timing-system instance through the public interface;
- inject stub RFID observations and verify registrations/status;
- add/remove ready-team values and verify display model/state;
- start procedure commands;
- verify several configured system instances/sources behave independently;
- verify backup/restore and application restart at the observable interface level.

This is intended to become the **primary fast system-level regression layer**.

#### ST-2 — Socket loop/network profile

Purpose: add a real process/network communication boundary for the backoffice while remaining lightweight.

Composition:

```text
Application test driver ----> SI-01 public application interface
                               |
                               +-- SocketBackofficeAdapter
                                         ^
                                         |
                                    simple TCP socket
                                         |
                               Backoffice test simulator
```

Characteristics:

- no RabbitMQ/Docker required;
- same source-aware semantic backoffice messages as other transports;
- simple public/synthetic test framing;
- one socket can multiplex several registration sources;
- suitable for reconnect/session/source-routing tests;
- still fast enough for normal automated integration testing.

Typical cases:

- several registration sources over one socket session;
- source identity preserved in both directions;
- socket loss reflected in status while local operation continues;
- reconnect and resume;
- outbound registrations observed by the simulator;
- inbound reference/control data delivered to the correct source/application path;
- full-field multi-instance simulation without broker infrastructure.

#### ST-3 — RabbitMQ integration profile

Purpose: verify the production-shaped broker transport against a real RabbitMQ service.

Composition:

```text
Application test driver ----> SI-01 public application interface
                               |
                               +-- RabbitMqBackofficeAdapter
                                         |
                                         v
                                  RabbitMQ test broker
                                  (Docker Compose)
                                         ^
                                         |
                               broker-side test driver
```

Characteristics:

- disposable real RabbitMQ broker;
- synthetic/public queue/exchange/source topology;
- verifies connection/channel/consumer/publisher behaviour;
- verifies multiple source consumers on shared connection(s);
- exercises broker restart and outbox recovery;
- slower than ST-1/ST-2 and may run as integration CI.

Typical cases:

- one registration source inbound/outbound happy path;
- two or more sources sharing one broker connection;
- independent inbound consumers per source;
- source-specific outbound routing;
- broker outage while local registrations continue;
- pending outbound data retained during outage;
- reconnect restores all source consumers;
- broker restart does not alter committed registration sequence identity;
- malformed/unavailable/misconfigured broker resource handling.

#### ST-4 — Target/full-system profile

Purpose: run representative system tests on target hardware and/or with real external hardware/services.

Possible compositions include:

- SI-01 on original Raspberry Pi Zero with ST-1 application driver;
- Pi Zero + socket simulator to isolate target runtime/network behaviour;
- Pi Zero + RabbitMQ broker on another host;
- Pi Zero + real RFID/CAN/display hardware;
- SI-02/SI-03 clients against the real target application.

ST-4 is generally slower/on-demand and can reuse test scenarios first proven at ST-1/ST-3.

### Raspberry Pi Zero baseline evidence

The original Raspberry Pi Zero / Zero W is a mandatory target for software item 01.

The first representative executable should therefore capture a repeatable baseline on real hardware using the selected Java 8 runtime.

Minimum baseline record:

```text
hardware model / RAM
OS image/version
Java runtime vendor/version
application commit/version
configuration profile
startup time
RSS after startup
RSS after representative workload
heap settings / observed heap use
thread count
idle CPU
representative workload CPU
configured TimingSystemInstance / asset / source counts
socket/RabbitMQ connection counts when enabled
RabbitMQ channel/consumer counts when enabled
version/status request latency
notes / anomalies
```

A later Java 11 evaluation must compare against the same or equivalent workload and hardware rather than only desktop benchmarks.

### RabbitMQ container integration environment

ST-3 uses a disposable real RabbitMQ broker, preferably through Docker Compose in the implementation/reference repository.

The broker fixture must use only synthetic/public test topology and credentials.

A normal test sequence should be automatable as:

```text
start RabbitMQ container
      |
      v
wait for broker health/readiness
      |
      v
start SI-01/reference application with synthetic multi-source configuration
      |
      v
exercise inbound + outbound messaging
      |
      v
stop/restart RabbitMQ
      |
      v
verify connection recovery + source consumer restoration + outbox resume
      |
      v
collect evidence and remove test environment
```

The same basic Compose definition should be usable locally and in GitHub Actions where practical.

Actual production queue names, source IDs, schemas and credentials are not public test data.

### Fault-injection verification

Failures should be verified deliberately rather than waiting for accidental occurrence.

Candidate injected conditions include:

- RFID power unavailable / boot failure / unresponsive reader;
- CAN device disappears;
- non-discoverable keypad remains silent;
- Display V1 reconnect/reset;
- Display V2 network disconnect/reconnect;
- local network loss;
- internet loss with local LAN still available;
- simple socket backoffice disconnect/reconnect;
- RabbitMQ/backoffice connection loss;
- individual registration-source consumer failure while broker remains connected;
- RabbitMQ broker restart;
- delayed or rejected reference-data update;
- file backup write failure;
- corrupt/missing restore data;
- application restart after traceable events;
- queue pressure/overload;
- GUI/client disconnect and stale status.

Stubs/test-control interfaces should inject faults through normal adapter boundaries rather than mutating domain state directly.

### CI execution classes

A likely CI split is:

```text
PR fast checks
  compile
  unit tests
  architecture/dependency checks
  ST-1 application behaviour tests
  selected fast component/interface tests

PR integration
  ST-2 socket loop/network tests
  reference-project consumer tests
  selected fault/reconnect scenarios

merge / selected PR / scheduled integration
  ST-3 RabbitMQ Docker/Compose integration tests
  high-source-count/full-field simulations

scheduled/on-demand
  long-running integration
  performance/resource regression where a suitable target exists

hardware pipeline
  ST-4 Pi Zero / RFID / CAN / display hardware-in-loop
```

The exact boundary between normal PR and merge-time ST-3 execution can be adjusted once runtime is known. Exact workflow names and triggers belong in implementation repositories and the SDE.

### Public/private verification model

The public framework must be verifiable without proprietary source or deployment identities.

The public reference/test project should prove that published Maven artifacts and public contracts work outside the framework reactor through ST-1, ST-2 and a synthetic ST-3 RabbitMQ topology.

Private repositories should reuse the same scenario concepts where possible. A private implementation is successful when it can replace a public stub/default adapter through the supported API/SPI without requiring changes to public framework source.

Production asset names, source IDs, broker mappings, proprietary message schemas and credentials must not be copied into public verification fixtures.

### Generated evidence

Useful evidence may include:

- JUnit/Maven test reports;
- GitHub Actions run links;
- ST-1/ST-2/ST-3 scenario reports;
- integration logs;
- Docker/Compose service logs for integration failures;
- resource-measurement summaries;
- generated architecture/documentation review output;
- hardware-test notes or captured device logs;
- protocol/interface test reports where appropriate.

The active implementation PR should contain or link the detailed evidence for its scope. Long-term plans should only retain durable conclusions/baselines.

### Verification status model

Documents and requirements should eventually support states such as:

```text
not verified
verification planned
verification implemented
verified
failed / evidence not sufficient
verification impacted by change
```

The exact traceability tooling is still open; initially this can remain Markdown + tests + PR evidence.

### Open verification topics

- requirement and verification-case identifier conventions;
- scenario identifier convention across ST-1/ST-4 profiles;
- when numeric Pi Zero budgets become acceptance criteria rather than measured baselines;
- standard test framework/version compatible with Java 8;
- architecture-test tooling compatible with the Java baseline;
- exact public test-driver protocol/API for ST-1 automation;
- exact simple socket framing for ST-2;
- Docker/Compose version/image-pinning conventions for ST-3;
- hardware-runner setup and how ST-4 is triggered;
- coverage expectations and whether line coverage is useful for this project;
- long-running/soak-test duration and acceptance criteria;
- timestamp precision/clock-synchronisation verification method;
- RFID filtering verification data sets;
- RabbitMQ production acknowledgement/reconciliation verification approach;
- how proprietary interface/protocol verification evidence is referenced without exposing private details in public repositories;
- release-level regression criteria.


---

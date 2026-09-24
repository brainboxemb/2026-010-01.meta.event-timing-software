# System use cases

Status: working draft / non-authoritative

This document captures system-level operational use cases that explain how operators, devices, external systems and test tooling use the event-timing software system.

Use cases are intentionally placed between the domain baseline and formal requirements. They describe **desired externally meaningful behaviour and goals**, not implementation details. Later system requirements, IDDs, software-item SRDs and verification cases may reference these use cases.

The public repository uses generic/synthetic identities. Real deployment asset names, external data-source IDs, broker topology and proprietary protocol details remain outside this repository.

## Relationship to other documents

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

## Use-case format

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

## Use-case catalogue

| ID | Name | Primary actor | Goal |
| --- | --- | --- | --- |
| UC-001 | Start and prepare a waypoint system | Operator | Bring one configured waypoint system into a usable operational state. |
| UC-002 | Open a waypoint system | Operator | Start accepting/processing normal timing operation and create the required traceable open event(s). |
| UC-003 | Register a participant through RFID | RFID subsystem | Turn valid filtered/decrypted RFID observations into traceable source-specific registration records. |
| UC-004 | Recover or reinitialise RFID equipment | Operator / system | Restore an RFID device after startup, heartbeat or protocol failure without losing committed timing state. |
| UC-005 | Manage teams to prepare through keypad/operator input | Operator / keypad | Add or remove team numbers from the preparation registry and preserve the change history. |
| UC-006 | Drive a passive display from current system state | Timing application | Keep a passive Display V1 aligned with the authoritative current ready-team/display model. |
| UC-007 | Synchronise a smart display | Smart display | Connect to the advertised service and receive current/synchronised display data without moving domain authority out of SI-01. |
| UC-008 | Operate SI-01 through a desktop GUI | Operator | View status/data and execute permitted commands while SI-01 may run on a remote Raspberry Pi. |
| UC-009 | Operate SI-01 through the browser/iPad application | Operator | Download the web application and use HTTP/WebSocket for status, registration data and operator commands. |
| UC-010 | Synchronise reference data from backoffice | Backoffice | Deliver start times, reserve-tag mappings and other required reference data for local use. |
| UC-011 | Synchronise `UniqueID`-scoped data to backoffice | Timing application / backoffice | Deliver committed source streams while preserving source identity, ordering and recoverability. |
| UC-012 | Continue local operation during backoffice outage | Operator / timing application | Continue required local timing behaviour while external synchronisation is unavailable, retaining data for later recovery. |
| UC-013 | Restart and restore local state | Operator / platform | Restore source sequences, registration state, ready-team/reference state and status after process/device restart. |
| UC-014 | Run multiple waypoint systems in one process | Test/operator tooling | Run several independently addressed waypoint systems and source streams in one SI-01 process. |
| UC-015 | Simulate a complete field toward backoffice | Test tooling | Exercise normal multi-instance/source behaviour without real production hardware or private deployment identities. |
| UC-016 | Replace real devices with controllable stubs | Test tooling | Drive normal application paths with simulated RFID/CAN/display/backoffice components and fault injection. |
| UC-017 | Use an alternative backoffice transport for loop testing | Test tooling / simulator | Exercise source-aware backoffice semantics across a real socket/process boundary without requiring RabbitMQ. |
| UC-018 | Verify production-shaped messaging through RabbitMQ | Test tooling / backoffice adapter | Exercise source-specific consumers/publishing, broker recovery and outbox behaviour against a real disposable broker. |
| UC-019 | Process a test RFID tag | RFID subsystem / operator | Recognise a test-tag identity and apply explicit test-tag behaviour without silently treating it as a normal or reserve participant tag. |

## UC-001 — Start and prepare a waypoint system

**Goal:** bring one configured `Waypoint` into a known usable state.

**Primary actor:** operator or automated startup policy.

**Preconditions:**

- SI-01 has loaded and validated configuration;
- the target instance exists;
- required local state has been restored or an explicit restore fault is visible.

**Main flow:**

1. The actor selects/addresses a waypoint system.
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

## UC-002 — Open a waypoint system

**Goal:** enter normal timing operation in a traceable way.

**Primary actor:** operator.

**Main flow:**

1. The operator issues `open` through an authorised operator interface.
2. The command is translated to the shared application command boundary.
3. The addressed `Waypoint` processes the command through its serialized state boundary.
4. The lifecycle becomes `OPEN` if preconditions are met.
5. The required operational open event is written as a traceable registration-stream entry for the applicable source(s) according to the final requirements.
6. Status/event consumers receive the new lifecycle state.

**Alternative/failure flows:**

- invalid lifecycle transition;
- required persistence cannot commit the open event;
- degraded devices exist but policy still permits open;
- duplicate/open-again command.

## UC-003 — Register a participant through RFID

**Goal:** create a valid traceable registration from RFID observations without treating the first raw observation as automatically authoritative.

**Primary actor:** RFID subsystem.

**Main flow:**

1. The RFID adapter captures raw tag data, antenna identity and observation time.
2. The RFID integration supplies the observation with its configured hardware/antenna context and SI-01 routes it into the addressed `Waypoint`.
3. Proprietary/private decoding/decryption translates the raw tag into a public semantic identity representation while retaining whether the tag is normal, reserve or test-class.
4. Filtering/observation accumulation determines whether the observation is accepted.
5. Reserve-tag resolution is applied when applicable using locally available reference data.
6. A test-tag identity branches to the explicit test-tag behaviour in UC-019 rather than silently continuing as a normal participant registration.
7. The configured producer/data mapping determines the applicable `UniqueID` used for the committed ordered stream.
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

## UC-004 — Recover or reinitialise RFID equipment

**Goal:** allow explicit operator/system recovery of an RFID device while keeping timing-system state and committed registrations intact.

**Primary actor:** operator, supported by health/recovery logic.

**Main flow:**

1. SI-01 detects/reports an RFID startup, heartbeat or protocol problem.
2. The operator sees the exact affected asset/antenna state.
3. The operator requests reinitialisation, reconnect, reset or power-cycle according to supported recovery policy.
4. The adapter performs the hardware/protocol recovery operation.
5. Device state returns through `INITIALISING` to `READY`, or remains in an explicit error state.
6. Existing committed registration/source sequence state is not reset or rewritten by device recovery.

## UC-005 — Manage ready teams through keypad/operator input

**Goal:** maintain the current registry of teams that must prepare at the waypoint/exchange point while keeping keypad/operator add/remove history traceable.

**Primary actor:** keypad or operator client.

**Main flow:**

1. A team-number add/remove action enters through a normal input adapter.
2. SI-01 routes the command to the applicable waypoint system.
3. `PrepareTeamRegistry` records the traceable add/remove mutation and updates its current set.
4. Display state is rebuilt/updated from the authoritative current prepare-team registry.
5. Operator/status clients can observe the resulting state.

The `PrepareTeamRegistry` history is separate from participant/timing `RegistrationRecord` streams.

## UC-006 — Drive a passive display from current system state

**Goal:** ensure Display V1 shows the current authoritative ready-team/display model.

**Primary actor:** SI-01.

**Main flow:**

1. SI-01 derives a current `DisplayModel` from application state.
2. The passive-display adapter translates that model into CAN/device commands.
3. On state change, reconnect or rediscovery, SI-01 actively refreshes the display as required.
4. The display itself does not become authoritative for ready-team/domain state.

## UC-007 — Synchronise a smart display

**Goal:** provide a smarter network display with data/state while SI-01 remains authoritative.

**Primary actor:** smart display.

**Main flow:**

1. SI-01 advertises the configured service through mDNS.
2. The display discovers and connects to SI-01.
3. SI-01 provides a full current snapshot/data set.
4. Subsequent updates are synchronised over the selected network protocol.
5. After reconnect, the display can recover from a fresh authoritative snapshot.

## UC-008 — Operate SI-01 through a desktop GUI

**Goal:** operate/observe a timing application running locally or on another host such as a Raspberry Pi.

**Primary actor:** operator.

**Main flow:**

1. SI-02 connects through the system-defined application-control/status interface.
2. It retrieves current application/instance/subsystem state.
3. The operator performs permitted commands such as open/close/device recovery and later registration-related operations.
4. SI-02 shows command outcome and live/stale/disconnected status explicitly.
5. No authoritative timing state is stored solely in the GUI.

## UC-009 — Operate SI-01 through the browser/iPad application

**Goal:** provide local browser/iPad operation without requiring a separately installed native client.

**Primary actor:** operator.

**Main flow:**

1. The browser loads the compiled React application from SI-01 over HTTP.
2. The application obtains initial state/registration data via HTTP/query endpoints.
3. Live state/registration changes arrive over WebSocket.
4. Operator actions such as open/close/start are submitted through the same shared application semantics as other clients.
5. Disconnection/stale state is visible to the operator.

## UC-010 — Synchronise reference data from backoffice

**Goal:** make required reference data available locally even when later backoffice connectivity is interrupted.

**Primary actor:** backoffice.

**Main flow:**

1. Source-aware inbound backoffice communication receives a reference-data update.
2. The transport adapter translates private/wire representation into public semantic data.
3. SI-01 validates and applies the update.
4. Start times/reserve-tag mappings and related metadata are stored in in-memory repositories.
5. Backup/restore state is updated according to persistence policy.
6. Status exposes version/freshness/health where required.

## UC-011 — Synchronise `UniqueID`-scoped data to backoffice

**Goal:** deliver committed ordered source streams without coupling domain logic to one transport technology.

**Primary actors:** SI-01 and backoffice.

**Main flow:**

1. A source record is committed locally with `(UniqueID, SequenceNumber)` identity.
2. A corresponding outbound item becomes pending in the outbox/synchronisation state.
3. The selected `BackofficeTransportPort` sends the semantic message through its configured transport.
4. RabbitMQ production-shaped transport may map the source to its configured exchange/routing endpoint; a test socket adapter may use a simpler synthetic framing.
5. Successful acknowledgement/reconciliation advances the pending state according to the final protocol.
6. Source ordering and gap detection remain possible at higher levels.

## UC-012 — Continue local operation during backoffice outage

**Goal:** preserve required local timing functionality and traceability while external connectivity is unavailable.

**Primary actor:** operator / SI-01.

**Main flow:**

1. SI-01 detects loss of internet/broker/backoffice connectivity and exposes the appropriate status layer.
2. Local device operation, registration and calculations continue where required local configuration/reference data is available.
3. New committed source records remain locally durable.
4. Outbound items remain pending.
5. After transport recovery, synchronisation resumes without inventing/reusing committed sequence numbers.

## UC-013 — Restart and restore local state

**Goal:** recover a coherent timing application after restart/power interruption.

**Primary actor:** platform/operator.

**Main flow:**

1. SI-01 starts and loads configuration.
2. Source-specific registration files and sequence state are restored/validated.
3. Ready-team/reference/other recoverable state is restored according to the design.
4. The runtime reconstructs configured waypoint systems and configured hardware/data-source adapters.
5. Status reports restore health/errors before normal operation is presented as healthy.
6. Backoffice/outbox recovery resumes independently from local startup.

## UC-014 — Run multiple waypoint systems in one process

**Goal:** host multiple independently addressed waypoint systems while preserving independent lifecycle, state and `UniqueID`-scoped streams.

**Primary actor:** configuration/test/operator tooling.

**Main flow:**

1. Settings describe several independently addressed `Waypoint` objects and their location/waypoint identity mappings.
2. Each instance receives its own logical serialized state boundary.
3. Deployment configuration independently maps physical producer/asset identities to the applicable logical `UniqueID` identities without making those hardware objects children of the `Waypoint` software model.
4. Runtime-wide infrastructure may be shared without sharing mutable instance state.
5. Public interfaces can address each instance explicitly.

## UC-015 — Simulate a complete field toward backoffice

**Goal:** exercise realistic multi-instance/multi-source behaviour from one test application.

**Primary actor:** automated/system test tooling.

**Main flow:**

1. A synthetic configuration creates enough waypoint systems and configured producer/waypoint identity mappings to represent the required test scale.
2. Stub devices inject observations/faults through normal adapter boundaries.
3. SI-01 follows the same queues, `UniqueID`-scoped sequences, persistence and backoffice-port paths as production composition.
4. A backoffice simulator or broker fixture observes all source streams.
5. Tests validate isolation, ordering, recovery and status across the simulated field.

## UC-016 — Replace real devices with controllable stubs

**Goal:** make hardware-dependent application behaviour testable without duplicating business logic.

**Primary actor:** test tooling.

**Main flow:**

1. Composition selects stub adapters through normal public contracts.
2. Test control injects reads, device discovery, disconnects, failures or recoveries through the adapter surface.
3. The application processes those events through normal queues/domain handlers.
4. Tests observe behaviour only through supported state/interfaces/evidence points.

## UC-017 — Use an alternative backoffice transport for loop testing

**Goal:** test real process/network communication and `UniqueID`-scoped stream routing without RabbitMQ.

**Primary actors:** backoffice simulator and test tooling.

**Main flow:**

1. SI-01 is configured with a simple socket-based `BackofficeTransportPort` implementation.
2. A simulator connects over a real TCP/socket boundary.
3. Generic public `BackofficeEnvelope` messages are framed with explicit `UniqueID` context.
4. Several `UniqueID`-scoped streams can share the connection.
5. Disconnect/reconnect and malformed-message behaviour can be injected cheaply.
6. SI-01's domain/outbox/stream behaviour remains identical to the RabbitMQ composition.

This use case is intentionally protocol-neutral and does not reproduce private production RabbitMQ message schemas.

## UC-018 — Verify production-shaped messaging through RabbitMQ

**Goal:** verify broker/client lifecycle and source-specific messaging using a real disposable broker.

**Primary actors:** automated test tooling and SI-01 RabbitMQ adapter.

**Main flow:**

1. A Docker/Compose test environment starts a RabbitMQ broker with synthetic topology/credentials.
2. SI-01 establishes the configured broker connection(s).
3. Each configured `UniqueID`-scoped inbound stream establishes its applicable queue consumer/channel.
4. Outbound messages use `UniqueID`-specific routing configuration.
5. Tests exercise inbound/outbound behaviour and `UniqueID` isolation.
6. The broker is stopped/restarted to exercise reconnect, consumer restoration and pending-outbox resume.

Production names, source IDs, schemas and credentials remain outside the public fixture.

## UC-019 — Process a test RFID tag

**Goal:** recognise a test-tag observation and apply deliberate test-specific behaviour without allowing the tag to masquerade as a normal or reserve participant tag.

**Primary actors:** RFID subsystem and operator.

**Preconditions:**

- the tag has been decoded sufficiently to identify its semantic tag class;
- the configured waypoint system can identify that the tag is a test tag.

**Main flow:**

1. The RFID adapter captures the observation through the same normal ingress path used for other tags.
2. Decoding preserves the semantic tag class as `test` rather than flattening the identity to a normal participant identity.
3. Any common validation/filtering that also applies to test tags is performed according to the final requirements.
4. SI-01 applies the configured/test-tag policy instead of the normal or reserve-tag path.
5. The resulting action and operator-visible state remain explicitly distinguishable as test-tag behaviour.
6. If any record is persisted or synchronised, its semantics remain distinguishable from a normal participant registration.

**Behaviour still to define:**

- whether a test tag creates a registration-stream record at all;
- whether it uses a dedicated record type and/or `UniqueID` routing rule;
- whether it may affect elapsed-time/ranking/other derived calculations;
- whether it is synchronised to backoffice, and if so with what semantics;
- in which lifecycle states a test tag is accepted;
- what an operator sees when a test tag is detected/accepted/rejected;
- whether test-tag handling requires an explicit enable/configuration mode.

This use case is about a real semantic RFID tag class. It is separate from UC-015/016 software simulation and stub-device testing.

## Cross-cutting alternative/failure scenarios

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

## Traceability direction

When requirements are promoted, prefer explicit references such as:

```text
UC-003
  -> SYS-REG-xxx
  -> IDD-... where external behaviour applies
  -> SI01-SRD-...
  -> SDD registration/RFID/`UniqueID`-routing elements
  -> VC-... / ST-1, ST-2, ST-3, HIL evidence
```

This allows one operational goal to remain visible even when implementation responsibilities are distributed over several software items/components.

## Open use-case questions

- Which use cases are required during normal operation versus maintenance/service-only operation?
- What exact preconditions are required before a waypoint system may be opened?
- Which subsystem failures should block `OPEN`, and which should only mark the instance degraded?
- Which operational events besides `OPEN` must become registration-stream records?
- Can a waypoint system change location during one operational session, or is `LocationId` fixed until the waypoint is closed/reconfigured?
- What operator roles/authorisation distinctions will exist for local, desktop and web clients?
- Which reference-data updates are automatically accepted versus requiring operator acknowledgement?
- What exact local behaviour is required if reference data is stale but backoffice is unavailable?
- Which configured mapping cases can intentionally create records in multiple virtual/`UniqueID`-scoped streams from one accepted RFID event?
- Which UC-019 test-tag behaviours are part of normal operational verification versus maintenance/service-only behaviour?

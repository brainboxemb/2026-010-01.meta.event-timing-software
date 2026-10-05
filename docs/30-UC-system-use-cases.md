# System use cases

Status: working draft / non-authoritative

## Purpose

This document captures system-level operational use cases that explain how operators, devices, external systems and test tooling use the event-timing software system.

Use cases describe **desired externally meaningful behaviour and goals**, not implementation details.

The public repository uses generic/synthetic identities. Real deployment asset names, external data-source IDs, broker topology and proprietary protocol details remain outside this repository.

## Terms and abbreviations

- **UC** — Use Case
- **SSSD** — Software System Specification Document
- **ISD** — Interface Specification Document
- **SI** — Software Item


## Relationship to other documents

System use cases are part of the software-system specification/design family. They express behaviour of the **software system as a whole** before that behaviour is decomposed across software items.

Relevant parent-system/external inputs are registered in `20-EXT-external-system-inputs.md`. Together with the domain baseline they can shape these system use cases and the SSSD.

```text
03 Domain baseline -----------+
                                 |
20-EXT External/parent inputs ----+--> 30-UC System use cases
                                              |
                                              v
                                         31-SSSD
                                              |
                                  allocates items/interfaces
                                              |
                              +---------------+---------------+
                              |                               |
                              v                               v
                    32-<IF> system ISDs             optional software-item UC
                              |                               |
                              +---------------+---------------+
                                              |
                                              v
                                         41-<SI>-SSD
                                              |
                                              v
                                         43-<SI>-SDD
```

A software-item use case is optional. It is appropriate when a system use case has been allocated across software items and describing one item's actor/goal behaviour separately makes the subsequent SSD clearer. It should reference the originating system use case and must not merely copy it.

A use case is not a test case. One use case may be realised by several requirements and verified by several unit, interface, system, fault-injection and hardware tests.

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

The catalogue is grouped by operational purpose for readability. Use-case IDs
remain stable traceability identifiers; their numeric order does not define the
reading order or implementation sequence.

### Normal operation

| ID | Name | Primary actor | Goal |
| --- | --- | --- | --- |
| UC-001 | Connect to a registration system | Operator | Connect to a known registration system and view its current operational state. |
| UC-002 | Configure, open and close a registration point | Operator | Set the operational location, open registration, and close it again without changing location while open. |
| UC-003 | Register a participant through RFID | RFID subsystem | Turn valid filtered/decrypted RFID observations into traceable source-specific registration records. |
| UC-004 | Recover or reinitialise RFID equipment | Operator / system | Restore an RFID device after startup, heartbeat or protocol failure without losing committed timing state. |
| UC-005 | Manage teams to prepare through keypad/operator input | Operator / keypad | Add or remove team numbers from the next-up team state and preserve the change history. |
| UC-006 | Drive a passive CAN display from current system state | Timing application | Keep DisplayRev1Can aligned with the current ready-team/display model. |
| UC-007 | Synchronise a smart display | Smart display | Connect to the advertised service and receive current/synchronised display data while SI-01 remains the source of that state. |
| UC-008 | Operate SI-01 through the planned desktop GUI | Operator | View status/data and execute permitted commands through the API. |

### System, backoffice and recovery

| ID | Name | Primary actor | Goal |
| --- | --- | --- | --- |
| UC-010 | Synchronise reference data from backoffice | Backoffice | Deliver start times, participant/reference mappings and other required reference data for local use. |
| UC-011 | Synchronise `TimingNodeId`-scoped data to backoffice | Timing application / backoffice | Deliver committed source streams while preserving source identity, ordering and recoverability. |
| UC-012 | Continue local operation during backoffice outage | Operator / timing application | Continue required local timing behaviour while external synchronisation is unavailable, retaining data for later recovery. |
| UC-013 | Restart and restore local state | Operator / platform | Restore source sequences, registration state, ready-team/reference state and status after process/device restart. |
| UC-014 | Run multiple TimingNodes in one process | Test/operator tooling | Run several independently addressed TimingNodes and source streams in one SI-01 process. |
| UC-020 | Diagnose degraded TimingNode startup | Operator / platform | Keep the application diagnosable when one TimingNode cannot restore its local state. |

:::{uc} Diagnose degraded TimingNode startup  
:id: UC-020

**Goal:** keep SI-01 reachable and diagnosable when one configured TimingNode cannot
complete local state recovery.

**Primary actor:** operator / platform.

**Preconditions:**

- application-level configuration is valid enough to construct the runtime and
  diagnostic presentation interfaces;
- one configured TimingNode encounters a contained startup/recovery failure.

**Main flow:**

1. SI-01 starts and validates application-level configuration.
2. A TimingNode detects that its recoverable local state cannot be restored safely,
   for example because persisted TimingData belongs to another TimingNodeId.
3. SI-01 keeps that TimingNode out of normal operation and marks it `ERROR`.
4. The application continues starting/running its diagnostic presentation interfaces.
5. Status identifies the affected TimingNode and exposes a machine-readable problem
   plus a human-readable diagnostic summary.
6. The operator can query status through the supported local/remote interfaces and
   determine why the TimingNode did not become operational.
7. Normal state-changing and registration operations for the errored TimingNode are
   rejected explicitly.
8. In a multi-TimingNode composition, independently healthy TimingNodes remain
   available unless an application-wide failure prevents safe operation.
9. The application can still be shut down through the supported controlled path.

**Alternative/failure flows:**

- invalid application-wide configuration or failure of mandatory application-wide
  infrastructure may still prevent the process from providing diagnostic interfaces;
- a later recovery/reinitialisation mechanism may move the TimingNode out of `ERROR`,
  but that mechanism is outside this initial containment use case.

**Observable result:** a node-local recovery problem does not turn into an opaque
process crash; the running application exposes the failed TimingNode and its diagnostic
problem through normal status interfaces.

:::

### Engineering, simulation and verification

| ID | Name | Primary actor | Goal |
| --- | --- | --- | --- |
| UC-009 | Exercise the registration system through the Engineering Client | Test/developer | Inspect and exercise supported public behaviour without becoming another source of domain state. |
| UC-015 | Simulate a complete field toward backoffice | Test tooling | Exercise normal multi-TimingNode/source behaviour without real production hardware or private deployment identities. |
| UC-016 | Replace real devices with controllable stubs | Test tooling | Drive normal application paths with simulated RFID/CAN/display/backoffice components and fault injection. |
| UC-017 | Use an alternative backoffice transport for loop testing | Test tooling / simulator | Exercise source-aware backoffice semantics across a real socket/process boundary without requiring RabbitMQ. |
| UC-018 | Verify production-shaped messaging through RabbitMQ | Test tooling / backoffice adapter | Exercise source-specific consumers/publishing, broker recovery and outbox behaviour against a real disposable broker. |
| UC-019 | Handle provider-specific input classification | Input subsystem / operator | Preserve a provider-declared semantic input classification when public processing policy needs it, without exposing provider-private encoding details. |

### Normal operation

:::{uc} Connect to a registration system  
:id: UC-001

**Goal:** allow an operator application to connect to a known registration
system and show its current operational state.

**Primary actor:** operator.

**Preconditions:**

- the registration system is running and reachable;
- the operator application knows the address of the registration system.

**Main flow:**

1. The operator application connects to the registration system.
2. The application requests the current operational state.
3. The application shows the system identity, current `LocationId` if configured, and whether the registration point is `OPEN` or `CLOSED`.
4. The operator can continue with the operations permitted for the reported state.

The operator does not need to select or understand an internal `TimingNode`
before using the registration system. The public state may expose the configured
TimingNode identity so the connected source can be identified, but the domain
structure remains an implementation/interface concern rather than an operator
navigation concept.

**Alternative/failure flows:**

- the registration system cannot be reached;
- the connection is lost;
- the current state cannot be retrieved.

**Observable result:** the operator can identify the connected registration
system and see its current location and open/closed state.

:::

:::{uc} Configure, open and close a registration point  
:id: UC-002

**Goal:** let an operator prepare a registration point for one location, open it
for registrations, and close it again.

**Primary actor:** operator.

**Preconditions:**

- the operator application is connected to the registration system;
- the current registration state is available.

**Main flow:**

1. While the registration point is `CLOSED`, the operator selects the operational `LocationId` for the next open.
2. The operator requests `OPEN` for that selected location as one operation.
3. The registration system validates the requested location and other required open conditions.
4. When accepted, the registration system applies the LocationId and changes the registration point to `OPEN` as one ordered operation.
5. The application shows the registration point as `OPEN` with that location.
6. Registrations may now be accepted for that location.
7. The operator requests `CLOSE`.
8. The application shows the registration point as `CLOSED`.
9. The last selected location may remain visible after close; another location can be selected for a later OPEN request.

The operational location is fixed while registration is `OPEN`. A normal operator
OPEN action therefore carries the intended LocationId instead of depending on a
separately ordered location command immediately before OPEN.

Whether open/close actions are themselves represented in TimingData or sent
upstream is a later interface/protocol decision.

**Alternative/failure flows:**

- `OPEN` is requested with an invalid operational location;
- a location change is requested while registration is `OPEN`;
- another required open condition is not satisfied;
- the command cannot be completed or its resulting state cannot be confirmed.

**Observable result:** the operator application shows the selected location and
the resulting `OPEN` or `CLOSED` state explicitly.

:::

:::{uc} Register a participant through RFID  
:id: UC-003

**Goal:** turn an accepted participant observation into one traceable registration
for the location that is currently open.

**Primary actor:** RFID subsystem.

**Preconditions:**

- registration is `OPEN`;
- a valid operational location is active.

**Main flow:**

1. The RFID subsystem observes a participant tag and captures the observation time.
2. Tag interpretation and observation filtering determine whether the observation represents an accepted participant registration.
3. An accepted semantic registration is submitted to the registration point.
4. The registration system captures its own source identity and the active `LocationId`.
5. It assigns the next source sequence and creates the committed TimingData registration.
6. The registration retains the active location and accepted observation time even if the registration point is later closed or configured for another location.
7. The committed registration becomes available in registration history/current state and as a live update where supported.
8. Outbound synchronisation may consume the committed registration independently when that capability is implemented.


**Alternative/failure flows:**

- the observation is invalid or not accepted by filtering;
- an accepted-registration request arrives while registration is `CLOSED`;
- the semantic participant identity is invalid;
- the registration cannot be committed;
- outbound/backoffice synchronisation is unavailable after local commit.

**Observable result:** one accepted participant observation produces one committed
registration associated with the source and location that were active at the
time of acceptance.

:::

:::{uc} Recover or reinitialise RFID equipment  
:id: UC-004

**Goal:** allow explicit operator/system recovery of an RFID device while keeping timing-system state and committed registrations intact.

**Primary actor:** operator, supported by health/recovery logic.

**Main flow:**

1. SI-01 detects/reports an RFID startup, heartbeat or protocol problem.
2. The operator sees the exact affected asset/antenna state.
3. The operator requests reinitialisation, reconnect, reset or power-cycle according to supported recovery policy.
4. The adapter performs the hardware/protocol recovery operation.
5. Device state returns through `INITIALISING` to `READY`, or remains in an explicit error state.
6. Existing committed registration/source sequence state is not reset or rewritten by device recovery.

:::

:::{uc} Manage ready teams through keypad/operator input  
:id: UC-005

**Goal:** maintain the current list of teams that must prepare at the timing node/exchange point while keeping keypad/operator add/remove history traceable.

**Primary actor:** keypad or operator client.

**Main flow:**

1. A team-number add/remove action enters through a normal input adapter.
2. SI-01 routes the command to the applicable TimingNode.
3. `NextUpTeams` records the traceable add/remove mutation and updates its current set.
4. Display state is rebuilt/updated from the current prepare-team state.
5. Operator/status clients can observe the resulting state.

Any `NextUpTeams` change history required by the promoted requirements is separate from participant/timing `TimingData` streams.

:::

:::{uc} Drive a passive CAN display from current system state  
:id: UC-006

**Goal:** ensure the passive DisplayRev1Can shows the current ready-team/display model.

**Primary actor:** SI-01.

**Main flow:**

1. `CanNetworkController` discovers and monitors the configured CAN devices.
2. SI-01 derives a current `DisplayModel` from application state.
3. DisplayRev1Can-specific handling translates that model into CAN/device commands.
4. On state change or CAN-device rediscovery, SI-01 actively refreshes the display as required.
5. The passive display itself does not own ready-team/domain state.

:::

:::{uc} Provide data to a smart network display  
:id: UC-007

**Goal:** expose current timing/status/reference data so a smart display can render and synchronise itself without SI-01 owning its presentation logic.

**Primary actor:** smart display.

**Main flow:**

1. `WifiNetworkController` starts the configured local data service and advertises that service through mDNS.
2. DisplayRev2Wifi discovers the advertised SI-01 service and initiates the connection.
3. SI-01 provides current timing/status/reference data through the selected network interface.
4. DisplayRev2Wifi owns its local rendering and synchronisation state and consumes the data it needs.
5. If the connection is lost, DisplayRev2Wifi is responsible for rediscovery/reconnect and can rebuild its local view from current SI-01 data.

SI-01 does not drive DisplayRev2Wifi through the passive-display `DisplayModel`. Exact mDNS service naming and the application protocol carried by the connection remain interface-design decisions.

:::

:::{uc} Operate SI-01 through a desktop GUI  
:id: UC-008

**Goal:** operate/observe a timing application through the
API.

**Primary actor:** operator.

**Main flow:**

1. SI-02 connects through the system-defined application-control/status interface.
2. It retrieves current application/instance/subsystem state.
3. The operator performs permitted commands such as open/close/device recovery and later registration-related operations.
4. SI-02 shows command outcome and live/stale/disconnected status explicitly.
5. Timing state remains in SI-01 rather than being stored only in the GUI.
6. After event-stream reconnect, the GUI rebuilds its view from current SI-01 state instead of presenting an old cache as live.

**Alternative/failure flows:** an unknown or no-longer-present target, rejected
lifecycle transition, unsupported command, lost connection with unknown command
outcome, or stale cached state must all remain explicit to the operator.

The Development Client may inspect the same public state semantics as engineering
tooling, but it is not SI-02 and does not own SI-02 operator-interface requirements.

:::

### System, backoffice and recovery

:::{uc} Synchronise reference data from backoffice  
:id: UC-010

**Goal:** make required reference data available locally even when later backoffice connectivity is interrupted.

**Primary actor:** backoffice.

**Main flow:**

1. Source-aware inbound backoffice communication receives a reference-data update.
2. The transport adapter translates private/wire representation into public semantic data.
3. SI-01 validates and applies the update.
4. Start times and participant/team/tag reference data are applied to their owning domain state (`StageStartTimes` and `RaceData`) for the addressed TimingNode, without silently updating another target.
5. SI-01 makes accepted/rejected update outcomes and current reference state observable through the public semantics required by the slice.
6. Backup/restore state is updated according to later persistence policy; status exposes freshness/health where required.

**Alternative/failure flows:** unknown target, invalid or conflicting reference
update, or unavailable upstream transport. Message submission alone must not
be presented as proof that the target's reference state changed.

:::

:::{uc} Synchronise TimingNodeId-scoped data to backoffice  
:id: UC-011

**Goal:** deliver committed ordered source streams without coupling domain logic to one transport technology.

**Primary actors:** SI-01 and backoffice.

**Main flow:**

1. A committed TimingData record contains the source `TimingNodeId`, the `LocationId` active when that record was accepted, and its source sequence identity.
2. A corresponding outbound item becomes pending in the outbox/synchronisation state when that capability is implemented.
3. `UpstreamProtocol` represents the semantic message and `UpstreamGateway` carries it through the configured connector.
4. A production connector such as RabbitMQ may later map that semantic message to its transport.
5. Successful acknowledgement/reconciliation advances pending state according to the final protocol.
6. Source ordering and gap detection remain possible at higher levels.

**First-registration slice:** D03 defines the identity and outbound semantic
representation needed for committed registration TimingData. The exact
`TimingNodeId`/`LocationId` wire types and validation belong to the
TimingData/ISD contract. Real RabbitMQ delivery, durable outbox/restart,
acknowledgement/reconciliation and inbound reference-data simulation are later
increments.

:::

:::{uc} Continue local operation during backoffice outage  
:id: UC-012

**Goal:** preserve required local timing functionality and traceability while external connectivity is unavailable.

**Primary actor:** operator / SI-01.

**Main flow:**

1. SI-01 detects loss of internet/broker/backoffice connectivity and exposes the appropriate status layer.
2. Local device operation, registration and calculations continue where required local configuration/reference data is available.
3. New committed source records remain locally durable.
4. Outbound items remain pending.
5. After transport recovery, synchronisation resumes without inventing/reusing committed sequence numbers.

:::

:::{uc} Restart and restore local state  
:id: UC-013

**Goal:** recover a coherent timing application after restart/power interruption.

**Primary actor:** platform/operator.

**Main flow:**

1. SI-01 starts and loads configuration.
2. Source-specific registration files and sequence state are restored/validated.
3. Ready-team/reference/other recoverable state is restored according to the design.
4. The runtime reconstructs configured TimingNodes and configured hardware/data-source adapters.
5. Status reports restore health/errors before normal operation is presented as healthy.
6. Backoffice/outbox recovery resumes independently from local startup.

:::

:::{uc} Run multiple TimingNodes in one process  
:id: UC-014

**Goal:** host multiple independently addressed TimingNodes
while preserving independent lifecycle, state and
`TimingNodeId`-scoped streams.

**Primary actor:** configuration/test/operator tooling.

**Main flow:**

1. Settings describe several independently addressed `TimingNode` objects and their location/timing node identity mappings.
2. Each instance receives its own logical serialized state boundary.
3. Deployment configuration routes each producer/asset/antenna origin to one or more applicable `TimingNodeId` targets without making those hardware objects children of the `TimingNode` software model.
4. Runtime-wide infrastructure may be shared without sharing mutable instance state.
5. Public interfaces can address each instance explicitly.
6. An engineering query, change or synthetic upstream input for one TimingNode
   identifies its target and does not accidentally change another node's state.

**Observable result:** two synthetic TimingNodes have separately inspectable
lifecycle, reference/next-up state and independently ordered TimingData. Any
intentional fan-out from one observation to several streams is a separately
specified mapping rule, not accidental cross-instance sharing.

:::

### Engineering, simulation and verification

:::{uc} Exercise the registration system through the Engineering Client  
:id: UC-009

**Goal:** provide one engineering application for inspecting and exercising the
public registration-system behaviour during development and integration.

**Primary actor:** test/developer.

**Preconditions:** the registration system exposes the relevant public interfaces,
or the client can make their unavailability visible. Optional engineering controls
require an explicitly advertised **supported and enabled** capability.

**Main flow:**

1. The Engineering Client connects to the registration system through its public interfaces.
2. It shows build/version identity, connection state, the configured source identity, current `LocationId` if any, and `OPEN`/`CLOSED` state.
3. While registration is `CLOSED`, the developer may set or change the operational location through the public command boundary.
4. The developer may request `OPEN` and `CLOSE`; invalid lifecycle/location combinations remain explicit.
5. When direct-registration simulation is supported and enabled, the developer may submit an already-accepted semantic participant registration, with a deterministic observation time when supported.
6. The registration system applies the same registration operation used after normal antenna/filtering acceptance and supplies its own source identity, active location and next source sequence.
7. The client shows the command outcome separately from the resulting TimingData/history and live update.
8. On disconnect the client marks cached information stale. After reconnect it rebuilds current state and registration data before treating subsequent updates as live.
9. The Engineering Client remains engineering tooling and does not become another owner of registration/domain state.

**Alternative/failure flows:**

- a required public interface is unavailable or the live update connection is lost;
- `OPEN` is requested without a valid location;
- a location change is requested while registration is `OPEN`;
- direct registration is requested while registration is `CLOSED`;
- the engineering capability is unsupported/disabled or semantic input is invalid;
- a command was submitted but its resulting state cannot yet be confirmed after connection loss.

**Observable result:** the Engineering Client can demonstrate
`location -> open -> accepted registration -> observable TimingData -> close`
through public boundaries without RFID hardware, filtering or a real backoffice.

A separate lightweight browser test client is not part of this slice. Broader
upstream/reference-data simulation is deferred to a later increment.

:::

:::{uc} Simulate a complete field toward backoffice  
:id: UC-015

**Goal:** exercise realistic multi-TimingNode/multi-source behaviour from one test application.

**Primary actor:** automated/system test tooling.

**Main flow:**

1. A synthetic configuration creates enough TimingNodes and configured producer/timing node identity mappings to represent the required test scale.
2. Stub devices inject observations/faults through normal adapter boundaries.
3. SI-01 follows the same queues, `TimingNodeId`-scoped sequences, persistence and backoffice-port paths as production composition.
4. A backoffice simulator or broker fixture observes all source streams.
5. Tests validate isolation, ordering, recovery and status across the simulated field.

:::

:::{uc} Replace real devices with controllable stubs  
:id: UC-016

**Goal:** make hardware-dependent application behaviour testable without duplicating business logic.

**Primary actor:** test tooling.

**Main flow:**

1. Composition selects stub adapters through normal public contracts.
2. Test control injects reads, device discovery, disconnects, failures or recoveries through the adapter surface.
3. The application processes those events through normal queues/domain handlers.
4. Tests observe behaviour only through supported state/interfaces/evidence points.

:::

:::{uc} Use an alternative backoffice transport for loop testing  
:id: UC-017

**Goal:** test real process/network communication and `TimingNodeId`-scoped stream routing without RabbitMQ.

**Primary actors:** backoffice simulator and test tooling.

**Main flow:**

1. SI-01 is configured with a simple socket-based `BackofficeTransportPort` implementation.
2. A simulator connects over a real TCP/socket boundary.
3. Generic public `BackofficeEnvelope` messages are framed with explicit `TimingNodeId` context.
4. Several `TimingNodeId`-scoped streams can share the connection.
5. Disconnect/reconnect and malformed-message behaviour can be injected cheaply.
6. SI-01's domain/outbox/stream behaviour remains identical to the RabbitMQ composition.

This use case is intentionally protocol-neutral and does not reproduce private production RabbitMQ message schemas.

:::

:::{uc} Verify production-shaped messaging through RabbitMQ  
:id: UC-018

**Goal:** verify broker/client lifecycle and source-specific messaging using a real disposable broker.

**Primary actors:** automated test tooling and SI-01 RabbitMQ adapter.

**Main flow:**

1. A Docker/Compose test environment starts a RabbitMQ broker with synthetic topology/credentials.
2. SI-01 establishes the configured broker connection(s).
3. Each configured `TimingNodeId`-scoped inbound stream establishes its applicable queue consumer/channel.
4. Outbound messages use `TimingNodeId`-specific routing configuration.
5. Tests exercise inbound/outbound behaviour and `TimingNodeId` isolation.
6. The broker is stopped/restarted to exercise reconnect, consumer restoration and pending-outbox resume.

Production names, source IDs, schemas and credentials remain outside the public fixture.

:::

:::{uc} Handle provider-specific input classification  
:id: UC-019

**Goal:** preserve a provider-declared semantic input classification when the
public application contract needs distinct processing, without publishing
provider-private source encoding or mapping rules.

**Primary actors:** input subsystem and operator.

**Preconditions:**

- the selected provider has decoded the private/source representation;
- any semantic classification exposed to the application is part of that
  provider's public contract.

**Main flow:**

1. The input adapter receives a decoded semantic observation from the selected provider.
2. Provider-private codes remain behind the provider boundary.
3. SI-01 preserves any public semantic classification required by application policy.
4. The normal TimingNode path validates and processes the resulting semantic input.
5. Any committed TimingData record uses only the public canonical TimingData fields.

**Behaviour still to define:**

- which provider-declared semantic classifications, if any, require distinct public application behaviour;
- which lifecycle/configuration policies apply to such classifications;
- what operator-visible diagnostics are required.

Concrete production encodings, private mapping tables and deployment-specific
categories are outside this public use case.

:::

## Cross-cutting alternative/failure scenarios

The following scenarios should be associated with applicable use cases rather than becoming isolated implementation details:

- RFID power/boot/heartbeat failure;
- invalid/decryption/filtering failure;
- missing/stale reference data;
- source-specific input rejected by the selected provider/policy;
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
- GUI/test-client disconnect/stale state;
- socket transport disconnect/reconnect;
- RabbitMQ broker/channel/consumer recovery.

## Traceability direction

When requirements are promoted, prefer explicit references such as:

```text
UC-003
  -> SYS-REG-xxx
  -> ISD-... where external behaviour applies
  -> SI01-REQ-...
  -> SDD registration/RFID/`TimingNodeId`-routing elements
  -> VC-... / ST-1, ST-2, ST-3, HIL evidence
```

This allows one operational goal to remain visible even when implementation responsibilities are distributed over several software items/components.

## Open use-case questions

- Which use cases are required during normal operation versus maintenance/service-only operation?
- What exact preconditions are required before a TimingNode may be opened?
- Which subsystem failures should block `OPEN`, and which should only mark the instance degraded?
- Which operational events besides `OPEN` must become registration-stream records?
- What operator roles/authorisation distinctions will exist for local, desktop and web clients?
- Which reference-data updates are automatically accepted versus requiring operator acknowledgement?
- What exact local behaviour is required if reference data is stale but backoffice is unavailable?
- Which configured mapping cases can intentionally create records in multiple virtual/`TimingNodeId`-scoped streams from one accepted RFID event?

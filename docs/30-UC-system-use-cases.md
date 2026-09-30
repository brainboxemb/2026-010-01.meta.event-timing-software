# System use cases

Status: working draft / non-authoritative

This document captures system-level operational use cases that explain how operators, devices, external systems and test tooling use the event-timing software system.

Use cases are intentionally placed between the domain baseline and formal requirements. They describe **desired externally meaningful behaviour and goals**, not implementation details. Later system requirements, IDDs, software-item SSDs and verification cases may reference these use cases.

The public repository uses generic/synthetic identities. Real deployment asset names, external data-source IDs, broker topology and proprietary protocol details remain outside this repository.

## Relationship to other documents

System use cases are part of the software-system specification/design family. They express behaviour of the **software system as a whole** before that behaviour is decomposed across software items.

Relevant parent-system/external inputs are registered in `20-EXT-external-system-inputs.md`. Together with the domain baseline they can shape these system use cases and the SSSD.

```text
00-04 Domain baseline -----------+
                                 |
20-01 External/parent inputs ----+--> 30-UC System use cases
                                              |
                                              v
                                         31-SSSD
                                              |
                                  allocates items/interfaces
                                              |
                              +---------------+---------------+
                              |                               |
                              v                               v
                    32-<IF> system IDDs             optional software-item UC
                              |                               |
                              +---------------+---------------+
                                              |
                                              v
                                         40-<N>-SSD
                                              |
                                              v
                                         41-<N>-SDD
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

| ID | Name | Primary actor | Goal |
| --- | --- | --- | --- |
| UC-001 | Start and prepare a TimingNode | Operator | Bring one configured TimingNode into a usable operational state. |
| UC-002 | Open and close a TimingNode | Operator | Control the TimingNode operational session while keeping its active location fixed. |
| UC-003 | Register a participant through RFID | RFID subsystem | Turn valid filtered/decrypted RFID observations into traceable source-specific registration records. |
| UC-004 | Recover or reinitialise RFID equipment | Operator / system | Restore an RFID device after startup, heartbeat or protocol failure without losing committed timing state. |
| UC-005 | Manage teams to prepare through keypad/operator input | Operator / keypad | Add or remove team numbers from the next-up team state and preserve the change history. |
| UC-006 | Drive a passive CAN display from current system state | Timing application | Keep DisplayRev1Can aligned with the current ready-team/display model. |
| UC-007 | Synchronise a smart display | Smart display | Connect to the advertised service and receive current/synchronised display data while SI-01 remains the source of that state. |
| UC-008 | Operate SI-01 through the planned desktop GUI | Operator | View status/data and execute permitted commands through the API. |
| UC-009 | Exercise SI-01 through the Engineering Client | Test/developer | Inspect and exercise supported public interfaces without becoming another source of domain state. |
| UC-010 | Synchronise reference data from backoffice | Backoffice | Deliver start times, reserve-tag mappings and other required reference data for local use. |
| UC-011 | Synchronise `TimingNodeId`-scoped data to backoffice | Timing application / backoffice | Deliver committed source streams while preserving source identity, ordering and recoverability. |
| UC-012 | Continue local operation during backoffice outage | Operator / timing application | Continue required local timing behaviour while external synchronisation is unavailable, retaining data for later recovery. |
| UC-013 | Restart and restore local state | Operator / platform | Restore source sequences, registration state, ready-team/reference state and status after process/device restart. |
| UC-014 | Run multiple TimingNodes in one process | Test/operator tooling | Run several independently addressed TimingNodes and source streams in one SI-01 process. |
| UC-015 | Simulate a complete field toward backoffice | Test tooling | Exercise normal multi-TimingNode/source behaviour without real production hardware or private deployment identities. |
| UC-016 | Replace real devices with controllable stubs | Test tooling | Drive normal application paths with simulated RFID/CAN/display/backoffice components and fault injection. |
| UC-017 | Use an alternative backoffice transport for loop testing | Test tooling / simulator | Exercise source-aware backoffice semantics across a real socket/process boundary without requiring RabbitMQ. |
| UC-018 | Verify production-shaped messaging through RabbitMQ | Test tooling / backoffice adapter | Exercise source-specific consumers/publishing, broker recovery and outbox behaviour against a real disposable broker. |
| UC-019 | Process a test RFID tag | RFID subsystem / operator | Recognise a test-tag identity and apply explicit test-tag behaviour without silently treating it as a normal or reserve participant tag. |

```{uc} Start and prepare a TimingNode
:id: UC-001

**Goal:** bring one configured `TimingNode` into a known usable state.

**Primary actor:** operator or automated startup policy.

**Preconditions:**

- SI-01 has loaded and validated configuration;
- the target instance exists with its configured, non-empty `TimingNodeId`;
- required local state has been restored or an explicit restore fault is visible.

**Main flow:**

1. The actor selects/addresses a TimingNode by its configured identity.
2. SI-01 reports current instance and subsystem status, including whether a `LocationId` is currently assigned.
3. While the TimingNode is `CLOSED`, the actor may assign or change its `LocationId`.
4. Required devices are started according to configuration/policy.
5. SI-01 reports individual device/subsystem readiness rather than hiding startup progress behind one boolean.
6. The instance becomes ready for `OPEN` only when a valid operational `LocationId` is assigned and other required operational prerequisites are satisfied.

A TimingNode does not have an "unset" runtime identity: its `TimingNodeId` comes
from configuration and remains stable for that instance. A `LocationId` is
different: it may be unassigned while `CLOSED`. A value representing
"not configured" is not itself a valid operational location; the exact
data/wire representation is owned by the TimingData/IDD contract.

**Alternative/failure flows:**

- assigning an invalid location is rejected;
- changing location while `OPEN` is rejected;
- an RFID device does not boot or initialise;
- a CAN device is not discovered;
- required reference data is unavailable/stale;
- persistence/restore is unhealthy;
- network/backoffice is unavailable while local operation may still remain possible.

**Relevant interfaces:** IF-01/02/03, IF-07, IF-08, status model.

```

```{uc} Open and close a TimingNode
:id: UC-002

**Goal:** control one TimingNode operational session in a traceable way while
keeping its active location stable.

**Primary actor:** operator.

**Preconditions:**

- the addressed TimingNode exists and is `CLOSED`;
- a valid operational `LocationId` has been assigned.

**Main flow:**

1. The operator issues `open` through an authorised operator interface.
2. The command is translated to the shared application command boundary.
3. The addressed TimingNode validates its lifecycle and location preconditions through its serialized state boundary.
4. The lifecycle becomes `OPEN`.
5. The current `LocationId` is fixed for the duration of this open session.
6. Status/event consumers receive the new lifecycle and active-location state.
7. Normal registration operations may now be accepted.
8. When the operator issues `close`, the lifecycle returns to `CLOSED`.
9. The last assigned `LocationId` may remain visible after close, but it can only be changed while the node is `CLOSED`.

Whether `OPEN`/`CLOSE` transitions themselves become TimingData or are
reported upstream is a protocol/design decision; the lifecycle rule does not
depend on that choice.

**Alternative/failure flows:**

- `open` without a valid assigned location is rejected;
- changing `LocationId` while `OPEN` is rejected;
- duplicate/open-again or close-again commands receive an explicit outcome;
- another required operational prerequisite blocks `OPEN`.

```

```{uc} Register a participant through RFID
:id: UC-003

**Goal:** create a valid traceable registration from an accepted participant
observation without treating the first raw RFID observation as automatically
accepted.

**Primary actor:** RFID subsystem.

**Main flow:**

1. The RFID adapter captures raw tag data, antenna identity and observation time.
2. The RFID integration supplies the observation with its configured hardware/antenna context and routes it toward the addressed TimingNode.
3. Proprietary/private decoding/decryption translates the raw tag into a public semantic identity representation while retaining whether the tag is normal, reserve or test-class.
4. Filtering/observation accumulation determines whether the observation is accepted.
5. Reserve-tag resolution is applied when applicable using locally available reference data.
6. A test-tag identity branches to the explicit test-tag behaviour in UC-019 rather than silently continuing as a normal participant registration.
7. The accepted semantic registration enters the TimingNode registration operation.
8. The TimingNode accepts the registration only while `OPEN`, captures its own configured `TimingNodeId` and the active `LocationId`, and assigns the next source sequence number.
9. The committed TimingData retains that location even if the TimingNode is later closed and configured for another location.
10. The accepted observation time is retained; engineering/test input may supply a deterministic observation time where the public test contract permits it.
11. The committed registration becomes visible through the public registration state/history and subsequent live update semantics.
12. Outbound synchronisation, when implemented, consumes the committed TimingData independently from local acceptance.

**Step-4 engineering path:** the first registration slice may bypass antenna,
decoding and filtering by injecting an **already accepted semantic registration**
through an explicit engineering capability. That input enters the same TimingNode
registration operation at step 7. It does not inject a completed TimingData record,
does not choose its own source sequence, `TimingNodeId` or active `LocationId`,
and does not bypass the `OPEN` lifecycle rule.

A later simulated-antenna slice enters earlier in this use case so decoding,
observation accumulation and filtering can be exercised before reaching the same
accepted-registration operation.

**Alternative/failure flows:**

- decryption/validation fails;
- tag is observed but filtering does not yet accept it;
- reserve mapping is unavailable;
- a test-tag policy does not permit the requested/observed operation;
- accepted-registration input arrives while the TimingNode is `CLOSED`;
- source routing is ambiguous/invalid;
- local commit fails;
- backoffice is unavailable after local commit.

```

```{uc} Recover or reinitialise RFID equipment
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

```
```{uc} Manage ready teams through keypad/operator input
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

```
```{uc} Drive a passive CAN display from current system state
:id: UC-006

**Goal:** ensure the passive DisplayRev1Can shows the current ready-team/display model.

**Primary actor:** SI-01.

**Main flow:**

1. `CanNetworkController` discovers and monitors the configured CAN devices.
2. SI-01 derives a current `DisplayModel` from application state.
3. DisplayRev1Can-specific handling translates that model into CAN/device commands.
4. On state change or CAN-device rediscovery, SI-01 actively refreshes the display as required.
5. The passive display itself does not own ready-team/domain state.

```
```{uc} Provide data to a smart network display
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

```
```{uc} Operate SI-01 through a desktop GUI
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

The planned SI-02 GUI is not built in Step 4; the existing Engineering Client
may inspect these same public state semantics without claiming to implement SI-02.

```

```{uc} Exercise SI-01 through the Engineering Client
:id: UC-009

**Goal:** provide one engineering application for inspecting and exercising the
public SI-01 boundaries during development and integration.

**Primary actor:** test/developer.

**Preconditions:** SI-01 exposes the relevant public interfaces, or the client can
make their unavailability visible. Optional engineering controls require an
explicitly advertised **supported and enabled** capability.

**Main flow:**

1. The Engineering Client connects to supported public SI-01 interfaces and shows build/version identity, current status, connection state and event information.
2. For the first registration slice, it shows the addressed TimingNode identity, assigned/unassigned location state and `CLOSED`/`OPEN` lifecycle.
3. While the node is `CLOSED`, the developer may set/change its location through the public command boundary.
4. The developer may issue `open` and `close`; invalid lifecycle/location combinations remain explicit rather than being repaired silently by the client.
5. When the direct-registration simulation capability is supported and enabled, the developer may submit an accepted semantic participant registration, with a deterministic observation time when supported.
6. That simulation enters the TimingNode registration operation after the antenna/filtering boundary; the client cannot supply a completed TimingData record, source sequence or substitute source/location identity.
7. The client shows the resulting registration history/TimingData and subsequent live update separately from the command-submission result.
8. On disconnect the client marks cached information stale. After reconnect it rebuilds current TimingNode state and registration data before treating subsequent live updates as current.
9. The Engineering Client remains test/engineering tooling and does not become another owner of timing/domain state.

**Alternative/failure flows:**

- IF-03 unavailable or the live update connection is lost;
- invalid/unassigned location when `open` is requested;
- location change requested while `OPEN`;
- registration injection requested while `CLOSED`;
- unsupported/disabled engineering capability or invalid semantic registration input;
- a command was submitted but its resulting state cannot yet be confirmed after connection loss.

**Observable result:** the engineering client can demonstrate
`location -> open -> accepted registration -> observable TimingData -> close`
through public boundaries without requiring RFID hardware, filtering or a real
backoffice.

A separate lightweight browser test client is not part of this slice. Broader
upstream/reference-data simulation is deferred to a later increment.

```

```{uc} Synchronise reference data from backoffice
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

```
```{uc} Synchronise TimingNodeId-scoped data to backoffice
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
TimingData/IDD contract. Real RabbitMQ delivery, durable outbox/restart,
acknowledgement/reconciliation and inbound reference-data simulation are later
increments.

```

```{uc} Continue local operation during backoffice outage
:id: UC-012

**Goal:** preserve required local timing functionality and traceability while external connectivity is unavailable.

**Primary actor:** operator / SI-01.

**Main flow:**

1. SI-01 detects loss of internet/broker/backoffice connectivity and exposes the appropriate status layer.
2. Local device operation, registration and calculations continue where required local configuration/reference data is available.
3. New committed source records remain locally durable.
4. Outbound items remain pending.
5. After transport recovery, synchronisation resumes without inventing/reusing committed sequence numbers.

```
```{uc} Restart and restore local state
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

```
```{uc} Run multiple TimingNodes in one process
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

```

```{uc} Simulate a complete field toward backoffice
:id: UC-015

**Goal:** exercise realistic multi-TimingNode/multi-source behaviour from one test application.

**Primary actor:** automated/system test tooling.

**Main flow:**

1. A synthetic configuration creates enough TimingNodes and configured producer/timing node identity mappings to represent the required test scale.
2. Stub devices inject observations/faults through normal adapter boundaries.
3. SI-01 follows the same queues, `TimingNodeId`-scoped sequences, persistence and backoffice-port paths as production composition.
4. A backoffice simulator or broker fixture observes all source streams.
5. Tests validate isolation, ordering, recovery and status across the simulated field.

```
```{uc} Replace real devices with controllable stubs
:id: UC-016

**Goal:** make hardware-dependent application behaviour testable without duplicating business logic.

**Primary actor:** test tooling.

**Main flow:**

1. Composition selects stub adapters through normal public contracts.
2. Test control injects reads, device discovery, disconnects, failures or recoveries through the adapter surface.
3. The application processes those events through normal queues/domain handlers.
4. Tests observe behaviour only through supported state/interfaces/evidence points.

```
```{uc} Use an alternative backoffice transport for loop testing
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

```
```{uc} Verify production-shaped messaging through RabbitMQ
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

```
```{uc} Process a test RFID tag
:id: UC-019

**Goal:** recognise a test-tag observation and apply deliberate test-specific behaviour without allowing the tag to masquerade as a normal or reserve participant tag.

**Primary actors:** RFID subsystem and operator.

**Preconditions:**

- the tag has been decoded sufficiently to identify its semantic tag class;
- the configured TimingNode can identify that the tag is a test tag.

**Main flow:**

1. The RFID adapter captures the observation through the same normal ingress path used for other tags.
2. Decoding preserves the semantic tag class as `test` rather than flattening the identity to a normal participant identity.
3. Any common validation/filtering that also applies to test tags is performed according to the final requirements.
4. SI-01 applies the configured/test-tag policy instead of the normal or reserve-tag path.
5. The resulting action and operator-visible state remain explicitly distinguishable as test-tag behaviour.
6. If any record is persisted or synchronised, its semantics remain distinguishable from a normal participant registration.

**Behaviour still to define:**

- whether a test tag creates a registration-stream record at all;
- whether it uses a dedicated record type and/or `TimingNodeId` routing rule;
- whether it may affect elapsed-time/ranking/other derived calculations;
- whether it is synchronised to backoffice, and if so with what semantics;
- in which lifecycle states a test tag is accepted;
- what an operator sees when a test tag is detected/accepted/rejected;
- whether test-tag handling requires an explicit enable/configuration mode.

This use case is about a real semantic RFID tag class. It is separate from UC-015/016 software simulation and stub-device testing.

```
## Step-4 operational review: first registration slice

This review deliberately narrows Step 4 to the smallest useful vertical slice.
It identifies behaviour that needs a public representation before D03 designs
the interfaces. It is not a new set of API paths and does not expose any private
compatibility-source protocol.

| Use case | First-slice inspection/control need | Explicitly later |
| --- | --- | --- |
| UC-001 / UC-002 | Inspect one configured TimingNode identity, assigned/unassigned location and lifecycle; set/change location only while `CLOSED`; reject `OPEN` without a valid location; keep location fixed while `OPEN`; close explicitly. | Full device-readiness/open policy, durable lifecycle records and multi-node operation. |
| UC-003 | Inject one already-accepted semantic registration after the filtering boundary; TimingNode supplies its own identity, active location and next sequence; inspect committed registration history/TimingData. | Simulated antenna, tag decoding, observation accumulation/filtering, reserve/test-tag behaviour and persistence/recovery. |
| UC-009 | Exercise the above through IF-03/Engineering Client; distinguish command submission from resulting state; rebuild state/history after reconnect and then continue with live updates. | SI-02, browser test client and broader engineering controls. |
| UC-011 | Define the first committed registration TimingData identity and outbound semantic representation. | RabbitMQ, durable outbox/ack/replay and inbound upstream/reference-data simulation. |

For this slice the behavioural identity rules are:

- every TimingNode already has a configured, non-empty `TimingNodeId`; there is no runtime "unset TimingNodeId" state;
- a `LocationId` may be unassigned while `CLOSED`, but a valid operational location is required before `OPEN`;
- changing location while `OPEN` is rejected;
- committed TimingData captures the active location at acceptance time, so later reconfiguration cannot change historical records;
- the exact public types, allowed formats/values and null/unassigned representation are defined once in the TimingData/IDD contract rather than duplicated here.

The first protocol review (D03) must resolve:

- the compact public `TimingNodeId` representation and validation;
- the positive operational `LocationId` representation and how "unassigned while CLOSED" is represented without treating a non-location sentinel as a valid location;
- the first registration TimingData shape, including source sequence and accepted observation time;
- the IF-03 commands/results for location, open/close and direct accepted-registration simulation;
- current snapshot/history versus live-update semantics, including reconnect/rebuild;
- the minimal outbound semantic registration representation for later upstream transport.

`StageStartTimes`, `RaceData`, `NextUpTeams`, keypad/display behaviour,
simulated antenna/filtering, inbound DebugConnector messages and multi-node
isolation are intentionally outside this first slice.

The accepted first-executable IF-03 version/status/WebSocket semantics remain
the Step-3 baseline. D03 extends them only as required by this smaller slice.

## Cross-cutting alternative/failure scenarios## Cross-cutting alternative/failure scenarios

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
- GUI/test-client disconnect/stale state;
- socket transport disconnect/reconnect;
- RabbitMQ broker/channel/consumer recovery.

## Traceability direction

When requirements are promoted, prefer explicit references such as:

```text
UC-003
  -> SYS-REG-xxx
  -> IDD-... where external behaviour applies
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
- Which UC-019 test-tag behaviours are part of normal operational verification versus maintenance/service-only behaviour?

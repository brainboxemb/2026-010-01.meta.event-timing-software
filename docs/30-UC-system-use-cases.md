# System use cases

Status: working draft / non-authoritative

## Purpose

This document captures use cases for the registration system as a whole: operators, registration cabinets, connected devices, external systems and engineering/test equipment.

Use cases describe actor goals and externally observable system behaviour. Relevant physical equipment and network assumptions belong here; software-item allocation, interface IDs, protocol design and internal classes belong downstream in the SSSD, ISDs and SSDs.

The public repository uses generic/synthetic identities. Real deployment asset names, external data-source IDs, broker topology and proprietary protocol details remain outside this repository.

## Terms and abbreviations

- **UC** — Use Case
- **SSSD** — Software System Specification Document
- **ISD** — Interface Specification Document
- **SI** — Software Item


## Relationship to other documents

System use cases describe the **registration system and its environment**, including relevant physical interaction and connectivity. The SSSD then specifies the software-system responsibilities and allocates software items and interfaces.

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
Status (D — Draft, R — Review, A — Approved)
Name / goal
Primary actor(s)
Supporting actor(s)
Preconditions
Trigger
Main flow
Alternative / failure flows
Postconditions / observable result
Relevant physical equipment / operating environment, where important
```

The current catalogue starts lightweight and can be expanded as behaviour is reviewed. Each use case carries its own maturity status; this is separate from the document status. A use case does not assign software IF numbers, software items or requirements.

## Use-case catalogue

The catalogue is grouped by operational purpose for readability. Use-case IDs
remain stable traceability identifiers; their numeric order does not define the
reading order or implementation sequence.

### Normal operation

| ID | Name | Primary actor | Goal |
| --- | --- | --- | --- |
| UC-001 | Open a registration point | Operator | Use an iPad browser to reach a registration cabinet and open registration for a selected location. |
| UC-002 | Close a registration point | Operator | Stop accepting new registrations at an open registration point. |
| UC-003 | Register a participant through RFID | RFID subsystem | Turn valid filtered/decrypted RFID observations into traceable source-specific registration records. |
| UC-004 | Recover or reinitialise RFID equipment | Operator / system | Restore an RFID device after startup, heartbeat or protocol failure without losing committed timing state. |
| UC-005 | Manage teams to prepare through keypad/operator input | Operator / keypad | Add or remove team numbers from the next-up team state and preserve the change history. |
| UC-006 | Drive a passive CAN display from current system state | Timing application | Keep DisplayRev1Can aligned with the current ready-team/display model. |
| UC-007 | Synchronise a smart display | Smart display | Connect to the advertised service and receive current/synchronised display data while SI-01 remains the source of that state. |

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
:status: D

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

:::{uc} Open a registration point
:id: UC-001
:status: D

**Goal:** allow the operator to open a registration cabinet for participant
registration at a chosen location.

**Primary actor:** operator.

**Preconditions:**

- the registration cabinet is powered on;
- the iPad is connected to the same local network as the registration cabinet;
- the operator knows the registration cabinet's IP address.

**Main flow:**

1. The operator opens a Web browser on the iPad and enters the IP address of the registration cabinet.
2. The cabinet presents the operator interface and its current registration state.
3. The operator sees that registration is `CLOSED`.
4. The operator enters the location at which participants will be registered.
5. The operator selects **Open**.
6. The registration cabinet accepts the location and opens registration for that location.
7. The interface confirms `OPEN` and shows the active location.

**Alternative/failure flows:**

- **Already open:** the operator connects to a cabinet that is already `OPEN`.
  The interface shows the existing location and `OPEN` state. Connecting does not
  change either; the operator can continue existing registration or close it (UC-002).
- **Cabinet unreachable:** the operator cannot load the interface and cannot
  confirm the current state.
- **Invalid location:** the cabinet rejects the requested location and remains
  `CLOSED`.
- **Software errors:** the cabinet software has detected errors. The operator
  sees the relevant errors and current state; opening is refused when an error
  prevents safe operation.
- **Open not confirmed or connection lost:** the operator does not assume
  registration is open until the resulting state can be confirmed. Reconnecting
  must show the cabinet's actual current state.

**Postcondition:** if opening succeeds, registration is `OPEN` for the selected
location. Closing the browser or losing the iPad connection does not itself
close registration.

:::

:::{uc} Close a registration point
:id: UC-002
:status: D

**Goal:** allow the operator to close an open registration point so no new
participant registrations are accepted.

**Primary actor:** operator.

**Preconditions:**

- the operator can reach the registration cabinet through the iPad Web browser;
- registration is `OPEN`.

**Main flow:**

1. The operator sees the cabinet's current location and `OPEN` state.
2. The operator selects **Close**.
3. The registration cabinet stops accepting new registrations.
4. The interface confirms `CLOSED`.

**Alternative/failure flows:**

- **Software errors:** the cabinet reports detected errors and its current
  state. An error that prevents opening need not prevent safe closing.
- **Close unavailable or unsuccessful:** the interface reports the failure and
  must not falsely claim that the cabinet is `CLOSED`.
- **Connection lost or outcome unknown:** the operator reconnects to establish
  the current cabinet state rather than assuming the close succeeded.
- **Already closed:** the operator sees `CLOSED`; there is no open
  registration to close.

**Postcondition:** when closing succeeds, the cabinet is `CLOSED` and
previously accepted registrations remain retained. Disconnecting the iPad
does not itself change the cabinet state.

:::

:::{uc} Register a participant through RFID  
:id: UC-003  
:status: D

**Goal:** turn an accepted participant observation into one traceable registration
for the location that is currently open.

**Primary actor:** RFID subsystem.

**Preconditions:**

- registration is `OPEN`;
- a valid operational location is active.

**Main flow:**

1. The RFID subsystem observes a participant tag and captures the observation time.
2. The registration equipment checks whether the tag observation is a valid participant registration.
3. An accepted observation is registered at the open registration point.
4. The registration system associates the registration with its identity and current location.
5. The registration system records the registration and its observation time.
6. The registration retains the active location and accepted observation time even if the registration point is later closed or configured for another location.
7. The registration becomes visible in the registration history.
8. The registration remains available for later synchronisation with backoffice.


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
:status: D

**Goal:** restore RFID registration after equipment startup or an antenna failure without restarting the registration cabinet or losing recorded registrations.

**Primary actor:** operator / registration system.

**Preconditions:**

- SI-01 is running and the configured antenna is still part of the active composition;
- the antenna may have failed an earlier self-test or runtime operation;
- committed TimingData is independent from antenna control state.

**Main flow:**

1. The registration cabinet reports that one RFID antenna is unavailable or has failed.
2. Registration is opened or the operator requests another start attempt.
3. The cabinet retries starting the affected antenna even if an earlier attempt failed.
4. On success, RFID registration is available again.
5. Previously recorded registrations and any unaffected antennas remain available.

**Alternative / failure flows:**

- if the new attempt fails, SI-01 records that failed attempt and leaves the antenna in a
  state from which a later explicit request can try again;
- SI-01 does not automatically loop retries solely because an attempt failed;
- repeated failures of one antenna do not prevent independent configured antennas from
  being operated or retried;
- invalid configuration or a deliberately disabled capability may reject the request
  because there is no valid antenna operation to perform.

**Observable result:** a failed antenna operation does not permanently disable the
antenna. A later inventory demand can start another attempt without restarting SI-01.

:::

:::{uc} Manage ready teams through keypad/operator input  
:id: UC-005  
:status: D

**Goal:** maintain the current list of teams that must prepare at the timing node/exchange point while keeping keypad/operator add/remove history traceable.

**Primary actor:** keypad or operator client.

**Main flow:**

1. An operator enters or removes a team number using the keypad or another supported operator control.
2. The registration system updates its list of teams preparing next.
3. The change becomes visible on connected displays and operator views.
4. The system keeps the history needed to trace changes.

Any `NextUpTeams` change history required by the promoted requirements is separate from participant/timing `TimingData` streams.

:::

:::{uc} Drive a passive CAN display from current system state  
:id: UC-006  
:status: D

**Goal:** show the current teams preparing on the passive display.

**Primary actor:** registration system.

**Main flow:**

1. The registration cabinet is connected to the passive display.
2. When the list of teams preparing changes, the cabinet updates the display.
3. After a display reset or reconnection, the current information is shown again.
4. The display continues showing the current information supplied by the cabinet.

:::

:::{uc} Provide data to a smart network display  
:id: UC-007  
:status: D

**Goal:** let a smart network display show up-to-date registration and reference information.

**Primary actor:** smart display.

**Main flow:**

1. The smart display finds the available registration-system service on the network.
2. The display connects and receives the information needed to show current status and reference data.
3. The display presents the information using its own user interface.
4. After a network interruption, the display reconnects and refreshes its current information.

:::

### System, backoffice and recovery

:::{uc} Synchronise reference data from backoffice  
:id: UC-010  
:status: D

**Goal:** make required reference data available locally even when later backoffice connectivity is interrupted.

**Primary actor:** backoffice.

**Main flow:**

1. Backoffice sends updated start times or participant reference information to a registration point.
2. The registration system checks the update and whether it applies to that registration point.
3. A valid update becomes available for local registration and operator views.
4. The system reports when an update cannot be accepted.
5. Accepted information remains available during a later connection interruption.

**Alternative/failure flows:** unknown target, invalid or conflicting reference
update, or unavailable upstream transport. Message submission alone must not
be presented as proof that the target's reference state changed.

:::

:::{uc} Synchronise TimingNodeId-scoped data to backoffice  
:id: UC-011  
:status: D

**Goal:** send recorded registrations to backoffice in their correct source order and resume after interruptions.

**Primary actors:** SI-01 and backoffice.

**Main flow:**

1. The registration cabinet records participant registrations with their registration-point identity, location and order.
2. The cabinet sends records to backoffice in the correct order.
3. Backoffice receives the registrations and confirms receipt as supported.
4. After an interruption, the cabinet resumes delivery without duplicating or losing registrations.

:::

:::{uc} Continue local operation during backoffice outage  
:id: UC-012  
:status: D

**Goal:** allow registration to continue locally when the backoffice connection is unavailable, without losing accepted registrations.

**Primary actor:** operator / SI-01.

**Main flow:**

1. The registration cabinet loses communication with backoffice and reports the connection problem.
2. The operator continues local registration using the information already available.
3. The cabinet retains the registrations made while disconnected.
4. When connectivity returns, the cabinet sends the pending registrations without losing or reordering them.

:::

:::{uc} Restart and restore local state  
:id: UC-013  
:status: D

**Goal:** restore safe registration cabinet operation and previously recorded registrations after restart or power interruption.

**Primary actor:** platform/operator.

**Main flow:**

1. The registration cabinet restarts after shutdown or power interruption.
2. The cabinet restores previously recorded registrations, current location and required operating state.
3. The cabinet reports any information that could not be restored safely.
4. The operator sees whether the registration point is ready or needs attention.
5. Pending backoffice synchronisation can resume after connectivity is restored.

:::

:::{uc} Run multiple TimingNodes in one process  
:id: UC-014  
:status: D

**Goal:** host multiple independently addressed TimingNodes
while preserving independent lifecycle, state and
`TimingNodeId`-scoped streams.

**Primary actor:** configuration/test/operator tooling.

**Main flow:**

1. An engineer configures multiple virtual registration points for one test setup.
2. Each registration point can be identified and operated independently.
3. Recorded registrations and operational state remain associated with the correct point.
4. An action addressed to one point does not change a different point.
5. The engineer can inspect each point separately.

**Observable result:** two synthetic TimingNodes have separately inspectable
lifecycle, reference/next-up state and independently ordered TimingData. Any
intentional fan-out from one observation to several streams is a separately
specified mapping rule, not accidental cross-instance sharing.

:::

### Engineering, simulation and verification

:::{uc} Exercise the registration system through the Engineering Client  
:id: UC-009  
:status: D

**Goal:** provide the SI-02 Engineering Desktop Client for inspecting and exercising
public registration-system behaviour during development, integration, commissioning and system test.

**Primary actor:** developer, integration/commissioning engineer or system tester.

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
9. The Engineering Client is SI-02 and remains a client of SI-01; it does not become another owner of registration/domain state.

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
:status: D

**Goal:** exercise realistic multi-TimingNode/multi-source behaviour from one test application.

**Primary actor:** automated/system test tooling.

**Main flow:**

1. A system tester sets up a simulated field with multiple registration points and devices.
2. The test equipment simulates participant observations, equipment faults and communication interruptions.
3. The simulated registration points operate independently and send results to a backoffice test system.
4. The tester checks the recorded results, ordering, isolation, recovery and visible status.

:::

:::{uc} Replace real devices with controllable stubs  
:id: UC-016  
:status: D

**Goal:** make hardware-dependent application behaviour testable without duplicating business logic.

**Primary actor:** test tooling.

**Main flow:**

1. A tester starts the registration system with simulated devices in place of physical devices.
2. The tester simulates participant observations, connection losses, faults or recovery.
3. The registration system responds as it would to equivalent real-device events.
4. The tester observes the results using the normal available system controls and outputs.

:::

:::{uc} Use an alternative backoffice transport for loop testing  
:id: UC-017  
:status: D

**Goal:** test real process/network communication and `TimingNodeId`-scoped stream routing without RabbitMQ.

**Primary actors:** backoffice simulator and test tooling.

**Main flow:**

1. A tester connects a backoffice simulator to a registration cabinet over an independent network connection.
2. The simulator exchanges registrations and reference updates with the cabinet.
3. Several registration points can be tested in the same setup.
4. The tester interrupts and restores communication and checks that registration data stays correct.
5. The test can be conducted without the production message broker.

:::

:::{uc} Verify production-shaped messaging through RabbitMQ  
:id: UC-018  
:status: D

**Goal:** verify broker/client lifecycle and source-specific messaging using a real disposable broker.

**Primary actors:** automated test tooling and SI-01 RabbitMQ adapter.

**Main flow:**

1. A system tester runs a disposable message broker for a representative backoffice connection.
2. The registration system exchanges test data with backoffice through the broker.
3. The tester verifies that data reaches the correct registration point and remains identifiable.
4. The broker is interrupted and restarted.
5. The tester checks reconnection and delivery of registrations recorded during the outage.

:::

:::{uc} Handle provider-specific input classification  
:id: UC-019  
:status: D

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

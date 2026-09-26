# Software architecture document set

Generated review/output book containing the software-system architecture, software-item architectures, and only currently active focused detailed design. The numbered source documents on the source branch remain authoritative.

## Contents

- [Software System Architecture Document (SSAD)](30-SSAD-software-system-architecture.md)
- [Timing Application Architecture (SAD)](31-01-SAD-timing-application-architecture.md)
- [Java component, package and artifact detailed design](31-01-SDD-02-java-component-design.md)
- [GUI Application Architecture (SAD)](31-02-SAD-gui-application-architecture.md)

---

## Software System Architecture Document (SSAD)

**Source document:** [30-SSAD-software-system-architecture.md](30-SSAD-software-system-architecture.md)

Status: working draft / non-authoritative

This document defines the architecture of the software system as a whole. Its purpose is to show the software items, their responsibilities and relationships, the system-owned interfaces, deployment relationships and constraints that apply across software-item boundaries.

It deliberately does **not** define the internal threading, messaging, persistence, package structure, device processing or implementation technology of the **Headless Timing Application** (SI-01). Those concerns belong in the applicable software-item SAD and, only where justified later, a focused detailed-design document.

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

- the **Headless Timing Application** (SI-01) keeps the local timing/registration state and runs the timing/device functions;
- the planned **Desktop GUI Application** (SI-02) is a separate software item and communicates with the Headless Timing Application through the Remote API;
- local timing/device operation must not depend on a connected GUI or engineering/test client;
- external devices and backoffice systems are explicit system interfaces rather than hidden implementation dependencies;
- public framework/reference code and private/proprietary implementations must meet common supported contracts without private source leaking into public code;
- deployments should support the intended field target and normal development/test hosts; target limits are measured rather than assumed;
- system interfaces and software-item ownership should remain stable even when internal implementation technology changes;
- IP-based system interfaces must not require a particular router or Wi-Fi topology merely to exercise the interface.

### Software-item register

The second-level number used in SRD/SAD/SDD filenames identifies the software item.

| Software item | Name | Current status | Primary responsibility | Expected deployment |
| --- | --- | --- | --- | --- |
| **SI-01** | Headless Timing Application | working architecture | Local timing/registration runtime, device integration, state, status, persistence and backoffice synchronisation | Raspberry Pi Zero/Zero W; Linux/Windows development/test/runtime |
| **SI-02** | Desktop GUI Application | planned / technology open | Desktop client for status and later control through the Remote API | Operator workstation/laptop |

Supporting framework modules, adapters and engineering/test clients are not automatically separate product software items. The current JavaFX Remote API client is engineering support, not SI-02. A small web test client may be added later without creating another software item.

### System context

```text
                         Operator
                            |
                            v
                    SI-02 Desktop GUI
                            |
                            v
                    SI-01 Timing Application
                       ^            ^
                       |            |
              engineering/test   scripts / optional
              JavaFX client      web test client
                    /      |       \
                   v       v        v
             field devices local   Backoffice
             RFID / CAN     state   integration
             / displays
```

GUI and engineering/test clients may disconnect without changing where timing state is kept: it remains in the **Headless Timing Application** (SI-01).

<a id="fig-sys-01"></a>
![Software items and principal system interfaces](../assets/architecture/software-item-system-overview.svg)
*Figure SYS-01 — Software items and principal system interfaces.*

### Software-item relationships

#### **Headless Timing Application** (SI-01) ↔ **Desktop GUI Application** (SI-02)

The **Desktop GUI Application** (SI-02) is an IP network client of the **Headless Timing Application** (SI-01). It presents operator status and control but does not access the application's memory, files or Java objects directly. The logical IF-03 relationship does not require a Wi-Fi router: a direct, same-host, point-to-point or normal LAN/Wi-Fi IP path may carry the interface.


#### **Headless Timing Application** (SI-01) ↔ backoffice

The **Headless Timing Application** (SI-01) exchanges race/reference data, registration information, status and reconciliation information with the backoffice through a system-owned semantic interface. The concrete transport, codec and network route are implementation/integration design concerns for the **Headless Timing Application** (SI-01) unless they change the external system contract.

#### **Headless Timing Application** (SI-01) ↔ field devices

RFID, CAN, keypad and display equipment are external device boundaries of the **Headless Timing Application** (SI-01). Device semantics belong in system/device interfaces; internal adapter lifecycle, threads and processing pipelines belong in the **Headless Timing Application** (SI-01) architecture/design.

### System interface catalogue

This catalogue identifies system-owned boundaries before all individual IDDs are mature. IDs are working identifiers but should remain stable once promoted.

| Interface | Parties | Current transport/direction | Purpose | Planned documentation |
| --- | --- | --- | --- | --- |
| **IF-01 Local Operator Console** | Operator ↔ SI-01 | local console/shell | Local version, status and operator commands | operator/application interface material |
| **IF-02 Remote Shell** | Operator/service tool ↔ SI-01 | remote terminal/shell, technology TBD | Remote status and commands using shared semantics | IDD candidate |
| **IF-03 Remote API** | SI-02 / engineering & test clients ↔ SI-01 | HTTP/JSON + WebSocket over an available IP path | General remote query/control/diagnostics/test API; first slice is version/status/events | `40-01-IDD-application-control-status.md` candidate |
| **IF-04 Desktop Operator HMI** | Operator ↔ SI-02 | desktop GUI | Desktop screens, controls and operator feedback | GUI/HMI IDD candidate |
| **IF-06 Backoffice Integration** | SI-01 ↔ Backoffice | transport implementation below semantic boundary | Race/reference-data sync, registrations, reconciliation/status | system IDD; proprietary wire details may remain private |
| **IF-07 RFID Integration** | SI-01 ↔ RFID subsystem | hardware/protocol adapter | RFID observations, lifecycle and health | device/semantic contract candidate |
| **IF-08 CAN Device Integration** | SI-01 ↔ CAN bus/devices | CAN | Discovery, Display V1 and keypad interaction | system/device IDD candidate |
| **IF-09 Smart Display V2** | SI-01 ↔ Display V2 | IP path; direct or LAN/Wi-Fi deployment | Synchronised display/domain data | system IDD candidate |
| **IF-10 Test Control** | test/reference tooling ↔ public stubs | development-only | Inject device/network/fault behaviour through supported boundaries | SDE/SVP/test design |
| **IF-11 Application Configuration** | Deployment/configuration source → SI-01 | external configuration + platform/profile overlays + secret references | Define deployed TimingNodes, I/O assets, presentation bindings and runtime composition inputs | `40-02-IDD-application-configuration.md` |

System-level IDDs own interface semantics. Software-item SRDs and SADs reference those obligations rather than redefining the wire/system contract independently.

### Cross-software-item interaction principles

The following rules apply across software-item boundaries:

- operator and engineering clients should use shared application semantics rather than implement different business rules per client;
- network clients read state from and send commands to the **Headless Timing Application** (SI-01); timing state remains in that application;
- loss of the **Desktop GUI Application** (SI-02) or an engineering/test client must not by itself stop local operation of the **Headless Timing Application** (SI-01);
- IF-03 and IF-09 are endpoint-to-endpoint logical interfaces and must not make a physical Wi-Fi router an architectural prerequisite;
- development and automated integration verification may use loopback, same-host or direct IP connectivity while exercising the same system interface semantics;
- interface versioning and compatibility must be explicit once interfaces become stable contracts;
- transport-specific implementation detail should not leak into the semantic system interface unless that transport is itself part of the external contract;
- system status must distinguish local IP availability, configured network-infrastructure state, external reachability and backoffice/session health where those distinctions affect operator decisions.

### System deployment view

The principal device/interface relationships are a **software-system concern** because they show where the **Headless Timing Application** (SI-01), the operator software items, external field devices and backoffice meet. The lines in this view are logical system-interface relationships: they deliberately do not force traffic through a router node.

<a id="fig-sys-02"></a>
![System device and logical interface topology](../assets/architecture/system-device-network-topology.svg)
*Figure SYS-02 — System device and logical interface topology.*

Representative relationships are:

```text
Deployment/configuration source
  +-- IF-11 --> SI-01

Field host
  SI-01 Headless Timing Application
    |
    +-- IF-07 --> RFID subsystem
    +-- IF-08 --> CAN devices / keypad / Display V1
    +-- local persistent state

SI-02 Desktop GUI
  +-- IF-03 over available IP path --> SI-01

Engineering/test clients
  +-- IF-03 over available IP path --> SI-01

Smart Display V2
  +-- IF-09 over available IP path --> SI-01

Backoffice
  +-- IF-06 over configured external path --> SI-01
```

An available IP path may be direct/point-to-point, same-host or loopback during development/test, or may run over normal LAN/Wi-Fi infrastructure in a field deployment. A Wi-Fi router/access point is therefore **optional deployment infrastructure**, not part of the semantic definition of IF-03 or IF-09.

#### Connectivity and reachability state

Network health is not one boolean and should not be modeled as one mandatory chain. The system needs to expose separately observable states because they answer different operational questions.

<a id="fig-sys-03"></a>
![Network connectivity status — separate observations](../assets/architecture/system-connectivity-status.svg)
*Figure SYS-03 — Network connectivity status — separate observations.*

At minimum distinguish:

- **local IP connectivity** — network interface/link of the **Headless Timing Application** (SI-01) and its ability to communicate with local peers;
- **configured router/AP connectivity** — whether the deployment is connected/associated with the configured local router or access point; this may legitimately be **N/A** for direct/development/test compositions;
- **external network reachability** — whether connectivity beyond the local network is available;
- **backoffice connectivity** — whether the configured backoffice endpoint/transport/session is healthy.

These states must not be conflated. For example, local timing and direct local clients may remain fully operational while the router, external uplink or backoffice is unavailable. Conversely, a configured field deployment may need to report that it has lost its expected router/AP even before external reachability is tested.

The exact process/thread topology, internal runtime cardinality, queueing model, service composition, connectivity probing mechanism and adapter implementation are intentionally outside this SSAD.

### Cross-system architectural constraints

#### State ownership and disconnected operation

The **Headless Timing Application** (SI-01) keeps the local operational state. Losing a GUI/test client or external connection must not move that state elsewhere or make synchronisation appear healthy when it is not.

#### Public/private implementation boundary

System contracts used by public framework/reference code must allow private production implementations to plug in without public code depending on private source or proprietary identities.

#### Interface-first separation

Software-item interaction is defined in terms of system-owned semantics. Internal implementation choices such as RabbitMQ libraries, HTTP servers, logging frameworks, executors or file formats are owned by the relevant software-item architecture unless the choice becomes part of an external contract.

#### Deployment portability

The architecture must support constrained field deployment and normal Linux/Windows development/test environments without changing the software-item boundaries. Automated integration verification must be able to exercise network interfaces without provisioning a physical Wi-Fi router unless the test explicitly targets router/AP behaviour.

### Relationship to software-item architecture

The SAD for the **Headless Timing Application** (SI-01) owns, among other things:

- layered application responsibilities;
- `TimingNode` software/domain decomposition, separate registration-hardware topology, and their configuration/data-source identity mapping;
- threading/concurrency and internal messaging;
- status architecture and lifecycle handling;
- persistence and restore strategy;
- logging/configuration/composition choices;
- Java/framework/library decisions;
- RFID/CAN/display adapter architecture behind the system device interfaces;
- backoffice transport implementation behind IF-06;
- resource-budget implications of those choices.

The SAD for the planned **Desktop GUI Application** (SI-02) owns its internal architecture while conforming to the Remote API and applicable IDDs.

### Architecture review model

The project uses the 4+1 architectural view model as a review aid, not as a requirement for five documents. At system level, the SSAD primarily provides system context and deployment/relationship views. The software-item SADs provide the coherent logical, process, development and deployment views of each item and reference selected use cases as scenarios.

Reference: `reference/README.md`.

### Open system-architecture questions

- final system interface/IDD breakdown and ownership;
- authentication, authorisation and secure transport requirements across software-item boundaries;
- compatibility/versioning policy for IF-03 and IF-06;
- which device semantics require system-level IDDs versus software-item-only design;
- required behaviour when local IP, configured router/AP, external network or backoffice connectivity is unavailable;
- final system-level availability/recovery requirements.


---

## Timing Application Architecture (SAD)

**Source document:** [31-01-SAD-timing-application-architecture.md](31-01-SAD-timing-application-architecture.md)

Status: working draft / non-authoritative

Software item: **Headless Timing Application** (SI-01)

This Software Architecture Document describes the **Headless Timing Application** (SI-01). It sits below `30-SSAD-software-system-architecture.md` and is the primary technical design document for this application at the current project stage.

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

The **Headless Timing Application** (SI-01) architecture is driven by these concerns:

- run on the original Raspberry Pi Zero / Zero W target; actual runtime/resource constraints are established by measurement;
- remain usable on Linux/Windows development and test hosts;
- keep timing/domain state in the application;
- support one or more logical TimingNodes without state leakage;
- preserve deterministic ordering of state-changing work;
- isolate external I/O concurrency from application/domain state mutation;
- preserve unambiguous time semantics across local time zones, daylight-saving transitions and wall-clock corrections;
- remain testable without production RFID, CAN, backoffice or proprietary implementations;
- expose one coherent command/query/status/event model to local and network presentation adapters;
- support local persistence/recovery and disconnected operation;
- keep public framework/reference code independent of private production source;
- avoid framework complexity that is not justified by the application.

### +1 scenarios used to validate the architecture

The existing use cases in `04-UC-system-use-cases.md` are the scenario source. The SAD should not create a second competing use-case catalogue.

Representative architecture-validation scenarios include:

1. start the **Headless Timing Application** (SI-01), load configuration, expose version/status and shut down cleanly;
2. accept an operator command through local or network presentation and route it to the correct logical TimingNode;
3. accept a device observation from an external callback without allowing that callback thread to change application state directly;
4. persist accepted operational state and recover it after restart;
5. continue local operation while a GUI/test client or backoffice connection is unavailable;
6. host several TimingNodes in a development/simulation composition without state leakage;
7. substitute public stubs for production devices/transports while exercising the same application/domain paths;
8. capture and process observations correctly when local civil time crosses a daylight-saving transition or the operating-system wall clock is corrected forwards/backwards.

These scenarios are used to check the logical, process, development and deployment views below.

### Logical view

#### Layered application architecture

The primary logical view is a responsibility/layer view. It describes semantic ownership and dependency direction; it does **not** prescribe one Maven artifact per layer.

`TimingApplication` is the top-level executable/composition root. Presentation interfaces, application-layer coordination, domain state and I/O adapters are instantiated as parts of that one running application; `TimingApplication` is therefore not itself a component inside the application layer.

The compact software/domain ownership model is intentionally also kept as copyable text:

```text
TimingApplication
  |
  +-- SystemStatus
  |
  +-- 1..N TimingNode
        +-- TimingNodeId
        +-- LocationID
        +-- lifecycle / status
        +-- TagProcessor
        +-- StageStartTimes
        +-- Journal
        +-- NextUpTeams
        +-- RaceData
        +-- StageTiming
```

<a id="fig-si01-01"></a>
![SI-01 layered architecture](../assets/architecture/layered-architecture.svg)
*Figure SI01-01 — SI-01 layered architecture.*

The source for this view is `docs/_diagrams/layered-architecture.yaml`.

#### Presentation

Presentation owns client-facing interfaces and their external representations. Its structure is **functional interface first, transport second**:

```text
presentation/
  interfaces/
    remoteapi/
      http/
      websocket/
      messages/
    console/
    shell/
  common/
    terminal/         behaviour genuinely shared by console + shell
```

The **Remote API** is the general programmable interface of the **Headless Timing Application** (SI-01) for remote clients, engineering tools and headless black-box/integration tests. A06/A07 implement only its first version/status/event slice; later supported control and diagnostic operations grow inside the same functional interface.

A browser-based engineering client, if useful later, consumes the same Remote API as other external test tools. It does not require a separate SI-01 presentation interface merely because the client itself runs in a browser. Console and remote shell remain separate presentation interfaces; sharing a terminal session does not make them one interface.

`presentation.common` is reserved for behaviour genuinely shared across presentation interfaces. Message mapping shared only by Remote API HTTP and WebSocket stays under `interfaces/remoteapi/messages`, not global common code.

Presentation converts external requests to application calls and application results to client representations. It does not own mutable application/domain state.

#### Application

The application responsibility coordinates use cases:

```text
application/
  Conductor
    lifecycle and application-wide coordination

  CommandHandler
    shared presentation command/query boundary
```

`Conductor` coordinates application-wide lifecycle and active TimingNodes.

`CommandHandler` is the shared entry point for presentation requests. It may
serve simple application reads such as `version()`. When a presentation command
or query names a `TimingNodeId`, the application looks up that `TimingNode` and
submits state-changing work to its serial executor.

Once code is executing for a TimingNode, normal direct Java calls are preferred;
do not introduce commands merely to preserve a layer diagram. I/O routing and
binding are configuration/composition responsibilities; they do not imply
separate router classes unless implementation behaviour later justifies them.

#### Domain

The domain owns timing rules and TimingNode state:

```text
TimingNode
  TimingNodeId
  LocationID
  TagProcessor
  StageStartTimes
  Journal
  NextUpTeams
  RaceData
  StageTiming
```

`TagProcessor` handles tag observations. `StageStartTimes` owns stage start references. `Journal` owns
registration/history data and sequence semantics. `NextUpTeams` owns the teams
expected next at the TimingNode.
`RaceData` contains participant/team/tag reference data. `StageTiming`
derives running times and ranking.

Detailed domain semantics belong in `03-domain-baseline.md`.

#### Core runtime support

Core contains reusable execution mechanics, not business behaviour:

```text
serial execution
lifecycle mechanics
scheduling
asynchronous completion
```

#### I/O

I/O contains adapters that move data between the application and the outside world:

```text
io/
  Antenna (0..N)
  BackofficeConnector (0..N)
    RabbitMqBackofficeConnector
    SocketBackofficeConnector
  Devices
    CAN
    Display
  Storage
    file
    db
```

Presentation stays separate because it owns client-facing API/view semantics.
I/O owns the external boundary and its mapping to TimingNodes.

The **Headless Timing Application** (SI-01) may compose 0..N configured `Antenna` instances and 0..N
`BackofficeConnector` instances. Antenna mappings route observations to 1..N
TimingNodes; connector bindings map inbound/outbound data to/from TimingNodes.
Concrete antennas/connectors own their protocol/device resources internally.

#### Platform

Platform contains low-level execution-environment facilities:

```text
clock / time source
filesystem/path primitives
executors / threads
process/runtime information
network / OS primitives
```

#### Cross-cutting concerns

Cross-cutting technical concerns include logging, configuration, diagnostics,
metrics and build/version identity. In Java, `infra` is reserved for concrete
cross-cutting support such as `BuildIdentity`; it is not the I/O layer.

### Principal runtime abstractions

A `TimingNode` is the primary independently addressed operational/domain aggregate inside the **Headless Timing Application** (SI-01). One application process may host one or more TimingNodes. `SystemStatus` is application-scoped and aggregates/monitors overall runtime and TimingNode status rather than belonging to one TimingNode.

The architecture deliberately uses **separate views** for software/domain decomposition, hardware/deployment topology and configuration/identity mapping. These views must not be collapsed into one ownership tree.

#### Software/domain decomposition

```text
TimingApplication
  |
  +-- SystemStatus
  |
  +-- 1..N TimingNode
        +-- TimingNodeId
        +-- LocationID
        +-- lifecycle / status
        +-- TagProcessor
        +-- StageStartTimes
        +-- Journal
        +-- NextUpTeams
        +-- RaceData
        +-- StageTiming
```

`TimingNodeId` is the stable identity of the `TimingNode` and scopes its registration sequence, persistence and synchronisation semantics. `LocationID` is the separately configured physical event location.

<a id="fig-si01-02"></a>
![SI-01 software/domain decomposition](../assets/architecture/timing-node-software-decomposition.svg)
*Figure SI01-02 — SI-01 software/domain decomposition.*

The exact Java class/package boundaries may evolve as implementation evidence appears, but the `TimingNode` aggregate is the semantic owner of the operational TimingNode state. The physical registration asset is not a child component of this software tree.

#### Antenna topology

The active software/configuration model uses the configured antenna directly:

```text
Antenna (0..N)
```

An `Antenna` is an I/O source with its own `AntennaId` and concrete
driver/connection settings. Reader/protocol/device details stay inside that
concrete antenna implementation/configuration unless later evidence requires a
separate architectural concept.

One antenna may intentionally feed one or more TimingNodes.

#### Configuration, routing and identity mapping

Configuration connects identities without collapsing them:

```text
Antenna (0..N)
    +-- each Antenna -> 1..N TimingNodeId

BackofficeConnector (0..N)
    +-- bindings <-> 1..N TimingNodeId
```

<a id="fig-si01-03"></a>
![TimingNode, hardware and backoffice routing](../assets/architecture/timing-node-routing-mapping.svg)
*Figure SI01-03 — TimingNode, hardware and backoffice routing.*

`TimingNodeId` is the stable identity of a `TimingNode` and scopes its sequence, persistence and synchronisation semantics. `LocationID` and `AntennaId` are separate namespaces.

Configured antenna mappings associate each `AntennaId` with one or more TimingNodes. Fan-out is explicit: if one antenna feeds two TimingNodes, each target TimingNode processes the observation through its own serialized state boundary and keeps its own TimingNodeId-scoped sequence/state while the original `AntennaId` remains available as context.

Configured backoffice bindings map connector-specific inbound/outbound data to TimingNodes. A connector binding may assign an external/backoffice-facing name to a TimingNode without changing its internal `TimingNodeId`. One connector may serve many TimingNodes and one TimingNode may bind to more than one connector.

These mappings belong to the I/O composition/configuration boundary; they do not require a separate router object. Concrete `Antenna` and `BackofficeConnector` implementations own their protocol/device resources internally.

Runtime-wide infrastructure may be shared where that does not leak mutable TimingNode state. Candidates include backing executors, logging infrastructure, HTTP server infrastructure, shared connector infrastructure, configuration loading and network monitoring.

Stable domain facts behind these views are maintained in `03-domain-baseline.md`; this SAD owns their software-architecture composition and execution implications.

### Command, query and event model

All presentation transports should converge on one shared application model. The first Java implementation proves this with a deliberately small `CommandHandler.version()` query rather than a generic messaging framework; future request methods should be added only when a real client use case requires them.

```text
local console ----------------+
remote shell -----------------+
Remote API HTTP/JSON ---------+--> typed command/query boundary --> application runtime
Remote API WebSocket <---------+<--------------------------------------------+
future Web interface ----------+
```

Working rules:

- commands request state changes;
- queries read current state/snapshots without becoming alternate owners of state;
- events report facts/results that have occurred;
- external protocol DTOs are mapped at the presentation/I/O boundary rather than used as the internal domain model;
- messages crossing thread/process boundaries should be immutable where practical;
- a generic event-bus framework is **not** assumed to be necessary.

The initial architecture uses explicit typed routing because the flow is easier to reason about, test and keep lightweight on the Pi Zero. A third-party messaging/event framework should only be introduced when it solves a demonstrated problem better than explicit routing and JDK concurrency primitives.

### Process view: threading and concurrency

The domain model is intentionally kept simple. Code working on one `TimingNode`
should be able to behave as if it is single-threaded.

That guarantee is provided by the application around the domain code. Domain
objects are not expected to add locks everywhere to protect themselves from
normal application callbacks.

#### The rule for one TimingNode

For each `TimingNode`:

1. any code that changes its mutable state is submitted to that TimingNode's
   serial executor;
2. that executor runs at most one accepted task for that TimingNode at a time;
3. once a task is running there, normal direct Java calls are used between the
   TimingNode's domain objects;
4. a second task for the same TimingNode waits until the first one has finished;
5. another TimingNode may run at the same time.

In short:

```text
RFID callback ----+
operator command -+--> TimingNode A serial executor --> normal domain calls
timer callback ---+

other input ------+--> TimingNode B serial executor --> normal domain calls
```

The serial executor does not need a dedicated thread. It may use a shared
`ExecutorService`. The important rule is that two tasks for the same TimingNode
must never execute at the same time.

The initial constrained composition may use one shared worker. A desktop or
simulation composition may use more workers so different TimingNodes can run in
parallel.

#### Where input enters

External libraries may call the application from their own threads. Examples are HTTP,
WebSocket, shell, RFID, CAN, RabbitMQ and timer callbacks.

Those callback threads must not change mutable TimingNode state directly.

The application boundary determines which TimingNode(s) receive the work:

- `CommandHandler` handles presentation commands/queries that address a TimingNode;
- configured antenna mappings map an `AntennaId` to 1..N TimingNodes;
- configured connector bindings/names map a `BackofficeConnector` to 1..N TimingNodes;
- a scheduled task keeps the TimingNode target it was registered for.

Each resolved target is then submitted to that TimingNode's serial executor.
When one observation fans out to two TimingNodes, both receive their own queued
work and keep independent TimingNode-scoped state/sequence semantics.

There is no central generic `TimingSystemDispatcher`. The two routers above are
specific boundary responsibilities with real mapping ownership; they are not a
generic message bus or all-purpose mediator.

```text
operator endpoint
      |
      v
 CommandHandler ---------------------+
      |                              |
      v                              v
TimingNode A serial executor    TimingNode B serial executor
      ^                              ^
      |                              |
I/O mappings / timers resolve targets
```

<a id="fig-si01-04"></a>
![SI-01 runtime dispatch process](../assets/architecture/runtime-dispatch-process.svg)
*Figure SI01-04 — SI-01 runtime dispatch process.*

The source for this process view is
`docs/_diagrams/runtime-dispatch-process.yaml`.

#### Reads

A read does not automatically need the TimingNode serial executor.

Use the simplest rule that preserves correctness:

- application data that does not depend on mutable TimingNode state, such as the
  build/version identity, may be read directly;
- a read that must see an exact combination of mutable TimingNode values is run
  through that TimingNode's serial executor;
- presentation code must not gain write access to domain state just because it
  can read it.

The HTTP/status representation may later be built from values returned by the
application. The architecture does not require a Java class called
`ApplicationStatusSnapshot`, `ApplicationStatusModel` or any other specific
status helper merely to satisfy this rule.

#### Blocking I/O

Do not block the TimingNode serial executor on network, device or slow file I/O.

A normal flow is:

```text
TimingNode task
   |
   +--> request I/O
            |
            v
      I/O executor / external library
            |
            v
      completion/failure
            |
            +--> submit follow-up task to the owning TimingNode
```

If a domain transition depends on successful I/O, represent that pending state
explicitly and finish the transition when the completion comes back. Do not keep
the TimingNode blocked while waiting for the external operation.

#### Queue and failure behaviour

The queue in front of a TimingNode must be bounded in field use.

- accepted tasks are processed in submission order;
- a full queue is an explicit failure, never a silent drop;
- one task throwing an exception must not permanently stop later accepted work;
- queue depth/high-water information should be observable for diagnostics;
- exact queue sizes remain a configuration/verification decision.

#### Shutdown

Normal shutdown follows the same ownership rules:

1. stop accepting new client/device input;
2. stop or quiesce adapters;
3. allow already accepted TimingNode work to finish within a configured timeout;
4. finish required persistence/outbox work;
5. stop scheduler/I/O/state executors;
6. report failure if graceful shutdown cannot finish in time.

#### Architecture review cases

The concurrency design is reviewed against concrete cases rather than by adding
placeholder classes:

| Case | Required behaviour |
| --- | --- |
| Two commands arrive at the same TimingNode together | one runs, then the other; they never overlap |
| Commands arrive at two different TimingNodes | they may run concurrently |
| RFID callback arrives while an operator command changes the same TimingNode | callback work waits in the same TimingNode queue |
| Timer fires while that TimingNode is busy | timer work is queued for the same TimingNode |
| A handler throws | failure is reported; later accepted tasks can still run |
| TimingNode queue is full | submission fails visibly; work is not silently dropped |
| Blocking network/file/device operation is needed | I/O runs outside the TimingNode serial executor |
| I/O completion comes back on another thread | completion is submitted back to the owning TimingNode before changing state |
| A query needs an exact view of several mutable TimingNode values | query runs in that TimingNode serial executor |
| A client asks for application build/version | read directly; no TimingNode executor is involved |
| Shutdown starts with queued work | new ingress stops and accepted work gets a bounded chance to finish |
| Domain code calls another domain object while already inside the TimingNode task | use a normal direct Java call; do not send another command merely to preserve layers |

These cases are the basis for implementation tests of the serial-execution
mechanism and its callers.

#### Concurrency technology baseline

The selected baseline is deliberately small:

- JDK `java.util.concurrent`;
- one small project-owned serial-executor implementation per TimingNode;
- one shared configurable backing `ExecutorService`;
- separate I/O/scheduler execution when needed;
- direct/controllable executors in unit tests;
- no actor, reactive-stream or generic event-bus framework unless a later
  measured need justifies one.

### Time and clock architecture

Time is an explicit architecture concern rather than an incidental use of `Date`, `Calendar`, `LocalDateTime`, Java/SQL timestamp classes or raw millisecond values throughout the codebase.

#### `TimingTimestamp` value

The **Headless Timing Application** (SI-01) uses one dedicated immutable application/domain class named `TimingTimestamp` for externally meaningful absolute event times such as observations, registrations, start times and persisted/synchronised event timestamps.

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

TimingNodeId + SequenceNumber
  stable stream ordering / gap detection
```

A source sequence is not derived from a timestamp. Two registrations may have equal timestamps, and a wall-clock correction may even make a later observation carry an earlier absolute timestamp; source ordering must remain recoverable from source sequence semantics.

#### Architecture risk — wall-clock discontinuity and local-time ambiguity

This is an explicit architecture risk because timing software can produce plausible but incorrect results when local civil time and elapsed time are conflated.

| Risk | Possible consequence | Architectural mitigation / open work |
| --- | --- | --- |
| daylight-saving transition repeats or skips local civil times | ambiguous/non-existent local timestamps and wrong ordering if local time is persisted directly | persist/use absolute `TimingTimestamp`; perform local-zone conversion only at explicit boundaries; add DST transition tests |
| NTP, manual correction or platform synchronisation steps wall clock backwards/forwards | negative/large elapsed differences; a later observation can have an earlier wall-clock timestamp | use monotonic time for durations; source sequence for ordering; expose/inject wall clock; define correction/health policy |
| clock offset/drift differs between the application and external systems | incorrect elapsed/race-time calculations or reconciliation disagreement | define clock synchronisation/offset acceptance requirements and verification before timing accuracy is accepted |
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
  request a consistency-sensitive result from current TimingNode state
```

The exact Java interface/generic signatures remain implementation detail, but the semantic distinction should stay visible.

Rules:

- use typed messages when work crosses an asynchronous or TimingNode execution boundary;
- resolve the target explicitly; do not use a generic event bus or topic discovery;
- once running in a TimingNode's serial executor, use normal direct Java calls;
- submit asynchronous I/O completion back to the owning TimingNode before changing its state;
- RabbitMQ is external I/O, not an in-process message bus.

Choose concrete command/query return types when the first real consumers need them.

### Status and diagnostics architecture

Status is a first-class current-state model and is distinct from logging.

Status should allow presentation and diagnostics to observe application, timing-system and subsystem health without parsing log text. Representative areas include:

- application version / uptime / overall health;
- TimingNode lifecycle;
- registration asset/source state;
- TimingNode queue depth/high-water/overload health;
- RFID power/startup/protocol/heartbeat;
- CAN/device availability;
- persistence/backup state;
- race-data freshness;
- local clock/time-source health where relevant to timing validity;
- network/backoffice connectivity;
- inbound/outbound synchronisation state.

Status returned to a client is read-only from that client's point of view. The transport response does not define the internal Java class structure used to produce it.

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
                     |
                     +-- console handler
                     +-- file handler
                     +-- future live diagnostic handler
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
- stable TimingNode/data-source/device/correlation identifiers should be represented consistently in diagnostic messages/context, without making logging context the owner of application state;
- logging is not the mechanism for application status, registration history, audit/domain records or backoffice synchronisation state;
- the selected backend may publish the same log records to multiple handlers/sinks;
- the initial operational sink is file logging; a later diagnostic/debug presentation may add a live sink without changing framework logging calls;
- a live diagnostic sink is a support/presentation stream and must not become a substitute for the structured application-status model.

The exact field handlers, console/file split, rotation, retention and default level policy remain deployment/runtime configuration choices. They must be measured on the Pi Zero before being treated as accepted field defaults.

SLF4J 2.0.x is compatible with the Java-8 baseline; the implementation repository should pin the API/provider patch version together through Maven dependency management.

### Configuration and composition architecture

Configuration describes deployment/composition rather than domain behaviour hard-coded in source. The concrete deployment/configuration contract is owned by **IF-11** in `40-02-IDD-application-configuration.md`.

The main configuration groups are:

```text
ApplicationConfig
├── timingNodes
├── io
│   ├── hardware
│   ├── registrationRouting
│   ├── backoffice
│   │   └── 0..N connectors
│   └── storage
├── presentation
├── runtime
└── security
```

The identity boundaries are deliberate:

- a `TimingNode` owns its stable `TimingNodeId` and configured `LocationID`;
- the application may compose 0..N configured antennas; each antenna has its own `AntennaId` and may map to 1..N `TimingNodeId` targets;
- the application may compose 0..N backoffice connectors, each with 1..N TimingNode bindings;
- connector-specific external names/routing identities do not replace `TimingNodeId`;
- presentation endpoints reference TimingNodes explicitly; an HTTP port, tablet or shell binding is not a property of the TimingNode domain object.

Deployment composition is intentionally small:

```text
base application configuration
        +
one platform overlay
        +
optional one profile overlay
        +
resolved secret values
        =
effective ApplicationConfig
```

A profile such as `simulation` changes composition by selecting simulated adapters in place of real hardware/integration adapters. It does not introduce a second domain model or simulation-specific TimingNode semantics. Platform selection and profile selection remain separate concerns; for example, Windows does not imply simulation.

Startup follows three distinct responsibilities:

```text
load sources -> effective typed configuration -> validate references/settings -> compose application
```

Build provenance remains separate from deployment configuration. `BuildIdentity` describes the built artifact; it is not loaded from IF-11 deployment settings. The embedded provenance contains stable build inputs/context — version, exact revision, source ref, build origin and dirty-state — but deliberately omits wall-clock build time, CI run identifiers and actor/user data. This keeps the artifact self-identifying for test/support work without introducing per-run variability solely from timestamp/run metadata.

Working rules:

- keep secrets/credentials out of committed configuration and store only secret references there;
- prefer explicit/manual composition initially rather than adding a dependency-injection framework without a demonstrated need;
- keep overlay rules deliberately limited rather than creating general inheritance/includes;
- keep the concrete file syntax/library open until the first Step-3 implementation selects it;
- create Java configuration types only as real executable slices need them rather than mirroring the entire conceptual tree in advance.

### Data and persistence architecture

The initial architecture keeps application/domain state in memory and uses simple file-based persistence/restore rather than requiring an embedded database.

Keep these concepts distinct:

1. ingress/ordering — concurrency ownership;
2. registration ledger/source sequence — traceable domain/operational history;
3. prepare-team registry — current teams-to-prepare plus internal traceable history;
4. race/reference data — locally available participant/team/tag-reference input received from external sources;
5. absolute event time — project-owned `TimingTimestamp` semantics independent of local display time;
6. local backup/restore — restart/power-loss recovery;
7. backoffice outbox/synchronisation — pending external delivery/reconciliation.

Registration identity remains TimingNode-scoped; the current stable conceptual key is `(TimingNodeId, SequenceNumber)`.

Persistence durability semantics, file format, atomic-write strategy and corruption/recovery rules remain open decisions and may justify a focused data/persistence SDD only when implementation reaches that complexity.

### Integration architecture

The **external device and network topology is owned by the SSAD**, because RFID/CAN devices, local LAN clients, displays and backoffice are system-level deployment/interface relationships. This SAD starts at the **Headless Timing Application** (SI-01) boundary and explains how the application realises those system interfaces internally through ports, adapters, callbacks, status handling and transport implementations.

#### Backoffice

RabbitMQ is not the application-level backoffice API. The application depends on semantic source-aware ports, explicit TimingNode routing/bindings and local synchronisation/outbox behaviour. A process may compose 0..N backoffice connectors; RabbitMQ is one connector type.

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

CAN/device integrations follow the same rule: device/protocol callbacks enter the application through integration boundaries and application-facing messages. Display state remains in the application rather than in the display device.

Display V1 is a CAN-based integration. Display V2 is a network client that discovers the Headless Timing Application service on the local network and connects for synchronised display data. Exact protocol/session details remain deferred until implementation requires them.

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
  interfaces
    remoteapi
    console
    shell
    web          when implemented
  common
io
platform
```

Within presentation, functional interfaces own their transport-specific subpackages. External GUI or engineering clients consume the Remote API rather than creating transport packages inside SI-01.

Do not create future packages merely to mirror the architecture picture. Package structure becomes explicit only as real classes make ownership and dependency rules enforceable.

#### Public/private extension model

Private repositories may provide production RFID control, encrypted/proprietary protocol implementations, deployment mappings and production backoffice codecs. Public framework code defines supported contracts and must compile/test without those private implementations.

### Technology decision register

This table intentionally lives in the SAD because these choices shape the whole **Headless Timing Application** (SI-01) architecture.

| Concern | Current direction | Status / next evidence |
| --- | --- | --- |
| Java baseline | Java SE 8 is the current SI-01 baseline | accepted for current implementation; verify the selected runtime on the Pi target |
| Build | Maven | accepted |
| Concurrency | one project-owned `SerialExecutor` per `TimingNode` over shared configurable JDK executors | architecture baseline selected; keep defaults simple and tune only if evidence requires it |
| Internal messaging | typed immutable command/event/query objects only at async/ownership boundaries + explicit TimingNode mapping/routing at the owning boundary; no central generic dispatcher; direct calls inside a TimingNode task | architecture baseline selected; refine first consumer API signatures during implementation |
| Time model | dedicated project-owned immutable `TimingTimestamp` + injectable absolute clock + separate monotonic duration source | working direction; define precision/serialisation, sync and clock-correction policy |
| Dependency injection | explicit/manual composition initially | working direction; add framework only if complexity justifies it |
| Logging | SLF4J API in reusable framework; initial executable provider `slf4j-jdk14` / `java.util.logging` | architecture baseline selected; refine handlers/retention when runtime needs are known |
| Configuration | IF-11 effective `ApplicationConfig`: base + platform + optional profile + secret resolution | file syntax/library and first Java type set still open |
| Persistence | application/domain state + simple file persistence/restore | durability/file mechanics still open |
| Remote API HTTP | JDK `HttpServer` for the first IF-03 request/response slice | A06 baseline selected; transport belongs to the Remote API functional interface |
| Remote API WebSocket | `org.java-websocket:Java-WebSocket:1.6.0` on a dedicated configured listener | A07 baseline selected; Java 8+, pure Java/NIO and existing SLF4J boundary; keep A06 JDK `HttpServer` unchanged |
| Remote shell | Java 8 JDK `ServerSocket`, line-oriented TCP, shared A04 command semantics | A05 development/service baseline selected; one active session, reconnect allowed; SSH/Telnet/authentication deferred |
| Backoffice | semantic ports + socket test adapter + RabbitMQ production-shaped adapter | architecture direction established; implementation detail deferred |
| Test doubles | public controllable stubs through the same supported ports | established direction |

Technology choices should fit the actual application and target. Pi compatibility is verified on real hardware; memory/thread footprint becomes a design concern only when measurements make it one.

### Physical/deployment view

Representative **Headless Timing Application** (SI-01) deployments are:

```text
Production field host
  Raspberry Pi Zero / Zero W
    one Headless Timing Application process
      one or more configured TimingNode objects
      local devices + local files
      optional network/backoffice connectivity

Development/test host
  Linux or Windows
    same Headless Timing Application framework/application behaviour
    real or stub adapters
    may host larger multi-TimingNode simulation topology
```

The architecture should not require a different domain implementation for simulation. Different compositions select different adapters/topologies around the same application/domain behaviour. The system-level placement of the Headless Timing Application relative to devices, operator clients, LAN/Wi-Fi and backoffice is defined in the SSAD rather than duplicated here.

### Testability and failure/recovery architecture

Testability is an architecture property. Application/domain code should where practical:

- avoid uncontrolled threads and global mutable state;
- receive absolute time through an injectable abstraction;
- receive duration/timeout measurements through a controllable monotonic abstraction where needed;
- include tests that step the wall clock forwards/backwards and cross representative DST/local-time transitions;
- exercise `SerialExecutor` ordering, same-TimingNode non-overlap, cross-TimingNode parallelism and bounded-queue rejection deterministically;
- depend on semantic ports rather than concrete device/network libraries;
- keep protocol parsing in adapters;
- use deterministic handlers that can run synchronously in unit tests;
- expose observable status for degraded/failure conditions;
- avoid `Thread.sleep()` as a domain timing mechanism.

Fault handling should preserve local operation, traceability and explicit status. Exact retry counts, timeouts and durability guarantees belong to requirements or focused implementation design when evidence exists.

Detailed verification strategy belongs in `50-SVP-software-verification-plan.md`.

### Detailed-design documents

Keep this SAD as the main technical design for the **Headless Timing Application** (SI-01). Use a separate SDD only when
implementation detail would make the SAD harder to read.

Current active focused SDD:

```text
31-01-SDD-02-java-component-design.md
  Java packages, Maven artifacts and composition
```

Persistence/data and backoffice transport notes remain deferred until their
implementation needs focused design.

### Open architecture decisions

The next useful architecture work is to resolve concrete implementation choices, not create more document layers:

- TimingNode queue capacities and overload policy if real workloads show a need for explicit limits;
- field logging handlers, level defaults and rotation/retention;
- remote-shell technology;
- first concrete command/query submission/result API signatures;
- `TimingTimestamp` representation/precision/serialisation and equality/comparison semantics;
- wall-clock synchronisation, correction detection and the operational policy for a material forward/backward clock step;
- concrete configuration file syntax/library and first Java configuration type boundaries;
- persistence commit/durability/atomic-write/recovery policy;
- concrete Java runtime/vendor/version for the Pi target;
- status/health vocabulary and publication model;
- exact public API/SPI boundaries as real consumers appear;
- RabbitMQ connection/channel/retry strategy when that integration becomes active;
- whether there is ever a concrete reason to move beyond the current Java 8 baseline.


---

## Java component, package and artifact detailed design

**Source document:** [31-01-SDD-02-java-component-design.md](31-01-SDD-02-java-component-design.md)

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

The current Java structure should grow from real code, not from the architecture
diagram.

Likely top-level packages are:

```text
io.github.brainboxemb.eventtiming/
  application/
  domain/
  core/
  presentation/
    interfaces/
      remoteapi/
        http/
        websocket/
        messages/
      console/
      shell/
      web/              only when implemented
    common/
      terminal/
  io/
    hardware/
    messaging/
    storage/
  infra/
  platform/
```

Presentation subpackages are organised by **functional interface first**. HTTP/WebSocket are implementation transports inside a functional interface, not global presentation categories. `presentation.common` is only for behaviour shared by more than one presentation interface.

These are source-organisation boundaries, not automatically Maven modules.

Use these rules:

- create a class only when current behaviour needs it;
- keep small enums with the object that owns them until reuse justifies a
  separate type;
- do not create marker classes to represent layers;
- place a type by what it means, not by which layer happens to call it;
- use capability-oriented subpackages when a domain concept has a main object plus
  closely related value/supporting types; keep that small group together rather
  than introducing generic `helper`, `model` or single-type `identity`
  subpackages;
- split a capability package further only when multiple cohesive sub-capabilities
  exist in real code;
- reserve `infra` for concrete cross-cutting technical support such as
  `BuildIdentity`;
- use `io` for external hardware, messaging and storage adapters.

For example, the first TimingNode implementation is grouped as:

```text
domain/
  timing/
    TimingNode.java
    TimingNodeId.java
```

If this capability later grows into several cohesive areas, deeper packages such
as `timing/registration` or `timing/stage` may become useful. Do not create
those packages before the corresponding code exists.

An IDD response shape does not require an equally shaped internal Java object.
For example, the status JSON does not by itself require classes named
`ApplicationStatusSnapshot` or `ApplicationStatusModel`.

### Contract placement

Place contracts with the responsibility that owns their meaning:

```text
presentation
  functional client interfaces / transport mapping / wire messages

application
  commands, queries and application-level ports

domain
  domain model and semantic ports

core
  runtime/execution contracts

io
  hardware, messaging and storage adapters

infra
  cross-cutting technical support

platform
  execution-environment abstractions
```

Do not create one generic top-level `api` package merely to collect
interfaces.

### Internal dependency direction

```text
presentation --> application
application  --> domain / core / I/O ports
io           --> application/domain ports + platform
core         --> reusable runtime mechanics
platform     --> low-level environment only
```

Domain code does not depend on presentation or concrete I/O adapters.
Executable composition may depend on the complete supported framework surface
and selected external libraries.

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
  -> obtain embedded BuildIdentity
  -> load effective ApplicationConfig
  -> validate configuration
  -> select/construct concrete presentation/I/O/platform implementations
  -> create reusable application/domain/core objects
  -> start lifecycle
  -> install shutdown handling
```

`BuildIdentity` and `ApplicationConfig` are different inputs. Build identity is artifact provenance; application configuration is deployment composition defined by IF-11. The executable embeds deterministic provenance fields (`application`, `version`, exact `revision`, `sourceRef`, `buildOrigin`, `dirty`, `apiVersion`). Wall-clock build time, CI run/build id and actor/user are not embedded because they are per-run metadata rather than stable build inputs/context.

Reusable application behaviour should not migrate into the executable merely because the architectural responsibility is called `application`. When a reusable framework application/runtime object becomes justified by real shared behaviour, executables should **compose** that object rather than extend a `BaseApplication` hierarchy.

The current executable uses a small nested composition helper:

```java
TimingApplication.builder(buildIdentity).build()
```

This builder is an executable-composition convenience, not a new architecture layer. It should construct only currently real collaborators and grow only when concrete composition needs appear. `ApplicationConfigLoader` now owns the implemented Step-3 YAML parsing/validation, while `ApplicationConfig` and the currently real presentation config types remain executable-composition inputs rather than domain objects.

The implemented presentation structure is:

```text
presentation/
  interfaces/
    console/
      LocalConsole
    shell/
      RemoteShellServer
    remoteapi/
      http/
        RemoteApiHttpServer
      websocket/
        RemoteApiWebSocketServer
      messages/
        RemoteApiMessageWriter
  common/
    terminal/
      TerminalSession
```

Console and remote shell are separate presentation interfaces. They share only the
line-oriented command-session behaviour in `presentation.common.terminal`; both call
the same `CommandHandler` and shutdown callback.

A06/A07 are the first slice of the functional **Remote API**:

```text
RemoteApiHttpServer
  +-- GET /api/v1/version
  +-- GET /api/v1/status
            \
             +--> CommandHandler.version() / status()
            /
RemoteApiWebSocketServer
  +-- WS /api/v1/events
  +-- STATUS_SNAPSHOT on connect/reconnect
  +-- STATUS_CHANGED only for real status changes
```

`RemoteApiMessageWriter` owns the IF-03 wire/JSON representation shared by the Remote
API HTTP and WebSocket transports. It is not application/control logic and therefore
does not live in the application layer or in global presentation common code.

The first WebSocket implementation uses `Java-WebSocket 1.6.0` in the reusable
framework and keeps the accepted A06 JDK HTTP server unchanged rather than replacing
both transports with a larger combined stack.

A browser-based engineering client, if added, should consume the Remote API like any other external client. It does not require a separate SI-01 `presentation.web` package.

Manual inspection is provided by an independent development tool:

```text
test-client/
  TestClientApplication      plain Java launcher
          |
          v
  TestClientFxApplication    JavaFX development view
          |
          +-- RemoteApiClient          HTTP/JSON client
          +-- RemoteApiEventClient       Java 17 WebSocket client
          +-- RemoteShellClient          A05 raw TCP shell client
          |
          v
        SI-01
```

`test-client/` is a standalone Java-17 Maven project, not a module in the Java-8
SI-01 reactor. It has no dependency on `event-timing-framework` or
`event-timing-app`; this preserves the external-client boundary and makes later
extraction to a dedicated repository straightforward if the tool grows. It is engineering support rather than the planned SI-02 GUI, and its JavaFX choice does not select the SI-02 GUI technology.

The shared presentation/application boundary remains small:
`CommandHandler.version()` returns build identity and
`CommandHandler.status()` returns the current TimingNode status used by the
current presentation adapters.

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
- product-specific I/O/protocol implementations;
- production asset/source inventory and mappings;
- production backoffice schemas/codecs where sensitive;
- deployment-specific composition/policies.

Prefer normal composition and constructor/factory injection. Do not introduce a subclass-based `BaseApplication` extension model or runtime plugin discovery unless a real requirement appears.

### Possible future artifacts

Create future artifacts only when a real boundary requires them. Candidates might eventually include:

- RabbitMQ/messaging I/O;
- Linux/Raspberry-Pi platform support;
- public/private RFID/CAN I/O implementations;
- stable Java API/SPI;
- reusable test support.

Splitting later is preferred over speculative libraries, provided package/responsibility boundaries remain clean enough to extract.

### Architecture/dependency checks

Useful automated rules may include:

- presentation packages do not own or persist application state;
- domain services do not reference presentation or concrete I/O classes;
- platform packages do not depend on event-timing application/domain behaviour;
- wire/protocol classes stay with their presentation or I/O capability;
- semantic contracts are not moved into transport packages merely because transport code uses them;
- public code contains no real deployment mappings or proprietary values;
- the executable consumes `event-timing-framework` rather than copying/forking framework source;
- the framework artifact does not carry a concrete SLF4J provider/backend transitively;
- an executable runtime contains exactly one intended SLF4J provider.

### Open detailed-design decisions

- exact package granularity after real application/domain classes exist;
- final package naming where capability-oriented packages prove clearer than layer names;
- exact reusable boundary between single-instance runtime mechanics and multi-system application orchestration;
- how applications select/inject presentation/I/O/platform implementations;
- private Maven artifact publication/consumption mechanism;
- version alignment between public framework and private implementations;
- which I/O capabilities eventually deserve independent artifacts;
- whether and when a dedicated public Java API/SPI artifact becomes justified;
- exact field logging configuration/rotation/retention policy in the default executable.


---

## GUI Application Architecture (SAD)

**Source document:** [31-02-SAD-gui-application-architecture.md](31-02-SAD-gui-application-architecture.md)

Status: working draft / non-authoritative

Software item: **Desktop GUI Application** (SI-02)

This Software Architecture Document describes the initial architecture direction for the planned desktop GUI. The GUI is a separate software item from the **Headless Timing Application** (SI-01) and communicates with it through system-defined network interfaces.

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

### Relationship to the current JavaFX test client

The current JavaFX test client is an engineering/manual-integration tool for IF-03. It is
**not** the first implementation of SI-02 and does not select the GUI toolkit, runtime or
packaging for SI-02.

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

These operations are handled by the **Headless Timing Application** (SI-01). The GUI sends commands and presents state; it does not duplicate timing-domain business rules.

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

The future SRD for the **Desktop GUI Application** (SI-02) can reference the applicable GUI-IDD clauses as requirements instead of copying the interface definition into the software-item requirements.

### Software-to-software interface IDD

A separate system-level IDD should define the communication interface between the **Desktop GUI Application** (SI-02) and **Headless Timing Application** (SI-01).

Current direction:

- HTTP/JSON for commands, queries and initial snapshots;
- WebSocket for live status/data events;
- explicit versioning/compatibility of the interface;
- connection/reconnection semantics;
- authentication/authorisation when defined;
- stale-data behaviour;
- errors/result semantics.

The same interface is also used by engineering/test tools. A small browser-based test client may consume it later without becoming another software item.

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
- whether the GUI uses the same Java baseline as the **Headless Timing Application** (SI-01) or can use a newer runtime;
- configuration storage for known endpoints;
- authentication/credential storage;
- update mechanism.

The Raspberry Pi Java-8 constraint applies to the headless timing application. It does **not automatically require** the desktop GUI to use Java 8; that should be a separate software-item decision.


---

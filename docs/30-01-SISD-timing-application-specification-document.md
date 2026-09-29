# Timing Application Specification Document (SISD)

Status: working/review baseline

Software item: **SI-01 — Headless Timing Application**

This Software Item Specification Document combines the SI-01 software requirements and
software-item architecture in one versionable baseline. Requirement identifiers remain
`SI01-REQ-...`; architecture elements and focused SDDs remain traceable to those
requirements without creating a release dependency between a separate SRD and SAD.

## Inputs

The SI-01 specification is derived from upstream software-system authority:

- `04-UC-system-use-cases.md` for applicable operational intent;
- `20-SSSD-software-system-specification-document.md` for SI-01 allocation,
  software-system constraints and interface ownership;
- `21-01-IDD-application-control-status.md` for IF-03 obligations;
- `21-02-IDD-application-configuration.md` for IF-11 obligations.

`03-domain-baseline.md` supplies shared terminology/domain facts. It is supporting
source knowledge rather than a substitute for a released requirement/interface baseline.

The **SIP is not an input** to this specification: it chooses when accepted capability is
implemented. The **SVP is not an input** either: it defines how accepted requirements and
interfaces are verified. Focused SDDs are downstream design refinements of this SISD.

When documents are independently released, each released SISD shall identify the exact
revision/version of its SSSD and IDD inputs. While this repository releases the document
set together, the repository release/tag/commit is the shared baseline identifier.

## Software-item requirements

### Requirement identifier convention

Requirements in this slice use:

```text
SI01-REQ-<number>
```

Identifiers in this review candidate are intended to remain stable. A later capability should add requirements without renumbering these merely for document neatness.

### First-executable requirements

#### Process lifecycle and configuration

**SI01-REQ-001 — Start from external configuration**  
SI-01 shall start using externally supplied configuration rather than requiring production/deployment values to be compiled into application code. The deployment/configuration contract is defined by IF-11.

**SI01-REQ-002 — Clean process shutdown**  
SI-01 shall support a controlled shutdown path that terminates the first-executable runtime without requiring forced process termination during normal operation/testing.

```{req} Minimal TimingNode composition
:id: SI01-REQ-003
:derived_from: UC-001, UC-014

The first executable shall support configuration of at least
one `TimingNode` with a stable `TimingNodeId` that can be
represented in application status.
```

IF-11 defines how a configured TimingNode is referenced from presentation and I/O configuration while keeping `TimingNodeId`, registration-asset identity and antenna identity distinct. Detailed operational RFID behaviour remains outside this first slice.

#### Build and version identity

**SI01-REQ-010 — Single application build identity**  
A running SI-01 process shall expose one authoritative application build/version identity derived from the produced application artifact/build.

**SI01-REQ-011 — Consistent identity across interfaces**  
The build/version identity exposed through supported first-executable operator/application interfaces shall represent the same underlying build identity rather than interface-specific copies.

The public representation and required fields are defined by IF-03.

#### Status

```{req} Authoritative current status snapshot
:id: SI01-REQ-020
:derived_from: UC-001, UC-008

SI-01 shall maintain an authoritative current application
status model that is separate from log output.
```

```{req} Minimum first-executable status content
:id: SI01-REQ-021
:derived_from: UC-001, UC-008

The first-executable status shall expose enough information
to determine at least:

- application/build identity;
- application state;
- configured `TimingNode` `TimingNodeId` value(s);
- the current minimal lifecycle state represented for those
  TimingNodes;
- explicit degraded/error information for first-executable
  configuration/startup failures that remain observable
  while the process can continue serving status.
```

The concrete IF-03 schema is defined by `21-01-IDD-application-control-status.md`.

```{req} Equivalent status semantics across first interfaces
:id: SI01-REQ-022
:derived_from: UC-008

Local console, remote-shell and IF-03
application-control/status representations shall be derived
from the same application status semantics. A transport
adapter shall not maintain a separate authoritative status
model.
```

**SI01-REQ-023 — Status-change publication**  
SI-01 shall publish first-executable status-change information through IF-03 WebSocket/event delivery from the same authoritative status model used for status queries.

On connection/reconnection the client shall be able to recover a complete authoritative snapshot according to the IF-03 contract.

#### Application boundary and testability

```{req} Shared application behaviour
:id: SI01-REQ-030

Transport-specific adapters shall invoke shared SI-01
application commands/queries rather than implementing
independent copies of version/status behaviour.
```

```{req} Externally testable executable
:id: SI01-REQ-031

The produced SI-01 application shall support ST-1
verification as a separate running process through its
public application interface without direct test mutation of
internal application/domain state.
```

**SI01-REQ-032 — Safe default network exposure**  
The first-executable IF-03 service shall default to local/loopback-only access. Non-loopback listening shall require explicit configuration until a later security/interface baseline defines production exposure and authentication policy.

**SI01-REQ-033 — Compatible first API evolution**  
SI-01 shall implement IF-03 `v1` such that compatible additions can be made without requiring clients to understand every newly added JSON member or event type; breaking interface semantics shall not silently redefine the existing `v1` contract.

### First-executable lifecycle interpretation

The first executable is not yet an operational timing implementation.

Therefore:

- application state may move through `STARTING`, `RUNNING`, `DEGRADED` and `STOPPING` according to IF-03;
- at least one configured minimal `TimingNode` is represented;
- that TimingNode reports lifecycle `CLOSED` in this slice;
- operational open/close commands and resulting registration-stream events remain deferred to the later domain increment.

This prevents the first version/status executable from inventing partial operational semantics merely to make a demo look more complete.

### Explicitly deferred requirements

The following areas are intentionally not made concrete by this SISD slice:

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

These areas remain in the use-case/working-specification baseline until a later planned increment promotes their requirements.

### Traceability view

| Requirement | Upstream authority | Interface/design allocation | Planned verification |
| --- | --- | --- | --- |
| SI01-REQ-001/002 | UC-001; SSSD deployment/operability allocation | IF-11 + SI-01 composition/runtime | build/start/stop + ST-1 process control |
| SI01-REQ-003 | UC-001/014; SSSD software-item topology | IF-11 + SI-01 runtime composition | `VC-ST1-001` status inspection |
| SI01-REQ-010/011 | UC-008/009; SSSD IF-03 allocation | IF-01/02/03; shared query boundary | V2/V3 + `VC-ST1-001` |
| SI01-REQ-020/021/022 | UC-001/008/009; SSSD status/control allocation | Status service/model + IF-01/02/03 | V1/V2 + `VC-ST1-001` |
| SI01-REQ-023 | UC-008/009; IF-03 live-event obligation | IF-03 WebSocket/event adapter | V2/V3 + `VC-ST1-001` |
| SI01-REQ-030/031 | UC-008/009/014; SSSD interface/testability separation | shared application boundary | architecture/component checks + `VC-ST1-001` |
| SI01-REQ-032 | IF03-REQ-002/009 | Remote API binding/configuration | configuration/interface verification |
| SI01-REQ-033 | IF03-REQ-010 | interface compatibility/evolution | contract/component verification |

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

A chosen implementation technology must satisfy this SISD and IF-03 rather than redefining them.

## Software-item architecture

### Architecture drivers

The **Headless Timing Application** (SI-01) architecture is driven by these concerns:

- run on the original Raspberry Pi Zero / Zero W target; actual runtime/resource constraints are established by measurement;
- remain usable on Linux/Windows development and test hosts;
- keep timing/domain state in the application;
- support one or more logical TimingNodes without state leakage;
- preserve deterministic ordering of state-changing work;
- isolate external I/O concurrency from application/domain state mutation;
- preserve unambiguous time semantics across local time zones, daylight-saving transitions and wall-clock corrections;
- remain testable without production RFID, CAN, upstream/backoffice or proprietary implementations;
- expose one coherent command/query/status/event model to local and network presentation adapters;
- support local persistence/recovery and disconnected operation;
- keep public framework/reference code independent of private production source;
- avoid framework complexity that is not justified by the application.

### +1 scenarios used to validate the architecture

The existing use cases in `04-UC-system-use-cases.md` are the scenario source. The SISD should not create a second competing use-case catalogue.

Representative architecture-validation scenarios include:

1. start the **Headless Timing Application** (SI-01), load configuration, expose version/status and shut down cleanly;
2. accept an operator command through local or network presentation and route it to the correct logical TimingNode;
3. accept a device observation from an external callback without allowing that callback thread to change application state directly;
4. persist accepted operational state and recover it after restart;
5. continue local operation while a GUI/test client or upstream connection is unavailable;
6. host several TimingNodes in a development/simulation composition without state leakage;
7. substitute public stubs for production devices/transports while exercising the same application/domain paths;
8. capture and process observations correctly when local civil time crosses a daylight-saving transition or the operating-system wall clock is corrected forwards/backwards.

These scenarios are used to check the logical, process, development and deployment views below.

### Logical view

#### Layered application architecture

The primary logical view is a responsibility/layer view. It describes semantic ownership and dependency direction; it does **not** prescribe one Maven artifact per layer.

`TimingApplication` is the top-level framework runtime object. The cross-cutting `ApplicationBootstrap` framework component owns startup composition from an already parsed/validated deployment configuration: it constructs the selected presentation/I/O/platform implementations and reusable application/domain objects, and then starts the runtime. The runnable `event-timing-app` artifact remains a thin launcher/input adapter that reads concrete YAML/build-resource inputs and delegates to the framework. `TimingApplication` is therefore not itself a component inside the application layer, and bootstrap is not a normal runtime layer or mandatory call path.

The compact software/domain ownership model is intentionally also kept as copyable text:

```text
TimingApplication
  +-- ApplicationId
  +-- SystemStatus
  |
  +-- 1..N TimingNode
        +-- TimingNodeId
        +-- LocationID
        +-- lifecycle / status
        +-- UpstreamMessagePort
        +-- TagProcessor
        +-- StageStartTimes
        +-- Journal
        +-- NextUpTeams
        +-- RaceData
        +-- StageTiming
```

<a id="fig-si01-01"></a>
![SI-01 layered architecture](../../../raw/prod/docs/assets/architecture/layered-architecture.svg)
*Figure SI01-01 — SI-01 layered architecture.*

The source for this view is `docs/_diagrams/layered-architecture.yaml`.

The Domain/I/O boundary is deliberately **shaped rather than a rigid horizontal
layer cake**. Domain has extra space below its contained components and yields
through a lower-right polygon cut-away. I/O uses a complementary polygon with a
raised right shoulder around Devices. A small visible gap remains between both
layer outlines, so neither responsibility appears to overlap the other. This
expresses architectural proximity/cohesion only; it does not permit Domain to
depend on concrete I/O.

#### Presentation

Presentation owns client-facing interfaces and their external representations. Its structure is **functional interface first, transport second**:

```text
presentation/
  interfaces/
    console/
    shell/
    web/
    remoteapi/        primary Remote API transport/message classes
  common/
    terminal/         behaviour genuinely shared by console + shell
```

```{arch} Remote API
---
id: RemoteApi
satisfies: >-
  SI01-REQ-031, IF03-REQ-001, IF03-REQ-002,
  IF03-REQ-004
---

The **Remote API** is the general programmable interface of
the **Headless Timing Application** (SI-01) for remote
clients, engineering tools and headless
black-box/integration tests. A06/A07 implement only its
first version/status/event slice; later supported control
and diagnostic operations grow inside the same functional
interface.
```

**Web** is modelled separately as the browser-facing presentation interface of SI-01. The intended runtime topology is one configured Web endpoint per TimingNode, so an application with 1..N TimingNodes exposes 1..N Web bindings/ports. Each Web binding references its TimingNode by `TimingNodeId`; the bind address/port remains presentation configuration and is not a property of the TimingNode domain object. Web may reuse application queries/events and transport facilities, but it is not collapsed into the Remote API merely because both can use HTTP/WebSocket technology.

**Console** and **RemoteShell** also remain separate presentation interfaces. They share a common terminal-handling responsibility for command parsing/session behaviour where that behaviour is genuinely identical; the shared `SharedTerminalHandler` component then converges on the same `CommandHandler` as the other presentation interfaces.

`presentation.common` is reserved for behaviour genuinely shared across presentation interfaces. Terminal behaviour shared by Console and RemoteShell belongs under `presentation.common.terminal`. Remote API HTTP, WebSocket and wire-message mapping remain together at the `interfaces.remoteapi` component package root while that implementation is still small; deeper transport/message subpackages are introduced only when they contain a real cohesive decomposition.

Presentation converts external requests to application calls and application results to client representations. It does not own mutable application/domain state.

#### Application

The application responsibility coordinates use cases:

```text
application/
  Conductor
    lifecycle and application-wide coordination

  CommandHandler
    shared presentation command/query boundary

  UpstreamMessageRouter
    upstream-only application/domain target resolution and routing
```

```{arch} Conductor
:id: Conductor

`Conductor` coordinates application-wide lifecycle and
active TimingNodes.
```

```{arch} CommandHandler
---
id: CommandHandler
satisfies: >-
  SI01-REQ-022, SI01-REQ-030, SI01-REQ-031,
  IF03-REQ-001, IF03-REQ-004
---

`CommandHandler` is the shared entry point for presentation
requests. It may serve simple application reads such as
`version()`. Application-wide operations delegate to
`Conductor` where lifecycle or cross-node coordination is
required. When a presentation command or query names a
`TimingNodeId`, `CommandHandler` resolves that `TimingNode`
and submits state-changing work directly to its serial
executor; `Conductor` is not a mandatory hop for
TimingNode-scoped work.
```

Once code is executing for a TimingNode, normal direct Java calls are preferred;
do not introduce messages merely to preserve a layer diagram. Upstream messaging
is the explicit exception: `UpstreamMessageRouter` owns target resolution for
messages exchanged with the upstream system at application scope. **Upstream**
describes that external system relationship, not the direction of an individual
message; the exchange is bidirectional. It routes
application-scoped upstream messages to the relevant domain responsibility and
TimingNode-scoped messages by `TimingNodeId` to that node's
`UpstreamMessagePort`. It is deliberately **not** a generic application message
bus or mediator for normal collaboration between domain components.

#### Domain

The domain owns timing rules and TimingNode state:

```text
TimingNode
  TimingNodeId
  LocationID
  State
  UpstreamMessagePort
  TagProcessor
  StageStartTimes
  Journal
  NextUpTeams
  RaceData
  StageTiming
```

`TimingNode` is the top-level domain class for one timing location. It owns its
identity (`TimingNodeId` and `LocationID`), lifecycle/state, and the per-node
components shown beneath it in Figure SI01-01.

`UpstreamMessagePort` is the bidirectional upstream-message boundary of one
TimingNode. Its name identifies the relationship with the upstream system; it
does not imply that every message travels away from the TimingNode. Inbound messages have already been resolved to that TimingNode by
`UpstreamMessageRouter`; state-changing handling executes through the
TimingNode's serial boundary and delegates to the relevant TimingNode
responsibilities. Outbound TimingNode messages leave through the same semantic
port and return to `UpstreamMessageRouter` for application/upstream routing. The
port owns no transport connection, connector lifecycle or cross-node target
resolution.
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
  Devices
    AntennaManager
      Antenna (0..N)
        Vendor1Antenna
    Display
      DisplayRev1Can
      DisplayRev2Wifi
    Keypad
      KeypadRev1Can

  DeviceNetworks
    CanNetworkController
    NetworkDeviceService

  Messaging
    UpstreamGateway
      Connector (1..N)
        RabbitMqConnector
        SocketConnector

  Storage
    file
    db
```

Presentation stays separate because it owns client-facing API/view semantics.
I/O owns the external boundary and its mapping to TimingNodes. In Figure SI01-01
Domain and I/O both use explicit polygon outlines. The I/O outline rises around
Devices, so Devices remains completely inside its owning layer while being drawn
beside the lower Domain area. The normal I/O band and its Storage, Messaging and
DeviceNetworks cards stay compact because they no longer need to inherit the
height required by Devices. The contained Storage, Devices, Messaging and
DeviceNetworks elements carry
packaging-component notation where the package-like ownership/decomposition
semantics are meaningful. For compactness, Figure SI01-01 shows their contained
software components as an indented hierarchy rather than as nested component
boxes; `UpstreamGateway` remains a software component owned by Messaging.

The high-level I/O view separates **Devices** from **DeviceNetworks**.

`Devices` groups the software components that represent external device roles in
SI-01. `AntennaManager` owns the configured 0..N `Antenna` components and the
coordination needed when multiple physical antennas form one registration input
path. `Vendor1Antenna` is a concrete antenna implementation. `Display` and
`Keypad` name the software-facing device roles; `DisplayRev1Can`,
`DisplayRev2Wifi` and `KeypadRev1Can` are concrete variants. These names
describe software components/implementations, not the physical devices themselves.

`DeviceNetworks` owns the communication/network responsibilities used to reach
those devices. `CanNetworkController` owns CAN-bus lifecycle, discovery/scanning,
online state and CAN-device communication. `NetworkDeviceService` owns the
bidirectional network-device boundary for smart/network-attached devices: SI-01
can expose data outward and receive device-originated messages/events inward.

Service discovery, connection/session handling and protocol framing are
subordinate design concerns of `NetworkDeviceService`, not peer components in
the high-level architecture. The current IF-09 direction may use mDNS and a
client-initiated IP session, but `NetworkDeviceService` itself is not Wi-Fi
specific and does not own smart-display rendering/domain behaviour.

When upstream messaging is configured, SI-01 composes one `UpstreamGateway`
inside I/O/Messaging. The gateway uses 1..N connectors and owns the external
upstream-system boundary plus connector-facing message exchange. A concrete connector
owns its transport resources and protocol/session mechanics.
`UpstreamMessageRouter` in the application layer owns application/domain target
resolution instead of placing that responsibility in I/O.

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

Cross-cutting technical concerns include logging, diagnostics, metrics and
build/version identity. In Java, `infra` is reserved for concrete cross-cutting
support such as `BuildIdentity`; it is not the I/O layer.

`ApplicationBootstrap` is shown as a small concrete framework component inside the
cross-cutting area because startup composition touches several normal layers
without becoming a layer itself. It consumes the effective `ApplicationConfig`,
selects and wires concrete presentation, I/O and platform implementations,
creates the reusable application/domain objects, and initiates startup/shutdown
handling. Concrete configuration-file parsing belongs to the executable input
adapter. Normal runtime interactions do not route through bootstrap after
composition is complete.

### Principal runtime abstractions

```{arch} TimingNode
:id: TimingNode
:satisfies: SI01-REQ-003, SI01-REQ-020, SI01-REQ-021

A `TimingNode` is the primary independently addressed
operational/domain aggregate inside the **Headless Timing
Application** (SI-01). One application process may host one
or more TimingNodes. `SystemStatus` is application-scoped
and aggregates/monitors overall runtime and TimingNode
status rather than belonging to one TimingNode.
```

The architecture deliberately uses **separate views** for software/domain decomposition, hardware/deployment topology and configuration/identity mapping. These views must not be collapsed into one ownership tree.

#### Software/domain decomposition

```text
TimingApplication
  +-- ApplicationId
  +-- SystemStatus
  |
  +-- 1..N TimingNode
        +-- TimingNodeId
        +-- LocationID
        +-- lifecycle / status
        +-- UpstreamMessagePort
        +-- TagProcessor
        +-- StageStartTimes
        +-- Journal
        +-- NextUpTeams
        +-- RaceData
        +-- StageTiming
```

`ApplicationId` identifies the running Headless Timing Application instance.
`TimingNodeId` is the stable identity of a `TimingNode` and scopes its
registration sequence, persistence and synchronisation semantics. The two
identities remain separate types/namespaces even when their configured string
values are equal. For the current single-TimingNode deployment style, using the
same configured value for `ApplicationId` and `TimingNodeId` is the intended
starting convention. `LocationID` is the separately configured physical event
location.

<a id="fig-si01-02"></a>
![SI-01 software/domain decomposition](../../../raw/prod/docs/assets/architecture/timing-node-software-decomposition.svg)
*Figure SI01-02 — SI-01 software/domain decomposition.*

The exact Java class/package boundaries may evolve as implementation evidence appears, but the `TimingNode` aggregate is the semantic owner of the operational TimingNode state. The physical registration asset is not a child component of this software tree.

#### Devices and device-network topology

The high-level I/O model separates device concepts from the communication
responsibilities that serve them:

```text
Devices
  +-- Antenna (0..N)
  +-- DisplayRev1Can
  +-- Keypad
  +-- DisplayRev2Wifi

Device Networks
  +-- CanNetworkController
  +-- NetworkDeviceService
```

An `Antenna` remains an I/O source with its own `AntennaId` and concrete
driver/connection settings. Grouping it under Devices does not change its
TimingNode routing semantics: one antenna may intentionally feed one or more
TimingNodes.

`CanNetworkController` represents the actively managed CAN network rather than
one particular CAN device. `NetworkDeviceService` represents the general
bidirectional service boundary for network-attached devices. It may support
outbound SI-01 data and inbound device requests/events without requiring the
device/domain object itself to know about sockets, discovery or transport
sessions.

The current smart-display direction remains client initiated: SI-01 makes its
service discoverable and DisplayRev2Wifi connects to it. The exact discovery,
listener/session and packet-framing design belongs below this high-level view.

#### Configuration, routing and identity mapping

Configuration connects identities without collapsing them:

```text
TimingApplication
    +-- ApplicationId

Devices
    +-- Antenna (0..N)
    |     +-- each Antenna -> 1..N TimingNodeId
    +-- DisplayRev1Can
    +-- Keypad
    +-- DisplayRev2Wifi

Device Networks
    +-- CanNetworkController
    +-- NetworkDeviceService

Messaging
    +-- UpstreamGateway
          +-- Connector (1..N)

UpstreamMessageRouter
    +-- application-scoped upstream target -> Domain responsibility
    +-- TimingNodeId -> TimingNode.UpstreamMessagePort
```

<a id="fig-si01-03"></a>
![TimingNode, hardware and upstream-system messaging routing](../../../raw/prod/docs/assets/architecture/timing-node-routing-mapping.svg)
*Figure SI01-03 — TimingNode, hardware and upstream-system messaging routing.*

`TimingNodeId` is the stable identity of a `TimingNode` and scopes its sequence, persistence and synchronisation semantics. `LocationID` and `AntennaId` are separate namespaces.

Configured antenna mappings associate each `AntennaId` with one or more TimingNodes. Fan-out is explicit: if one antenna feeds two TimingNodes, each target TimingNode processes the observation through its own serialized state boundary and keeps its own TimingNodeId-scoped sequence/state while the original `AntennaId` remains available as context.

CAN and smart-network controllers are not alternate presentation layers. They are
I/O/device-network responsibilities. A keypad or display may present information
to a human, but it is still an external device from SI-01's architecture
perspective.

`UpstreamGateway` is the I/O upstream-messaging boundary. It exchanges
transport-neutral messages with its configured connectors but does not resolve
those messages to application/domain targets. `UpstreamMessageRouter` owns that
application-level target resolution: an application-scoped upstream message can
be routed to the relevant Domain responsibility (for example `SystemStatus`),
while a `TimingNodeId` target resolves to that TimingNode's
`UpstreamMessagePort`.

Connectors do not route directly to Domain or TimingNodes and do not own domain
semantics. A connector-specific external name or routing key may participate in
boundary mapping, but it does not replace `ApplicationId` or the stable
internal `TimingNodeId`. One gateway may use multiple connectors and one
TimingNode may exchange messages through more than one connector via the gateway,
router and its bidirectional port.

`ApplicationId` establishes the separate addressable identity for
application-scoped upstream messages. That does not require a synthetic
application-level `UpstreamMessagePort`; `UpstreamMessageRouter` can route such
messages directly to the appropriate application/domain responsibility.

Runtime-wide infrastructure may be shared where that does not leak mutable TimingNode state. Candidates include backing executors, logging infrastructure, HTTP server infrastructure, shared connector infrastructure, configuration loading and network monitoring.

Stable domain facts behind these views are maintained in `03-domain-baseline.md`; this SISD owns their software-architecture composition and execution implications.

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
- configured device/antenna mappings map an `AntennaId` to 1..N TimingNodes;
- `CanNetworkController` owns CAN discovery/state and converts device callbacks into application-facing work;
- `NetworkDeviceService` owns bidirectional network-device communication; discovery/session mechanics stay below this high-level responsibility;
- `UpstreamMessageRouter` resolves upstream targets: application-scoped messages go to the relevant Domain responsibility and `TimingNodeId` messages go to the matching TimingNode's `UpstreamMessagePort`;
- a scheduled task keeps the TimingNode target it was registered for.

Each resolved target is then submitted to that TimingNode's serial executor.
When one observation fans out to two TimingNodes, both receive their own queued
work and keep independent TimingNode-scoped state/sequence semantics.

There is no central generic `TimingSystemDispatcher`. `CommandHandler`,
antenna mapping and upstream messaging remain separate boundary responsibilities.
`UpstreamMessageRouter` is specifically for target resolution on the
bidirectional upstream-system relationship; it is not a generic message bus or
all-purpose mediator. `UpstreamGateway` remains the I/O upstream-system
boundary and connector owner.

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
![SI-01 runtime dispatch process](../../../raw/prod/docs/assets/architecture/runtime-dispatch-process.svg)
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
- network/upstream connectivity;
- inbound/outbound synchronisation state.

Status returned to a client is read-only from that client's point of view. The transport response does not define the internal Java class structure used to produce it.

Logging records diagnostic/history information; status represents current operational state. One must not be used as a substitute for the other.

### Logging architecture

Logging is a SISD architecture-level cross-cutting technology decision because it affects almost every
component, operational diagnostics, footprint and engineering support.

The A08 baseline keeps framework logging calls independent from the concrete runtime backend:

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
                     +-- ConsoleHandler
                     +-- rotating FileHandler
                     +-- LiveLogHandler
                              |
                              v
                     DiagnosticLogServer
                              ^
                              |
                    engineering client connects
```

Working decisions:

- reusable framework code logs through the SLF4J API;
- `event-timing-framework.jar` depends on `slf4j-api` only and must not impose a provider/backend on consumers;
- the executable composition selects exactly one provider;
- the initial Java-8/Pi-Zero application composition uses `slf4j-jdk14`, delegating to the JDK `java.util.logging` backend;
- the default executable owns the concrete JUL handler/server composition; changing that composition must not require domain/framework logging calls to change;
- the startup configuration defines one global semantic log level; the A08 baseline uses the normal `TRACE / DEBUG / INFO / WARN / ERROR` vocabulary and maps it to the selected backend;
- `LoggingControl` owns the current global level and may apply a **temporary runtime override**. A runtime override is intentionally not written back to `application.yml` and resets to the configured level on restart;
- the durable operational sink is a human-readable rotating file log with configured size limit and retained generations;
- console logging remains available for local startup/development feedback;
- an optional `DiagnosticLogServer` accepts a connection initiated by the JavaFX engineering client and streams new log records through a dedicated diagnostics channel;
- the same diagnostics connection may query/change the temporary runtime log level; this control remains logging-specific rather than becoming a generic application command bus;
- live delivery is best effort: a missing, slow or disconnected engineering client must not block TimingNode/application execution, and live records need not be retained for later replay;
- the file sink is the retained source for historical operational logs; A08 does not add an in-memory log-history model or ring buffer;
- the live diagnostics channel is **separate from IF-03 `/api/v1/events`**. Log records are diagnostics, not application/domain status events;
- high-frequency observations should not automatically produce one INFO record per observation; detailed per-observation diagnostics belong at controlled diagnostic levels while current health/counters remain part of status/metrics;
- stable TimingNode/data-source/device/correlation identifiers should be represented consistently in diagnostic messages/context, without making logging context the owner of application state;
- logging is not the mechanism for application status, registration history, audit/domain records or upstream synchronisation state;
- Logback/reload4j or another backend is not part of the baseline unless later operational requirements justify it.

<a id="fig-si01-05"></a>
![Runtime logging and live diagnostics](../../../raw/prod/docs/assets/architecture/runtime-logging.svg)
*Figure SI01-05 — Runtime logging, retained file sink and engineering live diagnostics.*

The exact default file size, retention count and production log level remain deployment choices
and must be measured on the target platform before being treated as accepted field defaults.
Per-package levels, persistent runtime overrides, JSON file logging and a general-purpose
diagnostics framework are outside A08.

SLF4J 2.0.x is compatible with the Java-8 baseline; the implementation repository should pin
the API/provider patch version together through Maven dependency management.

### Configuration and composition architecture

Configuration describes deployment/composition rather than domain behaviour hard-coded in source. The concrete deployment/configuration contract is owned by **IF-11** in `21-02-IDD-application-configuration.md`.

The main configuration groups are:

```text
ApplicationConfig
├── applicationId
├── timingNodes
├── io
│   ├── devices
│   │   └── antennas
│   ├── deviceNetworks
│   │   ├── can
│   │   └── network
│   ├── registrationRouting
│   ├── messaging
│   │   └── upstream
│   │       └── connectors (1..N when UpstreamGateway is configured)
│   └── storage
├── presentation
├── logging
├── runtime
└── security
```

The identity boundaries are deliberate:

- the application owns a stable `ApplicationId`;
- a `TimingNode` owns its stable `TimingNodeId` and configured `LocationID`;
- `ApplicationId` and `TimingNodeId` are different identities, but a single-TimingNode deployment may intentionally configure the same value for both;
- the high-level I/O model separates Devices from Device Networks;
- Devices names the functional device endpoints/concepts, including antennas, passive CAN devices and smart network devices;
- the application may compose 0..N configured antennas; each antenna has its own `AntennaId` and may map to 1..N `TimingNodeId` targets;
- Device Networks contains `CanNetworkController` for the actively managed CAN network and `NetworkDeviceService` for bidirectional network-device communication;
- when upstream messaging is configured, the application composes one `UpstreamGateway` using 1..N connectors;
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
7. upstream outbox/synchronisation — pending external delivery/reconciliation.

Registration identity remains TimingNode-scoped; the current stable conceptual key is `(TimingNodeId, SequenceNumber)`.

Persistence durability semantics, file format, atomic-write strategy and corruption/recovery rules remain open decisions and may justify a focused data/persistence SDD only when implementation reaches that complexity.

### Integration architecture

The **external device and network topology is owned by the SSSD**, because RFID/CAN devices, local LAN clients, displays and the upstream system are system-level deployment/interface relationships. This SISD starts at the **Headless Timing Application** (SI-01) boundary and explains how the application realises those system interfaces internally through ports, adapters, callbacks, status handling and transport implementations.

#### Upstream messaging

Upstream messaging is a semantic application boundary, not a RabbitMQ API.
`UpstreamGateway` owns the external upstream-system boundary across 1..N transport
connectors. `UpstreamMessageRouter` owns application/domain target resolution.
A TimingNode-targeted message is resolved by `TimingNodeId`, submitted through
that TimingNode's serial boundary and enters/leaves the TimingNode through its
bidirectional `UpstreamMessagePort`.

```text
external upstream system
        |
        +--> RabbitMqConnector --+
        +--> SocketConnector ----+--> UpstreamGateway
                                      |
                                      v
                               UpstreamMessageRouter
                                  |             |
                      application/domain       +--> TimingNodeId
                            target                     |
                              |                        v
                              v                  TimingNode
                         SystemStatus              UpstreamMessagePort
```

Connectors own transport/session mechanics and protocol-specific mapping at the
external boundary. Exact RabbitMQ connection/channel topology, routing keys and
retry mechanics are connector-level decisions and should be detailed when that
implementation is active. Product/deployment-specific upstream-system names and private
wire details remain outside the public architecture documentation.

`ApplicationId` is used for application-scoped upstream addressing.
`UpstreamMessageRouter` provides that application-level routing without adding a
generic application message handler merely to complete the symmetry. Additional
domain handling is introduced only when a concrete application-scoped
message capability is actually implemented.

#### RFID

RFID integration is an adapter boundary. Raw callbacks/protocol data do not directly mutate application state. The adapter is responsible for protocol/device interaction and turns accepted observations/health changes into typed application-facing messages.

Decoding must retain public semantic tag classification (normal/reserve/test) even if proprietary prefix/encryption details stay in a private codec. Reserve resolution and test-tag policy are domain/use-case concerns rather than reasons for the adapter to silently rewrite every decoded tag to one normal identity.

Power/startup/recovery lifecycle and filtering semantics are architectural concerns where they affect application behaviour; exact protocol commands, crypto/proprietary codecs and retry sequences remain implementation/private detail.

#### CAN, keypad and displays

`CanNetworkController` owns the active CAN network: bus lifecycle, discovery/scanning,
device online state and communication. CAN/device callbacks do not mutate
TimingNode state directly; accepted work crosses the normal application/serial
boundary.

`DisplayRev1Can` is the passive CAN display generation. SI-01 owns the
display-specific `DisplayModel` for this path and actively translates that model
into CAN/device commands. The display does not own the ready-team/domain model.

`DisplayRev2Wifi` is deliberately different. It is a smart external client with
its own rendering and synchronisation behaviour. `NetworkDeviceService` provides the bidirectional network-device boundary.
In the current IF-09 design it makes the SI-01 data service discoverable and
accepts the session initiated by DisplayRev2Wifi. DisplayRev2Wifi owns
reconnect/resynchronisation behaviour. The concrete discovery/listener/session
mechanics are detailed below the high-level architecture rather than represented
as additional peer components.

SI-01 therefore publishes current timing/status/reference data to smart clients;
it does **not** drive DisplayRev2Wifi through the passive-display `DisplayModel`
and does not need to know how that smart display renders the data. Exact mDNS
service names and the application protocol (for example TCP/WebSocket) remain
deferred until IF-09 implementation needs them.

#### Connectivity

Status must distinguish at least local network reachability from external/upstream session health where those distinctions affect operator decisions. Temporary external connectivity loss must not silently invalidate otherwise available local operation.

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

Private repositories may provide production RFID control, encrypted/proprietary protocol implementations, deployment mappings and production upstream/backoffice codecs. Public framework code defines supported contracts and must compile/test without those private implementations.

### Technology decision register

This table intentionally lives in the architecture section of this SISD because these choices shape the whole **Headless Timing Application** (SI-01) architecture.

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
| Upstream messaging | semantic ports + socket test adapter + RabbitMQ production-shaped adapter | architecture direction established; implementation detail deferred |
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
      optional network/upstream connectivity

Development/test host
  Linux or Windows
    same Headless Timing Application framework/application behaviour
    real or stub adapters
    may host larger multi-TimingNode simulation topology
```

The architecture should not require a different domain implementation for simulation. Different compositions select different adapters/topologies around the same application/domain behaviour. The system-level placement of the Headless Timing Application relative to devices, operator clients, LAN/Wi-Fi and the upstream system is defined in the SSSD rather than duplicated here.

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

Keep this SISD as the main technical design for the **Headless Timing Application** (SI-01). Use a separate SDD only when
implementation detail would make the architecture section of this SISD harder to read.

Current active focused SDD:

```text
31-01-SDD-02-java-component-design.md
  Java packages, Maven artifacts and composition
```

Persistence/data and upstream transport notes remain deferred until their
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

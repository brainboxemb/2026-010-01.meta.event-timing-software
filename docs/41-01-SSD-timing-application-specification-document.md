# Timing Application Specification Document (SSD)

Status: working/review baseline

Software item: **SI-01 — Timing Point Application**


## Purpose

This document combines the SI-01 requirements and architecture in one baseline.
Requirements keep their `SI01-REQ-...` identifiers. Detailed SDDs build on this
architecture instead of repeating it.

## Terms and abbreviations

- **SSD** — Software Specification Document
- **SI** — Software Item
- **SSSD** — Software System Specification Document
- **ISD** — Interface Specification Document
- **SDD** — Software Design Description


## Relationship to other documents

The SI-01 specification consumes the software-system allocation and the interface obligations that apply to SI-01:

- `31-SSSD-software-system-specification-document.md` for SI-01 allocation and software-system constraints;
- `32-03-ISD-application-control-status.md` for IF-03 obligations;
- `32-04-ISD-web-interface.md` for IF-04 Web interface obligations;
- `32-05-ISD-timingdata-interchange.md` for IF-05 TimingData obligations;
- `32-11-ISD-application-configuration.md` for IF-11 obligations;
- applicable parent/external-system inputs registered by `20-EXT-external-system-inputs.md` when an obligation is allocated directly to SI-01.

`30-UC-system-use-cases.md` provides operational traceability. If SI-01 behaviour later benefits from a separate software-item use-case decomposition, that may be added as an optional software-item use-case document and referenced here; its numbering range will be assigned when such documents are actually introduced, rather than reusing the SSD/SDD ranges.

`03-domain-baseline.md` supplies shared terminology/domain facts. It is supporting source knowledge rather than a substitute for a released requirement/interface baseline.

When documents are independently released, each released SSD shall identify the exact revision/version of its SSSD, applicable external inputs and ISD inputs. While this repository releases the local document set together, the repository release/tag/commit is the shared local baseline identifier.

## Design boundary

Use this SSD for the **requirements and architecture** of SI-01: what the main
parts are responsible for, how they relate, and which constraints detailed
design must respect.

Implementation detail is split over focused SDDs:

| Document | What belongs there |
| --- | --- |
| `43-01-SDD-01-data-and-display-design.md` | internal data/runtime behaviour: LogBook recording, commit ordering, persistence/recovery algorithms, query isolation, prepare-team/reference/display data |
| `43-01-SDD-02-java-component-design.md` | concrete Java realisation: modules, packages, classes/interfaces, queue/executor/thread choices, provider discovery and dependency enforcement |
| `43-01-SDD-03-backoffice-transport-design.md` | concrete transport realisation below the system/upstream semantic boundary |
| applicable ISD | externally visible interface/file/protocol requirements/semantics; an SDD shall not redefine them |

An SDD may choose the concrete mechanism, as long as it still fits this SSD and
the applicable ISD. Keep class names, queue types, worker threads, file-recovery
steps and package layout out of the SSD unless they change the architecture.

## Software-item requirements

### Requirement identifier convention

Requirements in this slice use:

```text
SI01-REQ-<number>
```

Identifiers in this review candidate are intended to remain stable. A later capability should add requirements without renumbering these merely for document neatness.

### First-executable requirements

#### Process lifecycle and configuration

:::{req} Start from external configuration  
:id: SI01-REQ-001  
:status: R  

SI-01 shall start using externally supplied configuration rather than requiring production/deployment values to be compiled into application code. The deployment/configuration contract is defined by IF-11.
:::

:::{req} Clean process shutdown  
:id: SI01-REQ-002  
:status: R  

SI-01 shall support a controlled shutdown path that terminates the first-executable runtime without requiring forced process termination during normal operation/testing.
:::

:::{req} Minimal TimingSystem / TimingNode composition  
:id: SI01-REQ-003  
:status: R  
:derived_from: UC-001, UC-014  

The first executable shall support configuration of at least
one internal `TimingSystem` containing at least one
`TimingNode` with a stable `TimingNodeId` that can be
represented in application status.
:::

IF-11 defines the internal TimingSystem/TimingNode configuration hierarchy and how a configured TimingNode is referenced from presentation and I/O configuration while keeping `TimingSystemId` internal and `TimingNodeId`, antenna identity and location identity distinct. Detailed operational RFID behaviour is owned by its functional requirements and device/input design rather than by the configuration contract.

#### Build and version identity

:::{req} Single application build identity  
:id: SI01-REQ-010  
:status: R  

A running SI-01 process shall expose one authoritative application build/version identity derived from the produced application artifact/build.
:::

:::{req} Consistent identity across interfaces  
:id: SI01-REQ-011  
:status: R  

The build/version identity exposed through supported first-executable operator/application interfaces shall represent the same underlying build identity rather than interface-specific copies.
:::

The semantic build identity is defined by IF-03. The current v1 wire fields are defined by `33-03-IDD-api-http-websocket.md`.

#### Status

:::{req} Authoritative current status snapshot  
:id: SI01-REQ-020  
:status: R  
:derived_from: UC-001, UC-008  

SI-01 shall maintain an authoritative current application
status model that is separate from log output.
:::

:::{req} Minimum first-executable status content  
:id: SI01-REQ-021  
:status: R  
:derived_from: UC-001, UC-008, UC-020  

The first-executable status shall expose enough information
to determine at least:

- application/build identity;
- application state;
- configured `TimingNode` `TimingNodeId` value(s);
- the current operational state represented for those TimingNodes;
- explicit degraded/error information for contained first-executable
  configuration/startup failures, including the affected TimingNode identity and
  a machine-readable problem indication while the process continues serving status.
:::

The IF-03 status semantics are defined by `32-03-ISD-application-control-status.md`; the current wire schema is defined by `33-03-IDD-api-http-websocket.md`.

:::{req} Equivalent status semantics across first interfaces  
:id: SI01-REQ-022  
:status: R  
:derived_from: UC-008  

Local console, remote-shell and IF-03
application-control/status representations shall be derived
from the same application status semantics. A transport
adapter shall not maintain a separate authoritative status
model.
:::

:::{req} Status-change publication  
:id: SI01-REQ-023  
:status: R  

SI-01 shall publish first-executable status-change information through IF-03 live-event delivery from the same authoritative status model used for status queries.
:::

On connection/reconnection the client shall be able to recover a complete authoritative snapshot according to the IF-03 contract.

#### Application boundary and testability

:::{req} Shared application behaviour  
:id: SI01-REQ-030  
:status: R  

Transport-specific adapters shall invoke shared SI-01
application commands/queries rather than implementing
independent copies of version/status behaviour.
:::

:::{req} Externally testable executable  
:id: SI01-REQ-031  
:status: R  

The produced SI-01 application shall support ST-1
verification as a separate running process through its
public application interface without direct test mutation of
internal application/domain state.
:::

:::{req} Safe default network exposure  
:id: SI01-REQ-032  
:status: R  

The first-executable IF-03 service shall default to local/loopback-only access. Non-loopback listening shall require explicit configuration until a later security/interface baseline defines production exposure and authentication policy.
:::

:::{req} Compatible first API evolution  
:id: SI01-REQ-033  
:status: R  

SI-01 shall implement IF-03 so compatible additions can be introduced without silently changing existing operation or value semantics; breaking interface semantics shall require a new major interface version or an explicitly documented compatible migration.
:::

#### First registration operation

:::{req} Operational location and lifecycle  
:id: SI01-REQ-040  
:status: R  
:derived_from: UC-001, UC-002, UC-008, UC-009  

SI-01 shall expose the current operational `LocationId` and `OPEN`/`CLOSED`
state. Every normal OPEN application command shall carry the requested valid LocationId.
For a CLOSED TimingNode SI-01 shall apply that LocationId and the CLOSED-to-OPEN
transition as one ordered operation, then keep the active location fixed while OPEN.
The normal application-control boundary shall not require a separate Set Location
operation before OPEN.
:::

:::{req} Accepted semantic registration operation  
:id: SI01-REQ-041  
:status: R  
:derived_from: UC-003, UC-009  

SI-01 shall provide one application/domain operation for an already-accepted
semantic registration. The caller supplies the supported registration action, resolved
`RegistrationId` and accepted `time`; SI-01 supplies its own source identity, active
`LocationId` and next committed sequence before committing the TimingData value. The
first implemented automatic-registration action is `ADD`; additional actions require
defined TimingData semantics before they are supported.
:::

:::{req} Committed registration observability  
:id: SI01-REQ-042  
:status: R  
:derived_from: UC-003, UC-009, UC-011  

SI-01 shall make committed registration TimingData observable through current
history and live post-commit notification without exposing uncommitted records
as committed state.
:::

:::{req} Capability-gated dev auto-reg  
:id: SI01-REQ-043  
:status: R  
:derived_from: UC-009  

The dev auto-reg control shall be usable only when
SI-01 advertises that the corresponding engineering capability is both supported
and enabled. This control enters at the accepted semantic registration boundary
and shall not let the client supply final TimingData, source sequence, active
LocationId or source identity.
:::

:::{req} Reconnect rebuild before live presentation  
:id: SI01-REQ-044  
:status: R  
:derived_from: UC-009  

After IF-03 reconnect, an engineering/operator client shall be able to rebuild
current status and committed registration history before treating subsequent
updates as a live view. Duplicate TimingData observed through history plus live
delivery shall be identifiable by Node ID together with sequence number.
:::

:::{req} Reference TimingData representation support  
:id: SI01-REQ-045  
:status: D  
:derived_from: UC-011, IF05-REQ-001, IF05-REQ-002, IF05-REQ-003, IF05-REQ-004, IF05-REQ-005, IF05-REQ-006, IF05-REQ-007  

SI-01 shall support the current reference TimingData representation defined by
`33-05-IDD-timingdata-interchange.md` for local persistence and engineering
interchange. For every supported record type, encoding and decoding shall
preserve the applicable IF-05 semantic values.
:::

:::{req} Write TimingData before commit completion  
:id: SI01-REQ-046  
:status: D  
:derived_from: UC-003, UC-012  

SI-01 shall successfully write one complete TimingData record to the configured
local TimingData store before completing that TimingData commit. Only after
that write succeeds may SI-01 add the record to committed LogBook state,
publish a committed live event or report the commit as successful.

If the write fails or remains incomplete, the commit shall fail and the record
shall not be treated as committed.
:::

:::{req} Restore committed TimingData after restart  
:id: SI01-REQ-047  
:status: D  
:derived_from: UC-013, IF05-REQ-002, IF05-REQ-003, IF05-REQ-007  

On startup, SI-01 shall rebuild each configured TimingNode's committed TimingData
history from valid complete persisted records in sequence-number order before
accepting new TimingData commit work for that TimingNode. The next sequence
shall be 1 when no committed record exists, otherwise the last committed
sequence plus 1.

Recovery of committed TimingData shall not by itself restore the previous
operational Location ID or OPEN state.
:::

:::{req} Reject invalid TimingData recovery input  
:id: SI01-REQ-048  
:status: D  
:derived_from: UC-013  

When recovering the current reference representation, SI-01 shall not treat an
incomplete trailing record as committed. A malformed complete record,
unsupported representation version, Node ID mismatch, duplicate sequence,
sequence gap or sequence regression shall produce an explicit recovery failure
for that TimingNode rather than being silently skipped or renumbered.
:::

:::{req} Contain TimingNode recovery failure  
:id: SI01-REQ-049  
:status: D  
:derived_from: UC-020  

After application-level configuration has been accepted, a failure while restoring
or validating recoverable state for one configured TimingNode shall be contained to
that TimingNode where continued application operation remains safe.

SI-01 shall:

- place the affected TimingNode in `ERROR` instead of presenting it as `CLOSED`
  or `OPEN`;
- reject normal state-changing and registration operations for that TimingNode;
- continue starting/running the application and its diagnostic presentation
  interfaces;
- keep independently healthy TimingNodes available in a multi-node composition; and
- expose the contained failure through the authoritative application status model.

Failures of mandatory application-wide configuration or infrastructure that prevent
safe construction of the diagnostic runtime are outside this containment rule.
:::

:::{req} Use maximum-RSSI tag observation for registration  
:id: SI01-REQ-050  
:status: D  
:derived_from: UC-003  

SI-01 shall use the tag observation with the maximum RSSI as the registration observation
and shall finalize that selection after a configured timeout without a new observation.
:::

For this requirement, the registration time is the original timestamp of the selected
observation. The timeout closes the observation group; it does not replace the selected
maximum-RSSI observation with the last observation. A maximum group duration, equal-RSSI
tie handling and implementation scheduling belong to the detailed design.

This requirement does not introduce a minimum-RSSI rejection threshold.

:::{req} Keep local registration independent from presentation, diagnostic logging and backoffice delivery  
:id: SI01-REQ-051  
:status: D  
:derived_from: UC-003, UC-012  

SI-01 shall not require presentation clients, diagnostic logging or backoffice
delivery for a local RFID registration to be accepted and committed. Failure or
unavailability of those functions shall not by itself stop an operational TimingNode
from accepting and committing local registrations.
:::

:::{req} Contain antenna startup and runtime failure  
:id: SI01-REQ-052  
:status: D  
:derived_from: UC-003  

At application startup SI-01 shall attempt a health probe for every configured
antenna. Failure of one configured antenna shall not by itself prevent health
probing or later operation of other independently healthy configured antennas.
The failed antenna shall remain represented as unavailable or in error.
:::

:::{req} Couple antenna operation to assigned TimingNode state  
:id: SI01-REQ-053  
:status: D  
:derived_from: UC-001, UC-003  

A healthy configured antenna shall provide inventory while at least one TimingNode
assigned to that antenna is OPEN. When no assigned TimingNode is OPEN, SI-01 shall
stop inventory for that antenna and release or power down the antenna according to
its configured installation lifecycle.
:::

:::{req} Multiplex mutually exclusive antenna inventory  
:id: SI01-REQ-054  
:status: D  
:derived_from: UC-003  

For antennas configured in the same inventory mutual-exclusion group, SI-01 shall
keep at most one healthy group member inventorying at a time and shall rotate
inventory between available group members using the configured inventory interval.
Failure of one group member shall not stop remaining healthy group members.
:::

### Lifecycle interpretation

The first registration baseline uses the following TimingNode operational-state semantics:

- at least one configured TimingNode is represented;
- a TimingNode that cannot safely complete contained startup recovery is represented
  as `ERROR` and does not accept normal operational commands;
- explicit LocationId assignment is allowed only while CLOSED;
- normal OPEN carries the requested valid LocationId and applies that LocationId
  together with the CLOSED-to-OPEN transition as one ordered operation;
- a restarted TimingNode begins CLOSED with no current operational location;
- the current location cannot change while OPEN;
- an accepted semantic registration can commit only while OPEN;
- committed registration history and live post-commit updates are observable
  through the applicable presentation interface;
- physical RFID observation/filtering is outside the accepted-registration
  application operation.

### Traceability view

| Requirement | Upstream authority | Interface/design allocation |
| --- | --- | --- |
| SI01-REQ-001/002 | UC-001; SSSD deployment/operability allocation | IF-11 + SI-01 composition/runtime |
| SI01-REQ-003 | UC-001/014; SSSD software-item topology | IF-11 + SI-01 runtime composition |
| SI01-REQ-010/011 | UC-008/009; SSSD IF-03 allocation | IF-01/02/03; shared query boundary |
| SI01-REQ-020/021/022 | UC-001/008/009; SSSD status/control allocation | Status service/model + IF-01/02/03 |
| SI01-REQ-023 | UC-008/009; IF-03 live-event obligation | IF-03 event adapter |
| SI01-REQ-030/031 | UC-008/009/014; SSSD interface/testability separation | shared application boundary |
| SI01-REQ-032 | IF03-REQ-002/009 | API binding/configuration |
| SI01-REQ-033 | IF03-REQ-010 | interface compatibility/evolution |
| SI01-REQ-040 | UC-001/002/008/009 | TimingNode + IF-03/IF-04 control/status |
| SI01-REQ-041/043 | UC-003/009 | TimingNode accepted-registration operation + IF-03 engineering control |
| SI01-REQ-042/044 | UC-003/009/011 | LogBook/TimingData event + IF-03 bounded history/event delivery |
| SI01-REQ-045 | UC-011 + IF05-REQ-001..007 + 33-05-IDD | reference TimingData codec/persistence boundary |
| SI01-REQ-046 | UC-003/012 | local TimingData commit ordering |
| SI01-REQ-047 | UC-013 + IF05-REQ-002/003/007 | startup TimingData recovery |
| SI01-REQ-048 | UC-013 + 33-05-IDD | reference-store recovery validation |
| SI01-REQ-049 | UC-020 + SI01-REQ-021/022 + IF03-REQ-017 | degraded TimingNode containment + diagnostic status |
| SI01-REQ-050 | UC-003 | RFID passage aggregation + strongest-observation selection |
| SI01-REQ-051 | UC-003/012 | local registration independent from presentation, diagnostic logging and backoffice delivery |
| SI01-REQ-052 | UC-003 | per-antenna startup/runtime failure containment + observable antenna health |
| SI01-REQ-053 | UC-001/003 + IF-11 antenna mapping | TimingNode-driven antenna inventory/power lifecycle |
| SI01-REQ-054 | UC-003 + IF-11 antenna manager policy | mutually exclusive antenna inventory scheduling |

## Software-item architecture

### Architecture drivers

The **Timing Point Application** (SI-01) architecture is driven by these concerns:

- run on the original Raspberry Pi Zero / Zero W target; actual runtime/resource constraints are established by measurement;
- remain usable on Linux/Windows development and test hosts;
- keep timing/domain state in the application;
- support 1..N internal TimingSystems, each with 1..N logical TimingNodes, without state leakage;
- preserve deterministic ordering of state-changing work;
- isolate external I/O concurrency from application/domain state mutation;
- keep the local registration work from antenna observation through TagProcessor,
  TimingNode queue admission, the required TimingData write and LogBook commit
  independent from presentation, diagnostic logging and backoffice delivery;
- preserve unambiguous time semantics across local time zones, daylight-saving transitions and wall-clock corrections;
- remain testable without production RFID, CAN, upstream/backoffice or proprietary implementations;
- expose one coherent command/query/status/event model to local and network presentation adapters;
- support local persistence/recovery and disconnected operation;
- keep the public reference/core implementation independent of private production source;
- allow selected concrete implementations to be supplied through a small Java-8-compatible provider/extension mechanism without making normal domain/application code plugin-aware;
- avoid reusable-core or extension complexity that is not justified by the application.

### +1 scenarios used to validate the architecture

The existing use cases in `30-UC-system-use-cases.md` are the scenario source. The SSD should not create a second competing use-case catalogue.

Representative architecture-validation scenarios include:

1. start the **Timing Point Application** (SI-01), load configuration, expose version/status and shut down cleanly;
2. accept an operator command through local or network presentation and route it to the correct logical TimingNode;
3. accept a device observation from an external callback without allowing that callback thread to change application state directly;
4. persist accepted operational state and recover it after restart;
5. continue local operation while a GUI/test client or upstream connection is unavailable;
6. host several independent TimingSystems, each with one or more TimingNodes, in a development/simulation composition without state leakage;
7. substitute public stubs for production devices/transports while exercising the same application/domain paths;
8. capture and process observations correctly when local civil time crosses a daylight-saving transition or the operating-system wall clock is corrected forwards/backwards.

These scenarios are used to check the logical, process, development and deployment views below.

### Logical view

#### Layered application architecture

The primary logical view is a responsibility/layer view. It describes semantic ownership and dependency direction; it does **not** prescribe one Maven artifact per layer.

:::{arch} TimingApplicationRuntime  
:id: TimingApplicationRuntime  

`TimingApplicationRuntime` is the top-level Runtime composition and lifecycle
owner for one running SI-01 process. It constructs and owns the concrete object
graph from validated effective configuration, including the Domain, I/O,
Application, Platform and Presentation runtime parts. Composition is behaviour
of this runtime object, not a separate architectural component.
:::

:::{arch} PresentationRuntime  
:id: PresentationRuntime  

`PresentationRuntime` is the Runtime-owned child that contains the concrete
presentation adapters and their lifecycle. It activates after the core
Domain/I/O/Application graph is ready and deactivates before those dependencies
are torn down.
:::

:::{arch} RuntimeExecutors  
:id: RuntimeExecutors  

`RuntimeExecutors` owns the physical execution resources used by the logical
component lanes. It owns worker lifecycle but not Domain/Application semantics.
:::

The executable has one visible composition flow. From validated configuration it proceeds in a deliberately simple order:

```text
resolve effective configuration
  -> create PlatformEnvironment
  -> construct Runtime resources
  -> construct Domain, I/O, Application and Presentation objects
  -> wire cross-component relationships
  -> Runtime execution resources start
  -> components activate in explicit order
       Domain / I/O / Application / Presentation
```

Construction itself must not start physical application worker threads or install hidden cross-component behaviour. Cross-component application coordination is owned by `Conductor` and is connected explicitly before component activation. Concrete Presentation adapters are also composed here rather than in the executable launcher. Deactivation follows ownership in reverse order, followed by closing Runtime execution resources. Normal application/domain interactions do not route through the composition responsibility after activation. Presentation, I/O, Platform and Infrastructure objects keep their semantic layer ownership even though Runtime composition creates them.

The compact software/domain ownership model is intentionally also kept as copyable text:

```text
Application
  +-- ApplicationId
  |
  +-- 1..N TimingSystem
        +-- TimingSystemId        internal composition/simulation identity
        +-- SystemStatus          complete current system overview
        +-- UpstreamMessagePort   system-level upstream messages
        +-- UpstreamProtocol
        |     +-- heartbeat / ping
        |     +-- synchronisation / reconciliation
        +-- 1..N TimingNode
              +-- TimingNodeId   functional upstream/timing-data identity
              +-- LocationId
              +-- lifecycle / status
              +-- UpstreamMessagePort
              +-- TagProcessor
              +-- StageStartTimes
              +-- LogBook
              |     +-- 0..N TimingData
              +-- NextUpTeams
              +-- RaceData
              +-- StageTiming
              +-- uses / produces TimingData

Shared Domain contracts:
  +-- EventData
  +-- TimingData
```

<a id="fig-si01-01"></a>
![SI-01 layered architecture](../../../raw/prod/docs/assets/architecture/layered-architecture.svg)
*Figure SI01-01 — SI-01 layered architecture.*

The source for this view is `docs/_diagrams/layered-architecture.yaml`.

In Figure SI01-01, `TimingSystem` and `TimingNode` are shown as UML-style
component/aggregate containers. They are the architecture identities themselves,
not UML class declarations. A small neutral inner property block lists the
important identity/state concepts owned by each aggregate, without its own title,
stereotype or component glyph; it therefore does not prescribe Java fields or a
concrete class shape. Geometric containment plus the `TimingNode (1..N)` label
expresses that one TimingSystem owns 1..N TimingNodes.

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
    api/        primary API transport/message classes
  common/
    terminal/         behaviour genuinely shared by console + shell
```

:::{arch} API  
---
id: Api
satisfies: >-
  SI01-REQ-031, IF03-REQ-001, IF03-REQ-002,
  IF03-REQ-004
---

The **API** is the general programmable interface of
the **Timing Point Application** (SI-01) for remote
clients, engineering tools and headless
black-box/integration tests. A06/A07 implement only its
first version/status/event slice; later supported control
and diagnostic operations grow inside the same functional
interface.
:::

:::{arch} Web  
:id: Web  

**Web** is the browser-facing presentation interface of SI-01. Each configured
`TimingNode` has exactly one Web binding and therefore one configured Web
listener port. The binding targets that TimingNode; its bind address/port remains
Presentation configuration and is not a property of the TimingNode domain
aggregate. A multi-TimingNode process therefore exposes 1..N Web ports. Web may
reuse application queries/events and transport facilities, but it is not
collapsed into the API merely because both can use HTTP/WebSocket
technology.
:::

:::{arch} Console  
:id: Console  

`Console` is the local text presentation interface. It delegates common
terminal parsing/session behaviour to `SharedTerminalHandler` and reaches
application behaviour through the shared `PresentationGateway`; it does not own
application/domain state.
:::

:::{arch} RemoteShell  
:id: RemoteShell  

`RemoteShell` is the remote text presentation interface. It shares terminal
session behaviour with Console through `SharedTerminalHandler` while remaining
a separate external interface and transport concern.
:::

:::{arch} SharedTerminalHandler  
:id: SharedTerminalHandler  

`SharedTerminalHandler` owns command parsing and terminal-session behaviour that
is genuinely shared by Console and RemoteShell. It converges those interfaces on
the same `PresentationGateway` used by other presentation interfaces.
:::

`presentation.common` is reserved for behaviour genuinely shared across
presentation interfaces. Terminal behaviour shared by Console and RemoteShell
belongs under `presentation.common.terminal`. API HTTP, WebSocket and
wire-message mapping remain together at the `interfaces.api` component
package root while that implementation is still small; deeper transport/message
subpackages are introduced only when they contain a real cohesive decomposition.

Presentation converts external requests to application calls and application results to client representations. It does not own mutable application/domain state.

#### Application

The application responsibility coordinates use cases:

```text
application/
  Conductor
    lifecycle and application-wide coordination

  PresentationGateway
    shared presentation-facing application gateway

  TimingNodeProxy
    node-scoped presentation-facing application boundary

  ConfigurationControl
    configuration query/update use-cases

  UpstreamMessageRouter
    upstream-only application/domain target resolution and routing
```

:::{arch} Conductor  
:id: Conductor  

`Conductor` coordinates application-wide lifecycle and the 1..N active `TimingSystem` aggregates, including their TimingNodes. It owns cross-component application coordination that does not belong to one Domain or I/O component. For example, when TimingNode state determines whether assigned antennas should inventory, Runtime composition wires that relationship through Conductor rather than placing the callback in a Runtime container or device class.
:::

:::{arch} Configuration control  
:id: ConfigurationControl  

`ConfigurationControl` is the Application-layer use-case boundary for reading
running configuration and requesting validated runtime overrides. Presentation
interfaces call this boundary rather than mutating the Runtime configuration tree
or generic configuration values directly.
:::

:::{arch} PresentationGateway  
---
id: PresentationGateway
satisfies: >-
  SI01-REQ-022, SI01-REQ-030, SI01-REQ-031,
  IF03-REQ-001, IF03-REQ-004
---

`PresentationGateway` is the shared entry point for presentation
requests. It is owned by the Application layer; `Presentation` in the name identifies
the adjacent side whose traffic the gateway mediates, not the layer that owns it.
This uses the same directional naming principle as `UpstreamGateway`, while the two
remain separate responsibilities: `PresentationGateway` is transport-independent
application access and `UpstreamGateway` owns external upstream transport/integration.
The gateway exposes application-wide information such as `version()` and capabilities.
Application-wide operations delegate to `Conductor` where lifecycle or cross-node
coordination is required. Node-scoped presentation work is exposed through a
`TimingNodeProxy` so operations such as `open(...)` are explicitly attached to a
TimingNode-facing object rather than appearing as context-free methods on the gateway.
`Conductor` is not a mandatory hop for TimingNode-scoped work.
:::

:::{arch} TimingNodeProxy  
:id: TimingNodeProxy  

`TimingNodeProxy` is the Application-layer boundary object for one addressed
`TimingNode`. The architectural multiplicity is therefore **1..N TimingNodeProxy
instances per application composition: one proxy per composed TimingNode**. The default
executable composition currently instantiates one TimingNode and therefore one proxy;
multi-node composition does not change the boundary shape. Each proxy exposes presentation-facing
node status, commands, bounded LogBook queries and post-fact events while keeping the
Domain `TimingNode` itself behind the Application boundary.

The proxy does not own mutable TimingNode state. It maps presentation intent to the
TimingNode's typed ordered operations and maps node status to the node-scoped,
presentation-facing `TimingNodeStatus`. Normal OPEN is `open(LocationId)`; there is no separate
Set Location presentation operation. Automatic registration uses
`applyAutomaticRegistration(action, registrationId, time)`; the implemented action set
contains `ADD`, while any additional action requires its own defined TimingData semantics.
:::

Once code is executing for a TimingNode, normal direct Java calls are preferred;
do not introduce messages merely to preserve a layer diagram.

:::{arch} UpstreamMessageRouter  
:id: UpstreamMessageRouter  

`UpstreamMessageRouter` owns target resolution for messages exchanged with the
upstream system at application scope. **Upstream** describes that external
system relationship, not the direction of an individual message; the exchange is
bidirectional. The upstream wire contract does not need to expose
`TimingSystemId`. Each configured upstream protocol/gateway context belongs
internally to one `TimingSystem`; node-scoped messages are routed functionally
by `TimingNodeId` to that system's addressed TimingNode. Protocol-level
messages such as ping/heartbeat can be handled by
`TimingSystem`/`UpstreamProtocol` without involving a TimingNode.

The router is deliberately **not** a generic application message bus or mediator
for normal collaboration between domain components.
:::

#### Domain

The domain owns timing semantics, per-TimingSystem system semantics and
TimingNode state. The main responsibilities are deliberately not represented as
one parent/child tree:

```text
TimingSystem (1..N per Application)
  TimingSystemId              internal only
  SystemStatus                complete current system overview
  UpstreamMessagePort         system-level upstream messages
  UpstreamProtocol
    TimingData transfer
    synchronisation / reconciliation
    ping / pong and other protocol messages
  1..N TimingNode
    TimingNodeId              functional protocol/data identity
    LocationId
    State
    UpstreamMessagePort       TimingNode-level upstream messages
    TagProcessor
    StageStartTimes
    LogBook
      0..N TimingData
    NextUpTeams
    EventData
    StageTiming
    uses / produces TimingData

TimingData
  common semantic contracts
  configured concrete profile
  factory / codec / compatibility
```

`TimingSystem` is the parent logical domain aggregate. One Timing Point Application hosts 1..N TimingSystems; each TimingSystem owns an internal `TimingSystemId`, a complete `SystemStatus` overview, a system-level `UpstreamMessagePort`, one `UpstreamProtocol` context and 1..N TimingNodes. `TimingSystemId` exists to separate local runtime/simulation instances and is not assumed to be visible to the upstream peer. This lets one process simulate or host multiple independent timing systems without changing the functional TimingNode-oriented external contract.

`TimingNode` is the per-location domain aggregate inside one `TimingSystem`. It owns its
identity (`TimingNodeId` and `LocationId`), lifecycle/state and the per-node
components shown inside the TimingNode aggregate in Figure SI01-01.

A TimingNode is also the **active serialization and ownership boundary** for mutable per-node
state. State-dependent commands and consistency-sensitive reads enter one bounded serial
execution path and are processed in order. Code outside that boundary does not directly
read or mutate the node's lifecycle/location state or the mutable contents of its contained
`LogBook`, `NextUpTeams`, `StageStartTimes` and `RaceData` objects. Those objects remain
passive and do not receive their own workers. A short operation on the node lane may publish
an immutable snapshot/read view for longer work outside the lane. The LogBook keeps 0..N
committed immutable `TimingData` values and does not own a second worker or second timing-record
representation.

Both aggregate levels expose a bidirectional semantic `UpstreamMessagePort`.
The two roles share the same semantic concept but have distinct engineering
identities in Figure SI01-01 so interactive selection remains unambiguous.

:::{arch} TimingSystem UpstreamMessagePort  
:id: SystemUpstreamMessagePort  

The TimingSystem-level `UpstreamMessagePort` receives and emits system-level
operations such as status/heartbeat and synchronisation control that do not
target one TimingNode. It does not own transport connections, connector
lifecycle or cross-aggregate target resolution.
:::

:::{arch} TimingNode UpstreamMessagePort  
:id: TimingNodeUpstreamMessagePort  

The TimingNode-level `UpstreamMessagePort` receives and emits node-scoped
operations after `UpstreamMessageRouter` has resolved the owning TimingSystem
and target `TimingNodeId`. It does not own transport connections or
cross-aggregate target resolution.
:::

:::{arch} TagProcessor  
:id: TagProcessor  

`TagProcessor` owns TimingNode-local processing of decoded tag observations and
the registration semantics needed by the TimingNode. It resolves the semantic
TagId through EventData before registration-level duplicate suppression and
passage aggregation. Passage state is keyed by RegistrationId while preserving
per-TagId attribution for diagnostics/engineering inspection. It does not write
files from the antenna callback. State-changing registration work crosses the
TimingNode's bounded serial execution boundary and is completed by that node's
worker.
:::

:::{arch} StageStartTimes  
:id: StageStartTimes  

`StageStartTimes` owns the stage-start reference values used by one TimingNode.
:::

:::{arch} NextUpTeams  
:id: NextUpTeams  

`NextUpTeams` owns the ordered/expected teams that are next for one TimingNode.
:::

:::{arch} RaceData
:id: RaceData

`RaceData` is passive TimingNode-local runtime race data. It may be updated
from upstream during an event and may contain live/temporary information such
as reserve-tag mappings. It remains ordered with other TimingNode state through
the owning TimingNode execution boundary.
:::

:::{arch} EventData
:id: EventData

`EventData` is a shared Domain capability parallel to `TimingData`. A
configured EventData profile defines stable event-specific source/reference
semantics, including the 1..N relationship between `RegistrationId` and
`TagId`. SI-01 and engineering tools consume the common contract while an
event-specific typed provider/profile library supplies the concrete profile.
That provider may be discovered and loaded at Runtime through the same typed
extension architecture used for TimingData providers, without coupling the
EventData and TimingData provider families to each other. `RaceData` remains
separate TimingNode-local runtime/upstream race state.
:::

:::{arch} StageTiming  
:id: StageTiming  

`StageTiming` derives running-time and ranking results from the TimingNode's
accepted timing state and reference data.
:::

`LogBook` is passive state contained by one TimingNode and keeps that node's
committed timing history as 0..N immutable `TimingData` values. Concrete objects
may come from different compatible TimingData profiles; LogBook does not maintain
a second logbook-specific record representation.

`EventData` is a separate SI-01/domain capability alongside `TimingData`.
EventData owns event-specific source/reference relationships; TimingData owns
committed timing facts. One RegistrationId may map from multiple TagIds. The
antenna/provider layer performs physical decoding/decryption but exposes a
semantic TagId to generic processing.

`TimingData` is the SI-01/domain capability that realises the system-owned
IF-05 TimingData Interchange contract. IF-05 defines the common semantic
contracts, identity/ordering rules and compatibility obligations. A configured
TimingData profile supplies the concrete immutable TimingData classes plus the
matching factory and codec.

A `TimingDataProvider` supplies that coherent profile family. Its factory is
stateless and constructs concrete TimingData values from explicit construction
values; it does not own TimingNode state policy, sequence allocation,
persistence or event publication. The same common provider/API boundary is
reusable by SI-01 and engineering tools such as the JavaFX Development Client;
normal domain users remain unaware of provider discovery mechanics.

`UpstreamProtocol` is a Domain responsibility owned in the context of one `TimingSystem`. It uses `TimingData` for timing-record transfer and additionally defines semantic messages needed for synchronisation, reconciliation, heartbeat/ping and other upstream-system exchanges. It is therefore broader than the TimingData record format itself. Protocol-level activity that is not about one TimingNode stays here rather than leaking into each TimingNode. A concrete protocol implementation may be selected through an `UpstreamProtocolProvider`; the semantic boundary remains the same whether the implementation is built in or extension-provided.

`PlatformEnvironment` supplies the process/runtime time capabilities used by
SI-01: an absolute wall-clock `Clock` for externally meaningful timestamps and
a `MonotonicClock` for elapsed-time semantics. Domain objects consume the
semantic time values they need; they do not own a second per-TimingSystem clock
abstraction.

Detailed domain semantics belong in `03-domain-baseline.md`.

#### Runtime execution model

Execution mechanics support the layered architecture but are not a separate
logical layer in Figure SI01-01. Runtime owns the physical execution resources;
the functional components own their logical ordering/serialization boundaries.

The architecture distinguishes a **logical serial lane** from a **physical
worker**:

```text
logical lane
  = component-local ordering, admission and queue state

physical worker
  = Runtime-owned thread/executor resource that executes work from one or more lanes
```

Execution identity follows the same ownership split. The logical lane is identified
with the component whose work it orders; physical worker/thread identity belongs to
the Runtime resource that executes lane work. Sharing one physical worker therefore
does not merge the logical execution identities of the components using it.

A Timing Point Application may contain multiple TimingNodes without allocating
one physical worker per node. Each TimingNode keeps an independent bounded
serial lane so its mutable state remains ordered and isolated, while all
TimingNode lanes use one shared physical TimingNode worker by default.

Each TimingNode-local TagProcessor likewise owns its own logical scheduled
serial lane, while all TagProcessor lanes share one physical TagProcessor
worker by default.

Application-wide coordination has a separate execution boundary. Conductor
owns a serial application-coordination lane so cross-component behaviour does
not execute synchronously on the thread that emitted a Domain or I/O event.

AntennaManager owns one serial scheduled I/O lane. Probe, initialize,
power-control transitions, start/stop inventory and multiplex switching/rotation
all enter that same logical lane; the lane runs on one Runtime-owned I/O-role
worker. There is no separate initialization worker and no separate switching
worker in the baseline. Elapsed-time waits such as power stabilization are
scheduled continuations on that same lane, so the physical I/O worker is released
while time passes.

The baseline execution topology is therefore:

```text
Domain
  TimingNode 1 ─ serial lane ─┐
  TimingNode 2 ─ serial lane ─┼─> one shared TimingNode worker
  TimingNode N ─ serial lane ─┘

  TagProcessor 1 ─ scheduled serial lane ─┐
  TagProcessor 2 ─ scheduled serial lane ─┼─> one shared TagProcessor worker
  TagProcessor N ─ scheduled serial lane ─┘

Application
  Conductor ─ serial lane ────────────────> one application worker

I/O
  AntennaManager ─ scheduled serial lane ─> one shared I/O worker
```

The default is **one physical worker per functional role**, not one worker per
component instance and not one worker per CPU core.

This minimal topology applies to both known deployment classes:

- the simple one-antenna Timing Point Application on Raspberry Pi Zero;
- the larger Raspberry Pi 3 Model B deployment, including the known
  two-antenna configuration that multiplexes inventory at 500 ms.

The Raspberry Pi 3 having more CPU cores does not by itself justify more
physical workers. Likewise, configuring multiple TimingNodes or multiple
antennas does not automatically increase worker count. In the known two-antenna
baseline, AntennaManager deliberately inventories only one multiplex-group
member at a time, so an additional I/O worker is not assumed to provide useful
antenna parallelism.

Additional physical parallelism is a measurement-driven refinement. V01 runtime
characterization must demonstrate a concrete contention, latency or throughput
problem before a role receives more physical workers. Any such change must
preserve the component-local serial-lane semantics above.

Platform provides reusable execution mechanics for components that need more
than direct lane admission. In particular, bounded result waiting, timeout/cancellation
propagation and delayed continuation are treated as shared execution concerns rather than
being reimplemented independently by each I/O/Application component.

That higher-level task-handling mechanism is optional. A component that only needs direct
serial admission/ordering continues to use its execution lane directly. The presence of a
shared task-handling capability does not require TimingNode, TagProcessor or Conductor to
be wrapped in another abstraction when their semantics do not need timeout/result/delayed
handling.

Runtime worker items are deliberately bounded. A worker item must not occupy a
physical worker merely to wait for time to pass. Delays such as antenna power
stabilization are represented as scheduled continuation work on the owning
logical lane:

```text
power on
  -> return worker
  -> scheduled continuation after stabilization delay
  -> probe / initialize
```

External I/O may require bounded waiting for one device/protocol operation, but a
shared worker must not be monopolized by an unbounded wait, polling loop or sleep.
A provider that needs long-lived blocking behaviour must expose that behaviour
through an execution design that does not stall unrelated work on the shared
role worker.

TimingNode is a different kind of execution boundary: one admitted Domain item is
normally processed to its semantic completion before the next item on that
TimingNode lane. That may include short in-process state work, LogBook/persistence
commit and publication of the resulting immutable event. TimingNode work must not,
however, sleep for elapsed time or wait on external hardware/network activity.

The one-worker I/O baseline is therefore not justified by an assumption that
device calls are free or instantaneous. It is justified by the intended quality
of worker items: short/bounded provider operations plus scheduled continuations
for elapsed-time waits. Additional I/O workers remain a V01 evidence-based
decision if independent I/O lanes later contend on genuinely blocking operations.

Thread priorities are not part of correctness. The baseline uses normal/default
JVM priority for all Runtime-owned workers; priority tuning requires measurement
evidence and target-platform requalification.

The concrete Java realization of these rules belongs in SDD-02. That design may
use types such as `SerialExecutor`, `SerialScheduledExecutor`,
`ThreadPoolExecutor` and `ScheduledThreadPoolExecutor`, but those Java types
are implementation mechanisms rather than the architecture identity of the
execution model.

#### I/O

I/O contains adapters that move data between the application and the outside world. Figure SI01-01 shows one logical I/O layer, but the runtime composition is per `TimingSystem`: with 1..N TimingSystems, the corresponding Storage/Devices/Messaging/DeviceNetworks composition is instantiated 1..N times unless a lower-level implementation explicitly multiplexes a shared physical resource.

```text
io/
  Devices
    AntennaManager
      Antenna (0..N)
        SimulatedAntenna
    AntennaPowerControl (0..N)
    Display
      Rev1CanDisplay
      Rev2WifiDisplay
    Keypad
      Rev1CanKeypad
    Beeper

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
DeviceNetworks elements carry packaging-component notation where the
package-like ownership/decomposition semantics are meaningful. For compactness,
Figure SI01-01 shows their contained software components as an indented hierarchy
rather than as nested component boxes.

:::{arch} Storage  
:id: Storage  

`Storage` owns generic lower-layer persistence mechanisms plus backup/restore mechanics. Storage contracts are independent of higher Application/Domain types. TimingData-specific encoding, identity/sequence validation and commit semantics remain above Storage; Runtime composition connects that semantic persistence component to the selected generic file/database mechanism.
:::

:::{arch} Devices  
:id: Devices  

`Devices` groups the software components that represent external device roles in
SI-01. A TimingSystem may be configured without RFID antennas. When one or more
antennas are configured, one `AntennaManager` coordinates that 1..N `Antenna`
set for the TimingSystem. Optional `AntennaPowerControl` capabilities represent
installation-owned external power channels used by AntennaManager; they are peers of
the antenna/provider role rather than hidden vendor-driver behaviour.
`SimulatedAntenna` is the built-in reference/simulation implementation.
`Display`, `Keypad` and `Beeper` name software-facing device roles; their
concrete variants remain subordinate to this package/component boundary.
:::

:::{arch} DeviceNetworks  
:id: DeviceNetworks  

`DeviceNetworks` owns communication/network responsibilities used to reach
devices. `CanNetworkController` owns CAN-bus lifecycle, discovery/scanning,
online state and CAN-device communication. `NetworkDeviceService` owns the
bidirectional network-device boundary for smart/network-attached devices.

Service discovery, connection/session handling and protocol framing are
subordinate design concerns of `NetworkDeviceService`, not peer high-level
components. The boundary is not Wi-Fi specific and does not own smart-display
rendering/domain behaviour.
:::

:::{arch} Messaging  
:id: Messaging  

`Messaging` owns the external upstream transport/session package. When upstream
messaging is configured it contains one `UpstreamGateway`; the gateway uses
1..N connectors and concrete connectors own transport resources,
delivery/session mechanics and transport-specific addressing.

The semantic `UpstreamProtocol` remains in Domain. Messaging may transport an
encoded protocol representation without interpreting `TimingData` fields or
reimplementing synchronisation rules; after protocol decoding,
`UpstreamMessageRouter` owns application-level target resolution.
:::

### Nested I/O component identities

The compact I/O cards in Figure SI01-01 keep their subordinate software
components as structured rows rather than expanding each component into a
separate box. The following rows are nevertheless stable architecture objects
and use the same engineering identity model as top-level diagram nodes.

:::{arch} AntennaManager  
:id: AntennaManager  

`AntennaManager` coordinates 1..N configured Antenna components for one
TimingSystem. If that TimingSystem has no configured antenna, no AntennaManager
is required.
:::

:::{arch} Antenna  
:id: Antenna  

`Antenna` is the software-facing RFID antenna/reader role consumed by
AntennaManager. Concrete vendor or simulated implementations remain behind this
role.
:::

:::{arch} AntennaPowerControl  
:id: AntennaPowerControl  

`AntennaPowerControl` is the optional software-facing I/O capability for an
installation-owned external antenna power channel. AntennaManager uses it to order
power-on, stabilization and power-off around probe and normal operation. It remains
separate from `Antenna` because the physical power switch may be a relay, GPIO or
other installation device unrelated to the antenna vendor protocol.
:::

:::{arch} SimulatedAntennaPowerControl  
:id: SimulatedAntennaPowerControl  

`SimulatedAntennaPowerControl` is the deterministic built-in implementation used
with `SimulatedAntenna` to verify powered/unpowered state, stabilization sequencing
and power-cycle behaviour without physical relay or reader hardware.
:::

:::{arch} SimulatedAntenna  
:id: SimulatedAntenna  

`SimulatedAntenna` is the built-in controllable Antenna implementation used for
development, simulation and hardware-independent verification.
:::

:::{arch} VendorAntenna  
:id: VendorAntenna  

`VendorAntenna` is the generic architecture role for an extension-provided
production Antenna implementation beside the built-in simulator. It establishes
that production/vendor implementations use the same Antenna contract and
AntennaProvider extension path; an actual vendor integration may receive a more
specific implementation name when selected.
:::

:::{arch} Display  
:id: Display  

`Display` is the software-facing output-device role for presenting timing
information without coupling Domain/Application behaviour to one physical
display generation or transport.
:::

:::{arch} Rev1CanDisplay  
:id: Rev1CanDisplay  

`Rev1CanDisplay` is the CAN-connected revision-1 implementation of the Display
role.
:::

:::{arch} Rev2WifiDisplay  
:id: Rev2WifiDisplay  

`Rev2WifiDisplay` is the network-attached revision-2 implementation of the
Display role.
:::

:::{arch} Keypad  
:id: Keypad  

`Keypad` is the software-facing operator-input device role used for keypad
events without making the timing domain depend on a concrete bus implementation.
:::

:::{arch} Rev1CanKeypad  
:id: Rev1CanKeypad  

`Rev1CanKeypad` is the CAN-connected revision-1 implementation of the Keypad
role.
:::

:::{arch} Beeper  
:id: Beeper  

`Beeper` is the transport-neutral audible-feedback device role. A concrete
connection/implementation is selected only when required by deployment design.
:::

:::{arch} CanNetworkController  
:id: CanNetworkController  

`CanNetworkController` owns CAN-bus lifecycle, discovery/scanning, online state
and CAN-device communication for the DeviceNetworks package.
:::

:::{arch} NetworkDeviceService  
:id: NetworkDeviceService  

`NetworkDeviceService` owns the bidirectional boundary for
network-attached/smart devices, including data sent outward and device-originated
messages/events received inward.
:::

:::{arch} UpstreamGateway  
:id: UpstreamGateway  

`UpstreamGateway` is the Messaging-owned external upstream transport/session
boundary. It owns connector coordination but not UpstreamProtocol semantics.
:::

:::{arch} Connector  
:id: Connector  

`Connector` is the transport/session role used 1..N times by UpstreamGateway.
Concrete connectors own transport resources, delivery/session mechanics and
transport-specific addressing.
:::

:::{arch} RabbitMqConnector  
:id: RabbitMqConnector  

`RabbitMqConnector` is the RabbitMQ implementation of the Connector role for
production-shaped upstream messaging.
:::

:::{arch} DebugConnector  
:id: DebugConnector  

`DebugConnector` is the development/debug implementation of the Connector role.
It provides a production-semantics-preserving upstream transport path that an
independent engineering desktop/debug tool can use without becoming part of
SI-01 or bypassing UpstreamGateway/UpstreamProtocol. The concrete debug transport
and desktop-tool interaction are refined by downstream design rather than by
Figure SI01-01.
:::

#### Platform

Platform is the small technical foundation below the application, domain and I/O
responsibilities. It contains JDK-only reusable primitives and low-level
execution-environment abstractions:

```text
bounded serial execution (SerialExecutor / SerialScheduledExecutor)
optional scheduled task handling (ScheduledTaskRunner)
local typed events (Event<T> / EventSource<T>)
absolute wall clock (Clock)
elapsed-time source (MonotonicClock)
```

A domain or I/O component may compose a Platform primitive such as
`SerialExecutor`, `SerialScheduledExecutor`, `ScheduledTaskRunner` or `Event<T>`; the primitive itself remains unaware of
TimingNode, TimingData, presentation or external I/O semantics.

The layered view groups Platform into three small technical responsibilities:

:::{arch} PlatformExecution  
:id: PlatformExecution  

`PlatformExecution` owns the reusable bounded serial execution primitives
`SerialExecutor` and `SerialScheduledExecutor`. It also provides the optional
`ScheduledTaskRunner` helper for bounded result waiting, cancellation
propagation and delayed continuations on an existing scheduled serial lane.
These mechanisms own no TimingNode state or domain policy.
:::

:::{arch} PlatformEvents  
:id: PlatformEvents  

`PlatformEvents` supplies the small typed `Event<T>` / `EventSource<T>` local-event mechanism used for
post-fact notifications. Event instances remain owned by the component that
publishes them; Platform does not provide a central event bus.
:::

:::{arch} PlatformEnvironment  
:id: PlatformEnvironment  

`PlatformEnvironment` is the small process/platform boundary composed by
Runtime. It provides the absolute wall-clock `Clock` used when externally
meaningful timestamps are attached, the `MonotonicClock` used for elapsed time,
timeouts, filtering windows and metrics, and a normalized `OperatingSystem`
identity used for explicit Runtime composition defaults. It is deliberately not
a general service locator for filesystem, networking or arbitrary OS facilities.
:::

#### Runtime and infrastructure

The right-hand side of the layered view separates two technical responsibilities:

- **Runtime** — `TimingApplicationRuntime` as the top-level composition/lifecycle owner, its child `PresentationRuntime`, Runtime-owned physical execution resources and the concrete running configuration tree;
- **Infrastructure / cross-cutting** — supporting technical facilities such as logging, diagnostics, build identity, typed configuration mechanics, configuration mapping and extension discovery.

:::{arch} Application configuration  
:id: ApplicationConfiguration  

`ApplicationConfiguration` is the concrete Runtime configuration tree for the
currently composed SI-01 process. It contains typed branches such as per-TimingNode
configuration and references Infrastructure configuration values, but it does not
own external YAML parsing or presentation-facing control use-cases.
:::

:::{arch} Typed configuration values  
:id: Configuration  

`Configuration<T>` represents the reusable Infrastructure responsibility for
typed startup/current values, validated runtime override state and post-change
notification. These mechanics contain no knowledge of TimingNode, TagProcessor,
IF-11 paths or IF-03 routes.
:::

#### Cross-cutting concerns

Cross-cutting technical concerns include logging, diagnostics, metrics and
build/version identity. In Java, `infra` is reserved for concrete cross-cutting
support such as `BuildIdentity`; it is not the I/O layer.

:::{arch} Logging  
:id: Logging  

`Logging` is reusable runtime logging infrastructure owned by the core artifact. Reusable
application-core/domain code emits records through SLF4J; the default executable selects
`slf4j-jdk14 -> java.util.logging` and starts the core-provided logging composition.
Logging owns backend/sink lifecycle and the current global logging level; it does not own
application or domain state.
:::

:::{arch} LoggingServer  
:id: LoggingServer  

`LoggingServer` is the optional external engineering interface for live log records and
temporary global-level control. The engineering client initiates the connection. This
logging-specific TCP boundary is separate from the IF-03 API/status/event
interface and live delivery remains best effort.
:::

`TimingApplicationRuntime` owns concrete knowledge of the running application graph. Infrastructure remains supporting/cross-cutting: the default YAML loader maps deployment input to effective runtime configuration, logging and diagnostics provide technical services, and extension discovery supplies selected implementations. The executable supplies the configuration path rather than owning the parser. `LoggingServer` depends on the narrow `Logging` surface for level control/common formatting; `Logging` does not depend on or own `LoggingServer`.

### Principal runtime abstractions

:::{arch} TimingSystem  
:id: TimingSystem  

A `TimingSystem` is an internal parent domain aggregate.
One **Timing Point Application** (SI-01) may host 1..N
TimingSystems, for example to run multiple independent
simulation contexts. Each TimingSystem owns a complete
`SystemStatus` overview, a system-level
`UpstreamMessagePort`, one `UpstreamProtocol` context and 1..N TimingNodes. Its internal `TimingSystemId` is not
assumed to be part of the upstream wire contract.
:::

:::{arch} SystemStatus  
:id: SystemStatus  

`SystemStatus` is a dedicated Domain component contained by one
`TimingSystem`. It owns the complete current operational overview of that
system, including TimingNode state plus semantic device, device-network,
storage, upstream-connectivity and synchronisation status. Concrete adapter
objects remain outside Domain and contribute status through typed semantic
inputs.
:::

:::{arch} TimingNode  
:id: TimingNode  
:satisfies: SI01-REQ-003, SI01-REQ-020, SI01-REQ-021  

A `TimingNode` is the independently addressed
operational/domain aggregate at one timing location. It
belongs to exactly one `TimingSystem` and is the active
serialization boundary for that node's mutable state.
Its contained state objects are passive; the upstream and
TimingData contracts remain centred on `TimingNodeId`.
:::


:::{arch} LogBook  
:id: LogBook  

A `LogBook` is passive state contained by one TimingNode.
It holds that node's committed immutable `TimingData` values.
The current design does not introduce a second
logbook-specific timing-record representation.
:::

:::{arch} TimingData  
:id: TimingData  

`TimingData` is the shared Domain capability that realises
system-owned IF-05 inside SI-01. It exposes the typed
common `TimingData` semantic interfaces plus configured factory/codec services needed
by application code. Canonical record/file semantics and
compatibility remain defined by IF-05; Storage, Web and upstream
protocol code consume that contract without redefining it.
:::

:::{arch} UpstreamProtocol  
:id: UpstreamProtocol  

Each TimingSystem owns one `UpstreamProtocol` context. It uses
TimingData for timing-record transfer and owns protocol-level
synchronisation, reconciliation and ping/heartbeat semantics so
those concerns do not leak into individual TimingNodes.
:::



The architecture deliberately uses **separate views** for software/domain decomposition, hardware/deployment topology and configuration/identity mapping. These views must not be collapsed into one ownership tree.

#### Software/domain decomposition

```text
Application
  +-- ApplicationId
  |
  +-- 1..N TimingSystem
        +-- TimingSystemId        internal composition/simulation identity
        +-- SystemStatus          complete current system overview
        +-- UpstreamMessagePort   system-level upstream messages
        +-- UpstreamProtocol
        |     +-- heartbeat / ping
        |     +-- synchronisation / reconciliation
        +-- 1..N TimingNode
              +-- TimingNodeId   functional upstream/timing-data identity
              +-- LocationId
              +-- lifecycle / status
              +-- UpstreamMessagePort
              +-- TagProcessor
              +-- StageStartTimes
              +-- LogBook
              |     +-- 0..N TimingData
              +-- NextUpTeams
              +-- RaceData
              +-- StageTiming
              +-- uses / produces TimingData

Shared Domain contract:
  +-- TimingData
```

`ApplicationId` identifies the running Timing Point Application instance. `TimingSystemId` is an internal identity used only to distinguish 1..N hosted TimingSystem contexts. `TimingNodeId` remains the functional identity used by TimingData and upstream node addressing and scopes the node's registration sequence and synchronisation semantics. `LocationId` is the separately configured physical event location. The upstream contract therefore does not gain a TimingSystem identifier merely because one process can host multiple systems.

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
  +-- Rev1CanDisplay
  +-- Keypad
  +-- Beeper
  +-- Rev2WifiDisplay

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
service discoverable and Rev2WifiDisplay connects to it. The exact discovery,
listener/session and packet-framing design belongs below this high-level view.

#### Configuration, routing and identity mapping

Configuration connects identities without collapsing them:

```text
Application
    +-- ApplicationId

Devices
    +-- Antenna (0..N)
    |     +-- each Antenna -> 1..N TimingNodeId
    +-- Rev1CanDisplay
    +-- Keypad
    +-- Beeper
    +-- Rev2WifiDisplay

Device Networks
    +-- CanNetworkController
    +-- NetworkDeviceService

Messaging
    +-- UpstreamGateway
          +-- Connector (1..N)
                +-- RabbitMqConnector
                +-- DebugConnector

UpstreamMessageRouter
    +-- system-level message -> TimingSystem.UpstreamMessagePort
    +-- TimingNodeId -> TimingNode.UpstreamMessagePort
    +-- TimingSystemId remains internal composition context
```

<a id="fig-si01-03"></a>
![TimingNode, hardware and upstream-system messaging routing](../../../raw/prod/docs/assets/architecture/timing-node-routing-mapping.svg)
*Figure SI01-03 — TimingNode, hardware and upstream-system messaging routing.*

`TimingNodeId` is the stable identity of a `TimingNode` and scopes its sequence, persistence and synchronisation semantics. `LocationId` and `AntennaId` are separate namespaces.

Configured antenna mappings associate each `AntennaId` with one or more TimingNodes. Fan-out is explicit: if one antenna feeds two TimingNodes, each target TimingNode processes the observation through its own serialized state boundary and keeps its own TimingNodeId-scoped sequence/state while the original `AntennaId` remains available as context.

CAN and smart-network controllers are not alternate presentation layers. They are
I/O/device-network responsibilities. A keypad, beeper or display may interact with or present information
to a human, but it is still an external device from SI-01's architecture
perspective.

`UpstreamGateway` is the I/O upstream-messaging boundary. It exchanges transport-neutral messages with its configured connectors but does not own protocol semantics. Each configured gateway/protocol context is associated internally with one `TimingSystem`. `UpstreamMessageRouter` routes system-level semantic operations to `TimingSystem.UpstreamMessagePort` and resolves TimingNode-targeted operations by `TimingNodeId` to `TimingNode.UpstreamMessagePort`; `UpstreamProtocol` owns protocol semantics such as ping, status exchange and synchronisation. No external `TimingSystemId` field is required.

Connectors do not route directly to Domain or TimingNodes and do not own domain
semantics. A connector-specific external name or routing key may participate in
boundary mapping, but it does not replace the stable functional `TimingNodeId`.
Internal `TimingSystemId` is local composition context rather than a new
upstream routing identity. One gateway may use multiple connectors and one
TimingNode may exchange messages through more than one connector via the gateway,
router and its bidirectional port. `RabbitMqConnector` represents the
production-shaped transport; `DebugConnector` provides an engineering/debug
transport to an external desktop/debug tool while preserving the same gateway
and protocol boundary.

`ApplicationId` remains a runtime/application identity and is not assumed to be an upstream protocol address. Protocol-level exchanges are scoped by the configured TimingSystem/gateway context; TimingNode-specific exchanges remain addressed by `TimingNodeId`.

Runtime-wide infrastructure may be shared where that does not leak mutable TimingNode state. The Java baseline shares physical execution workers by functional role while each TimingNode keeps its own bounded serial command lane and node-local TagProcessor state. Logging infrastructure, HTTP server infrastructure, connector infrastructure, configuration loading and network monitoring may likewise be shared where their semantics remain isolated.

Stable domain facts behind these views are maintained in `03-domain-baseline.md`; this SSD owns their software-architecture composition and execution implications.

### Command, query and event model

All presentation transports converge on one shared application model. The Java design uses a deliberately small `PresentationGateway.version()` query rather than a generic messaging framework; request methods are added only when a concrete client use case requires them.

```text
local console ----------------+
remote shell -----------------+
API HTTP/JSON ---------+--> typed command/query boundary --> application runtime
API WebSocket <---------+<--------------------------------------------+
optional Web interface --------+
```

Working rules:

- commands request state changes;
- a state-dependent command may wait for the domain result produced when that command reaches the TimingNode's ordered execution path;
- submission-only ingress is explicit: acceptance means only that bounded work was accepted for later processing;
- queries do not become alternate owners of state; consistency-sensitive reads run on the TimingNode's ordered path or use an immutable snapshot published from that path;
- events report facts/results that have occurred;
- queue admission, domain result and caller wait timeout are different outcomes and shall not be represented as though they mean the same thing;
- a caller timeout does not prove rejection or rollback of already accepted work; until state is queried or another result is observed, the final outcome is unknown to that caller;
- external protocol DTOs are mapped at the presentation/I/O boundary rather than used as the internal domain model;
- messages crossing thread/process boundaries should be immutable where practical;
- post-fact notifications may use a small typed `Event<T>` abstraction with explicit `subscribe` / `unsubscribe` / `emit`; commands and queries are not routed through that mechanism.

The event mechanism is deliberately local and simple. The generic `Event<T>`
mechanism is a small reusable Platform primitive; a producing component owns a concrete
event such as `timingDataCommittedEvent : Event<TimingData>` and interested listeners
subscribe directly to that event. There are no string topics, central event
dispatcher or global static bus. Emitting an event reports that a fact has
already occurred; it does not transfer ownership of TimingNode state.

### Process view: ordering and concurrency

SI-01 receives work from several places at once: operator interfaces, devices,
timers and upstream connections. State changes for one `TimingNode` still have
to happen in a clear order.

Architecture rules:

- callbacks do not change TimingNode state directly;
- resolve the target TimingNode before state-dependent work enters its ordered path;
- code outside a TimingNode does not directly inspect or mutate that node's mutable state;
- two state changes for the same TimingNode do not run over each other;
- the TimingNode behaves as an active object: one bounded serial execution
  boundary owns state-dependent command ordering and consistency-sensitive reads;
- state-dependent validation is performed when the operation executes against the current ordered state, not from a stale pre-queue read;
- the contained LogBook, NextUpTeams, StageStartTimes and EventData objects remain
  passive and do not each receive their own execution thread;
- short read operations may capture immutable snapshots for longer calculations outside the TimingNode lane;
- different TimingNodes may make progress at the same time;
- file writes must not hold up RFID/device/operator callbacks;
- a slow query or ranking calculation must not hold up LogBook commits;
- a slow network connection must not hold up a local commit;
- queues/resources are bounded and overload is visible instead of silently dropping work;
- during shutdown, stop new input first and give accepted work time to finish.

The primary latency risk is therefore **producer backpressure**, not whether every TimingNode operation is asynchronous. Device/RFID/TagProcessor ingress must use the submission-only path and return after bounded-queue admission; it does not wait for persistence or a domain result. Presentation/application callers may use a result-bearing command path when they need that result.

Short consistency-sensitive queries are allowed to occupy the TimingNode lane for a bounded period. The design does not require a copied snapshot as the default read mechanism. Read/query implementations may traverse contained state directly on the ordered lane, use a compact derived/indexed representation, or copy data only when measurement shows that the copy is the better trade-off. Longer ranking/formatting work must still avoid becoming a second writer or unboundedly holding up timing commits. Synchronous persistence may occupy the lane; its impact is controlled through bounded queues and observable queue/store latency.

Post-commit listeners are subject to the same rule: network/backpressure work must not execute synchronously on the TimingNode lane unless the adapter is proven to enqueue/buffer and return promptly.

The SSD only sets these rules. SDD-01 describes state ordering, persistence and
consumer visibility. SDD-02 chooses the Java queue/worker implementation. The
current direction is the Active Object pattern implemented by composition, not a
mandatory `TimingNode extends ActiveObject` class hierarchy.

External ingress still keeps its functional routing responsibilities:

- `PresentationGateway` exposes application-wide presentation metadata/capabilities and node proxies;
- `TimingNodeProxy` exposes node-scoped presentation operations, reads and events;
- configured device/antenna mappings resolve device observations to TimingNodes;
- `UpstreamMessageRouter` resolves system-level versus TimingNode-targeted
  upstream messages;
- scheduled work retains its owning target.

There is no central dispatcher through which commands and queries must pass. Components may expose local typed events such as `timingDataCommittedEvent` for post-fact notification; those events are not the owner or execution path for TimingNode state.

<a id="fig-si01-04"></a>
![SI-01 runtime dispatch process](../../../raw/prod/docs/assets/architecture/runtime-dispatch-process.svg)
*Figure SI01-04 — Concurrent ingress resolves to ordered TimingNode state-change boundaries; concrete execution mechanics belong to detailed design.*

The source for this process view is
`docs/_diagrams/runtime-dispatch-process.yaml`.

### Time and clock architecture

Time is an explicit architecture concern rather than an incidental use of `Date`, `Calendar`, `LocalDateTime`, Java/SQL timestamp classes or raw millisecond values throughout the codebase.

#### `TimingTimestamp` value

The **Timing Point Application** (SI-01) uses one dedicated immutable application/domain class named `TimingTimestamp` for externally meaningful **absolute event times** such as observations, accepted registrations and persisted/synchronised event timestamps. A race/stage start definition is not required to be an absolute timestamp: it may be supplied as local time-of-day without a date, or with an explicit date when that information is available.

Working semantics:

- `TimingTimestamp` represents an absolute point on a UTC-based time line;
- it does not contain an implicit local time zone or daylight-saving state;
- conversion to/from local civil time happens at explicit presentation/configuration/integration boundaries;
- its precision and external serialisation are explicit rather than inherited accidentally from a Java API or wire codec;
- domain/application APIs pass `TimingTimestamp` rather than arbitrary `long`, `Date`, generic Java timestamp classes or local-date/time values where an absolute event time is intended.

The dedicated class may internally delegate to a suitable Java primitive such as `Instant`, but its public semantic contract remains project-owned. Protocol-specific formatting/parsing and deployment-specific zone conversion belong in boundary adapters/codecs rather than in `TimingTimestamp` itself. Time-only race/start definitions are a separate domain/reference-data concept and shall not be forced into `TimingTimestamp` by inventing a date.

When a race/stage start is defined only by local time-of-day, elapsed-time calculation shall resolve that clock time against the accepted registration timestamp using the configured event/race time zone. The resolved start is the most recent valid occurrence of that time-of-day that is not after the registration. This deliberately supports one civil-day rollover: a start at `23:59:50` followed by a registration at `00:00:10` resolves to an elapsed time of 20 seconds rather than a negative value. If an explicit start date is supplied, that date is authoritative. A time-only definition cannot by itself distinguish elapsed durations of 24 hours or more; such cases require an explicit date or another higher-level race-day reference.

#### Time sources

SI-01 uses the Runtime-composed `PlatformEnvironment` as the process/platform
time boundary.

```text
Clock
  absolute externally meaningful time
  observation/event timestamps
  persistence / synchronisation semantics

MonotonicClock
  elapsed time only
  filtering windows
  scheduling delays
  timeouts / metrics
```

The absolute wall clock may be controlled by simulation composition when a
deterministic scenario requires it. Monotonic values are process-local and are
never persisted as event timestamps. Device/provider code attaches a
`TimingTimestamp` at the earliest accepted decoded-observation point using the
configured absolute clock when the provider does not supply a trustworthy
source timestamp.


#### Architecture risk — wall-clock discontinuity and local-time ambiguity

This is an explicit architecture risk because timing software can produce plausible but incorrect results when local civil time and elapsed time are conflated.

| Risk | Possible consequence | Architectural mitigation / open work |
| --- | --- | --- |
| daylight-saving transition repeats or skips local civil times | ambiguous/non-existent local timestamps and wrong ordering if local time is persisted directly | persist/use absolute `TimingTimestamp` for events; resolve time-only race/start definitions through an explicit event-zone rule and require more context where a local time is ambiguous/non-existent; add DST transition tests |
| NTP, manual correction or platform synchronisation steps wall clock backwards/forwards | negative/large elapsed differences; a later observation can have an earlier wall-clock timestamp | use monotonic time for durations; source sequence for ordering; expose/inject wall clock; define correction/health policy |
| clock offset/drift differs between the application and external systems | incorrect elapsed/race-time calculations or reconciliation disagreement | define clock synchronisation/offset acceptance requirements and verification before timing accuracy is accepted |
| restart loses monotonic origin | process-local duration marks cannot be compared across restart | never persist monotonic marks as event timestamps; restore from absolute `TimingTimestamp` plus domain/source state |

Daylight-saving time by itself does **not** change UTC/absolute time; the ambiguity appears when a local civil time is treated as if it were an absolute timestamp. Conversely, using an absolute `TimingTimestamp` does not make the operating-system clock monotonic: a wall-clock correction can still cause newly captured absolute timestamps to move backwards.

Before physical timing behaviour is accepted, the project must decide how an active timing system reacts to a material clock correction: whether it is merely diagnosed, blocks/marks the system degraded, records an audit event, or uses an explicit correction/offset mechanism. That policy needs requirements and verification evidence rather than being hidden inside the `TimingTimestamp` class.

### Internal messaging direction

Internal messaging exists at asynchronous/ownership boundaries; it is **not** a requirement to turn ordinary in-lane Java calls into messages.

Working semantic categories are:

```text
state-dependent command
  request a state change
  caller may wait for the processed domain result

submission-only input
  request bounded admission for later processing
  admission is not the later domain result

consistency-sensitive query
  capture/read current TimingNode state on the ordered path

event
  report an observation, fact, completion or failure that has occurred
```

These are interaction semantics, not a requirement for public `Command` or `Query`
classes. The caller-facing TimingNode API may remain ordinary synchronous methods.
A Future/Promise is a suitable internal Active Object mechanism for connecting a
queued operation to a caller that waits for its result; that mechanism need not
appear in the public application/domain API.

Rules:

- use typed internal work only where work crosses an asynchronous or TimingNode execution boundary;
- resolve command/query targets explicitly; do not route commands or mutable-state access through events; local typed events are only for post-fact notification;
- once running in a TimingNode's serial execution lane, use normal direct Java calls;
- do not call a blocking public TimingNode operation recursively from that same lane;
- submit asynchronous I/O completion back to the owning TimingNode before changing its state;
- RabbitMQ is external I/O, not an in-process message bus.

SDD-01 illustrates the interaction cases. SDD-02 owns the concrete Java Future,
queue, timeout and worker mechanics.

### Status and diagnostics architecture

Status is a first-class current-state model and is distinct from logging.

Status should allow presentation and diagnostics to observe application, timing-system and subsystem health without parsing log text. Representative areas include:

- application version / uptime / overall health;
- TimingNode state;
- registration asset/source state;
- TimingNode queue depth/high-water/overload health;
- RFID power/startup/protocol/heartbeat;
- CAN/device availability;
- persistence/backup state;
- race-data freshness;
- local clock/time-source health where relevant to timing validity;
- network/upstream connectivity;
- inbound/outbound synchronisation state.

Each `TimingSystem` contains its own dedicated Domain `SystemStatus` component. This is a complete current-state
overview of that TimingSystem, not an `OK`/error flag. It aggregates the
TimingSystem lifecycle and protocol state, its 1..N TimingNode statuses and the
semantic status of composed I/O relevant to operation: for example antenna
availability, whether a display is connected, keypad/beeper availability,
device-network health, storage availability, upstream connectivity and
synchronisation state. Domain owns the meaning of this overview; concrete CAN,
socket, vendor-device and persistence implementations remain in I/O and report
semantic status without leaking adapter classes into Domain.

`SystemStatus` does not bypass TimingNode ownership to inspect node internals.
A TimingNode supplies a semantic immutable status/result from its own ordered
state boundary; SystemStatus may retain/aggregate that representation together
with system/I/O health. An application-wide status response may therefore use
published node-status snapshots, or obtain a consistency-sensitive node status
through the normal TimingNode query operation when that stronger ordering is
required.

An application-facing status view may aggregate the 1..N TimingSystem statuses
and application/runtime problems into one response; that aggregation does not
move SystemStatus ownership back to the Application.

Status returned to a client is read-only from that client's point of view. The transport response does not define the internal Java class structure used to produce it.

Logging records diagnostic/history information; status represents current operational state. One must not be used as a substitute for the other.

### Logging architecture

Logging is a SSD architecture-level cross-cutting technology decision because it affects almost every
component, operational diagnostics, footprint and engineering support.

The A08 baseline keeps application-core logging calls independent from the concrete runtime backend:

```text
application core / domain code
        |
        v
      SLF4J API
        |
        v
application-core infrastructure: Logging
        |
        +-- initial provider: slf4j-jdk14
                         |
                         v
                  java.util.logging
                     |
                     +-- ConsoleHandler
                     +-- TimestampedFileLogHandler
                     +-- LiveLogHandler
                              |
                              v
                       LoggingServer
                              ^
                              |
                    engineering client connects
```

Working decisions:

- reusable application-core code logs through the SLF4J API;
- `timing-point-core.jar` depends on `slf4j-api` only and must not impose a provider/backend on consumers;
- the executable composition selects exactly one provider;
- the initial Java-8/Pi-Zero application composition uses `slf4j-jdk14`, delegating SLF4J records to the JDK `java.util.logging` backend configured by the core-provided `Logging` infrastructure;
- `timing-point-core.jar` provides reusable `io.github.brainboxemb.eventtiming.timingpoint.infra.logging.Logging` and separate `io.github.brainboxemb.eventtiming.timingpoint.infra.loggingserver.LoggingServer` infrastructure; both use JDK JUL facilities and introduce no external backend dependency because JUL is part of the Java runtime;
- the startup configuration defines one global semantic log level; the A08 baseline uses the normal `TRACE / DEBUG / INFO / WARN / ERROR` vocabulary and maps it to the selected backend;
- `LoggingControl` owns the current global level and may apply a **temporary runtime override**. A runtime override is intentionally not written back to `application.yml` and resets to the configured level on restart;
- the durable operational sink is a human-readable rotating `TimestampedFileLogHandler` with configured size limit and retained generations; its wall-clock filename is for operator readability, not uniqueness, so stale/repeated Raspberry Pi startup time must never overwrite an existing log or cause retention to prune the active file;
- console logging remains available for local startup/development feedback;
- an optional `LoggingServer` is independently composed beside `Logging`, attaches its own live handler, accepts a connection initiated by the JavaFX engineering client and streams new log records through a dedicated diagnostics channel;
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

Configuration describes deployment/composition rather than domain behaviour hard-coded in source. The concrete deployment/configuration contract is owned by **IF-11** in `32-11-ISD-application-configuration.md`.

The main configuration groups are:

```text
ApplicationConfig
├── applicationId
├── timingSystems
│   └── <timingSystem>
│       ├── timingSystemId
│       └── timingNodes
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
- the application composes 1..N internal `TimingSystem` contexts, each with an internal `TimingSystemId`;
- each TimingSystem owns 1..N TimingNodes;
- a `TimingNode` owns its stable functional `TimingNodeId` and configured `LocationId`;
- `TimingSystemId` is local composition/simulation identity and is not added to TimingData/upstream addressing;
- the high-level I/O model separates Devices from Device Networks;
- Devices names the functional device endpoints/concepts, including antennas, keypads, beepers, passive CAN devices and smart network devices;
- the application may compose 0..N configured antennas; each antenna has its own `AntennaId` and may map to 1..N `TimingNodeId` targets;
- Device Networks contains `CanNetworkController` for the actively managed CAN network and `NetworkDeviceService` for bidirectional network-device communication;
- when upstream messaging is configured for a TimingSystem, its protocol/gateway context uses 1..N connectors; multiple hosted TimingSystems keep those semantic contexts separate;
- connector-specific external names/routing identities do not replace `TimingNodeId`;
- presentation endpoints reference TimingNodes explicitly; an HTTP port, tablet or shell binding is not a property of the TimingNode domain object.

Deployment composition is intentionally small and default-driven:

```text
built-in application profile defaults
        +
platform defaults
        +
operating-mode defaults
        +
explicit deployment overrides
        +
resolved secret values
        =
effective ApplicationConfig
```

The selected **application profile** defines a topology/capability template for
the Timing Point Application. Concrete deployment profile IDs, TimingNode counts,
device combinations and compatibility mappings are not defined by this public
architecture unless an explicit public requirement owns them.

Profiles do not create different application/domain models. They resolve to the
same TimingSystem/TimingNode architecture and may be combined with platform and
operating-mode defaults plus explicit deployment configuration within the
profile's compatibility rules.

Platform and operating mode remain independent dimensions. Simulation may replace
concrete adapters while preserving the same TimingNode/domain implementation.

Console, Remote Shell and API form the baseline control/automation capability set
of the Timing Point Application and are not selected by the application profile.
Deployment configuration still controls concrete listener/binding settings. Web
remains a separate per-TimingNode browser-facing capability.

Startup follows distinct responsibilities:

```text
select defaults
  -> apply explicit deployment overrides
  -> resolve effective typed configuration
  -> validate references/settings
  -> runtime Composition composes the application
```

Profile/platform/mode resolution is configuration infrastructure. It is complete
before `Composition` receives the effective runtime `Config`; composition
does not contain profile-specific branches.

Build provenance remains separate from deployment configuration. `BuildIdentity` describes the built artifact; it is not loaded from IF-11 deployment settings. Core `EmbeddedBuildIdentityLoader` interprets the standard embedded provenance resource, while the concrete executable owns and filters that resource with its own application/build values. The embedded provenance contains stable build inputs/context — version, exact revision, source ref, build origin and dirty-state — but deliberately omits wall-clock build time, CI run identifiers and actor/user data. This keeps the artifact self-identifying for test/support work without introducing per-run variability solely from timestamp/run metadata.

Working rules:

- keep secrets/credentials out of committed configuration and store only secret references there;
- prefer explicit/manual composition rather than adding a dependency-injection framework without a demonstrated need;
- keep overlay rules deliberately limited rather than creating general inheritance/includes;
- use YAML as the current default IF-11 file syntax and keep its SnakeYAML parser/mapping inside application-core infrastructure; the logical IF-11 contract is not coupled to the SnakeYAML API;
- create Java configuration types only as real executable slices need them rather than mirroring the entire conceptual tree in advance.

### Data and persistence architecture

Keep the data roles simple:

- `LogBook` is passive state and holds committed immutable `TimingData` values;
- `NextUpTeams`, `StageStartTimes` and `EventData` are separate passive
  per-node state objects;
- the TimingNode worker is the single writer for those mutable per-node objects;
- each state type that needs persistence owns its semantic persistence rules above the lower Storage layer;
- `TimingDataPersistence` is the durable/recovery semantic boundary for committed timing data;
- lower Storage contracts remain generic and contain no TimingData/TimingNode semantics;
- when NextUpTeams, StageStartTimes or EventData require persistence, that persistence follows the same dependency direction rather than adding Domain interfaces implemented by I/O;
- queries read consistent state without becoming another owner of it.

For example, StageStartTimes may be sent again when a TimingNode is opened after
a reboot, while the separately stored historical snapshots remain useful for
post-event analysis.

The persistence architecture permits simple local files and does not require an
embedded database. SDD-01 defines ordering, commit/visibility and the different persistence
roles. SDD-02 defines the Java worker and store boundaries.

Practical detailed-design work includes a half-written last TimingData record,
corrupt-file reporting, durable flush/fsync behaviour, file rotation and bounded
consumer reads. Analysis stores may use simpler append/snapshot formats because
they do not define the TimingData commit point.

### Integration architecture

The **external device and network topology is owned by the SSSD**, because RFID/CAN devices, local LAN clients, displays and the upstream system are system-level deployment/interface relationships. This SSD starts at the **Timing Point Application** (SI-01) boundary and explains how the application realises those system interfaces internally through ports, adapters, callbacks, status handling and transport implementations.

#### Upstream messaging

Upstream messaging is a semantic system boundary, not a RabbitMQ API.
`UpstreamProtocol` in Domain defines the messages and state semantics exchanged
with the upstream system. It uses `TimingData` for timing-record payloads and
also owns synchronisation/reconciliation and system-level protocol messages such
as ping/pong.

`UpstreamGateway` and its 1..N connectors remain I/O responsibilities. They
carry the encoded protocol representation and own transport/session resources;
they do not become owners of TimingData fields or upstream protocol semantics.
`UpstreamMessageRouter` owns application-level target resolution after semantic
protocol decoding. A system-level operation is delivered through the owning
`TimingSystem.UpstreamMessagePort`; a TimingNode-targeted operation is resolved
by `TimingNodeId`, submitted through that TimingNode's serial boundary and
enters/leaves through `TimingNode.UpstreamMessagePort`. Protocol-level
operations such as heartbeat/status and synchronisation control therefore do
not need to be forced through a TimingNode.

```text
external upstream system
        |
        +--> RabbitMqConnector --+
        +--> DebugConnector -----+--> UpstreamGateway
                                      |
                                      | encoded UpstreamProtocol
                                      v
                               UpstreamProtocol
                                 /          \
                                /            +--> TimingData
                               v
                      UpstreamMessageRouter
                         |              |
                         v              +--> TimingNodeId
                   TimingSystem                |
              UpstreamMessagePort              v
               status / ping              TimingNode
                                       UpstreamMessagePort
```

Exact RabbitMQ connection/channel topology, routing keys and retry mechanics are
connector-level decisions. Product/deployment-specific upstream-system names and
private transport details remain outside the public architecture documentation.
Public protocol semantics and TimingData compatibility remain owned by Domain.

`TimingSystemId` and `ApplicationId` are not required on the upstream wire. `UpstreamMessageRouter` provides target resolution without becoming a generic internal message bus. Protocol messages that belong to the configured TimingSystem use its `UpstreamMessagePort` and `UpstreamProtocol`/`SystemStatus`; they do not need to be forced through a TimingNode.

#### RFID

RFID integration is an adapter boundary. Raw vendor callbacks/protocol frames do not
directly mutate application state. A concrete antenna provider owns protocol/device
interaction and emits decoded observations through the common antenna capability.

The stable decoded observation contains at least:

```text
TagObservation
  TagId
  RSSI
  TimingTimestamp
```

The timestamp is attached at the earliest accepted point at which SI-01 can identify the
observation as a decoded tag observation. When a provider exposes a trustworthy source
timestamp that can be mapped to the SI-01 time model, the adapter may use it; otherwise the
adapter uses the Runtime-composed PlatformEnvironment wall clock at the observation boundary. Timestamp
assignment is not delayed until registration commit.

An antenna publishes observations through the normal local typed event mechanism. The
antenna owns `Event<TagObservation>`; consumers receive only the
`EventSource<TagObservation>` view. Delivery is synchronous on the provider/device
callback thread, so downstream processing must remain short and must not wait for
TimingData persistence.

Antenna operation has a lifecycle around observation delivery. An
`AntennaManager` owns one or more configured antenna instances and coordinates:

- optional power switching where the deployment provides it;
- open/startup and initialization;
- a one-shot startup probe that can power/open the antenna, perform a
  hello/identity/version check and close it again without starting normal inventory;
- inventory start/stop per antenna so multiple configured antennas can be controlled
  independently;
- normal shutdown and recovery/reinitialization.

Concrete vendor commands, framing, crypto/proprietary codecs and retry sequences remain
inside the provider/private implementation. A provider may hide device-specific power
control behind its antenna implementation, or runtime composition may provide an optional
power-control capability to the manager; external power switching is not required of every
antenna.

Antenna lifecycle/device-control calls are separate from observation delivery. One AntennaManager belongs to one TimingSystem and owns ordered control state
for its configured antennas. Probe, power, initialize, inventory start/stop and shutdown
are submitted as bounded control work so potentially blocking device I/O does not run on
a TimingNode lane or on a presentation callback. Application startup may wait for a
result-bearing manager operation because readiness depends on that outcome.

The Java realization should use a shared bounded I/O `ExecutorService` rather than a
dedicated thread per AntennaManager or per antenna. Per-manager ordering is a logical
serialization constraint layered on that executor; it does not imply permanent thread
ownership. Other device/network capabilities may use the same bounded I/O execution
facility where their blocking characteristics fit the same policy, while retaining their
own state/ordering ownership.

Observation delivery does not run on the manager control lane. Concrete providers emit
`TagObservation` from their device/library callback context through the synchronous local
event. TagProcessor therefore executes only short thread-safe filtering/mapping/admission
work on that callback thread and returns after bounded TimingNode submission.

Raw TagObservation retention is optional non-critical diagnostic persistence. When enabled,
it subscribes to the same observation event but only performs a bounded non-blocking handoff
from the provider callback. File/storage I/O executes later on the shared bounded I/O
executor. Queue saturation or diagnostic-store failure must not block or reject the normal
registration path; it is reported through diagnostics/counters and may drop raw diagnostic
observations according to the configured retention policy.

This is deliberately different from TimingData/LogBook persistence. TimingData durability
is part of the committed-domain-record contract and remains ordered with commit before
LogBook visibility. A raw observation log is not TimingData, is not used to rebuild LogBook and does not
participate in registration commit success.

After decoding, generic SI-01 tag processing is distinct from vendor protocol handling.
Repeated reads of one physical passage are first aggregated as one observation burst.

```text
Antenna Event<TagObservation>
          |
          v
   observation burst per TagId
     - update strongest RSSI/timestamp
     - close after configured quiet time
     - force close at configured maximum burst duration
          |
          v
      TagProcessor
        - choose strongest observation/timestamp
        - TagId -> RegistrationId mapping
        - registration duplicate suppression
          |
          v
      TimingNode bounded submission
```

The absence of a new observation is significant: once no observation for that TagId has
arrived during the configured quiet timeout, the open burst is closed and its selected
candidate continues immediately to filtering/mapping/admission. Registration therefore
does not depend on a later tag callback arriving.

A maximum burst duration prevents a continuously visible tag from postponing processing
indefinitely. When that maximum expires, the current burst is closed even if observations
continue. A subsequent observation may open a new burst, while the longer
registration-duplicate window prevents an already accepted RegistrationId from being
registered again too soon.

Burst aggregation and registration duplicate suppression solve different problems.
Low-strength reads remain part of the burst because the purpose is to find the strongest
observation of the passage, not to register as quickly as possible.

The selected event timestamp is the timestamp of the observation with the highest RSSI in
the closed burst. That strongest observation is used as the best available approximation
of the participant being closest to the antenna, giving a more uniform registration point
than the first/last read of a variable RF read zone. For equal maximum RSSI, the first
observation at that maximum is kept.

D04 does **not** define a minimum-RSSI rejection threshold. If later evidence shows that
signal-strength rejection is needed, that is a separate requirement/design decision and
must not be inferred from the presence of RSSI in TagObservation.

Burst deadlines and the registration duplicate window use monotonic elapsed time.
Their durations are configuration/profile decisions. The processor must remain safe
when observations from multiple antennas arrive concurrently and must not add an unbounded
worker merely to serialize them.

`TagId -> RegistrationId` resolution is owned by `EventData`. One RegistrationId
may be associated with multiple TagIds; TagProcessor resolves the semantic TagId
before RegistrationId-keyed duplicate suppression and passage aggregation.

Source/provider-specific decoding and mapping policy must not be guessed by a generic
adapter. Built-in `SimulatedAntenna` uses the same lifecycle, observation event and
TagProcessor path as a real provider and does not call TimingNode/TimingData through a
test-only bypass.

#### CAN, keypad, beeper and displays

`CanNetworkController` owns the active CAN network: bus lifecycle, discovery/scanning,
device online state and communication. CAN/device callbacks do not mutate
TimingNode state directly; accepted work crosses the normal application/serial
boundary.

`Rev1CanDisplay` is the passive CAN display generation. SI-01 owns the
display-specific `DisplayModel` for this path and actively translates that model
into CAN/device commands. The display does not own the ready-team/domain model.

`Rev2WifiDisplay` is deliberately different. It is a smart external client with
its own rendering and synchronisation behaviour. `NetworkDeviceService` provides the bidirectional network-device boundary.
In the current IF-09 design it makes the SI-01 data service discoverable and
accepts the session initiated by Rev2WifiDisplay. Rev2WifiDisplay owns
reconnect/resynchronisation behaviour. The concrete discovery/listener/session
mechanics are detailed below the high-level architecture rather than represented
as additional peer components.

SI-01 therefore publishes current timing/status/reference data to smart clients;
it does **not** drive Rev2WifiDisplay through the passive-display `DisplayModel`
and does not need to know how that smart display renders the data. Exact mDNS
service names and the application protocol (for example TCP/WebSocket) remain
deferred until IF-09 implementation needs them.

#### Connectivity

Status must distinguish at least local network reachability from external/upstream session health where those distinctions affect operator decisions. Temporary external connectivity loss must not silently invalidate otherwise available local operation.

### Development view

#### Development boundaries

The development structure shall preserve the architecture dependency direction
without assuming that every architecture layer is a package or Maven artifact.

Architecture-level boundaries are:

- SI-01 has a reusable application-core implementation and a deployable
  executable application;
- the public IF-05 Java contract must be independently consumable by SI-01 and
  engineering/test tooling without depending on SI-01 internal Domain packages;
- dependencies normally follow the layer order downward; lower I/O code does not import Application/Domain types;
- higher layers may use generic lower-layer I/O contracts while Runtime composition selects concrete I/O implementations;
- public reference/core implementation code compiles and verifies without private
  production implementations.

The exact Maven reactor, artifact names, Java package layout, shared
`timing-data-api` placement and dependency checks are owned by SDD-02.

#### Public/private extension model

Private repositories may provide production device control, protocol implementations, deployment mappings and production data/codecs. Public core/reference implementation code defines supported contracts and must compile/test without those private implementations.

SI-01 uses one small **typed provider/extension mechanism** for implementation families that may cross the public/private boundary. The currently expected provider contracts are:

```text
TimingDataProvider
UpstreamProtocolProvider
AntennaProvider
CanProtocolProvider
DisplayProtocolProvider
```

The provider contracts are capability-specific; there is no generic domain-level
`Plugin` abstraction. Infrastructure extension-discovery support finds built-in and external providers at startup; `Composition` uses the resulting typed registry, validates configured provider IDs and then builds the normal runtime graph. Runtime/domain components receive normal typed
interfaces and never interact with class loaders or provider discovery.

Provider discovery/loading is a startup/composition responsibility. Provider IDs
must remain unambiguous and configuration errors must fail explicitly. The
concrete Java discovery/class-loading mechanism is detailed in SDD-02.

Built-in reference/simulation implementations remain part of the normal public
software where they are needed for development and verification. In particular,
`SimulatedAntenna` is always built in. Figure SI01-01 labels the generic
extension-provided alternative `VendorAntenna`; that label is illustrative, not
a fixed public implementation type. A deployment can select an
extension-provided implementation without changing the application/domain path
used by the built-in implementation. IF-11 owns provider selection in deployment
configuration; the concrete external-JAR packaging/search path remains a detailed
implementation concern.

### Runtime execution and target-resource architecture

SI-01 is designed for constrained Raspberry Pi-class targets as well as development
hosts. Runtime resource rules therefore apply across component boundaries rather than
belonging to one Java helper class:

- keep each TimingNode work queue bounded;
- prefer explicit bounded queues over hidden or unbounded executor queues;
- keep contained Domain state passive and single-writer where practical;
- keep concrete TimingData values immutable after creation;
- avoid routine LogBook list copies or deep copies when direct bounded traversal is
  sufficient;
- introduce reusable scratch storage, compact indexes or incremental derived state only
  when measurement demonstrates a concrete benefit;
- keep blocking network/retry work behind capability-specific output boundaries rather
  than on the TimingNode execution lane;
- move analysis-store writes off the TimingNode lane only when measurement shows that
  synchronous writes cause unacceptable delay;
- measure queue high-water, storage latency, LogBook/query cost, heap/GC behaviour and
  scheduling/CPU effects before increasing concurrency or adding runtime complexity.

These are software-item architecture constraints, not a prescription for one particular
Java executor implementation. SDD-02 defines the current Java realization of the
TimingNode execution lane; the verification/environment documents define how runtime
characterization evidence is collected.

### Technology decision register

This table intentionally lives in the architecture section of this SSD because these choices shape the whole **Timing Point Application** (SI-01) architecture.

| Concern | Current direction | Current rationale / open point |
| --- | --- | --- |
| Java baseline | Java SE 8 is the current SI-01 baseline | architecture baseline; verify the selected runtime on the Pi target |
| Extension mechanism | typed capability-specific provider contracts with startup composition; runtime/domain code remains provider-discovery agnostic | concrete Java discovery/loading is owned by SDD-02 |
| Build | Maven | accepted |
| Concurrency | TimingNode is an active object with one bounded serial execution boundary; contained state objects stay passive; callbacks, long queries and slow delivery remain outside that worker | SDD-02 uses composition and keeps the executor implementation replaceable |
| Internal messaging | typed immutable command/event/query objects only at async/ownership boundaries + explicit TimingNode mapping/routing at the owning boundary; no central generic dispatcher; direct calls inside a TimingNode task | architecture baseline; add/refine consumer API signatures only for concrete needs |
| Time model | dedicated `TimingTimestamp` + Runtime-composed `PlatformEnvironment` with absolute `Clock` and separate `MonotonicClock` | IF-05 fixes canonical external timestamp serialization; simulation may provide a controlled wall clock; clock synchronisation/correction policy remains to be completed |
| Dependency injection | explicit/manual composition | add a framework only if measured/maintainability complexity justifies it |
| Logging | SLF4J API in reusable application core; default executable provider `slf4j-jdk14` / `java.util.logging` | handlers/retention remain configuration and operational concerns |
| Configuration | IF-11 effective `ApplicationConfig`: base + platform + optional profile + secret resolution; YAML/SnakeYAML is the default Java input realization | profile/platform/mode resolution is architecturally defined but not yet fully implemented |
| Persistence | Domain-owned TimingDataPersistence over generic lower-layer storage; file/database mechanisms do not import Domain/Application types | ordering and visibility in SDD-01; Java storage/persistence split in SDD-02; record contract in IF-05 |
| API HTTP | JDK `HttpServer` for IF-03 request/response | selected transport; belongs to the API functional interface |
| API WebSocket | `org.java-websocket:Java-WebSocket:1.6.0` on a dedicated configured listener | selected transport; Java 8+, pure Java/NIO and existing SLF4J boundary; keep the HTTP transport separate |
| Remote shell | Java 8 JDK `ServerSocket`, line-oriented TCP, shared command semantics | development/service interface with one active session and reconnect; SSH/Telnet/authentication are outside the current public design |
| Upstream messaging | semantic ports + socket test adapter + RabbitMQ production-shaped adapter | architecture direction established; implementation detail deferred |
| Test doubles | public controllable stubs through the same supported ports | established direction |

Technology choices should fit the actual application and target. Pi compatibility is verified on real hardware; memory/thread footprint becomes a design concern only when measurements make it one.

### Physical/deployment view

Representative **Timing Point Application** (SI-01) deployments are:

```text
Production field host
  Raspberry Pi Zero / Zero W
    one Timing Point Application process
      one or more TimingSystem aggregates
        each with 1..N TimingNodes
      local devices + local files
      optional network/upstream connectivity

Development/test host
  Linux or Windows
    same Timing Point Application core/application behaviour
    real or stub adapters
    may host multiple independent TimingSystems for simulation
```

The architecture should not require a different domain implementation for simulation. Different compositions select different adapters/topologies around the same application/domain behaviour. The system-level placement of the Timing Point Application relative to devices, operator clients, LAN/Wi-Fi and the upstream system is defined in the SSSD rather than duplicated here.

### Testability and failure/recovery architecture


Testability is an architecture property. Application/domain code should where practical:

- avoid uncontrolled threads and global mutable state;
- receive absolute time through an injectable abstraction;
- receive duration/timeout measurements through a controllable monotonic abstraction where needed;
- include tests that step the wall clock forwards/backwards and cross representative DST/local-time transitions;
- exercise per-TimingNode ordering/non-overlap, fair progress between node-local lanes on shared role workers, and bounded-ingress overload behaviour deterministically;
- depend on semantic ports rather than concrete device/network libraries;
- keep protocol parsing in adapters;
- use deterministic handlers that can run synchronously in unit tests;
- expose observable status for degraded/failure conditions;
- avoid `Thread.sleep()` as a domain timing mechanism.

Failures should stay visible and should not silently lose timing history. Retry
counts, timeouts and the exact durability guarantee are detailed-design choices
once we have real implementation/measurement evidence.


### Detailed-design documents

Keep this SSD at architecture level. Put implementation detail in the focused
SDDs below instead of repeating it here.

Current focused SDDs:

```text
43-01-SDD-01-data-and-display-design.md
  internal data/runtime algorithms:
  LogBook recording, TimingData persistence/recovery, query isolation,
  prepare-team/reference/display behaviour

43-01-SDD-02-java-component-design.md
  concrete Java realisation:
  Maven artifacts, packages, classes/interfaces, queue/thread/executor choices,
  provider discovery and dependency checks

43-01-SDD-03-backoffice-transport-design.md
  transport realisation below the upstream semantic boundary
```

IDDs define the external/file/API contracts. The SDDs use those contracts; they
do not define a second version of them.

### Open architecture decisions

Only keep questions here if the answer could change the SI-01 architecture.
Implementation questions go in the relevant SDD.

Open architecture questions include:

- operational policy for material wall-clock corrections when it affects timing
  correctness or operator action;
- final upstream/backoffice semantic responsibilities as IF-06 is promoted;
- whether measured multi-TimingNode/Pi resource behaviour ever requires changing
  the current ordered-per-node responsibility model;
- any target-runtime limitation that forces a change to the Java-8/application
  architecture baseline.

Queue sizes, Java signatures, executor choice, fsync/atomic file operations,
rotation and LogBook indexes belong in SDD-01/SDD-02, not here.

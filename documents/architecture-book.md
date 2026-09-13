# Software architecture document set

Generated review/output book containing the software-system architecture, software-item architectures, and only currently active focused detailed design.

The numbered source documents on the source branch remain authoritative.

## Contents

- [Software System Architecture Document (SSAD)](./30-SSAD-software-system-architecture.md)
- [Timing Application Architecture (SAD)](./31-01-SAD-timing-application-architecture.md)
- [Java component, package and artifact detailed design](./31-01-SDD-02-java-component-design.md)
- [GUI Application Architecture (SAD)](./31-02-SAD-gui-application-architecture.md)
- [Web Operator Application Architecture (SAD)](./31-03-SAD-web-operator-application-architecture.md)

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

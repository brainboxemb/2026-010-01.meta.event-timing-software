# Timing Application Architecture (SAD)

Status: working draft / non-authoritative

Software item: **SI-01 — Headless Timing Application**

This Software Architecture Document describes the architecture of software item 01: the headless Java timing application. It sits below `30-SSAD-software-system-architecture.md` and is the primary technical design document for SI-01 at the current project stage.

The SAD is expected to contain concrete architecture decisions such as threading, concurrency, internal messaging, framework/library choices, logging, configuration, persistence, composition and integration structure. A separate SDD is created only when a topic genuinely needs implementation detail that would make this SAD harder to use.

## Document relationship

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

## Architecture drivers

SI-01 architecture is driven by these concerns:

- run on the original Raspberry Pi Zero / Zero W as a mandatory constrained target;
- remain usable on Linux/Windows development and test hosts;
- keep authoritative timing/domain state local to SI-01;
- support one or more logical timing-system instances without state leakage;
- preserve deterministic ordering of state-changing work;
- isolate external I/O concurrency from application/domain state mutation;
- remain testable without production RFID, CAN, backoffice or proprietary implementations;
- expose one coherent command/query/status/event model to local and network presentation adapters;
- support local persistence/recovery and disconnected operation;
- keep public framework/reference code independent of private production source;
- avoid framework complexity that is not justified on the constrained target.

## +1 scenarios used to validate the architecture

The existing use cases in `04-UC-system-use-cases.md` are the scenario source. The SAD should not create a second competing use-case catalogue.

Representative architecture-validation scenarios include:

1. start SI-01, load configuration, expose version/status and shut down cleanly;
2. accept an operator command through local or network presentation and route it to the correct logical timing-system instance;
3. accept a device observation from an external callback without allowing that callback thread to mutate authoritative application state directly;
4. persist accepted operational state and recover it after restart;
5. continue local operation while a GUI/browser or backoffice connection is unavailable;
6. host several timing-system instances in a development/simulation composition without state leakage;
7. substitute public stubs for production devices/transports while exercising the same application/domain paths.

These scenarios are used to check the logical, process, development and deployment views below.

## Logical view

### Layered application architecture

The primary logical view is a responsibility/layer view. It describes semantic ownership and dependency direction; it does **not** prescribe one Maven artifact per layer.

![SI-01 layered architecture](../../../raw/prod/docs/assets/architecture/layered-architecture.svg)

The source for this view is `docs/_diagrams/layered-architecture.yaml`.

### Presentation

Presentation exposes SI-01 behaviour and current state to external clients through concerns such as:

```text
HTTP / JSON
WebSocket
local console
remote shell
protocol/DTO mapping for those interfaces
```

Presentation translates external requests into application commands/queries and application status/events into external representations. It does not own running application state.

### Application

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

### Domain

The domain responsibility owns reusable timing rules, services, entities and value semantics. Representative services currently include:

```text
RegistrationService
StartTimeService
ReadyTeamService
ReferenceDataService
```

Representative concepts include timing-system identity/value concepts, `RegistrationAsset`, `RegistrationSource`, registration observations/results, start-time values, ready-team values and reference-data value objects.

Product/deployment-specific policy does not automatically belong in the reusable domain model.

### Core runtime support

Core runtime support provides reusable execution mechanics that let application/domain behaviour run predictably, for example:

```text
serialized execution
lifecycle mechanics
routing primitives
scheduling
command/event dispatch mechanics
```

Core runtime support is not a second owner of domain behaviour or application state.

### Infrastructure / integration

Integration implementations connect SI-01 to external systems/devices and persistence mechanisms, including:

```text
persistence / file backup and restore
backoffice socket / RabbitMQ integration
RFID integration
CAN integration
display integration
```

### Platform

Platform abstractions isolate execution-environment and low-level facilities such as clock/time source, filesystem/path primitives, executor/thread primitives, process/runtime information and network/OS facilities.

Platform is not a catch-all location for HTTP, RabbitMQ or device/domain protocols.

### Cross-cutting concerns

Logging, configuration, diagnostics, metrics where useful and build/version identity cross several responsibilities without becoming owners of domain/application state.

## Principal runtime abstractions

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

![SI-01 configurable runtime topology](../../../raw/prod/docs/assets/architecture/runtime-registration-topology.svg)

Stable domain facts behind this topology are maintained in `03-domain-baseline.md`; this SAD owns their software-architecture composition and execution implications.

## Command, query and event model

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

The preferred initial direction is explicit typed command/event routing because the flow is easier to reason about, test and keep lightweight on the Pi Zero. A third-party messaging/event framework should only be introduced when it solves a demonstrated problem better than explicit routing and JDK concurrency primitives.

## Process view: threading and concurrency

External libraries may create callbacks/threads for HTTP/WebSocket, shell, RFID, CAN, RabbitMQ, timers and network sessions. Those threads must not directly mutate authoritative timing-system state.

The intended processing path is:

1. capture externally meaningful timestamps immediately where timing matters;
2. attach stable instance/device/source context;
3. convert input into an immutable command/event;
4. route it to the addressed `TimingSystemInstance`;
5. serialize state-changing handling for that instance;
6. keep blocking hardware/network/file operations outside the serialized state path;
7. return relevant completion/failure into the state path as commands/events when required.

```text
many adapter callbacks
        |
        v
routing + immutable message
        |
        v
TimingSystemInstance ingress
        |
        v
logical SerialExecutor
        |
        +-- registration/source state
        +-- lifecycle/ready-team/display state
        +-- status transitions
```

A logical serial executor does not imply a dedicated operating-system thread. Multiple logical executors may share a small backing `ExecutorService` appropriate to Pi Zero constraints.

### Concurrency technology direction

Initial architectural preference:

- use `java.util.concurrent` primitives (`Executor`, `ExecutorService`, queues/futures where justified) as the baseline;
- provide a small explicit serial-execution abstraction owned by the runtime support layer;
- avoid introducing a broad concurrency/reactive framework until a requirement demonstrates value that outweighs footprint and conceptual complexity;
- preserve the ability to use a direct/synchronous executor in deterministic unit tests.

The exact queue bounds, rejection/backpressure policy, backing-pool size and fairness policy remain architecture decisions to be measured and resolved before the corresponding workload is implemented.

## Internal messaging direction

Internal messaging is a programming/architecture mechanism, not a reason to introduce a broker inside SI-01.

Preferred direction:

```text
typed command/query/event objects
        +
explicit routing/dispatch
        +
per-instance serialized state-changing execution
```

Do not use RabbitMQ, an in-process event bus or another messaging framework simply to move calls between internal layers. External broker transport belongs to the backoffice integration adapter.

A framework may still become appropriate if later needs such as complex fan-out, durable internal queues or independently deployable components appear; those needs do not exist in the current architecture.

## Status and diagnostics architecture

Status is a first-class current-state model and is distinct from logging.

Status should allow presentation and diagnostics to observe application, timing-system and subsystem health without parsing log text. Representative areas include:

- application version / uptime / overall health;
- timing-system lifecycle;
- registration asset/source state;
- RFID power/startup/protocol/heartbeat;
- CAN/device availability;
- persistence/backup state;
- reference-data freshness;
- network/backoffice connectivity;
- inbound/outbound synchronisation state.

Status snapshots exposed to consumers should be immutable from the consumer perspective.

Logging records diagnostic/history information; status represents current operational state. One must not be used as a substitute for the other.

## Logging architecture

Logging is a SAD-level technology decision because it affects almost every component, operational diagnostics, footprint and private/public integration.

Working direction:

- application/framework code should log through a stable logging facade rather than bind domain code to a concrete backend;
- structured context should include stable identifiers such as timing-system/source/device/correlation identity where useful;
- logging must not become the mechanism for application status or durable domain history;
- configuration should permit development verbosity while keeping field deployment output and resource use controlled;
- concrete backend and version must be selected and measured on the Pi Zero before the architecture decision is accepted.

**Open technology decision:** evaluate a lightweight SLF4J-based approach versus using only JDK logging. The decision should consider Java 8 support, footprint, configuration, rolling/file behaviour and operational familiarity rather than popularity alone.

## Configuration and composition architecture

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

## Data and persistence architecture

The initial architecture uses typed in-memory authoritative state/repositories with simple file-based persistence/restore rather than requiring an embedded database.

Keep these concepts distinct:

1. ingress/ordering — concurrency ownership;
2. registration ledger/source sequence — traceable domain/operational history;
3. ready-team journal/current projection — separate operational capability;
4. reference data — locally available input received from external sources;
5. local backup/restore — restart/power-loss recovery;
6. backoffice outbox/synchronisation — pending external delivery/reconciliation.

Registration identity remains source-scoped; the current stable conceptual key is `(RegistrationSystemId, SequenceNumber)`.

Persistence durability semantics, file format, atomic-write strategy and corruption/recovery rules remain open decisions and may justify a focused data/persistence SDD only when implementation reaches that complexity.

## Integration architecture

The principal device/network relationships are shown below. The diagram is an SI-01 integration/deployment view, not a software-system decomposition.

![SI-01 device and network integration topology](../../../raw/prod/docs/assets/architecture/device-network-topology.svg)

### Backoffice

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

### RFID

RFID integration is an adapter boundary. Raw callbacks/protocol data do not directly mutate application state. The adapter is responsible for protocol/device interaction and turns accepted observations/health changes into typed application-facing messages.

Power/startup/recovery lifecycle and filtering semantics are architectural concerns where they affect application behaviour; exact protocol commands, crypto/proprietary codecs and retry sequences remain implementation/private detail.

### CAN, keypad and displays

CAN/device integrations follow the same rule: device/protocol callbacks enter SI-01 through integration boundaries and application-facing messages. Display state remains owned by SI-01 rather than by the display device.

Display V1 is a CAN-based integration. Display V2 is a network client that discovers the SI-01 service on the local network and connects for synchronised display data. Exact protocol/session details remain deferred until implementation requires them.

### Connectivity

Status must distinguish at least local network reachability from external/backoffice session health where those distinctions affect operator decisions. Temporary external connectivity loss must not silently invalidate otherwise available local operation.

## Development view

### Maven artifact boundary

The current implementation baseline deliberately starts with one reusable framework library and one executable application:

```text
event-timing-parent
framework/ -> event-timing-framework.jar
app/       -> event-timing-app.jar
```

Architecture layers/packages are **not automatically Maven artifacts**. A new artifact is justified by an actual consumer, reuse, dependency, lifecycle, deployment, public/private or release boundary.

### Package direction

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

### Public/private extension model

Private repositories may provide production RFID control, encrypted/proprietary protocol implementations, deployment mappings and production backoffice codecs. Public framework code defines supported contracts and must compile/test without those private implementations.

## Technology decision register

This table intentionally lives in the SAD because these choices shape the whole SI-01 architecture.

| Concern | Current direction | Status / next evidence |
| --- | --- | --- |
| Java baseline | Java SE 8 initially because original Pi Zero/ARMv6 is mandatory | accepted baseline; pin/verify reference runtime |
| Build | Maven | accepted |
| Concurrency | JDK `java.util.concurrent` + small serial-execution abstraction | working direction; measure pool/queue behaviour |
| Internal messaging | typed immutable commands/events + explicit routing; no generic event bus initially | working direction |
| Dependency injection | explicit/manual composition initially | working direction; add framework only if complexity justifies it |
| Logging | stable facade; lightweight backend to be selected | compare SLF4J-based backend vs JDK logging on target |
| Configuration | external typed/validated configuration | file format/library still open |
| Persistence | typed in-memory state + simple file persistence/restore | durability/file mechanics still open |
| HTTP/WebSocket | embedded Java-8-compatible technology | selection still open |
| Remote shell | shared command semantics, transport technology open | selection still open |
| Backoffice | semantic ports + socket test adapter + RabbitMQ production-shaped adapter | architecture direction established; implementation detail deferred |
| Test doubles | public controllable stubs through the same supported ports | established direction |

A technology should not be selected solely because it is common in unconstrained server applications. Pi Zero compatibility, memory/thread footprint, testability and operational simplicity are architecture criteria.

## Physical/deployment view

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

The architecture should not require a different domain implementation for simulation. Different compositions select different adapters/topologies around the same application/domain behaviour.

## Testability and failure/recovery architecture

Testability is an architecture property. Application/domain code should where practical:

- avoid uncontrolled threads and global mutable state;
- receive time through an injectable abstraction;
- depend on semantic ports rather than concrete device/network libraries;
- keep protocol parsing in adapters;
- use deterministic handlers that can run synchronously in unit tests;
- expose observable status for degraded/failure conditions;
- avoid `Thread.sleep()` as a domain timing mechanism.

Fault handling should preserve local authority, traceability and explicit status. Exact retry counts, timeouts and durability guarantees belong to requirements or focused implementation design when evidence exists.

Detailed verification strategy belongs in `50-SVP-software-verification-plan.md`.

## When a separate SDD is justified

A separate SDD should be introduced or retained only when at least one of these is true:

- the topic has enough algorithm/state-machine/configuration detail that it obscures the architecture in this SAD;
- several implementation alternatives need a focused design/review;
- a component has an independently meaningful lifecycle, contract or complexity;
- the detail is needed directly by implementation/reviewers but is not useful to a reader trying to understand SI-01 architecture as a whole.

Examples that may eventually justify focused SDDs include exact persistence/restore mechanics or exact RabbitMQ connection/retry/topology behaviour. Threading, messaging, logging and the main runtime topology remain SAD concerns unless their implementation becomes substantially more complex.

## Detailed-design document disposition

This architecture review deliberately reduced the active SDD set.

- `31-01-SDD-01-timing-system-design.md`: **retired**. Its useful logical/process architecture was consolidated into this SAD or is already represented by the domain baseline; speculative pseudocode/history remains available through Git history rather than as active design.
- `31-01-SDD-02-data-and-display-design.md`: **deferred working note**. It is excluded from the architecture book while persistence/data mechanics are still too early for a dedicated active SDD.
- `31-01-SDD-03-java-component-design.md`: **active focused SDD** because artifact/package/composition decisions already affect the implementation repository.
- `31-01-SDD-04-runtime-topology-and-configuration.md`: **retired**. Stable topology facts are in `03-domain-baseline.md`; runtime/configuration architecture is owned here.
- `31-01-SDD-05-backoffice-transport-design.md`: **deferred working note**. Detailed transport design should mature just in time with backoffice implementation and is excluded from the architecture book for now.

No new SDD should be created during this cleanup unless a clear separate detailed-design purpose is demonstrated.

## Open architecture decisions

The next useful architecture work is to resolve concrete implementation choices, not create more document layers:

- logging facade/backend and field log configuration;
- embedded HTTP/WebSocket technology compatible with Java 8 and Pi Zero constraints;
- remote-shell technology;
- exact `SerialExecutor`/backing-executor design and queue/backpressure policy;
- typed internal message/dispatcher API shape;
- configuration format, validation library and override/secrets model;
- persistence commit/durability/atomic-write/recovery policy;
- reference ARMv6 Java 8 runtime/vendor/version;
- status/health vocabulary and publication model;
- exact public API/SPI boundaries as real consumers appear;
- RabbitMQ connection/channel/retry strategy when that integration becomes active;
- evidence threshold and timing for a later Java 11 migration.

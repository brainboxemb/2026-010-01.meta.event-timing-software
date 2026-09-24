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
- support one or more logical waypoint systems without state leakage;
- preserve deterministic ordering of state-changing work;
- isolate external I/O concurrency from application/domain state mutation;
- preserve unambiguous time semantics across local time zones, daylight-saving transitions and wall-clock corrections;
- remain testable without production RFID, CAN, backoffice or proprietary implementations;
- expose one coherent command/query/status/event model to local and network presentation adapters;
- support local persistence/recovery and disconnected operation;
- keep public framework/reference code independent of private production source;
- avoid framework complexity that is not justified on the constrained target.

## +1 scenarios used to validate the architecture

The existing use cases in `04-UC-system-use-cases.md` are the scenario source. The SAD should not create a second competing use-case catalogue.

Representative architecture-validation scenarios include:

1. start SI-01, load configuration, expose version/status and shut down cleanly;
2. accept an operator command through local or network presentation and route it to the correct logical waypoint system;
3. accept a device observation from an external callback without allowing that callback thread to mutate authoritative application state directly;
4. persist accepted operational state and recover it after restart;
5. continue local operation while a GUI/browser or backoffice connection is unavailable;
6. host several waypoint systems in a development/simulation composition without state leakage;
7. substitute public stubs for production devices/transports while exercising the same application/domain paths;
8. capture and process observations correctly when local civil time crosses a daylight-saving transition or the operating-system wall clock is corrected forwards/backwards.

These scenarios are used to check the logical, process, development and deployment views below.

## Logical view

### Layered application architecture

The primary logical view is a responsibility/layer view. It describes semantic ownership and dependency direction; it does **not** prescribe one Maven artifact per layer.

`TimingApplication` is the top-level executable/composition root. Presentation interfaces, application-layer coordination, domain state and integrations are instantiated as parts of that one running application; `TimingApplication` is therefore not itself a component inside the application layer.

The compact software/domain ownership model is intentionally also kept as copyable text:

```text
TimingApplication
  |
  +-- SystemStatus
  |
  +-- 1..N Waypoint
        +-- UniqueID
        +-- LocationID
        +-- lifecycle / status
        +-- TagProcessor
        +-- StageStartTimeRegistry
        +-- WaypointJournal
        +-- PrepareTeamRegistry
        +-- RaceData
        +-- StageTiming
```

![SI-01 layered architecture](../../../raw/prod/docs/assets/architecture/layered-architecture.svg)

The source for this view is `docs/_diagrams/layered-architecture.yaml`.

### Presentation

Presentation exposes SI-01 behaviour and current state through three deliberately distinct interface perspectives:

```text
Console / Remote Shell     development + service
Desktop GUI Interface      debug / development application
HTTP / WebSocket           iPad / operator UI
```

Protocol/DTO mapping belongs with these presentation boundaries rather than with domain behaviour.

Presentation translates external requests into application commands/queries and application status/events into external representations. It does not own running application state.

### Application

The application layer coordinates use cases without becoming the top-level application container. Its current working decomposition is:

```text
Application layer
  +-- ApplicationConductor
  |     application lifecycle/state orchestration
  |     active Waypoint coordination
  |
  +-- CommandDispatcher
        central command intake and dispatch
        routes commands to the appropriate application/domain responsibility
```

`ApplicationConductor` coordinates application-wide mutable runtime/lifecycle state and the active waypoint composition. It orchestrates application flow without becoming the owner of waypoint domain behaviour.

`CommandDispatcher` is the central command-handling boundary. It accepts commands translated by presentation interfaces and dispatches them to the appropriate application/domain responsibility. It is not a transport endpoint and does not own domain behaviour.

The application layer coordinates persistence/integration ports without moving transport/protocol details into domain behaviour.

### Domain

The domain responsibility owns reusable timing rules, entities, processors, registries, journals and value semantics. Names should describe the responsibility rather than defaulting every capability to a generic `*Service` suffix.

Current naming direction includes:

```text
TagProcessor
StageStartTimeRegistry
WaypointJournal
PrepareTeamRegistry
RaceData
StageTiming
```

`TagProcessor` represents the RFID/tag-observation processing responsibility. It does not own the physical RFID reader/antenna lifecycle.

`StageStartTimeRegistry` owns locally available start-time reference data for the stage ending at the waypoint. It is a registry/state responsibility rather than a generic background service.

`WaypointJournal` is the waypoint-oriented registration/history view. It must preserve the independent `UniqueID` sequence/persistence semantics of committed data rather than turning several logical streams into one untraceable sequence.

`PrepareTeamRegistry` keeps track of the teams that must prepare at the waypoint/exchange point, based on keypad/operator input. The registry also owns the traceable add/remove history needed for audit and restore; that history is an internal persistence/state concern of the registry, not a separate architecture component. Application command handlers coordinate registry mutation + display refresh; there is no separate generic `ReadyTeamService` responsibility merely to wrap those operations.

`RaceData` is waypoint-scoped participant/team/tag reference data, including reserve-tag mapping semantics where applicable. It belongs to the `Waypoint` data/state model. Synchronising or loading that data from backoffice is handled by application/integration responsibilities rather than by turning the data object itself into a generic service.

`StageTiming` owns the derived stage-timing view for the waypoint, including elapsed/running times and local ranking. It is not primarily a registry; it derives timing results from waypoint registrations and stage/reference data.

Representative concepts include waypoint identity/value concepts, `Stage`, `LocationID`, `UniqueID`, registration observations/results, `TimingTimestamp`, start-time values, ready-team values, tag-class values and race/participant/tag-reference values.

Hardware inventory concepts such as `RegistrationAssetId` and `AntennaId` may appear in domain/application data as origin or diagnostic context, but the physical asset/antenna hierarchy is not the domain/software decomposition.

Decoded RFID identity must preserve whether a tag is normal, reserve or test-class until the applicable domain/use-case policy has been applied. A test tag is therefore not silently normalised into a normal participant identity at an adapter boundary.

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

A `Waypoint` is the primary independently addressed operational/domain aggregate inside SI-01. One application process may host one or more waypoints. `SystemStatus` is application-scoped and aggregates/monitors overall runtime and waypoint status rather than belonging to one waypoint.

The architecture deliberately uses **separate views** for software/domain decomposition, hardware/deployment topology and configuration/identity mapping. These views must not be collapsed into one ownership tree.

### Software/domain decomposition

```text
TimingApplication
  |
  +-- SystemStatus
  |
  +-- 1..N Waypoint
        +-- UniqueID
        +-- LocationID
        +-- lifecycle / status
        +-- TagProcessor
        +-- StageStartTimeRegistry
        +-- WaypointJournal
        +-- PrepareTeamRegistry
        +-- RaceData
        +-- StageTiming
```

`UniqueID` is the stable identity of the `Waypoint` and scopes its registration sequence, persistence and synchronisation semantics. `LocationID` is the separately configured physical event location.

![SI-01 software/domain decomposition](../../../raw/prod/docs/assets/architecture/waypoint-software-decomposition.svg)

The exact Java class/package boundaries may evolve as implementation evidence appears, but the `Waypoint` aggregate is the semantic owner of the operational waypoint state. The physical registration asset is not a child component of this software tree.

### Hardware/deployment decomposition

A physical registration system is described separately:

```text
RegistrationAsset asset-01
    +-- Antenna ANT1
    +-- Antenna ANT2
    +-- ...
```

![Registration hardware/deployment topology](../../../raw/prod/docs/assets/architecture/registration-hardware-topology.svg)

A `RegistrationAsset` represents physical/configured equipment identity. One registration system may have one or more antennas. The antenna count does not define additional `Waypoint` identities or `UniqueID` values.

### Configuration and identity mapping

Configuration connects the software and deployment identities without making them the same object:

```text
Waypoint waypoint-A -> LocationID X
Waypoint waypoint-A -> UniqueID waypoint-A
RegistrationAsset asset-01 -> used by/configured for waypoint-A
```

![Waypoint, hardware and data-source configuration mapping](../../../raw/prod/docs/assets/architecture/waypoint-hardware-mapping.svg)

`UniqueID` is the stable identity of a `Waypoint` and the scope for its sequence, persistence and synchronisation semantics. `LocationID` separately identifies where that waypoint is configured/deployed. `UniqueID` is not derived from `RegistrationAssetId`.

Runtime-wide infrastructure may be shared where that does not leak mutable waypoint state. Candidates include backing executors, logging infrastructure, HTTP server infrastructure, backoffice connection infrastructure, configuration loading and network monitoring.

Stable domain facts behind these views are maintained in `03-domain-baseline.md`; this SAD owns their software-architecture composition and execution implications.

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

The initial architecture uses explicit typed routing because the flow is easier to reason about, test and keep lightweight on the Pi Zero. A third-party messaging/event framework should only be introduced when it solves a demonstrated problem better than explicit routing and JDK concurrency primitives.

## Process view: threading and concurrency

External libraries may create callbacks/threads for HTTP/WebSocket, shell, RFID, CAN, RabbitMQ, timers and network sessions. Those threads must not directly mutate authoritative waypoint-system state.

The intended processing path is:

1. capture externally meaningful `TimingTimestamp` values immediately where timing matters;
2. attach stable instance/device/source context;
3. convert input into an immutable command/event;
4. route it to the addressed `Waypoint`;
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

![SI-01 runtime dispatch process](../../../raw/prod/docs/assets/architecture/runtime-dispatch-process.svg)

The source for this process view is `docs/_diagrams/runtime-dispatch-process.yaml`. Boxes show state/execution ownership and arrows show the principal dispatch, execution and published-snapshot relationships rather than a complete call graph.

### Per-instance serialized state lane

Every `Waypoint` owns one logical serialized state lane implemented by a small project-owned `SerialExecutor` abstraction.

Required semantics:

- messages accepted for one instance execute in FIFO enqueue order;
- at most one state-changing handler for an instance is active at a time;
- the serial executor does **not** own a dedicated operating-system thread;
- each serial executor delegates runnable work to a shared backing `ExecutorService`;
- different waypoint systems may execute concurrently when the backing executor has more than one worker;
- increasing backing parallelism must never allow two state handlers of the same instance to overlap.

The design follows the standard `Executor` composition pattern rather than introducing an actor/reactive framework. The constrained field profile should start with one backing state worker; larger development/integration compositions may configure more workers after measurement. This allows the same logical model to run conservatively on a Pi Zero and with parallel independent instances on a desktop test host.

A direct/synchronous executor remains a supported test composition so handlers can be exercised deterministically without real threads.

### Dispatcher and ingress ownership

A `TimingSystemDispatcher` is the application/runtime routing boundary from externally concurrent producers to per-instance state lanes.

The dispatcher resolves a stable timing-system identity to the applicable serial executor and submits the typed message. It does not implement domain rules itself.

Ingress rules:

- adapter callbacks do the minimum synchronous work needed to capture timestamp/context and validate framing;
- callback threads must not call mutable domain/application state directly;
- device/source ordering guarantees provided by an adapter must be preserved before dispatch;
- the dispatcher does not sort messages by wall-clock timestamp;
- when multiple producer threads concurrently submit to the same instance, the state lane processes the order in which submissions are accepted into that lane;
- source sequence numbers are assigned according to domain/source commit semantics, not inferred from callback thread identity or timestamp ordering.

### Snapshot reads and consistency-sensitive queries

Not every read needs to occupy the serialized state lane.

The application should publish immutable current-state/status snapshots that can be read safely by presentation/status consumers without mutating the instance. A lightweight atomic publication mechanism may be used for the current snapshot.

Queries that require a state-consistent calculation against mutable authoritative state enter the same serialized lane as state-changing work. The API must make the difference between a potentially slightly stale published snapshot and a consistency-sensitive query explicit rather than hiding it behind one generic getter.

### Blocking I/O and asynchronous completion

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

### Queue bounds, overload and failure containment

An unbounded ingress queue is not an acceptable field default on the constrained target.

Working rules:

- each instance state lane has a bounded/configurable pending-work capacity;
- queue saturation must never silently discard a command, observation or completion;
- rejected/overloaded submissions produce explicit diagnostics/status/counters and a visible failure path to the calling adapter/interface;
- an adapter may apply protocol-specific backpressure or its own bounded buffering where the external protocol supports it, but that policy remains outside the generic dispatcher;
- queue depth/high-water information should be observable for diagnostics;
- one handler exception must not permanently stall the serial executor; handler failure is contained/reported and scheduling of subsequent accepted work continues unless the application deliberately transitions the instance to a failed/stopped state.

Exact capacities and the final overload reaction for timing-critical device ingress require workload evidence. They are configuration/verification decisions, not permission to use an unbounded queue meanwhile.

### Lifecycle and shutdown

Normal shutdown should preserve executor ownership explicitly:

1. stop accepting new external/operator ingress;
2. stop or quiesce device/network adapters;
3. allow accepted instance-lane work to drain within a configured timeout;
4. complete required persistence/outbox shutdown handling;
5. shut down scheduler/I/O executors and the shared state executor;
6. expose failure if the bounded graceful-shutdown window cannot complete.

### Concurrency technology baseline

The selected baseline is:

- JDK `java.util.concurrent` (`Executor`, `ExecutorService`, `ThreadPoolExecutor`, `ScheduledExecutorService`, futures where justified);
- a small explicit project-owned `SerialExecutor` abstraction per waypoint system;
- one shared configurable state backing executor;
- separate I/O/scheduler execution where blocking or delayed work requires it;
- no Akka/reactive-stream/event-bus framework in the initial architecture;
- controllable/direct executors in unit tests.

Do not use convenience executor factories that hide unbounded queues where a bounded field queue is required; construct/configure the relevant executor explicitly.

## Time and clock architecture

Time is an explicit architecture concern rather than an incidental use of `Date`, `Calendar`, `LocalDateTime`, Java/SQL timestamp classes or raw millisecond values throughout the codebase.

### `TimingTimestamp` value

SI-01 uses one dedicated immutable application/domain class named `TimingTimestamp` for externally meaningful absolute event times such as observations, registrations, start times and persisted/synchronised event timestamps.

Working semantics:

- `TimingTimestamp` represents an absolute point on a UTC-based time line;
- it does not contain an implicit local time zone or daylight-saving state;
- conversion to/from local civil time happens at explicit presentation/configuration/integration boundaries;
- its precision and external serialisation are explicit rather than inherited accidentally from a Java API or wire codec;
- domain/application APIs pass `TimingTimestamp` rather than arbitrary `long`, `Date`, generic Java timestamp classes or local-date/time values where an absolute event time is intended.

The dedicated class may internally delegate to a suitable Java primitive such as `Instant`, but its public semantic contract remains project-owned. Protocol-specific formatting/parsing, time-only strings and deployment-specific zone conversion belong in boundary adapters/codecs rather than in `TimingTimestamp` itself. This keeps the domain type independent of one protocol, storage format or deployment time zone.

### Time sources

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

UniqueID + SequenceNumber
  stable stream ordering / gap detection
```

A source sequence is not derived from a timestamp. Two registrations may have equal timestamps, and a wall-clock correction may even make a later observation carry an earlier absolute timestamp; source ordering must remain recoverable from source sequence semantics.

### Architecture risk — wall-clock discontinuity and local-time ambiguity

This is an explicit architecture risk because timing software can produce plausible but incorrect results when local civil time and elapsed time are conflated.

| Risk | Possible consequence | Architectural mitigation / open work |
| --- | --- | --- |
| daylight-saving transition repeats or skips local civil times | ambiguous/non-existent local timestamps and wrong ordering if local time is persisted as authority | persist/use absolute `TimingTimestamp`; perform local-zone conversion only at explicit boundaries; add DST transition tests |
| NTP, manual correction or platform synchronisation steps wall clock backwards/forwards | negative/large elapsed differences; a later observation can have an earlier wall-clock timestamp | use monotonic time for durations; source sequence for ordering; expose/inject wall clock; define correction/health policy |
| clock offset/drift differs between SI-01 and external systems | incorrect elapsed/race-time calculations or reconciliation disagreement | define clock synchronisation/offset acceptance requirements and verification before timing accuracy is accepted |
| restart loses monotonic origin | process-local duration marks cannot be compared across restart | never persist monotonic marks as event timestamps; restore from absolute `TimingTimestamp` plus domain/source state |

Daylight-saving time by itself does **not** change UTC/absolute time; the ambiguity appears when a local civil time is treated as if it were an absolute timestamp. Conversely, using an absolute `TimingTimestamp` does not make the operating-system clock monotonic: a wall-clock correction can still cause newly captured absolute timestamps to move backwards.

Before physical timing behaviour is accepted, the project must decide how an active timing system reacts to a material clock correction: whether it is merely diagnosed, blocks/marks the system degraded, records an audit event, or uses an explicit correction/offset mechanism. That policy needs requirements and verification evidence rather than being hidden inside the `TimingTimestamp` class.

## Internal messaging direction

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

## Status and diagnostics architecture

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

## Logging architecture

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
- stable waypoint/data-source/device/correlation identifiers should be represented consistently in diagnostic messages/context, without making logging context the owner of application state;
- logging is not the mechanism for application status, registration history, audit/domain records or backoffice synchronisation state.

The exact field handlers, console/file split, rotation, retention and default level policy remain deployment/runtime configuration choices. They must be measured on the Pi Zero before being treated as accepted field defaults.

SLF4J 2.0.x is compatible with the Java-8 baseline; the implementation repository should pin the API/provider patch version together through Maven dependency management.

## Configuration and composition architecture

Configuration describes deployment/composition rather than domain behaviour hard-coded in source.

Representative structure:

```text
application
  waypoint systems
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
3. prepare-team registry — current teams-to-prepare plus internal traceable history;
4. race/reference data — locally available participant/team/tag-reference input received from external sources;
5. absolute event time — project-owned `TimingTimestamp` semantics independent of local display time;
6. local backup/restore — restart/power-loss recovery;
7. backoffice outbox/synchronisation — pending external delivery/reconciliation.

Registration identity remains waypoint-scoped; the current stable conceptual key is `(UniqueID, SequenceNumber)`.

Persistence durability semantics, file format, atomic-write strategy and corruption/recovery rules remain open decisions and may justify a focused data/persistence SDD only when implementation reaches that complexity.

## Integration architecture

The **external device and network topology is owned by the SSAD**, because RFID/CAN devices, local LAN clients, displays and backoffice are system-level deployment/interface relationships. This SAD starts at the SI-01 boundary and explains how SI-01 realises those system interfaces internally through ports, adapters, callbacks, status handling and transport implementations.

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

Decoding must retain public semantic tag classification (normal/reserve/test) even if proprietary prefix/encryption details stay in a private codec. Reserve resolution and test-tag policy are domain/use-case concerns rather than reasons for the adapter to silently rewrite every decoded tag to one normal identity.

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

## Physical/deployment view

Representative SI-01 deployments are:

```text
Production field host
  Raspberry Pi Zero / Zero W
    one SI-01 process
      one or more configured Waypoint objects
      local devices + local files
      optional network/backoffice connectivity

Development/test host
  Linux or Windows
    same SI-01 framework/application behaviour
    real or stub adapters
    may host larger multi-instance simulation topology
```

The architecture should not require a different domain implementation for simulation. Different compositions select different adapters/topologies around the same application/domain behaviour. The system-level placement of SI-01 relative to devices, operator clients, LAN/Wi-Fi and backoffice is defined in the SSAD rather than duplicated here.

## Testability and failure/recovery architecture

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

## When a separate SDD is justified

A separate SDD should be introduced or retained only when at least one of these is true:

- the topic has enough algorithm/state-machine/configuration detail that it obscures the architecture in this SAD;
- several implementation alternatives need a focused design/review;
- a component has an independently meaningful lifecycle, contract or complexity;
- the detail is needed directly by implementation/reviewers but is not useful to a reader trying to understand SI-01 architecture as a whole.

Examples that may eventually justify focused SDDs include exact persistence/restore mechanics or exact RabbitMQ connection/retry/topology behaviour. Threading, messaging, logging and the main runtime topology remain SAD concerns unless their implementation becomes substantially more complex.

## Detailed-design document disposition

This architecture review deliberately reduced and renumbered the current SDD set. At this project stage SDD numbers are working document identifiers, so removing a document also closes the numbering gap rather than preserving obsolete sequence numbers.

- `31-01-SDD-01-data-and-display-design.md`: **deferred working note**. It is excluded from the architecture book while persistence/data mechanics are still too early for a dedicated active SDD.
- `31-01-SDD-02-java-component-design.md`: **active focused SDD** because artifact/package/composition decisions already affect the implementation repository.
- `31-01-SDD-03-backoffice-transport-design.md`: **deferred working note**. Detailed transport design should mature just in time with backoffice implementation and is excluded from the architecture book for now.

The former timing-system detailed design and runtime-topology/configuration detailed design were retired after their useful architecture was consolidated into this SAD or the domain baseline. Their historical filenames and content remain available through Git history rather than reserving gaps in the current SDD numbering.

No new SDD should be created during this cleanup unless a clear separate detailed-design purpose is demonstrated.

## Open architecture decisions

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

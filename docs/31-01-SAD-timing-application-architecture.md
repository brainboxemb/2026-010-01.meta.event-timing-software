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
- support one or more logical TimingNodes without state leakage;
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
2. accept an operator command through local or network presentation and route it to the correct logical TimingNode;
3. accept a device observation from an external callback without allowing that callback thread to mutate authoritative application state directly;
4. persist accepted operational state and recover it after restart;
5. continue local operation while a GUI/browser or backoffice connection is unavailable;
6. host several TimingNodes in a development/simulation composition without state leakage;
7. substitute public stubs for production devices/transports while exercising the same application/domain paths;
8. capture and process observations correctly when local civil time crosses a daylight-saving transition or the operating-system wall clock is corrected forwards/backwards.

These scenarios are used to check the logical, process, development and deployment views below.

## Logical view

### Layered application architecture

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
        +-- StageStartTimeRegistry
        +-- Journal
        +-- PrepareTeamRegistry
        +-- RaceData
        +-- StageTiming
```

![SI-01 layered architecture](../../../raw/prod/docs/assets/architecture/layered-architecture.svg)

The source for this view is `docs/_diagrams/layered-architecture.yaml`.

### Presentation

Presentation owns client-facing interfaces and mapping:

```text
Console / Remote Shell     development + service
Desktop GUI Interface      debug / development
HTTP / WebSocket           iPad / operator UI
```

It converts external requests to application calls and application results to
client representations. It does not own mutable application/domain state.

### Application

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

### Domain

The domain owns timing rules and TimingNode state:

```text
TimingNode
  TimingNodeId
  LocationID
  TagProcessor
  StageStartTimeRegistry
  Journal
  PrepareTeamRegistry
  RaceData
  StageTiming
```

`TagProcessor` handles tag observations. `StageStartTimeRegistry` owns stage
start references. `Journal` owns registration/history data and sequence
semantics. `PrepareTeamRegistry` owns teams preparing at the TimingNode.
`RaceData` contains participant/team/tag reference data. `StageTiming`
derives running times and ranking.

Detailed domain semantics belong in `03-domain-baseline.md`.

### Core runtime support

Core contains reusable execution mechanics, not business behaviour:

```text
serial execution
lifecycle mechanics
scheduling
asynchronous completion
```

### I/O

I/O contains adapters that move data between SI-01 and the outside world:

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

SI-01 may compose 0..N configured `Antenna` instances and 0..N
`BackofficeConnector` instances. Antenna mappings route observations to 1..N
TimingNodes; connector bindings map inbound/outbound data to/from TimingNodes.
Concrete antennas/connectors own their protocol/device resources internally.

### Platform

Platform contains low-level execution-environment facilities:

```text
clock / time source
filesystem/path primitives
executors / threads
process/runtime information
network / OS primitives
```

### Cross-cutting concerns

Cross-cutting technical concerns include logging, configuration, diagnostics,
metrics and build/version identity. In Java, `infra` is reserved for concrete
cross-cutting support such as `BuildIdentity`; it is not the I/O layer.

## Principal runtime abstractions

A `TimingNode` is the primary independently addressed operational/domain aggregate inside SI-01. One application process may host one or more TimingNodes. `SystemStatus` is application-scoped and aggregates/monitors overall runtime and TimingNode status rather than belonging to one TimingNode.

The architecture deliberately uses **separate views** for software/domain decomposition, hardware/deployment topology and configuration/identity mapping. These views must not be collapsed into one ownership tree.

### Software/domain decomposition

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
        +-- StageStartTimeRegistry
        +-- Journal
        +-- PrepareTeamRegistry
        +-- RaceData
        +-- StageTiming
```

`TimingNodeId` is the stable identity of the `TimingNode` and scopes its registration sequence, persistence and synchronisation semantics. `LocationID` is the separately configured physical event location.

![SI-01 software/domain decomposition](../../../raw/prod/docs/assets/architecture/timing-node-software-decomposition.svg)

The exact Java class/package boundaries may evolve as implementation evidence appears, but the `TimingNode` aggregate is the semantic owner of the operational TimingNode state. The physical registration asset is not a child component of this software tree.

### Antenna topology

The active software/configuration model uses the configured antenna directly:

```text
Antenna (0..N)
```

An `Antenna` is an I/O source with its own `AntennaId` and concrete
driver/connection settings. Reader/protocol/device details stay inside that
concrete antenna implementation/configuration unless later evidence requires a
separate architectural concept.

One antenna may intentionally feed one or more TimingNodes.

### Configuration, routing and identity mapping

Configuration connects identities without collapsing them:

```text
Antenna (0..N)
    +-- each Antenna -> 1..N TimingNodeId

BackofficeConnector (0..N)
    +-- bindings <-> 1..N TimingNodeId
```

![TimingNode, hardware and backoffice routing](../../../raw/prod/docs/assets/architecture/timing-node-routing-mapping.svg)

`TimingNodeId` is the stable identity of a `TimingNode` and scopes its sequence, persistence and synchronisation semantics. `LocationID` and `AntennaId` are separate namespaces.

Configured antenna mappings associate each `AntennaId` with one or more TimingNodes. Fan-out is explicit: if one antenna feeds two TimingNodes, each target TimingNode processes the observation through its own serialized state boundary and keeps its own TimingNodeId-scoped sequence/state while the original `AntennaId` remains available as context.

Configured backoffice bindings map connector-specific inbound/outbound data to TimingNodes. A connector binding may assign an external/backoffice-facing name to a TimingNode without changing its internal `TimingNodeId`. One connector may serve many TimingNodes and one TimingNode may bind to more than one connector.

These mappings belong to the I/O composition/configuration boundary; they do not require a separate router object. Concrete `Antenna` and `BackofficeConnector` implementations own their protocol/device resources internally.

Runtime-wide infrastructure may be shared where that does not leak mutable TimingNode state. Candidates include backing executors, logging infrastructure, HTTP server infrastructure, shared connector infrastructure, configuration loading and network monitoring.

Stable domain facts behind these views are maintained in `03-domain-baseline.md`; this SAD owns their software-architecture composition and execution implications.

## Command, query and event model

All presentation transports should converge on one shared application model. The first Java implementation proves this with a deliberately small `CommandHandler.version()` query rather than a generic messaging framework; future request methods should be added only when a real client use case requires them.

```text
local console -------+
remote shell --------+
HTTP/JSON -----------+--> typed command/query boundary --> application runtime
WebSocket <-----------+<---------------------------------------------+
```

Working rules:

- commands request state changes;
- queries read current state/snapshots without becoming alternate owners of state;
- events report facts/results that have occurred;
- external protocol DTOs are mapped at the presentation/I/O boundary rather than used as the internal domain model;
- messages crossing thread/process boundaries should be immutable where practical;
- a generic event-bus framework is **not** assumed to be necessary.

The initial architecture uses explicit typed routing because the flow is easier to reason about, test and keep lightweight on the Pi Zero. A third-party messaging/event framework should only be introduced when it solves a demonstrated problem better than explicit routing and JDK concurrency primitives.

## Process view: threading and concurrency

The domain model is intentionally kept simple. Code working on one `TimingNode`
should be able to behave as if it is single-threaded.

That guarantee is provided by the application around the domain code. Domain
objects are not expected to add locks everywhere to protect themselves from
normal application callbacks.

### The rule for one TimingNode

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

### Where input enters

External libraries may call SI-01 from their own threads. Examples are HTTP,
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

![SI-01 runtime dispatch process](../../../raw/prod/docs/assets/architecture/runtime-dispatch-process.svg)

The source for this process view is
`docs/_diagrams/runtime-dispatch-process.yaml`.

### Reads

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

### Blocking I/O

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

### Queue and failure behaviour

The queue in front of a TimingNode must be bounded in field use.

- accepted tasks are processed in submission order;
- a full queue is an explicit failure, never a silent drop;
- one task throwing an exception must not permanently stop later accepted work;
- queue depth/high-water information should be observable for diagnostics;
- exact queue sizes remain a configuration/verification decision.

### Shutdown

Normal shutdown follows the same ownership rules:

1. stop accepting new client/device input;
2. stop or quiesce adapters;
3. allow already accepted TimingNode work to finish within a configured timeout;
4. finish required persistence/outbox work;
5. stop scheduler/I/O/state executors;
6. report failure if graceful shutdown cannot finish in time.

### Architecture review cases

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

### Concurrency technology baseline

The selected baseline is deliberately small:

- JDK `java.util.concurrent`;
- one small project-owned serial-executor implementation per TimingNode;
- one shared configurable backing `ExecutorService`;
- separate I/O/scheduler execution when needed;
- direct/controllable executors in unit tests;
- no actor, reactive-stream or generic event-bus framework unless a later
  measured need justifies one.

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

TimingNodeId + SequenceNumber
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
  request a consistency-sensitive result from authoritative TimingNode state
```

The exact Java interface/generic signatures remain implementation detail, but the semantic distinction should stay visible.

Rules:

- use typed messages when work crosses an asynchronous or TimingNode execution boundary;
- resolve the target explicitly; do not use a generic event bus or topic discovery;
- once running in a TimingNode's serial executor, use normal direct Java calls;
- submit asynchronous I/O completion back to the owning TimingNode before changing its state;
- RabbitMQ is external I/O, not an in-process message bus.

Choose concrete command/query return types when the first real consumers need them.

## Status and diagnostics architecture

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
- stable TimingNode/data-source/device/correlation identifiers should be represented consistently in diagnostic messages/context, without making logging context the owner of application state;
- logging is not the mechanism for application status, registration history, audit/domain records or backoffice synchronisation state.

The exact field handlers, console/file split, rotation, retention and default level policy remain deployment/runtime configuration choices. They must be measured on the Pi Zero before being treated as accepted field defaults.

SLF4J 2.0.x is compatible with the Java-8 baseline; the implementation repository should pin the API/provider patch version together through Maven dependency management.

## Configuration and composition architecture

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

Build provenance remains separate from deployment configuration. `BuildIdentity` describes the built artifact; it is not loaded from IF-11 deployment settings.

Working rules:

- keep secrets/credentials out of committed configuration and store only secret references there;
- prefer explicit/manual composition initially rather than adding a dependency-injection framework without a demonstrated need;
- keep overlay rules deliberately limited rather than creating general inheritance/includes;
- keep the concrete file syntax/library open until the first Step-3 implementation selects it;
- create Java configuration types only as real executable slices need them rather than mirroring the entire conceptual tree in advance.

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

Registration identity remains TimingNode-scoped; the current stable conceptual key is `(TimingNodeId, SequenceNumber)`.

Persistence durability semantics, file format, atomic-write strategy and corruption/recovery rules remain open decisions and may justify a focused data/persistence SDD only when implementation reaches that complexity.

## Integration architecture

The **external device and network topology is owned by the SSAD**, because RFID/CAN devices, local LAN clients, displays and backoffice are system-level deployment/interface relationships. This SAD starts at the SI-01 boundary and explains how SI-01 realises those system interfaces internally through ports, adapters, callbacks, status handling and transport implementations.

### Backoffice

RabbitMQ is not the application-level backoffice API. SI-01 depends on semantic source-aware ports, explicit TimingNode routing/bindings and local synchronisation/outbox behaviour. A process may compose 0..N backoffice connectors; RabbitMQ is one connector type.

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
io
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
| Concurrency | one project-owned `SerialExecutor` per `TimingNode` over shared configurable JDK executors; constrained profile starts with one state worker | architecture baseline selected; verify queue capacities, overload behaviour and worker-count evidence |
| Internal messaging | typed immutable command/event/query objects only at async/ownership boundaries + explicit TimingNode mapping/routing at the owning boundary; no central generic dispatcher; direct calls inside a TimingNode task | architecture baseline selected; refine first consumer API signatures during implementation |
| Time model | dedicated project-owned immutable `TimingTimestamp` + injectable absolute clock + separate monotonic duration source | working direction; define precision/serialisation, sync and clock-correction policy |
| Dependency injection | explicit/manual composition initially | working direction; add framework only if complexity justifies it |
| Logging | SLF4J API in reusable framework; initial executable provider `slf4j-jdk14` / `java.util.logging` | architecture baseline selected; pin compatible 2.0.x API/provider and measure field logging on Pi Zero |
| Configuration | IF-11 effective `ApplicationConfig`: base + platform + optional profile + secret resolution | file syntax/library and first Java type set still open |
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
      one or more configured TimingNode objects
      local devices + local files
      optional network/backoffice connectivity

Development/test host
  Linux or Windows
    same SI-01 framework/application behaviour
    real or stub adapters
    may host larger multi-TimingNode simulation topology
```

The architecture should not require a different domain implementation for simulation. Different compositions select different adapters/topologies around the same application/domain behaviour. The system-level placement of SI-01 relative to devices, operator clients, LAN/Wi-Fi and backoffice is defined in the SSAD rather than duplicated here.

## Testability and failure/recovery architecture

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

Fault handling should preserve local authority, traceability and explicit status. Exact retry counts, timeouts and durability guarantees belong to requirements or focused implementation design when evidence exists.

Detailed verification strategy belongs in `50-SVP-software-verification-plan.md`.

## Detailed-design documents

Keep this SAD as the main SI-01 technical design. Use a separate SDD only when
implementation detail would make the SAD harder to read.

Current active focused SDD:

```text
31-01-SDD-02-java-component-design.md
  Java packages, Maven artifacts and composition
```

Persistence/data and backoffice transport notes remain deferred until their
implementation needs focused design.

## Open architecture decisions

The next useful architecture work is to resolve concrete implementation choices, not create more document layers:

- TimingNode queue capacities, overload policy per ingress class and backing-worker count based on Pi-Zero/integration-test measurements;
- field logging handlers, level defaults, rotation/retention and Pi-Zero resource evidence;
- embedded HTTP/WebSocket technology compatible with Java 8 and Pi Zero constraints;
- remote-shell technology;
- first concrete command/query submission/result API signatures;
- `TimingTimestamp` representation/precision/serialisation and equality/comparison semantics;
- wall-clock synchronisation, correction detection and the operational policy for a material forward/backward clock step;
- concrete configuration file syntax/library and first Java configuration type boundaries;
- persistence commit/durability/atomic-write/recovery policy;
- reference ARMv6 Java 8 runtime/vendor/version;
- status/health vocabulary and publication model;
- exact public API/SPI boundaries as real consumers appear;
- RabbitMQ connection/channel/retry strategy when that integration becomes active;
- evidence threshold and timing for a later Java 11 migration.

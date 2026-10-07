# Java component, package and artifact detailed design

Status: working draft / focused detailed design

Software item: **SI-01 — Timing Point Application**

## Purpose

This SDD describes the **Java implementation** of the SI-01 design: Maven
modules, packages, classes/interfaces, composition, queues/threads and provider
loading.

## Terms and abbreviations

- **SDD** — Software Design Description
- **SSD** — Software Specification Document
- **SI** — Software Item
- **JAR** — Java archive
- **Maven** — Java build and dependency tool


## Relationship to other documents

This SDD refines the SI-01 SSD and SDD-01 into concrete Java structure. Applicable
ISDs/IDDs remain the external contract; this document selects Java mechanisms that
realise those decisions. The Java implementation and component tests are downstream.

`44-01-GPD-java-design-rules.md` collects recurring non-normative Java implementation
and review checks derived from this design. It supports code review but does not override
this SDD or introduce product behaviour.

The SSD says what the architecture must do. SDD-01 describes the LogBook/data
flow. IDDs such as IF-05 define external/file contracts. This document picks the
Java mechanisms that implement those decisions.

## Why this SDD exists

This detail is separate because module/package choices directly affect the Java
repository, dependencies and what can be reused by other applications.

The central rule is:

> **An architecture layer or Java package is not automatically a Maven artifact.**

Keep these concepts distinct:

1. **Architecture responsibility** — semantic ownership and dependency direction, defined by the SSD architecture.
2. **Java package** — cohesive source organisation and enforceable dependency discipline.
3. **Maven artifact** — reusable library or deployable application with a concrete consumer/lifecycle reason to exist.
4. **Application composition** — assembly of application-core code and selected implementations into an executable.
5. **Contract/port** — semantic boundary placed with the responsibility that owns its meaning.

A separate artifact is justified only by a real consumer, reuse, dependency, lifecycle, deployment, ownership, public/private, release or versioning boundary.

## Maven reactor

The current reactor has two reusable artifacts plus one executable application.
The shared TimingData library artifact is justified by the independent SI-01 and
Development Client consumers. It intentionally remains one artifact containing the
semantic contracts, default/reference profile, codec and factory/provider; these
responsibilities are not split into separate API/default JARs:

```text
reactor/
├── pom.xml                    timing-point-parent
├── shared/
│   └── timing-data/
│       └── pom.xml            event-timing-data.jar
├── core/
│   └── pom.xml                timing-point-core.jar
└── app/
    └── pom.xml                timing-point-app.jar
```

Working coordinates:

```text
groupId: io.github.brainboxemb.eventtiming

parent:          timing-point-parent
TimingData:      event-timing-data
core:            timing-point-core
executable:      timing-point-app
```

The root POM only groups/configures the build; it is not a runtime component.

The `core/` Maven module is the reusable **application core of SI-01**. It contains
the main application, domain, presentation, I/O, infrastructure, runtime and
Platform implementation that is shared by executable compositions. The name
`core` is an artifact/source boundary only: it does **not** reintroduce a
separate Core architecture layer in Figure SI01-01. The executable `app/`
module stays deliberately thin and adds the launcher, concrete runtime-provider
selection and packaging needed to run that core.

The Maven `groupId` remains the **event-timing software-system/product-family** coordinate. SI-01 Java code is more specific: the reusable application core and default executable live under `io.github.brainboxemb.eventtiming.timingpoint`. `TimingPoint` names the local software/deployment role; it does **not** replace the internal `TimingNode` domain aggregate. One Timing Point Application process may host 1..N TimingSystems and therefore multiple TimingNodes.

## Package direction

The current Java structure should grow from real code, not from the architecture
diagram.

Likely top-level packages are:

```text
io.github.brainboxemb.eventtiming/timingpoint/
  application/
  domain/
  platform/
    execution/
    events/
    environment/
  presentation/
    interfaces/
      api/
      console/
      shell/
      web/
    common/
      terminal/
  io/
    devices/
      antenna/
      display/
      keypad/
      beeper/
    devicenetworks/
      can/
      network/
    messaging/
    storage/
  infra/
    configuration/
    logging/
    loggingserver/
  runtime/
    config/
```

Presentation subpackages are organised by **functional interface first**. Console, Remote Shell, Web and API are separate presentation interfaces. The intended Web topology is one configured Web endpoint/binding per TimingNode (1..N), each with its own presentation port and a `TimingNodeId` reference. HTTP/WebSocket are implementation transports inside a functional interface, not global presentation categories. The primary API classes stay directly at `presentation.interfaces.api` while that component is small; a one-class `http`, `websocket` or `messages` package would hide the component overview without adding a useful boundary. `presentation.common.terminal` contains only terminal handling genuinely shared by Console and Remote Shell; `presentation.common` is not a generic dumping ground.

These are source-organisation boundaries, not automatically Maven modules.

Use these rules:

- create a class only when current behaviour needs it;
- keep small enums with the object that owns them until reuse justifies a
  separate type;
- do not create marker classes to represent layers;
- place a type by what it means, not by which layer happens to call it;
- keep primary component/capability classes visible at that component package
  root so opening the package gives a useful architecture overview;
- do not introduce a subpackage merely to classify one class by transport,
  message shape or implementation role;
- use a deeper subpackage for a cohesive supporting family when it materially
  improves navigation, or when multiple real sub-capabilities need their own
  namespace;
- preserve Java encapsulation when choosing package boundaries: subpackages do
  not share package-private access, so do not split implementation helpers only
  to make a tree look tidy if that would force a wider API;
- use capability-oriented subpackages when a domain concept has a main object plus
  closely related value/supporting types; keep that small group together rather
  than introducing generic `helper`, `model` or single-type `identity`
  subpackages;
- reserve `platform` for small JDK-only reusable primitives and execution-environment abstractions, including bounded/serial execution and typed local events;
- reserve `infra` for concrete cross-cutting technical support such as `BuildIdentity`, logging, diagnostics and configuration/extension adapters;
- reserve `runtime` for concrete application composition, the running application container and lifecycle;
- use `io` for external hardware, messaging and storage adapters.

The shared EventData artifact has its own package root:

```text
shared/event-data/
  io.github.brainboxemb.eventtiming.eventdata/
    EventData.java
    TagId.java
    EventDataProvider.java
    defaultprofile/
      DefaultEventData.java
      DefaultEventDataProvider.java
```

The common EventData API is intentionally independent of SI-01 runtime classes
and JavaFX so both the Timing Point Application and engineering tools can consume
the same event-profile semantics. Event-specific provider JARs may supply
alternative EventData profiles through the normal typed extension mechanism.
Runtime discovery treats `EventDataProvider` as a typed provider family parallel
to `TimingDataProvider`; neither provider API depends on the other. `RaceData`
remains a separate TimingNode-local mutable/runtime data source and is not part
of the shared EventData artifact.

The shared TimingData artifact has its own package root:

```text
shared/timing-data/
  io.github.brainboxemb.eventtiming.timingdata/
    TimingData.java
      AutomaticRegistration
      ManualRegistration
      ManualTimeSource
      RecordKey
    LocationId.java
    RegistrationId.java
    TimingTimestamp.java
    TimingDataFactory.java
      Context
    TimingDataCodec.java
      CodecException
    TimingDataProvider.java
    defaultprofile/
      DefaultTimingDataFactory.java
      DefaultTimingDataCodec.java
      private automatic/manual default value implementations
```

`TimingDataFactory.Context` is the one immutable value-only construction context for
fields shared by every TimingData variant. Do not mirror the semantic type tree
with `AutomaticRegistrationContext`, `ManualRegistrationContext` or nested
per-variant context types.

The TimingNode implementation is grouped as:

```text
application/
  ApplicationId.java
  UpstreamMessageRouter.java       when upstream messaging is implemented
  ConfigurationControl.java        configuration query/update use-cases
  Conductor.java                   SI-01 cross-component rules
  logic/
    AbstractConductor.java          generic Conductor lifecycle template
    ComponentLifecycleManager.java ordered activation/rollback helper
  property/
    TimingNodeStateProperty.java

infra/
  property/
    TrackedProperty.java            generic tracked-value scheduling/change detection
  extension/
    ExtensionRegistry.java          typed provider discovery/selection
  configuration/
    ReadOnlyConfiguration.java     startup/current value + change observation
    DynamicConfiguration.java      validated runtime override/clear primitive
    ConfigurationChange.java       immutable typed change notification
    ConfigurationUpdateResult.java APPLIED/NO_CHANGE/INVALID/RESTART_REQUIRED

runtime/
  configuration/
    ApplicationConfiguration.java  concrete running configuration tree
    TimingNodeConfiguration.java   node-local runtime configuration branch

domain/
  system/
    TimingSystem.java                   parent aggregate for 1..N TimingNodes
    TimingSystemId.java                 internal composition/simulation identity
    SystemStatus.java                   complete current TimingSystem overview
    UpstreamMessagePort.java            system-level upstream messages
  timing/
    TimingNode.java
    TimingNodeId.java
    UpstreamMessagePort.java          TimingNode-level upstream messages
    NextUpTeams.java                  passive per-node state
    NextUpTeamsStore.java             persistence port for next-up analysis history
    StageStartTimes.java              passive per-node reference state
    StageStartTimesStore.java         persistence port for start-time analysis history
    TagProcessor.java                 node-local registration-passage processing
    TagProcessingPolicy.java          compiled defaults + active tag-processing policy
  logbook/
    LogBook.java                        passive committed TimingData history
  timingdata/
    TimingDataPersistence.java          TimingData-specific persistence contract
    DefaultTimingDataPersistence.java   TimingData codec/identity/sequence mapping
  upstream/
    UpstreamProtocol.java               TimingData + sync/ping semantics
    UpstreamProtocolProvider.java       typed extension provider contract

io/
  devices/
    antenna/
      AntennaId.java                    configured software identity of one antenna
      AntennaInfo.java                  self-test identity/version result
      TagObservation.java               EventData TagId + RSSI + TimingTimestamp fact
      model/
        Antenna.java                    device/provider lifecycle + observation contract
        SimulatedAntenna.java           built-in reference/simulation implementation
      manager/
        AntennaManager.java             lifecycle/status + control state machine
        AntennaSet.java                 composition-time antenna set + multiplex configuration
        ManagedAntenna.java             direct one-antenna operations + runtime status
        AntennaManagerTypes.java        manager/status value types
        task/
          SelfTestTask.java             complete startup self-test round
          InventoryTask.java            enable/disable/multiplex inventory state machine
          AntennaShutdownTask.java      cooperative device shutdown
          AntennaTaskResult.java        task completion success/failure value
    power/
      PowerDevice.java                  external power-device contract
      SimulatedPowerDevice.java         deterministic simulated power device
    display/
      DisplayProtocolProvider.java      typed protocol-extension provider contract
      Rev1CanDisplay.java               passive CAN display support when implemented
    keypad/                        only when device-specific code justifies it
    beeper/                         transport-specific implementation only when justified

  devicenetworks/
    can/
      CanNetworkController.java    CAN lifecycle, discovery and device state
      CanProtocolProvider.java     typed protocol-extension provider contract
    network/
      NetworkDeviceService.java    bidirectional network-device boundary

  messaging/
    UpstreamGateway.java            when upstream messaging is implemented
    Connector.java                 only if multiple transports justify a shared contract
    rabbitmq/
      RabbitMqConnector.java
      DebugConnector.java                 engineering/debug connector when implemented
  storage/
    AppendOnlyRecordStore.java             generic opaque-record storage contract
    FileAppendOnlyRecordStore.java         LF framing • file append/recovery
    # generic lower-layer storage mechanisms only as real needs appear

platform/
  execution/
    SerialExecutor.java                    bounded serial lane + lifecycle
    SerialExecutorMetrics.java             lane-local queue/execution measurements
    SerialScheduledExecutor.java           serial lane + delayed/fixed-delay scheduling
    SerialScheduledExecutorMetrics.java    scheduled-lane measurements
    CooperativeTaskRunner.java             cooperative task-runner contract
    SerialTaskRunner.java                  cooperative turns on SerialExecutor
    ScheduledTaskRunner.java               cooperative turns + delayed/result handling
    CooperativeTaskController.java         wake/coalescing for component state machines
    AbstractTask.java                      reusable child-task execution lifecycle
    CooperativeTask.java                   one-step state-machine task contract
    TaskStep.java                          AGAIN / AFTER / DONE continuation decision
  events/
    Event.java                            owner-side typed emit primitive
    EventSource.java                      subscription-only consumer view
  environment/
    PlatformEnvironment.java              raw wall-clock + monotonic-clock + OS boundary
    MonotonicClock.java                   elapsed-time source
    SystemMonotonicClock.java             JVM monotonic implementation
  time/
    TimeSource.java                       shared absolute Instant source contract
    ClockTimeSource.java                  wall-clock-backed baseline implementation
  metrics/
    RuntimeObservation.java               explicit on-demand JVM/GC/thread observation
```

The names above record ownership/direction, not a requirement to create empty
types early. Lower layers expose generic contracts that do not import higher
layers. TimingData-specific persistence semantics stay in Domain and use the
generic `io.storage.AppendOnlyRecordStore`; the file implementation remains
completely unaware of TimingData, TimingNode and Domain types.
The SI-01 SSD defines the execution topology and ownership rules: component-local
logical serial lanes, one shared physical worker per functional role by default, separate
Application/I/O execution boundaries, and measurement-driven physical parallelism.

The Java realization uses `SerialExecutor` for the TimingNode lane. Each TimingNode
receives a distinct instance with its own bounded `ArrayBlockingQueue`, admission state
and lane-local metrics. All instances use the Runtime-owned single-worker
`ThreadPoolExecutor` for the TimingNode role.

`SerialScheduledExecutor` realizes the TagProcessor scheduled serial lane. Each
TagProcessor receives a distinct logical lane, while all such lanes use the Runtime-owned
single-worker `ScheduledThreadPoolExecutor` for the TagProcessor role. Scheduled
housekeeping and immediate work therefore preserve node-local ordering without creating a
thread per processor.

Runtime also creates the Conductor `SerialExecutor` over the application worker and the
AntennaManager `SerialScheduledExecutor` over the shared scheduled I/O worker.

The lane classes receive their backing JDK executor as an external dependency; they never
create, configure or shut down the physical worker themselves. Closing a logical lane
therefore never shuts down a shared worker. Runtime retains physical-worker lifecycle
ownership.

The current Java baseline uses one physical worker for each of these Runtime roles:

```text
TimingNode     -> ThreadPoolExecutor(1)
TagProcessor   -> ScheduledThreadPoolExecutor(1)
Conductor      -> ThreadPoolExecutor(1)
shared I/O     -> ScheduledThreadPoolExecutor(1)
```

This worker count realizes the SSD baseline for both Raspberry Pi Zero and Raspberry Pi 3
Model B deployments. It is not derived from available CPU-core count. V01 measurement
evidence is required before increasing a role's physical worker count.

All Runtime-owned workers use the normal JVM priority. Tests that need asynchronous
execution create and own their test worker separately, while deterministic package-local
seams may use direct execution.

These project types exist to realize the SSD execution model; they are not justification
for reimplementing JDK executor internals.

### Cooperative task execution

:::{design} Cooperative execution and application coordination
:id: DD-CooperativeExecution

Detailed Java design for cooperative task runners/controllers and the
Application-layer coordination pattern used by Conductor.
:::


Some component operations consist of several ordered steps. Some of those steps only
need to yield the owning serial lane; others must also wait for elapsed time. Running the
complete operation in one executor callback would either monopolise the lane or require
blocking sleeps. Spreading the same control flow over ad-hoc callbacks or
`CompletableFuture` chains would instead make the component's state machine implicit and
duplicate wake/coalescing, cancellation and failure mechanics.

The Java design therefore uses a small **cooperative task** model on top of the existing
serial lanes. The component/task remains the owner of its state machine. Platform execution
code owns only admission and continuation:

```text
                    CooperativeTask
                          |
                          | runStep()
                          v
                       TaskStep
                    /      |      \
                 AGAIN   AFTER(t)  DONE
                   |        |        |
                   |        |        +--> run complete
                   |        |
                   |        +--> scheduled continuation
                   |
                   +--> re-admit at back of serial lane
```

A cooperative task is a small state machine. One call executes one logical step and returns
a `TaskStep` describing what should happen next:

```java
interface CooperativeTask {
    TaskStep runStep();
}

TaskStep.again();
TaskStep.after(Duration delay);
TaskStep.done();
```

`AGAIN` is a deliberate yield point. It does **not** call the task recursively and does
not execute the next state in the same callback. The runner re-admits the task at the back
of the same bounded serial queue so already admitted work gets an opportunity to run first.

`AFTER(delay)` additionally needs scheduled execution. It releases the physical worker and
represents the wait only as a timer registration before the next task step is admitted.
Multi-step tasks must therefore not use `Thread.sleep()` to model stabilization, retry
waits or other deliberate delays.

Two runner forms realize the same task contract:

```text
SerialExecutor
    |
    +-- SerialTaskRunner
            AGAIN / DONE

SerialScheduledExecutor
    |
    +-- ScheduledTaskRunner
            AGAIN / AFTER(delay) / DONE
```

A component must not receive a scheduled lane merely because it uses the cooperative task
model. If the state machine only needs short serial turns, `SerialTaskRunner` uses the
component's existing `SerialExecutor`. `ScheduledTaskRunner` is reserved for operations
that actually need delayed continuation or its bounded result/timeout support.

For long-lived component control state machines, external events and child-task completion
signals are treated as **wake-ups**, not as places to execute transition logic.
`CooperativeTaskController` owns only the generic scheduling facts:

```text
event/request/completion
        |
        v
      wake()
        |
        +-- no run active ----> start one cooperative run
        |
        +-- run active -------> remember one pending wake

run completes
        |
        +-- wake pending -----> start one fresh current-state run
        |
        +-- otherwise --------> idle
```

Any number of wake-ups while one run is active therefore coalesce into one later pass. The
component's `runStep()` reads current authoritative state again; it does not replay stale
event payloads. Scheduling state such as "run active" and "wake pending" is kept out of the
component's application/device state.

The responsibilities are deliberately separated:

```text
CooperativeTask
  component/operation-specific state machine
  application/domain/device decisions
  no executor ownership

TaskStep
  next execution decision only:
  AGAIN / AFTER(delay) / DONE

CooperativeTaskController
  wake/coalescing lifecycle for a long-lived state machine
  no application/domain/device decisions

SerialTaskRunner
  cooperative turns on an existing SerialExecutor
  no elapsed-time scheduling

ScheduledTaskRunner
  cooperative turns on an existing SerialScheduledExecutor
  delayed continuation
  bounded result waiting/cancellation/failure mapping

SerialExecutor / SerialScheduledExecutor
  bounded ordered logical lane
  queue/admission mechanics

Runtime
  physical worker creation, role assignment and lifecycle
```

A single task step should be short and bounded where the underlying API permits that. A
blocking provider call may still occupy the worker for the duration of that call; the
cooperative model does not pretend that a synchronous provider API is asynchronous. If a
provider exposes explicit start/poll or start/completion semantics, those belong in
separate task states so the lane can be released between them.

The first concrete consumer is antenna control. `AntennaManager` is itself a cooperative
control state machine. Startup self-test and inventory work are child tasks. External
inventory requests and child-task completions only wake the manager; manager
`runStep()` decides the next transition from current state. The generic controller owns
wake coalescing rather than `AntennaManager` maintaining local
`stateMachineRunning/stateMachineWakePending` flags.

`InventoryTask` drives the requested inventory state to the applied device state and owns
power preparation, direct-antenna start/stop and multiplex rotation. A representative enable path is:

```text
InventoryTask
  POWER_ON
      |
      +-- AFTER(powerStabilization)
      v
  INITIALIZE
      |
      +-- AGAIN
      v
  START_DIRECT / START_GROUP
      |
      +-- AFTER(inventoryInterval) when multiplexing
      v
  SWITCH / DONE
```

`Conductor` uses cooperative task execution for Application-layer coordination, but does
**not** currently define its own state-machine phases. It remains on its normal Application
`SerialExecutor` and runs through `SerialTaskRunner`. TimingNode property-change events
only wake the Conductor control task. `Conductor.runStep()` reads the latest authoritative
`TimingNodeTypes.State` and applies the corresponding cross-component rule.

Conductor does not keep a second copy of TimingNode state or a separate
"last handled state" marker. `TimingNodeStateProperty` remains the sole holder of the
tracked TimingNode state. Conductor maps the current value to idempotent desired inventory
state on `AntennaManager`.

AntennaManager reuses its existing `Setting<Boolean>` for that desired/applied inventory
state. State-driven updates use an idempotent setting update so a coalesced duplicate wake
does not become an implicit retry. Explicit repeated inventory requests remain a separate
retry mechanism and deliberately advance the Setting request revision.

If future application coordination needs several ordered phases or waits, Conductor may
then introduce its own explicit `Phase`/state-machine. Until that need exists, calling the
current Conductor itself a state machine would be misleading.

The cooperative model is deliberately optional. A component that only needs one short
ordered action continues to submit that action directly to its serial lane. TimingNode and
TagProcessor are not wrapped in a cooperative state-machine abstraction merely for
uniformity. Introduce the model when it makes ownership, sequencing or elapsed-time waits
clearer.

A concrete antenna/provider implementation may itself use the same cooperative-task pattern
when its protocol requires multiple commands, waits, retries or readiness checks. That
device state machine remains inside the antenna implementation rather than being copied into
`AntennaManager`. A device-specific logical lane may be backed by the same Runtime-owned
shared I/O worker when ordering/isolation requires a separate lane without another physical
thread. Parent/manager code must observe such child work asynchronously; it must never block
a shared worker waiting for work that still needs that worker (or the same serial lane) to
run.

This cooperative model is an implementation technique for the SSD requirement to use
component-local ordered execution with a small, measurement-driven number of physical
workers. It does not change component ownership or add parallel execution within one serial
lane.

### EventData and TagProcessor realization

:::{design} EventData and TagProcessor realization
:id: DD-EventTagProcessing

Detailed Java realization of EventData-backed tag resolution, TagProcessor
filtering/passage state and the boundary into TimingNode registration work.
:::


The Java design consumes the shared `event-data` capability beside the shared
TimingData capability. `EventData` owns the stable event-profile TagId-to-RegistrationId relationship;
the top-level `TimingApplicationRuntime.create(...)` API does not accept a loose
tag-to-registration mapper dependency.

The provider/antenna implementation may decode or decrypt proprietary source
bytes, but after that boundary generic code uses the shared `eventdata.TagId`.
`TagObservation` therefore carries TagId, RSSI and TimingTimestamp.

TagProcessor resolves each observation through EventData and keeps its
`TagObservationFilter` keyed by RegistrationId. The existing registration-keyed
filtering model is retained rather than creating independent per-tag filters.

The burst/passsage state is extended with per-TagId statistics and the selected
observation identity. A package-level immutable diagnostic snapshot exposes this
state read-only for Presentation/engineering use. The snapshot is diagnostic;
it is not persisted as TimingData and cannot mutate TagProcessor state.

The duplicate filter remains keyed by RegistrationId. Once TimingNode accepts a
registration, every TagId resolving to that RegistrationId is suppressed by the
same duplicate window.

RaceData remains a separate TimingNode-local runtime source. It may receive
upstream updates such as reserve-tag mappings during the event. Resolution code
may therefore combine the selected EventData profile with RaceData overrides,
but EventData remains the owner of stable event-profile semantics and RaceData
remains the owner of live per-node state.

`TimingNode` remains the visible Domain component boundary used by higher layers. It owns
serialized access through the injected `SerialExecutor`, operation admission/timeout
mapping and post-commit event publication. It also creates and owns its node-local
`TagProcessor` child from injected EventData/configuration and the Runtime-supplied
`SerialScheduledExecutor`. Package-private `TimingNodeLogic` contains the mutable node
state and domain decisions: lifecycle, current `LocationId`, LogBook interaction and
TimingData commit behaviour. `TimingNodeLogic` is an implementation detail of the
TimingNode component, not a second architecture component.

A production `TimingNode` is always constructed as a complete capability.
`TimingDataPersistence`, `TimingDataFactory`, the injected absolute-time supplier,
EventData/tag-processing configuration and both execution lanes are constructor dependencies; there is no
lifecycle-only or partially configured production node. The only non-public construction
seam exists for deterministic TimingNode execution-boundary tests and is documented as
test-only in code.

`TimingNodeTypes` is only a Java source-code grouping for the public TimingNode status/result/exception value types. It has no runtime state, lifecycle or architectural responsibility and therefore does not appear as another component in Figure SI01-01.

:::{design} Presentation-facing application access
:id: DD-PresentationAccess

Detailed Application-layer design for PresentationGateway and its node-scoped
TimingNodeProxy boundary. Presentation transports remain outside this boundary.
:::

The application `PresentationGateway` is always composed with a complete
`TimingNode`; there is no status-only or partially configured production
gateway. Presentation tests use complete test fixtures rather than adding a
second production construction mode.

`PresentationGateway` is an Application-layer component named for the adjacent
Presentation side whose traffic it mediates. Gateway names describe the side of
the architectural boundary, not the owning package/layer. `UpstreamGateway`
follows the same naming principle on the I/O/upstream boundary, but owns external
transport/integration rather than presentation-facing application operations.

Node-scoped presentation access is exposed through `TimingNodeProxy`.
`PresentationGateway` owns application-wide presentation information such as
build identity and capabilities; a proxy gives an adapter explicit TimingNode
context for node status, commands, queries and events. The architectural composition
contains **one TimingNodeProxy per composed TimingNode (1..N)**. The default executable currently has one because the executable still composes one TimingNode. A proxy is
an Application-layer boundary object, not a second owner of TimingNode state.

Status-change detection remains owned by the TimingNode serial boundary. A
state-changing command compares authoritative status before and after the domain
operation on that TimingNode lane. A real difference emits the TimingNode status
event before the result leaves ordered command execution. `TimingNodeProxy` maps
that fact to the node-scoped Application-layer `TimingNodeStatus`; it does not perform a second before/after query
outside the ordered boundary.

The visible Domain component boundary uses typed commands and queries rather than
mirroring every `TimingNodeLogic` method:

```java
TimingNodeTypes.OpenResult opened =
        node.invoke(TimingNodeCommands.open(locationId));

TimingNodeTypes.CommandAdmission admitted =
        node.offer(
                TimingNodeCommands.addAutomaticRegistration(
                        registrationId,
                        time));

TimingNodeTypes.Status status =
        node.query(TimingNodeQueries.status());
```

Presentation adapters use the node-scoped Application boundary:

```java
TimingNodeProxy node = presentationGateway.timingNode();

node.open(locationId);
node.applyAutomaticRegistration(
        AutomaticRegistrationAction.ADD,
        registrationId,
        time);
node.statusChangedEvent().subscribe(statusListener);
node.timingDataCommittedEvent().subscribe(timingDataListener);
```

`invoke(command)` is the result-bearing path: presentation/application callers may
wait for the processed domain result. `offer(command)` is the producer path: it
returns only immediate bounded-queue admission and deliberately does not wait for
the later domain result. RFID/TagProcessor-style ingress uses this form so a device
callback cannot be held up by persistence, LogBook work or another queued TimingNode
operation.

`query(query)` is the consistency-sensitive read path. Short reads run in the same
ordering as commands. The ordering boundary is the required property; a copied
LogBook snapshot is not. Query implementations should avoid routine list copies
when direct bounded traversal on the node lane is cheaper, and may introduce
compact derived/indexed state only when measurement justifies it. Typed
command/query objects are local operation descriptions, not another component,
central dispatcher or generic message bus.

The presentation-facing automatic-registration boundary is
`applyAutomaticRegistration(action, registrationId, time)`. The action is explicit
because an automatic-registration record can express more than one semantic
action; the current implemented action set contains only `ADD` until REV semantics
are defined. The Domain command for that implemented action is
`addAutomaticRegistration(...)`. The short IF-03 engineering resource name
`auto-reg` remains a transport concern.

`ApplicationId`, internal `TimingSystemId` and functional
`TimingNodeId` are separate Java identities. `TimingSystemId` distinguishes
multiple hosted/simulated systems locally; it is not automatically serialized
into TimingData or exposed as an upstream address.

:::{design} Timing-time composition
:id: DD-TimingTimeComposition

Detailed composition of raw platform time and the shared semantic TimeSource
used by Domain and I/O timestamp producers.
:::

The raw absolute wall clock and monotonic elapsed-time source come from
`PlatformEnvironment`. Runtime composes a `platform.time.TimeSource` from the
absolute Clock and passes that timing source to components that attach or record
event time. TimeSource returns `Instant`, keeping Platform independent of the
TimingData/domain value model. The current baseline implementation is `ClockTimeSource`;
tests and simulation may inject controlled equivalents.

TimeSource ownership is deliberately not encoded as TimingSystem or TimingNode
API. Composition decides its sharing scope. The current single-node Runtime has
one source; a later TimingSystem composition may pass one shared source to all
TimingNodes and timestamp-producing I/O providers in that system. This preserves
one corrected timing basis without creating another raw platform clock.

The I/O package structure is logical; executable composition is per
`TimingSystem`. Hosting 1..N TimingSystems therefore normally constructs 1..N
corresponding I/O compositions, each with its own configured Storage, Devices,
Messaging and DeviceNetworks objects. Explicit lower-level multiplexing may share
a physical resource, but the owning TimingSystem contexts stay separate.

`CanNetworkController` owns CAN-network lifecycle/discovery and CAN-device
communication. `NetworkDeviceService` owns the general bidirectional
network-device boundary. It may expose application data outward and accept
device-originated messages/events inward.

The high-level architecture deliberately stops there. Service discovery,
connection/listener/session handling and protocol framing are lower-level design
concerns below `NetworkDeviceService`. Likewise, a smart-display/domain handler
should not acquire socket, mDNS or transport knowledge merely because it is
reached through this service. The smart display remains an external client and
therefore does not require a `Rev2WifiDisplay` class inside SI-01 merely to
mirror the hardware name.

`TimingNode` contains its passive `LogBook` as part of the TimingNode
aggregate. LogBook keeps 0..N committed `TimingData` values. The current
design deliberately avoids a second logbook-specific record type because there
is no different domain shape that needs one.

`TimingData` remains the Domain capability/contract name and becomes the small
shared Java interface implemented by concrete profile values. The default profile
and validation/codec services realise the system-owned IF-05 contract. Concrete
storage, Web and messaging adapters may carry that record or its encoded form
without redefining field semantics.

`UpstreamProtocol` is a Domain capability owned by one `TimingSystem` and built partly on `TimingData`. It adds synchronization and protocol-level messages such as ping/pong so individual TimingNodes do not need to implement those concerns. `UpstreamGateway` owns the external transport boundary and uses 1..N concrete connectors. A connector such as `RabbitMqConnector` or `DebugConnector` owns transport/session mechanics, not TimingData or UpstreamProtocol semantics. `DebugConnector` is the engineering transport intended for an independent desktop/debug tool; that tool remains an external consumer rather than part of SI-01. `UpstreamMessageRouter` resolves semantic work inside the already selected TimingSystem context: system-level work uses `TimingSystem.UpstreamMessagePort`, while node-level work is resolved by `TimingNodeId` to `TimingNode.UpstreamMessagePort`. `TimingSystemId` is not required on the wire.

If the TimingNode capability grows into several cohesive areas, deeper
packages such as `timing/registration` or `timing/stage` may become useful.
Do not create those packages before the corresponding code exists.

The Domain-level `SystemStatus` is a dedicated component contained by one `TimingSystem`. It is a semantic aggregate, not a wrapper around
concrete adapter objects and not merely an `OK` flag. It can represent current
TimingNode state together with operational I/O state such as antenna/display
connectivity, keypad/beeper availability, device-network health, storage,
upstream connectivity and synchronisation. Concrete I/O components expose or
publish semantic status inputs; `SystemStatus` must not depend on classes such
as `Rev1CanDisplay`, socket/session implementations or vendor antenna drivers.

TimingNode status reaches this aggregate as an immutable semantic snapshot/result
created through the TimingNode ownership boundary. `SystemStatus` does not call
into `LogBook`, lifecycle fields, location fields or other mutable TimingNode
internals directly.

An external interface response shape does not require an equally shaped internal Java object.
For example, the status JSON does not by itself require classes named
`TimingNodeStatusSnapshot` or `TimingNodeStatusModel`.

## Contract placement

Place contracts with the responsibility that owns their meaning:

```text
presentation
  functional client interfaces / transport mapping / wire messages

application
  commands, queries, application-level ports and authoritative running
  configuration semantics

domain
  domain model, semantic ports, TimingData representation/codec and UpstreamProtocol semantics

io
  hardware, messaging and storage adapters

infra
  concrete cross-cutting technical support, including logging, diagnostics,
  configuration mapping and extension discovery

runtime
  concrete application composition, top-level running application and lifecycle

platform
  small JDK-only reusable primitives and execution-environment abstractions,
  including serial execution and local typed events
```

Do not create one generic top-level `api` package merely to collect
interfaces.

## Internal dependency direction

```text
presentation --> application
application  --> domain / I/O / platform
domain       --> I/O / platform
io           --> platform / JDK
runtime      --> application / domain / presentation / I/O / infra / platform
infra        --> owned support contracts + platform / JDK / selected support libraries
platform     --> JDK and low-level environment only
```

The normal dependency direction follows the layer order and is intentionally
easy to read from imports. A lower layer does not import a higher layer merely
to implement one of its interfaces. Domain may depend on a generic I/O contract,
but not on a concrete I/O implementation; Runtime composition selects the
concrete implementation.

For example:

```text
TimingNodeLogic
  -> TimingDataPersistence
       -> AppendOnlyRecordStore
            <- FileAppendOnlyRecordStore selected by Runtime
```

`AppendOnlyRecordStore` contains only opaque-record storage semantics.
`DefaultTimingDataPersistence` owns TimingData codec, TimingNodeId and sequence
validation. This keeps `io.storage` independent from Domain.
Executable composition may depend on the complete supported application-core surface
and selected external libraries.

## Logging dependency placement

:::{design} Runtime logging infrastructure
:id: DD-LoggingRuntime

Detailed Java design for reusable Logging ownership, retained/live sinks,
LoggingServer and runtime logging-level control.
:::


Logging follows the same library-versus-executable composition boundary.

```text
timing-point-core.jar
  -> slf4j-api only
  -> io.github.brainboxemb.eventtiming.timingpoint.infra.logging
       +-- Logging
       +-- LoggingConfig / LoggingLevel / LoggingFileConfig
       +-- LoggingControl
       +-- ConsoleHandler
       +-- TimestampedFileLogHandler + CompactLogFormatter
  -> io.github.brainboxemb.eventtiming.timingpoint.infra.loggingserver
       +-- LoggingServer
       +-- LoggingServerConfig
       +-- LiveLogHandler
       +-- client-initiated live diagnostics + temporary level control

timing-point-app.jar
  -> selects exactly one SLF4J provider
  -> default provider: slf4j-jdk14
  -> delegates SLF4J records to java.util.logging
  -> starts/stops core-provided Logging
  -> independently starts/stops optional LoggingServer
```

Working rules:

- application-core code may compile against the SLF4J API but must not force a concrete provider/backend on consumers;
- provider-neutral deployment values stay component-owned: `LoggingConfig` contains `LoggingLevel` and `LoggingFileConfig`; optional `LoggingServerConfig` belongs to `LoggingServer`; runtime `Config` may reference both as composition data;
- the executable application chooses and configures the provider/backend before `runtime.TimingApplicationRuntime.create(...)` starts normal application composition;
- the default Java-8 application uses `slf4j-jdk14` so the provider delegates to JDK `java.util.logging` without introducing Logback;
- concrete JUL backend/file lifecycle stays under `timingpoint.infra.logging`; the live diagnostics handler/socket lifecycle stays under `timingpoint.infra.loggingserver`; neither package defines domain/application contracts;
- `infra.logging` must not depend on `infra.loggingserver` or `runtime.config`; the thin executable starts the two infrastructure components separately before handing control to runtime composition. `infra.loggingserver` may depend on the narrow public `Logging` runtime surface for current level control and record formatting, but the logging component does not construct or own the server;
- `LoggingServerConfig` belongs to the `LoggingServer` component and carries its listener values (`bindAddress`, `port`); the default YAML loader maps the external `logging.live` syntax to that component-owned type;
- `LoggingLevel` is a logging-domain value rather than `LoggingConfig.Level`, so live level control does not depend on an umbrella configuration class;
- the core artifact owns that reusable implementation because it has no dependency on executable-specific YAML/resource loading and uses only JDK facilities plus component-owned logging configuration;
- `Logging` is the primary runtime logging infrastructure component and owns backend setup, console/file handler composition, record formatting and the current global-level control;
- `LoggingServer` is the separate externally reachable live-diagnostics component; it owns the live JUL handler plus logging-specific socket/protocol boundary, delegates temporary level changes to `Logging`, and is not a Presentation/IF-03 endpoint;
- the default retained file sink uses the local wall-clock start/rotation timestamp as a human-readable filename, normally `yyyyMMdd-HHmmss.txt`; this timestamp is not treated as a unique or monotonic session identity;
- Raspberry Pi startup must not assume that wall-clock time is already network-synchronised: the clock may repeat or move backwards across restarts, so retained log creation must use non-overwriting create semantics, add a collision suffix when necessary, and protect the active log from retention decisions regardless of timestamp ordering;
- retained text records use the compact operator-facing form `HH:mm:ss.SSS - [LEVEL] - message - [sourceClass.sourceMethod]`; exception stack traces follow the record line when present;
- `LoggingControl` owns the configured global level plus an optional temporary runtime override; applying an override changes the running logger threshold without mutating deployment configuration;
- the optional diagnostic listener is a logging-specific engineering facility. The test client initiates its TCP connection, log delivery is best effort, and network failure must not be allowed to block ordinary log publishers;
- the live diagnostics protocol is separate from the IF-03 status/event wire model;
- another executable/private consumer may select another compatible provider without changing core/domain source;
- exactly one provider should be present in a runtime composition;
- provider/backend versions are pinned centrally by Maven dependency management rather than scattered through modules.

This keeps provider selection replaceable at the executable boundary while allowing the reusable
application core to provide the default JUL logging infrastructure and its configuration contract.

## Default executable application

:::{design} Executable and presentation composition
:id: DD-ExecutableComposition

Detailed Java composition/lifecycle design for TimingApplicationRuntime,
PresentationRuntime and the built-in Console, RemoteShell and API adapters.
:::


`timing-point-app` is the executable consumer of the application-core library.

Its executable package is deliberately thin:

```text
io.github.brainboxemb.eventtiming.timingpoint.app/
  Main.java
```

The application core owns the reusable SI-01 runtime and supporting infrastructure:

```text
io.github.brainboxemb.eventtiming/timingpoint/
  runtime/
    Lifecycle.java
    TimingApplicationRuntime.java
    RuntimeExecutors.java
    RuntimeTimeSources.java
    simulator/
      SimulationRuntime.java
    config/
      Config.java
      Presentation.java
      Api.java
      YamlLoader.java
  infra/
    BuildIdentity.java
    EmbeddedBuildIdentityLoader.java
    logging/
      Logging.java
      LoggingConfig.java
      LoggingLevel.java
      LoggingFileConfig.java
      LoggingControl.java
      TimestampedFileLogHandler.java
      CompactLogFormatter.java
    loggingserver/
      LoggingServer.java
      LoggingServerConfig.java
      LiveLogHandler.java
```

`runtime/` owns knowledge of the concrete running application through
`TimingApplicationRuntime`, execution-resource construction and the effective composition
configuration. Figure SI01-01 shows this explicitly as the **Runtime** block.
Runtime is not another business/domain layer; it is where the executable object graph is
assembled.

The executable composition must remain readable as one linear construct-wire-start flow.
`runtime.TimingApplicationRuntime.create(...)` is the single concrete composition root and the
returned `TimingApplicationRuntime` owns the lifecycle of that already composed graph. A second
bootstrap/builder/composition class must not hide the object graph. Small private helpers may format repetitive local
construction, but cross-component relationships and lifecycle order remain visible in
`TimingApplicationRuntime.create(...)`. The visible composition and startup ownership is:

```text
validated Config
  -> PlatformEnvironment
  -> RuntimeExecutors/resources
  -> RuntimeTimeSources -> TimeSource
  -> Domain + I/O + Application objects
  -> explicit Conductor/event wiring
  -> RuntimeExecutors.start()
  -> Conductor.activate()
       -> AbstractConductor lifecycle template
            -> ComponentLifecycleManager.activateAll()
                 -> TimingNode.activate()
                 -> AntennaManager.activate()
            -> start Application lane
            -> Conductor.onActivated()
                 -> AntennaManager startup self-test runs asynchronously
                 -> initialize tracked application properties
  -> PresentationRuntime.activate()
```

`application.Conductor` owns SI-01 application coordination between already
constructed components. Runtime creates and wires the Conductor but does not reimplement
application startup policy in the composition root.

Generic Conductor lifecycle mechanics are deliberately kept out of the concrete SI-01
class. `application.logic.AbstractConductor` owns the reusable lifecycle template:
component registration, ordered activation, starting/closing the Application lane,
activation-failure cleanup and reverse-order deactivation. It uses
`application.logic.ComponentLifecycleManager` for the mechanical component order and
rollback.

The abstract base has one concrete-startup hook, `onActivated()`, called only after
registered components are active and the Application lane is running. The base contains no
TimingNode, AntennaManager, provider, property or SI-01 decision logic.

The concrete `application.Conductor` registers its components and implements
`onActivated()` with SI-01 startup actions such as tracked
property initialization. It also contains the application rules that map tracked values to
component intent.

```text
AbstractConductor
  generic lifecycle only
      |
      +--> ComponentLifecycleManager
      +--> Application SerialExecutor lifecycle
      +--> cleanup / rollback mechanics
      |
      v
Conductor
  SI-01 logic only
      |
      +--> TimingNodeStateProperty
      +--> antenna inventory intent from TimingNode state
      +--> TimingNode state -> explicit antenna inventory action
```

Neither class is a general application framework. Component discovery, dependency
injection, rule engines and provider lifecycle do not belong in this base hierarchy.

Conductor owns one logical `SerialExecutor` application lane on a Runtime-owned
application worker. Application-level values that drive cross-component behaviour are
represented explicitly as application properties backed by the generic
`infra.property.TrackedProperty<T>` mechanism rather than as Conductor-specific
refresh flags.

`infra.property.TrackedProperty<T>` owns only the reusable mechanism: a readable name,
an authoritative value reader, the shared Application lane, current-value tracking,
change detection and coalesced refresh scheduling. It has no knowledge of TimingNode,
AntennaManager or Conductor.

Concrete application properties live under `application.property`. They bind the generic
mechanism to one application concept and expose a domain-meaningful change signal. A source
event is only a **change signal**: it never becomes the stored value directly. The tracked
property schedules its own refresh on the Application lane, reads the current authoritative
value and invokes application behaviour only when the effective value changed.

The first concrete property is `TimingNode.lifecycle`:

```text
TimingNode.statusChangedEvent
        |
        | change signal only
        v
application.property.TimingNodeStateProperty
        |
        | read TimingNodeQueries.status().lifecycle()
        | compare with tracked current value
        v
lifecycle changed
        |
        v
Conductor application rule
        |
        +--> AntennaManager inventory required = (lifecycle == OPEN)
```

Because local `Event<T>` delivery is synchronous, the event callback performs only
bounded property signalling; cross-component behaviour never runs on the emitting
TimingNode thread. During startup Conductor first activates components and performs
required health work, then performs an explicit initial property refresh before startup is
reported complete. The same property logic handles later changes without replaying stale
event snapshots.

`TrackedProperty<T>` is deliberately not a general reactive framework, rule engine
or dependency graph. New properties are added only for concrete application-level values
that need tracked current state and change-driven behaviour.

`RuntimeExecutors` construction allocates executor objects only; physical worker startup
is an explicit `start()` action owned by Runtime. Runtime also owns the outer
`PresentationRuntime` lifecycle and activates Presentation only after Conductor has made
the application core ready. Runtime execution resources are closed only after Conductor
has deactivated its application components and Presentation is inactive.

Cross-component event wiring is visible at the composition point. The antenna manager owns
the concrete `Antenna` instances; it does not expose those device objects for callers to
walk. Composition addresses a configured source by `AntennaId` and subscribes the target
to the manager's subscription-only event source, conceptually:

```java
antennaManager.tagObservedEvent(antennaId)
        .subscribe(timingNode.tagProcessor()::onTagObserved);

timingNode.statusChangedEvent()
        .subscribe(conductor.timingNodeLifecycleProperty().changeSignal());
```

For semantic local events, accessor names describe the fact that happened and end in
`Event`, matching existing names such as `statusChangedEvent()` and
`timingDataCommittedEvent()`. The antenna APIs therefore use
`tagObservedEvent()` / `tagObservedEvent(AntennaId)`; a plural collection-like name such
as `observations()` is not used for an `EventSource`. `TagObservation` remains the
immutable event value and does not need an `AntennaId` field merely for routing because
the configured source identity is already known at the subscription point.

`runtime.simulator.SimulationRuntime` is an explicit simulator composition entry point.
It selects simulated installations/mappings through the same `TimingApplicationRuntime.create(...)`
path; it
does not introduce a simulated domain path or bypass TagProcessor/TimingNode.

The running application's configuration is not the same object as the startup YAML/runtime mapper DTO. Runtime owns the concrete `ApplicationConfiguration` tree because that tree describes the composed executable and its current effective settings. Infrastructure owns the reusable typed configuration-value mechanics. the Application layer owns the configuration query/update use-cases over that runtime tree and exposes only a narrow control interface toward Presentation. Domain, Presentation and I/O consumers do not receive writable access to the runtime tree merely because they need one configured value.

The executable artifact remains deliberately thin. Its launcher/input adapter stays under `...eventtiming.app`; reusable logging remains Infrastructure support. Main selects the config file, supplies process console streams and installs the JVM shutdown hook, but does not construct or order concrete Presentation adapters. Runtime composition owns `PresentationRuntime`, which creates the configured HTTP/WebSocket/remote-shell/local-console adapters and participates in normal activate/deactivate ordering. The IF-11 YAML mapper stays with `runtime.config` because it knows the concrete runtime configuration schema.

```text
timing-point-core.jar
  io.github.brainboxemb.eventtiming.timingpoint.infra/
    BuildIdentity.java
    EmbeddedBuildIdentityLoader.java
    configuration/
      ReadOnlyConfiguration.java
      DynamicConfiguration.java
      ConfigurationChange.java
      ConfigurationUpdateResult.java
      DefaultDynamicConfiguration.java
      FixedConfiguration.java

  io.github.brainboxemb.eventtiming.timingpoint.application/
    ConfigurationControl.java
    Conductor.java
    framework/
      AbstractConductor.java
      ComponentLifecycleManager.java
    property/
      TimingNodeStateProperty.java

  io.github.brainboxemb.eventtiming.timingpoint.runtime/
    TimingApplicationRuntime.java
    RuntimeExecutors.java
    RuntimeTimeSources.java
    PresentationRuntime.java
    ShutdownSignal.java
    configuration/
      ApplicationConfiguration.java
      TimingNodeConfiguration.java
    config/
      Config.java
      Presentation.java
      Api.java
      YamlLoader.java

timing-point-app.jar
  io.github.brainboxemb.eventtiming.timingpoint.app/
    Main.java
```

`timing-point-core.jar` contains the JUL-based default logging infrastructure but still does **not** select an SLF4J provider. Provider selection remains an executable-composition concern: the default app contributes `slf4j-jdk14` at runtime, while another consumer may choose another compatible composition and omit the default `Logging` component.

The executable startup/configuration flow is:

```text
main()
  -> core EmbeddedBuildIdentityLoader
       -> executable-provided filtered build resource
  -> configuration resolution
       -> selected built-in application-profile defaults
       -> selected platform defaults
       -> selected operating-mode defaults
       -> explicit IF-11 YAML deployment overrides
       -> secret resolution
       -> validated effective startup runtime Config
  -> core runtime configuration-tree resolution
       -> compiled component defaults
       -> apply resolved IF-11 startup overrides
       -> create runtime ApplicationConfiguration tree
  -> Logging
       -> configure JUL level + console/file handlers
  -> optional LoggingServer
       -> attach live handler + diagnostics listener
       -> use Logging for current level / common formatting
  -> core runtime.TimingApplicationRuntime.create(...)
       -> create PlatformEnvironment
       -> create RuntimeExecutors and RuntimeTimeSources
       -> create one TimeSource for the current timing context
       -> construct reusable application/domain/I/O objects
       -> construct and wire application.Conductor
       -> construct configured PresentationRuntime adapters
       -> return composed TimingApplicationRuntime
  -> TimingApplicationRuntime.activate()
       -> RuntimeExecutors.start()
       -> Conductor.activate()
            -> AbstractConductor activates application components + Application lane
            -> Conductor.onActivated() performs SI-01 startup health/property work
       -> PresentationRuntime.activate()
  -> executable waits for shutdown request and owns JVM shutdown-hook handling
```

The current `runtime.config.YamlLoader` implements only the explicit
YAML subset already needed by the running application. `runtime.config.Config`
is a startup/composition input and is not the authoritative mutable configuration
object of the running process. Profile/platform/mode
resolution is part of the configuration architecture but is not yet implemented; the architecture does not
require a new public Java type for each source before that behaviour is
implemented.

`BuildIdentity` and runtime `Config` are different inputs. Build identity is artifact provenance; application configuration is deployment composition defined by IF-11. The executable embeds deterministic provenance fields (`application`, `version`, exact `revision`, `sourceRef`, `buildOrigin`, `dirty`, `apiVersion`). Wall-clock build time, CI run/build id and actor/user are not embedded because they are per-run metadata rather than stable build inputs/context.

Reusable application behaviour should not migrate into the executable merely because the architectural responsibility is called `application`. When a reusable application-core runtime object becomes justified by real shared behaviour, executables should **compose** that object rather than extend a `BaseApplication` hierarchy.

The application core uses one explicit runtime composition boundary. There is no builder layered on top of another bootstrap object. `runtime.TimingApplicationRuntime.create(...)` constructs and wires the current graph. The returned Runtime owns process-level composition, physical execution resources and outer Presentation lifecycle; `application.Conductor` owns lifecycle coordination of the application components inside that graph.

### Running configuration model

:::{design} Running configuration model
:id: DD-RunningConfiguration

Detailed design for ApplicationConfiguration, reusable typed Configuration
values and presentation-facing ConfigurationControl use-cases.
:::


The configuration design has three deliberately separate ownership levels:

```text
Infrastructure
  typed configuration-value mechanics

Runtime
  concrete ApplicationConfiguration tree for this executable

Application
  query/update use-cases over that tree
```

Infrastructure provides the reusable value contracts. They contain no knowledge of
TimingNode, TagProcessor, YAML paths or API routes:

```java
interface ReadOnlyConfiguration<T> {
    T startupValue();
    T currentValue();
    boolean overridden();
    EventSource<ConfigurationChange<T>> changes();
}

interface DynamicConfiguration<T> extends ReadOnlyConfiguration<T> {
    ConfigurationUpdateResult override(T value);
    ConfigurationUpdateResult clearOverride();
}
```

A successful update replaces one immutable typed value atomically and emits one
typed `ConfigurationChange<T>`. Validation happens before replacement. `NO_CHANGE`
does not emit a change. `INVALID` and `RESTART_REQUIRED` leave the current value
unchanged.

Runtime owns `ApplicationConfiguration` and its concrete branches such as
`TimingNodeConfiguration`. This is the authoritative configuration tree of the
currently composed process. It is not a generic key/value map and it is not the
external IF-11/YAML DTO.

Application owns `ConfigurationControl`: the use-case boundary for querying current
configuration and requesting runtime changes. Runtime composition supplies the
node-scoped `DynamicConfiguration<TagProcessingPolicy>` views when constructing this
control; Presentation never receives those Infrastructure objects or the concrete
`ApplicationConfiguration` tree directly.

`ConfigurationControl` returns Presentation-safe startup/current policy projections,
runtime-mutability metadata and semantic `APPLIED`, `NO_CHANGE`, `INVALID` or
`RESTART_REQUIRED` update outcomes. Partial TagProcessing SET requests are serialized
by this control and are built from the current effective policy, so omitted fields retain
the value from the preceding accepted update rather than reverting to startup defaults.
An applied change emits one post-fact application `Change` event; no-change, invalid
and restart-required requests do not emit that event.

Normal components receive only the narrow Infrastructure read-only view they need.
For TagProcessor that value is immutable `TagProcessingPolicy`. A runtime update
that changes `observationQueueCapacity` is rejected atomically as
`RESTART_REQUIRED`; the dynamic duration/cadence subset is not partially applied.
TagProcessor reads `currentValue()` when making policy decisions. Its change
subscription is used only for mechanics that need explicit re-registration, such
as replacing the fixed-delay housekeeping cadence.

Runtime composition creates the concrete configuration tree from compiled component
defaults plus resolved IF-11 startup overrides. Clearing a runtime override restores
the resolved startup value; restart reconstructs the tree from those startup sources.

The default IF-11 file syntax is YAML and its parser/mapping stays beside the effective runtime configuration model. `runtime.config.YamlLoader` maps external YAML into `runtime.config.Config`; it is not a generic Infrastructure YAML utility. As profile support is implemented, configuration support resolves built-in profile/platform/mode defaults plus explicit deployment YAML before runtime composition starts.

The resolver responsibility must remain data/composition oriented:

- application profiles are data/default templates, not Java subclasses;
- do not introduce profile-specific Application subclasses or a
  profile-specific domain hierarchy;
- profile defaults may select topology/cardinality and capability defaults;
- platform defaults may select environment-specific values;
- operating-mode defaults may replace real providers with simulated providers;
- explicit IF-11 deployment values have highest non-secret precedence;
- `runtime.TimingApplicationRuntime.create(...)` consumes only the resolved/validated runtime `Config` and contains no profile-name switches.

SnakeYAML is therefore an application-core implementation dependency; the IF-11 contract
remains independent of SnakeYAML APIs and another input adapter may construct the
same typed effective runtime `Config` without YAML.

Build-identity interpretation is reusable for the same reason. The application core owns
`BuildIdentity` and `EmbeddedBuildIdentityLoader`. The concrete executable still owns
the filtered `event-timing-build.properties` resource and build-time provenance injection,
because those values identify that executable artifact. The core loader only interprets
the classpath resource and has no dependency on `app.Main` or another app class.

The implemented presentation structure is:

```text
presentation/
  interfaces/
    console/
      LocalConsole
    shell/
      RemoteShellServer
    api/
      HttpEndpoint
      WebSocketEndpoint
      WebSocketOutboundDelivery
      MessageWriter
  common/
    terminal/
      TerminalSession
```

Console and remote shell are separate presentation interfaces. They share the
line-oriented command parsing and text presentation in
`presentation.common.terminal.TerminalSession`; both call the same
`PresentationGateway` application boundary and shutdown callback. The current shared
terminal command baseline is:

```text
help
version
status
open <locationId>
close
auto-reg <registrationId> <time>
config
config tag-processing set <field=value>...
config tag-processing clear
log
log T|D|I|W|E
quit
exit
```

These are Presentation commands, not a second Domain/Application semantic contract.
`open`, `close` and `auto-reg` delegate to `TimingNodeProxy`; configuration
commands delegate to `ConfigurationControl`. `log` reads/changes the temporary
global log level through `LoggingLevelControl`; the single-letter forms map to
TRACE, DEBUG, INFO, WARN and ERROR. LocalConsole and RemoteShell therefore
cannot drift into separate implementations of node or configuration behaviour.

Console, Remote Shell and API are baseline Timing Point Application capabilities.
Application profiles do not add/remove or redefine their command/status semantics.
Concrete network listener bindings remain deployment configuration, so a listener
may still be explicitly left unbound/disabled without creating another profile.

The functional **API** currently contains:

```text
HttpEndpoint
  +-- GET  /api/v1/version
  +-- GET  /api/v1/status
  +-- GET  /api/v1/configuration
  +-- POST /api/v1/node/{nodeId}/configuration/tag-processing
                    |
                    +--> PresentationGateway
                           +--> TimingNodeProxy
                           +--> ConfigurationControl

WebSocketEndpoint
  +-- WS /api/v1/events
  +-- STATUS_SNAPSHOT on connect/reconnect
  +-- STATUS_CHANGED only for real status changes
  +-- TIMING_DATA_COMMITTED after committed TimingData
  +-- CONFIGURATION_CHANGED only after an applied runtime configuration change
```

`MessageWriter` owns the IF-03 wire/JSON representation shared by the Remote
API HTTP and WebSocket transports. It is not application/control logic and therefore
does not live in the application layer or in global presentation common code.

The local class names deliberately omit the `Api` prefix because the enclosing `presentation.interfaces.api` package already supplies that functional context. `Endpoint` is used rather than `Server` for the transport-facing classes; in particular, `HttpServer` is avoided because the implementation uses `com.sun.net.httpserver.HttpServer` internally.

The WebSocket transport uses `Java-WebSocket 1.6.0` in the reusable
application core and keeps the JDK HTTP transport unchanged rather than replacing
both transports with a larger combined stack.

`WebSocketOutboundDelivery` owns only per-client transport backlog bookkeeping.
`WebSocketEndpoint` still owns connection/event semantics. The delivery helper does not
buffer event values itself: it counts sends while the Java-WebSocket connection still
reports buffered data. After 32 such sends without an observed full drain, it refuses the
next event and requests close code 1013. This bounds application-driven growth of the
library's otherwise unbounded outbound queue without blocking, retrying or moving
backpressure onto TimingNode. Reconnect recovery remains authoritative through
`STATUS_SNAPSHOT` plus LogBook queries.

A browser-based engineering client, if added, should consume the API like any other external client. It does not require a separate SI-01 `presentation.web` package.

Manual inspection is provided by an independent development tool:

```text
test-client/
  TestClientApplication      plain Java launcher
          |
          v
  TestClientFxApplication    JavaFX development view
          |
          +-- ApiClient          HTTP/JSON client
          +-- ApiEventClient       Java 17 WebSocket client
          +-- RemoteShellClient          A05 raw TCP shell client
          |
          v
        SI-01
```

`test-client/` is a standalone Java-17 application and does not depend on
`timing-point-core` or `timing-point-app` implementation code. It may,
however, depend on the separately reusable `event-timing-data` artifact because
TimingData codec/provider reuse is now a real cross-executable requirement. This
preserves the external-client boundary while allowing SI-01 and the Development
Client to exercise the exact same public or proprietary TimingData translator.

The Development Client remains development/test support rather than the
SI-02 GUI, and its JavaFX choice does not select the SI-02 GUI technology.

The shared Presentation-facing application boundary remains small:
`PresentationGateway.version()` returns build identity,
`PresentationGateway.timingNode()` returns the node-scoped `TimingNodeProxy`, and
`PresentationGateway.configuration()` returns the application-owned
`ConfigurationControl`. The proxy obtains current node status through the TimingNode
query/ownership boundary; the configuration control operates on Runtime-supplied typed
configuration views. Presentation adapters therefore do not read node-owned fields or
the concrete Runtime configuration tree directly.

## Antenna input and tag-processing implementation

:::{design} Antenna runtime and device control
:id: DD-AntennaRuntime

Detailed Java design for AntennaManager, Antenna implementations, optional
PowerDevice control, inventory lifecycle and SimulatedAntenna behaviour.
:::


The Java antenna boundary separates device lifecycle from decoded observation processing.

### Antenna and manager

`Antenna` represents one configured logical antenna/device capability. It owns the
decoded observation event and provider-specific device/session mechanics needed for
startup self-test, initialization and inventory control.

The application-facing and device-facing lifecycle words are kept distinct. TimingNode
uses `OPEN` / `CLOSED`; antenna/provider cleanup uses `shutdown()` rather than
`close()` so device cleanup is not confused with TimingNode state.

Illustrative provider shape:

```java
interface Antenna {
    AntennaInfo selfTest();

    void initialize();

    void startInventory();

    void stopInventory();

    boolean inventoryRunning();

    void shutdown();

    EventSource<TagObservation> tagObservedEvent();
}
```

`selfTest()` is the startup device check and has PASS/FAIL semantics at manager level.
It may return decoded identity/version information for diagnostics, but SI-01 does not
model a parallel antenna status model merely to represent startup progress.
`initialize()` prepares the provider for normal use. `startInventory()` and
`stopInventory()` control observation delivery. `shutdown()` releases provider
resources and remains valid when initialization did not complete successfully.

#### Coordination ownership

Application intent and device mechanics are separate responsibilities:

```text
TimingNode state
      |
      v
  Conductor
decides inventory intent
      |
      v
AntennaManager
owns lifecycle + inventory intent
      |
      +--> AntennaSet
      |       +--> ManagedAntenna(s)
      |               +--> Antenna
      |               +--> optional PowerDevice
      |
      +--> reusable SelfTestTask
      +--> reusable InventoryTask
      +--> reusable AntennaShutdownTask
```

`Conductor` owns cross-component application decisions. It requests inventory enabled
or disabled from TimingNode state. It does not issue device-mechanism commands such as
power-on, initialize, power-cycle or reader switching.

`AntennaManager` is the single controller for the configured 1..N antenna capability of
one TimingSystem. It owns lifecycle/status, the requested/applied inventory setting and
one explicit manager control state machine. It owns the three reusable task objects
directly. The physical multi-step sequences live in those task classes under `manager/task`.
The task classes work directly on manager-owned `ManagedAntenna` objects; there is no
second task-facing antenna interface.

The manager uses a small `Setting<Boolean>` for inventory intent:

```text
requestedValue
appliedValue
changePending = requestedValue != appliedValue
```

`Setting` owns no executor, lifecycle, retry policy or device action.
`AntennaManager` calls `markApplied(value)` only after the corresponding task has
completed successfully. A
newer request may therefore arrive while an older transition is executing; once the older
transition completes, `changePending` still exposes whether another transition is needed.

Device objects and configuration remain separate concepts. `Antenna` and
`PowerDevice` are device objects. `AntennaSet` is the composition-time collection that
binds those device objects to stable `AntennaId` values and stores the optional external
power stabilization value. Multiplex membership and switch interval are configured once at
set level. There is deliberately no per-antenna `AntennaInstallation` value.

Activating `AntennaManager` starts one reusable `SelfTestTask` for the complete antenna
set. The manager does not contain the per-antenna self-test sequence and does not wait for
provider I/O. The task performs one physical action per turn, releases the shared worker
during real stabilization waits and publishes one completion event when the complete round
finishes. Presentation startup can therefore continue while self-test is in progress.

#### Temporary Windows development default

Until the normal runtime mapper composes the full IF-11 antenna configuration, the Windows
development platform uses one explicit fallback so AntennaManager is exercised by the
normal executable:

```text
PlatformEnvironment = WINDOWS
and no explicit antenna composition available yet
        |
        v
1 -> built-in SimulatedAntenna
        + optional SimulatedPowerDevice
        |
        v
normal AntennaManager
        |
        v
asynchronous self-test + inventory intent
```

This fallback is a development/platform default, not a silent physical-reader substitute.
Startup logging must state clearly that the Windows default selected a simulated antenna
and that no physical RFID reader is in use. On non-Windows platforms, no antenna
configuration continues to mean no AntennaManager.

Operating-system identity is exposed once through `PlatformEnvironment`; Runtime and
Application code must not scatter direct `System.getProperty("os.name")` checks.

Explicit IF-11 antenna configuration takes precedence as soon as that mapper/composition
path is implemented. The fallback does not redefine the IF-11 antenna schema or provider
selection rules.

#### Startup self-test

Startup self-test is one manager-owned cooperative task:

```text
AntennaManager.activate()
        |
        v
SelfTestTask

for each ManagedAntenna:
    POWER_ON
       |
       +-- AFTER(stabilization)
       v
    provider selfTest
       |
       +-- AGAIN
       v
    POWER_OFF
       |
       v
next antenna

round complete
       |
       v
selfTestCompletedEvent(result)
       |
       v
AntennaManager

self-test round complete -> manager ready for later control
individual PASS/FAIL results remain diagnostic
```

The configured stabilization interval is an actual physical wait and therefore uses
`AFTER(delay)`. The task owns the round and its execution handle. `AntennaManager`
subscribes once to the task completion event; it does not keep the task Future or duplicate
the per-antenna progress state. The current provider call may still be synchronous within
one task turn. A future provider may use callbacks, bounded polling or its own internal
execution without changing the manager contract.

Startup self-test result and normal operating state remain separate. The antenna operation
state is limited to the lifecycle needed for normal control:

```text
INACTIVE -> PREPARING -> READY -> INVENTORY
                              |
                              +--> stop -> READY

shutdown -> INACTIVE
```

After a successful self-test with external power removed, the antenna is therefore
self-test PASS + `INACTIVE`, not artificially `READY`.

#### TimingNode-driven inventory actions

SI01-REQ-053 is expressed as an application decision followed by an explicit
AntennaManager action. Conductor does not encode that action as a boolean flag:

```text
TimingNode state OPEN
        |
        v
TimingNodeStateProperty.changedEvent()
        |
        v
Conductor.onTimingNodeStateChanged(OPEN)
        |
        v
AntennaManager.requestEnableInventory()
        |
        +--> start a fresh preparation attempt
        +--> optional power ON
        +--> stabilization delay
        +--> initialize
        +--> start inventory directly
             or through multiplex group
```

The inverse flow is equally explicit:

```text
TimingNode state CLOSED or ERROR
        |
        v
TimingNodeStateProperty.changedEvent()
        |
        v
Conductor.onTimingNodeStateChanged(CLOSED/ERROR)
        |
        v
AntennaManager.requestDisableInventory()
        |
        +--> cancel multiplex rotation
        +--> stop inventory
        +--> optional external power OFF
```

`requestEnableInventory()` and `requestDisableInventory()` are asynchronous
application-facing requests. The convenience `enableInventory()` and
`disableInventory()` methods use the same asynchronous request path and only turn
immediate request rejection into an exception; they do not wait for physical completion.
Applied state is observed through manager/device status and the `Setting` state.

Disabling inventory is an operational action, not provider shutdown. The AntennaManager
remains ACTIVE and may enable the same antenna again after a later OPEN. Provider
`shutdown()` belongs to application/component deactivation.

An antenna mapped to multiple TimingNodes therefore remains enabled until the last assigned
TimingNode leaves OPEN. Conductor owns the application decision; AntennaManager owns the
power/initialize/start/stop mechanics.

#### Failure and recovery ownership

While inventory remains required, a runtime device failure does not change the application
intent. AntennaManager owns any recovery/reinitialization process needed to restore the
requested state:

```text
inventory enable remains requested
        |
        v
runtime antenna/provider failure
        |
        v
AntennaManager records failure
        |
        +--> stop/clean up failed operation
        +--> optional power cycle
        +--> stabilization / self-test or readiness check as required
        +--> reinitialize
        +--> resume inventory when usable
```

Conductor does not micromanage that recovery sequence and does not need to resend the same
OPEN-derived intent after every provider failure. The exact automatic retry trigger,
retry limit, delay/backoff and terminal-failure policy remain an open detailed-design
decision and must be tied to an explicit requirement before implementation adds that
policy.

#### Execution and delayed device work

AntennaManager owns one project `SerialScheduledExecutor` logical control lane on the
Runtime-owned scheduled I/O-role worker. One `ScheduledTaskRunner` executes all three
manager-owned reusable tasks. This does not add physical threads.

```text
          Runtime-owned shared scheduled I/O worker
                         |
                         v
               SerialScheduledExecutor
                 AntennaManager lane
                         |
                         v
               ScheduledTaskRunner
                  /       |       \
                 v        v        v
          SelfTestTask InventoryTask ShutdownTask
                 \        |        /
                  \       v       /
                   -> ManagedAntenna(s)
                         |
                         +--> Antenna
                         +--> optional PowerDevice
```

Each cooperative task executes one logical step per turn and returns `AGAIN`,
`AFTER(delay)` or `DONE`. `AGAIN` is a yield back to the queue. `AFTER(delay)`
uses a timer registration and does not occupy the physical worker while waiting.
Antenna-specific code must not rebuild these mechanics with ad-hoc
`CompletableFuture.thenCompose(...)` chains.

For antenna control, one task turn corresponds to at most one direct physical device
action. `AntennaManager` owns one reusable self-test task, one reusable inventory task and
one reusable shutdown task directly.

Representative state machines are:

```text
SelfTestTask
  POWER_ON -> AFTER(stabilization) -> SELF_TEST -> POWER_OFF -> next antenna -> event

InventoryTask
  requested OFF:
    STOP_INVENTORY -> POWER_OFF -> applied=false

  requested ON:
    POWER_ON -> AFTER(stabilization) -> INITIALIZE -> START_INVENTORY
    -> applied=true

  multiplex while requested ON:
    WAIT(interval) -> STOP_CURRENT -> START_NEXT -> WAIT(interval)
```

The inventory task re-reads the requested `Setting<Boolean>` on each turn. A changed
request therefore changes the next direction of the same long-lived state machine rather
than causing a second inventory controller or a new enable/disable task object to be
constructed.

A synchronous provider method such as `selfTest()`, `initialize()`,
`startInventory()` or `stopInventory()` still occupies the worker for the duration of
that call. Cooperative scheduling cannot make a blocking provider API non-blocking. A real
provider must therefore either use bounded device/protocol I/O for such a step or expose
staged readiness/completion mechanics that its own cooperative state machine can use.

The generic manager runner does not justify a second timeout thread merely to interrupt an
unknown future provider implementation. Exact provider-operation timeout/cancellation
semantics are deferred until a real antenna provider establishes what its serial/network
API can guarantee. Whatever mechanism is chosen must not block the shared worker waiting
for work that still needs that same worker or serial lane to execute.

A concrete antenna/provider implementation may itself use cooperative tasks when one
device operation consists of multiple protocol commands, waits, retries or readiness
checks. If isolation requires a device-specific logical lane, that lane may still use the
same Runtime-owned physical I/O worker. This preserves ordering/isolation without creating
one operating-system thread per antenna.

Concrete `Antenna` construction is passive. Creating and wiring a provider object must
not start inventory or hidden background activity.

#### External power

External power switching is optional and modelled as a separate `PowerDevice`.
Composition may bind an antenna to a power device plus a stabilization duration. The
manager task can then order power-on before self-test/initialize, yield for stabilization,
and power-off when the antenna is no longer required.

`PowerDevice` remains separate from `Antenna`. A physical reader may be powered through
a relay board, GPIO-controlled supply or another installation component unrelated to the
reader vendor protocol. A provider that owns its power mechanism internally may omit the
external device.

#### Multiplex switching

One AntennaManager supports zero or one inventory mutual-exclusion group. Antennas outside
that group operate independently. The group contains 2..N configured antennas that may
not inventory simultaneously.

SI01-REQ-054 requires only this behaviour:

```text
inventory group required
        |
        v
start first available member

every configured interval:
        current member inventory OFF
                    |
                    v
        next healthy member inventory ON
                    |
                    +--> failed/unavailable member: skip
```

At most one healthy group member inventories at a time. A failed member is skipped without
stopping healthy members.

The switch is fail-safe when stopping the currently active member fails. Because that
reader may still be inventorying, `AntennaSwitchTask` must **not** start another group
member. The failed stop is recorded on the current antenna and normal
recovery/diagnostics handle the fault; mutual exclusion takes priority over continuing
round-robin rotation.

There is deliberately no separate switching controller. `AntennaSwitchTask` owns the
small amount of switch-local state: phase, current/next selection and interval wait. It is
one reusable state-machine object owned directly by `AntennaManager` and reset
before a new switching run.

The task does not own startup self-test, power preparation, antenna initialization,
manager-wide status, requested/applied inventory state or generic scheduling mechanics.
Those remain with their existing owners.

The public/reference baseline remains the known two-antenna group with a 500 ms interval.
The number of configured antennas does not by itself justify more physical I/O workers;
V01 runtime characterization remains the authority for increasing physical parallelism.

The built-in `SimulatedAntenna` path models the same lifecycle contract. Simulation
includes explicit powered/unpowered state when paired with simulated power control,
initialization/inventory preconditions and controllable self-test/initialize/start failures so
startup containment, recovery design and multiplex behaviour can be verified without
hardware.

### TagObservation and local event delivery

`TagObservation` is an immutable decoded input fact:

```java
final class TagObservation {
    TagId tagId();
    int rssi();
    TimingTimestamp observedAt();
}
```

The antenna/provider implementation owns vendor bytes, framing, encryption and
decryption. Once that work is complete, the generic observation carries the
semantic `domain.eventdata.TagId`. RSSI is the decoded/normalized signal
strength used by TagProcessor policy.

The timestamp is attached at the earliest accepted decoded-observation point. It
becomes the automatic registration effective time when that observation is selected
as the strongest observation of the resolved RegistrationId passage and the
TimingNode command is admitted.

Each antenna owns:

```java
private final Event<TagObservation> observationEvent = new Event<>();

public EventSource<TagObservation> tagObservedEvent() {
    return observationEvent;
}
```

Provider callbacks perform only bounded observation ingress. EventData resolution,
duplicate suppression, passage filtering, diagnostics and TimingNode admission run
on the TagProcessor serial scheduled lane.

### Optional raw-observation persistence

Raw tag-observation logging is a separate non-critical consumer of
`EventSource<TagObservation>`. It does not sit inline between Antenna and TagProcessor.

The Java shape is a bounded asynchronous sink:

```text
Antenna Event<TagObservation>
       |
       +--> TagProcessor ----------------------> TimingNode.offer(...)
       |
       +--> RawTagObservationSink
              |
              +-- bounded local buffer
              +-- non-blocking offer on callback thread
              |
              v
        shared bounded I/O ExecutorService
              |
              v
        append/rotate diagnostic observation store
```

Do not submit one unbounded executor task per observation. The sink owns a bounded buffer
and schedules/drains work through the shared executor so a burst of raw observations
cannot fill the executor queue with arbitrary numbers of tiny persistence tasks.

Required behaviour:

- observation callback performs only a bounded/non-blocking buffer offer;
- one sink keeps at most one drain job queued or running; new observations go only into
  that sink's bounded local buffer;
- a drain job processes a bounded batch before returning to the shared I/O executor;
- stored records preserve the immutable observation values exactly enough for diagnostics;
- queue-full/drop count is observable;
- storage/write failures are observable;
- diagnostic logging failure does not change TagProcessor admission or TimingData commit;
- shutdown performs a bounded drain according to the configured diagnostic-retention
  policy and then closes the store;
- raw observation files are explicitly non-authoritative and may be rotated/retained
  independently from TimingData.

A concrete sink may bind source/antenna identity from the subscription/composition context
when that is needed for diagnostics; D04 does not require source identity to be added to
the generic TagObservation value merely for logging.

### Tag processing

The node-local tag-processing path is:

```text
TagProcessor
  -> EventData.registrationIdFor(TagId)
  -> RegistrationDuplicateFilter
  -> TagObservationFilter
       keyed by RegistrationId
       retains per-TagId passage attribution
  -> TimingNode.offer(...)
```

`TagProcessor.onTagObserved(...)` is the Antenna EventSource callback. It only
attempts bounded admission of the immutable observation and returns. Mapping,
filtering and diagnostics do not run on the provider callback thread.

On the TagProcessor lane, EventData first resolves the semantic `TagId` to a
`RegistrationId`. Unmapped observations are counted and discarded. Duplicate
suppression is then checked by RegistrationId. Only registrations that still need
processing enter passage aggregation.

One participant/registration may have multiple physical tags. The passage filter
therefore remains keyed by RegistrationId:

```text
TAG-A -> R-123 --+
                  +--> one R-123 passage
TAG-B -> R-123 --+
```

It does **not** maintain independent passage or duplicate windows per tag.

#### Registration passage state

A high-rate reader may report many observations during one physical passage. Keep
one small mutable passage state per active RegistrationId. In addition to expiry
and strongest-observation state, retain compact per-tag attribution:

```text
PassageState R-123
  firstSeenNanos
  lastSeenNanos

  TAG-A
    observationCount
    strongestRssi
    first/last observed time

  TAG-B
    observationCount
    strongestRssi
    first/last observed time

  selected
    TagId
    strongestRssi
    observedAt
```

The implementation need not retain every TagObservation. Per-tag counters/extrema
are sufficient for the baseline diagnostic requirement.

A passage closes when either condition becomes true:

```text
now - lastSeen >= quietTimeout
OR
now - firstSeen >= maxBurstDuration
```

The selected candidate is the strongest observation over the complete
RegistrationId passage, regardless of which associated TagId produced it. Equal
RSSI keeps the earlier selected observation unless later requirements define
another rule.

The selected observation's original TimingTimestamp becomes the automatic
registration effective time.

#### Duplicate suppression and admission

The filtering order is:

```text
TagObservation(TagId, RSSI, observedAt)
  |
  +--> EventData.registrationIdFor(TagId)
          |
          +--> no RegistrationId ----------------------> unmapped
          |
          +--> RegistrationDuplicateFilter ------------> duplicate
          |
          +--> TagObservationFilter
                  keyed by RegistrationId
                  per-TagId attribution
                  strongest observation
                  |
                  +--> TimingNode.offer(addAutomaticRegistration)
                          |
                          +--> ACCEPTED -> record duplicate window
                          +--> FULL     -> do not suppress retry
                          +--> NOT_RUNNING -> do not suppress retry
```

Record duplicate-window state only after `TimingNode.offer(...)` returns
`ACCEPTED`. Once R-123 is suppressed, observations from TAG-A and TAG-B are both
suppressed because EventData resolves both to the same RegistrationId.

#### Engineering diagnostic view

TagProcessor exposes an immutable read-only diagnostic snapshot of pending/recent
passage processing. It is intended for engineering presentation and may contain:

- RegistrationId;
- contributing TagIds;
- observation count per TagId;
- strongest RSSI per TagId;
- selected TagId, RSSI and observed time;
- first/last observation timing;
- processing state/outcome where retained.

The snapshot is not TimingData, is not authoritative commit state and does not
allow mutation of TagProcessor. It may be sampled/published through the normal
Presentation path without making the engineering client part of timing processing.

#### Execution and housekeeping

TagProcessor still owns one bounded observation input queue and one logical
`SerialScheduledExecutor` lane. All TagProcessor lanes share the Runtime-owned
TagProcessor worker. Observation draining, policy changes, passage expiry and
duplicate cleanup use that same lane.

Housekeeping uses monotonic elapsed time and remains scheduled only while timed
processing state exists. No timer/scheduled task is created per observation and
no dedicated thread is created per TagProcessor.

The processor constructor receives EventData rather than a loose mapper:

```java
TagProcessor(
    TimingNode timingNode,
    EventData eventData,
    TagProcessingPolicy policy,
    MonotonicClock monotonicClock,
    TagProcessingMetrics counters,
    SerialScheduledExecutor executor)
```

`TimingApplicationRuntime.create(...)` does not expose a separate tag-to-registration
mapper parameter. Normal and simulated compositions construct/use EventData and then use
the same TagProcessor path.

`TagProcessingPolicy` continues to own quiet timeout, maximum passage duration,
registration duplicate window, sweep cadence and bounded observation-input queue
capacity. Runtime policy replacement remains serialized onto the TagProcessor lane.

### SimulatedAntenna

`SimulatedAntenna` implements the same lifecycle and observation contract. It can be
probed/initialized, inventory can be enabled/disabled and deterministic
`TagObservation` values can be emitted only while inventory is active.

It owns no TimingNode, mapper, filter or persistence shortcut. Its only test/simulation
specific capability is deterministic control of the decoded observations it publishes.

## Registration work and other runtime work

The normal automatic-registration flow is:

```text
antenna/provider callback
  -> Event<TagObservation>
  -> TagProcessor
  -> TimingNode.offer(...)
  -> TimingNode worker
  -> TimingDataPersistence.append(...)
  -> LogBook.add(...)
  -> timingDataCommittedEvent.emit(...)
```

The first four steps must stay short and must not write files, send network data or wait
for presentation/backoffice work. `TimingNode.offer(...)` is the fire-and-forget boundary:
it performs only bounded queue admission and returns to TagProcessor without executing or
waiting for the TimingNode command. The lower-priority TimingNode lane processes accepted
work independently afterwards.

The TimingNode worker is allowed to wait for the required
`TimingDataPersistence.append(...)` call because that local durable write is part of the
TimingData commit. After the record has been written and added to LogBook, short local
post-commit listeners may run synchronously on the TimingNode worker.

A post-commit listener that needs socket I/O, retry, backoffice delivery or another
potentially slow operation must hand that work to its own bounded delivery mechanism and
return. Synchronous `Event<T>` delivery is therefore allowed; Step-5 measurements check
whether listener execution time materially increases TimingNode queue wait or queue
high-water.

Raw antenna-observation logging is diagnostic work. It uses its own bounded buffer and
does not sit between TagProcessor and `TimingNode.offer(...)`. Losing raw diagnostic
records does not change whether a TimingData registration is accepted or committed.

## Internal runtime measurements

Runtime measurements are engineering data used to characterize the running Java design.
They are not TimingData, TimingNode domain state, application status or presentation/API
data.

The registration path records only small primitive counters and monotonic durations at
the component where the work happens. Reading measurements is a separate pull operation.
A read may allocate an immutable snapshot because it is not performed for every
observation or registration.

Three snapshot groups are used:

```text
TimingNodeRuntimeSnapshot
  queue depth / high-water
  admitted / full / not-running / completed work
  total + maximum queue wait
  total + maximum serial execution time
  TimingData append attempts / failures
  total + maximum append time
  committed TimingData count
  post-commit event deliveries / listener failures
  total + maximum post-commit event delivery time

TagProcessingMetrics.Snapshot
  received observations
  observation-input queue full / processor-not-running ingress
  closed observation bursts
  mapped / unmapped observations
  registration duplicates
  TimingNode admitted / full / not-running results

JvmRuntimeSnapshot
  heap used
  live thread count
  GC collection count
  GC collection time
  shared role-worker CPU time when the JVM exposes it
```

The exact Java value classes may group fields for readability, but these three meanings
must remain separate. A JVM/process snapshot is not a TimingNode snapshot, and
tag-processing counts are not TimingNode queue counts.

### Counter ownership

The component that performs the work owns the hot-path counter update:

- `SerialExecutorMetrics` owns lane-local queue admission, queue depth/high-water,
  queue wait and execution duration; callers read those values through an immutable
  `SerialExecutorMetrics.Snapshot`. `SerialExecutor` records the execution facts but
  does not embed the diagnostics model in the executor class. Because every physical worker
  is externally owned, lane snapshots do not claim its CPU time; the existing lane CPU-time
  field reports unavailable (`-1`);
- the TimingNode commit path owns TimingData append/commit and post-commit event-delivery
  counters;
- `TagProcessingMetrics` owns observation, burst, mapping, duplicate and
  TimingNode-admission counters for `domain.timing.processing` and exposes them through an
  immutable `TagProcessingMetrics.Snapshot`;
- `SerialScheduledExecutorMetrics` owns lane-local measurements such as accepted
  immediate work, scheduled registrations/cancellations, executed work, runtime failures
  and queue depth. `SerialScheduledExecutor` records those facts but remains focused on
  execution/lifecycle. The metrics class does not mirror TagProcessor's observation-input
  queue and does not attribute the externally owned worker's CPU time to one processor
  lane; its lane CPU-time field likewise reports unavailable (`-1`);
- physical role-worker identity/CPU time and JVM/process values are read on demand from the
  supported JDK management APIs.

Do not copy these counters into a second continuously updated model merely to make them
easier to display.

### Engineering access boundary

The current one-TimingNode characterization uses one explicit Java reader:

```text
domain/timing/processing/
  TagProcessingMetrics
    -> TagProcessingMetrics.Snapshot

runtime/measurement/
  RuntimeMeasurementReader
  TimingNodeRuntimeSnapshot
  JvmRuntimeSnapshot
```

`RuntimeMeasurementReader` is constructed only by engineering-harness composition. It
reads the component-owned counters and creates/returns the immutable snapshots above. The
tag-processing snapshot is the existing `TagProcessingMetrics.Snapshot`; D05 does not
add a second wrapper with the same fields.

Its visible read shape is:

```java
TimingNodeRuntimeSnapshot timingNode();
TagProcessingMetrics.Snapshot tagProcessing();
JvmRuntimeSnapshot jvm();
```

The normal public Domain component contract does not expose runtime measurements:

```text
TimingNode
  invoke(...)
  offer(...)
  query(...)
  statusChangedEvent()
  timingDataCommittedEvent()

  X runtimeMetrics()
```

`TimingNodeTypes` therefore contains Domain/result/status types only; an engineering
runtime snapshot is not a `TimingNodeTypes` member.

`RuntimeMeasurementReader` is not exposed through `PresentationGateway`, IF-03, the
local console or the remote shell merely for characterization. T01 obtains it from
engineering-harness composition that already depends directly on `timing-point-core`.

A02 may realize the reader's internal connection to TimingNode-owned counters with
package-private readers or composition-retained measurement handles. For tag processing,
composition may retain the same `TagProcessingMetrics` instance that it passes to
`TagProcessor`. That mechanical
choice must not add a public measurement method back to `TimingNode`, must not add
measurement types to `TimingNodeTypes`, and must not make the reader a second owner of
runtime state.

### Snapshot semantics

A snapshot is diagnostic, not transactional. Each field must be safe to read while the
application runs, but fields do not have to represent one globally locked instant. The
measurement path must not pause registration merely to make all counters change
atomically together.

Counter and duration totals are cumulative for the lifetime of their owning component.
The harness calculates workload deltas from a before/after pair instead of resetting
product counters between runs. Current queue depth is a gauge; queue high-water is a
lifetime maximum for that component instance.

Unsupported JVM measurements use an explicit unavailable value in the engineering
snapshot. Measurement unavailability or snapshot creation failure must not change
registration admission or TimingData commit behaviour.

No continuous measurement thread is introduced. Timer/scheduler work used for
TagProcessor burst expiry is unrelated to runtime measurement.

## Runtime thread ownership and naming

:::{design} Runtime execution model
:id: DD-RuntimeExecution

Detailed Java design for Runtime-owned physical workers and the bounded
SerialExecutor / SerialScheduledExecutor logical-lane realization.
:::


Project-owned SI-01 runtime threads use the diagnostic name form
`tp-<owner>-<role>[-<qualifier>]`. The prefix makes Timing Point Application threads easy
to separate from JDK, Maven/JGit and third-party library threads in a debugger, profiler or
thread dump. The owner abbreviations used by the current runtime are `prl` (Presentation),
`dml` (Domain), `io` (shared device/network I/O executor), `inf` (Infrastructure) and
`run` (Runtime/composition).

Examples:

```text
tp-prl-console
tp-prl-api-http
tp-prl-remote-shell
tp-inf-live-log
tp-inf-live-log-writer
tp-run-shutdown
tp-io-shared-<index>
tp-dml-node-worker
tp-dml-tagproc-worker
```

Physical worker names describe the shared executor role, not one logical object that happens
to submit work. A `TimingNodeId` therefore does **not** appear in the TimingNode or
TagProcessor worker-thread name: one worker services the lanes for multiple nodes over its
lifetime. Node identity remains available in lane/component diagnostics and metrics.

Threads owned by the JDK or external libraries keep their own names.

### Thread priority and execution roles

The execution design keeps latency-sensitive work on separate **role workers**, while
each configured node retains its own logical serial lane:

```text
shared TagProcessor role worker
  -> serial TagProcessor lane per TimingNode
  -> highest registration-ingress latency class candidate

shared TimingNode role worker
  -> bounded serial TimingNode lane per TimingNode
  -> medium registration/command latency class candidate

shared background/application execution
  -> lower-priority candidate for non-critical periodic/data-processing work
```

The third category is an execution resource for active background/application work; it is
not a reason to turn passive Domain objects into threaded objects. Blocking device/I/O work
also remains on its separate bounded I/O executor.

Step 5 still starts with normal/default Java thread priority for all roles. D04 defines
functional separation and makes later role-specific tuning possible, but does not assign
numeric Java priority values.

V01 measures queue wait, execution latency, CPU/thread behaviour and fairness. The current
reference stress workload is **20 registrations per second for the whole SI-01 application**.
That target is aggregate across all configured TimingNodes: adding a second node does not
turn it into 40 registrations/s. Multi-node characterization should vary the distribution
of that same total load (for example 20/0 and 10/10) to expose unfair scheduling or queue
growth without silently multiplying the hardware requirement.

If evidence shows useful separation under load, role-specific priorities may then be tested,
for example TagProcessor above TimingNode and background work below it. The exact values must
be qualified on both the development host and the Raspberry Pi target.

Correct registration behaviour, ordering and overload handling must never depend on Java
thread priority. Java priority is only a scheduler hint and may behave differently between
JVM/OS combinations.

## TimingNode active-object execution and persistence

:::{design} TimingNode execution, LogBook and local events
:id: DD-TimingNodeExecution

Detailed design for TimingNode ordered execution, durable TimingData commit,
passive LogBook reads and the local Event/EventSource publication boundary.
:::


The Java design implements the **Active Object pattern** for each TimingNode,
but does not make `TimingNode` inherit from an `ActiveObject` base class.

The architectural rule is simple:

```text
TimingNode
  +-- one bounded serial execution boundary
  +-- at most one work item active on that lane
  +-- physical TimingNode worker shared with other node lanes
  |
  +-- passive LogBook
  +-- passive NextUpTeams
  +-- passive StageStartTimes
  +-- passive RaceData
  |
  +-- per-type store ports
```

This gives one writer for all mutable per-node state and one clear ordering
between registration, lifecycle, next-up and reference-data changes.

### Why composition instead of an ActiveObject base class

A reusable base class such as `TimingNode extends ActiveObject<Work>` is
possible, but it would couple the domain type to one threading mechanism.
Composition keeps that choice replaceable and lets the public TimingNode API stay
synchronous and domain-oriented.

For state-dependent operations the caller waits for the result produced on the
TimingNode lane. Queue admission and the processed operation result are represented
separately:

```java
final class TimingNode {
    private final TimingNodeLogic logic;
    private final SerialExecutor serialLane;

    <R> R invoke(TimingNodeCommand<R> command) {
        // admit + wait for the processed result
    }

    CommandAdmission offer(TimingNodeCommand<?> command) {
        // bounded admission only; producer returns immediately
    }

    <R> R query(TimingNodeQuery<R> query) {
        // ordered consistency-sensitive read
    }
}

final class TimingNodeLogic {
    private State state = State.CLOSED;
    private LocationId locationId;
    private final LogBook logBook;

    OpenResult open(LocationId locationId) {
        // apply requested location + OPEN as one domain operation
    }
}
```

The visible `TimingNode` keeps execution mechanics around the component boundary, while `TimingNodeLogic` keeps the stateful domain behaviour readable. Queue admission and the processed domain result remain separate; moving the mutable logic out of the boundary does not make `TimingNodeLogic` externally addressable.

The public methods above are illustrative signatures, not a requirement to use
those exact result class names. The important split is:

```text
open(locationId) / close / consistency-sensitive query
    -> queued internally
    -> execute against current ordered TimingNode state
    -> caller receives processed domain result

device/callback ingress that is explicitly offer-only
    -> bounded queue admission result
    -> callback may continue immediately
    -> later processing has no synchronous caller waiting for its domain result
```

A queue-admission result is never used as a substitute for the domain result of
a state-dependent command.

The Future used to connect the queued work with a waiting caller is an internal
Active Object mechanism. It does not appear in the normal TimingNode
application/domain interface. The current synchronous caller contract needs only an internal plain
`Future<R>`; `CompletionStage` is not required.

Code already running on the TimingNode lane uses direct private/domain methods
such as `doOpen()` rather than calling the blocking public `open()` method
again. Re-entering a public blocking operation from the same serial lane would
wait on work that cannot run until the current work item finishes.

### Operation results and execution failures

Keep domain outcomes separate from failures of the execution boundary.

For example:

```text
OpenResult
  OPENED
  ALREADY_OPEN
  NO_LOCATION

submission/execution failure
  queue full
  node stopping/unavailable
  unexpected internal failure

wait timeout
  caller stopped waiting
  operation may still be queued or executing
  final domain outcome is unknown to that caller
```

A domain rejection such as `NO_LOCATION` is a normal processed result. Queue
full or a stopping worker means the operation was not admitted and belongs to an
operation/execution exception rather than `OpenResult`.

A timeout is different again. It means only that the caller did not receive the
processed result within the configured guard time. TimingNode timeout handling
must not automatically cancel or interrupt an already accepted state change.
The caller must treat the final outcome as unknown and re-query the current state
before assuming that the command did not happen.

TimingNode uses a small operation/execution exception model rather than leaking
`TimeoutException`, `ExecutionException` or `InterruptedException` from
`java.util.concurrent` through the domain API.
Keep that family small and add distinct exception types only where callers need
different recovery behaviour. Timeout is a useful distinct case because its
outcome semantics differ from definite submission rejection.

### SerialExecutor design

`SerialExecutor` preserves TimingNode execution semantics while separating the logical
bounded lane from the physical worker.

The production baseline is:

```text
Runtime TimingNode role executor
  ThreadPoolExecutor
    corePoolSize = 1
    maximumPoolSize = 1
    physical thread = tp-dml-node-worker

TimingNode A SerialExecutor lane
  bounded ArrayBlockingQueue
  at most one drain token scheduled

TimingNode B SerialExecutor lane
  bounded ArrayBlockingQueue
  at most one drain token scheduled
```

Only one lane item is processed per drain token. If another node already has a drain token
waiting on the shared role executor, it gets an opportunity to run before a busy lane
resubmits its next item. This provides fairness at task boundaries without pretending that a
single-core Raspberry Pi gains CPU capacity from one Java worker per TimingNode.

The role executor queue does not buffer registration workload directly. At most one drain
token per active lane is scheduled there; workload/backpressure remains in each bounded
lane-local `ArrayBlockingQueue`. The lane always runs on an externally supplied
`Executor`; production supplies the shared role executor and tests own any worker they
create.

Do **not** replace the lane-local bounded queue with
`Executors.newSingleThreadExecutor()` or another unbounded workload queue; that would hide
overload behaviour.

The project API keeps the two result moments explicit:

```java
final class SerialExecutor implements AutoCloseable {
    enum AdmissionResult {
        ACCEPTED,
        FULL,
        NOT_RUNNING
    }

    static final class SubmitResult<R> {
        AdmissionResult admission();
        Future<R> futureResult();
    }

    <R> SubmitResult<R> submit(Callable<R> work) {
        // Non-blocking bounded admission.
        // futureResult() exists only when admission() == ACCEPTED.
    }

    AdmissionResult offer(Runnable work) {
        // Admission-only fire-and-forget producer path.
    }
}
```

Usage rules:

- `AdmissionResult` answers only whether the bounded serial lane accepted the work item;
- `SubmitResult.futureResult()` represents the later processed result and is available only
  for accepted work;
- `ACCEPTED` is never interpreted as successful domain processing;
- `offer(Runnable)` is for producer paths that intentionally do not wait for a result;
- TimingNode `invoke(...)` and consistency-sensitive `query(...)` use the result-bearing
  path;
- TimingNode `offer(...)` uses the admission-only path.

The JDK executor rejection path is translated into the project `FULL / NOT_RUNNING`
semantics; `RejectedExecutionException` does not leak into normal TimingNode callers.

The required behaviour remains:

- queue capacity is visible and bounded per TimingNode lane;
- FIFO order is preserved for one TimingNode;
- at most one work item from one lane executes at a time;
- different node lanes share the role worker and make progress at task boundaries;
- state-dependent validation happens on the ordered node-local lane;
- result-bearing work has an internal Future;
- offer-only ingress observes definite queue admission without waiting;
- one ordinary work-item failure does not terminate the lane;
- an unexpected fatal lane failure is observable and does not shut down sibling lanes or the
  shared role worker;
- closing one lane stops new admission and drains its accepted work without closing the
  externally owned role executor;
- a fatal lane failure likewise never shuts down that executor;
- Runtime shuts down the shared role executor only after component lanes have stopped.

The TimingNode remains the owner of this execution lane. `SerialExecutor` is a Platform
primitive and contains no TimingNode/domain/persistence logic.

Execution measurements are owned by the separate `SerialExecutorMetrics` class in the same
Platform execution package. `SerialExecutor` only records lifecycle/admission/execution facts
into that object and exposes it through `metrics()`. Hot-path updates remain
primitive/low-allocation; an explicit `metrics().snapshot()` call creates the immutable
engineering view. Keeping the metrics implementation in a separate source file prevents the
executor's queue/lifecycle logic from being obscured by diagnostic state while still keeping
the metrics component-owned rather than introducing a second runtime model.

### SerialScheduledExecutor design

`SerialScheduledExecutor` is a separate Platform primitive for active objects that need one
serial lane plus delayed/periodic work. It is not a subclass of `SerialExecutor`.

Production Runtime owns one shared single-worker `ScheduledThreadPoolExecutor` for the
TagProcessor role. Each TagProcessor gets a logical `SerialScheduledExecutor` lane backed by
that worker. The lane provides:

- immediate serial execution for coalesced processing/control work;
- fixed-delay housekeeping serialized with that immediate work;
- cancellation of scheduled work;
- lane-local lifecycle/diagnostic state.

A periodic trigger does not execute TagProcessor state concurrently with immediate work: it
enters the same logical serial lane, and the next fixed-delay trigger is registered after
that lane execution completes. Closing or faulting one lane never shuts down the shared
TagProcessor role executor.

For Java 8 the shared scheduled worker enables `setRemoveOnCancelPolicy(true)` so cancelled
periodic triggers are removed promptly from the delayed queue. `SerialScheduledExecutor`
always receives an externally owned `ScheduledExecutorService`; tests that need a real
scheduler create and shut down that scheduler outside the lane.

TagProcessor owns its `ArrayBlockingQueue<TagObservation>` separately. Only coalesced queue
drain work, policy-control work and housekeeping enter its scheduled serial lane; there is no
executor task per observation.

`SerialScheduledExecutor` follows the same observability shape as `SerialExecutor`, with
measurement state in the separate `SerialScheduledExecutorMetrics` class.
`metrics().snapshot()` returns an immutable lane snapshot. These executor metrics describe
only work accepted and executed by the scheduled lane; observation ingress/drop metrics stay
owned by `TagProcessingMetrics`.

The execution types intentionally differ because their workloads differ:

```text
TimingNode
  -> SerialExecutor
       bounded command work queue
       result-bearing and admission-only commands

TagProcessor
  -> bounded TagObservation input queue
  -> SerialScheduledExecutor
       coalesced queue draining
       scheduled housekeeping
```

Both are JDK-backed baselines. `SerialScheduledExecutor` reuses a `SerialExecutor`
internally as its logical serialization lane; this does not add another physical worker.
The small lane-drain adapter exists only to preserve per-node bounded ordering on shared JDK
role workers; it does not replace JDK thread coordination or scheduling. More complex
worker-pool behaviour remains an optimization option only after V01 demonstrates a need.

### TimingData commit

The queue does not contain a pre-numbered TimingData record. Sequence is chosen
on the worker immediately before persistence:

```java
private void processRegistration(RegistrationInput input) {
    long sequence = logBook.nextSequence();

    TimingDataFactory.Context context =
        timingDataContext(sequence, activeLocationId, input.effectiveTime(), timeSource.now());

    RegistrationId registrationId = raceData.resolveRegistrationId(input);

    TimingData data;
    if (input.isAutomatic()) {
        data = timingDataFactory.createAutomaticRegistration(context, registrationId);
    } else {
        data = timingDataFactory.createManualRegistration(
                context, registrationId, input.timeSource());
    }

    timingDataStore.append(data);    // durable before return
    logBook.add(data);               // committed domain state
    timingDataCommittedEvent.emit(data);
}
```

Only the TimingNode worker calls this commit path, so a producer lock around
sequence allocation is unnecessary.

`LogBook.nextSequence()` reads committed state and does not consume the value.
If append fails, LogBook is unchanged and retry uses the same next sequence. The
worker must not process a later timing record ahead of that failed record.

### Passive LogBook and TimingNode-owned reads

`LogBook` has no worker thread. It stores immutable `TimingData` values,
but it is contained mutable TimingNode state rather than a globally readable
repository.

Code outside the TimingNode ownership boundary does not read the mutable
LogBook list directly. A consistency-sensitive query enters the TimingNode lane
and performs its bounded read in the same ordering as state changes.

The read representation is deliberately not fixed to a copied list. Bounded
IF-03 range/latest queries traverse the owned LogBook records on the TimingNode
lane and build only the final response representation; no temporary LogBook
`List` copy escapes the owner. Network
write/send remains outside the TimingNode lane.

For range/latest/ranking-style access, prefer direct bounded traversal of the
owned records when that avoids unnecessary allocation and GC pressure. A query may
instead use compact derived/indexed state, reusable scratch storage or a copied
view when measurements show that approach is cheaper overall.

The important guarantees are:

- each consistency-sensitive read has a defined place in the same ordering as
  state changes;
- no external consumer retains a mutable collection owned by TimingNode;
- long or blocking I/O work does not execute on the TimingNode lane;
- read strategy is selected from measured CPU, allocation/GC and lane-occupancy
  behaviour rather than convenience alone.

A high-frequency status/read path may use a worker-published immutable
snapshot when measurement justifies it. Such a published snapshot is an
explicit read model with known freshness semantics, not permission for callers
to read TimingNode-owned mutable objects directly.

### Per-type stores

Use a separate persistence boundary for each state type whose history/snapshots
need to be kept:

| Store | Purpose | Commit role |
| --- | --- | --- |
| `TimingDataPersistence` | append/load canonical TimingData | durable append is required before LogBook visibility; source for LogBook rebuild |
| per-type persistence components | preserve accepted analysis history/snapshots | do not make the lower storage layer own domain semantics |

The lower I/O layer exposes storage mechanics rather than domain-specific store
interfaces. The current Java persistence split is:

```text
Domain
  DefaultTimingDataPersistence
    - TimingDataCodec
    - TimingNodeId validation
    - sequence validation
           |
           v
I/O
  AppendOnlyRecordStore
           ^
           |
  FileAppendOnlyRecordStore
    - LF/CRLF framing
    - incomplete-tail repair
    - directory/file handling
    - FileChannel.force(true)
```

Runtime composition creates the file store and supplies it to
`DefaultTimingDataPersistence`. No class under `io.storage` imports a Domain
or Application class.

The TimingNode worker fixes the order in which state changes execute against the node-owned state. The
current design may call the small/infrequent analysis-store writes on the
same worker. If measurements show that one of those writes delays registrations,
the worker can hand an immutable snapshot to a bounded storage executor. Do not
add one thread per state object and do not introduce an unbounded background
queue.

For the registration path, synchronous persistence on the node lane remains the baseline:
producer callbacks return after command admission, while the shared TimingNode role worker
performs the durable append before LogBook/event visibility. Because that physical worker is
shared, a long `FileChannel.force(true)` can temporarily delay other TimingNode lanes as
well. That is an explicit trade-off for the resource-constrained baseline, not an assumption
that nodes execute in parallel.

Characterize store latency, per-lane queue high-water and fairness under the aggregate
20 registrations/s application workload before moving durability work off the shared node
worker. If the reference Raspberry Pi cannot meet the workload because durable storage
stalls the role worker, the next design step is a bounded durability mechanism that preserves
commit-before-LogBook/event ordering; it is not to multiply the stress target per node.

For example, a StageStartTimes update may be:

```text
TimingNode worker
  -> validate received snapshot
  -> replace StageStartTimes live state
  -> StageStartTimesStore.append(snapshot for analysis)
```

After a reboot, the live protocol can send the current StageStartTimes again
(for example as part of OPEN handling). The historical file is still retained
for analysis.

### Simple typed events

Local typed facts/notifications use the small `Event<T>` abstraction rather than a
central event bus. Examples include decoded antenna observations, post-commit TimingData
and tracked application-property changes. The reusable mechanism lives under
`platform.events` because it is a small JDK-only primitive rather than domain semantics,
external I/O or concrete infrastructure.

Conceptually:

```java
interface EventSource<T> {
    boolean subscribe(Consumer<T> listener);
}

final class Event<T> implements EventSource<T> {
    DeliveryReport emit(T value);
}
```

A component owns the mutable `Event<T>` instance and is the only code allowed to emit the
fact. Consumers receive an `EventSource<T>` view, so they can wire a listener without
gaining publication rights.

Event wiring is part of application composition:

```text
Runtime.create(...)
  -> construct components
  -> subscribe EventSource listeners
  -> wiring complete

Runtime.activate()
  -> components/workers become active
  -> runtime uses emit(...)
  -> no dynamic subscribe/unsubscribe rewiring
```

The event graph is therefore fixed before activation. `subscribe(...)` is a
composition-time operation and `EventSource` deliberately exposes no `unsubscribe(...)`
in the baseline. If a future requirement genuinely needs dynamic connection lifecycle,
that requirement must define its ownership and concurrency semantics rather than silently
turning every local event into a runtime-mutable graph.

`EventSource<T>` always has 0..N notification semantics. Callers do not choose a
single-listener or multi-listener event type. The implementation may optimize storage for
the common case:

```text
0 listeners  -> null / no listener container
1 listener   -> Consumer<T> directly
2+ listeners -> immutable Consumer[] in subscription order
```

That 0/1/N representation is only an allocation/memory optimization. It does not change the
public 0..N semantics.

For committed TimingData the component owns an explicitly named post-fact event:

```java
private final Event<TimingData> timingDataCommittedEvent = new Event<>();

public EventSource<TimingData> timingDataCommittedEvent() {
    return timingDataCommittedEvent;
}
```

The commit path is therefore:

```text
TimingNode serial lane
  -> persist TimingData
  -> update committed LogBook state
  -> timingDataCommittedEvent.emit(timingData)
       |
       +--> subscribed listener
       +--> subscribed listener
```

Delivery is synchronous on the emitting thread and `Event<T>` does not serialize
concurrent `emit(...)` calls. The completed listener graph is read-only during runtime.
An owner that requires ordered/non-overlapping callbacks emits from its own ordered
execution boundary; TimingNode status and committed-TimingData events therefore originate
from the TimingNode serial lane.

Ordinary listener RuntimeExceptions are isolated and reported in the delivery report so
one failing listener does not prevent later listeners from seeing the fact. Fatal Errors
are not swallowed.

Listeners must not become alternate owners of component mutable state. A listener must
also remain short and non-blocking. Slow network delivery, retry or persistence work hands
the immutable value to its own bounded mechanism and returns. A WebSocket or transport
adapter therefore never uses the TimingNode lane as its backpressure mechanism.

If listener notification fails after a TimingData record is committed, that does not roll
back the commit. A consumer that needs reliable recovery uses authoritative
persisted/LogBook state and its own recovery/delivery mechanism.

Tracked properties use the same event convention. A source event only calls
`signalChanged()` to invalidate the cached value. After rereading the authoritative
source, a real later value change is published through `changedEvent()`. The initial
value is returned explicitly by `initialize()` and is not fabricated as a change event.

Use `onXxx(...)` for listener/handler methods, for example
`onTimingNodeStateChanged(State state)`. Do not introduce a parallel callback
registration API such as `onChange(Consumer<T>)`, `addListener(...)` or
`setCallback(...)` when `EventSource.subscribe(...)` expresses the notification.

Other local events may use the same abstraction when a real consumer needs them. Do not
introduce events merely to replace an ordinary direct method call to one owned component.

### Multiple TimingNodes

The semantic requirement is one serial execution lane per TimingNode, not
permanently one operating-system thread per node.

The current realization is:

```text
1 TimingNode
  -> 1 SerialExecutor
       -> ThreadPoolExecutor(1 thread)
       -> bounded ArrayBlockingQueue
  -> passive state objects
  -> store dependencies
```

The semantic requirement remains one serial lane per TimingNode, not one particular executor
implementation forever. If later multi-node evidence shows that one JDK worker per node is
too expensive, a shared execution implementation may be evaluated only if it preserves the
same per-node ordering, bounded-admission and result semantics.

The cross-cutting bounded-resource, single-writer, immutability and
measurement-before-concurrency rules are owned by the SI-01 SSD. This SDD specifies the
Java realization only where a concrete component boundary requires it.

## Shared TimingData library and concrete profiles

:::{design} TimingData shared contract and profiles
:id: DD-TimingDataProfiles

Detailed Java design for the shared TimingData API, default profile,
factory/codec boundary and typed provider mechanism.
:::


Both SI-01 and the Development Client need common TimingData contracts without
depending on the whole SI-01 application core. The shared artifact therefore
owns the semantic interfaces and value types that every supported TimingData
profile must implement; it does **not** require one concrete record class for all
profiles.

The traced Java semantic model is intentionally small:

```text
shared/timing-data
  TimingData
    common TimingNodeId / sequence / LocationId / time access
    AutomaticRegistration
      RegistrationId
    ManualRegistration
      RegistrationId
      ManualTimeSource
    ManualTimeSource
    RecordKey
  LocationId
  RegistrationId
  TimingTimestamp
  TimingDataFactory
    Context
  TimingDataCodec
    CodecException
  TimingDataProvider

default profile
  DefaultTimingDataFactory
    private automatic/manual immutable implementations
  DefaultTimingDataCodec

test / product-specific profile
  DummyEventTimingDataFactory
    private profile-specific immutable implementations
  DummyEventTimingDataCodec
```

There is no intermediate public `RegistrationData` interface. Automatic and
manual registration are already the useful type-safe variants, so another level
would add hierarchy without giving callers a stronger contract.

`LocationId` and `RegistrationId` are standalone shared value types because
they are used at boundaries beyond one concrete TimingData subtype. They define
stable Java/IF-05 representations and only minimal structural validity. Concrete
event/profile/reference-data meaning and allowed values remain outside the shared
library.

Likewise, `TimingNodeStateData` and `RegistrationRevokedData` are not created
from old record-enum values. UC-002 still defers OPEN/CLOSE-as-TimingData and the
current use-case baseline does not require revocation. Add those semantic types
only after a promoted requirement justifies them.

The semantic interfaces are common. A configured profile supplies simple
immutable implementing classes:

```java
TimingData.AutomaticRegistration automatic =
        timingDataFactory.createAutomaticRegistration(context, registrationId);

TimingData.ManualRegistration manual =
        timingDataFactory.createManualRegistration(
                context, registrationId, TimingData.ManualTimeSource.OPERATOR_ENTERED);
```

The return types preserve variant type safety even when the configured provider
returns a different concrete implementation.

### Stateless TimingData factory

`TimingDataFactory` is a stateless construction service. It does not validate
TimingNode state policy, allocate sequence numbers, resolve `TagId` or
`TeamId`, commit data, own a LogBook or publish events. Those responsibilities
stay with the TimingNode and its contained domain components.

Source/reference resolution happens before TimingData factory construction. Stable event-profile relationships come from EventData while live per-node overrides may come from RaceData:

```text
TagId  ------> EventData --------\
                 + RaceData ------+--> RegistrationId
TeamId ---------------------------/
```

The factory receives the already selected common construction values in one
generic context and only the extra values required by the requested variant:

```java
TimingData.AutomaticRegistration createAutomaticRegistration(
        TimingDataFactory.Context context,
        RegistrationId registrationId);

TimingData.ManualRegistration createManualRegistration(
        TimingDataFactory.Context context,
        RegistrationId registrationId,
        TimingData.ManualTimeSource timeSource);
```

```text
TimingDataFactory.Context
  timingNodeId
  sequenceNumber
  locationId
  effectiveTime
  recordedAt
```

For the current manual variant, `TimingData.ManualTimeSource` is constrained to
`SYSTEM_ASSIGNED` or `OPERATOR_ENTERED`. Automatic registration uses observed
time by definition, so callers do not pass an `origin` or `OBSERVED` flag
merely to restate the return type.

The context contains values only. It does not contain `TimingNode`, `LogBook`,
stores, services or other mutable collaborators.

The design does not use an abstract TimingData base class.
Concrete immutable implementations may delegate to `TimingDataFactory.Context`.
Introduce a private/protected helper only when multiple real implementations show
enough repeated behaviour to justify it; such a helper remains implementation
reuse, not an additional public semantic layer.

### Provider boundary

A `TimingDataProvider` supplies a coherent family:

```text
TimingDataProvider
  stable provider/profile id
  TimingDataFactory
  TimingDataCodec
```

The factory creates the concrete in-memory TimingData objects. The codec
encodes/decodes the same profile family.
The built-in default/reference codec uses Jackson's streaming API only; JSON Lines
record framing, durable append and incomplete-tail recovery remain store responsibilities.
Provider discovery and configuration remain bootstrap/infrastructure concerns.

A `TimingDataCodec` is a **configured translator instance**. Its per-record API
remains deliberately small:

```java
byte[] encode(TimingData data)
TimingData decode(byte[] encodedRecord)
```

Do not add event date, time zone, deployment configuration or UI context to those
method calls. A provider that needs translation context receives and validates it
at provider/codec creation time, and the returned codec captures the resolved
immutable values it needs.

For example, a profile that serializes registration time as local time-of-day
may capture an event-date/day-selection rule and a `ZoneId` or fixed
`ZoneOffset`. If the profile cannot resolve a local time uniquely (for example
a daylight-saving overlap) or cannot represent the semantic instant within its
configured day scope, encode/decode fails according to that profile rather than
guessing from the host clock.

This translation context is distinct from `TimingDataFactory.Context`.
`TimingDataFactory.Context` contains semantic values of one record; provider
configuration explains how those values are represented externally.

The current `TimingDataProvider.createCodec()` shape does not force a
configuration mechanism by itself. When generic provider discovery/configuration
is implemented, bootstrap must construct or configure the provider before asking
it for a codec. If implementation evidence requires a typed provider
creation/configuration object, that type belongs at the provider/bootstrap
boundary, not in `TimingDataCodec.encode/decode`.

The provider therefore does more than representation translation, but it still
does not own TimingNode business rules. It chooses the concrete TimingData
implementation and its representation while preserving the common semantic
contracts defined by IF-05.

Both the Java-8 SI-01 runtime and Java-17 Development Client can depend on
`event-timing-data`. The Development Client may inspect the common interfaces
without depending on SI-01 Domain classes. Profile-specific inspection can be
added only where a real consumer needs it.

The current design keeps the default/reference profile inside the shared
TimingData library while the design is still changing; do not create another
production Maven artifact solely to mirror the conceptual profile split. A dummy
event-specific implementation in tests is sufficient to prove that the common
contract does not accidentally depend on the default concrete classes. A
separate provider artifact becomes justified when a real independently deployed
profile exists.

This artifact contains no SI-01 runtime/application classes and no JavaFX code.
Its Java API must remain usable from both the Java-8 SI-01 baseline and the
Java-17 Development Client.

## Derived consumers

The application core is deliberately not tied to one executable topology. Plausible consumers include:

```text
single-system application
multi-system / simulation application
public reference/test application
private/product application
```

These are consumer possibilities, not modules to create now.

## Java 8 extension/provider mechanism

A concrete public/private extension requirement now exists, so provider discovery
is no longer merely an optional capability. Keep the mechanism narrow and
composition-oriented.

The first V04 implementation slice covers only `EventDataProvider` and
`TimingDataProvider`:

```text
IF-11 provider ids
        |
        v
runtime.TimingApplicationRuntime.create(...)
        |
        v
infra.extension.ExtensionRegistry
        |
        +--> built-in EventDataProvider("reference")
        +--> built-in TimingDataProvider("reference")
        +--> ServiceLoader external EventDataProvider(s)
        +--> ServiceLoader external TimingDataProvider(s)
        |
        v
resolve configured ids
        |
        +--> EventData
        +--> TimingDataFactory + TimingDataCodec
        |
        v
normal application composition
```

`infra.extension.ExtensionRegistry` owns only typed provider registration,
duplicate-id detection, discovery from a supplied `ClassLoader` and lookup by
stable provider ID. It is not a generic `Plugin` API and it does not know
TimingNode/Application behaviour.

The public built-in EventData and TimingData providers both use the IF-11 stable
ID `reference`. TimingData therefore has a concrete
`DefaultTimingDataProvider` beside the existing default factory/codec.

For the Java 8 baseline, an external provider JAR uses normal
`META-INF/services` metadata. A caller may create a dedicated
`URLClassLoader` for one or more provider JARs and pass that loader to
`ExtensionRegistry`; the registry then uses standard `ServiceLoader`.
The registry does not choose a filesystem extension directory, scan arbitrary
folders, own hot reload/unload or own class-loader lifecycle. The exact
external-JAR directory/layout and dependency-isolation policy therefore remain
separate/open deployment decisions.

The current single-TimingSystem runtime configuration carries
`eventDataProvider` and `timingDataProvider` selections. The reference IDs
remain the compiled/default profile values when a deployment does not override
them. Runtime resolves both provider IDs before creating TimingData persistence
or the TimingNode. Unknown configured IDs and duplicate IDs within one provider
family fail before normal composition rather than silently falling back.

A synthetic V04 test creates an external provider JAR and a dedicated
`URLClassLoader` to prove that `ServiceLoader` discovery works outside the
built-in class set.

Provider contracts belong with the capability whose meaning they create;
class-loader/discovery mechanics belong under application-core Infrastructure
support. Domain, Application and I/O component code must not depend on
`URLClassLoader`, `ServiceLoader` or a generic extension interface.

Later slices may register typed `UpstreamProtocolProvider`,
`AntennaProvider`, `CanProtocolProvider` and
`DisplayProtocolProvider` families in the same registry pattern when those
capabilities are implemented. They are intentionally not created as empty
families in the first EventData/TimingData slice.

IF-11 selects providers by stable provider ID. Missing providers, duplicate IDs
or an incompatible provider/configuration combination fail during validation or
startup rather than silently falling back to another implementation.

Whether the provider contracts eventually justify a separately versioned SPI
artifact remains implementation/evidence-driven.

## Public/private composition

Expected private/product-specific areas may include:

- production RFID control/protocol details;
- product-specific I/O/protocol implementations;
- production asset/source inventory and mappings;
- production upstream/backoffice schemas/codecs where sensitive;
- deployment-specific composition/policies.

Prefer normal composition and constructor/factory injection. Do not introduce a subclass-based `BaseApplication` extension model. The provider mechanism above is the explicit runtime-extension boundary; do not generalise it into arbitrary plugin access from domain/application code.

## Artifact extraction criteria

Create additional artifacts only when a real boundary requires them. Candidate extractions include:

- RabbitMQ/messaging I/O;
- Linux/Raspberry-Pi platform support;
- public/private RFID/CAN I/O implementations;
- separately versioning `event-timing-data` if binary compatibility/release evidence requires an independent release cycle;
- reusable test support.

Extraction is preferred over speculative libraries: keep package/responsibility boundaries clean enough that a proven boundary can be split without redesign.

## Architecture/dependency checks

Useful automated rules may include:

- presentation packages do not own or persist application state;
- domain services do not reference presentation or concrete I/O classes;
- platform packages do not depend on event-timing application/domain behaviour;
- wire/protocol classes stay with their presentation or I/O capability;
- semantic contracts are not moved into transport packages merely because transport code uses them;
- public code contains no real deployment mappings or proprietary values;
- domain/application/runtime components do not depend on extension class-loader mechanics;
- duplicate provider IDs and unknown configured provider IDs fail deterministically;
- the executable consumes `timing-point-core` rather than copying/forking application-core source;
- the core artifact does not carry a concrete SLF4J provider/backend transitively;
- an executable runtime contains exactly one intended SLF4J provider.

## Open detailed-design decisions

- exact package granularity after real application/domain classes exist;
- final package naming where capability-oriented packages prove clearer than layer names;
- exact reusable boundary between single-instance runtime mechanics and multi-system application orchestration;
- exact bounded TimingNode work-queue capacity and queue-full operational policy after Raspberry-Pi burst/latency measurement;
- exact guard timeout for synchronous TimingNode operations and how it is configured/exposed diagnostically;
- concrete immutable TimingNode read-view representation and compact LogBook indexing required by the ranking/query implementation;
- exact antenna automatic-recovery trigger, retry/backoff, retry-limit and terminal-failure policy;
- exact external extension-JAR directory/layout and dependency-isolation policy;
- private Maven artifact publication/consumption mechanism;
- version alignment between public core/provider contracts and private implementations;
- which I/O capabilities eventually deserve independent artifacts;
- whether and when provider contracts deserve a dedicated independently versioned SPI artifact;
- exact field logging configuration/rotation/retention policy in the default executable.

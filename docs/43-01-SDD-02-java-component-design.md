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

infra/
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
    TimeSource.java                     per-system absolute time / test control
  timing/
    TimingNode.java
    TimingNodeId.java
    UpstreamMessagePort.java            TimingNode-level upstream messages
    NextUpTeams.java                    passive per-node state
    NextUpTeamsStore.java               persistence port for next-up analysis history
    StageStartTimes.java                passive per-node reference state
    StageStartTimesStore.java           persistence port for start-time analysis history
    RaceData.java                       passive per-node reference state
    RaceDataStore.java                  persistence port for race/reference analysis history
    TagProcessor.java                   node-local tag filtering/mapping policy
    TagRegistrationMapper.java          DecryptedTagId -> RegistrationId policy boundary
    TagProcessingPolicy.java            compiled defaults + active tag-processing policy
  logbook/
    LogBook.java                        passive committed TimingData history
  timingdata/
    TimingDataPersistence.java          TimingData-specific persistence contract
    DefaultTimingDataPersistence.java   TimingData codec/identity/sequence mapping
  upstream/
    UpstreamProtocol.java               TimingData + sync/reconcile/ping semantics
    UpstreamProtocolProvider.java       typed extension provider contract

io/
  devices/
    antenna/
      Antenna.java                      stable device/lifecycle + tag-observed event contract
      AntennaId.java                    configured software identity of one antenna
      AntennaManager.java               execution/lifecycle boundary for 1..N antennas
      AntennaManagerLogic.java          package-private antenna/power/multiplex state logic
      AntennaManagerTypes.java          manager lifecycle/status/failure value types
      AntennaInstallation.java          AntennaId + package-local antenna/power installation binding
      AntennaProvider.java              typed extension provider contract
      AntennaPowerControl.java          optional external power-switch capability
      SimulatedAntennaPowerControl.java deterministic simulated external power channel
      AntennaInfo.java                  hello/identity/version probe result
      DecryptedTagId.java               provider-decoded/decrypted source identity
      TagObservation.java               DecryptedTagId + RSSI + TimingTimestamp fact
      SimulatedAntenna.java             built-in reference/simulation implementation
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
    SerialScheduledExecutor.java           serial lane + fixed-delay scheduling
    SerialScheduledExecutorMetrics.java    scheduled-lane measurements
  events/
    Event.java                            owner-side typed emit primitive
    EventSource.java                      subscription-only consumer view
  environment/                            low-level environment adapters only when real types justify them
```

The names above record ownership/direction, not a requirement to create empty
types early. Lower layers expose generic contracts that do not import higher
layers. TimingData-specific persistence semantics stay in Domain and use the
generic `io.storage.AppendOnlyRecordStore`; the file implementation remains
completely unaware of TimingData, TimingNode and Domain types.
`SerialExecutor` is the project execution primitive used by TimingNode. Each
TimingNode owns one bounded FIFO lane with its own `ArrayBlockingQueue`, admission state and
lane-local metrics. **The lane is not the physical worker.** Production Runtime supplies one
shared single-worker `ThreadPoolExecutor` for the TimingNode role and all TimingNode lanes
schedule short drain tokens onto that shared worker. `SerialExecutor` receives that worker
as an external `Executor` dependency; it never creates, configures or shuts down the
physical worker. Tests that need asynchronous execution create and own their test worker
separately, while deterministic package-local seams may use direct execution.

`SerialScheduledExecutor` is the corresponding serial scheduling capability used by
TagProcessor. Each TagProcessor keeps its own bounded observation queue and logical serial
scheduled lane, while production Runtime supplies one shared single-worker
`ScheduledThreadPoolExecutor` for the TagProcessor role. Scheduled housekeeping and
coalesced immediate work are serialized per TagProcessor without allocating a physical
worker per processor.

**Runtime composition constructs and owns the physical role workers centrally, then creates
logical lanes over those workers.** TimingNode and TagProcessor do not choose production
thread names or create hidden production threads. Runtime gives one logical
`SerialExecutor` and one logical `SerialScheduledExecutor` to each composed TimingNode,
but all nodes share the corresponding role worker. TimingNode owns the lifecycle of its
node-local logical lanes together with its child TagProcessor; closing a lane never shuts
down the supplied physical worker. Runtime retains physical-worker shutdown ownership.
Shared blocking-I/O executors remain Runtime-owned and separate from both Domain role
workers.

The central construction point deliberately leaves Java thread priority at the JVM
default. Correctness and forward progress do not depend on priority. A role-specific
priority change remains a measurement-driven tuning option and must be requalified on the
target JVM/OS.

These project types exist to make execution ownership and application semantics explicit.
They are not justification for reimplementing JDK executor internals. A lower-level custom
worker/scheduler requires Step-5 measurement evidence.

`TimingNode` remains the visible Domain component boundary used by higher layers. It owns
serialized access through the injected `SerialExecutor`, operation admission/timeout
mapping and post-commit event publication. It also creates and owns its node-local
`TagProcessor` child from injected mapping/configuration and the Runtime-supplied
`SerialScheduledExecutor`. Package-private `TimingNodeLogic` contains the mutable node
state and domain decisions: lifecycle, current `LocationId`, LogBook interaction and
TimingData commit behaviour. `TimingNodeLogic` is an implementation detail of the
TimingNode component, not a second architecture component.

A production `TimingNode` is always constructed as a complete capability.
`TimingDataPersistence`, `TimingDataFactory`, `TimeSource`, tag-processing
configuration/mapping and both execution lanes are constructor dependencies; there is no
lifecycle-only or partially configured production node. The only non-public construction
seam exists for deterministic TimingNode execution-boundary tests and is documented as
test-only in code.

`TimingNodeTypes` is only a Java source-code grouping for the public TimingNode status/result/exception value types. It has no runtime state, lifecycle or architectural responsibility and therefore does not appear as another component in Figure SI01-01.

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

Each `TimingSystem` owns one Domain `TimeSource`. The production implementation
may delegate to a Platform wall-clock abstraction; tests/simulations may provide
a controllable implementation with a per-system offset or stepped time. The
Domain contract returns project-owned absolute `TimingTimestamp` values rather
than exposing a platform clock API directly. Monotonic duration/time-out sources
remain separate Platform/runtime concerns.

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

`UpstreamProtocol` is a Domain capability owned by one `TimingSystem` and built partly on `TimingData`. It adds synchronization/reconciliation and protocol-level messages such as ping/pong so individual TimingNodes do not need to implement those concerns. `UpstreamGateway` owns the external transport boundary and uses 1..N concrete connectors. A connector such as `RabbitMqConnector` or `DebugConnector` owns transport/session mechanics, not TimingData or UpstreamProtocol semantics. `DebugConnector` is the engineering transport intended for an independent desktop/debug tool; that tool remains an external consumer rather than part of SI-01. `UpstreamMessageRouter` resolves semantic work inside the already selected TimingSystem context: system-level work uses `TimingSystem.UpstreamMessagePort`, while node-level work is resolved by `TimingNodeId` to `TimingNode.UpstreamMessagePort`. `TimingSystemId` is not required on the wire.

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
  domain model, semantic ports, per-TimingSystem TimeSource, TimingData representation/codec and UpstreamProtocol semantics

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
- the executable application chooses and configures the provider/backend before `runtime.TimingApplication.create(...)` starts normal application composition;
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
    TimingApplication.java
    RuntimeExecutors.java
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
`TimingApplication`, execution-resource construction and the effective composition
configuration. Figure SI01-01 shows this explicitly as the **Runtime** block.
Runtime is not another business/domain layer; it is where the executable object graph is
assembled.

The executable composition must remain readable as one linear construct-wire-start flow.
`runtime.TimingApplication.create(...)` is the single concrete composition root and the
returned `TimingApplication` owns the lifecycle of that already composed graph. A second
bootstrap/builder/composition class must not hide the object graph. Small private helpers may format repetitive local
construction, but cross-component relationships and lifecycle order remain visible in
`TimingApplication.create(...)`. The visible composition order is:

```text
validated Config
  -> PlatformEnvironment
  -> RuntimeExecutors/resources
  -> Domain + I/O + Application objects
  -> explicit Conductor/event wiring
  -> RuntimeExecutors.start()
  -> component start
  -> Presentation endpoint start
```

`application.Conductor` owns application-wide coordination between already constructed
components. Runtime creates and wires the Conductor but does not reimplement that
coordination in component constructors or anonymous hidden wiring callbacks.
`RuntimeExecutors` construction allocates executor objects only; physical worker startup
is an explicit lifecycle action. Shutdown unwinds started resources in reverse ownership
order.

Cross-component event wiring is visible at the composition point. The antenna manager owns
the concrete `Antenna` instances; it does not expose those device objects for callers to
walk. Composition addresses a configured source by `AntennaId` and subscribes the target
to the manager's subscription-only event source, conceptually:

```java
antennaManager.tagObservedEvent(antennaId)
        .subscribe(timingNode.tagProcessor()::onTagObserved);

timingNode.statusChangedEvent()
        .subscribe(conductor::onTimingNodeStatusChanged);
```

For semantic local events, accessor names describe the fact that happened and end in
`Event`, matching existing names such as `statusChangedEvent()` and
`timingDataCommittedEvent()`. The antenna APIs therefore use
`tagObservedEvent()` / `tagObservedEvent(AntennaId)`; a plural collection-like name such
as `observations()` is not used for an `EventSource`. `TagObservation` remains the
immutable event value and does not need an `AntennaId` field merely for routing because
the configured source identity is already known at the subscription point.

`runtime.simulator.SimulationRuntime` is an explicit simulator composition entry point.
It selects simulated installations/mappings through the same `TimingApplication.create(...)`
path; it
does not introduce a simulated domain path or bypass TagProcessor/TimingNode.

The running application's configuration is not the same object as the startup YAML/runtime mapper DTO. Runtime owns the concrete `ApplicationConfiguration` tree because that tree describes the composed executable and its current effective settings. Infrastructure owns the reusable typed configuration-value mechanics. the Application layer owns the configuration query/update use-cases over that runtime tree and exposes only a narrow control interface toward Presentation. Domain, Presentation and I/O consumers do not receive writable access to the runtime tree merely because they need one configured value.

The executable artifact remains deliberately thin. Its launcher/input adapter stays under `...eventtiming.app`; reusable logging remains Infrastructure support. The IF-11 YAML mapper stays with `runtime.config` because it knows the concrete runtime configuration schema.

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

  io.github.brainboxemb.eventtiming.timingpoint.runtime/
    TimingApplication.java
    Lifecycle.java
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
  -> core runtime.TimingApplication.create(...)
       -> create PlatformEnvironment
       -> construct runtime resources and reusable application/domain/I/O objects
       -> construct and wire application.Conductor
       -> return composed TimingApplication
  -> TimingApplication.start()
       -> explicitly start execution resources and components
  -> executable starts presentation endpoints and shutdown handling
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

The application core uses one explicit runtime composition boundary. There is no builder layered on top of another bootstrap object. `runtime.TimingApplication.create(...)` constructs and wires the current graph; the returned `runtime.TimingApplication` owns start/stop lifecycle.

### Running configuration model

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
- `runtime.TimingApplication.create(...)` consumes only the resolved/validated runtime `Config` and contains no profile-name switches.

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
quit
exit
```

These are Presentation commands, not a second Domain/Application semantic contract.
`open`, `close` and `auto-reg` delegate to `TimingNodeProxy`; configuration
commands delegate to `ConfigurationControl`. LocalConsole and RemoteShell therefore
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

The Java antenna boundary separates device lifecycle from decoded observation processing.

### Antenna and manager

`Antenna` represents one configured logical antenna capability. It owns its decoded
observation event and the provider-specific device/session mechanics needed for probing,
initialization and inventory control.

Illustrative shape:

```java
interface Antenna extends AutoCloseable {
    AntennaInfo probe();

    void initialize();

    void startInventory();

    void stopInventory();

    boolean inventoryRunning();

    EventSource<TagObservation> observations();
}
```

The exact checked/runtime exception family remains capability-specific; the important
contract is that probe and normal inventory are different lifecycle operations.

`probe()` is a one-shot health/compatibility operation. It opens/starts the provider as
needed, performs the provider's hello/identity/version exchange and returns the decoded
`AntennaInfo`. The provider is not left inventorying after a probe.

Normal operation uses `initialize()` followed by explicit
`startInventory()/stopInventory()`. Closing the antenna stops delivery and releases the
provider/device resources.

`AntennaManager` owns the configured set of 1..N antennas for one TimingSystem and
the installation-level lifecycle around them. It coordinates independent startup health
checks, normal initialize/shutdown, optional injected power control, per-antenna health
and per-antenna inventory state. One provider failure is contained to that antenna; the
manager does not roll back independently healthy antennas merely because another antenna
fails.

At application startup the manager performs a non-inventory sanity sequence for every
configured antenna:

```text
optional power ON
        |
        v
configured stabilization delay
        |
        v
one-shot probe / identity-health check
        |
        v
optional power OFF
```

Failure of one sequence records that antenna as unavailable/error and the manager continues
with the remaining configured antennas.

Normal antenna operation is driven by the lifecycle of the TimingNodes mapped to each
antenna. When at least one assigned TimingNode is OPEN, a healthy antenna is powered when
required, allowed to stabilize, initialized and made available for inventory. When no
assigned TimingNode remains OPEN, inventory is stopped and externally controlled power is
removed. An antenna mapped to several TimingNodes therefore remains active until the last
mapped TimingNode closes.

The manager tracks per-antenna state separately from its aggregate health. Aggregate
health may be degraded while healthy antennas remain operational.

The manager serializes its lifecycle operations through the project-wide
`SerialExecutor` primitive on top of the shared bounded I/O `ExecutorService`:

```text
                    shared bounded I/O ExecutorService
                    /              |               \
                   /               |                \
      SerialExecutor A      SerialExecutor B      other blocking I/O
      manager A lane         manager B lane         capability work
             |                     |
             v                     v
      AntennaManager A      AntennaManager B
             |                     |
             v                     v
       provider A calls      provider B calls
```

The per-manager `SerialExecutor` is a logical ordering boundary, not a dedicated Java
thread. AntennaManager does not implement another private queue/drain executor. Runtime
constructs the lane on the shared I/O worker; the manager owns its lane lifecycle while
Runtime owns the physical worker lifecycle. At most one lifecycle operation for one
manager executes at a time, while unrelated managers/capabilities may make progress on
other I/O workers.

The shared executor itself is bounded and owned by runtime composition. It is not used by
TagProcessor or the TimingNode worker. Result-bearing provider operations retain explicit
timeouts/cancellation policy so a stuck reader does not consume executor capacity
indefinitely. Lane admission failure remains visible rather than falling back to an
unbounded queue.

Startup/runtime callers use result-bearing manager operations when they must know whether
a probe/initialize/control transition succeeded. TimingNode/device observation processing
does not synchronously wait for manager control work.

External power switching is optional. When deployment hardware exposes it, composition
supplies an `AntennaPowerControl` capability to the manager so the manager can order
power-on before probe/initialize and power-off after close. An antenna provider that owns
its power mechanism internally may omit that external capability; the generic
`Antenna` contract does not pretend every reader has a separately switchable supply.

`AntennaPowerControl` is deliberately separate from `Antenna`. A physical reader may be
powered through a relay board, GPIO-controlled supply or another installation component
that is unrelated to the reader's vendor protocol. The per-antenna installation
configuration therefore binds an optional power-control capability and a power
stabilization interval to the antenna. Provider-owned power remains possible by omitting
the external capability.

One AntennaManager supports zero or one inventory mutual-exclusion group. The manager may
still own 1..N antennas; antennas outside the optional group operate independently. When
the group is present it contains 2..N configured antennas that share RF/device constraints
forbidding simultaneous inventory. AntennaManager owns the multiplex policy for that one
group: at most one healthy member inventories at a time, the active member rotates at the
configured interval, and a failed member is skipped without stopping healthy members. The
public/reference baseline is the known two-antenna installation with a 500 ms interval.

The Java implementation keeps the public manager boundary small. `AntennaManagerTypes`
owns lifecycle/status/failure value types, while package-private `AntennaManagerLogic`
owns mutable per-antenna state, power transitions and the single-group rotation rules.
This split is justified by the manager's current size; it is not a generic command/query
framework. Public manager operations remain start/close, synchronous or non-blocking
operational transition, and status queries.

The built-in `SimulatedAntenna` path must model the same lifecycle contract. Simulation
includes explicit powered/unpowered state when paired with simulated power control,
initialization/inventory preconditions and controllable probe/initialize/start failures so
startup containment and degraded/multiplex behaviour can be verified without hardware.

### TagObservation and local event delivery

`TagObservation` is an immutable decoded input fact:

```java
final class TagObservation {
    DecryptedTagId tagId();
    int rssi();
    TimingTimestamp observedAt();
}
```

`DecryptedTagId` is the provider-decoded/decrypted tag identity exposed to TagProcessor.
Vendor protocol bytes, framing, encryption and decryption mechanics do not escape the
antenna/provider boundary. RSSI is the decoded/normalized signal-strength value
used by the configured SI-01 filter policy.

The timestamp is attached at the earliest accepted decoded-observation point. It becomes
the automatic registration effective time if the decrypted tag maps successfully, the
resulting RegistrationId passage passes filtering and the command is admitted. TagProcessor does not replace it with a later processing/commit timestamp.

Each antenna owns:

```java
private final Event<TagObservation> observationEvent = new Event<>();

public EventSource<TagObservation> observations() {
    return observationEvent;
}
```

The provider emits synchronously on its callback/device thread. This deliberately reuses
the project-wide `Event<T>/EventSource<T>` primitive instead of introducing an
Antenna-specific listener registry. Runtime composition subscribes the relevant
TagProcessor to the configured antenna event sources.

Multiple antenna providers may call their events concurrently. TagProcessor handles that
concurrency only at its bounded observation-input queue: each provider callback performs
non-blocking ingress and returns. Mapping, passage filtering, duplicate filtering,
housekeeping and runtime policy replacement execute on TagProcessor's one serial scheduled
lane. Runtime constructs that `SerialScheduledExecutor` centrally; TimingNode creates and
owns the TagProcessor child that uses it. Passive filter state therefore remains
single-lane and requires no additional locks.

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

The node-local tag-processing path is split by responsibility:

```text
TagProcessor
  -> TagRegistrationMapper
  -> RegistrationDuplicateFilter
  -> TagObservationFilter
  -> TimingNode.offer(...)

TagProcessor
  -> bounded TagObservation input queue
  -> SerialScheduledExecutor
       -> queue-drain work
       -> scheduled housekeeping on the same serial lane

TagProcessingMetrics
  -> owns the low-allocation processing counters
```

`TagProcessor.onTagObserved(...)` is the Antenna EventSource callback. The antenna has
already decoded/decrypted the provider data into a `DecryptedTagId`. The callback only
attempts bounded admission of the immutable observation to TagProcessor's serial execution
lane and then returns. It does not map, filter or offer TimingNode work on the
antenna/provider callback thread.

TagProcessor is an active object. It owns the serial execution lane used for all processing
of admitted observations and for its scheduled housekeeping. On that lane it maps
`DecryptedTagId` to `RegistrationId`, rejects unmapped observations, suppresses a
RegistrationId while it remains inside the duplicate window of a previously accepted
TimingNode offer, updates passage state only for registrations that still need passage
processing, and performs the non-blocking `TimingNode.offer(...)` handoff to the
lower-priority TimingNode lane.

Duplicate suppression is registration-based rather than raw-tag-based, so mapping remains
before the duplicate check. A RegistrationId enters the duplicate window only after
`TimingNode.offer(...)` returns `ACCEPTED`; `FULL` and `NOT_RUNNING` do not suppress
later observations. This avoids maintaining burst/RSSI/housekeeping state that cannot
produce usable work while preserving retry opportunity after rejected TimingNode admission.

Because all TagProcessor-owned mutable processing state is touched only on this one lane,
`TagObservationFilter` and `RegistrationDuplicateFilter` remain passive state objects and
do not need their own thread, scheduler, lifecycle or locking. The duplicate filter exposes
the two distinct moments explicitly: check whether a RegistrationId is currently suppressed,
and record it only after an accepted TimingNode offer.

#### Observation burst aggregation

A high-rate reader can report the same participant many times during one physical passage,
and one participant may have multiple decrypted tags that map to the same
`RegistrationId`. Passage aggregation therefore happens on the resolved
`RegistrationId`, not on the source tag identity.

Do not schedule/cancel a Java `TimerTask` for every observation and do not retain a
`List<TagObservation>` merely to choose the strongest read. Keep only the state needed
to determine passage expiry and the strongest observation.

Keep one small mutable `BurstState` per currently active `RegistrationId`:

```java
final class BurstState {
    long firstSeenNanos;
    long lastSeenNanos;
    int maxRssi;
    TimingTimestamp maxRssiObservedAt;
}
```

On each observation:

1. create the state when the `RegistrationId` has no open burst;
2. update `lastSeenNanos`;
3. replace `maxRssi` and `maxRssiObservedAt` only when the new RSSI is strictly
   greater, so equal maxima keep the earlier observation.

A burst closes when either condition becomes true:

```text
now - lastSeen >= quietTimeout
OR
now - firstSeen >= maxBurstDuration
```

The quiet-time rule is essential: if no further observation arrives, expiry still closes
the burst and immediately continues with duplicate filtering/admission. Registration
therefore does not wait for a later tag callback.

The maximum-duration rule prevents a continuously visible tag from keeping one burst open
forever. After forced closure, a later observation opens a new burst; the
registration-level duplicate window prevents an already accepted RegistrationId from
producing another registration inside its longer duplicate window.

The selected candidate is the strongest observation in the burst and retains that
observation's original `TimingTimestamp`.

Do not pre-filter observations on RSSI. The burst exists to find the maximum RSSI across
the complete passage.

The timestamp of the maximum-RSSI observation becomes the automatic-registration
effective time. This intentionally targets the participant's closest observed approach to
the antenna rather than the earliest possible read.

D04 defines no minimum-RSSI rejection threshold. RSSI is used for strongest-observation
selection only. A future rejection/filter rule requires separate requirement/design
authority.

Timing deadlines use `MonotonicClock`; they do not use `Date`,
`System.currentTimeMillis()` or the potentially corrected observation timestamp.

#### Burst expiry and scheduled serial work

Quiet-time expiry must still happen when no new observation arrives. The same serial lane
that processes admitted observations therefore also supports delayed/scheduled work.

The execution model is:

```text
antenna/provider callback
  -> TagProcessor.onObservation(observation)
       -> bounded inputQueue.offer(observation)
       -> return

TagProcessor execution lane
  -> drain/process queued observations
       -> map
       -> passage update
       -> duplicate/admission processing
  -> scheduled housekeeping
       -> passage expiry
       -> duplicate cleanup
```

Scheduled housekeeping is not executed on a second TagProcessor-specific worker thread.
A due sweep enters the same **logical TagProcessor serial lane** as observation-drain and
policy-change work. Production Runtime provides one shared scheduled role worker for all
TagProcessor lanes.

TagProcessor separates ingress buffering from execution:

- one bounded input queue per TagProcessor stores accepted `TagObservation` values;
- one logical serial lane per TagProcessor drains/processes that queue;
- all TagProcessor lanes share the Runtime-owned physical scheduled worker;
- scheduled housekeeping enters the same node-local lane as observation work.

The input queue is not the shared role executor's work queue. The antenna callback only
performs `inputQueue.offer(observation)` and returns. This keeps provider/event delivery
independent from mapping/filtering execution and avoids creating one executor task object per
observation.

Drain work is coalesced. One drain invocation processes the queue depth captured when that
drain begins; observations arriving during that batch cause a later drain token rather than
extending the current invocation indefinitely. The queue bound therefore limits one batch,
and task-boundary resubmission gives already-waiting sibling TagProcessor lanes and
housekeeping work an opportunity to run on the shared worker.

The baseline Java execution mechanism uses one Runtime-owned single-thread
`ScheduledThreadPoolExecutor` for the TagProcessor role plus lane-local serial admission.
The exact wake-up/coalescing strategy is Platform execution detail, but it must avoid
periodic polling latency when observations arrive and must avoid one scheduled/executor task
per observation.

The JDK executor's scheduling/thread coordination remains the default implementation. Do not
replace it with a custom timer heap, wait/notify loop or per-processor worker thread unless
Step-5 runtime characterization shows a material CPU, allocation, latency or memory reason.

For the Java-8 baseline, the shared `ScheduledThreadPoolExecutor` uses
`setRemoveOnCancelPolicy(true)` so cancelled housekeeping triggers are removed promptly.
The logical fixed-delay registration is implemented so its next trigger is scheduled only
after the previous housekeeping execution has completed on that TagProcessor lane. Ordinary
runtime failures are contained/reported and do not silently disable unrelated processor
lanes.

The bounded TagProcessor input queue provides the explicit observation-overload boundary. A
full queue drops/rejects that incoming observation according to the defined FULL policy; it
does not consume role-worker queue capacity. Sustained observation ingress must still not
indefinitely starve due housekeeping or sibling processor lanes.

TagProcessor keeps at most one logical housekeeping registration. When time-based processing
state changes from empty to non-empty, it registers fixed-delay housekeeping at the
configured sweep cadence. When no open passage or duplicate-window state remains,
TagProcessor cancels that registration. A later transition from empty to non-empty starts one
new logical registration.

This avoids both extremes:
- there is no timer/scheduled task per observation;
- there is no permanently running housekeeping registration while TagProcessor has no timed
  state;
- there is no dedicated Java worker thread per TagProcessor.

The timed state includes open passage state and any duplicate-window state that still needs
housekeeping. Passive components may expose a small state query such as `isEmpty()` /
`hasPendingState()`; they do not schedule themselves.

The execution capability uses monotonic elapsed time for scheduled deadlines. Observation
timestamps are not used for execution scheduling. The JDK executor implementation remains
subject to V01 measurement; custom lower-level execution is an optimization option, not the
baseline design.

The previous separate `PeriodicExecutor` / `PeriodicTask` TagProcessor mechanism is not
part of this design. `runtime.TimingApplication.create(...)` constructs and wires the worker and processor;
TagProcessor owns the worker lifecycle.

`TagProcessor.start()` starts its serial execution lane. Shutdown first stops antenna inventory and
unsubscribes `TagProcessor.onTagObserved`, then stops TagProcessor so no new ingress is
accepted. Accepted observation work follows the worker drain policy; future scheduled sweeps
are cancelled. Shutdown does not force-close a passage that has not reached its normal
quiet/max-duration condition.

The bounded observation ingress introduces an explicit overload outcome. FULL or
NOT_RUNNING admission must be observable through engineering counters/worker state and must
not block the antenna/provider callback.

#### Registration filtering and admission

Mapping precedes passage aggregation:

```text
TagObservation(DecryptedTagId, RSSI, observedAt)
  |
  +--> TagRegistrationMapper
          |
          +--> no RegistrationId ----------------------> unmapped
          |
          +--> RegistrationDuplicateFilter ------------> duplicate
          |
          +--> TagObservationFilter
                  keyed by RegistrationId
                  strongest RSSI / selected observedAt
                  |
                  +--> TimingNode.offer(addAutomaticRegistration)
                          |
                          +--> ACCEPTED -> record duplicate window
                          +--> FULL     -> do not suppress retry
                          +--> NOT_RUNNING -> do not suppress retry
```

The passage filter and the longer registration duplicate window are both keyed by
`RegistrationId`, but they solve different problems. The duplicate window is checked
first, after tag-to-registration mapping: a recently admitted RegistrationId bypasses
passage aggregation entirely. For registrations that are still eligible, passage filtering
combines repeated reads, including reads from different decrypted tags for the same
registration, into one strongest-RSSI passage.

`TimingNode.offer(...)` is a bounded fire-and-forget handoff. It only reports immediate
admission to the lower-priority TimingNode queue; it never waits for TimingNode processing.
Record duplicate-window state only when that offer returns `ACCEPTED`. `FULL` and
`NOT_RUNNING` therefore do not prevent a later observation from retrying.

The processor owns its bounded observation input queue and receives one serial scheduled
execution capability for processing and housekeeping:

```java
TagProcessor(
    TimingNode timingNode,
    TagRegistrationMapper mapper,
    TagProcessingPolicy policy,
    MonotonicClock monotonicClock,
    TagProcessingMetrics counters,
    SerialScheduledExecutor executor)
```

`SerialScheduledExecutor` is a narrow project execution contract, not a requirement for a
hand-written worker implementation. Its default implementation is JDK-backed. The contract
exists to keep component code independent from JDK rejection/cancellation details and to
expose the application's bounded-admission and measurement semantics consistently.

Runtime/engineering composition retains the same `TagProcessingMetrics` instance when
it needs pull-based measurements. TagProcessor owns the supplied execution capability
lifecycle; supplying it does not make `runtime.TimingApplication.create(...)` the execution model.

`TagProcessingPolicy` owns at least:

- burst quiet timeout;
- maximum burst duration;
- registration duplicate window;
- sweep cadence;
- bounded observation input-queue capacity.

The reusable `TagProcessingPolicy` owns usable compiled defaults so TagProcessor can be
composed without mandatory deployment repetition. The current first-executable defaults are:

- quiet timeout: 250 ms;
- maximum burst duration: 1000 ms;
- duplicate window: 15000 ms;
- sweep cadence: 50 ms;
- observation input-queue capacity: 256.

Runtime composition resolves an immutable startup policy from those compiled defaults plus
optional profile/platform/mode and explicit IF-11 overrides. Queue capacity is a resource
bound owned by TagProcessor, not a TimingNode/domain identity value.

IF-03 may replace runtime-adjustable policy fields while the application is running.
Policy replacement is itself serialized onto the TagProcessor lane so no filter/housekeeping
operation observes a partially updated policy. Quiet timeout, maximum burst duration,
duplicate window and sweep cadence are runtime-adjustable. Existing first-seen/accepted
timestamps remain unchanged; later expiry/duplicate decisions use the newly active policy.
Changing sweep cadence replaces the housekeeping registration on the same lane.

`observationQueueCapacity` is startup-only in the current baseline because it sizes the
owned `ArrayBlockingQueue<TagObservation>`. A live override request for that field is
rejected as restart-required rather than replacing the queue underneath concurrent ingress.

Runtime overrides are process state. Clearing an override restores the resolved startup
value; restart reconstructs the startup policy from compiled defaults plus IF-11 sources.

#### Tag-processing map sizing

`TagObservationFilter` keeps one map entry per currently open distinct `RegistrationId`.
`RegistrationDuplicateFilter` keeps one entry per accepted `RegistrationId` whose
duplicate-window state may still matter.

Do not hard-code an arbitrary initial `HashMap` capacity as a presumed optimization.
Java's default HashMap is lazy; an explicit capacity is useful only when a deployment
profile provides a credible expected count or Step-5 measurements show resizing to be
material.

If an explicit capacity is introduced later, size it from the expected entry count and
the map load factor so that the expected working set fits without immediate resizing.
The value and its evidence belong to the implementation/profile documentation, not to a
generic timing-domain requirement.

### TagRegistrationMapper

The mapper is a function/policy boundary, not a required in-memory map:

```java
interface TagRegistrationMapper {
    RegistrationId map(DecryptedTagId tagId);
}
```

Returning no RegistrationId means the decoded tag is not mappable by the active policy.
A concrete mapper may:

- perform a deterministic transformation;
- apply provider/profile-specific conversion;
- query locally available RaceData/reference data when that event actually requires it.

The public deterministic reference mapper uses the documented transformation:

```text
TAG-001 -> N-001
TAG-123 -> N-123
```


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
    private Lifecycle lifecycle = Lifecycle.CLOSED;
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
The caller must treat the final outcome as unknown and re-query/reconcile state
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

TimingNode TN-01 SerialExecutor lane
  bounded ArrayBlockingQueue
  at most one drain token scheduled

TimingNode TN-02 SerialExecutor lane
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

Local typed facts/notifications use a small `Event<T>` abstraction rather than a
central event bus. Examples include decoded antenna observations and post-commit
TimingData/status notifications. The reusable mechanism lives under `platform.events` because it
is a small JDK-only reusable primitive rather than domain semantics, external I/O
or concrete infrastructure.

Conceptually:

```java
interface EventSource<T> {
    boolean subscribe(Consumer<T> listener);
    boolean unsubscribe(Consumer<T> listener);
}

final class Event<T> implements EventSource<T> {
    DeliveryReport emit(T value);
}
```

A component owns the mutable `Event<T>` instance and is the only code that emits
the fact. Consumers receive an `EventSource<T>` subscription-only view, so they
subscribe directly without gaining permission to publish the event.

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

The design has no central dispatcher or string/topic routing; listeners
subscribe directly to the exposed event source they need. The event name states
the completed fact: a processed registration attempt that does not commit
TimingData does not emit this event.

Listeners must not become alternate owners of TimingNode mutable state. Slow
network delivery or retry work must also not block the TimingNode serial lane;
a listener that needs such work hands the TimingData value to its own bounded
execution/delivery mechanism.

The `Event<T>` listener registry is thread-safe and uses snapshot iteration, so
subscribe/unsubscribe may race safely with delivery. Delivery itself is
synchronous on the emitting thread and `Event<T>` does not serialize concurrent
`emit(...)` calls. An owner that requires ordering or non-overlapping callbacks
must emit from its own ordered execution boundary. TimingNode status-change and
committed-TimingData events are therefore emitted from the TimingNode serial
lane.

This is part of the same ingress/latency risk analysis: a synchronous local listener is acceptable only when it is demonstrably short and non-blocking. A WebSocket or other transport adapter must enqueue/buffer its outbound work and return quickly, or introduce its own bounded delivery executor. The TimingNode lane is not a network backpressure mechanism.

If listener notification fails after the record is committed, that does not
roll back the TimingData commit. A consumer that needs reliable recovery uses
authoritative persisted/LogBook state and its own reconciliation/delivery
mechanism.

Other local events may use the same `Event<T>` abstraction when a real consumer
needs them. Do not introduce events merely to replace ordinary direct method
calls.

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
TimingNode lifecycle policy, allocate sequence numbers, resolve `DecryptedTagId` or
`TeamId`, commit data, own a LogBook or publish events. Those responsibilities
stay with the TimingNode and its contained domain components.

Source/reference resolution happens before factory construction:

```text
DecryptedTagId  -----> RaceData ----\
                         +--> RegistrationId
TeamId -----> RaceData ----/
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
is no longer merely a optional capability. Keep the mechanism narrow and
composition-oriented:

```text
runtime.TimingApplication.create(...)
  -> infra extension discovery support
       -> discover built-in providers
       -> discover external provider JARs
  -> ExtensionRegistry
       TimingDataProvider
       UpstreamProtocolProvider
       AntennaProvider
       CanProtocolProvider
       DisplayProtocolProvider
  -> validate configured provider IDs
  -> create normal typed implementations
  -> return runtime.TimingApplication
```

For the Java 8 baseline, external discovery can use a dedicated `URLClassLoader`
plus standard `ServiceLoader` SPI metadata. Discovery happens during startup;
runtime hot reload/unload is deliberately out of scope. The provider registry
combines built-in and external providers and rejects duplicate provider IDs.

Provider contracts belong with the capability whose meaning they create;
class-loader/discovery mechanics belong under application-core Infrastructure support. Domain,
application and I/O runtime code must not depend on `URLClassLoader`,
`ServiceLoader` or a generic `Plugin` interface.

`SimulatedAntenna` and its provider are built into the public baseline and are
always available. External antenna JARs add alternative `AntennaProvider`
implementations. The same typed pattern is available for concrete TimingData,
UpstreamProtocol, CAN-protocol and display-protocol implementations where a
public/private or vendor boundary requires it.

IF-11 selects providers by stable provider ID. Missing providers, duplicate IDs
or an incompatible provider/configuration combination fail during validation or
startup rather than silently falling back to another implementation.

The exact external-JAR directory/layout, dependency isolation strategy and
whether the provider contracts eventually justify a separately versioned SPI
artifact remain implementation/evidence-driven decisions.

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
- exact external extension-JAR directory/layout and dependency-isolation policy;
- private Maven artifact publication/consumption mechanism;
- version alignment between public core/provider contracts and private implementations;
- which I/O capabilities eventually deserve independent artifacts;
- whether and when provider contracts deserve a dedicated independently versioned SPI artifact;
- exact field logging configuration/rotation/retention policy in the default executable.

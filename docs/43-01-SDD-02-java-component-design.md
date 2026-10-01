# Java component, package and artifact detailed design

Status: working draft / focused detailed design

Software item: **SI-01 — Timing Point Application**

This SDD describes the **Java implementation** of the SI-01 design: Maven
modules, packages, classes/interfaces, composition, queues/threads and provider
loading.

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
4. **Application composition** — assembly of framework code and selected implementations into an executable.
5. **Contract/port** — semantic boundary placed with the responsibility that owns its meaning.

A separate artifact is justified only by a real consumer, reuse, dependency, lifecycle, deployment, ownership, public/private, release or versioning boundary.

## Initial Maven reactor

The current reactor has two reusable artifacts plus one executable application.
The separate TimingData API artifact is justified by the independent SI-01 and
Engineering Client consumers:

```text
event-timing-framework/
├── pom.xml                    event-timing-parent
├── timing-data-api/
│   └── pom.xml                event-timing-data-api.jar
├── framework/
│   └── pom.xml                event-timing-framework.jar
└── app/
    └── pom.xml                event-timing-app.jar
```

Working coordinates:

```text
groupId: io.github.brainboxemb.eventtiming

parent:          event-timing-parent
TimingData API:  event-timing-data-api
framework:       event-timing-framework
executable:      event-timing-app
```

The root POM only groups/configures the build; it is not a runtime component.

The Maven `groupId` remains the **event-timing software-system/product-family** coordinate. SI-01 Java code is more specific: the reusable framework and default executable live under `io.github.brainboxemb.eventtiming.timingpoint`. `TimingPoint` names the local software/deployment role; it does **not** replace the internal `TimingNode` domain aggregate. One Timing Point Application process may host 1..N TimingSystems and therefore multiple TimingNodes.

## Package direction

The current Java structure should grow from real code, not from the architecture
diagram.

Likely top-level packages are:

```text
io.github.brainboxemb.eventtiming/timingpoint/
  application/
  domain/
  core/
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
    bootstrap/
      config/
    logging/
    loggingserver/
  runtime/
  platform/
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
- reserve `infra` for concrete cross-cutting technical support such as
  `BuildIdentity`;
- use `io` for external hardware, messaging and storage adapters.

For example, the first TimingNode implementation is grouped as:

```text
application/
  ApplicationId.java
  UpstreamMessageRouter.java       when upstream messaging is implemented

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
  logbook/
    LogBook.java
    LogBookItem.java                    internal logbook-domain representation
  timingdata/
    TimingData.java                     framework-owned semantic protocol API
    TimingDataRecord.java               canonical persistent/interchange record
    TimingDataCodec.java                canonical public/reference codec
    TimingDataProvider.java             external-format translation provider
  upstream/
    UpstreamProtocol.java               TimingData + sync/reconcile/ping semantics
    UpstreamProtocolProvider.java       typed extension provider contract

io/
  devices/
    antenna/
      Antenna.java                      stable antenna contract
      AntennaProvider.java              typed extension provider contract
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
```

The names above record ownership/direction, not a requirement to create empty
types early. `ApplicationId`, internal `TimingSystemId` and functional
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

`TimingNode` contains its `LogBook` as part of the TimingNode aggregate. The
LogBook keeps 0..N `LogBookItem` values as its internal operational
representation. A separate `logbook` package may still be used to keep that
cohesive implementation together; package placement does not make LogBook a
separate top-level aggregate.

`TimingData` is also a Domain capability, not an I/O codec package. `TimingNode`
has the explicit semantic relationship with this capability for timing data it
produces or consumes. The Java `TimingDataRecord` model and validation/codec
services realise the system-owned IF-05 contract; they do not create a second
public protocol authority. Concrete storage, Web and messaging adapters may
depend on that API and carry an encoded representation without knowing or
switching on individual TimingData fields.

`UpstreamProtocol` is a Domain capability owned by one `TimingSystem` and built partly on `TimingData`. It adds synchronization/reconciliation and protocol-level messages such as ping/pong so individual TimingNodes do not need to implement those concerns. `UpstreamGateway` owns the external transport boundary and uses 1..N concrete connectors. A connector such as `RabbitMqConnector` or `DebugConnector` owns transport/session mechanics, not TimingData or UpstreamProtocol semantics. `DebugConnector` is the engineering transport intended for an independent desktop/debug tool; that tool remains an external consumer rather than part of SI-01. `UpstreamMessageRouter` resolves semantic work inside the already selected TimingSystem context: system-level work uses `TimingSystem.UpstreamMessagePort`, while node-level work is resolved by `TimingNodeId` to `TimingNode.UpstreamMessagePort`. `TimingSystemId` is not required on the wire.

If the TimingNode capability later grows into several cohesive areas, deeper
packages such as `timing/registration` or `timing/stage` may become useful.
Do not create those packages before the corresponding code exists.

The Domain-level `SystemStatus` is a dedicated component contained by one `TimingSystem`. It is a semantic aggregate, not a wrapper around
concrete adapter objects and not merely an `OK` flag. It can represent current
TimingNode state together with operational I/O state such as antenna/display
connectivity, keypad/beeper availability, device-network health, storage,
upstream connectivity and synchronisation. Concrete I/O components expose or
publish semantic status inputs; `SystemStatus` must not depend on classes such
as `Rev1CanDisplay`, socket/session implementations or vendor antenna drivers.

An IDD response shape does not require an equally shaped internal Java object.
For example, the status JSON does not by itself require classes named
`ApplicationStatusSnapshot` or `ApplicationStatusModel`.

## Contract placement

Place contracts with the responsibility that owns their meaning:

```text
presentation
  functional client interfaces / transport mapping / wire messages

application
  commands, queries and application-level ports

domain
  domain model, semantic ports, per-TimingSystem TimeSource, TimingData representation/codec and UpstreamProtocol semantics

core
  runtime/execution contracts

io
  hardware, messaging and storage adapters

infra
  cross-cutting technical support and framework bootstrap/composition

runtime
  top-level composed runtime object and lifecycle mechanics

infra
  extension discovery/registry and framework bootstrap/composition

platform
  execution-environment abstractions
```

Do not create one generic top-level `api` package merely to collect
interfaces.

## Internal dependency direction

```text
presentation    --> application
application     --> domain / core / I/O ports
io              --> application/domain ports/contracts + platform
runtime         --> application / domain / core
infra.bootstrap --> runtime + selected presentation/I/O/platform implementations
core            --> reusable execution mechanics
platform        --> low-level environment only
```

Domain code does not depend on presentation or concrete I/O adapters.
Executable composition may depend on the complete supported framework surface
and selected external libraries.

## Logging dependency placement

Logging follows the same library-versus-executable composition boundary.

```text
event-timing-framework.jar
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

event-timing-app.jar
  -> selects exactly one SLF4J provider
  -> initial provider: slf4j-jdk14
  -> delegates SLF4J records to java.util.logging
  -> starts/stops framework-provided Logging
  -> independently starts/stops optional LoggingServer
```

Working rules:

- framework code may compile against the SLF4J API but must not force a concrete provider/backend on consumers;
- provider-neutral deployment values stay component-owned: `LoggingConfig` contains `LoggingLevel` and `LoggingFileConfig`; optional `LoggingServerConfig` belongs to `LoggingServer`; `ApplicationConfig` may reference both as composition data;
- the executable application chooses and configures the provider/backend before `ApplicationBootstrap` starts normal runtime composition;
- the initial Java-8/Pi-Zero baseline uses `slf4j-jdk14` so the provider delegates to JDK `java.util.logging` without introducing Logback;
- concrete JUL backend/file lifecycle stays under `timingpoint.infra.logging`; the live diagnostics handler/socket lifecycle stays under `timingpoint.infra.loggingserver`; neither package defines domain/application contracts;
- `infra.logging` must not depend on `infra.loggingserver` or `infra.bootstrap.config`; executable/bootstrap composition starts the two components separately. `infra.loggingserver` may depend on the narrow public `Logging` runtime surface for current level control and record formatting, but the logging component does not construct or own the server;
- `LoggingServerConfig` belongs to the `LoggingServer` component and carries its listener values (`bindAddress`, `port`); the default YAML loader maps the external `logging.live` syntax to that component-owned type;
- `LoggingLevel` is a logging-domain value rather than `LoggingConfig.Level`, so live level control does not depend on an umbrella configuration class;
- the framework artifact owns that reusable implementation because it has no dependency on executable-specific YAML/resource loading and uses only JDK facilities plus component-owned logging configuration;
- `Logging` is the primary runtime logging infrastructure component and owns backend setup, console/file handler composition, record formatting and the current global-level control;
- `LoggingServer` is the separate externally reachable live-diagnostics component; it owns the live JUL handler plus logging-specific socket/protocol boundary, delegates temporary level changes to `Logging`, and is not a Presentation/IF-03 endpoint;
- the default retained file sink uses the local wall-clock start/rotation timestamp as a human-readable filename, normally `yyyyMMdd-HHmmss.txt`; this timestamp is not treated as a unique or monotonic session identity;
- Raspberry Pi startup must not assume that wall-clock time is already network-synchronised: the clock may repeat or move backwards across restarts, so retained log creation must use non-overwriting create semantics, add a collision suffix when necessary, and protect the active log from retention decisions regardless of timestamp ordering;
- retained text records use the compact operator-facing form `HH:mm:ss.SSS - [LEVEL] - message - [sourceClass.sourceMethod]`; exception stack traces follow the record line when present;
- `LoggingControl` owns the configured global level plus an optional temporary runtime override; applying an override changes the running logger threshold without mutating deployment configuration;
- the optional diagnostic listener is a logging-specific engineering facility. The test client initiates its TCP connection, log delivery is best effort, and network failure must not be allowed to block ordinary log publishers;
- the live diagnostics protocol is separate from the IF-03 status/event wire model;
- another executable/private consumer may select another compatible provider later without changing framework/domain source;
- exactly one provider should be present in a runtime composition;
- provider/backend versions are pinned centrally by Maven dependency management rather than scattered through modules.

This keeps provider selection replaceable at the executable boundary while allowing the reusable
framework to provide the default JUL logging infrastructure and its configuration contract.

## Default executable application

`event-timing-app` is the first executable consumer of the framework library.

Its executable package is deliberately thin:

```text
io.github.brainboxemb.eventtiming.timingpoint.app/
  TimingApplicationMain.java
```

The framework owns the reusable SI-01 runtime, bootstrap and infrastructure components:

```text
io.github.brainboxemb.eventtiming/timingpoint/
  runtime/
    TimingApplication.java
    TimingApplicationLifecycle.java
  infra/
    BuildIdentity.java
    EmbeddedBuildIdentityLoader.java
    bootstrap/
      ApplicationBootstrap.java
      config/
        ApplicationConfig.java
        PresentationConfig.java
        RemoteShellConfig.java
        ApiConfig.java
        ApiHttpConfig.java
        ApiWebSocketConfig.java
        YamlApplicationConfigLoader.java
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

`runtime/` is the Java source-organisation package for the top-level running
composition and lifecycle objects. Figure SI01-01 now shows this explicitly as a
separate **Runtime** block containing `TimingApplication`. Runtime is not an
additional business/domain layer: it is the execution container that holds the
running application/domain composition. In the current implementation
`ApplicationBootstrap` still owns startup/cleanup of concrete presentation
endpoints around that runtime; those endpoints retain their Presentation
ownership even if their lifecycle is later retained directly by the runtime.

The executable artifact is deliberately thin. Its launcher/input adapters remain under
`...eventtiming.app`; reusable runtime logging belongs to framework infrastructure:

```text
event-timing-framework.jar
  io.github.brainboxemb.eventtiming.timingpoint.infra.logging/
    Logging.java
    LoggingConfig.java
    LoggingLevel.java
    LoggingFileConfig.java
    LoggingControl.java
    TimestampedFileLogHandler.java
    CompactLogFormatter.java

  io.github.brainboxemb.eventtiming.timingpoint.infra.loggingserver/
    LoggingServer.java
    LoggingServerConfig.java
    LiveLogHandler.java

event-timing-framework.jar
  io.github.brainboxemb.eventtiming.timingpoint.infra/
    BuildIdentity.java
    EmbeddedBuildIdentityLoader.java
    bootstrap/
      ApplicationBootstrap.java
      config/
        YamlApplicationConfigLoader.java

event-timing-app.jar
  io.github.brainboxemb.eventtiming.timingpoint.app/
    TimingApplicationMain.java
```

`event-timing-framework.jar` contains the JUL-based default logging infrastructure but still does **not** select an SLF4J provider. Provider selection remains an executable-composition concern: the default app contributes `slf4j-jdk14` at runtime, while another consumer may choose another compatible composition and omit the default `Logging` component.

The target executable startup/configuration flow is:

```text
main()
  -> framework EmbeddedBuildIdentityLoader
       -> executable-provided filtered build resource
  -> configuration resolution
       -> selected built-in application-profile defaults
       -> selected platform defaults
       -> selected operating-mode defaults
       -> explicit IF-11 YAML deployment overrides
       -> secret resolution
       -> validated effective ApplicationConfig
  -> Logging
       -> configure JUL level + console/file handlers
  -> optional LoggingServer
       -> attach live handler + diagnostics listener
       -> use Logging for current level / common formatting
  -> framework ApplicationBootstrap
       -> select/construct concrete presentation/I/O/platform implementations
       -> create reusable application/domain/runtime objects
       -> install/start presentation and shutdown handling
  -> TimingApplication runtime
```

The current Step-3 `YamlApplicationConfigLoader` implements only the explicit
YAML subset already needed by the running application. Profile/platform/mode
resolution is the next configuration responsibility; the architecture does not
require a new public Java type for each source before that behaviour is
implemented.

`BuildIdentity` and `ApplicationConfig` are different inputs. Build identity is artifact provenance; application configuration is deployment composition defined by IF-11. The executable embeds deterministic provenance fields (`application`, `version`, exact `revision`, `sourceRef`, `buildOrigin`, `dirty`, `apiVersion`). Wall-clock build time, CI run/build id and actor/user are not embedded because they are per-run metadata rather than stable build inputs/context.

Reusable application behaviour should not migrate into the executable merely because the architectural responsibility is called `application`. When a reusable framework application/runtime object becomes justified by real shared behaviour, executables should **compose** that object rather than extend a `BaseApplication` hierarchy.

The framework keeps the small `TimingApplication.Builder` only for constructing
the runtime object itself. `ApplicationBootstrap` is the concrete cross-cutting
composition component around it and consumes the framework-owned effective
`ApplicationConfig`.

The default IF-11 file syntax is YAML and its parser/mapping belongs to reusable
framework infrastructure. `YamlApplicationConfigLoader` lives with the framework
bootstrap/configuration model. As profile support is implemented, configuration
infrastructure resolves built-in profile/platform/mode defaults plus explicit
deployment YAML into one effective `ApplicationConfig` **before**
`ApplicationBootstrap` runs.

The resolver responsibility must remain data/composition oriented:

- `standard` and `finish` are profile IDs/default templates, not Java subclasses;
- do not introduce `StandardTimingApplication`, `FinishTimingApplication` or a
  profile-specific domain hierarchy;
- profile defaults may select topology/cardinality and capability defaults;
- platform defaults may select environment-specific values;
- operating-mode defaults may replace real providers with simulated providers;
- explicit IF-11 deployment values have highest non-secret precedence;
- `ApplicationBootstrap` consumes only the resolved/validated
  `ApplicationConfig` and contains no profile-name switches.

SnakeYAML is therefore a framework implementation dependency; the IF-11 contract
remains independent of SnakeYAML APIs and another input adapter may construct the
same typed effective `ApplicationConfig` without YAML.

Build-identity interpretation is reusable for the same reason. The framework owns
`BuildIdentity` and `EmbeddedBuildIdentityLoader`. The concrete executable still owns
the filtered `event-timing-build.properties` resource and build-time provenance injection,
because those values identify that executable artifact. The framework loader only interprets
the classpath resource and has no dependency on `TimingApplicationMain` or another app class.

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

Console and remote shell are separate presentation interfaces. They share only the
line-oriented command-session behaviour in `presentation.common.terminal`; both call
the same `CommandHandler` and shutdown callback.

Console, Remote Shell and API are baseline Timing Point Application capabilities.
Application profiles do not add/remove or redefine their command/status semantics.
Concrete network listener bindings remain deployment configuration, so a listener
may still be explicitly left unbound/disabled without creating another profile.

A06/A07 are the first slice of the functional **API**:

```text
HttpEndpoint
  +-- GET /api/v1/version
  +-- GET /api/v1/status
            \
             +--> CommandHandler.version() / status()
            /
WebSocketEndpoint
  +-- WS /api/v1/events
  +-- STATUS_SNAPSHOT on connect/reconnect
  +-- STATUS_CHANGED only for real status changes
```

`MessageWriter` owns the IF-03 wire/JSON representation shared by the Remote
API HTTP and WebSocket transports. It is not application/control logic and therefore
does not live in the application layer or in global presentation common code.

The local class names deliberately omit the `Api` prefix because the enclosing `presentation.interfaces.api` package already supplies that functional context. `Endpoint` is used rather than `Server` for the transport-facing classes; in particular, `HttpServer` is avoided because the implementation uses `com.sun.net.httpserver.HttpServer` internally.

The first WebSocket implementation uses `Java-WebSocket 1.6.0` in the reusable
framework and keeps the accepted A06 JDK HTTP server unchanged rather than replacing
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
`event-timing-framework` or `event-timing-app` implementation code. It may,
however, depend on the separately reusable `timing-data-api` artifact because
TimingData codec/provider reuse is now a real cross-executable requirement. This
preserves the external-client boundary while allowing SI-01 and the Engineering
Client to exercise the exact same public or proprietary TimingData translator.

The Engineering Client remains engineering support rather than the planned SI-02
GUI, and its JavaFX choice does not select the SI-02 GUI technology.

The shared presentation/application boundary remains small:
`CommandHandler.version()` returns build identity and
`CommandHandler.status()` returns the current TimingNode status used by the
current presentation adapters.

## LogBook recording and TimingData persistence

The existing architecture remains authoritative: one `TimingNode` contains one
`LogBook`, and that LogBook owns the node's operational traceable state as
0..N `LogBookItem` values.

IF-05 `TimingData` is the persistent/interchange representation used to store
and exchange those committed facts. Do not introduce a second domain component
called `TimingDataJournal` or a separate `TimingDataProjection` beside the
LogBook.

The TimingNode handles the domain-facing operation. For example,
`register(teamIdentity, time)` validates/resolves the registration and calls
`LogBook.record(...)`. That LogBook call is the asynchronous recording
boundary.

The first Java implementation keeps the queue and worker **inside the LogBook
implementation**:

```text
TimingNode
  +-- register(...)
  |
  +--> LogBook.record(...)
         +-- bounded ArrayBlockingQueue<LogBookEntryCandidate>
         +-- one record worker
         +-- committed LogBookItem state
         |
         +--> TimingDataStore
                |
                +-- FileTimingDataStore
                    file persistence / recovery
```

No `LogBookRecorder` or `LogBookCommitter` architecture type is required.
The queue and worker are runtime details of LogBook recording. If a small private
or package-private helper later makes the implementation easier to test or
maintain, it remains an implementation detail.

### First-slice Java responsibilities

| Type | Responsibility | Thread/queue ownership |
| --- | --- | --- |
| `TimingNode` | Own lifecycle and domain-facing operations for one timing point; resolve input and hand traceable entries to LogBook | no persistence worker |
| `LogBookEntryCandidate` | Internal description of one traceable fact before sequence/recordedAt/commit | none |
| `LogBook` | Own committed `LogBookItem` state plus the ordered asynchronous recording lane | one bounded queue + one record worker in the first implementation |
| `TimingDataStore` | Storage boundary used by LogBook recording for IF-05 append/read/recovery | none |
| `FileTimingDataStore` | Concrete file handling: append, durable flush, startup scan, incomplete-tail repair and record loading | blocking file I/O on the LogBook record worker |
| `CommittedTimingDataSink` | Non-blocking hand-off for committed IF-05 facts that need signalling/upstream delivery | slow sinks own their own async boundary |
| query/ranking services | Read LogBook/reference state and perform expensive work outside the LogBook worker | introduced with their real use cases |

`TimingDataStore` is an I/O/storage boundary. It does not become a Domain
aggregate and does not replace the LogBook. Diagrams label it **file persistence
/ recovery**; the concrete `FileTimingDataStore` contains the actual filesystem
handling.

### LogBook queue and worker

Use a bounded `ArrayBlockingQueue<LogBookEntryCandidate>` rather than a
linked/unbounded queue or the default queue hidden inside
`Executors.newSingleThreadExecutor()`.

Reasons:

- capacity is explicit and observable;
- the backing reference array is allocated once;
- queue bookkeeping does not allocate one linked node per event;
- overload cannot grow memory without bound on the Raspberry Pi;
- FIFO behaviour matches the serial per-TimingNode commit-order requirement.

Do not guess the production queue size yet. Measure event bursts and worst-case
file-write latency on the Raspberry Pi. A full queue must be visible to
application/status code; never silently drop a traceable entry.

A first implementation can keep the worker directly inside `LogBook`:

```java
final class LogBook implements AutoCloseable {
    private final BlockingQueue<LogBookEntryCandidate> recordQueue;
    private final TimingDataStore timingDataStore;
    private final Thread recordWorker;

    boolean record(LogBookEntryCandidate entry) {
        return recordQueue.offer(entry);
    }

    private void runRecordWorker() {
        while (running) {
            commit(recordQueue.take());
        }
    }

    private void commit(LogBookEntryCandidate entry) {
        long sequence = sequenceState.peekNext();
        TimingTimestamp recordedAt = timeSource.now();

        LogBookItem item =
            logBookItemFactory.create(entry, sequence, recordedAt);
        TimingDataRecord record = timingData.toRecord(item);

        timingDataStore.append(record);
        sequenceState.commit(sequence);
        applyCommitted(item);
        committedSinks.publish(record);
    }
}
```

The sketch fixes ownership, not final class shape. Shutdown/interruption/error
handling still has to be designed carefully.

`TimingNode.register(...)` therefore returns **accepted** after
`LogBook.record(...)` has accepted the entry into the bounded queue. It does not
wait for the durable file append.

If `timingDataStore.append(record)` fails, do not advance the sequence and do
not expose the item as committed LogBook state. Later entries in the same node's
record lane must not overtake it. On restart/retry, first repair the file back to
its last complete record, rebuild LogBook state, then continue with the same next
sequence.

The commit code can be unit-tested with an in-memory `TimingDataStore`, fake
`TimeSource`, deterministic sequence state and fake committed sinks. Extracting
a private helper for testability is allowed, but it does not become a new
architecture component.

### LogBook reads and long-running queries

Queries and ranking logic do not consume a second TimingData queue. They read the
LogBook and the other Domain/reference components that own the required
information.

Keep LogBook reads short. A long ranking/report calculation should not hold a
LogBook lock and should not deep-copy the complete history.

Depending on the first real query, suitable Pi-friendly patterns include:

- capture only the small set of immutable `LogBookItem` references required by
  the calculation;
- maintain compact indexes inside LogBook for current participant/event lookup;
- capture a sequence/version boundary and use it to define the query view;
- copy a small primitive/reference index when cheaper than retaining a lock.

Do not clone the complete LogBook for every query, and do not use
`CopyOnWriteArrayList` for frequently changing registration/history data.

### External committed-data output

External signalling, WebSocket publication or upstream delivery may block/retry
independently. Such work does not execute on the LogBook record worker.

```java
interface CommittedTimingDataSink {
    boolean offer(TimingDataRecord record);
}
```

Each concrete slow/network sink owns its own bounded queue/worker or durable
outbox as required by that capability. There is no shared second
`BlockingQueue<TimingDataRecord>` for LogBook state, queries and all external
outputs.

### Multiple TimingNodes

The semantic requirement is one serial LogBook recording lane per
`TimingNodeId`, not permanently one operating-system thread per TimingNode.

For the first one-node application:

```text
1 TimingNode
  -> 1 LogBook
       -> 1 bounded recording queue
       -> 1 record worker
       -> 1 TimingDataStore dependency
```

If a later multi-node application shows that one worker per LogBook is too
expensive, multiple logical lanes may share a small executor while preserving
FIFO ordering independently per TimingNode. Do not build that scheduler before
the multi-node consumer exists.

### Raspberry-Pi implementation rules

For the initial Pi-oriented runtime:

- keep each LogBook recording queue bounded;
- prefer `ArrayBlockingQueue` over linked/unbounded work queues;
- do not allocate a `CompletableFuture`/task wrapper per LogBook event unless a
  real asynchronous result consumer requires it;
- do not deep-copy complete LogBook state for routine queries;
- do not use `CopyOnWriteArrayList` for registration/event history;
- keep long-lived record-worker count explicit in composition/status;
- keep LogBook mutation single-writer where practical;
- move blocking network/retry work behind capability-specific output boundaries;
- measure queue high-water, durable-store latency, heap/GC behaviour and query
  latency on the target Raspberry Pi before increasing concurrency.

## Shared TimingData API artifact

Both SI-01 and the Engineering Client need the TimingData types/provider SPI.
That is enough reason for a small shared artifact; the Java-17 Engineering Client
should not have to depend on the whole SI-01 framework.

Conceptually:

```text
timing-data-api
  TimingDataRecord / TimingDataRecordKey
  RegistrationIdentity and TimingData value types
  TimingDataCodec
  TimingDataProvider / translator SPI

event-timing-framework  ---> timing-data-api
test-client             ---> timing-data-api

reference TimingData provider  ---> timing-data-api
private eBART provider         ---> timing-data-api
                                  |
                                  +-- optional native/proprietary DLL
```

Both applications may load the same provider implementation. The shared Java
types follow IF-05; IF-05 remains the place that defines the fields, ordering,
versioning and file format. A provider only translates an external format to/from
that model.

The shared artifact contains **interchange values**, not the whole SI-01 Domain
model. For example, SI-01 keeps its strong `TimingNodeId` type, while the IF-05
record carries the serialized `timingNodeId` value as a non-empty `String`:

```text
SI-01 Domain
  TimingNodeId
      |
      | value()
      v
timing-data-api
  TimingDataRecord.timingNodeId : String
  TimingDataRecordKey.timingNodeId : String
```

The framework maps between those two forms at the TimingData boundary. That keeps
the Engineering Client independent from SI-01 Domain packages, while
`timing-data-api` stays a small file/interchange API rather than becoming a
second Domain model.

This artifact contains no SI-01 runtime/application classes and no JavaFX code.
Its Java API must remain usable from both the Java-8 SI-01 baseline and the
Java-17 Engineering Client.

## Derived consumers

The framework is deliberately not tied to one executable topology. Plausible consumers include:

```text
single-system application
multi-system / simulation application
public reference/test application
private/product application
```

These are consumer possibilities, not modules to create now.

## Java 8 extension/provider mechanism

A concrete public/private extension requirement now exists, so provider discovery
is no longer merely a future possibility. Keep the mechanism narrow and
composition-oriented:

```text
ApplicationBootstrap
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
  -> compose TimingApplication
```

For the Java 8 baseline, external discovery can use a dedicated `URLClassLoader`
plus standard `ServiceLoader` SPI metadata. Discovery happens during startup;
runtime hot reload/unload is deliberately out of scope. The provider registry
combines built-in and external providers and rejects duplicate provider IDs.

Provider contracts belong with the capability whose meaning they create;
class-loader/discovery mechanics belong under framework bootstrap/infra. Domain,
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

## Possible future artifacts

Create future artifacts only when a real boundary requires them. Candidates might eventually include:

- RabbitMQ/messaging I/O;
- Linux/Raspberry-Pi platform support;
- public/private RFID/CAN I/O implementations;
- separately versioning `timing-data-api` if binary compatibility/release evidence later requires an independent release cycle;
- reusable test support.

Splitting later is preferred over speculative libraries, provided package/responsibility boundaries remain clean enough to extract.

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
- the executable consumes `event-timing-framework` rather than copying/forking framework source;
- the framework artifact does not carry a concrete SLF4J provider/backend transitively;
- an executable runtime contains exactly one intended SLF4J provider.

## Open detailed-design decisions

- exact package granularity after real application/domain classes exist;
- final package naming where capability-oriented packages prove clearer than layer names;
- exact reusable boundary between single-instance runtime mechanics and multi-system application orchestration;
- exact bounded LogBook ingress-queue capacity and queue-full operational policy after Raspberry-Pi burst/latency measurement;
- concrete compact LogBook indexes/read-view mechanics required by the first ranking/query implementation;
- exact external extension-JAR directory/layout and dependency-isolation policy;
- private Maven artifact publication/consumption mechanism;
- version alignment between public framework/provider contracts and private implementations;
- which I/O capabilities eventually deserve independent artifacts;
- whether and when provider contracts deserve a dedicated independently versioned SPI artifact;
- exact field logging configuration/rotation/retention policy in the default executable.

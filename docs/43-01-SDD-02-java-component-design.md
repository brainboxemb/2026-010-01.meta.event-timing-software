# Java component, package and artifact detailed design

Status: working draft / non-authoritative

Software item: **SI-01 — Timing Point Application**

This SDD has one focused purpose: refine the SI-01 architecture into Java package, Maven artifact, composition and contract-placement rules that are already relevant to the implementation repository.

The application architecture itself — including runtime hierarchy, threading, messaging, integration, configuration and technology direction — is owned by the architecture part of `41-01-SSD-timing-application-specification-document.md`.

## Why this SDD exists

This detail is kept separate because artifact/package choices already affect source layout, dependency checks, public/private composition and release boundaries in the implementation repository.

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

## TimingData runtime implementation model

The IF-05 contract and the asynchronous processing design now have a concrete
Java-8 realisation direction. Keep the implementation deliberately small for the
Raspberry-Pi baseline: one bounded ingress queue and one dedicated record worker
per active serial commit lane are sufficient for the first slice.

Do not introduce a generic event bus, actor framework, reactive-stream library or
unbounded executor merely to implement this path.

### First-slice Java responsibilities

```text
domain/application producer
  TagProcessor / manual registration / lifecycle
        |
        | TimingDataIntent
        v
application.timingdata.TimingDataRecorder
  ArrayBlockingQueue<TimingDataIntent>
  one worker thread
        |
        v
application.timingdata.TimingDataCommitter
  synchronous + unit-testable
        |
        +--> TimingDataJournal
        |      |
        |      +--> io.storage.timingdata.FileTimingDataJournal
        |
        +--> TimingDataProjection
        |
        +--> CommittedTimingDataSink(s)
               |
               +--> each slow/network sink owns its own async boundary
```

Proposed concrete first-slice types:

| Type | Responsibility | Thread/queue ownership |
| --- | --- | --- |
| `TimingDataIntent` | Immutable internal description of one timing fact before sequence/recordedAt/commit | none |
| `TimingDataRecorder` | Accept intents, own bounded ingress queue and record-worker lifecycle | owns one `ArrayBlockingQueue` and worker thread |
| `TimingDataCommitter` | Turn the next intent into one committed IF-05 record in strict source order | called only by record worker; no thread of its own |
| `TimingDataJournal` | Application-facing append/recovery port for authoritative committed TimingData history | none |
| `FileTimingDataJournal` | Canonical IF-05 append-only file implementation | blocking file I/O on record worker |
| `TimingDataProjection` | Apply committed records to compact runtime LogBook/business read state | synchronous, short single-writer update |
| `CommittedTimingDataSink` | Non-blocking hand-off contract for committed facts that need external signalling/delivery | contract only; concrete slow sinks own queue/worker |
| `TimingDataQueryService` | Query the current projection without executing on the record worker | introduced with first real non-trivial query use case |

The names are design candidates until implementation begins, but the
responsibility boundaries are intentional. In particular,
`TimingDataRecorder` and `TimingDataCommitter` are separate so concurrency can
be tested independently from commit semantics.

### Why ArrayBlockingQueue

The ingress boundary should use a bounded `ArrayBlockingQueue<TimingDataIntent>`
rather than `LinkedBlockingQueue` or the default work queue hidden inside
`Executors.newSingleThreadExecutor()`.

Reasons:

- capacity is explicit and observable;
- the backing reference array is allocated once;
- queue bookkeeping does not allocate one linked node per registration;
- overload cannot grow memory without bound on a Raspberry Pi;
- FIFO behaviour matches the serial source-order requirement.

The exact capacity is a deployment/verification value and shall be selected from
measured burst rate plus worst-case journal latency. Queue-full behaviour must be
explicitly surfaced as timing-data backpressure/fault state; silently dropping an
intent is not permitted.

For the first single-TimingNode implementation a dedicated worker loop is clearer
than wrapping this queue in a general executor:

```java
final class TimingDataRecorder implements AutoCloseable {
    private final BlockingQueue<TimingDataIntent> queue;
    private final TimingDataCommitter committer;
    private final Thread worker;

    boolean submit(TimingDataIntent intent) {
        return queue.offer(intent);
    }

    private void run() {
        while (running) {
            TimingDataIntent intent = queue.take();
            committer.commit(intent);
        }
    }
}
```

The production implementation needs deliberate interruption/shutdown and failure
handling; the example shows ownership rather than final exception policy.

### Synchronous commit core

`TimingDataCommitter` contains the ordered algorithm and has no executor or
sleep/wait logic:

```java
CommittedTimingData commit(TimingDataIntent intent) {
    long sequence = sequenceState.peekNext();
    TimingTimestamp recordedAt = timeSource.now();

    TimingDataRecord record =
        recordFactory.create(intent, sequence, recordedAt);

    journal.append(record);          // returns only after durable commit
    sequenceState.commit(sequence);  // number is now consumed
    projection.apply(record);        // short deterministic update
    committedSinks.publish(record);  // non-blocking hand-off only

    return new CommittedTimingData(record);
}
```

If `journal.append(record)` fails, neither sequence state nor projection state
advances. The next intent for that TimingNode must not overtake the failed
record. Recovery/retry uses the same sequence value after the journal has been
restored to its last complete committed boundary.

This synchronous core can be unit-tested using an in-memory journal, fake
`TimeSource`, deterministic sequence state, in-memory projection and fake
committed sink. Unit tests therefore do not need real worker threads or sleeps to
verify ordering and commit semantics.

### No second queue for queries

A potentially slow query does **not** consume the committed TimingData stream and
does not require another queue in the commit pipeline.

After durable commit, the record worker performs only a short projection update.
Queries operate on that projection from another execution context:

```text
record worker
    |
    +-- journal.append(record)
    +-- projection.apply(record)       short
    +-- outputSink.offer(record)       short/non-blocking
              |
              +--> slow network/output worker elsewhere

query caller
    |
    +-- acquire/read compact projection view
    +-- release projection synchronisation
    +-- perform expensive calculation outside record worker
```

Do not deep-copy the complete LogBook/domain object graph for each query. The
Raspberry-Pi baseline should keep read capture small and bounded.

When a coherent long-running query requires a stable view, prefer one of these
small-footprint patterns, selected when the real query is implemented:

- immutable per-team/per-entry state with a short capture of only the references
  required by that query;
- a compact primitive/reference index captured under a short read section;
- sequence/version validation around a read operation where the underlying data
  structure makes such optimistic reading safe.

The design explicitly rejects holding a long read lock while ranking/report
calculation runs. It also rejects `CopyOnWriteArrayList` for high-frequency
registration state and rejects a mandatory deep snapshot on every query.

### Projection storage direction

The projection is a runtime read/business model, not a second durable authority.
It has one writer: `TimingDataCommitter`.

For bounded participant domains, fixed/indexed structures are preferred where
they make the model simpler and cheaper than general-purpose maps. For example,
current per-participant state may eventually use arrays/indexes keyed by the
validated IF-05 registration type/number domain. Do not commit to such a physical
layout until the first ranking/query implementation demonstrates which indexes
are actually useful.

Historical/audit truth remains the append-only TimingData journal. The projection
may therefore optimize for current calculations and rebuild itself from journal
replay at startup.

### Committed output boundaries

External signalling and upstream delivery may block or retry independently, so a
slow output adapter must not execute network/file delivery on the record worker.

`CommittedTimingDataSink` is therefore a narrow application-facing hand-off:

```java
interface CommittedTimingDataSink {
    boolean offer(TimingDataRecord record);
}
```

A concrete sink that can block owns its own bounded queue/worker or durable
outbox. There is no requirement for one global second
`BlockingQueue<TimingDataRecord>` shared by projections, queries and all
outputs. This avoids competing-consumer ambiguity and lets each output capability
define its own backpressure/retry semantics.

### Multiple TimingNodes

The semantic requirement is one ordered serial commit lane per `TimingNodeId`,
not permanently one operating-system thread per TimingNode.

For the first one-node application:

```text
1 TimingNode
  -> 1 TimingDataRecorder
  -> 1 bounded queue
  -> 1 record worker
```

That is the preferred first implementation because it is explicit and easy to
verify.

If a later multi-node application demonstrates that one worker thread per node is
too expensive, several logical lanes may share a small executor while preserving
FIFO ordering independently for each TimingNode. Do not introduce that scheduler
abstraction before the multi-node consumer exists.

### Raspberry-Pi allocation/threading rules

For the initial Pi-oriented runtime:

- keep the ingress queue bounded;
- prefer `ArrayBlockingQueue` over linked/unbounded work queues;
- do not allocate a `CompletableFuture` or task-wrapper object for every timing
  record unless a real asynchronous result consumer requires it;
- do not deep-copy the complete projection for routine queries;
- do not use `CopyOnWriteArrayList` for registration/event state;
- keep the number of long-lived worker threads explicit in composition/status;
- keep record/projection updates single-writer wherever practical;
- move blocking network/retry work behind capability-specific asynchronous
  output boundaries;
- measure queue high-water, journal latency, heap/GC behaviour and query latency
  on the target Raspberry Pi before increasing concurrency.

## Shared TimingData API artifact

The Engineering Client is a second real consumer of the TimingData model and
provider SPI. That reuse justifies a small independently reusable artifact rather
than forcing the Java-17 test client to depend on the SI-01 framework artifact.

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

Both executables may discover/select the same provider implementation. The
shared Java types and codec/provider SPI **realise IF-05**; the normative record,
identity, ordering, versioning and file/interchange semantics remain owned by
`32-05-IDD-timingdata-interchange.md`. The provider translates between an
external format and that IF-05 model; it does not redefine TimingData field
semantics.

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
- exact bounded record-queue capacity and queue-full operational policy after Raspberry-Pi burst/latency measurement;
- concrete compact projection/index structures required by the first ranking/query implementation;
- exact external extension-JAR directory/layout and dependency-isolation policy;
- private Maven artifact publication/consumption mechanism;
- version alignment between public framework/provider contracts and private implementations;
- which I/O capabilities eventually deserve independent artifacts;
- whether and when provider contracts deserve a dedicated independently versioned SPI artifact;
- exact field logging configuration/rotation/retention policy in the default executable.

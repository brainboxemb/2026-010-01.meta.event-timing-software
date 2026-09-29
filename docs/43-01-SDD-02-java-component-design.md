# Java component, package and artifact detailed design

Status: working draft / non-authoritative

Software item: **SI-01 — Headless Timing Application**

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

## Package direction

The current Java structure should grow from real code, not from the architecture
diagram.

Likely top-level packages are:

```text
io.github.brainboxemb.eventtiming/
  application/
  domain/
  core/
  presentation/
    interfaces/
      remoteapi/
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
  runtime/
  platform/
```

Presentation subpackages are organised by **functional interface first**. Console, Remote Shell, Web and Remote API are separate presentation interfaces. The intended Web topology is one configured Web endpoint/binding per TimingNode (1..N), each with its own presentation port and a `TimingNodeId` reference. HTTP/WebSocket are implementation transports inside a functional interface, not global presentation categories. The primary Remote API classes stay directly at `presentation.interfaces.remoteapi` while that component is small; a one-class `http`, `websocket` or `messages` package would hide the component overview without adding a useful boundary. `presentation.common.terminal` contains only terminal handling genuinely shared by Console and Remote Shell; `presentation.common` is not a generic dumping ground.

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
  timing/
    TimingNode.java
    TimingNodeId.java
    UpstreamMessagePort.java            when upstream message handling is implemented
  logbook/
    LogBook.java
    LogBookItem.java                    internal logbook-domain representation
  timingdata/
    TimingData.java                     canonical record/codec contract
    TimingDataRecord.java               persistent/interchange record
  upstream/
    UpstreamProtocol.java               TimingData + sync/reconcile/ping semantics

io/
  devices/
    antenna/
      Antenna.java                 concrete/source types only when implemented
    display/
      DisplayRev1Can.java          passive CAN display support when implemented
    keypad/                        only when device-specific code justifies it
    beeper/                         transport-specific implementation only when justified

  devicenetworks/
    can/
      CanNetworkController.java    CAN lifecycle, discovery and device state
    network/
      NetworkDeviceService.java    bidirectional network-device boundary

  messaging/
    UpstreamGateway.java            when upstream messaging is implemented
    Connector.java                 only if multiple transports justify a shared contract
    rabbitmq/
      RabbitMqConnector.java
```

The names above record ownership/direction, not a requirement to create empty types early. `ApplicationId`, internal `TimingSystemId` and functional `TimingNodeId` are separate Java identities. `TimingSystemId` distinguishes multiple hosted/simulated systems locally; it is not automatically serialized into TimingData or exposed as an upstream address.

`CanNetworkController` owns CAN-network lifecycle/discovery and CAN-device
communication. `NetworkDeviceService` owns the general bidirectional
network-device boundary. It may expose application data outward and accept
device-originated messages/events inward.

The high-level architecture deliberately stops there. Service discovery,
connection/listener/session handling and protocol framing are lower-level design
concerns below `NetworkDeviceService`. Likewise, a smart-display/domain handler
should not acquire socket, mDNS or transport knowledge merely because it is
reached through this service. The smart display remains an external client and
therefore does not require a `DisplayRev2Wifi` class inside SI-01 merely to
mirror the hardware name.

`TimingNode` owns the lifecycle of its `LogBook`, while the LogBook remains
a separate Domain capability. The LogBook keeps 0..N `LogBookItem` values as
its internal operational representation.

`TimingData` is also a Domain capability, not an I/O codec package. It owns the
canonical `TimingDataRecord` representation plus the public validation,
encode/decode and compatibility contract used for persistence and interchange.
Concrete storage, Web and messaging adapters may depend on that API and carry an
encoded representation without knowing or switching on individual TimingData
fields.

`UpstreamProtocol` is a Domain capability owned by one `TimingSystem` and built partly on `TimingData`. It adds synchronization/reconciliation and protocol-level messages such as ping/pong so individual TimingNodes do not need to implement those concerns. `UpstreamGateway` owns the external transport boundary and uses 1..N concrete connectors. A connector such as `RabbitMqConnector` owns transport/session mechanics, not TimingData or UpstreamProtocol semantics. `UpstreamMessageRouter` resolves semantic TimingNode-targeted work by `TimingNodeId` inside the already selected TimingSystem context; `TimingSystemId` is not required on the wire. `TimingNode.UpstreamMessagePort` remains the bidirectional semantic upstream-message port of one TimingNode.

If the TimingNode capability later grows into several cohesive areas, deeper
packages such as `timing/registration` or `timing/stage` may become useful.
Do not create those packages before the corresponding code exists.

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
  domain model, semantic ports, TimingData representation/codec and UpstreamProtocol semantics

core
  runtime/execution contracts

io
  hardware, messaging and storage adapters

infra
  cross-cutting technical support and framework bootstrap/composition

runtime
  top-level composed runtime object and lifecycle mechanics

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
  -> provider-neutral LoggingConfig values

event-timing-app.jar / runtime composition
  -> selects exactly one SLF4J provider
  -> initial provider: slf4j-jdk14
  -> backend: java.util.logging
  -> RuntimeLogging / LoggingControl
       +-- ConsoleHandler
       +-- FileHandler
       +-- LiveLogHandler + DiagnosticLogServer
```

Working rules:

- framework code may compile against the SLF4J API but must not force a concrete provider/backend on consumers;
- provider-neutral deployment values such as semantic level, log-file path/rotation and optional live-listener bind/port may live in the framework-owned effective configuration model;
- the executable application chooses and configures the provider/backend before `ApplicationBootstrap` starts normal runtime composition;
- the initial Java-8/Pi-Zero baseline uses `slf4j-jdk14` so the provider delegates to JDK `java.util.logging` without introducing Logback;
- concrete JUL types such as `FileHandler`, `Handler`, backend `Level` and socket lifecycle stay in the executable implementation, not in reusable domain/framework contracts;
- `LoggingControl` owns the configured global level plus an optional temporary runtime override; applying an override changes the running logger threshold without mutating deployment configuration;
- the optional diagnostic listener is a logging-specific engineering facility. The test client initiates its TCP connection, log delivery is best effort, and network failure must not be allowed to block ordinary log publishers;
- the live diagnostics protocol is separate from the IF-03 status/event wire model;
- another executable/private consumer may select another compatible provider later without changing framework/domain source;
- exactly one provider should be present in a runtime composition;
- provider/backend versions are pinned centrally by Maven dependency management rather than scattered through modules.

This keeps logging technology replaceable at the executable boundary while giving reusable
framework code one consistent facade and one small provider-neutral configuration contract.

## Default executable application

`event-timing-app` is the first executable consumer of the framework library.

Its package root remains:

```text
io.github.brainboxemb.eventtiming.app/
  TimingApplication.java
  TimingApplicationLifecycle.java
  bootstrap/
    ApplicationBootstrap.java
    ApplicationConfig.java
    ApplicationConfigLoader.java
    PresentationConfig.java
    RemoteShellConfig.java
    RemoteApiConfig.java
    RemoteApiHttpConfig.java
    RemoteApiWebSocketConfig.java
```

The framework owns the reusable SI-01 runtime and bootstrap components:

```text
io.github.brainboxemb.eventtiming/
  runtime/
    TimingApplication.java
    TimingApplicationLifecycle.java
  infra/
    bootstrap/
      ApplicationBootstrap.java
      config/
        ApplicationConfig.java
        PresentationConfig.java
        RemoteShellConfig.java
        RemoteApiConfig.java
        RemoteApiHttpConfig.java
        RemoteApiWebSocketConfig.java
        LoggingConfig.java
        LoggingFileConfig.java
        LoggingLiveConfig.java
```

`runtime/` is a Java source-organisation package for the top-level runtime
objects; it is **not** an additional architecture layer or box in Figure SI01-01.
The figure already describes the contents/responsibilities of that running
`TimingApplication`.

The executable artifact is deliberately thin:

```text
io.github.brainboxemb.eventtiming.app/
  TimingApplicationMain.java
  bootstrap/
    YamlApplicationConfigLoader.java
    EmbeddedBuildIdentityLoader.java
  logging/
    RuntimeLogging.java
    LiveLogHandler.java
    DiagnosticLogServer.java
```

The executable startup flow is:

```text
main()
  -> EmbeddedBuildIdentityLoader
  -> YamlApplicationConfigLoader
       -> validated ApplicationConfig
  -> RuntimeLogging
       -> configure JUL level + console/file/live handlers
  -> framework ApplicationBootstrap
       -> select/construct concrete presentation/I/O/platform implementations
       -> create reusable application/domain/runtime objects
       -> install/start presentation and shutdown handling
  -> TimingApplication runtime
```

`BuildIdentity` and `ApplicationConfig` are different inputs. Build identity is artifact provenance; application configuration is deployment composition defined by IF-11. The executable embeds deterministic provenance fields (`application`, `version`, exact `revision`, `sourceRef`, `buildOrigin`, `dirty`, `apiVersion`). Wall-clock build time, CI run/build id and actor/user are not embedded because they are per-run metadata rather than stable build inputs/context.

Reusable application behaviour should not migrate into the executable merely because the architectural responsibility is called `application`. When a reusable framework application/runtime object becomes justified by real shared behaviour, executables should **compose** that object rather than extend a `BaseApplication` hierarchy.

The framework keeps the small `TimingApplication.Builder` only for constructing
the runtime object itself. `ApplicationBootstrap` is the concrete cross-cutting
composition component around it and consumes the framework-owned effective
`ApplicationConfig`.

Concrete syntax/parsing is intentionally outside the framework. The default
`event-timing-app` launcher currently uses SnakeYAML through
`YamlApplicationConfigLoader`, maps that input into the framework configuration
model, loads embedded build provenance through `EmbeddedBuildIdentityLoader`,
and then delegates to `ApplicationBootstrap`. This keeps format/tooling
dependencies such as SnakeYAML out of the reusable framework while making the
architectural bootstrap/configuration model reusable.

The implemented presentation structure is:

```text
presentation/
  interfaces/
    console/
      LocalConsole
    shell/
      RemoteShellServer
    remoteapi/
      RemoteApiHttpServer
      RemoteApiWebSocketServer
      RemoteApiMessageWriter
  common/
    terminal/
      TerminalSession
```

Console and remote shell are separate presentation interfaces. They share only the
line-oriented command-session behaviour in `presentation.common.terminal`; both call
the same `CommandHandler` and shutdown callback.

A06/A07 are the first slice of the functional **Remote API**:

```text
RemoteApiHttpServer
  +-- GET /api/v1/version
  +-- GET /api/v1/status
            \
             +--> CommandHandler.version() / status()
            /
RemoteApiWebSocketServer
  +-- WS /api/v1/events
  +-- STATUS_SNAPSHOT on connect/reconnect
  +-- STATUS_CHANGED only for real status changes
```

`RemoteApiMessageWriter` owns the IF-03 wire/JSON representation shared by the Remote
API HTTP and WebSocket transports. It is not application/control logic and therefore
does not live in the application layer or in global presentation common code.

The first WebSocket implementation uses `Java-WebSocket 1.6.0` in the reusable
framework and keeps the accepted A06 JDK HTTP server unchanged rather than replacing
both transports with a larger combined stack.

A browser-based engineering client, if added, should consume the Remote API like any other external client. It does not require a separate SI-01 `presentation.web` package.

Manual inspection is provided by an independent development tool:

```text
test-client/
  TestClientApplication      plain Java launcher
          |
          v
  TestClientFxApplication    JavaFX development view
          |
          +-- RemoteApiClient          HTTP/JSON client
          +-- RemoteApiEventClient       Java 17 WebSocket client
          +-- RemoteShellClient          A05 raw TCP shell client
          |
          v
        SI-01
```

`test-client/` is a standalone Java-17 Maven project, not a module in the Java-8
SI-01 reactor. It has no dependency on `event-timing-framework` or
`event-timing-app`; this preserves the external-client boundary and makes later
extraction to a dedicated repository straightforward if the tool grows. It is engineering support rather than the planned SI-02 GUI, and its JavaFX choice does not select the SI-02 GUI technology.

The shared presentation/application boundary remains small:
`CommandHandler.version()` returns build identity and
`CommandHandler.status()` returns the current TimingNode status used by the
current presentation adapters.

## Derived consumers

The framework is deliberately not tied to one executable topology. Plausible consumers include:

```text
single-system application
multi-system / simulation application
public reference/test application
private/product application
```

These are consumer possibilities, not modules to create now.

## Public/private composition

Expected private/product-specific areas may include:

- production RFID control/protocol details;
- product-specific I/O/protocol implementations;
- production asset/source inventory and mappings;
- production upstream/backoffice schemas/codecs where sensitive;
- deployment-specific composition/policies.

Prefer normal composition and constructor/factory injection. Do not introduce a subclass-based `BaseApplication` extension model or runtime plugin discovery unless a real requirement appears.

## Possible future artifacts

Create future artifacts only when a real boundary requires them. Candidates might eventually include:

- RabbitMQ/messaging I/O;
- Linux/Raspberry-Pi platform support;
- public/private RFID/CAN I/O implementations;
- stable Java API/SPI;
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
- the executable consumes `event-timing-framework` rather than copying/forking framework source;
- the framework artifact does not carry a concrete SLF4J provider/backend transitively;
- an executable runtime contains exactly one intended SLF4J provider.

## Open detailed-design decisions

- exact package granularity after real application/domain classes exist;
- final package naming where capability-oriented packages prove clearer than layer names;
- exact reusable boundary between single-instance runtime mechanics and multi-system application orchestration;
- how applications select/inject presentation/I/O/platform implementations;
- private Maven artifact publication/consumption mechanism;
- version alignment between public framework and private implementations;
- which I/O capabilities eventually deserve independent artifacts;
- whether and when a dedicated public Java API/SPI artifact becomes justified;
- exact field logging configuration/rotation/retention policy in the default executable.

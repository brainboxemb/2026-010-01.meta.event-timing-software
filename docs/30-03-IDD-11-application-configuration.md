# Application Configuration Interface (IDD)

Status: review candidate / SIP Step-3 configuration baseline

System interface: **IF-11 — Application Configuration**

## Purpose

This Interface Design/Description Document defines the deployment/configuration contract consumed by SI-01. It describes how a deployment identifies TimingNodes, I/O assets, presentation bindings, runtime settings and secret references before application composition starts.

It deliberately does **not** define domain behaviour, a Java class hierarchy, a specific YAML library or production secret values.

## Inputs

IF-11 is a system-owned deployment/configuration interface allocated by
`30-02-SSSD-software-system-specification-document.md`. Applicable system use cases and
deployment constraints provide upstream intent. The SI-01 SISD consumes this contract;
its internal architecture and Java SDD are downstream and are not inputs to the IDD.

## Boundary

```text
deployment configuration
        |
        | IF-11
        v
SI-01 configuration loading
        |
        v
effective ApplicationConfig
        |
        v
validation
        |
        v
application composition
```

Build provenance is outside IF-11. `BuildIdentity` comes from the built application artifact and remains separate from deployment configuration.

## Effective configuration model

The logical configuration root is:

```text
ApplicationConfig
├── applicationId
├── timingNodes
├── io
│   ├── devices
│   │   └── antennaManager
│   │       └── antennas
│   ├── deviceNetworks
│   │   ├── can
│   │   └── network
│   ├── registrationRouting
│   ├── messaging
│   │   └── upstream
│   │       └── connectors
│   └── storage
├── presentation
├── logging
├── runtime
└── security
```

The structure is a contract for configuration ownership. It does not require one Java POJO for every node before a running slice needs it.

### Application identity

`ApplicationId` identifies the configured Headless Timing Application instance.
It is a separate identity/type from `TimingNodeId`.

For the current single-TimingNode deployment style, the intended starting
convention is to configure the same string value for `ApplicationId` and the
single `TimingNodeId`. This equality is a deployment convention, not identity
aliasing: multi-TimingNode deployments may use one application id with several
different TimingNode ids.

Representative direction:

```text
applicationId: timing-node-01
```

### TimingNodes

Each configured TimingNode has its own stable identity and deployment context.

Representative fields:

```text
timingNodes
  timing-node-01
    timingNodeId
    locationId
```

Rules:

- `TimingNodeId` identifies the logical TimingNode;
- `LocationID` identifies the configured physical/event location and is not derived from `TimingNodeId`;
- presentation transport settings such as HTTP ports do not belong to the TimingNode.

### I/O

I/O configuration selects concrete external I/O implementations and their
TimingNode mappings.

Representative device configuration direction:

```text
io
  devices
    antennaManager
      antennas
        ANT1
          type: rfid
          timingNodes: [timing-node-01, timing-node-02]
        ANT2
          type: rfid
          timingNodes: [timing-node-02]

  deviceNetworks
    can
      enabled: true

    network
      enabled: true
```

`AntennaManager` is the configured owner of the antenna set and may define 0..N antennas. `AntennaId` is distinct from
`TimingNodeId`. One antenna may intentionally map to 1..N TimingNodes; this
fan-out does not merge their state or sequence streams.

The `deviceNetworks.can` section configures the network owned by
`CanNetworkController`; exact bus/driver/discovery fields are added when that
implementation slice exists.

The `deviceNetworks.network` section configures `NetworkDeviceService`, the
bidirectional network-device boundary. Detailed service discovery,
listen/session and protocol-framing settings are added only when IF-09 becomes
concrete. IF-09 remains an IP/network interface and does not require a physical
Wi-Fi router or WLAN. Exact mDNS service naming and network application protocol
remain deferred rather than being invented in IF-11 now.

Concrete antenna configuration owns its driver/protocol/device settings. A
separate registration-asset identity is not part of the active software
configuration model.

### Upstream messaging

**Upstream** identifies the central/external system relationship from SI-01's
perspective; it does not define the direction of each message. The relationship
is bidirectional.

When upstream messaging is enabled, SI-01 composes one `UpstreamGateway` using
1..N connectors plus one application-level `UpstreamMessageRouter`.
Configuration selects the concrete transports and any transport-specific
addressing/mapping needed at the external boundary; target resolution to
application/domain responsibilities remains an application concern.

Representative direction:

```text
io
  messaging
    upstream
      connectors
        connector-01
          type: rabbitmq
          credentials: rabbitmq-main
        connector-02
          type: socket
```

`UpstreamGateway` owns the external upstream-system boundary after a connector has
converted external protocol data into an application-facing message.
`UpstreamMessageRouter` resolves the internal target: `ApplicationId` can
address an application-scoped Domain responsibility, while `TimingNodeId`
resolves to the corresponding TimingNode's bidirectional
`UpstreamMessagePort`.

A connector owns transport resources such as RabbitMQ connections/channels or a
socket session. It does not own Domain/TimingNode selection or message
semantics. The router is upstream-specific and is not used as a generic internal
application message bus.

Storage settings remain under I/O because they configure external persistence.

### Presentation

Presentation configuration follows the same function-first ownership as the presentation architecture. Transport configuration is nested under the functional interface that owns it.

Representative direction:

```text
presentation
  web
    endpoints (1 per TimingNode)
      web-timing-node-01
        timingNodeId: timing-node-01
        bindAddress
        port
      ...
  remoteApi
    http
    webSocket
  remoteShell
```

The intended Web topology has exactly one configured Web binding for each
configured TimingNode. Each binding references a `TimingNodeId` and owns its
own bind address/port; a multi-TimingNode process therefore exposes 1..N Web
ports. Those listener settings remain Presentation configuration and do not
become fields of the TimingNode domain object.

A TimingNode therefore does not need to know that an HTTP listener, WebSocket, shell or external GUI/test client exists. Presentation interfaces map their requests to the application boundary.

The currently implemented A05-A07 subset is:

```yaml
presentation:
  remoteShell:
    bindAddress: 127.0.0.1
    port: 8023
  remoteApi:
    http:
      bindAddress: 127.0.0.1
      port: 8081
    webSocket:
      bindAddress: 127.0.0.1
      port: 8082
```

`remoteShell` and `remoteApi` are independently optional. Within `remoteApi`, HTTP
and WebSocket listeners are independently optional; when present, each requires its
`bindAddress` and `port`. The committed development example uses loopback for all listeners. External GUI/test clients connect to the Remote API and do not require their own SI-01 presentation configuration section. These settings configure presentation listeners and do not become TimingNode fields.

### Logging

Logging is cross-cutting deployment configuration and is not TimingNode/domain state.
The A08 baseline configures a startup level, a retained file sink and an optional
engineering live-diagnostics listener.

Representative direction:

```yaml
logging:
  level: INFO
  file:
    path: logs/event-timing.log
    rotateBytes: 1048576
    retainedFiles: 5
  live:
    bindAddress: 127.0.0.1
    port: 8030
```

Rules:

- `level` is the configured global startup level; the implementation accepts the
  semantic levels `TRACE`, `DEBUG`, `INFO`, `WARN` and `ERROR`;
- `file.path` identifies the operational log-file pattern/location; its parent
  directory may be created by the executable;
- `rotateBytes` and `retainedFiles` define basic size rotation/retention and
  must be positive;
- `live` is optional and owns its own bind address/listen port. The development
  example is loopback-only;
- an engineering client initiates the live connection to SI-01 and may query/set
  a temporary runtime log-level override on that diagnostics connection;
- runtime level overrides are process state only: they are not written back into
  IF-11 configuration and restart restores the configured `logging.level`;
- live log delivery is best effort and is not the durable log store;
- this diagnostics listener is separate from Presentation/IF-03 status/events;
  configuring it does not add fields to a TimingNode.

Per-package levels, persistent runtime overrides and general-purpose diagnostics
routing are deliberately outside the A08 baseline.

### Runtime

Runtime configuration contains process/executor/queue settings that affect application execution but are not domain identity.

Exact fields remain capability-driven and should be added when the corresponding runtime behaviour exists.

### Security and credentials

Committed configuration may state **which** credential is required, but not contain production secrets.

Example:

```text
rabbitmq
  host: rabbit.example
  port: 5672
  virtualHost: /timing
  username: timing-node
  passwordSecret: RABBITMQ_PASSWORD
```

The referenced secret value is resolved from environment/deployment secret storage at startup. The same principle applies later to HTTP authentication, upstream/backoffice credentials, certificates and similar sensitive values.

This baseline does not require a general `SecretProvider` hierarchy.

## Configuration sources and precedence

One deployment resolves at most these layers:

```text
base application configuration
        ↓
one platform override
        ↓
optional one profile override
        ↓
secret resolution
        ↓
effective ApplicationConfig
```

Typical source layout may be:

```text
config/
  application.yml
  platform/
    pi-zero.yml
    windows.yml
  profile/
    simulation.yml
```

The exact file format and parser/library remain implementation choices until the first real loader is selected.

General recursive inheritance, arbitrary include graphs and Kubernetes-like overlay machinery are intentionally outside this baseline.

## Platform and profile semantics

Platform and profile answer different questions:

- **platform** — the execution/deployment environment, such as Pi Zero or Windows;
- **profile** — a selected composition/behaviour variant, such as simulation or development.

Windows does not imply simulation.

A simulation profile replaces concrete adapters while preserving the same application/domain model:

```text
production: TimingNode -> real RFID adapter
simulation: TimingNode -> simulated RFID adapter
```

The same TimingNode identities, application commands and domain behaviour remain in use.

## Validation

SI-01 validates the complete effective configuration before normal application composition proceeds.

Validation includes, where applicable:

- missing/invalid `ApplicationId`;
- duplicate `TimingNodeId` values;
- references to unknown TimingNodes;
- invalid/duplicate `AntennaId` values;
- empty or invalid antenna-routing targets;
- invalid CAN device-network settings when CAN is enabled;
- invalid network-device service settings when the network device service is enabled;
- duplicate/conflicting upstream connector identifiers;
- upstream message mappings/targets that reference unknown TimingNodes;
- conflicting presentation/logging listener bind address/port combinations;
- invalid logging level, file rotation/retention values or live-listener settings;
- unsupported adapter/driver types;
- missing required secret references or unresolved required secret values;
- invalid runtime values such as impossible queue/executor settings.

Configuration loading, configuration validation and application composition are distinct responsibilities even when the initial implementation keeps them small.

## Startup contract

Conceptually startup is:

```text
main()
  -> obtain BuildIdentity from the built artifact
  -> load IF-11 configuration sources
  -> produce effective ApplicationConfig
  -> validate effective configuration
  -> configure executable runtime logging
  -> compose TimingApplication and selected adapters
  -> start application lifecycle
```

The executable may use a dedicated `ApplicationConfigLoader` once real configuration loading/overlay behaviour exists. A class must not be introduced merely to mirror this document before it owns real behaviour.

Reusable application/runtime behaviour should be shared through composition. IF-11 does not define or require a `BaseApplication` inheritance hierarchy.

## Public/private boundary

Public configuration examples use synthetic identities and endpoints.

Real deployment identities, production topology, credentials, encryption keys, proprietary mappings and private protocol values remain outside the public repositories.

## First Step-3 implementation slice

The first implementation should introduce only the configuration objects and fields needed by the executable slice being built.

At minimum, Step 3 needs enough configuration to:

- start from external configuration;
- construct the application with a stable `ApplicationId`;
- construct at least one configured TimingNode with a stable `TimingNodeId`;
- bind the first IF-03 presentation endpoint safely;
- report configuration/startup failures through the first executable behaviour.

Hardware, messaging, storage and security sections may remain unimplemented until a real Step-3/later consumer needs them; their ownership and identity rules are defined here so those additions do not distort the domain model later.

## Traceability

| IF-11 concern | SI-01 SISD requirement / architecture |
| --- | --- |
| external effective configuration | SI01-REQ-001 |
| configured TimingNode identity | SI01-REQ-003 |
| presentation listen/binding settings | SI01-REQ-032 + IF-03 |
| deployment/composition separation | SI-01 SISD configuration/composition architecture |
| Java composition/type growth | SI-01 Java component SDD |


# Application Configuration Interface (IDD)

Status: review candidate / SIP Step-3 configuration baseline

System interface: **IF-11 — Application Configuration**

## Purpose

This Interface Design/Description Document defines the deployment/configuration contract consumed by SI-01. It describes how a deployment identifies TimingNodes, I/O assets, presentation bindings, runtime settings and secret references before application composition starts.

It deliberately does **not** define domain behaviour, a Java class hierarchy, a specific YAML library or production secret values.

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
├── timingNodes
├── io
│   ├── hardware
│   ├── registrationRouting
│   ├── backoffice
│   │   └── connectors
│   └── storage
├── presentation
├── runtime
└── security
```

The structure is a contract for configuration ownership. It does not require one Java POJO for every node before a running slice needs it.

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

Representative antenna configuration:

```text
io
  antennaRouter
    antennas
      ANT1
        type: rfid
        timingNodes: [timing-node-01, timing-node-02]
      ANT2
        type: rfid
        timingNodes: [timing-node-02]
```

`AntennaRouter` owns 0..N configured antennas. `AntennaId` is distinct from
`TimingNodeId`. One antenna may intentionally route to 1..N TimingNodes; this
fan-out does not merge their state or sequence streams.

Concrete antenna configuration owns its driver/protocol/device settings. A
separate registration-asset identity is not part of the active software
configuration model.

### Backoffice connectors and routing

A deployment may configure 0..N backoffice connectors under one router:

```text
io
  backofficeRouter
    connectors
      connector-01
        type: rabbitmq
        credentials: rabbitmq-main
        bindings
          - timingNode: timing-node-01
            externalName: START
          - timingNode: timing-node-02
            externalName: FINISH
      connector-02
        type: rabbitmq
        credentials: rabbitmq-secondary
        bindings
          - timingNode: timing-node-01
            externalName: NODE-A
```

`BackofficeRouter` owns the connector collection and binding mapping. A
connector may bind 1..N TimingNodes and one TimingNode may be bound to more than
one connector. `externalName` is connector/backoffice-facing configuration and
does not replace the stable internal `TimingNodeId`.

Concrete connector implementations own transport resources such as RabbitMQ
connections/channels internally.

Storage settings remain under I/O because they configure external persistence.

### Presentation

Presentation configuration binds client-facing endpoints to application targets.

Representative structure:

```text
presentation
  endpoint-01
    type: http
    timingNode: timing-node-01
    port: 8081
  endpoint-02
    type: http
    timingNode: timing-node-02
    port: 8082
```

The binding direction is:

```text
HTTP :8081 -> timing-node-01
HTTP :8082 -> timing-node-02
```

A TimingNode therefore does not need to know that a tablet, HTTP listener, shell or later GUI/API endpoint exists. Additional presentation adapters may bind differently without changing the TimingNode domain configuration.

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

The referenced secret value is resolved from environment/deployment secret storage at startup. The same principle applies later to HTTP authentication, backoffice credentials, certificates and similar sensitive values.

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

- duplicate `TimingNodeId` values;
- references to unknown TimingNodes;
- invalid/duplicate `AntennaId` values;
- empty or invalid antenna-routing targets;
- duplicate/conflicting backoffice connector identifiers or bindings;
- connector bindings that reference unknown TimingNodes;
- conflicting presentation bind address/port combinations;
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
- construct at least one configured TimingNode with a stable `TimingNodeId`;
- bind the first IF-03 presentation endpoint safely;
- report configuration/startup failures through the first executable behaviour.

Hardware, messaging, storage and security sections may remain unimplemented until a real Step-3/later consumer needs them; their ownership and identity rules are defined here so those additions do not distort the domain model later.

## Traceability

| IF-11 concern | SI-01 requirement / architecture |
| --- | --- |
| external effective configuration | SI01-REQ-001 |
| configured TimingNode identity | SI01-REQ-003 |
| presentation listen/binding settings | SI01-REQ-032 + IF-03 |
| deployment/composition separation | SI-01 SAD configuration/composition architecture |
| Java composition/type growth | SI-01 Java component SDD |


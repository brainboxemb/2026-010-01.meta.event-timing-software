# Application Configuration Interface Specification (ISD)

Status: review candidate

System interface: **IF-11 — Application Configuration**


## Purpose

This Interface Specification Document defines the deployment/configuration contract consumed by SI-01. It describes how a deployment identifies internal TimingSystems and their TimingNodes, I/O assets, presentation bindings, runtime settings and secret references before application composition starts.

It deliberately does **not** define domain behaviour, a Java class hierarchy, a specific YAML library or production secret values.

## Terms and abbreviations

- **IF** — system interface
- **ISD** — Interface Specification Document
- **SI** — Software Item
- **ApplicationConfig** — effective resolved application configuration


## Relationship to other documents

IF-11 is a system-owned deployment/configuration interface allocated by
`31-SSSD-software-system-specification-document.md`. Applicable system use cases and
deployment constraints provide upstream intent. The SI-01 SSD consumes this contract;
its internal architecture and Java SDD are downstream and are not inputs to the ISD.

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

## Source template parameters

The external YAML source may define a small `parameters` mapping for deployment-local
string constants. Parameters are resolved before the effective `ApplicationConfig` is
created, so template syntax never becomes runtime/domain state.

Example:

```yaml
parameters:
  ID: A

timingSystems:
  - id: "{ID}"
    timingNodes:
      - id: "{ID}"
```

Rules:

- parameter names are non-blank identifiers and parameter values are YAML strings;
- a string scalar may reference a configured parameter as `{Name}`;
- parameter substitution is deterministic text replacement only: it does not evaluate
  expressions, execute code, load includes or introduce recursive inheritance;
- unknown or unresolved parameter references are configuration errors;
- topology uses ordered `timingSystems` and `timingNodes` YAML lists;
  each entry declares its identity with the contextual `id` field,
  not by a deployment-local mapping key;
- `{NodeId}` and `{SystemId}` are reserved contextual placeholders. They are resolved only
  where the owning field defines that context, currently TimingData storage paths;
- after substitution, the normal field-specific IF-11 validation rules still apply.

For a single-system/single-node configuration, `ID: A` makes both
`timingSystems[].id: "{ID}"` and `timingNodes[].id: "{ID}"` resolve to `A`.
Multi-system deployments may define separate parameters or explicit IDs as needed.

## Effective configuration model

The logical **effective** configuration root is:

The outline below names the *typed model concepts* (`timingSystemId` and
`timingNodeId`); the source YAML uses the shorter `id` declaration keys.


```text
ApplicationConfig
├── applicationId
├── timingSystems
│   └── <timingSystem>
│       ├── timingSystemId
│       ├── eventDataProvider
│       ├── timingDataProvider
│       ├── upstreamProtocolProvider
│       └── timingNodes
│           └── <timingNode>
│               ├── timingNodeId
│               ├── locationId
│               └── tagProcessing
├── io
│   ├── devices
│   │   └── antennaManagers
│   │       └── <managerBinding>
│   │           ├── timingSystemId
│   │           ├── antennas
│   │           └── inventoryGroup (optional)
│   ├── deviceNetworks
│   │   ├── can
│   │   └── network
│   ├── messaging
│   │   └── upstream
│   │       └── connectors
│   └── storage
│       └── timingData
│           ├── path (single-TimingNode shorthand)
│           └── nodes (multi-TimingNode mapping)
│               └── <storageBinding>
│                   ├── timingNodeId
│                   └── path
├── presentation
├── logging
├── runtime
└── security
```

The structure is a contract for configuration ownership. It does not require one Java POJO for every node before a running slice needs it.

### Application profile and baseline capabilities

A Timing Point Application may use a selected **application profile** as a
versioned default composition template. A profile can supply topology,
capability and compatibility defaults without introducing another domain model,
Java application subclass or software item.

This public baseline deliberately does not define concrete event/deployment
profile IDs, fixed TimingNode counts, device combinations or allowed LocationId
sets. Those details are added only when an explicit public requirement owns them;
private deployment profiles and compatibility mappings remain outside this
repository.

Explicit deployment configuration may override profile defaults where the
profile contract allows it. It must not bypass compatibility rules owned by the
selected profile.

Console, Remote Shell and API are baseline Timing Point Application capabilities,
not implicitly tied to one profile. Deployment configuration still controls
concrete listener/binding settings and may explicitly leave a network listener
unbound/disabled where appropriate.

Web remains a separate browser-facing capability whose per-TimingNode bindings
are composed when that capability is used.

### Application identity

`ApplicationId` identifies the configured Timing Point Application instance.
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

### TimingSystems and TimingNodes

The application composes 1..N internal `TimingSystem` contexts. Each
TimingSystem owns 1..N TimingNodes plus its own system-status/upstream-protocol
state. `TimingSystemId` is a local composition/simulation identity and is not
part of the upstream functional addressing contract.

Representative source:

```yaml
parameters:
  ID: A

timingSystems:
  - id: "{ID}"
    eventDataProvider: reference
    timingDataProvider: reference
    upstreamProtocolProvider: reference
    timingNodes:
      - id: "{ID}"
        tagProcessing:
          quietTimeoutMillis: 250
          maxBurstDurationMillis: 1000
          duplicateWindowMillis: 15000
          sweepCadenceMillis: 50
          observationQueueCapacity: 256
```

The same structure naturally represents multiple systems and nodes:

```yaml
timingSystems:
  - id: 9
    timingNodes:
      - id: A
      - id: B
  - id: C
    timingNodes:
      - id: C
```

In the topology declarations, `id` means **TimingSystemId** within a
`timingSystems` entry and **TimingNodeId** within a `timingNodes` entry.
This changes only the YAML field names, not the typed runtime identities.
References from other sections remain explicit: for example
`io.devices.antennaManagers.*.timingSystemId` and
`io.storage.timingData.nodes.*.timingNodeId`.

Rules:

- `timingSystems` and each nested `timingNodes` are non-empty YAML lists;
  their elements are YAML objects with explicit identity fields;
  mapping-based topology collections are not part of the IF-11 syntax;
- `TimingSystemId` is one character `A`..`Z` or `1`..`9` and unique among
  all TimingSystems hosted by the application;
- a TimingSystem with **one TimingNode** uses exactly the **same ID** as that node
  (system `A` contains node `A`, system `B` contains node `B`);
- a TimingSystem with **multiple TimingNodes** uses a **different** ID that does
  not equal any TimingNode ID in the application (for now, system `9`
  containing nodes `A` and `B`); no `SID-` prefix is used;
- `TimingSystemId` distinguishes hosted/simulated TimingSystem contexts locally;
- each TimingSystem contains 1..N TimingNodes;
- `TimingNodeId` identifies the logical TimingNode, is exactly one character `A`..`Z` or `1`..`9`, and remains application-wide unique;
- `LocationId` identifies the configured physical/event location and is not derived from `TimingNodeId`;
- each configured `LocationId` must satisfy any compatibility constraint of the selected built-in application profile;
- presentation transport settings such as HTTP ports do not belong to the TimingNode;
- the internal TimingSystem grouping does not add a TimingSystem identifier to TimingData or upstream wire messages.

### TimingNode tag-processing policy

`tagProcessing` belongs to one configured TimingNode because it controls that
TimingNode's TagProcessor semantics and bounded observation ingress. It is not
antenna/I/O routing configuration.

The reusable implementation owns usable compiled defaults. A deployment therefore
does not need to repeat these values merely to start:

```yaml
tagProcessing:
  quietTimeoutMillis: 250
  maxBurstDurationMillis: 1000
  duplicateWindowMillis: 15000
  sweepCadenceMillis: 50
  observationQueueCapacity: 256
```

The values above are the public first-executable defaults. A selected application
profile/platform/mode or explicit deployment configuration may override them where
that source deliberately specializes the policy.

Validation rules are:

- `quietTimeoutMillis`, `maxBurstDurationMillis` and `sweepCadenceMillis`
  must be positive;
- `duplicateWindowMillis` may be zero but must not be negative;
- `observationQueueCapacity` must be positive.

IF-11 owns the **effective startup configuration** only. After startup, IF-03 may
apply a temporary runtime override to fields explicitly marked runtime-adjustable.
Such an override changes current process state; it does not rewrite IF-11 deployment
configuration. Restart resolves the startup value again from compiled defaults plus
the configured override sources.

The current runtime-mutability baseline is:

| Field | Live override | Reason |
| --- | --- | --- |
| `quietTimeoutMillis` | yes | policy evaluation can change on the TagProcessor lane |
| `maxBurstDurationMillis` | yes | policy evaluation can change on the TagProcessor lane |
| `duplicateWindowMillis` | yes | duplicate-window evaluation can change on the TagProcessor lane |
| `sweepCadenceMillis` | yes | housekeeping registration can be replaced on the TagProcessor lane |
| `observationQueueCapacity` | no | it sizes the owned bounded queue and currently requires restart/recomposition |

A runtime API query may expose both the effective startup value and the currently
active value. Secrets remain excluded/redacted according to their own interface
rules.

### I/O

I/O configuration selects concrete external I/O implementations and their
TimingNode mappings.

Representative device configuration direction:

```text
io
  devices
    antennaManagers
      system-one-antennas
        timingSystemId: 9
        antennas
          1
            provider: simulated
            type: rfid
            timingNodes: [A, B]
            power
              controlRef: antenna-power-1
              stabilizationMillis: 1000
          2
            provider: simulated
            type: rfid
            timingNodes: [B]
            power
              controlRef: antenna-power-2
              stabilizationMillis: 1000
        inventoryGroup
          members: [1, 2]
          intervalMillis: 500

  deviceNetworks
    can
      enabled: true
      protocolProvider: reference

    network
      enabled: true
      displayProtocolProvider: reference
```

`AntennaManager` is an optional I/O capability per TimingSystem. The
`antennaManagers` mapping makes that ownership explicit: each binding contains
one `timingSystemId` reference, and the binding key itself is deployment-local
only. A TimingSystem may have zero or one manager binding. When present the
manager owns 1..N antennas and accepts one shared inventory demand: enabled while
any TimingNode of that system is OPEN, otherwise disabled. Internal multiplex
rotation is distinct from future individual antenna-control features.

`AntennaId` is exactly one digit `1`..`9` and is distinct from
`TimingNodeId`. One antenna may intentionally map to 1..N TimingNodes within
the manager's referenced TimingSystem; this fan-out does not merge their state
or sequence streams.

Antenna installation fields have these semantics:

- `timingSystemId` on the manager binding must reference one configured
  TimingSystem and may occur only once across manager bindings;
- `timingNodes` routes antenna observations to one or more TimingNodes that
  belong to that same TimingSystem; this mapping does not imply independently
  starting/stopping inventory per antenna;
- `power.controlRef` optionally references an installation-owned external power
  capability rather than reader/vendor protocol;
- `power.stabilizationMillis` defines how long SI-01 waits after external power-on
  before self-testing or initializing that antenna.

One AntennaManager may define **zero or one** `inventoryGroup`. When present:

- `members` identifies 2..N configured antennas that cannot inventory concurrently;
- `intervalMillis` is the rotation interval between configured group members;
- the public/reference two-antenna baseline is 500 ms;
- antennas not listed in the group may inventory independently.

Omitting `inventoryGroup` means no mutual-exclusion multiplexing is required. The
configuration contract deliberately does not define several independently named groups
until a concrete deployment requirement needs that capability.

Omitting `power` means the antenna/provider is responsible for any internal power
mechanism or is continuously powered.

Startup self-test is per antenna and is diagnostic. A failed self-test does not
permanently disable that antenna and does not prevent a later inventory attempt.
Failure of one antenna does not prevent independent operation or later attempts of
other antennas merely because they share one AntennaManager.

The `deviceNetworks.can` section configures the CAN network boundary. Exact
bus/driver/discovery fields belong to the concrete device-network design.

The `deviceNetworks.network` section configures the bidirectional network-device
boundary. Detailed service-discovery, session and protocol-framing design is
outside IF-11; this interface only owns the deployment values needed to compose
the selected network-device service.

Concrete antenna configuration owns its driver/protocol/device settings. Its
`provider` value selects a registered `AntennaProvider`; `simulated` is the
built-in provider and therefore requires no external extension JAR. A separate
registration-asset identity is not part of the active software configuration
model.

Provider IDs are implementation-selection keys, not domain/device identities.
The same rule applies to configured EventData, TimingData, UpstreamProtocol,
CAN-protocol and display-protocol providers.

For `eventDataProvider`, `reference` selects the built-in public/reference
EventData profile. Alternate/private providers may supply event-specific
TagId/RegistrationId semantics through the same shared EventData contract.

For `timingDataProvider`, `reference` selects the built-in implementation of
the canonical IF-05 representation. An alternate/private TimingData provider may
select another external representation/translator, but it still realises the
same IF-05 `TimingDataRecord` semantics; provider selection does not select a
different public record model.

Provider selection and provider-specific translation configuration are resolved
during bootstrap, before the codec is used by persistence or inspection code.
A provider whose external representation omits information carried by the common
semantic model must receive enough validated configuration to make the
translation reversible. For a local event-time-only representation this may
include an event date/day-selection rule plus an event time zone or fixed
offset. Those values are translation configuration, not TimingNode/domain state.

The configured codec is then a normal immutable translator instance. Runtime
callers pass only `TimingData` or encoded record bytes to `encode`/`decode`;
they do not pass deployment configuration, UI state or the current host date on
every record operation.

The common IF-11 contract does not prescribe one generic bag of provider
configuration keys. A concrete provider owns validation of the configuration it
requires, while bootstrap owns obtaining that configuration, selecting the
provider and failing before composition when the combination is invalid.

Public examples use generic/reference provider IDs; private provider names and
protocol values remain outside this repository.

### Upstream messaging

**Upstream** identifies the central/external system relationship from SI-01's
perspective; it does not define the direction of each message. The relationship
is bidirectional.

When upstream messaging is enabled, configuration associates each upstream
gateway/protocol context with exactly one internal `TimingSystem`. That context
may use 1..N connectors. Lower transport resources may later be shared when that
does not blur the semantic system boundary.

Representative direction:

```text
io
  messaging
    upstream
      gateways
        upstream-01
          timingSystem: timing-system-01
          connectors
            connector-01
              type: rabbitmq
              credentials: rabbitmq-main
            connector-02
              type: socket
```

The `timingSystem` reference is local composition information; it is not added
to the upstream protocol merely for routing. `UpstreamGateway` owns the
external transport/session boundary. The associated Domain `UpstreamProtocol`
handles system-level protocol semantics such as ping/synchronisation, while
`UpstreamMessageRouter` resolves TimingNode-targeted messages by
`TimingNodeId` to the corresponding bidirectional `UpstreamMessagePort`.

A connector owns transport resources such as RabbitMQ connections/channels or a
socket session. It does not own Domain/TimingNode selection or message
semantics. The router is upstream-specific and is not used as a generic internal
application message bus.

Storage settings remain under I/O because they configure external persistence.

### TimingData storage

TimingData persistence remains an I/O/deployment concern. Each configured
TimingNode that uses the reference file store resolves to exactly one authoritative
append-only TimingData file.

A compact path template can resolve storage for one or more TimingNodes:

```yaml
io:
  storage:
    timingData:
      path: data/node-{NodeId}-logbook.jsonl
```

For a single TimingNode `A`, this resolves to `data/node-A-logbook.jsonl`.

For a multi-TimingNode composition, use explicit node bindings:

```yaml
io:
  storage:
    timingData:
      nodes:
        node-a:
          timingNodeId: A
          path: data/node_A_logbook.jsonl
        node-b:
          timingNodeId: B
          path: data/node_B_logbook.jsonl
```

The key below `nodes` is a deployment-local binding name only.
`timingNodeId` is the real application-wide TimingNode reference. The storage
binding does not become part of TimingNode domain state.

Rules:

- a literal `path` without contextual placeholders is the single-TimingNode shorthand
  and is valid only when the effective application composition contains exactly one
  TimingNode;
- a `path` containing `{NodeId}` and/or `{SystemId}` is resolved separately for
  every configured TimingNode and may therefore be used for multi-TimingNode composition;
- every expanded path must still be unique after normal filesystem normalization;
- `nodes` remains the explicit per-node alternative when different path shapes or
  additional deployment-specific bindings are required;
- `path` and `nodes` are mutually exclusive;
- every configured TimingNode using the reference file store must resolve to
  exactly one storage binding;
- every `nodes.*.timingNodeId` must reference a configured TimingNode and may
  occur only once in the storage mapping;
- two bindings must not resolve to the same normalized filesystem path;
- a path may be relative to the application working directory or absolute;
- the configured path selects the file location only; IF-05 and the Java
  persistence design own record encoding, append ordering, recovery and
  corruption handling;
- startup recovery opens/validates each resolved file and rebuilds that
  TimingNode's committed LogBook state before the TimingNode begins accepting
  operational work;
- public examples use generic local paths and do not disclose deployment paths;
- the reference/example filename convention is
  `node-<TimingNodeId>-logbook.jsonl`, for example
  `node-A-logbook.jsonl`; the configured path remains authoritative.

Because `TimingNodeId` is application-wide unique, the same storage mapping
works for one or multiple TimingSystems without adding `TimingSystemId` to the
persistence binding.

The storage path does not contain a LocationId or RegistrationId policy. Those
identifier domains remain event/profile/reference-data concerns.

### Presentation

Presentation configuration follows the same function-first ownership as the presentation architecture. Transport configuration is nested under the functional interface that owns it.

Representative direction:

```text
presentation
  web
    endpoints (1 per TimingNode)
      web-timing-node-01
        timingNodeId: A
        bindAddress
        port
      ...
  api
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

The current executable subset is:

```yaml
presentation:
  remoteShell:
    bindAddress: 127.0.0.1
    port: 8023
  api:
    http:
      bindAddress: 127.0.0.1
      port: 8081
    webSocket:
      bindAddress: 127.0.0.1
      port: 8082
```

Remote Shell and API are baseline software capabilities. Their concrete network
bindings are deployment settings rather than profile choices. A deployment may
explicitly omit/disable a listener binding; when an API HTTP/WebSocket binding is
present it requires its `bindAddress` and `port`. The committed development
example uses loopback for all listeners. External GUI/test clients connect to the
API and do not require their own SI-01 presentation configuration section. These
settings configure presentation listeners and do not become TimingNode fields.

### Logging

Logging is cross-cutting deployment configuration and is not TimingNode/domain state.
The logging configuration provides a startup level, a retained file sink and an optional
engineering live-diagnostics listener.

Representative direction:

```yaml
logging:
  level: INFO
  file:
    path: logs
    rotateBytes: 1048576
    retainedFiles: 5
  live:
    bindAddress: 127.0.0.1
    port: 8030
```

Rules:

- `level` is the configured global startup level; the implementation accepts the
  semantic levels `TRACE`, `DEBUG`, `INFO`, `WARN` and `ERROR`;
- `file.path` identifies the directory used for retained operational text logs;
  the executable creates it when needed;
- each new runtime log file uses local wall-clock date/time in the filename,
  normally `yyyyMMdd-HHmmss.txt` (for example `20250514-101657.txt`);
- retained log records use `HH:mm:ss.SSS - [LEVEL] - message - [sourceClass.sourceMethod]`
  as the compact first-line format; exception stack traces follow when present;
- `rotateBytes` starts a new timestamped file when the current file reaches the configured size,
  and `retainedFiles` limits the number of timestamped files kept in the configured directory;
  both values must be positive;
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

The referenced secret value is resolved from environment/deployment secret storage at startup. The same principle applies to upstream credentials, certificates and similar sensitive values.

This baseline does not require a general `SecretProvider` hierarchy.

## Configuration sources and precedence

Source template parameters are resolved within the explicit deployment YAML before that
source participates in effective-configuration validation. They are a convenience for
writing one source file, not an additional precedence layer and not a runtime override.

The application resolves configuration **from compiled defaults toward explicit
deployment intent**. Explicit deployment values win over lower-precedence defaults,
but they do not override built-in profile compatibility constraints.

```text
compiled component defaults
        ↓
selected built-in application profile defaults
        ↓
selected platform defaults
        ↓
selected operating-mode defaults
        ↓
explicit deployment application.yml overrides
        ↓
secret resolution
        ↓
effective startup ApplicationConfig
```

Runtime overrides are deliberately not another IF-11 source. They are temporary
process state applied after startup through the application-control interface.

This is deliberately not arbitrary inheritance. The compiled component defaults provide a complete usable baseline for settings
that do not require deployment-specific identity or topology. The three selected
default sources then answer orthogonal questions:

- **application profile** — what Timing Point topology/capabilities are normally
  composed for the selected deployment family;
- **platform** — the execution/deployment environment, such as Pi Zero or Windows;
- **operating mode** — how concrete adapters are realised, such as normal/real
  operation versus simulation.

A representative source layout may eventually be:

```text
built-in defaults/
  profile/
    <profile-id>.yml
  platform/
    pi-zero.yml
    windows.yml
  mode/
    normal.yml
    simulation.yml

config/
  application.yml       explicit deployment overrides
```

The default source files above are conceptual/versioned application resources;
their exact storage form is an implementation decision. The external IF-11
deployment contract remains independent of a particular YAML merge library.

General recursive inheritance, arbitrary include graphs, profile-to-profile
inheritance and Kubernetes-like overlay machinery are intentionally outside this
baseline.

## Application profile, platform and operating-mode semantics

The three selectors are intentionally independent:

- **application profile** selects topology/capability defaults;
- **platform** selects execution-environment defaults;
- **operating mode** selects how concrete adapters are realised, for example
  normal operation versus simulation.

Simulation changes concrete adapter/provider defaults while preserving the same
application/domain model:

```text
normal:     TimingNode -> configured Antenna provider
simulation: TimingNode -> built-in SimulatedAntenna
```

A profile may provide a topology skeleton/cardinality, capability defaults and
compatibility constraints. Deployment-specific externally meaningful identities
and locations must either be supplied explicitly or follow a separately
specified deterministic public rule; profile resolution must not invent
ambiguous functional identities.

The exact selector syntax and any concrete public profile set are not defined by
this semantic configuration contract.

## Validation

SI-01 validates the complete effective configuration before normal application composition proceeds.

Validation includes, where applicable:

- missing/invalid `ApplicationId`;
- invalid template parameter names or non-string parameter values;
- unknown or unresolved `{Parameter}` references;
- unresolved contextual `{NodeId}` / `{SystemId}` references outside fields that own
  those contexts;
- missing/invalid, non-compact, or duplicate internal `TimingSystemId` values;
- one-node TimingSystems with IDs different from their TimingNodeId;
- multi-node TimingSystems with IDs matching any configured TimingNodeId;
- TimingSystems without at least one configured TimingNode;
- duplicate application-wide `TimingNodeId` values;
- a configured TimingNode `LocationId` that violates an explicitly defined compatibility rule of the selected application profile;
- references to unknown TimingSystems or TimingNodes;
- AntennaManager bindings that reference an unknown TimingSystem;
- more than one AntennaManager binding for the same TimingSystem;
- invalid/duplicate `AntennaId` values;
- empty or invalid antenna-routing targets;
- antenna-routing targets that do not belong to the manager's referenced
  TimingSystem;
- duplicate discovered provider IDs;
- unknown configured TimingData/UpstreamProtocol/Antenna/CAN/display provider IDs;
- provider/configuration combinations rejected by the selected provider;
- invalid CAN device-network settings when CAN is enabled;
- invalid network-device service settings when the network device service is enabled;
- duplicate/conflicting upstream connector identifiers;
- upstream message mappings/targets that reference unknown TimingNodes;
- conflicting presentation/logging listener bind address/port combinations;
- invalid logging level, file rotation/retention values or live-listener settings;
- unsupported adapter/driver types;
- missing required secret references or unresolved required secret values;
- invalid runtime values such as impossible queue/executor settings;
- missing/blank TimingData storage paths when the reference file store is part
  of the effective composition;
- use of a literal single-node `io.storage.timingData.path` with more than one configured
  TimingNode, or a multi-node path template whose expansion is not unique;
- simultaneous use of `io.storage.timingData.path` and
  `io.storage.timingData.nodes`;
- missing, duplicate or unknown `timingNodeId` references in
  `io.storage.timingData.nodes`;
- duplicate normalized TimingData file paths across node storage bindings.

Configuration loading, configuration validation and application composition are distinct responsibilities even when the initial implementation keeps them small.

## Startup contract

Conceptually startup is:

```text
main()
  -> obtain BuildIdentity from the built artifact
  -> select built-in application profile / platform / operating-mode defaults
  -> apply explicit IF-11 deployment overrides
  -> resolve secrets
  -> produce effective ApplicationConfig
  -> discover built-in and configured external extension providers
  -> validate effective configuration, profile constraints and provider references
  -> configure executable runtime logging
  -> runtime TimingApplication.create(...) constructs and wires the application and selected implementations
  -> recover configured TimingData storage into the TimingNode LogBook
  -> start application lifecycle
```

The executable may use a dedicated `ApplicationConfigLoader` once real configuration loading/overlay behaviour exists. A class must not be introduced merely to mirror this document before it owns real behaviour.

Reusable application/runtime behaviour should be shared through composition. IF-11 does not define or require a `BaseApplication` inheritance hierarchy.

## Public/private boundary

Public configuration examples use synthetic identities and endpoints.

Real deployment identities, production topology, credentials, encryption keys, proprietary mappings, private provider names and private protocol values remain outside the public repositories. Public examples use only generic/reference provider IDs and synthetic configuration.

## Current baseline coverage

The current configuration contract includes:

- external configuration loading;
- stable application and TimingNode identity;
- presentation listener/binding settings;
- logging configuration;
- the reference TimingData storage path and startup recovery dependency.

Hardware-specific settings, upstream connector details and multi-node storage
mapping are included only where their configuration semantics are defined.

## Traceability

| IF-11 concern | SI-01 SSD requirement / architecture |
| --- | --- |
| external effective configuration | SI01-REQ-001 |
| built-in application-profile defaults + explicit deployment overrides | SI01-REQ-001 / configuration-composition architecture |
| configured TimingSystem/TimingNode composition | SI01-REQ-003 |
| presentation listen/binding settings | SI01-REQ-032 + IF-03 |
| TimingData storage path + startup recovery | SI01-REQ-042 + IF-05 / Java persistence design |
| deployment/composition separation | SI-01 SSD configuration/composition architecture |
| Java composition/type growth | SI-01 Java component SDD |


# Java component and package structure

Status: working draft / non-authoritative

Software item: **SI-01 — Headless Timing Application**

This SDD defines the current working Java/Maven component direction for SI-01. Its main purpose is to keep **architectural responsibility**, **Maven modules**, **Java packages**, and **contracts** distinct so the implementation can evolve without creating artificial module boundaries too early.

The runtime/source hierarchy is defined in more detail in `31-01-SDD-04-runtime-topology-and-configuration.md`. Transport-independent backoffice behaviour is defined in `31-01-SDD-05-backoffice-transport-design.md`.

The initial `timing-api / timing-core / timing-runtime / timing-adapters / timing-testkit / timing-app` proposal is superseded by this working direction. The earlier split proved useful as a discussion aid, but it introduced modules before their responsibilities and consumers were sufficiently concrete.

## Core rules

Use four concepts for four different jobs:

1. **Architecture responsibility** — what code owns a concern and what it is allowed to know.
2. **Maven module** — a compile-time dependency/publication boundary that must earn its existence.
3. **Java package** — cohesive organisation inside a module.
4. **Contract/port** — an explicit boundary owned by the responsibility whose semantics it expresses.

Do not create a Maven module merely because a package name or architectural term exists. Do not create one global API module merely because several components need contracts.

A contract should normally live with its semantic owner:

- domain/application contracts with `domain`;
- runtime/orchestration contracts with `core`;
- execution-environment abstractions with `platform`;
- wire/protocol/endpoint contracts with `comm`.

A separate public API artifact may be introduced later when a real external Java consumer needs a stable independently published contract. It is not part of the initial reactor merely as a future placeholder.

## Working Maven reactor

Start with five short repository-local module directories:

```text
event-timing-framework/
├── pom.xml
├── domain/
├── core/
├── platform/
├── comm/
└── app/
```

The repository already supplies the `event-timing` context, so repeating `timing-` in every directory name adds little value.

Published Maven artifact IDs remain independently recognisable:

```text
event-timing-domain
event-timing-core
event-timing-platform
event-timing-comm
event-timing-app
```

The working Maven `groupId` and Java package root are:

```text
io.github.brainboxemb.eventtiming
```

Example package roots:

```text
io.github.brainboxemb.eventtiming.domain
io.github.brainboxemb.eventtiming.core
io.github.brainboxemb.eventtiming.platform
io.github.brainboxemb.eventtiming.comm
io.github.brainboxemb.eventtiming.app
```

Split a module further only when a real dependency, platform, release, ownership, public/private, or verification reason justifies the additional boundary.

## `domain`

Purpose: own the actual event-timing application/domain model and behaviour.

This is where the system's meaningful state, rules and services live. It should remain independent from concrete HTTP servers, WebSocket libraries, RabbitMQ clients, socket implementations, operating-system APIs and proprietary hardware/protocol implementations.

Candidate capability-oriented packages include:

```text
...eventtiming.domain.timingsystem
...eventtiming.domain.registrationasset
...eventtiming.domain.registrationsource
...eventtiming.domain.registration
...eventtiming.domain.readyteam
...eventtiming.domain.rfid
...eventtiming.domain.start
...eventtiming.domain.penalty
...eventtiming.domain.reference
...eventtiming.domain.display
...eventtiming.domain.backoffice
...eventtiming.domain.status
```

Representative responsibilities include:

```text
TimingSystemInstance
RegistrationAsset
RegistrationSource
RegistrationSequence
RegistrationService
RegistrationLedger
ReadyTeamService
ReadyTeamState
StartProcedureService
PenaltyService
ReferenceDataService
DisplayService
StatusService
```

Services belong here when they implement application/domain behaviour rather than generic runtime orchestration.

### Total system, registration asset and registration source

These remain different domain concepts:

```text
TimingSystemInstance
  lifecycle / ready-team / start procedure / display / instance state
       |
       +-- 1..X RegistrationAsset
               device/antenna identity + source-routing policy
               |
               +-- 1..X RegistrationSource
                       external RegistrationSystemId
                       source sequence
                       source registration file
```

A `RegistrationAsset` represents the configured physical/logical box. A `RegistrationSource` represents one ordered source stream. One asset can expose several sources, including virtual sources.

`RegistrationSequence` therefore belongs at source scope, not at total-system, asset or process scope.

### Registration and ready-team remain separate capabilities

```text
registration
  passage / start / manual / penalty / revocation / operational registration entries
  sequence allocated by RegistrationSource
  registration ledger
  local result/ranking derivation

readyteam
  team added / team removed
  traceable operational journal
  current ReadyTeamState projection
  feeds current display state
```

A keypad action must not create a participant/timing `RegistrationRecord` merely because it is persisted. It creates a `ReadyTeamEvent` and updates the ready-team projection.

### Domain contracts

When the domain requires an outward capability, the contract should normally be defined close to the domain semantics rather than moved to a generic `api` module.

Examples may include semantic registration persistence, source routing or backoffice publication boundaries.

Suitable package terms include `port` or `contract` where they add clarity. Avoid a Java package named `interface`; `interface` is a Java keyword, and the package name also says less about architectural intent.

## `core`

Purpose: provide the running engine around the domain.

`core` owns runtime/orchestration concerns rather than event-timing rules themselves.

Likely packages include:

```text
...eventtiming.core.bootstrap
...eventtiming.core.configuration
...eventtiming.core.instance
...eventtiming.core.execution
...eventtiming.core.routing
...eventtiming.core.lifecycle
...eventtiming.core.scheduling
...eventtiming.core.status
```

Responsibilities include:

- hosting `1..X` complete `TimingSystemInstance` objects;
- application/runtime registry;
- constructing configured system instances/assets/sources;
- routing commands/queries to a system instance;
- routing external observations to the correct instance/asset boundary;
- ingress queues;
- logical serialized execution per `TimingSystemInstance`;
- scheduling runtime work;
- runtime lifecycle;
- runtime-wide status aggregation.

The working threading model remains **logical serialization per `TimingSystemInstance`**, not one OS thread per system, asset, source or antenna. Multiple logical serial executors may use a small shared backing executor on Raspberry Pi Zero.

A class belongs in `core` because it helps the application *run*, not merely because it is important. Domain rules and services stay in `domain`.

## `platform`

Purpose: define abstractions of the execution platform/environment and, where justified, small generic/default implementations of those abstractions.

Candidate concerns include:

```text
...eventtiming.platform.clock
...eventtiming.platform.execution
...eventtiming.platform.filesystem
...eventtiming.platform.process
...eventtiming.platform.network
...eventtiming.platform.device
```

Examples of platform-level concepts may include:

- clock/time source;
- backing executor/thread primitives;
- filesystem/path access abstraction where portability/testability requires it;
- process/runtime information;
- low-level operating-system/device primitives needed to isolate Windows/Linux/Raspberry Pi differences.

`platform` is not the dumping ground for all technical code. A protocol-facing HTTP endpoint, WebSocket session, RabbitMQ transport or event-timing CAN protocol belongs under `comm`, not merely under `platform` because it uses the operating system.

The exact boundary for hardware-facing facilities is capability-specific. A low-level OS/device primitive can be platform-facing while the event-timing protocol/semantic communication built on it belongs in `comm`.

## `comm`

Purpose: own communication endpoints, protocols, transport implementations and their wire-facing contracts.

Candidate packages include:

```text
...eventtiming.comm.http
...eventtiming.comm.websocket
...eventtiming.comm.socket
...eventtiming.comm.rabbitmq
...eventtiming.comm.rfid
...eventtiming.comm.can
...eventtiming.comm.display
...eventtiming.comm.console
```

This is the natural location for concerns such as:

- HTTP application-control/status endpoints;
- WebSocket status/event streaming;
- lightweight socket system-test transport;
- RabbitMQ connection/channel/consumer/publisher behaviour;
- RFID reader/protocol communication;
- CAN communication and event-timing device protocols;
- display communication sessions/protocols.

Protocol/wire DTOs and transport-specific contracts should live with the relevant communication capability rather than in a generic cross-project API package.

Examples:

```text
comm/http/...             HTTP request/response representation
comm/websocket/...        WebSocket message representation
comm/backoffice/...       transport-facing backoffice protocol/session types
```

Transport-independent semantic obligations still belong to the semantic owner in `domain` or `core`. `comm` implements or translates those boundaries.

### Backoffice example

The domain/core side should work with semantic source-aware messages, not RabbitMQ destinations or socket framing.

Conceptually:

```java
interface BackofficePublisherPort {
    void publish(RegistrationSourceKey source, BackofficeEnvelope message);
}
```

The semantic port may be owned near the domain capability. Concrete implementations belong in `comm`, for example:

```text
comm/socket        lightweight ST-2 transport
comm/rabbitmq      production-shaped broker transport
```

Actual production queue/exchange/routing names, proprietary codecs and deployment mappings remain private/external configuration or private implementation.

## `app`

Purpose: remain a thin executable/composition root.

It should contain little or no event-timing behaviour:

```text
main()
  -> load settings
  -> validate topology
  -> construct/select platform facilities
  -> construct/select communication implementations
  -> construct core runtime
  -> create configured domain TimingSystemInstances
  -> start public interfaces
  -> install shutdown handling
```

Composition belongs here; reusable domain/runtime/communication behaviour does not.

The more important future external-consumer proof still belongs in a separate reference/test repository rather than growing `app` into a second implementation architecture.

## Working dependency direction

The intended compile-time direction is a DAG rather than one strictly linear stack.

Working baseline:

```text
platform
   ^       ^        ^
   |       |        |
domain <- core <- comm
            ^      ^
             \    /
               app
```

Expressed as dependencies:

```text
domain   -> platform abstractions where genuinely needed
core     -> domain + platform
comm     -> domain/core contracts + platform where needed
app      -> domain + core + platform + comm
```

Important rules:

- `domain` does not depend on `core`, `comm` or `app`;
- `core` does not depend on concrete communication implementations;
- `platform` does not depend on event-timing domain behaviour;
- `comm` translates external communication into domain/core semantics rather than moving protocol details inward;
- `app` is the composition root and may know all selected public components.

This dependency model is still a working design. A concrete capability may justify moving a contract to its clearer semantic owner, but circular dependencies are not acceptable as a way to avoid that decision.

## Contract placement

Do not collect all interfaces into one `api` module or one generic `interfaces` package.

Use ownership:

```text
domain
  semantic domain models/services
  domain ports/contracts

core
  runtime/orchestration contracts

platform
  execution-environment abstractions

comm
  endpoint/protocol/wire contracts and implementations
```

A contract shared by two modules should be placed according to who defines its semantics, not according to who happens to call it first.

Examples:

- a domain repository or source-routing port: `domain`;
- serialized runtime command submission: `core`;
- clock abstraction: `platform`;
- HTTP request/response or WebSocket message: `comm`.

## Public versus proprietary components

Expected proprietary areas may include:

- production RFID control/protocol details;
- product-specific communication/protocol implementations;
- production asset/source inventory and mappings;
- production backoffice message schemas/codecs where sensitive.

The public framework exposes only the contracts required for those components. Separate repositories do not require subclassing or dynamic plugin discovery.

Prefer composition and constructor/factory injection. If runtime plugin discovery later becomes a real requirement, evaluate `ServiceLoader` or another mechanism separately.

## Tests and future `testkit`

Ordinary tests stay with the module they verify:

```text
domain/src/test/...
core/src/test/...
platform/src/test/...
comm/src/test/...
app/src/test/...
```

Do **not** create a top-level `testkit` module until a real second consumer needs reusable test components across module/repository boundaries.

A future reusable test library may become justified for components such as a fake clock, scenario builders, stub communication peers or topology builders. Until then, such helpers remain local to the tests that use them.

## Future module splits

The five-module reactor is not a promise that every future capability remains in one artifact forever.

Examples that may later justify separate artifacts include:

- RabbitMQ communication because it brings a significant client dependency and lifecycle;
- Linux/Raspberry-Pi-specific platform support;
- proprietary communication implementations in a private repository;
- a stable public Java API/SPI if an external library consumer emerges;
- a reusable testkit after multiple real consumers exist.

Create those boundaries when evidence appears, not as placeholders.

## Architecture checks

Useful automated rules can eventually include:

- `domain` does not reference `core`, `comm` or `app` packages;
- `domain` does not reference HTTP, WebSocket, RabbitMQ, socket or concrete CAN/RFID implementation libraries;
- `core` does not reference concrete communication implementation packages;
- `platform` does not depend on event-timing domain/core behaviour;
- protocol/wire classes stay under `comm`;
- semantic domain contracts are not moved into `comm` merely because communication uses them;
- `RegistrationSequence` remains registration-source scoped;
- registration-asset/source topology is not inferred from communication implementation classes;
- public code does not contain real deployment asset/source mappings;
- backoffice semantic code does not depend on RabbitMQ/socket implementation classes;
- `registration` and `readyteam` remain independent domain capabilities;
- production runtime dependencies do not include future reusable test helpers accidentally.

A Java-8-compatible architecture-test library can be evaluated later, but Maven dependency rules already enforce important boundaries.

## Open decisions

- exact package granularity inside each capability;
- which low-level hardware/device concerns are platform primitives versus communication implementations;
- whether `platform` eventually separates contracts from OS-specific implementations;
- final configuration file format and include/override model;
- how configuration selects communication/platform implementations;
- private Maven artifact publication/consumption mechanism;
- version alignment between the public framework and private implementations;
- whether socket/RabbitMQ/platform-specific implementations warrant independent artifacts from their first real implementation;
- where the compiled React application belongs;
- whether and when a dedicated public Java API/SPI artifact becomes justified;
- exact boundary between the public reference application and private product composition.

# Java component and package structure

Status: working draft / non-authoritative

Software item: **SI-01 — Headless Timing Application**

This SDD defines the current working Java/Maven structure for SI-01. Its main purpose is to keep **architecture responsibilities**, **Java packages**, **Maven artifacts**, **application composition**, and **contracts** distinct so the implementation can be tested and evolved without creating artificial library boundaries too early.

The runtime/source hierarchy is defined in more detail in `31-01-SDD-04-runtime-topology-and-configuration.md`. Transport-independent backoffice behaviour is defined in `31-01-SDD-05-backoffice-transport-design.md`.

The earlier `timing-api / timing-core / timing-runtime / timing-adapters / timing-testkit / timing-app` proposal, and the later one-artifact-per-layer `domain / core / platform / comm / app` reactor, are both superseded by this working direction. They were useful discussion steps, but both coupled architecture vocabulary too directly to Maven publication boundaries.

## Core rules

Use different concepts for different jobs:

1. **Architecture responsibility** — what code owns a concern and what it is allowed to know.
2. **Java package** — cohesive organisation and dependency discipline inside a library/application.
3. **Maven artifact** — a reusable library, independently consumable integration, or deployable application that has a real consumer/lifecycle reason to exist.
4. **Application composition** — which framework/infrastructure implementations are assembled into one executable product.
5. **Contract/port** — an explicit semantic boundary owned by the responsibility whose semantics it expresses.

The central rule is:

> **An architecture layer/package is not automatically a Maven artifact.**

A separate Maven artifact should be introduced only when there is a concrete reason such as:

- another application must consume it independently;
- an optional integration brings a meaningful independent dependency or lifecycle;
- deployment, ownership, public/private boundaries, or release/versioning require separation;
- several applications need the same reusable implementation without depending on unrelated code.

Do not create an artifact merely to mirror an architecture diagram.

## Initial Maven reactor

The first structure deliberately proves only one reusable library and one executable application:

```text
event-timing-framework/
├── pom.xml                  event-timing-parent (build/aggregation metadata)
├── framework/
│   └── pom.xml              event-timing-framework.jar
└── app/
    └── pom.xml              event-timing-app.jar
```

The root parent POM is build metadata, not a deployed product component.

Working Maven coordinates:

```text
groupId: io.github.brainboxemb.eventtiming

parent:     event-timing-parent
library:    event-timing-framework
executable: event-timing-app
```

This is intentionally smaller than the architecture package model.

## Framework library

`event-timing-framework` is the reusable Java library consumed by executable applications.

Its initial package root is:

```text
io.github.brainboxemb.eventtiming
```

with working responsibility packages:

```text
io.github.brainboxemb.eventtiming.domain
io.github.brainboxemb.eventtiming.core
io.github.brainboxemb.eventtiming.platform
io.github.brainboxemb.eventtiming.comm
```

These are package/architecture responsibilities **inside one framework artifact**. They are not separate published libraries in the initial baseline.

### `domain`

Purpose: own reusable event-timing domain/application concepts, state, rules and services.

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

Representative reusable concepts may include:

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

A service belongs here when it implements event-timing/application behaviour rather than generic runtime mechanics.

The framework domain should contain behaviour that is meaningful across applications. Event/product-specific policy can remain in a derived application or an additional private/public extension library when that policy is not generally reusable.

### Total system, registration asset and registration source

These remain separate concepts:

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

A `RegistrationAsset` represents the configured physical/logical equipment unit. A `RegistrationSource` represents one ordered source stream. One asset can expose several sources, including virtual sources.

`RegistrationSequence` therefore belongs at source scope, not at application, asset or global scope.

### `core`

Purpose: own reusable runtime/engine mechanics around the domain.

Candidate concerns include:

```text
...eventtiming.core.execution
...eventtiming.core.lifecycle
...eventtiming.core.routing
...eventtiming.core.scheduling
...eventtiming.core.configuration
...eventtiming.core.status
```

Examples:

- logical serialized execution for one `TimingSystemInstance`;
- reusable lifecycle mechanics;
- reusable command/event routing primitives;
- scheduling/runtime support;
- orchestration that is independent of one concrete executable application.

A class belongs in `core` because it helps reusable framework behaviour *run*, not merely because it is important.

Do not automatically move all multi-system application behaviour into `core`. For example, a registry/routing policy that exists only because one executable hosts many systems can initially belong to that multi-system application. Promote it into reusable `core` only when several applications actually need it.

This distinction allows both a simple single-system application and a multi-system application to use the same framework without forcing the simpler application to adopt unnecessary orchestration.

### `platform`

Purpose: own abstractions of the execution environment and small reusable/default facilities where appropriate.

Candidate concerns include:

```text
...eventtiming.platform.clock
...eventtiming.platform.execution
...eventtiming.platform.filesystem
...eventtiming.platform.process
...eventtiming.platform.network
...eventtiming.platform.device
```

Examples may include:

- clock/time source abstractions;
- backing executor/thread primitives;
- filesystem/path abstractions where portability/testability requires them;
- process/runtime information;
- low-level OS/device primitives used to isolate Windows/Linux/Raspberry Pi differences.

`platform` is not a dumping ground for all technical code. HTTP, WebSocket, RabbitMQ or an event-timing device protocol remains a communication concern even though it uses platform facilities.

A platform-specific implementation may later become its own library if several applications need it independently or if native/platform dependencies justify isolation. Until then it can remain within the framework/application structure being proven.

### `comm`

Purpose: own reusable communication semantics/contracts and communication-facing code that belongs to the generic framework.

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

Possible concerns include:

- application-control/status endpoint contracts;
- WebSocket event/status messages;
- socket test transport semantics;
- backoffice communication contracts;
- RFID/CAN/display communication contracts and reusable protocol-independent pieces.

Protocol/wire types should stay close to their communication capability rather than being collected in one global `api` package.

Concrete communication implementations do not automatically need their own artifact. A RabbitMQ implementation, for example, becomes a separate library when there is a concrete benefit such as independent reuse, dependency isolation, lifecycle separation or private/public ownership. The initial structure does not pre-create that boundary.

## Contract placement

Do not collect all interfaces into one generic top-level `api` module.

Place a contract with the code that owns its semantics:

```text
domain
  domain models/services
  semantic domain ports/contracts

core
  runtime/orchestration contracts

platform
  execution-environment abstractions

comm
  endpoint/protocol/wire contracts
```

Examples:

- source-routing/domain repository port: `domain`;
- serialized runtime submission/lifecycle contract: `core`;
- clock abstraction: `platform`;
- HTTP/WebSocket wire representation: `comm`.

A dedicated public API/SPI artifact can be introduced later when an external Java consumer needs a stable independently versioned contract. It is not created as a placeholder.

## Default executable application

`event-timing-app` is the first executable consumer of the framework library.

Its Java package is rooted at:

```text
io.github.brainboxemb.eventtiming.app
```

It should remain a composition/startup boundary rather than a second home for reusable framework behaviour:

```text
main()
  -> load settings
  -> select/construct concrete infrastructure
  -> create framework domain/core objects
  -> wire communication/platform implementations
  -> start selected application interfaces
  -> install shutdown handling
```

The current bootstrap application exists only to prove that a real executable can consume the separately built framework JAR and can be produced/tested through the reusable Java toolchain.

## Derived applications

The framework is deliberately not tied to one fixed executable topology.

Two plausible consumers are:

```text
single-system application
  compose exactly one TimingSystemInstance
  minimal routing/registry overhead

multi-system application
  compose 1..X TimingSystemInstance objects
  application-level registry/routing/aggregate status as required
```

These are architectural examples, not modules to create now.

A later derived application can depend on `event-timing-framework` and inject/select its own implementations, for example:

```text
derived application
  -> event-timing-framework
  -> optional reusable infrastructure library/libraries
  -> product/private components where needed
```

This supports public reference applications, private product compositions, simulation applications and target-specific applications without forking the framework source.

## Generic framework versus product/application domain

Not all domain behaviour necessarily belongs in the reusable framework.

Working distinction:

```text
generic event-timing behaviour
  -> event-timing-framework/domain

application/product-specific policy
  -> derived application or dedicated extension library
```

A rule should move into the framework when it is genuinely reusable and part of the supported event-timing model. A deployment-specific mapping, one-off workflow or proprietary policy should not be generalised merely to keep all domain-looking code in one library.

## Internal dependency direction

Because `domain`, `core`, `platform` and `comm` initially live in one JAR, Maven does not enforce their package dependency rules. The design still needs a clear direction.

Working rules:

- `domain` does not depend on `core`, concrete communication implementations or application composition;
- `domain` may depend on narrow platform contracts where those abstractions are genuinely part of deterministic domain behaviour;
- `core` may depend on `domain` and platform abstractions;
- `comm` translates external communication into domain/core semantics and may use platform facilities;
- `platform` must not depend on event-timing domain behaviour;
- application composition may depend on the complete framework public surface and selected infrastructure libraries.

Circular package dependencies are not an acceptable substitute for choosing semantic ownership.

Architecture tests or dependency rules can be added when real code exists; do not add an architecture-testing framework solely for the bootstrap markers.

## Public/private composition

Expected proprietary/private areas may include:

- production RFID control/protocol details;
- product-specific communication/protocol implementations;
- production asset/source inventory and mappings;
- production backoffice schemas/codecs where sensitive;
- deployment-specific composition/policies.

The public framework should expose only the contracts needed to compose these pieces. Separate repositories do not require subclassing or dynamic plugin discovery.

Prefer composition and constructor/factory injection. If true runtime plugin discovery later becomes a requirement, evaluate `ServiceLoader` or another mechanism separately.

## Tests and possible future test library

Ordinary tests stay next to the code/application they verify.

Do not create a reusable `testkit` artifact until a real second consumer needs reusable test components across artifact/repository boundaries.

A future test library could become justified for fake clocks, scenario/topology builders, communication test peers or shared assertions. Until then these helpers stay local.

## Future artifact splits

Possible future library artifacts include, only when justified by concrete consumers:

- RabbitMQ communication integration;
- Linux/Raspberry-Pi-specific platform integration;
- public/private RFID/CAN implementations;
- a stable Java API/SPI;
- reusable test support.

The default is to keep code in the framework while learning the boundaries. Splitting later is preferred over creating speculative libraries now, provided package boundaries remain clean enough to permit extraction.

## Architecture checks

Useful future automated rules may include:

- domain packages do not reference app or concrete communication implementation packages;
- platform packages do not depend on event-timing domain/core behaviour;
- protocol/wire classes stay under communication packages;
- semantic domain contracts are not moved into communication packages merely because transport code uses them;
- `RegistrationSequence` remains registration-source scoped;
- public code contains no real deployment mappings or proprietary values;
- backoffice semantic code does not depend on a specific broker/socket implementation;
- registration and ready-team remain separate domain capabilities;
- the executable application depends on `event-timing-framework`, not on source-copy/forked framework code.

## Open decisions

- exact package granularity inside each capability;
- exact reusable boundary between single-instance core mechanics and multi-system application orchestration;
- which low-level hardware/device concerns are platform primitives versus communication implementations;
- final configuration file format and include/override model;
- how applications select/inject communication/platform implementations;
- private Maven artifact publication/consumption mechanism;
- version alignment between public framework and private implementations;
- which concrete integrations eventually deserve independent artifacts;
- whether and when a dedicated public Java API/SPI artifact becomes justified;
- exact boundary between public reference applications, simulation applications and private product compositions.

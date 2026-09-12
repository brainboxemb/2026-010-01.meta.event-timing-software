# Java component, layer and artifact structure

Status: working draft / non-authoritative

Software item: **SI-01 — Headless Timing Application**

This SDD defines the current working Java structure for SI-01. Its main purpose is to keep **architecture layers**, **Java packages**, **Maven artifacts**, **application composition**, and **contracts** distinct so the implementation can evolve without creating artificial library boundaries.

The runtime/source hierarchy is refined in `31-01-SDD-04-runtime-topology-and-configuration.md`. Transport-independent backoffice behaviour is refined in `31-01-SDD-05-backoffice-transport-design.md`.

The earlier `timing-api / timing-core / timing-runtime / timing-adapters / timing-testkit / timing-app` proposal, and the later one-artifact-per-layer `domain / core / platform / comm / app` reactor, are both superseded. Both were useful discussion steps but coupled architecture vocabulary too directly to Maven publication boundaries.

## Core rules

Use different concepts for different jobs:

1. **Architecture layer/responsibility** — what owns behaviour/state and what it may know.
2. **Java package** — cohesive code organisation and dependency discipline.
3. **Maven artifact** — a reusable library or deployable application with a real consumer/lifecycle reason to exist.
4. **Application composition** — which framework/infrastructure implementations are assembled into one executable.
5. **Contract/port** — a semantic boundary owned by the responsibility whose semantics it expresses.

The central rule remains:

> **An architecture layer or package is not automatically a Maven artifact.**

Create a separate artifact only when there is a concrete consumer or independent reuse, dependency, lifecycle, deployment, ownership, public/private, release or versioning boundary.

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

Working coordinates:

```text
groupId: io.github.brainboxemb.eventtiming

parent:     event-timing-parent
library:    event-timing-framework
executable: event-timing-app
```

The root parent POM is build metadata, not a deployed product component.

## Layered responsibility model

The framework/application is viewed as layered responsibilities rather than as one artifact per layer.

![SI-01 layered architecture](../../../raw/prod/docs/assets/architecture/layered-architecture.svg)

The diagram is generated from `docs/_diagrams/layered-architecture.yaml`. The diagram deliberately shows responsibilities and service boundaries; it does **not** prescribe Maven artifact boundaries.

### Presentation layer

Purpose: expose application behaviour and current application state to external clients.

Typical responsibilities:

```text
HTTP / JSON
WebSocket
local console
remote shell
protocol/DTO mapping for those interfaces
```

Presentation translates external requests into application commands/queries and translates application status/events into external representations.

Presentation **does not own running application state**. It may be state-aware because it presents current state, but the state remains owned by the application layer.

HTTP/WebSocket/console therefore fit the presentation view better than a generic catch-all "communication" layer.

### Application layer

Purpose: own the running application state and coordinate use cases.

Representative responsibilities include:

```text
TimingSystemInstance state
registration/source ledgers and current runtime state
commands / queries / workflows
status management and aggregation
immutable status snapshots
single-system or multi-system application coordination
```

The application layer is the normal owner of mutable runtime/application state.

It invokes domain services to perform domain behaviour and applies the resulting changes to application state. It also coordinates persistence and integration ports without moving protocol details into the domain.

This **application layer is not the same thing as the `event-timing-app` Maven artifact**. Reusable application-layer behaviour may live in `event-timing-framework`; the executable app remains the composition/startup root.

### Domain layer

Purpose: own reusable event-timing services, domain rules, entities and value semantics.

The domain layer should not become the owner of all running mutable application state. Services operate on domain/application data supplied through explicit calls/contexts and return domain results/state changes.

Current representative services include:

```text
RegistrationService
StartTimeService
ReadyTeamService
ReferenceDataService
```

#### RegistrationService

`RegistrationService` owns reusable registration behaviour such as registration flow and source-sequence semantics.

Start-related registration handling remains part of the registration flow. There is no separate active `StartProcedureService`.

When a registration flow produces or needs a start procedure/start-time action, `RegistrationService` may pass that start procedure to `StartTimeService`.

#### StartTimeService

`StartTimeService` is the specialised domain service for start-time behaviour and start-time data semantics.

Its responsibilities may include:

```text
interpret/update start-time values
look up the applicable start time
process a start procedure received from RegistrationService
apply start-time domain rules
```

Start-time updates may originate from backoffice information, but the backoffice transport does not call domain transport code directly. A backoffice integration translates the incoming message into an application update/command; the application flow then invokes `StartTimeService`.

#### ReadyTeamService

Ready-team behaviour remains a separate domain capability from registrations. It may maintain separate ledger/state semantics through the application layer and must not be conflated with the registration ledger.

#### ReferenceDataService

Reference-data behaviour owns the semantics needed to interpret participant/event reference information without depending on a specific backoffice transport.

#### Domain model and rules

Representative reusable domain concepts may include:

```text
TimingSystem identity/value concepts
RegistrationAsset
RegistrationSource
RegistrationSequence
registration observations/results
start-time values
ready-team values
reference-data value objects
```

`RegistrationSequence` remains registration-source scoped.

Product/deployment-specific policies do not automatically belong in the generic framework. A rule belongs in the framework when it is genuinely reusable event-timing behaviour.

### Core runtime support

Purpose: provide reusable runtime/engine mechanics that let application/domain behaviour run predictably.

Candidate concerns:

```text
serialized execution
lifecycle mechanics
routing primitives
scheduling
command/event dispatch mechanics
```

Core is support for the application layer; it is not a second home for domain behaviour or application state.

Do not automatically put all multi-system behaviour into core. A multi-system registry/routing policy may initially belong to the multi-system application until reuse proves that it is generic runtime behaviour.

### Infrastructure / integration layer

Purpose: implement communication with external systems/devices and persistence mechanisms.

Representative integrations include:

```text
persistence / file backup and restore
backoffice socket / RabbitMQ integration
RFID integration
CAN integration
display integration
```

These concerns are intentionally separate from presentation even though both use communication technologies.

The useful distinction is semantic direction:

```text
presentation
  external clients inspect/control the application

integration
  the application interacts with backoffice, devices and persistence
```

A transport/protocol implementation should depend inward on application/domain contracts rather than own application state.

A concrete integration becomes its own Maven artifact only when a real reuse/dependency/lifecycle/ownership boundary justifies it.

### Platform layer

Purpose: abstract the execution environment and low-level platform facilities.

Representative facilities:

```text
Clock / time source
filesystem/path primitives
executor/thread primitives
process/runtime information
network/OS primitives
low-level platform/device primitives where portability requires them
```

Platform is not a dumping ground for HTTP, RabbitMQ or domain/device protocols.

### Cross-cutting concerns

Cross-cutting concerns may span multiple layers without becoming the owner of domain/application state:

```text
logging
configuration
diagnostics
build/version identity
```

Their implementation still follows normal dependency rules; "cross-cutting" is not permission for circular dependencies.

## Artifact and package direction

The initial artifact model remains intentionally small:

```text
event-timing-framework.jar
event-timing-app.jar
```

The layered model above is finer-grained than the artifact model.

The bootstrap framework currently contains marker packages such as `domain`, `core`, `platform` and `comm`. These marker packages proved the framework-to-app artifact boundary; they are **not a commitment that every future architectural responsibility must map one-to-one to those four package names**.

In particular, implementation evidence may justify clearer package responsibilities such as:

```text
...eventtiming.application
...eventtiming.domain
...eventtiming.core
...eventtiming.presentation
...eventtiming.integration
...eventtiming.platform
```

or capability-oriented subpackages beneath those responsibilities.

Do not rename/split packages merely to make the source tree match a picture. Refine the package layout when real classes make the dependency direction testable.

## Contract placement

Do not collect every interface into one generic top-level `api` module.

Place contracts with the responsibility that owns their semantics. Examples:

```text
presentation
  external endpoint/wire contracts

application
  commands, queries, application-level ports

domain
  domain service/model contracts and semantic domain ports

core
  runtime/execution contracts

integration
  concrete external-system/device/persistence implementations

platform
  execution-environment abstractions
```

A dedicated public API/SPI artifact can be introduced later when an external Java consumer needs a stable independently versioned contract.

## Default executable application

`event-timing-app` is the first executable consumer of the framework library.

Its package root remains:

```text
io.github.brainboxemb.eventtiming.app
```

The executable should stay a composition/startup boundary:

```text
main()
  -> load settings
  -> select/construct concrete integrations/platform implementations
  -> create reusable application/domain/core objects
  -> wire presentation endpoints
  -> start lifecycle
  -> install shutdown handling
```

Reusable application behaviour should not migrate into the executable merely because the word "application" is used for the architectural layer.

## Derived applications

The framework is deliberately not tied to one executable topology.

Plausible consumers include:

```text
single-system application
  compose exactly one TimingSystemInstance

multi-system application
  compose 1..X TimingSystemInstance objects
  add registry/routing/aggregate status where required

simulation/reference application
  inject deterministic integrations and platform facilities

private/product application
  inject proprietary/product-specific components
```

These are consumer examples, not modules to create now.

## Internal dependency direction

Working rules:

- presentation depends inward on application contracts; it does not own application state;
- application owns running mutable state and coordinates domain/core/integration contracts;
- domain services/rules remain independent of presentation and concrete integrations;
- core supplies runtime mechanics and may depend on stable domain/application abstractions where required;
- concrete integrations depend inward on application/domain ports and may use platform facilities;
- platform does not depend on event-timing domain/application behaviour;
- executable composition may depend on the complete supported framework surface and selected external libraries.

Circular package dependencies are not an acceptable substitute for choosing semantic ownership.

## Public/private composition

Expected private/product-specific areas may include:

- production RFID control/protocol details;
- product-specific integration/protocol implementations;
- production asset/source inventory and mappings;
- production backoffice schemas/codecs where sensitive;
- deployment-specific composition/policies.

Prefer composition and constructor/factory injection.

If true runtime plugin discovery later becomes a requirement, evaluate that separately rather than building it into the first framework skeleton.

## Tests and possible future libraries

Ordinary tests stay next to the code/application they verify.

Do not create a reusable `testkit` artifact until a real second consumer needs reusable test components across artifact/repository boundaries.

Possible future artifacts, only when justified by concrete consumers, include:

- RabbitMQ integration;
- Linux/Raspberry-Pi platform integration;
- public/private RFID/CAN implementations;
- stable Java API/SPI;
- reusable test support.

Splitting later is preferred over speculative libraries, provided responsibility/package boundaries stay clean enough to extract.

## Architecture checks

Useful future automated rules may include:

- presentation packages do not own or persist application state;
- domain services do not reference presentation or concrete integration classes;
- platform packages do not depend on event-timing domain/application behaviour;
- protocol/wire classes stay with their presentation/integration capability;
- semantic domain contracts are not moved into transport packages merely because transport code uses them;
- `RegistrationSequence` remains registration-source scoped;
- registration and ready-team remain separate capabilities;
- `RegistrationService` may delegate start-time-specific work to `StartTimeService`; no separate active start-procedure service is assumed;
- backoffice start-time/reference updates enter through integration -> application flow before invoking domain services;
- public code contains no real deployment mappings or proprietary values;
- the executable application consumes `event-timing-framework` rather than copying/forking framework source.

## Open decisions

- exact package granularity after real application/domain classes exist;
- whether the final package names use `presentation`/`integration` explicitly or capability-oriented subpackages;
- exact reusable boundary between single-instance core mechanics and multi-system application orchestration;
- which low-level hardware concerns are platform primitives versus integration implementations;
- final configuration file format and include/override model;
- how applications select/inject presentation/integration/platform implementations;
- private Maven artifact publication/consumption mechanism;
- version alignment between public framework and private implementations;
- which integrations eventually deserve independent artifacts;
- whether and when a dedicated public Java API/SPI artifact becomes justified.

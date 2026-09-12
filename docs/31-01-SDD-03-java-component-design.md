# Java component, package and artifact detailed design

Status: working draft / non-authoritative

Software item: **SI-01 — Headless Timing Application**

This SDD refines the SI-01 architecture into Java package, Maven artifact, composition and contract-placement rules. The application architecture itself — including the layered responsibility view — is owned by `31-01-SAD-timing-application-architecture.md`.

The runtime/source hierarchy is refined where needed in `31-01-SDD-04-runtime-topology-and-configuration.md`. Transport-independent backoffice behaviour is refined in `31-01-SDD-05-backoffice-transport-design.md`.

The earlier `timing-api / timing-core / timing-runtime / timing-adapters / timing-testkit / timing-app` proposal, and the later one-artifact-per-layer `domain / core / platform / comm / app` reactor, are both superseded. Both were useful discussion steps but coupled architecture vocabulary too directly to Maven publication boundaries.

## Architecture-to-Java mapping rule

The SI-01 SAD defines architectural responsibilities such as presentation, application, domain, core runtime support, integrations and platform abstraction.

This SDD defines how those responsibilities may be organised in Java. The central rule is:

> **An architecture layer or Java package is not automatically a Maven artifact.**

Keep these concepts distinct:

1. **Architecture responsibility** — semantic ownership and allowed dependency direction, defined primarily by the SAD.
2. **Java package** — cohesive source organisation and enforceable dependency discipline.
3. **Maven artifact** — a reusable library or deployable application with a concrete consumer/lifecycle reason to exist.
4. **Application composition** — which framework/infrastructure implementations are assembled into an executable.
5. **Contract/port** — a semantic boundary owned by the responsibility whose semantics it expresses.

Create a separate artifact only when there is a concrete consumer or independent reuse, dependency, lifecycle, deployment, ownership, public/private, release or versioning boundary. Do not create an artifact merely to mirror an architecture diagram.

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

## Package direction

The layered responsibility model in the SAD is finer-grained than the initial artifact model.

The first framework skeleton contains marker packages such as `domain`, `core`, `platform` and `comm`. Those packages proved the framework-to-application artifact boundary; they are **not** a commitment that every architectural responsibility must map one-to-one to those four package names.

As real implementation classes appear, clearer package responsibilities may be justified, for example:

```text
io.github.brainboxemb.eventtiming.application
io.github.brainboxemb.eventtiming.domain
io.github.brainboxemb.eventtiming.core
io.github.brainboxemb.eventtiming.presentation
io.github.brainboxemb.eventtiming.integration
io.github.brainboxemb.eventtiming.platform
```

Capability-oriented subpackages may exist beneath those responsibilities.

Do not rename or split packages merely to make the source tree match a diagram. Refine the package layout when real classes make semantic ownership and dependency direction testable.

## Contract placement

Do not collect every interface into one generic top-level `api` package/module.

Place contracts with the responsibility that owns their semantics. Examples:

```text
presentation
  external endpoint/wire-facing contracts and DTO mapping

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

## Internal dependency direction

Java/package dependencies should preserve the architectural ownership defined by the SAD.

Working rules:

- presentation packages depend inward on application contracts and do not own application state;
- application packages own running mutable application state and coordinate domain/core/integration contracts;
- domain services/rules do not depend on presentation or concrete integrations;
- core packages supply runtime mechanics and may depend on stable domain/application abstractions where required;
- concrete integrations depend inward on application/domain ports and may use platform facilities;
- platform packages do not depend on event-timing domain/application behaviour;
- the executable composition package may depend on the complete supported framework surface and selected external libraries.

Circular package dependencies are not an acceptable substitute for choosing semantic ownership.

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

Reusable application behaviour should not migrate into the executable merely because the architectural responsibility is called “application”.

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

## Public/private composition

Expected private/product-specific areas may include:

- production RFID control/protocol details;
- product-specific integration/protocol implementations;
- production asset/source inventory and mappings;
- production backoffice schemas/codecs where sensitive;
- deployment-specific composition/policies.

Prefer normal composition and constructor/factory injection.

If true runtime plugin discovery later becomes a requirement, evaluate that separately rather than building it into the first framework structure.

## Tests and possible future libraries

Ordinary tests stay next to the code/application they verify.

Do not create a reusable `testkit` artifact until a real second consumer needs reusable test components across artifact/repository boundaries.

Possible future artifacts, only when justified by concrete consumers, include:

- RabbitMQ integration;
- Linux/Raspberry-Pi platform integration;
- public/private RFID/CAN implementations;
- stable Java API/SPI;
- reusable test support.

Splitting later is preferred over speculative libraries, provided package/responsibility boundaries stay clean enough to extract.

## Architecture/dependency checks

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

## Open detailed-design decisions

- exact package granularity after real application/domain classes exist;
- whether final package names use `presentation` / `integration` explicitly or capability-oriented subpackages;
- exact reusable boundary between single-instance core mechanics and multi-system application orchestration;
- which low-level hardware concerns are platform primitives versus integration implementations;
- how applications select/inject presentation/integration/platform implementations;
- private Maven artifact publication/consumption mechanism;
- version alignment between public framework and private implementations;
- which integrations eventually deserve independent artifacts;
- whether and when a dedicated public Java API/SPI artifact becomes justified.

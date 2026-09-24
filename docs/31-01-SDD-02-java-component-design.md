# Java component, package and artifact detailed design

Status: working draft / non-authoritative

Software item: **SI-01 — Headless Timing Application**

This SDD has one focused purpose: refine the SI-01 architecture into Java package, Maven artifact, composition and contract-placement rules that are already relevant to the implementation repository.

The application architecture itself — including runtime hierarchy, threading, messaging, integration, configuration and technology direction — is owned by `31-01-SAD-timing-application-architecture.md`.

## Why this SDD exists

This detail is kept separate because artifact/package choices already affect source layout, dependency checks, public/private composition and release boundaries in the implementation repository.

The central rule is:

> **An architecture layer or Java package is not automatically a Maven artifact.**

Keep these concepts distinct:

1. **Architecture responsibility** — semantic ownership and dependency direction, defined by the SAD.
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

The SAD responsibility model is finer-grained than the current artifact model.

The first framework skeleton contains marker packages such as `domain`, `core`, `platform` and `comm`. Those packages proved the framework-to-application artifact boundary; they are not a commitment that every architectural responsibility maps one-to-one to those four names.

As real implementation classes appear, package responsibilities may evolve toward areas such as:

```text
io.github.brainboxemb.eventtiming.application
io.github.brainboxemb.eventtiming.domain
io.github.brainboxemb.eventtiming.core
io.github.brainboxemb.eventtiming.presentation
io.github.brainboxemb.eventtiming.integration
io.github.brainboxemb.eventtiming.infra
io.github.brainboxemb.eventtiming.platform
```

Capability-oriented subpackages may exist beneath those responsibilities.

Do not rename or split packages merely to make the source tree match an architecture diagram. Refine package layout when real classes make semantic ownership and dependency direction testable.

Likewise, a logical layer/package does not require a runtime marker class merely to prove that the layer exists. The first Java implementation removed the bootstrap-only `CoreLayer`, `DomainLayer`, `CommLayer` and `PlatformLayer` markers once real application classes existed. Architecture is expressed through ownership, package/dependency direction and behaviour, not through one object per diagram box.

### Java object model rule

Do not create a Java class merely because the SAD or an IDD names a concept or
shows a field in a response.

Create an object when current behaviour needs an object with identity, state or
a useful grouped value. Create a separate helper only when it owns behaviour or
removes real duplication.

Examples:

- the IF-03 status JSON describes what a client receives; it does **not** require
  an internal class named `ApplicationStatusSnapshot`;
- a class such as `ApplicationStatusModel` is not required unless implemented
  status behaviour actually needs that model;
- a logical architecture box is not evidence that a Java class with the same
  name must exist.

For small enums, keep the enum with the object that owns its meaning when it is
used only there. A nested enum such as `TimingApplicationLifecycle.State` is
preferred over an extra top-level source file until real reuse or clarity
justifies separating it.

Package placement follows the meaning of the object, not the layer that happens
to expose it. For example, build provenance such as `BuildIdentity` belongs in
a small `infra` package even when `CommandHandler.version()` returns it to a
client. Do not move infrastructure values into `application` merely because
application code uses them.

This keeps the early implementation small and allows the object model to grow
from real use cases rather than from the diagrams alone.

## Contract placement

Do not collect every interface into one generic top-level `api` package/module.

Place contracts with the responsibility that owns their semantics. For example:

```text
presentation
  endpoint/wire-facing contracts and DTO mapping

application
  commands, queries and application-level ports

domain
  domain service/model contracts and semantic domain ports

core
  runtime/execution contracts

integration
  concrete external-system/device/persistence implementations

infra
  build/runtime provenance and other small infrastructure values

platform
  execution-environment abstractions
```

A dedicated public API/SPI artifact can be introduced later when an external Java consumer requires a stable independently versioned contract.

## Internal dependency direction

Java/package dependencies should preserve the ownership defined by the SAD.

Working rules:

- presentation depends inward on application contracts and does not own application state;
- application owns running mutable application state and coordinates domain/core/integration contracts;
- domain services/rules do not depend on presentation or concrete integrations;
- core supplies reusable runtime mechanics without becoming a second owner of application/domain behaviour;
- concrete integrations depend inward on application/domain ports and may use platform facilities;
- platform packages do not depend on event-timing application/domain behaviour;
- executable composition may depend on the complete supported framework surface and selected external libraries.

Circular package dependencies are not an acceptable substitute for choosing semantic ownership.

## Logging dependency placement

Logging follows the same library-versus-executable composition boundary.

```text
event-timing-framework.jar
  -> slf4j-api only

 event-timing-app.jar / runtime composition
  -> selects exactly one SLF4J provider
  -> initial provider: slf4j-jdk14
  -> backend: java.util.logging
```

Working rules:

- framework code may compile against the SLF4J API but must not force a concrete provider/backend on consumers;
- the executable application chooses the provider as part of runtime composition;
- the initial Java-8/Pi-Zero baseline uses `slf4j-jdk14` so the provider delegates to the JDK `java.util.logging` backend without introducing Logback into the baseline;
- another executable/private consumer may select another compatible provider later without changing framework source;
- exactly one provider should be present in a runtime composition;
- provider/backend versions are pinned centrally by Maven dependency management rather than scattered through modules.

This keeps logging technology replaceable at the executable boundary while giving reusable framework code one consistent facade.

## Default executable application

`event-timing-app` is the first executable consumer of the framework library.

Its package root remains:

```text
io.github.brainboxemb.eventtiming.app
```

The executable stays primarily a composition/startup boundary:

```text
main()
  -> load settings
  -> select/construct concrete integrations/platform implementations
  -> create reusable application/domain/core objects
  -> wire presentation endpoints
  -> configure runtime logging provider/backend
  -> start lifecycle
  -> install shutdown handling
```

Reusable application behaviour should not migrate into the executable merely because the architectural responsibility is called `application`.

The current executable uses a small nested composition helper:

```java
TimingApplication.builder(buildIdentity).build()
```

This builder is an executable-composition convenience, not a new architecture layer. It should construct only currently real collaborators and grow only when concrete composition needs appear. The first shared presentation/application boundary is similarly small: `CommandHandler.version()` returns the authoritative `BuildIdentity` used by local/remote clients.

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
- product-specific integration/protocol implementations;
- production asset/source inventory and mappings;
- production backoffice schemas/codecs where sensitive;
- deployment-specific composition/policies.

Prefer normal composition and constructor/factory injection. Do not introduce runtime plugin discovery unless a real requirement appears.

## Possible future artifacts

Create future artifacts only when a real boundary requires them. Candidates might eventually include:

- RabbitMQ integration;
- Linux/Raspberry-Pi platform integration;
- public/private RFID/CAN implementations;
- stable Java API/SPI;
- reusable test support.

Splitting later is preferred over speculative libraries, provided package/responsibility boundaries remain clean enough to extract.

## Architecture/dependency checks

Useful automated rules may include:

- presentation packages do not own or persist application state;
- domain services do not reference presentation or concrete integration classes;
- platform packages do not depend on event-timing application/domain behaviour;
- wire/protocol classes stay with their presentation/integration capability;
- semantic contracts are not moved into transport packages merely because transport code uses them;
- public code contains no real deployment mappings or proprietary values;
- the executable consumes `event-timing-framework` rather than copying/forking framework source;
- the framework artifact does not carry a concrete SLF4J provider/backend transitively;
- an executable runtime contains exactly one intended SLF4J provider.

## Open detailed-design decisions

- exact package granularity after real application/domain classes exist;
- final package naming where capability-oriented packages prove clearer than layer names;
- exact reusable boundary between single-instance runtime mechanics and multi-system application orchestration;
- how applications select/inject presentation/integration/platform implementations;
- private Maven artifact publication/consumption mechanism;
- version alignment between public framework and private implementations;
- which integrations eventually deserve independent artifacts;
- whether and when a dedicated public Java API/SPI artifact becomes justified;
- exact field logging configuration/rotation/retention policy in the default executable.

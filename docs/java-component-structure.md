# Java component and package structure

Status: working draft / non-authoritative

This document proposes an initial Java/Maven component structure. Its main purpose is to keep **architectural layering**, **Maven modules**, and **Java packages** distinct so they do not gradually become one ambiguous hierarchy.

## Core rule

Use three different concepts for three different jobs:

1. **Architecture layer / responsibility** — explains what code is allowed to know and do.
2. **Maven module** — creates a compile-time dependency and release boundary.
3. **Java package** — organises cohesive code *inside* one module.

Do not create a Maven module for every package and do not rely on package names alone to enforce architectural boundaries.

## Initial Maven reactor

A deliberately small initial structure is preferred:

```text
event-timing/
├── pom.xml                         parent + reactor
├── timing-api/                     stable public contracts and shared models
├── timing-core/                    application/domain behaviour
├── timing-runtime/                 runtime orchestration and composition support
├── timing-adapters/                public/default adapters
├── timing-testkit/                 reusable fakes, stubs and test harnesses
└── timing-app/                     executable headless reference application
```

This is a starting point, not a permanent maximum. Modules should be split later only when there is a real dependency, release, platform, ownership, or public/private boundary.

## `timing-api`

Purpose: public types that implementations and external/private components are allowed to depend on.

Expected contents:

- immutable identifiers and value objects that cross module boundaries;
- command/query/event contracts where these form a public extension boundary;
- device/service ports such as RFID, display, CAN, backoffice and clock contracts;
- status model exposed across software-item boundaries where appropriate;
- extension/service-provider contracts needed by public or proprietary modules.

Illustrative packages:

```text
...timing.api.model
...timing.api.command
...timing.api.query
...timing.api.event
...timing.api.status
...timing.api.port
...timing.api.extension
```

Keep this module conservative. Do not move classes here merely because several modules happen to use them. A type belongs here only when it is intentionally part of a supported cross-module contract.

## `timing-core`

Purpose: implementation of timing-system/application behaviour that must remain independent from concrete hardware, networking and filesystem implementations.

Illustrative packages should preferably be organised **by capability/domain**, not by generic technical layer names such as `service`, `manager`, `util`, and `impl` at the top level.

For example:

```text
...timing.core.timingsystem
    TimingSystem
    TimingSystemState
    TimingSystemHandler

...timing.core.registration
    RegistrationService
    RegistrationFactory
    RegistrationRepository

...timing.core.rfid
    RfidService
    TagFilter
    ParticipantResolver

...timing.core.start
    StartProcedureService

...timing.core.penalty
    PenaltyService

...timing.core.display
    DisplayService
    DisplayModelBuilder

...timing.core.reference
    ReferenceDataService
    StartTimeRepository
    ReserveTagRepository

...timing.core.status
    StatusService
```

Within one capability package, classes can still have domain/application distinctions when useful. The package tree should not repeat the complete architecture mechanically.

Dependencies:

```text
timing-core -> timing-api
```

`timing-core` must not depend on HTTP, RabbitMQ, a CAN library, Raspberry Pi libraries, or a concrete RFID implementation.

## `timing-runtime`

Purpose: host `1..X` logical timing systems and provide execution/orchestration infrastructure that is not timing-domain behaviour itself.

Likely responsibilities:

- timing-system registry/manager;
- routing incoming messages to a timing-system instance;
- serial execution/queue implementation;
- lifecycle/bootstrap abstractions;
- scheduling/timers;
- runtime-wide status aggregation;
- composition APIs used by executable applications.

Illustrative packages:

```text
...timing.runtime.bootstrap
...timing.runtime.execution
...timing.runtime.routing
...timing.runtime.lifecycle
...timing.runtime.status
```

Dependencies:

```text
timing-runtime -> timing-core -> timing-api
```

## `timing-adapters`

Purpose: public/default infrastructure and device implementations.

Initially this can remain one Maven module with capability-oriented packages:

```text
...timing.adapter.console
...timing.adapter.http
...timing.adapter.websocket
...timing.adapter.memory
...timing.adapter.filebackup
...timing.adapter.stub
```

If a concrete adapter later gains heavy dependencies or a separate release/platform lifecycle, split it into its own Maven module, for example:

```text
timing-adapter-http
timing-adapter-rabbitmq
timing-adapter-linux-can
```

A proprietary adapter should normally live in a different/private repository rather than being added to this public module.

## `timing-testkit`

Purpose: reusable test components for framework tests, reference applications and proprietary integration projects.

Expected contents:

- `DirectExecutor`;
- fake clock;
- in-memory repositories;
- stub RFID adapter/controller;
- stub CAN bus/device registry;
- stub display;
- stub backoffice;
- deterministic scenario builders;
- assertions/helpers for status and registration flows;
- optional test-control API around stubs.

Illustrative packages:

```text
...timing.testkit.clock
...timing.testkit.rfid
...timing.testkit.can
...timing.testkit.display
...timing.testkit.backoffice
...timing.testkit.scenario
```

Production application modules must not depend on `timing-testkit` unless they deliberately run in a development/demo profile that packages test devices. Prefer a separate reference/test application composition for that case.

## `timing-app`

Purpose: small public executable/reference application that composes framework modules and default/stub adapters.

This module should contain very little behaviour. It proves that the public components can produce a complete runnable application.

```text
main()
  -> load settings
  -> choose configured adapters
  -> compose runtime
  -> start interfaces
  -> start TimingSystem instances
```

If composition becomes complex, a dedicated `timing-composition` module can be introduced later, but it is not needed initially.

## Dependency direction

Desired compile-time direction:

```text
                 +----------------+
                 |   timing-api   |
                 +-------^--------+
                         |
                 +-------+--------+
                 |   timing-core  |
                 +-------^--------+
                         |
                 +-------+--------+
                 | timing-runtime |
                 +-------^--------+
                         |
          +--------------+--------------+
          |                             |
+---------+---------+          +--------+--------+
| timing-adapters   |          |   timing-app    |
+-------------------+          +-----------------+

Private/public adapter implementations depend on timing-api
(and only on timing-core/runtime when there is a deliberate need).
```

The important inversion is that core behaviour knows **ports/contracts**, while concrete adapters depend on and implement those contracts.

## Public versus proprietary implementation

Some real device control and protocols are expected to remain private, including candidate areas such as:

- production RFID antenna control;
- RFID/tag protocol/decryption details;
- production backoffice protocol/message contracts where these are product-specific;
- other proprietary device implementations.

The public framework should expose only the contract required to plug those implementations in.

Example:

```java
// public timing-api
public interface RfidReaderPort {
    void powerOn();
    void powerOff();
    void initialise();
    void setListener(RfidReaderListener listener);
}
```

A private repository can then provide:

```java
public final class ProductionRfidReaderAdapter implements RfidReaderPort {
    // proprietary protocol / hardware implementation
}
```

The core application does not know which repository supplied the implementation.

## Avoid a generic `impl` package structure

Avoid structures such as:

```text
service/
impl/
util/
manager/
controller/
```

as the dominant top-level package taxonomy. They mix unrelated capabilities and make it difficult to see ownership.

Prefer:

```text
registration/
rfid/
display/
reference/
status/
```

and only use a technical subpackage when a capability genuinely needs it.

For example:

```text
...registration.model
...registration.command
...registration.internal
```

can be reasonable, while one application-wide `...service.impl` package is not.

## Visibility policy

Prefer package-private implementation classes when they are not part of a module contract.

Keep exported/public classes deliberately small. Java 8 does not provide JPMS module descriptors, so Maven dependency boundaries, package visibility, tests, and architecture checks must provide the discipline initially.

A later move to Java 11 does not automatically imply adopting JPMS; that should be a separate decision.

## Architecture tests

Because Java 8 cannot enforce module exports with JPMS, consider automated architecture tests once the package layout exists.

Examples of useful rules:

- `timing-core` may not reference adapter packages;
- domain/core packages may not reference HTTP/RabbitMQ/CAN implementation libraries;
- public API packages may not depend on implementation packages;
- adapter packages may depend inward but not the reverse;
- testkit must not leak into production dependencies.

A library such as ArchUnit could be evaluated later if its Java-8-compatible version and footprint/build implications are acceptable. Maven module dependency checks can enforce a large part of this even without ArchUnit.

## Reference/test application strategy

A separate **reference/test project** should consume the public framework exactly as an external product would.

Its jobs are to:

- prove released/public Maven artifacts are usable outside the framework reactor;
- provide a runnable application using public/stub adapters;
- exercise system-level interfaces and IDDs;
- provide integration-test scenarios;
- act as a template/example for a complete application;
- prove the extension points required by proprietary modules.

Conceptually:

```text
public framework repository
    timing-api
    timing-core
    timing-runtime
    public adapters
    timing-testkit
             |
             | Maven dependencies
             v
public reference/test application
    reference composition
    stub/default components
    integration tests
             |
             | same extension contracts
             v
private product/integration repository
    proprietary RFID adapter
    proprietary protocol adapter(s)
    private backoffice implementation where required
    product configuration/composition
```

The private product repository should not fork or copy framework source. It should compose released/versioned public artifacts plus private Maven artifacts.

## Dependency injection / composition

Do not choose a large dependency-injection framework merely to solve composition.

The first implementation can use explicit constructor injection and a composition root:

```java
RfidReaderPort rfid = adapterFactory.createRfid(settings);
RegistrationRepository registrations = new InMemoryRegistrationRepository();
DisplayPort display = adapterFactory.createDisplay(settings);

TimingSystem timingSystem = new TimingSystem(
    registrations,
    rfid,
    display,
    clock,
    statusService);
```

This is transparent, Java-8-friendly and easy to unit test.

If runtime plugin discovery becomes a real requirement later, evaluate `ServiceLoader` or a dedicated plugin mechanism separately. Do not introduce dynamic plugin loading merely because public and private modules exist in separate repositories.

## Candidate repository split

Names are illustrative and should be decided deliberately before repositories are created:

```text
2026-010-01.meta.event-timing-software   planning / requirements / architecture
2026-010-02.java.event-timing-framework  public reusable framework + public adapters/testkit
2026-010-03.java.event-timing-reference  public external reference/test application
<private repository>                      product composition + proprietary adapters/protocols
```

The key architectural test is that `event-timing-reference` and the private product use the **same public extension contracts**.

## Open decisions

- final Maven groupId/artifactId convention;
- whether `timing-api` should initially be one module or split into `core-api` and device/extension API later;
- how configuration selects concrete adapters;
- whether public adapter implementations belong in the framework repository or separate adapter repositories over time;
- where the compiled React application belongs in the Maven/repository structure;
- how private Maven artifacts are made available securely to private CI/builds;
- exact release/version alignment between public framework artifacts and private implementations;
- whether the public reference/test application is also the software template from which concrete product-composition repositories are initially bootstrapped.

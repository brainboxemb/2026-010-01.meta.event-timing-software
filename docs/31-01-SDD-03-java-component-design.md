# Java component and package structure

Status: working draft / non-authoritative

Software item: **SI-01 — Headless Timing Application**

This SDD proposes the initial Java/Maven component structure. Its main purpose is to keep **architectural responsibility**, **Maven modules**, and **Java packages** distinct so layering does not become ambiguous.

The runtime/source hierarchy is defined in more detail in `31-01-SDD-04-runtime-topology-and-configuration.md`.

## Core rule

Use three concepts for three different jobs:

1. **Architecture responsibility** — what code is allowed to know and do.
2. **Maven module** — compile-time dependency, publication and ownership boundary.
3. **Java package** — cohesive organisation *inside* a module.

Do not create a Maven module for every package and do not rely on package names alone to enforce architecture.

## Initial Maven reactor

Start deliberately small:

```text
event-timing/
├── pom.xml
├── timing-api/          public contracts and shared cross-module models
├── timing-core/         application/domain behaviour
├── timing-runtime/      hosting, routing, scheduling and serialized execution
├── timing-adapters/     public/default infrastructure adapters
├── timing-testkit/      reusable fakes, stubs and test scenarios
└── timing-app/          small public executable/composition example
```

Split modules further only when there is a real dependency, platform, release, ownership or public/private reason.

## `timing-api`

Purpose: stable types that public and proprietary implementations are intentionally allowed to depend on.

Possible packages:

```text
...timing.api.model
...timing.api.command
...timing.api.query
...timing.api.event
...timing.api.status
...timing.api.port
...timing.api.extension
```

Candidate contracts include:

- RFID antenna/reader control and observation ports;
- CAN transport/device contracts;
- display data/session contracts;
- backoffice/reference-data contracts;
- clock/platform abstractions;
- externally exposed status/query models;
- extension/composition contracts.

Keep this module conservative. A class belongs here only because it is an intentional cross-module contract, not merely because two modules happen to use it.

## `timing-core`

Purpose: application/domain behaviour independent from concrete hardware, network, filesystem and UI technologies.

Top-level packages should be organised by **capability**, not by vague technical categories such as one application-wide `service`, `manager`, `impl` or `util` package.

Proposed capability structure:

```text
...timing.core.timingsystem
    TimingSystemInstance
    TimingSystemInstanceId
    TimingSystemInstanceState
    TimingSystemHandler

...timing.core.registrationsystem
    RegistrationSystem
    RegistrationSystemId
    RegistrationSystemRegistry
    RegistrationSequence
    AntennaId
    AntennaBinding

...timing.core.registration
    RegistrationService
    RegistrationRecord
    RegistrationLedger
    RegistrationRepository

...timing.core.readyteam
    ReadyTeamService
    ReadyTeamEventJournal
    ReadyTeamEventRepository
    ReadyTeamState
    ReadyTeamSequence

...timing.core.rfid
    RfidService
    TagDecryptor
    TagFilter
    ParticipantResolver

...timing.core.start
    StartProcedureService

...timing.core.penalty
    PenaltyService

...timing.core.reference
    ReferenceDataService
    StartTimeRepository
    ReserveTagRepository

...timing.core.display
    DisplayService
    DisplayModelBuilder

...timing.core.status
    StatusService
```

### Total system versus registration source

These are different aggregates and the Java model must make that obvious.

```text
TimingSystemInstance
  lifecycle / ready-team / start procedure / display / instance state
       |
       +-- 1..X RegistrationSystem
               source identity
               source sequence
               source registration file
               1..X antenna bindings
```

A `RegistrationSystem` owns **source identity and source-scoped sequence state**. It is not merely a field on `RegistrationRecord`.

The actual registration record capability remains separate:

```text
RegistrationSystem
    |
    | allocates source sequence / selects source repository
    v
RegistrationService
    |
    v
RegistrationRecord / RegistrationLedger
```

This prevents `RegistrationSequence` from accidentally becoming one global or one-total-system counter.

### Registration and ready-team are deliberately separate

These are different capabilities even though both require traceability and persistence:

```text
registration
  passage / start / manual / penalty / revocation / operational registration entries
  sequence allocated by RegistrationSystem source
  registration ledger
  local result/ranking derivation

readyteam
  team added / team removed
  traceable operational journal
  current ReadyTeamState projection
  feeds current display state
```

A keypad action must therefore not create a participant/timing `RegistrationRecord` merely because it is persisted. It creates a `ReadyTeamEvent` and updates the ready-team projection.

Dependencies:

```text
timing-core -> timing-api
```

`timing-core` must not reference HTTP servers, RabbitMQ libraries, concrete CAN libraries, Raspberry Pi libraries or proprietary RFID protocol code.

## `timing-runtime`

Purpose: host `1..X` complete `TimingSystemInstance` objects and provide non-domain execution/orchestration infrastructure.

Likely packages:

```text
...timing.runtime.bootstrap
...timing.runtime.configuration
...timing.runtime.execution
...timing.runtime.routing
...timing.runtime.lifecycle
...timing.runtime.scheduling
...timing.runtime.status
```

Responsibilities include:

- application/runtime registry;
- constructing configured system instances;
- routing commands/queries to a system instance;
- routing antenna observations through configured `AntennaBinding` data;
- ingress queues;
- logical `SerialExecutor` implementation;
- scheduling heartbeat/scanner/connectivity messages;
- runtime lifecycle;
- runtime-wide status aggregation.

The proposed threading model is **logical serialization per `TimingSystemInstance`**, not one OS thread per system, registration source or antenna. Multiple logical serial executors may use a small shared backing executor on Raspberry Pi Zero.

Dependencies:

```text
timing-runtime -> timing-core -> timing-api
```

## `timing-adapters`

Purpose: public/default concrete implementations of ports.

An initial single module can use capability-oriented packages:

```text
...timing.adapter.console
...timing.adapter.remote
...timing.adapter.http
...timing.adapter.websocket
...timing.adapter.memory
...timing.adapter.filebackup
...timing.adapter.stub
```

Later, heavy/platform-specific adapters can become separate Maven artifacts, for example:

```text
timing-adapter-rabbitmq
timing-adapter-linux-can
timing-adapter-mdns
```

Production/proprietary adapters should normally live in a private repository rather than inside the public adapter module.

## `timing-testkit`

Purpose: reusable test components for framework tests, the external reference application and private integration tests.

Expected contents include:

```text
DirectExecutor
FakeClock
InMemoryRegistrationRepository
InMemoryReadyTeamEventRepository
StubRfidAdapter
StubCanAdapter
StubDisplayV1
StubDisplayV2Session
StubBackofficeAdapter
ScenarioBuilder
TopologyBuilder
status/registration/ready-team assertions
```

Possible packages:

```text
...timing.testkit.execution
...timing.testkit.clock
...timing.testkit.registration
...timing.testkit.readyteam
...timing.testkit.rfid
...timing.testkit.can
...timing.testkit.display
...timing.testkit.backoffice
...timing.testkit.topology
...timing.testkit.scenario
```

The test-control interface manipulates stubs/adapters and still drives the normal application path. It must not mutate domain state directly.

A particularly important integration-test use case is constructing a multi-instance, multi-source topology to emulate complete field behaviour towards the backoffice.

## `timing-app`

Purpose: a small executable/composition example inside the framework repository.

It should contain little or no domain logic:

```text
main()
  -> load settings
  -> validate topology
  -> construct/select adapters
  -> construct runtime
  -> create configured TimingSystemInstances
  -> create RegistrationSystems + antenna bindings
  -> start public interfaces
```

The more important external consumer proof belongs in a **separate reference/test repository**.

## Dependency direction

Conceptually:

```text
                    timing-api
                 /      |       \
                /       |        \
        timing-core   adapters   private adapters
             |
        timing-runtime
             |
          timing-app
```

Adapters implement API ports and are selected in the composition root. Core behaviour must never depend back outward on a concrete adapter.

Where an adapter only needs `timing-api`, it should not depend on `timing-core` or `timing-runtime` unnecessarily.

## Public versus proprietary components

Expected proprietary areas include candidates such as:

- production RFID antenna control;
- production RFID protocol/decryption details;
- product-specific communication/protocol implementations;
- potentially production backoffice message contracts/adapter implementation.

The public framework exposes only the contracts required for those components.

Example public contract:

```java
public interface RfidAntennaPort {
    AntennaId id();
    void powerOn();
    void powerOff();
    void initialise();
    void setListener(RfidReaderListener listener);
}
```

Private repository:

```java
public final class ProductionRfidAntennaAdapter implements RfidAntennaPort {
    // proprietary hardware/protocol implementation
}
```

The public framework must not import or compile against that private implementation.

## Composition rather than subclassing

Do not make subclassing the primary extension mechanism.

Prefer constructor injection and composition.

Illustrative composition:

```java
RegistrationSystem sourceA = new RegistrationSystem(
    RegistrationSystemId.of("A"),
    sequenceA,
    registrationRepositoryA,
    Arrays.asList(rsAntenna1));

TimingSystemInstance instance = new TimingSystemInstance(
    instanceId,
    Arrays.asList(sourceA),
    readyTeamState,
    displayService,
    clock,
    statusService);
```

The actual constructor surface may use factories/builders to avoid large parameter lists.

No large dependency-injection framework is required initially.

If true runtime plugin discovery later becomes necessary, evaluate `ServiceLoader` or another plugin mechanism as a separate architecture decision. Separate repositories alone do **not** require dynamic plugin loading.

## Settings and composition root

Configuration must describe the runtime topology without naming private Java classes in public source.

A composition/factory layer resolves configured adapter types to actual implementations.

Conceptually:

```java
interface AdapterFactoryRegistry {
    RfidAntennaPort createRfid(String adapterType, DeviceSettings settings);
}
```

A public distribution can register public/stub factories. A private product repository can register proprietary factories during composition.

The final file format and factory mechanism remain open.

## External reference/test project

A separate public project should consume the framework exactly like an external application.

Conceptually:

```text
public framework repository
  timing-api
  timing-core
  timing-runtime
  public adapters
  timing-testkit
           |
           | Maven artifacts
           v
public reference/test repository
  application composition
  configurable multi-instance topology
  stub/default components
  integration scenarios
           |
           | same public contracts
           v
private product/integration repository
  proprietary RFID adapter
  proprietary protocols
  production composition/configuration
```

The reference project should prove:

- framework artifacts work outside their own reactor;
- documentation is sufficient for an external consumer;
- stub components can produce a complete application;
- multiple system instances and source streams can be configured;
- system IDDs can be exercised in integration tests;
- the same extension points are usable by a private repository;
- no framework source copy/fork is required.

Illustrative repository names remain:

```text
2026-010-01.meta.event-timing-software
2026-010-02.java.event-timing-framework
2026-010-03.java.event-timing-reference
<private product/integration repository>
```

## Package visibility

Prefer package-private implementation classes when they are not part of a supported contract.

Java 8 has no JPMS module descriptors, so discipline initially comes from:

- Maven module dependencies;
- minimal public API surface;
- package visibility;
- unit/integration tests;
- optional architecture tests.

A later Java 11 migration does not automatically mean JPMS should be adopted.

## Architecture checks

Useful automated rules can eventually include:

- `timing-core` does not reference adapter packages;
- `timing-core` does not reference HTTP/RabbitMQ/CAN implementation libraries;
- API packages do not depend on implementation packages;
- `RegistrationSequence` exists at registration-system/source scope, not as one global counter;
- registration-system topology is not inferred from adapter implementation classes;
- `registration` does not depend on `readyteam` merely to update a display;
- `readyteam` does not create participant/timing registration-domain records;
- adapters depend inward, never the reverse;
- testkit is absent from production runtime dependencies unless an explicit demo/test composition includes it.

A Java-8-compatible ArchUnit version can be evaluated later, but Maven dependency checks already enforce important boundaries.

## Open decisions

- final Maven `groupId` and artifact naming convention;
- whether `timing-api` stays one module or is split after extension contracts stabilise;
- final configuration file format and include/override model;
- how configuration selects adapter implementations;
- private Maven artifact publication/consumption mechanism;
- version alignment between framework/API and private adapters;
- where the compiled React application belongs;
- whether public adapter implementations eventually move to independent repositories;
- exact boundary between public reference application and private product composition.

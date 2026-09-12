# Java component and package structure

Status: working draft / non-authoritative

This SDD proposes an initial Java/Maven component structure. Its main purpose is to keep **architectural responsibility**, **Maven modules**, and **Java packages** distinct so layering does not become ambiguous.

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
├── timing-core/         TimingSystem/application/domain behaviour
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

- RFID reader/control and observation ports;
- CAN transport/device contracts;
- display data/session contracts;
- backoffice/reference-data contracts;
- clock/platform abstractions;
- externally exposed status/query models;
- extension/composition contracts.

Keep this module conservative. A class belongs here only because it is an intentional cross-module contract, not merely because two modules happen to use it.

## `timing-core`

Purpose: timing-system/application behaviour independent from concrete hardware, transport, filesystem and UI technologies.

Top-level packages should be organised by **capability**, not by vague technical categories such as one application-wide `service`, `manager`, `impl` or `util` package.

Proposed capability structure:

```text
...timing.core.timingsystem
    TimingSystem
    TimingSystemState
    TimingSystemHandler

...timing.core.registration
    RegistrationService
    RegistrationLedger
    RegistrationRepository
    RegistrationSequence

...timing.core.readyteam
    ReadyTeamService
    ReadyTeamEventJournal
    ReadyTeamEventRepository
    ReadyTeamState
    ReadyTeamSequence

...timing.core.rfid
    RfidService
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

### Registration and ready-team are deliberately separate

These are different capabilities even though both require traceability and persistence:

```text
registration
  passage / start / manual / penalty / revocation
  unique sequence
  registration ledger
  local result/ranking derivation

readyteam
  team added / team removed
  traceable operational journal
  current ReadyTeamState projection
  feeds current display state
```

A keypad action must therefore not create a `RegistrationRecord` merely because it is persisted. It creates a `ReadyTeamEvent` and updates the ready-team projection.

This distinction should remain visible in package names, types, repositories and tests.

Dependencies:

```text
timing-core -> timing-api
```

`timing-core` must not reference HTTP servers, RabbitMQ libraries, a concrete CAN library, Raspberry Pi libraries or proprietary RFID protocol code.

## `timing-runtime`

Purpose: host `1..X` logical timing systems and provide non-domain execution/orchestration infrastructure.

Likely packages:

```text
...timing.runtime.bootstrap
...timing.runtime.execution
...timing.runtime.routing
...timing.runtime.lifecycle
...timing.runtime.scheduling
...timing.runtime.status
```

Responsibilities include:

- timing-system registry;
- routing messages to a timing-system instance;
- ingress queues;
- logical `SerialExecutor` implementation;
- scheduling heartbeat/scanner/connectivity messages;
- runtime lifecycle;
- runtime-wide status aggregation.

The proposed threading model is **logical serialization per TimingSystem**, not necessarily one OS thread per system. Multiple logical serial executors may use a small shared backing executor on Raspberry Pi Zero.

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

Expected contents:

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
...timing.testkit.scenario
```

The test-control interface must manipulate the stubs/adapters and still drive the normal application path. It should not mutate domain state directly.

## `timing-app`

Purpose: a small executable/composition example inside the framework repository.

It should contain little or no domain logic:

```text
main()
  -> load settings
  -> construct/select adapters
  -> construct runtime
  -> start public interfaces
  -> create configured TimingSystem instances
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

More precisely, adapters implement API ports and are selected in the composition root. Core behaviour must never depend back outward on a concrete adapter.

Where an adapter only needs `timing-api`, it should not depend on `timing-core` or `timing-runtime` unnecessarily.

## Public versus proprietary components

Expected proprietary areas include at least candidates such as:

- production RFID antenna control;
- production RFID protocol/decryption details;
- product-specific communication/protocol implementations;
- potentially production backoffice message contracts/adapter implementation.

The public framework exposes only the contracts required for those components.

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

Private repository:

```java
public final class ProductionRfidReaderAdapter implements RfidReaderPort {
    // proprietary hardware/protocol implementation
}
```

The public framework must not import or compile against that private implementation.

## Composition rather than subclassing

Do not make subclassing the primary extension mechanism.

Prefer constructor injection and composition:

```java
RegistrationRepository registrations = repositories.registration();
ReadyTeamEventRepository readyTeamEvents = repositories.readyTeams();
RfidReaderPort rfid = adapters.rfid();
DisplaySink display = adapters.display();

TimingSystem system = new TimingSystem(
    registrations,
    readyTeamEvents,
    rfid,
    display,
    clock,
    statusService);
```

No large dependency-injection framework is required initially.

If true runtime plugin discovery later becomes necessary, evaluate `ServiceLoader` or another plugin mechanism as a separate architecture decision. Separate repositories alone do **not** require dynamic plugin loading.

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
- `registration` does not depend on `readyteam` merely to update a display;
- `readyteam` does not create registration-domain records;
- adapters depend inward, never the reverse;
- testkit is absent from production runtime dependencies unless an explicit demo/test composition includes it.

A Java-8-compatible ArchUnit version can be evaluated later, but Maven dependency checks already enforce important boundaries.

## Open decisions

- final Maven `groupId` and artifact naming convention;
- whether `timing-api` stays one module or is split after extension contracts stabilise;
- how application configuration selects adapter implementations;
- private Maven artifact publication/consumption mechanism;
- version alignment between framework/API and private adapters;
- where the compiled React application belongs;
- whether public adapter implementations eventually move to independent repositories;
- exact boundary between public reference application and private product composition.

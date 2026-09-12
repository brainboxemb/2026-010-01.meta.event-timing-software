# Timing Application Architecture (SAD)

Status: working draft / non-authoritative

Software item: **SI-01 — Headless Timing Application**

This Software Architecture Document describes the architecture of software item 01: the headless Java timing application. It sits below the system-level architecture in `30-SSAD-software-system-architecture.md` and above the detailed design documents that share the `31-01` software-item prefix.

## Document relationship

```text
30-SSAD  Software-system architecture
    |
    v
31-01-SAD  Software item 01 — Timing Application Architecture
    |
    +-- 31-01-SDD-01  TimingSystem detailed design
    +-- 31-01-SDD-02  Data and display detailed design
    +-- 31-01-SDD-03  Java component/package detailed design
    +-- 31-01-SDD-04  Runtime topology and configuration
    +-- 31-01-SDD-05  Backoffice transport detailed design
```

The `01` identifies the software item, not the document sequence. Software item 02 is the desktop GUI application and software item 03 is the browser/iPad operator application.

System interfaces remain system-owned and are documented in system-level IDDs. Software-item requirements may reference those IDDs as applicable requirements.

## Responsibility

The timing application is the headless system authority for local timing/registration operation. It is responsible for:

- process lifecycle and composition;
- hosting `1..X` logical `TimingSystemInstance` objects;
- routing commands, queries and device observations;
- central application/timing-system status;
- local console and remote-control interfaces;
- HTTP/JSON and WebSocket system interfaces;
- RFID, CAN, keypad and display integration through ports;
- local registration, ready-team and reference-data state;
- local backup/restore;
- transport-independent backoffice synchronisation;
- platform abstraction and Raspberry Pi Zero operation;
- public/stub/proprietary adapter composition through common contracts.

Presentation clients such as the desktop GUI and browser/iPad application are separate software items and do not own authoritative timing-domain state.

## Layered application architecture

The primary SI-01 application-architecture view is a responsibility/layer view. It describes architectural ownership and dependency direction; it does **not** prescribe one Maven artifact per layer.

![SI-01 layered architecture](../../../raw/prod/docs/assets/architecture/layered-architecture.svg)

The source for this view is `docs/_diagrams/layered-architecture.yaml`.

### Presentation

Presentation exposes application behaviour and current state to external clients through concerns such as:

```text
HTTP / JSON
WebSocket
local console
remote shell
protocol/DTO mapping for those interfaces
```

Presentation translates external requests into application commands/queries and application status/events into external representations. It does not own running application state.

### Application

The application responsibility owns running application state and coordinates use cases. Representative concerns include:

```text
TimingSystemInstance state
registration/source ledgers and current runtime state
commands / queries / workflows
status management and aggregation
immutable status snapshots
single-system or multi-system application coordination
```

The application responsibility invokes domain services and coordinates persistence/integration ports without moving transport/protocol details into domain behaviour.

### Domain

The domain responsibility owns reusable event-timing rules, services, entities and value semantics. Representative services currently include:

```text
RegistrationService
StartTimeService
ReadyTeamService
ReferenceDataService
```

Representative domain concepts include `TimingSystemInstance` identity/value concepts, `RegistrationAsset`, `RegistrationSource`, `RegistrationSequence`, registration observations/results, start-time values, ready-team values and reference-data value objects.

`RegistrationSequence` remains registration-source scoped. Product/deployment-specific policy does not automatically belong in the reusable domain model.

### Core runtime support

Core runtime support provides reusable execution mechanics that let application/domain behaviour run predictably, for example:

```text
serialized execution
lifecycle mechanics
routing primitives
scheduling
command/event dispatch mechanics
```

Core runtime support is not a second owner of domain behaviour or application state.

### Infrastructure / integration

Integration implementations connect SI-01 to external systems/devices and persistence mechanisms, including:

```text
persistence / file backup and restore
backoffice socket / RabbitMQ integration
RFID integration
CAN integration
display integration
```

The distinction from presentation is semantic: presentation is how external clients inspect/control SI-01, while integrations are how SI-01 interacts with backoffice, devices and persistence.

### Platform

Platform abstractions isolate execution-environment and low-level facilities such as:

```text
Clock / time source
filesystem/path primitives
executor/thread primitives
process/runtime information
network/OS primitives
low-level platform/device primitives where portability requires them
```

Platform is not a catch-all location for HTTP, RabbitMQ or device/domain protocols.

### Cross-cutting concerns

Cross-cutting concerns may span multiple responsibilities without becoming owners of domain/application state. Examples include logging, configuration, diagnostics and build/version identity.

Detailed Java package, Maven artifact and contract placement that implements this architecture belongs in `31-01-SDD-03-java-component-design.md`.

## Runtime hierarchy

A `TimingSystemInstance` is the primary logical isolation and ordering boundary inside this software item. One application process may host multiple independently addressed total systems.

```text
TimingApplicationRuntime
    |
    +-- TimingSystemInstance system-01
    |      +-- 1..X RegistrationAsset
    |              +-- 1..X antenna
    |              +-- 1..X RegistrationSource
    |
    +-- TimingSystemInstance system-02
           +-- ...
```

A registration asset represents the configured physical/logical box. A registration source represents one ordered registration stream with its own external source ID, monotonic sequence and source-specific registration file. One asset may expose multiple sources, including virtual sources.

Runtime-wide infrastructure may be shared where that does not leak mutable timing-system state. Candidates include thread pools, logging, HTTP server infrastructure, backoffice transport infrastructure, configuration loading and network monitoring.

Detailed topology belongs in `31-01-SDD-04-runtime-topology-and-configuration.md`.

## Command, query and event boundary

All operator/client transports should converge on one shared application model.

```text
local console -------+
remote shell --------+
HTTP/JSON -----------+--> command/query boundary --> runtime / TimingSystemInstance
WebSocket <-----------+<-- status/events ----------------+
```

The desktop GUI must be able to use this interface while the timing application runs on a separate Raspberry Pi. The GUI therefore cannot rely on in-process Java calls or local filesystem access to the timing application.

The browser/iPad client is expected to use the same application boundary through HTTP/WebSocket.

This application interface is also the primary entry point for the fastest automated application-behaviour system tests.

## Threading and concurrency

External I/O threads/callbacks must not directly mutate timing-system state.

Proposed processing model:

1. capture source timestamps at the adapter boundary where timing matters;
2. convert input into immutable commands/events;
3. enqueue work for the addressed `TimingSystemInstance`;
4. serialize state-changing processing for that timing system;
5. keep blocking hardware/network/file work outside the serialized state path;
6. return relevant completion/failure as messages/events.

A logical serial executor does not imply one operating-system thread per timing system. Multiple logical executors may use a small shared executor appropriate to Raspberry Pi Zero constraints.

The same handlers should run synchronously with a direct executor in unit tests.

## Status architecture

Status is a first-class application model and is distinct from logging. Immutable status snapshots should cover application, timing-system and subsystem health so console, GUI, browser and monitoring integrations observe the same state.

Examples include:

- application version / uptime / overall health;
- timing-system `OPEN` / `CLOSED` state;
- registration asset/source status;
- RFID power / startup / protocol / heartbeat;
- CAN bus and discovery;
- keypad activity where observable;
- display state;
- persistence/backup state;
- reference-data freshness;
- local network / internet / backoffice transport connectivity;
- per-source inbound/outbound synchronisation status.

## Persistence architecture

The initial design uses typed in-memory repositories/state with simple file backup/restore rather than requiring an embedded database engine.

Separate concepts include:

- ingress queue — ordering/thread safety;
- registration ledger — traceable registration history;
- source-specific registration files and sequence state;
- ready-team journal/state — traceable prepare/remove history and current state;
- reference data — start times and reserve-tag mappings;
- backup/restore — local restart recovery;
- backoffice outbox — pending external synchronisation.

Detailed data/display behaviour belongs in `31-01-SDD-02-data-and-display-design.md`.

## Backoffice transport abstraction

RabbitMQ is not the application-level backoffice interface. The application depends on source-aware semantic ports and a local outbox.

```text
application/domain
    BackofficePublisherPort / inbound listener
            |
            +--> StubBackofficeAdapter
            +--> SocketBackofficeAdapter
            +--> RabbitMqBackofficeAdapter
            +--> private/proprietary adapter/codec where needed
```

The lightweight socket adapter exists so multi-process/network system behaviour can be tested without RabbitMQ or Docker. It uses a synthetic/public test protocol and must not expose or copy proprietary production serialization.

The RabbitMQ adapter provides the production-shaped broker transport. Several registration sources may have independent inbound consumers/routing while sharing one physical broker connection.

Detailed backoffice design belongs in `31-01-SDD-05-backoffice-transport-design.md`.

## Hardware and platform abstraction

Core/application/domain code depends on public contracts rather than concrete device libraries. Important port families include RFID, CAN, display, backoffice, clock, settings/secrets, persistence/backup and platform capabilities.

Those contracts must support public/default implementations, development/test stubs, lightweight socket/network test adapters and private/proprietary production implementations.

## Public/private extension model

Private repositories may provide production RFID antenna control, encrypted RFID protocol/decryption, product-specific communication protocols, production asset/source mappings and proprietary backoffice message codecs. The public framework must compile and test without those private implementations or identities.

## System-test architecture direction

The architecture intentionally supports progressively more realistic automated system tests:

```text
ST-1  Application behaviour
      real SI-01 process + public application interface + stub dependencies

ST-2  Socket loop/network
      real SI-01 process + simple socket backoffice simulator

ST-3  RabbitMQ integration
      real SI-01 process + disposable RabbitMQ broker

ST-4+ Pi Zero / hardware / full-system profiles
```

ST-1 should provide the fastest application-level regression feedback. ST-2 verifies a real process/network boundary without external broker infrastructure. ST-3 verifies RabbitMQ-specific broker/channel/recovery behaviour.

Detailed verification strategy belongs in `50-SVP-software-verification-plan.md`.

## Technology baseline

Current baseline decisions/directions include:

- Maven;
- Java SE 8 initially, driven by mandatory original Raspberry Pi Zero support;
- Java 11 as an evidence-driven future upgrade candidate;
- externally configured settings/credentials/topology/transport selection;
- generated architecture documentation;
- Docker/Compose only where real external integration services such as RabbitMQ materially improve verification;
- generated architecture documents/diagrams published to `dev/pr-<N>/docs` and `prod/docs`.

## Relationship to GUI software item

Software item 02 is the desktop GUI application. Its architecture is separate from this SAD.

The intended boundary is network-based:

```text
Desktop GUI (software item 02)
          |
          | system-defined control/status interface
          v
Timing Application (software item 01)
          |
          v
Raspberry Pi / Windows / Linux host
```

The GUI should therefore be testable against a local development runtime, a stub/reference application, and a real timing application running remotely on a Raspberry Pi.

A system-level operator-GUI IDD may define the user-facing screen/interaction contract. A separate system-level application-control IDD can define the software-to-software network contract. The GUI SRD can reference both.

## Detailed design documents

- `31-01-SDD-01-timing-system-design.md`
- `31-01-SDD-02-data-and-display-design.md`
- `31-01-SDD-03-java-component-design.md`
- `31-01-SDD-04-runtime-topology-and-configuration.md`
- `31-01-SDD-05-backoffice-transport-design.md`

These documents are refinements, not an instruction to split every architectural responsibility into a separate detailed-design document.

## Open architecture questions

- exact queue/backpressure and serial-executor topology;
- Java-8-compatible HTTP/WebSocket and remote-shell technologies;
- logging framework;
- reference ARMv6 Java 8 runtime;
- configuration/secrets hierarchy and file format;
- persistence durability semantics;
- exact public API/SPI boundaries;
- exact socket-test framing;
- RabbitMQ one- versus two-connection strategy;
- system-level IDD breakdown;
- later Java 11 migration criteria.

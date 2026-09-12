# Timing Application Architecture (SAD)

Status: working draft / non-authoritative

Software item: **01 — Headless Timing Application**

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
```

The `01` identifies the software item, not the document sequence. Future software item 02 is the desktop GUI application; a browser/iPad application is a candidate software item 03.

System interfaces remain system-owned and are documented in system-level IDDs. Software-item requirements may reference those IDDs as applicable requirements.

## Responsibility

The timing application is the headless system authority for local timing/registration operation. It is responsible for:

- process lifecycle and composition;
- hosting `1..X` logical `TimingSystem` instances;
- routing commands, queries and device observations;
- central application/timing-system status;
- local console and remote-control interfaces;
- HTTP/JSON and WebSocket system interfaces;
- RFID, CAN, keypad and display integration through ports;
- local registration, ready-team and reference-data state;
- local backup/restore;
- backoffice synchronisation;
- platform abstraction and Raspberry Pi Zero operation;
- public/stub/proprietary adapter composition through common contracts.

Presentation clients such as the desktop GUI and browser/iPad application are separate software items and do not own authoritative timing-domain state.

## Application decomposition

```text
Timing Application
  |
  +-- bootstrap / composition root
  |
  +-- external interface adapters
  |     local console
  |     remote shell
  |     HTTP / JSON
  |     WebSocket
  |
  +-- runtime / orchestration
  |     TimingSystem registry
  |     routing
  |     scheduling
  |     serialized execution
  |     runtime status aggregation
  |
  +-- application/domain capabilities
  |     registration
  |     ready-team
  |     RFID processing
  |     start procedure
  |     penalties
  |     reference data
  |     display model
  |     status
  |
  +-- ports / contracts
        persistence / backup
        RFID
        CAN
        display
        backoffice
        clock
        settings / secrets
        platform capabilities
```

Concrete device, transport and platform implementations remain outside the core behaviour.

## TimingSystem boundary

A `TimingSystem` is the primary logical isolation and ordering boundary inside this software item. One application process may host multiple independently addressed timing systems.

```text
TimingApplicationRuntime
    |
    +-- TimingSystem A
    +-- TimingSystem B
    +-- TimingSystem C
```

Runtime-wide infrastructure may be shared where that does not leak mutable timing-system state. Candidates include thread pools, logging, HTTP server infrastructure, RabbitMQ infrastructure, configuration loading and network monitoring.

Detailed timing-system behaviour belongs in `31-01-SDD-01-timing-system-design.md`.

## Command, query and event boundary

All operator/client transports should converge on one shared application model.

```text
local console -------+
remote shell --------+
HTTP/JSON -----------+--> command/query boundary --> runtime / TimingSystem
WebSocket <-----------+<-- status/events ------------+
```

The desktop GUI must be able to use this interface while the timing application runs on a separate Raspberry Pi. The GUI therefore cannot rely on in-process Java calls or local filesystem access to the timing application.

The browser/iPad client is expected to use the same application boundary through HTTP/WebSocket.

## Threading and concurrency

External I/O threads/callbacks must not directly mutate timing-system state.

Proposed processing model:

1. capture source timestamps at the adapter boundary where timing matters;
2. convert input into immutable commands/events;
3. enqueue work for the addressed `TimingSystem`;
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
- RFID power / startup / protocol / heartbeat;
- CAN bus and discovery;
- keypad activity where observable;
- display state;
- persistence/backup state;
- reference-data freshness;
- local network / internet / RabbitMQ connectivity.

## Persistence architecture

The initial design uses typed in-memory repositories/state with simple file backup/restore rather than requiring an embedded database engine.

Separate concepts include:

- ingress queue — ordering/thread safety;
- registration ledger — traceable registration history;
- ready-team journal/state — traceable prepare/remove history and current state;
- reference data — start times and reserve-tag mappings;
- backup/restore — local restart recovery;
- backoffice outbox — pending external synchronisation.

Detailed data/display behaviour belongs in `31-01-SDD-02-data-and-display-design.md`.

## Hardware and platform abstraction

Core code depends on public contracts rather than concrete libraries. Important port families include RFID, CAN, display, backoffice, clock, settings/secrets, persistence/backup and platform capabilities.

Those same public contracts must support:

- public/default implementations;
- development/test stubs;
- private/proprietary production implementations.

## Public/private extension model

Private repositories may provide production RFID antenna control, encrypted RFID protocol/decryption, product-specific communication protocols and other proprietary adapters. The public framework must compile and test without those private implementations.

The detailed Maven/module/package design belongs in `31-01-SDD-03-java-component-design.md`.

## Technology baseline

Current baseline decisions/directions include:

- Maven;
- Java SE 8 initially, driven by mandatory original Raspberry Pi Zero support;
- Java 11 as an evidence-driven future upgrade candidate;
- externally configured settings/credentials;
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

## Open architecture questions

- exact queue/backpressure and serial-executor topology;
- Java-8-compatible HTTP/WebSocket and remote-shell technologies;
- logging framework;
- reference ARMv6 Java 8 runtime;
- configuration/secrets hierarchy;
- persistence durability semantics;
- exact public API/SPI boundaries;
- system-level IDD breakdown;
- later Java 11 migration criteria.

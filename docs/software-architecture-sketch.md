# Software architecture sketch

Status: working draft

This document is the first concrete architecture sketch for the waypoint timing/registration software. It is intentionally detailed enough to guide the first implementation increments, while still leaving unresolved choices explicit.

## Architecture decisions

A decision can be `proposed`, `accepted`, `superseded`, or `rejected`.

| ID | Status | Decision | Rationale / notes |
| --- | --- | --- | --- |
| ADR-001 | accepted | Use **Maven** as the Java build and dependency-management tool. | Maven is the preferred baseline because there is more existing project experience with it. |
| ADR-002 | accepted | Use **Java SE 8** as the initial language/API/runtime baseline for the headless waypoint runtime. | The original Raspberry Pi Zero / Zero W (ARMv6) is mandatory and the legacy application already uses Java 8. Start conservatively and gather evidence before increasing the baseline. |
| ADR-003 | proposed | Keep application code vendor-neutral at the Java SE level and pin an explicit ARMv6-capable reference runtime for Zero 1 deployment. | Deployment must be reproducible, but application code should not depend on vendor-specific JDK APIs. |
| ADR-004 | proposed | Evaluate **Java 11** as a later baseline upgrade after sufficient Zero 1 evidence exists. | Migration is desirable only when compatibility, footprint, performance, dependency support, maintenance, and deployment are proven on the mandatory target. |
| ADR-005 | proposed | Use **serialized application/domain execution** so mutable waypoint state has one logical writer; adapters own external I/O concurrency. | This avoids pervasive locking, makes ordering explicit, and keeps application/domain code straightforward to unit test. The exact executor topology for `1..X` logical waypoint systems remains open. |
| ADR-006 | proposed | Generate architecture diagrams from Python into both **SVG** and **draw.io** and publish generated documentation on `prod/docs`. | SVG keeps GitHub documentation directly readable; draw.io remains editable. One Python model prevents the two formats from drifting. No diagram-rendering Docker image is required initially. |

## Visual overview

After the documentation workflow has published `prod/docs`, the generated diagrams are available here:

- [Generated architecture documentation](../../../tree/prod/docs)
- [Editable system overview](../../../blob/prod/docs/architecture/system-overview.drawio)
- [Editable threading model](../../../blob/prod/docs/architecture/threading-model.drawio)

![Waypoint runtime component and interface overview](../../../raw/prod/docs/architecture/system-overview.svg)

The source model for these diagrams is `tools/generate_architecture_diagrams.py`.

## System boundary and clients

The core product is a **headless Java runtime**. User interfaces and external systems interact with it through defined interfaces rather than by calling internal runtime classes directly.

Current client/interface set:

1. **Local console** — interactive shell attached to the running process.
2. **Remote terminal/shell** — remotely reachable command-line interface using the same application command/query concepts.
3. **Machine-readable API** — HTTP/JSON-style queries and commands.
4. **Desktop GUI** — separate software item connecting through the public application interface.
5. **iPad/browser client** — React-based web application downloaded from the waypoint runtime itself.
6. **Backoffice system** — external system reached through a transport-independent backoffice boundary; RabbitMQ is the first intended adapter.
7. **Waypoint hardware** — RFID and CAN devices behind explicit device contracts.

The runtime should be able to host `1..X` logical waypoint systems in one process.

## Web / iPad interface

The iPad use case adds a browser-facing interface without adding a separate domain API.

The preferred direction is:

- the headless application serves the compiled React application as static files over simple HTTP;
- HTTP is used for initial state, queries, and operator commands;
- WebSocket is used for live status and registration updates;
- HTTP and WebSocket adapters translate to the same shared application command/query/event model used by other clients;
- the React application contains presentation logic, not waypoint domain rules.

Expected iPad/browser capabilities include:

- view registration data;
- view current status;
- open a logical waypoint system;
- close a logical waypoint system;
- initiate the local start procedure;
- later expose manual registration and penalty operations where authorised.

Authentication, authorisation, HTTPS, and deployment-network assumptions still need explicit requirements/design work. The first architecture only defines the separation and communication shape.

## Shared application boundary

The console, remote shell, API, GUI, and browser should not each implement business behaviour independently.

All command/query adapters should converge on a shared application boundary containing operations such as:

```text
version query
status query
open waypoint
close waypoint
start participant
manual registration
penalty registration
penalty revocation
```

The exact names and interfaces are illustrative. The important rule is that transport/presentation code translates input into application commands/queries and translates application results/events back to the client.

## Runtime and service structure

A first decomposition is:

```text
Bootstrap / composition
    |
    +-- interface adapters
    |     console
    |     remote shell
    |     HTTP + WebSocket
    |
    +-- runtime / orchestration
    |     application lifecycle
    |     logical waypoint manager (1..X)
    |
    +-- application/domain services
    |     status
    |     registration
    |     start procedure
    |     penalty handling
    |
    +-- ports / contracts
          registration storage
          RFID
          CAN
          backoffice
          clock
          settings
          platform capabilities
```

Concrete platform, hardware, persistence, and network implementations live below those contracts.

## Status as a first-class model

Status must have one central representation. Interfaces should display that model rather than each reconstructing status from logs or adapter-specific state.

Possible status levels include:

### Application status

- software version;
- startup time / uptime;
- overall health;
- configuration state;
- number of configured/running logical waypoint systems.

### Logical waypoint status

- identifier;
- lifecycle state such as `OPEN` / `CLOSED`;
- operational health;
- current start-procedure state;
- last meaningful activity/state transition.

### Subsystem status

- RFID;
- CAN;
- registration storage;
- backoffice connection;
- clock/time synchronisation;
- settings/configuration;
- public interface endpoints.

Status should be representable as immutable snapshots that can safely be consumed by console, API, WebSocket, GUI, diagnostics, and future monitoring integrations.

## Threading and concurrency model

The goal is to keep threading **out of the domain model** as much as possible.

![Threading and unit-testability model](../../../raw/prod/docs/architecture/threading-model.svg)

### External I/O

External libraries may create their own threads or callbacks, for example:

- HTTP/WebSocket server threads;
- remote-shell connections;
- RFID reader callbacks/threads;
- CAN receive thread;
- RabbitMQ consumer/connection threads.

Those threads must not directly mutate waypoint domain state.

At the adapter boundary they should instead:

1. capture externally meaningful timestamps immediately, especially RFID/CAN observations;
2. convert external input into immutable commands/events;
3. place the work on an application ingress queue/execution boundary.

This prevents queue/thread scheduling delay from changing the actual recorded observation time.

### Serialized domain execution

The current proposed model is **single-writer/serialized execution for mutable logical waypoint state**.

Benefits:

- deterministic ordering of registrations and operator commands;
- few or no locks inside domain services;
- less risk of partially updated state;
- simpler reasoning about `OPEN` / `CLOSED`, start procedures, penalties, and manual corrections;
- the same command handlers can be executed synchronously in unit tests.

The exact implementation remains open. Options include one runtime executor, one logical serialized executor per waypoint, or multiple logical serial executors multiplexed over a small thread pool. The Zero 1 memory/CPU constraint must be considered before choosing thread-per-waypoint designs.

### Blocking I/O

The serialized application/domain execution path must not be blocked for arbitrary periods by disk, network, or hardware access.

Blocking/slow operations should be owned by adapters or dedicated I/O executors. Completion/failure can return to the application as events so state transitions remain serialized.

Durability requirements for registrations may later require an explicit rule such as "registration becomes committed only after local persistence acknowledgement". That belongs in requirements and detailed persistence design rather than being guessed here.

## Unit-testability rules

Testability should be an architecture property rather than something added after implementation.

Application/domain code should therefore follow these rules where practical:

- do not create threads inside domain services;
- do not call `Thread.sleep()` in domain logic;
- do not use global/static mutable state;
- inject time through a `Clock`/clock port instead of directly reading system time throughout the code;
- inject storage, RFID, CAN, backoffice, and platform dependencies through contracts;
- keep commands/events/value objects immutable where practical;
- keep parsing/protocol logic in adapters, not in domain services;
- expose deterministic handlers that can be called synchronously in unit tests.

Typical unit tests can then use:

```text
FakeClock
InMemoryRegistrationStore
FakeRfidPort
FakeCanPort
FakeBackofficePort
```

Integration tests exercise real interface/server/persistence adapters separately.

This separation also makes Windows/Linux development possible without the real Pi/RFID/CAN hardware.

## Registration model direction

The registration store must eventually represent more than timing observations.

Candidate record/event categories include:

- RFID participant passage;
- participant start at the waypoint;
- manual registration;
- penalty-code registration;
- penalty-code revocation/correction;
- relevant operational/state transitions when required for audit/recovery.

A simple text/file-based implementation is the first persistence target, but higher-level code should depend on `RegistrationStore` rather than the file format.

A traceable append-oriented event model is worth investigating because revocations/corrections should not silently erase operational history. This is not yet an accepted requirement.

## Platform and device abstraction

Platform-level concerns and device-level concerns should be distinguishable.

Platform examples:

- clock;
- filesystem paths;
- process/service lifecycle;
- settings/secret sources;
- optional Raspberry Pi facilities.

Device examples:

- RFID reader/antenna;
- CAN interface.

Real and simulated adapters should implement the same relevant contracts. Unsupported facilities on Windows/development machines should therefore be representable without contaminating the application/domain layer with platform checks.

## Configuration and credentials

Credentials and environment-specific values must not be hard-coded.

The settings structure needs to cover at least:

- application settings;
- logical waypoint settings;
- interface/server configuration;
- device configuration;
- backoffice/RabbitMQ configuration;
- credentials/secrets through an external mechanism.

The source hierarchy (files, environment, secret files/stores, command-line overrides, etc.) remains open.

## Logging and diagnostics

A logging framework is required. Logs and status have different purposes:

- **logging** records what happened;
- **status** represents the current observable state.

Log context should make runtime, logical waypoint, subsystem/device/interface, and relevant operation identifiers visible where useful.

## Java/runtime direction

Java 8 is the accepted initial baseline. Java 11 is a later upgrade candidate and does not block the initial architecture or implementation.

The original Raspberry Pi Zero / Zero W is a mandatory ARMv6 target. The chosen Java 8 runtime must therefore be validated on actual hardware. Application code must remain vendor-neutral.

When Java 11 is evaluated, compare it with the working Java 8 application using evidence such as startup time, resident memory, heap behaviour, command/API responsiveness, dependency availability, maintenance/security updates, and deployment complexity.

## Generated documentation strategy

The source repository should remain easy to review while generated images remain easy to view.

The chosen initial pattern mirrors the CAD projects:

```text
source branch
  docs/*.md
  tools/generate_architecture_diagrams.py
            |
            | GitHub Actions
            v
prod/docs
  README.md
  architecture/
    system-overview.svg
    system-overview.drawio
    threading-model.svg
    threading-model.drawio
```

The Python generator uses only the standard library and produces both formats from the same node/edge/layout model.

Therefore no dedicated Docker image is required initially. A pinned documentation-toolchain container should only be introduced later if external renderers or fonts/tool versions become necessary for reproducible output.

## First architecture-validation increment

The first executable increment should validate the architecture rather than implement the complete event domain:

1. Maven-based headless Java 8 application;
2. central version model/service;
3. central status model/service;
4. local console interface;
5. remote terminal/shell interface;
6. HTTP/JSON interface;
7. basic WebSocket status/event path so the future browser client uses the same boundaries;
8. logging framework;
9. external settings structure;
10. unit tests around shared application behaviour;
11. GitHub Actions build/test;
12. execution on original Raspberry Pi Zero / Zero W with captured startup/memory/responsiveness evidence.

The React browser application itself can remain a subsequent software increment, but the server boundary should already anticipate it.

## Open architecture questions

- reference Java 8 runtime/version for Raspberry Pi Zero 1 deployment;
- evidence threshold and timing for a possible Java 11 migration;
- exact serialized executor topology for `1..X` logical waypoint systems;
- queue sizing/backpressure/overload behaviour;
- exact HTTP/API technology compatible with Java 8 and Zero 1;
- remote shell technology;
- desktop GUI technology;
- authentication/authorisation for browser/remote clients;
- status/health vocabulary;
- whether an internal event bus adds value beyond explicit application events;
- persistence commit/durability rules;
- text/file registration format and schema/versioning;
- RFID hardware contract;
- CAN library/platform support;
- backoffice message contracts, retry, buffering, and reconciliation;
- configuration/secret-loading hierarchy.

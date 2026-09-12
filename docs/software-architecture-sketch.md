# Software architecture sketch

Status: working draft

This document is an initial architecture sketch used to shape the software plan and early implementation increments. It is not yet the authoritative software architecture.

## Architecture decisions

This document also records architecture decisions as they become sufficiently concrete. A decision can be `proposed`, `accepted`, `superseded`, or `rejected`.

| ID | Status | Decision | Rationale / notes |
| --- | --- | --- | --- |
| ADR-001 | accepted | Use **Maven** as the Java build and dependency-management tool. | Maven is the preferred baseline because there is more existing project experience with it. Avoid introducing Gradle without a concrete need. |
| ADR-002 | proposed | Use **Java SE 21 LTS** as the language/API/runtime baseline. | Java 21 was released in September 2023 and is a mature LTS baseline with a substantially longer useful support horizon than Java 17 while avoiding adoption of the much newer Java 25 baseline immediately. The application should target the Java SE level rather than depend on one JDK vendor. |

### Java runtime portability note

The Java language/API baseline and the concrete JDK/runtime distribution are separate concerns.

The intended baseline is one Java SE level for application source and bytecode, while the runtime distribution can be selected per supported platform when necessary. Development and CI can standardise on one OpenJDK distribution for reproducibility without making that distribution part of the application architecture contract.

For Java 21, Eclipse Temurin is a suitable default candidate for normal Windows, Linux x86-64, and Linux AArch64 development/CI/runtime environments. Other Java SE 21-compatible OpenJDK distributions remain valid where platform support requires them.

This matters particularly for Raspberry Pi Zero-class hardware:

- original Raspberry Pi Zero / Zero W hardware uses the BCM2835 with a single-core ARM1176JZF-S (ARMv6-class) processor;
- Raspberry Pi Zero 2 W uses a quad-core 64-bit ARM Cortex-A53 (ARMv8) processor;
- current mainstream Java 21 distributions have good AArch64 support, making the Zero 2 W a much more natural target;
- Eclipse Temurin does not publish 32-bit ARM binaries for Java 21 and later;
- Azul documents that its Java 17+ 32-bit ARM builds do not support the original Raspberry Pi Zero 1;
- therefore selecting Java 17 instead of Java 21 does not provide a clean, vendor-neutral solution for original Raspberry Pi Zero / Zero W hardware;
- if original ARMv6 Zero hardware is a mandatory target, that needs a separate explicit runtime investigation and may require a special/older runtime strategy;
- if Raspberry Pi Zero 2 W or newer is the minimum Raspberry Pi target, Java 21 is the preferred current baseline.

The application architecture must not depend on vendor-specific JDK APIs unless explicitly justified.

ADR-002 remains `proposed` until the Java baseline and minimum Raspberry Pi target are explicitly accepted.

## Architectural goals

The current direction is a reusable Java-based waypoint runtime with the following characteristics:

- headless-first operation;
- support for Windows, Linux, and Raspberry Pi Zero-class targets;
- one runtime capable of hosting one to multiple logical waypoint systems;
- multiple external control/operator clients;
- explicit platform and device abstraction boundaries;
- good testability without requiring production hardware;
- clear status monitoring and status representation as a first-class architectural concern;
- generic/public framework parts separated cleanly from later product-specific/private implementations.

## Initial layered view

The embedded architecture reference collected in `reference/README.md` is useful as inspiration for explicit layering, service-style components, and platform abstraction. The Java design should adapt those ideas rather than copy the embedded implementation literally.

```text
External interfaces / clients
  - local console
  - remote terminal/shell
  - JSON/API interface
  - GUI client later
             |
             v
Application command/query boundary
  - version queries
  - status queries
  - operator commands
             |
             v
Runtime / orchestration
  - application lifecycle
  - waypoint-system manager (1..X)
  - status aggregation
             |
             v
Application and domain services
  - registration
  - waypoint open/closed lifecycle
  - start procedure
  - penalty-code handling
  - manual registration
  - backoffice communication
             |
             v
Ports / contracts
  - registration storage
  - RFID
  - CAN
  - backoffice transport
  - clock/time
  - settings/configuration
  - platform capabilities
             |
             v
Concrete adapters
  - text/file storage
  - RFID hardware or simulator
  - CAN implementation or simulator
  - RabbitMQ transport
  - Windows/Linux/Raspberry Pi platform adapters
```

The exact module boundaries, package structure, dependency-injection approach, and use of an internal event bus are still open.

## Shared command and query model

The local console, remote terminal connection, JSON/API interface, and future GUI should not each implement their own version of application behaviour.

The preferred direction is a shared application command/query boundary. Interface adapters translate their protocol or presentation model into the same application operations.

The first implementation can validate this architecture with two simple queries:

- application version;
- application/system status.

This gives the initial interfaces real architectural value without requiring the registration domain to be implemented immediately.

## Status as a first-class model

Status monitoring and representation should be designed centrally rather than reconstructed independently by each interface.

A possible status model includes:

### Application status

- software version;
- startup time / uptime;
- overall health/state;
- configuration loaded/not loaded;
- active logical waypoint-system count.

### Logical waypoint-system status

- waypoint-system identifier;
- lifecycle state, including at least `OPEN` and `CLOSED`;
- operational/health state;
- last meaningful activity or state transition;
- current start-procedure state when applicable.

### Subsystem status

Potential monitored subsystems include:

- RFID interface;
- CAN interface;
- registration storage;
- backoffice connection;
- clock/time synchronisation;
- configuration/settings;
- external interface endpoints.

A status item should be able to represent more than a boolean. A useful structure may include state, reason/detail, and last-change/observation time.

The same status representation should be consumable by the console, remote shell, API, future GUI, logging/diagnostics, and later monitoring integrations.

## Registration domain direction

The initial registration model must support more than RFID passage times.

Candidate registration/event categories include:

- participant passage detected through RFID;
- participant start at the waypoint;
- manual participant registration;
- penalty-code registration;
- penalty-code revocation/correction.

The exact domain model is not yet fixed. A unified append-oriented registration/event model may be useful because corrections and revocations should remain traceable rather than silently erasing operational history, but this needs explicit design work before becoming a requirement.

## Registration persistence

An early implementation should use a simple local text/file-based database or storage file for registrations.

It must eventually be capable of storing timing registrations as well as other operational registrations such as penalty codes and their revocations.

Still open:

- file format;
- schema/versioning;
- append-only versus update semantics;
- indexing/query strategy;
- crash/power-loss safety;
- file rotation/archival;
- concurrency model when multiple logical waypoint systems share a runtime.

The storage contract should be isolated from the application/domain logic so a later implementation can replace the first file-based store without changing higher-level services.

## Waypoint lifecycle and operations

The registration system needs explicit lifecycle/operational concepts.

Initial candidate behaviours:

- a waypoint system can be active/open;
- a waypoint system can be inactive/closed;
- a start procedure can register a participant starting locally at the waypoint;
- RFID passage registration is supported;
- manual registration is supported;
- penalty codes can be registered;
- penalty codes can later be revoked/corrected.

The exact commands, state transitions, validation rules, and audit semantics still need requirements work.

## Device and transport abstraction

RFID and CAN are distinct external interfaces and should be represented behind contracts rather than embedded directly in domain logic.

Possible ports include:

```text
RfidReaderPort
CanPort
RegistrationStore
BackofficePort
ClockPort
PlatformPort(s)
SettingsProvider
```

Names are illustrative only.

Real and simulated implementations should conform to the same contracts where practical so normal development and automated tests can run without waypoint hardware.

## Configuration and credentials

Credentials and environment-specific configuration must not be hard-coded in the application.

The architecture should provide a settings/configuration structure that can supply:

- normal application settings;
- per-waypoint settings;
- interface configuration;
- backoffice/RabbitMQ configuration;
- device configuration;
- credentials/secrets through an appropriate external mechanism.

The exact source hierarchy (configuration files, environment variables, secret files/stores, command-line overrides, etc.) remains to be selected.

## Logging and diagnostics

A logging framework is required as a cross-cutting infrastructure concern.

Logging should include enough structured context to distinguish:

- runtime/application;
- logical waypoint system;
- subsystem/device/interface;
- registration or operator operation where appropriate.

Logging is not a replacement for the status model. Logs describe events/history; status describes the current observable state.

## Backoffice boundary

RabbitMQ is one intended backoffice communication mechanism, but application/domain services should not depend directly on RabbitMQ-specific APIs.

A backoffice contract should allow a RabbitMQ adapter initially or later while preserving the option for other transports.

Offline buffering, retry, idempotency, message contracts, and reconciliation remain later design topics.

## First architecture-validation increment

Before implementing the registration domain, the architecture should be validated with the smallest useful executable:

1. start a headless Java application;
2. create a central version service/model;
3. create a central status service/model;
4. expose version (and preferably the same basic status) through:
   - local console;
   - remote terminal/shell connection;
   - JSON/API interface;
5. use a logging framework;
6. load settings through the configuration structure;
7. add unit tests around the shared application behaviour;
8. build and test through GitHub Actions.

This is intentionally small but exercises the boundaries that later registration, GUI, hardware, and backoffice functionality will use.

## Open architecture questions

- final acceptance of Java 21 LTS as the baseline;
- minimum Raspberry Pi Zero generation / CPU architecture that must be supported;
- standard development/CI JDK distribution and runtime distribution policy per platform;
- module/package boundaries;
- dependency injection or explicit composition approach;
- API protocol and server technology;
- remote shell/terminal technology;
- status state/health vocabulary;
- event bus versus direct service interaction;
- exact relationship between runtime-wide services and per-waypoint services;
- configuration and secret-loading approach;
- text/file registration format;
- CAN library/platform support;
- RFID hardware contract;
- GUI technology and repository/software-item boundary.

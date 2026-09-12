# Software architecture sketch

Status: working draft

This document is an initial architecture sketch used to shape the software plan and early implementation increments. It is not yet the authoritative software architecture.

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

- Java version/LTS baseline;
- Maven versus Gradle;
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

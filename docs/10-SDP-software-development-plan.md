# Software Development Plan (SDP)

Status: working draft / non-authoritative

This document describes the intended **phased evolution** of the software and related repositories. `docs/11-SIP-software-implementation-planning.md` is the more concrete step-by-step implementation plan.

The plan deliberately proves architectural and operational risks one at a time instead of building the complete timing system in one pass.

## Planning principles

- Build a small working vertical slice first and extend it in controlled phases.
- Keep the headless runtime independent from presentation clients.
- Keep platform/device/protocol specifics behind public contracts.
- Use Maven modules for compile-time/component boundaries and Java packages for cohesion inside a component.
- Keep registration history and ready-team operational state as separate domain capabilities.
- Make status, observability, traceability and testability first-class from the beginning.
- Use explicit constructor injection/composition before selecting a dependency-injection framework.
- Prove the public/private extension model before proprietary implementation grows large.
- Use automated unit tests and GitHub Actions from the first implementation repository.
- Prove the application on a development host before introducing target-image complexity.
- Automate Raspberry Pi image creation and application updates early so manual target preparation never becomes the normal workflow.
- Keep the mandatory original Raspberry Pi Zero target visible in every runtime/dependency choice.

See also:

- `docs/30-SSAD-software-system-architecture.md`;
- `docs/31-01-SAD-timing-application-architecture.md`;
- `docs/31-01-SDD-01-timing-system-design.md`;
- `docs/31-01-SDD-02-data-and-display-design.md`;
- `docs/31-01-SDD-03-java-component-design.md`;
- `docs/31-01-SDD-04-runtime-topology-and-configuration.md`;
- `docs/31-01-SDD-05-backoffice-transport-design.md`;
- `docs/50-SVP-software-verification-plan.md`.

## Intended repository chain

```text
meta repository
 requirements / architecture / IDDs / planning
               |
               v
public framework repository
 API + core + runtime + public adapters + testkit
               |
          +----+-------------------+
          |                        |
          v                        v
public reference/test app      private product/integration repo
stubs/default composition      proprietary adapters/protocols
integration scenarios          production composition
```

Illustrative names:

```text
2026-010-01.meta.event-timing-software
2026-010-02.java.event-timing-framework
2026-010-03.java.event-timing-reference
<private product/integration repository>
```

The exact names/repository split remain subject to an explicit repository-creation step.

## Phase 0 — Architecture and documentation baseline

Purpose: establish enough structure to start implementation without making foundational decisions ad hoc inside implementation pull requests.

Current scope includes:

- `TimingSystemInstance` as logical isolation boundary;
- `1..X` total-system instances per runtime;
- registration assets versus registration sources;
- serialized message/command processing;
- first-class status model;
- public platform/device ports;
- RFID lifecycle and processing pipeline;
- CAN/device discovery direction;
- network/status layers;
- registration ledger versus ready-team journal/state;
- in-memory active state with simple persistent backup/restore;
- display V1 versus V2 behaviour;
- Java/Maven module/package structure;
- transport-independent backoffice boundary;
- public/proprietary extension boundary;
- generated architecture diagrams and PR documentation branches;
- use cases and candidate requirements for later formal promotion;
- layered verification/system-test strategy.

This is the current phase.

## Phase 1 — Public framework skeleton

Purpose: create the first public Java framework repository and prove the build/dependency structure before adding domain complexity.

Initial Maven components are expected to resemble:

```text
timing-api
timing-core
timing-runtime
timing-adapters
timing-testkit
timing-app
```

Expected outcomes:

- Maven parent/reactor;
- Java 8 baseline;
- explicit artifact versions;
- module dependency direction;
- unit-test framework;
- logging framework;
- configuration/settings boundary;
- GitHub Actions build/test;
- clean startup/shutdown of a headless executable;
- architecture/dependency checks where useful.

No production RFID/CAN/backoffice protocol implementation belongs here yet.

## Phase 2 — Minimal version/status application on development host

Purpose: validate the application architecture with the smallest useful executable before target deployment is introduced.

The first concrete runtime environment is the normal development host, primarily Windows.

The headless application exposes one central version/status model through:

1. local console/shell;
2. remote terminal/shell;
3. HTTP/JSON API;
4. minimal WebSocket event/status stream.

This phase also proves:

- command/query adapters converge on one application boundary;
- a minimal `TimingSystemInstance` can be created and addressed;
- status is centrally represented;
- application/domain handlers remain independent from transport threads;
- serialized execution can use a direct executor in unit tests;
- `ST-1 Application Behaviour` can drive a real running process through public interfaces;
- the same application logic is not tied to Raspberry Pi-specific classes.

The purpose is to obtain a known-working executable **before** adding OS-image/runtime/service automation.

## Phase 3 — Raspberry Pi Zero image and update automation

Purpose: prove the mandatory target early using reproducible automation rather than a hand-prepared Raspberry Pi.

This phase establishes two distinct deployment paths.

### Full target image

Automatically produce a complete flashable image containing at least:

- a pinned supported Raspberry Pi OS/base image;
- a pinned ARMv6-capable Java 8 runtime;
- the SI-01 application artifact;
- service/startup definition;
- safe default/public configuration;
- build/provenance information.

Secrets and real/proprietary deployment mappings must not be embedded in public image recipes or generic image artifacts.

The exact image-generation technology is selected during implementation. Reproducibility is the requirement; no particular builder is assumed by this plan.

### Normal application update

Ordinary SI-01 development should not require a complete SD-card reflash.

Introduce an automated/versioned application-update path that can replace the application artifact on an already provisioned Pi, restart the service, preserve persistent data/configuration where required and provide an initial rollback/recovery direction.

Full image rebuilds remain appropriate when OS, Java runtime or image-level inputs change.

### Target evidence

Boot the generated image on a real original Raspberry Pi Zero / Zero W and establish the first repeatable target baseline including startup, RSS/heap, CPU, thread count and API/status responsiveness.

This target pipeline becomes the basis for later hardware and operational phases rather than being postponed until the end of the project.

## Phase 4 — First GUI client

Purpose: prove that a separate software item can use the public system interface without depending on runtime internals.

Initial scope is deliberately small:

- connect/disconnect;
- read/display application version;
- display application/timing-system/subsystem status;
- represent stale/disconnected state clearly;
- connect both to a local development SI-01 instance and the Raspberry Pi image from Phase 3.

This is the first practical validation of the API/IDD from a second software item.

The browser/iPad React application may later use the same HTTP/WebSocket boundary, but the first GUI proof does not need the complete registration domain.

## Phase 5 — External reference/test application

Purpose: prove the public framework works **outside its own Maven reactor** and establish a reusable application/template project.

Create a separate public repository that consumes framework artifacts just like a real product would.

It should:

- build against versioned/snapshot public Maven artifacts;
- compose a complete runnable headless application;
- use stub/default hardware and communication adapters;
- exercise console/remote/API/WebSocket interfaces;
- include deterministic `ST-1` scenarios;
- provide the lightweight `ST-2 Socket Loop` backoffice transport/simulator;
- support multiple synthetic system instances/assets/sources;
- use `timing-testkit` where appropriate;
- document external consumer setup;
- form the public template/reference for complete applications.

This phase is intentionally early so reactor-only shortcuts and accidental internal coupling are discovered before domain complexity grows.

## Phase 6 — Proprietary extension proof

Purpose: prove that private components can replace public stubs through the same contracts without modifying/forking framework source.

A small private integration/product repository should implement at least one real extension point.

Good candidates include:

- production RFID antenna control;
- RFID protocol/decryption implementation;
- product-specific backoffice protocol implementation.

The public reference application and private application must use the same public API/SPI boundaries.

Private implementation artifacts may be consumed from a private Maven package/repository or another secure build mechanism; that delivery mechanism remains a development/tooling decision.

## Phase 7 — Timing-system state and traceability foundation

Purpose: introduce the local domain/state model without real production hardware.

Implement in-memory structures and deterministic handlers for at least:

### Registration capability

- registration assets and registration sources;
- traceable per-source registration ledger;
- monotonically increasing sequence per registration source;
- passage/start/manual/penalty/revocation records;
- corrections/revocations referencing previous records rather than overwriting history;
- local derived registration/result views.

### Ready-team capability

- separate ready-team event journal;
- add/remove team actions;
- current ready-team state derived from journal/events;
- current list available to display logic.

### Reference data

- locally cached start times;
- reserve-tag conversion data;
- version/synchronisation metadata.

### Persistence

- in-memory repositories as the runtime API;
- simple file backup/restore;
- restoration of per-source sequence state;
- explicit backup/restore status.

All of this should be testable with no physical devices.

## Phase 8 — Browser/iPad operator application

Purpose: create the operational web client once meaningful timing-system state exists.

The headless application serves the compiled React application over HTTP. The browser uses HTTP for commands/queries and WebSocket for live updates.

Candidate operations:

- show registrations;
- show current status;
- open/close a timing-system instance;
- initiate local start procedure;
- inspect/manage ready-team state;
- later perform manual registration and penalty operations where authorised.

Business rules remain in the headless application.

## Phase 9 — Stub-controlled hardware integration

Purpose: prove complete hardware-facing flows before connecting proprietary/production implementations.

Use public/testkit stubs for:

- RFID reader and power/lifecycle;
- encrypted/raw RFID observation injection;
- CAN bus;
- keypad add/remove actions;
- discoverable V1 display;
- smart V2 display session;
- network/internet/backoffice availability.

A test-control interface manipulates the stubs but must still drive normal application paths.

This phase provides deterministic integration and failure/recovery tests.

## Phase 10 — Production RFID/CAN/display integration

Purpose: substitute real adapters for the proven public contracts.

Likely work:

- private RFID antenna/power/protocol adapter;
- RFID decryption implementation;
- real filtering/tuning with device data;
- production CAN adapter;
- keypad protocol adapter;
- V1 CAN display adapter;
- V2 mDNS/network data session;
- heartbeat/device-health monitoring;
- platform-specific Raspberry Pi integration.

The core domain should require minimal or no change when replacing stubs with production adapters.

## Phase 11 — Backoffice/reference-data integration

Purpose: connect the local system to the real backoffice while retaining autonomous local operation.

Scope includes:

- system-level IDD;
- transport-independent backoffice semantic boundary;
- RabbitMQ transport adapter;
- per-source inbound and outbound routing configuration;
- start-time synchronisation;
- reserve-tag conversion synchronisation;
- registration/outbox delivery;
- retry/reconnect/offline behaviour;
- idempotency/reconciliation;
- multi-level network/backoffice status;
- `ST-3` integration against a disposable RabbitMQ service.

## Phase 12 — Deployment hardening and operational maturity

Purpose: harden the early Phase-3 image/update pipeline once the application is representative and make target operation supportable.

Expected work:

- review/harden reproducible Raspberry Pi image generation;
- service startup/restart/watchdog policy;
- secure configuration/secret provisioning;
- versioned application-update and artifact-retention policy;
- rollback/recovery after failed updates;
- OS/runtime/image-update policy;
- support/diagnostic exports;
- longer-running integration tests;
- `ST-4` target/full-system and hardware-in-the-loop tests;
- measured Raspberry Pi Zero resource budgets promoted to acceptance limits where useful.

This phase should **refine** the early deployment automation, not introduce target automation for the first time.

## Java 11 upgrade checkpoint

Java 8 remains the implementation baseline until explicit evidence supports changing it.

Once the application is representative enough, compare Java 11 on the same Raspberry Pi Zero hardware/workload for:

- runtime availability/deployment complexity;
- startup time;
- memory use;
- responsiveness;
- required library compatibility;
- maintenance/security support.

A Java 11 move is an explicit architecture decision, not an automatic phase transition.

## Documentation evolution

As phases mature, brainstorm/use-case/candidate material should be promoted into the correct authoritative document families:

```text
20-29  software/system requirements
30-39  architecture and detailed design
40-49  system-level IDDs
50-59  verification planning/evidence structure
```

The IDD remains system-level. A software-item requirement may reference the applicable IDD requirement/interface identifier.

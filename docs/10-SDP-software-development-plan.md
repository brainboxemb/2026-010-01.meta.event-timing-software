# Software Development Plan (SDP)

Status: working draft / non-authoritative

This document describes the intended **phased evolution** of the software and related repositories. `docs/11-software-implementation-roadmap.md` is the more concrete step-by-step roadmap.

The plan deliberately proves architectural risks one at a time instead of building the complete timing system in one pass.

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
- Keep the mandatory original Raspberry Pi Zero target visible in every runtime/dependency choice.

See also:

- `docs/30-SSAD-software-system-architecture.md`;
- `docs/31-SAD-timing-system-architecture.md`;
- `docs/32-SDD-data-and-display-design.md`;
- `docs/33-SDD-java-component-structure.md`.

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

- `TimingSystem` as logical isolation boundary;
- `1..X` timing systems per runtime;
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
- public/proprietary extension boundary;
- generated architecture diagrams and PR documentation branches;
- candidate requirements for later formal promotion.

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

## Phase 2 — Minimal version/status application

Purpose: validate the architecture with the smallest useful executable.

The headless application exposes one central version/status model through:

1. local console/shell;
2. remote terminal/shell;
3. HTTP/JSON API;
4. minimal WebSocket event/status stream.

This phase also proves:

- command/query adapters converge on one application boundary;
- a minimal `TimingSystem` instance can be created and addressed;
- status is centrally represented;
- application/domain handlers remain independent from transport threads;
- serialized execution can use a direct executor in unit tests;
- Windows and Linux execution;
- actual execution on original Raspberry Pi Zero hardware with memory/startup/responsiveness evidence.

## Phase 3 — First GUI client

Purpose: prove that a separate software item can use the public system interface without depending on runtime internals.

Initial scope is deliberately small:

- connect/disconnect;
- read/display application version;
- display application/timing-system/subsystem status;
- represent stale/disconnected state clearly.

This is the first practical validation of the API/IDD from a second software item.

The browser/iPad React application may later use the same HTTP/WebSocket boundary, but the first GUI proof does not need the complete registration domain.

## Phase 4 — External reference/test application

Purpose: prove the public framework works **outside its own Maven reactor** and establish a reusable application/template project.

Create a separate public repository that consumes framework artifacts just like a real product would.

It should:

- build against versioned/snapshot public Maven artifacts;
- compose a complete runnable headless application;
- use stub/default hardware and communication adapters;
- exercise console/remote/API/WebSocket interfaces;
- include deterministic integration scenarios;
- use `timing-testkit` where appropriate;
- document external consumer setup;
- form the public template/reference for complete applications.

This phase is intentionally early so reactor-only shortcuts and accidental internal coupling are discovered before domain complexity grows.

## Phase 5 — Proprietary extension proof

Purpose: prove that private components can replace public stubs through the same contracts without modifying/forking framework source.

A small private integration/product repository should implement at least one real extension point.

Good candidates include:

- production RFID antenna control;
- RFID protocol/decryption implementation;
- product-specific backoffice protocol implementation.

The proof should look conceptually like:

```text
            public timing-api
               ^          ^
               |          |
      public stub      private implementation
               \          /
                \        /
              composition root
```

The public reference application and private application must use the same public API/SPI boundaries.

Private implementation artifacts may be consumed from a private Maven package/repository or another secure build mechanism; that delivery mechanism is a later development/tooling decision.

## Phase 6 — TimingSystem state and traceability foundation

Purpose: introduce the local domain/state model without real production hardware.

Implement in-memory structures and deterministic handlers for at least:

### Registration capability

- traceable registration ledger;
- unique monotonically increasing registration sequence numbers within the selected scope;
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
- restoration of sequence state;
- explicit backup/restore status.

All of this should be testable with no physical devices.

## Phase 7 — Browser/iPad operator application

Purpose: create the operational web client once meaningful timing-system state exists.

The headless application serves the compiled React application over HTTP. The browser uses HTTP for commands/queries and WebSocket for live updates.

Candidate operations:

- show registrations;
- show current status;
- open/close a timing system;
- initiate local start procedure;
- inspect/manage ready-team state;
- later perform manual registration and penalty operations where authorised.

Business rules remain in the headless application.

## Phase 8 — Stub-controlled hardware integration

Purpose: prove complete hardware-facing flows before connecting proprietary/production implementations.

Use public/testkit stubs for:

- RFID reader and power/lifecycle;
- encrypted/raw RFID observation injection;
- CAN bus;
- keypad add/remove actions;
- discoverable V1 display;
- smart V2 display session;
- network/internet/RabbitMQ availability.

A test-control interface manipulates the stubs but must still drive normal application paths.

This phase provides deterministic integration and failure/recovery tests.

## Phase 9 — Production RFID/CAN/display integration

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

## Phase 10 — Backoffice/reference-data integration

Purpose: connect the local system to the real backoffice while retaining autonomous local operation.

Scope includes:

- system-level IDD;
- RabbitMQ transport adapter;
- start-time synchronisation;
- reserve-tag conversion synchronisation;
- registration/outbox delivery;
- retry/reconnect/offline behaviour;
- idempotency/reconciliation;
- multi-level network/backoffice status;
- integration-test pipeline.

## Phase 11 — Deployment and operational maturity

Purpose: make the software reproducibly deployable and supportable on target systems.

Expected work:

- automated Raspberry Pi deployment;
- service startup/restart;
- Java runtime provisioning;
- configuration/secret provisioning;
- update/rollback;
- support/diagnostic exports;
- longer-running integration tests;
- hardware-in-the-loop tests;
- measured Raspberry Pi Zero resource budgets.

## Java 11 upgrade checkpoint

Java 8 remains the implementation baseline until explicit evidence supports changing it.

Once the application is representative enough, compare Java 11 on the same Raspberry Pi Zero hardware for:

- runtime availability/deployment complexity;
- startup time;
- memory use;
- responsiveness;
- required library compatibility;
- maintenance/security support.

A Java 11 move is an explicit architecture decision, not an automatic phase transition.

## Documentation evolution

As phases mature, brainstorm/candidate material should be promoted into the correct authoritative document families:

```text
20-29  software/system requirements
30-39  architecture and detailed design
40-49  system-level IDDs
50-59  verification planning/evidence structure
```

The IDD remains system-level. A software-item requirement may reference the applicable IDD requirement/interface identifier.

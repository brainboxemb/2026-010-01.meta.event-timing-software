# Software Implementation Planning (SIP)

Status: working draft / non-authoritative

This document is the concrete software implementation sequence derived from `docs/10-SDP-software-development-plan.md`.

The SDP defines the higher-level development approach and phased evolution. This SIP turns that direction into ordered implementation steps, scope and exit criteria.

Detailed implementation decisions, tests and evidence for an active step belong in that step's pull request.

Software-item identifiers are stable across the document set:

```text
SI-01  Headless Timing Application
SI-02  Desktop GUI Application
SI-03  Web Operator Application
```

## Step 1 — Architecture baseline

Status: in progress

Goal: define enough software-system/component architecture to start the framework repository deliberately.

Current outputs include:

- `docs/30-SSAD-software-system-architecture.md`;
- `docs/31-01-SAD-timing-application-architecture.md`;
- `docs/31-01-SDD-01-timing-system-design.md`;
- `docs/31-01-SDD-02-data-and-display-design.md`;
- `docs/31-01-SDD-03-java-component-design.md`;
- `docs/31-02-SAD-gui-application-architecture.md`;
- `docs/31-03-SAD-web-operator-application-architecture.md`;
- `docs/50-SVP-software-verification-plan.md`;
- software-item register and system interface catalogue;
- generated architecture/state-model diagrams on `dev/pr-<N>/docs`;
- Maven as accepted build tooling;
- Java 8 as accepted initial baseline for the mandatory original Raspberry Pi Zero target;
- Java 11 as a later evidence-driven upgrade candidate;
- `TimingSystem` as logical isolation boundary;
- serialized execution/threading direction;
- first-class status model;
- fault/recovery architecture direction;
- Pi Zero resource-baseline strategy;
- platform/device ports;
- public/private extension strategy;
- registration and ready-team traceability as separate capabilities;
- in-memory active state with simple file backup/restore.

Exit criteria:

- SI-01, SI-02 and SI-03 responsibilities are understandable;
- principal system interfaces are catalogued and future IDD ownership is clear;
- system, runtime, core, adapter and client responsibilities are understandable;
- Maven module/package direction is clear enough to create the framework skeleton;
- registration versus ready-team ownership is explicit;
- status/lifecycle/fault concepts are separated cleanly;
- public contracts can support stubs and private implementations;
- a verification strategy exists before implementation begins;
- unresolved decisions remain visible rather than being silently assumed;
- generated diagrams and documentation are reviewable in GitHub.

## Step 2 — Framework repository skeleton

Status: not started

Goal: create the public framework repository and establish build/dependency/test foundations for SI-01/framework development.

Candidate scope:

- Maven reactor;
- Java 8 compiler/runtime baseline;
- initial modules: `timing-api`, `timing-core`, `timing-runtime`, `timing-adapters`, `timing-testkit`, `timing-app`;
- version-source strategy;
- logging framework;
- unit-test framework;
- initial settings/configuration structure;
- GitHub Actions build/test;
- architecture/dependency checks where useful;
- minimal headless startup/shutdown;
- repository baseline from the SDE (`README.md`, `AGENTS.md`, `CHANGELOG.md`);
- PR/generated-output conventions where applicable.

No production device/backoffice protocols yet.

## Step 3 — Minimal version/status application (SI-01)

Status: not started

Goal: prove the public runtime/application boundary with deliberately small behaviour and establish the first Pi Zero resource baseline.

Required behaviour:

- one central version source;
- central application/status model;
- version/status readable through:
  1. local console/shell;
  2. remote terminal/shell;
  3. HTTP/JSON API;
- minimal WebSocket status/event stream;
- minimal configurable `TimingSystem` instance;
- transport adapters do not own application state;
- application handlers can run synchronously in unit tests;
- logging and externalised settings are active;
- GitHub Actions verifies fast tests;
- Windows/Linux execution;
- real Raspberry Pi Zero 1 execution.

Pi Zero evidence should establish the first measured baseline for startup time, RSS/heap behaviour, CPU, thread count and version/status responsiveness as defined by the SVP.

This step should also prove that lifecycle/status architecture is not coupled to one client transport.

## Step 4 — First Desktop GUI client (SI-02)

Status: not started

Goal: prove a separate software item can consume the system-defined application control/status interface, including when SI-01 runs on a different host such as a Raspberry Pi.

Initial scope:

- connect/disconnect;
- configure/select SI-01 endpoint;
- display application version;
- display application, timing-system and subsystem status;
- show disconnected/stale state;
- no direct dependency on internal SI-01 runtime classes or filesystem;
- verify local development connection and remote Pi connection.

This step is deliberately early because it validates the network/interface boundary before the domain becomes large.

## Step 5 — External reference/test project

Status: not started

Goal: create a separate public consumer/template project that builds against framework Maven artifacts.

Candidate scope:

- complete runnable composition using public/stub adapters;
- deterministic integration scenarios;
- use of `timing-testkit`;
- console/remote/API/WebSocket system tests;
- fault injection through stubs/test-control;
- documentation proving external consumer setup;
- CI that builds without relying on framework-reactor internals.

The reference project should become the normal public proof that extension contracts are actually consumable.

## Step 6 — Proprietary extension proof

Status: not started

Goal: prove one private implementation can replace a public stub through the same API/SPI contract.

Preferred early candidate:

- production RFID antenna adapter shell and/or proprietary tag protocol/decryption component.

Evidence should show:

- public framework source remains unchanged;
- reference and private applications use the same public contract;
- private Maven/dependency consumption works through the chosen secure mechanism;
- private code is not required to compile/test the public framework;
- public verification can remain meaningful without exposing proprietary protocol details.

## Step 7 — TimingSystem data/state foundation (SI-01)

Status: not started

Goal: implement deterministic local domain behaviour without production hardware.

### Registration

- registration ledger;
- unique monotonically increasing sequence number within the selected scope;
- passage, start, manual, penalty and revocation records;
- traceable correction/revocation relationships;
- local derived result/ranking views.

### Ready-team

- separate ready-team event journal;
- add/remove actions;
- current ready-team state projection;
- current ordered list for display logic;
- traceable persisted history.

### Reference data

- start-time repository;
- reserve-tag conversion repository;
- synchronisation/version metadata.

### Persistence

- in-memory repositories as application API;
- simple file backup/restore;
- sequence-state recovery;
- explicit backup/restore status;
- fault-injection tests for failed/corrupt backup/restore paths.

### State/recovery

- explicit `OPEN`/`CLOSED` lifecycle independent from subsystem health;
- RFID lifecycle/recovery model available to the domain/status layer;
- explicit stale/degraded/error status where relevant;
- bounded queue/backpressure behaviour designed and verified before representative load testing.

Promote mature candidate requirements before implementation.

## Step 8 — Web/iPad operator application (SI-03)

Status: not started

Goal: provide the React-based operational client over the existing HTTP/WebSocket system interface.

Candidate scope:

- SI-01 serves the compiled React bundle;
- show registrations/status;
- open/close timing system;
- start procedure control;
- show/manage ready-team state;
- later manual registrations/penalties where authorised;
- clear stale/disconnected representation;
- reconnect obtains a complete current state before normal live updates continue;
- verify representative iPad/Safari use;
- local browser operation does not require live internet/backoffice when SI-01 remains locally reachable.

Business rules remain server-side in SI-01.

## Step 9 — Stub-controlled hardware integration

Status: not started

Goal: exercise complete device and recovery flows deterministically before production adapters are integrated.

Stub/test-control scope may include:

- RFID power/lifecycle and raw reads;
- RFID health/heartbeat;
- RFID boot/reinitialise/error paths;
- CAN bus and discovery;
- keypad team add/remove;
- V1 display discovery/control/reconnect;
- V2 display connection/data synchronisation/reconnect;
- local network/internet/RabbitMQ failures and recovery;
- queue pressure scenarios.

Injected events must follow the same normal application paths as real adapters.

## Step 10 — Production RFID/CAN/display integration

Status: not started

Goal: replace proven stubs with real implementations.

Candidate scope:

- private RFID antenna/control adapter;
- proprietary RFID decrypt/protocol implementation;
- RFID filtering/tuning;
- production CAN adapter;
- periodic device scanner;
- keypad protocol;
- V1 passive CAN display driver;
- V2 mDNS/network data interface;
- status/heartbeat/recovery behaviour;
- hardware-in-the-loop verification from the SVP.

## Step 11 — Backoffice/reference-data integration

Status: not started

Goal: connect local operation to the real backoffice while retaining offline capability.

Candidate scope:

- system-level IDD(s);
- RabbitMQ adapter;
- start-time synchronisation;
- reserve-tag mapping synchronisation;
- registration outbox/delivery;
- retry/reconnect/idempotency/reconciliation;
- network/link/internet/broker status;
- slower integration-test pipeline;
- fault/recovery verification with network/internet/broker failures separated.

## Step 12 — Deployment and operationalisation

Status: not started

Goal: make target deployment reproducible and supportable.

Candidate scope:

- automated Raspberry Pi deployment;
- Java runtime provisioning;
- service startup/restart;
- configuration and secret provisioning;
- update/rollback;
- diagnostic/support export;
- long-running integration and hardware-in-the-loop tests;
- resource budgets promoted from measured baselines where evidence supports useful limits.

## Java 11 checkpoint

Status: future / evidence-driven

Do not block early development on Java 11.

When the application is representative enough, compare Java 11 with the working Java 8 baseline on the same Pi Zero hardware/workload for runtime availability, deployment, startup, memory, threads, CPU, responsiveness, library compatibility and maintenance support.

Only an explicit architecture decision may supersede the Java 8 baseline.

## Planning rules

- Do not start a later software step merely because an abstraction already exists.
- Keep fast unit/build checks suitable for normal pull requests.
- Separate longer integration/hardware/deployment pipelines when needed.
- Keep system-level IDDs authoritative for interfaces; software-item SRDs reference them where applicable.
- Keep implementation/evidence details in the active implementation PR.
- Keep registration and ready-team models distinct unless an explicit later requirement defines an interaction.
- Prefer public contracts plus composition over subclass-based/private-source coupling.
- Measure Pi Zero resource behaviour from the first executable and avoid invented numeric budgets without evidence.
- Keep lifecycle state, subsystem health and connectivity status separate concepts.

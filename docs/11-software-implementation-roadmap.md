# Software implementation roadmap

Status: working draft / non-authoritative

This document is the concrete software implementation sequence derived from `docs/10-SDP-software-development-plan.md`.

Detailed implementation decisions, tests and evidence for an active step belong in that step's pull request.

## Step 1 — Architecture baseline

Status: in progress

Goal: define enough software-system/component architecture to start the framework repository deliberately.

Current outputs include:

- `docs/30-SSAD-software-system-architecture.md`;
- `docs/31-SAD-timing-system-architecture.md`;
- `docs/32-SDD-data-and-display-design.md`;
- `docs/33-SDD-java-component-structure.md`;
- generated architecture diagrams on `dev/pr-<N>/docs`;
- Maven as accepted build tooling;
- Java 8 as accepted initial baseline for the mandatory original Raspberry Pi Zero target;
- Java 11 as a later evidence-driven upgrade candidate;
- `TimingSystem` as logical isolation boundary;
- serialized execution/threading direction;
- first-class status model;
- platform/device ports;
- public/private extension strategy;
- registration and ready-team traceability as separate capabilities;
- in-memory active state with simple file backup/restore.

Exit criteria:

- system, runtime, core, adapter and client responsibilities are understandable;
- Maven module/package direction is clear enough to create the framework skeleton;
- registration versus ready-team ownership is explicit;
- public contracts can support stubs and private implementations;
- unresolved decisions remain visible rather than being silently assumed;
- generated diagrams and documentation are reviewable in GitHub.

## Step 2 — Framework repository skeleton

Status: not started

Goal: create the public framework repository and establish build/dependency/test foundations.

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
- minimal headless startup/shutdown.

No production device/backoffice protocols yet.

## Step 3 — Minimal version/status application

Status: not started

Goal: prove the public runtime/application boundary with deliberately small behaviour.

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
- real Raspberry Pi Zero 1 execution with startup/memory/responsiveness evidence.

## Step 4 — First GUI client

Status: not started

Goal: prove a separate software item can consume the public interface/IDD.

Initial scope:

- connect/disconnect;
- display application version;
- display application, timing-system and subsystem status;
- show disconnected/stale state;
- no direct dependency on internal runtime classes.

## Step 5 — External reference/test project

Status: not started

Goal: create a separate public consumer/template project that builds against framework Maven artifacts.

Candidate scope:

- complete runnable composition using public/stub adapters;
- deterministic integration scenarios;
- use of `timing-testkit`;
- console/remote/API/WebSocket system tests;
- documentation proving external consumer setup;
- CI that builds without relying on framework-reactor internals.

## Step 6 — Proprietary extension proof

Status: not started

Goal: prove one private implementation can replace a public stub through the same API/SPI contract.

Preferred early candidate:

- production RFID antenna adapter shell and/or proprietary tag protocol/decryption component.

Evidence should show:

- public framework source remains unchanged;
- reference and private applications use the same public contract;
- private Maven/dependency consumption works through the chosen secure mechanism;
- private code is not required to compile/test the public framework.

## Step 7 — TimingSystem data/state foundation

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
- explicit backup/restore status.

Promote mature candidate requirements before implementation.

## Step 8 — Browser/iPad operator application

Status: not started

Goal: provide the React-based operational client over the existing HTTP/WebSocket system interface.

Candidate scope:

- application serves the compiled React bundle;
- show registrations/status;
- open/close timing system;
- start procedure control;
- show/manage ready-team state;
- later manual registrations/penalties where authorised;
- clear stale/disconnected representation.

Business rules remain server-side.

## Step 9 — Stub-controlled hardware integration

Status: not started

Goal: exercise complete device flows deterministically before production adapters are integrated.

Stub/test-control scope may include:

- RFID power/lifecycle and raw reads;
- RFID health/heartbeat;
- CAN bus and discovery;
- keypad team add/remove;
- V1 display discovery/control;
- V2 display connection/data synchronisation;
- network/internet/RabbitMQ failures and recovery.

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
- status/heartbeat/recovery behaviour.

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
- slower integration-test pipeline.

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
- measured resource budgets.

## Java 11 checkpoint

Status: future / evidence-driven

Do not block early development on Java 11.

When the application is representative enough, compare Java 11 with the working Java 8 baseline on the same Pi Zero hardware for runtime availability, deployment, startup, memory, responsiveness, library compatibility and maintenance support.

Only an explicit architecture decision may supersede the Java 8 baseline.

## Planning rules

- Do not start a later software step merely because an abstraction already exists.
- Keep fast unit/build checks suitable for normal pull requests.
- Separate longer integration/hardware/deployment pipelines when needed.
- Keep system-level IDDs authoritative for interfaces; software-item requirements may reference them.
- Keep implementation/evidence details in the active implementation PR.
- Keep registration and ready-team models distinct unless an explicit later requirement defines an interaction.
- Prefer public contracts plus composition over subclass-based/private-source coupling.

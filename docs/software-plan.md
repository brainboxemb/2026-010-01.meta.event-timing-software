# Software plan

Status: working draft

This document describes the intended staged evolution of the software. It is deliberately higher-level than `docs/software-planning.md`, which tracks the current concrete sequence of software increments.

## Planning principles

- Build the architecture incrementally instead of attempting the full waypoint system at once.
- Every early increment should exercise architectural boundaries that will still matter later.
- Keep the headless core independent from presentation clients.
- Keep platform/device specifics behind contracts.
- Make status and observability first-class from the beginning.
- Use automated tests and GitHub Actions from the first implementation repository.
- Keep credentials and environment-specific values outside application source code.
- Prefer replaceable adapters so the first simple implementation does not become a permanent architectural constraint.

## Increment 1 — Architecture baseline

Purpose: establish the first explicit Java architecture before implementation starts.

Outputs should include:

- runtime/application boundary;
- service/orchestration direction;
- platform and device abstraction direction;
- shared command/query boundary;
- first-class status model;
- configuration/settings boundary;
- logging approach direction;
- interface boundaries for local console, remote terminal, and API;
- initial testing/CI expectations.

The first draft is maintained in `docs/software-architecture-sketch.md`.

## Increment 2 — Minimal headless application

Purpose: validate the architecture with the smallest useful executable.

The application should:

- start as a headless Java application;
- have an explicit software version;
- make the version available through one shared application query/service;
- expose the version through three adapters:
  1. local console/shell;
  2. remote terminal/shell connection;
  3. machine-readable API, initially expected to use JSON;
- expose a basic central application/status representation so the status architecture is exercised immediately;
- use a real logging framework;
- use a settings/configuration structure instead of hard-coded environment values or credentials;
- include unit tests;
- build and test through GitHub Actions;
- remain compatible with the intended Windows, Linux, and Raspberry Pi Zero-class targets.

This increment should avoid registration-domain complexity. Its purpose is to prove packaging, boundaries, interfaces, status representation, logging, configuration, tests, and CI.

## Increment 3 — GUI/operator client

Purpose: prove that a separate user-facing software item can use the same application boundary as the non-GUI interfaces.

The GUI should initially remain deliberately small. A useful first scope is:

- connect to the running headless application through a defined system interface;
- display application version;
- display application and subsystem status;
- clearly represent connectivity loss or unavailable status;
- avoid direct dependency on internal runtime implementation classes.

This increment should help validate whether the API/IDD and status model are suitable for multiple clients.

## Increment 4 — Registration core

Purpose: introduce the waypoint registration domain while keeping hardware dependencies abstracted.

Initial domain capabilities to design and implement include:

- waypoint lifecycle: open/active and closed/inactive;
- participant passage registration via RFID abstraction;
- local start procedure;
- manual participant registration;
- penalty-code registration;
- penalty-code revocation/correction;
- simple local text/file-based registration storage;
- traceable status of registration/storage services.

The storage model must support both time registrations and other registration types.

## Increment 5 — Hardware and local interfaces

Purpose: connect the registration core to real/simulated external interfaces.

Likely scope:

- RFID adapter(s);
- CAN interface/adapter;
- simulated implementations for development and integration tests;
- platform-specific capabilities needed on the Raspberry Pi target;
- subsystem health/status integration.

## Increment 6 — Backoffice communication

Purpose: connect waypoint systems to a backoffice without coupling the registration domain to one transport.

RabbitMQ is an intended transport candidate.

Later work should cover:

- message/interface definition through system-level IDD documentation;
- connection status;
- retry/reconnect;
- offline buffering;
- acknowledgement and idempotency;
- reconciliation after connectivity loss;
- integration tests.

## Increment 7 — Target deployment and operational maturity

Purpose: make the software reliably deployable and operable on target systems.

Expected topics include:

- automated Raspberry Pi deployment;
- service startup/restart behaviour;
- package/runtime distribution;
- configuration/credential provisioning;
- update and rollback strategy;
- longer-running integration tests;
- hardware-in-the-loop tests where useful;
- operational diagnostics/support bundles.

## Documentation evolution

The documentation set should mature alongside these increments.

Expected system-level documents include:

- software requirements;
- software architecture;
- software development;
- software plan;
- software planning;
- system-level IDDs.

Software items such as the headless application and GUI may later receive their own requirement/design documents. Software-item requirements may reference system-level IDDs as applicable requirements.

## Items still requiring explicit selection

- Java version;
- build tooling;
- logging stack;
- local/remote shell technology;
- API technology;
- GUI technology;
- configuration library/format;
- persistence/file format;
- CAN implementation approach;
- RFID hardware/library;
- module/repository split;
- release/versioning convention.

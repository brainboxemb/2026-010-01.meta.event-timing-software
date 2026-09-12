# Software planning

Status: working draft

This document is the current software implementation roadmap. It is intentionally more concrete than `docs/software-plan.md`.

Detailed implementation work, evidence, test results, and deviations belong in the pull request for the active implementation step rather than being duplicated here.

## Step 1 — Initial architecture baseline

Status: draft

Goal: define enough architecture to start implementation without prematurely freezing the full system design.

Current outputs:

- `docs/software-architecture-sketch.md`;
- initial layered/service-oriented direction;
- platform/device abstraction direction;
- shared command/query boundary;
- first-class status representation;
- configuration/settings boundary;
- Maven as accepted build tooling;
- Java 8 as the conservative default candidate, with Java 11 to be evaluated on original Raspberry Pi Zero / Zero W hardware before final selection;
- first implementation sequence.

Exit criteria:

- the responsibilities of the headless runtime, application services, external interfaces, and platform/device adapters are understandable;
- status has a clear central ownership/model direction;
- the first headless implementation can be started without inventing architecture ad hoc inside its PR;
- unresolved technical choices are explicitly listed rather than silently assumed;
- Java 8 and Java 11 have a concrete comparison plan on real Raspberry Pi Zero 1 hardware;
- the final Java baseline can be selected from evidence covering runtime support, footprint, performance, dependency compatibility, and deployment complexity.

### Java baseline validation

The original Raspberry Pi Zero / Zero W is a mandatory target. The Java version must therefore be validated on that hardware before the baseline is accepted.

Compare at least:

- Java 8 LTS using a maintained ARMv6-capable runtime;
- Java 11 LTS using a maintained ARMv6-capable runtime.

Use the same small representative application and measure or verify:

- startup time;
- steady-state resident memory use;
- heap behaviour under a small representative workload;
- version/status command responsiveness;
- JSON/API responsiveness;
- availability of intended logging, API, remote-shell, RabbitMQ, RFID, and CAN libraries;
- runtime update/security availability;
- packaging, installation, and upgrade complexity.

Do not assume that the Raspberry Pi OS default Java package is suitable for Zero 1. The current OS package baseline and ARMv6 runtime support are separate concerns.

## Step 2 — Minimal version/status application

Status: not started

Goal: create the first executable Java application and validate the main software boundaries.

Required behaviour:

- headless application starts successfully;
- application has an explicit version;
- version is available through one shared application-level query/service;
- version can be read through:
  1. local console/shell;
  2. remote terminal/shell connection;
  3. machine-readable API, initially expected to use JSON;
- a basic shared application/status representation is exposed through the same architecture;
- a logging framework is used;
- settings/configuration are externalised;
- credentials are not hard-coded;
- unit tests exist for application-level behaviour;
- GitHub Actions builds and runs the fast test suite.

Implementation choices needed before or during this step:

- final Java baseline selected from Step 1 evidence;
- reference runtime/version for Raspberry Pi Zero 1;
- logging framework/facade;
- API technology;
- remote shell technology;
- initial configuration mechanism;
- version-source strategy.

Expected verification:

- automated unit tests;
- interface-level checks showing the same version value through all three interfaces;
- build/test evidence on GitHub Actions;
- basic Windows and Linux execution evidence;
- actual execution on an original Raspberry Pi Zero / Zero W using the selected runtime;
- captured startup time, steady-state memory use, and basic command/API responsiveness on the Pi Zero 1;
- confirmation that dependencies and APIs remain compatible with the selected Java baseline.

## Step 3 — GUI status client

Status: not started

Goal: create a separate GUI/operator application that connects to the headless runtime using the defined system interface.

Initial behaviour:

- connect/disconnect;
- display application version;
- display central application status;
- display available subsystem/waypoint status;
- clearly represent stale/unavailable/disconnected state.

The GUI must not depend directly on internal runtime classes. This step should validate the API/IDD and status representation from a second software item.

## Step 4 — Registration core

Status: not started

Goal: introduce the core waypoint registration behaviours independent of real hardware.

Candidate scope:

- lifecycle state `OPEN` / `CLOSED`;
- RFID-based participant registration through an abstraction;
- local start procedure;
- manual registration;
- penalty-code registration;
- penalty-code revocation/correction;
- simple text/file-based registration persistence;
- common registration/event model capable of representing time and non-time registrations;
- status/health for registration and persistence services.

Before implementation, these candidate behaviours should be promoted into appropriate requirements and interface documentation.

## Step 5 — RFID and CAN adapters

Status: not started

Goal: connect the registration core to external waypoint hardware/interfaces through explicit contracts.

Candidate scope:

- RFID implementation;
- CAN interface implementation;
- simulated/fake adapters;
- platform-specific capability handling;
- device status integration;
- integration tests.

## Step 6 — Backoffice integration

Status: not started

Goal: integrate with a backoffice through a transport-independent boundary, with RabbitMQ as an intended transport.

Candidate scope:

- system-level interface definition/IDD;
- RabbitMQ adapter;
- connection/status monitoring;
- retries/reconnect;
- buffering/offline behaviour;
- message idempotency/reconciliation;
- integration-test pipeline.

## Step 7 — Raspberry Pi deployment and operationalisation

Status: not started

Goal: make the application reproducibly deployable and operable on the Raspberry Pi target.

Candidate scope:

- automated deployment;
- service startup/restart;
- target configuration and credential provisioning;
- update/rollback;
- long-running integration checks;
- hardware-in-the-loop testing where appropriate.

## Planning rules

- The architecture sketch may evolve as implementation provides evidence.
- Do not expand a software step into later domain work merely because the architecture makes it possible.
- Keep fast unit/build checks suitable for normal pull requests.
- Treat longer integration/hardware/deployment tests as a separate pipeline concern when needed.
- Keep system-level IDDs authoritative for interfaces; software-item requirements may reference them.
- Keep current-step implementation details and evidence in its pull request.

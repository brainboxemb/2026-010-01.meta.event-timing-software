# Software Implementation Planning (SIP)

Status: working draft / non-authoritative

This is the implementation roadmap for the event-timing software. It is deliberately
structured, but kept compact: enough formality to keep the project understandable and
traceable without turning a hobby project into a paperwork exercise.

Detailed implementation discussion, test logs and CI evidence belong in the applicable
issues, pull requests, releases and generated evidence.

## How this plan is used

This SIP is the **content source of truth** for the implementation steps. Each step owns:

- its number, title and status;
- Goal;
- Scope;
- Result;
- Demo;
- Done.

The generated roadmap and step cards use this content directly.

Supporting planning YAML may add estimates, document maturity, detailed activities,
dependencies and planning-change notes. It must not maintain a second copy of a step's
title, status, result or demo.

Software-item names are written name-first in prose:

```text
Headless Timing Application (SI-01)
Desktop GUI Application (SI-02)
Web Operator Application (SI-03)
```

## Completion model

A step should end in something concrete that can be shown and reviewed. **Demo** says
what we should be able to show; **Done** says what is enough to close the step.

A software-producing step normally closes on a verified software release. The exact
release mechanics belong in the SDE and repository workflow rather than being repeated
here. Failed release candidates are not silently reused.

---

## Step 1 — Architecture baseline

Status: completed

### Goal

Define enough architecture to start implementation deliberately.

### Scope

- domain baseline and operational use cases;
- software-system and software-item architecture;
- initial interface catalogue and verification direction;
- Java/Maven, TimingNode, threading, status and public/private extension direction.

### Result

- Architecture baseline for software items and interfaces.
- TimingNode, runtime, package and public/private boundaries are clear enough to code.
- Build, test and verification direction is ready for implementation.

### Demo

- Walk through the architecture book and key diagrams.
- Show the runtime, domain and interface boundaries.
- Show how public interfaces and verification levels fit together.

### Done

- the architecture documents build and are reviewable;
- the implementation repository can be started without inventing its basic boundaries;
- unresolved topics remain visible instead of being hidden as assumptions.

---

## Step 2 — Framework repository skeleton

Status: completed

### Goal

Create the public Java repository and prove that it builds and runs independently.

### Scope

- Maven reactor with reusable framework and runnable application;
- Java 8 baseline for the original Raspberry Pi Zero target;
- build identity, logging and unit-test baseline;
- reusable Git/Java project tooling and Linux/Windows CI;
- minimal application lifecycle.

### Result

- Reusable framework JAR plus runnable application JAR.
- Clean bootstrap, build and test on Linux and Windows.
- Traceable build identity, logging and a clean application lifecycle.

### Demo

- Restore pinned tooling from a clean checkout.
- Run Maven verify and produce both artifacts.
- Start the application, show its version and stop cleanly.

### Done

- clean checkout/bootstrap/build works;
- Linux and Windows verification are green;
- release `v0.1.0` is the accepted Step-2 software baseline.

---

## Step 3 — Minimal application on development host

Status: active

### Goal

Build the first useful long-running **Headless Timing Application** (SI-01) on the
development host before adding Raspberry Pi deployment and real timing hardware.

### Scope

- external application configuration with at least one TimingNode;
- shared application command/query boundary;
- local console and remote shell;
- Remote API over HTTP/JSON and WebSocket;
- equivalent version/status semantics across the initial interfaces;
- runtime file logging;
- independent development/test client;
- first ST-1 black-box application test;
- repeatable Windows execution from built artifacts.

Raspberry Pi deployment remains Step 4.

### Result

- Headless Timing Application starts from external configuration.
- Console, shell and Remote API expose the same version/status view.
- Runtime logging and a repeatable black-box test path are available.

### Demo

- Start the application on Windows from configuration.
- Show the configured TimingNode, current version/status and runtime log file.
- Read the same version/status through console, remote shell, HTTP and WebSocket.

### Done

- configuration is validated and used for application composition;
- initial presentation interfaces use the shared application behaviour;
- ST-1 exercises the running process through public interfaces;
- Windows artifact execution is repeatable and CI is green;
- the step closes on the next accepted `0.2.x` release after the active work is complete.

---

## Step 4 — Raspberry Pi Zero image and updates

Status: planned

### Goal

Run the working application on the original Raspberry Pi Zero / Zero W with a repeatable
image and a fast application-update path.

### Scope

- pinned Raspberry Pi OS/base image and ARMv6-capable Java runtime;
- reproducible flashable image;
- automatic service startup;
- versioned application update without reflashing the whole image;
- preservation of configuration/data across normal app updates;
- first real Pi Zero resource measurements.

### Result

- Reproducible Raspberry Pi Zero image.
- Versioned application update without reflashing.
- First target-hardware resource baseline.

### Demo

- Flash the generated image and boot the target.
- Query application version and status remotely.
- Update the application and verify the restart path.

### Done

- image creation is repeatable from documented inputs;
- application starts automatically on a real original Pi Zero / Zero W;
- update works without manual file-copy guesswork;
- basic resource measurements and build/runtime identity are recorded.

---

## Step 5 — First Desktop GUI client

Status: planned

### Goal

Prove that the **Desktop GUI Application** (SI-02) can use the remote application
interface as a genuinely separate client.

### Scope

- connect/disconnect and endpoint selection;
- display version and basic application/TimingNode status;
- clear stale/disconnected state;
- no dependency on internal Headless Timing Application classes or files;
- local and Raspberry Pi endpoints.

### Result

- Separate desktop GUI client for the Headless Timing Application.
- Network-only connection to the application.
- The same client works with local and Raspberry Pi endpoints.

### Demo

- Show live version and status in the GUI.
- Stop/restart the Headless Timing Application and show reconnect behaviour.
- Switch the GUI from a local endpoint to the Raspberry Pi endpoint.

### Done

- GUI and Headless Timing Application build independently;
- basic connection/status behaviour has automated coverage;
- local and Raspberry Pi demonstrations use the same client logic.

---

## Step 6 — External reference/test project

Status: planned

### Goal

Create a separate public consumer that proves the framework can be used outside its own
reactor.

### Scope

- public/stub composition using published/local Maven artifacts;
- deterministic ST-1 application scenarios;
- lightweight ST-2 socket/backoffice simulator;
- multiple synthetic TimingNodes/sources where useful;
- fault injection through supported test boundaries.

### Result

- External reference/test repository.
- Framework consumed as a normal external dependency.
- Repeatable ST-1 and ST-2 synthetic scenarios.

### Demo

- Build and run from the reference repository only.
- Start a synthetic TimingNode composition.
- Exercise the socket simulator, disconnect and reconnect flow.

### Done

- no framework source copy/fork is required;
- public contracts are sufficient to compose and test the application;
- key synthetic scenarios run automatically where practical.

---

## Step 7 — Proprietary extension proof

Status: planned

### Goal

Prove that a private implementation can replace a public stub through the same public
contract.

### Scope

Use one small but realistic private component, preferably an RFID adapter shell or
proprietary tag/protocol implementation.

### Result

- A private implementation can replace a public stub.
- Both compositions use the same public framework contract.
- Public builds remain independent of private source.

### Demo

- Run the public-stub composition.
- Swap in the private implementation.
- Show equivalent higher-level application behaviour.

### Done

- public framework source does not change to select the private component;
- private code is not required to build/test the public framework;
- proprietary identities and protocol details remain private.

---

## Step 8 — TimingNode data and state foundation

Status: planned

### Goal

Implement the useful local timing/domain behaviour without depending on production
hardware.

### Scope

- registrations and per-source sequence/history;
- StageStartTimes and RaceData/reference data;
- NextUpTeams with traceable changes;
- StageTiming / derived timing results;
- simple persistence, restart and restore;
- clear TimingNode lifecycle and relevant degraded/error state;
- bounded state-changing work.

### Result

- Deterministic timing data and state foundation.
- Registration, next-up-team and reference-data behaviour works locally.
- State and source sequence continue correctly after restart.

### Demo

- Run two independent synthetic registration sources.
- Update local timing/team data and show a derived timing result.
- Restart and show restored state with continued source sequences.

### Done

- core state transitions and sequence rules have deterministic tests;
- restart/restore paths are automated;
- behaviour can be driven without production hardware;
- failures are visible rather than silently ignored.

---

## Step 9 — Web/iPad operator application

Status: planned

### Goal

Provide the browser/iPad **Web Operator Application** (SI-03).

### Scope

- Headless Timing Application serves the web bundle;
- web-specific HTTP endpoints and WebSocket channel;
- status, registrations and useful timing controls;
- TimingNode open/close and start flow where defined;
- NextUpTeams interaction;
- clear disconnected/stale state and reconnect snapshot;
- representative iPad/Safari use.

### Result

- Browser/iPad operator application.
- Live operation against the Headless Timing Application.
- Explicit stale and reconnect behaviour.

### Demo

- Operate the application from a browser/iPad.
- Interrupt the connection and show stale/disconnected state.
- Reconnect to a fresh snapshot and continue with live updates.

### Done

- representative Safari/iPad flow works;
- normal local use does not require internet/backoffice connectivity;
- business rules remain in the Headless Timing Application.

---

## Step 10 — Stub-controlled hardware integration

Status: planned

### Goal

Exercise device, fault and recovery flows deterministically before connecting production
hardware.

### Scope

- RFID power/lifecycle/reads and failure injection;
- CAN discovery, keypad and display behaviour;
- Display V1/V2 connection and reconnect flows;
- network/backoffice failure scenarios where useful;
- all injected events use normal adapter/application paths.

### Result

- Controlled synthetic hardware environment.
- RFID, CAN, keypad and display lifecycle simulation.
- Deterministic device fault and recovery injection.

### Demo

- Drive a normal synthetic device lifecycle.
- Inject reads, discovery and display updates.
- Force a failure and demonstrate recovery.

### Done

- scenarios are repeatable without physical hardware;
- test code does not directly mutate timing/domain state;
- the same contracts are suitable for later production adapters.

---

## Step 11 — Production RFID/CAN/display integration

Status: planned

### Goal

Replace the proven hardware stubs with representative real implementations.

### Scope

- production/private RFID control and protocol/decryption;
- production CAN adapter and supported devices;
- keypad and Display V1;
- Display V2 network data path;
- device health/recovery;
- hardware-in-the-loop verification.

### Result

- Real RFID, CAN and display adapters.
- Representative hardware-capable Headless Timing Application deployment.
- Observable device status and recovery.

### Demo

- Run the application with representative real hardware.
- Capture registrations and device discovery.
- Force a recoverable device failure and recover.

### Done

- representative HIL scenarios pass;
- production adapters replace stubs without changing domain behaviour;
- Pi Zero resource behaviour remains workable.

---

## Step 12 — Backoffice/reference-data integration

Status: planned

### Goal

Connect local operation to the backoffice while keeping local timing useful during an
outage.

### Scope

- system-level backoffice contract;
- transport-independent semantic boundary;
- RabbitMQ adapter and source-aware routing;
- StageStartTimes/reference-data synchronisation;
- registration outbox/delivery and reconciliation;
- reconnect/idempotency;
- ST-3 RabbitMQ integration environment.

### Result

- Backoffice-integrated Headless Timing Application.
- Offline-safe source-aware synchronisation.
- Reproducible RabbitMQ integration tests.

### Demo

- Exchange data through a synthetic broker topology.
- Stop the broker while local operation continues.
- Restart it and reconcile pending data.

### Done

- source routing/isolation is verified;
- local data survives broker outages;
- reconnect restores normal synchronisation;
- proprietary mappings remain outside the public repository.

---

## Step 13 — Deployment hardening and operation

Status: planned

### Goal

Turn the early target image/update path into a supportable operational setup.

### Scope

- harden image creation and service recovery;
- configuration/secrets provisioning;
- application and image/runtime update policy;
- rollback/recovery;
- diagnostics/support export;
- longer ST-4 and hardware-in-the-loop scenarios;
- resource limits based on measured evidence where useful.

### Result

- Supportable Raspberry Pi deployment lifecycle.
- Provisioning, updates, rollback and diagnostics.
- Operational ST-4 / hardware-test baseline.

### Demo

- Provision a clean target and start the service.
- Perform an update and a failed-update rollback.
- Produce diagnostics and run the representative operational scenario.

### Done

- provisioning/update/recovery paths are repeatable;
- configuration/secrets stay outside generic public images;
- operational diagnostics are useful;
- representative full-system verification is green.

---

## Java 11 checkpoint

Status: future

Do not block early work on Java 11. Once the application is representative, compare a
suitable Java 11 runtime with the working Java 8 baseline on the same Pi Zero class and
workload. Move only if the measured deployment, memory, CPU, compatibility and maintenance
trade-off is worthwhile.

## Planning rules

- Keep steps demonstrable and reasonably small.
- Prefer normal public interfaces over demo-only shortcuts.
- Keep detailed implementation/evidence in issues, PRs and generated evidence.
- Keep the SIP concise; change it when the plan changes, not when every task status changes.
- Measure Pi Zero behaviour rather than inventing resource budgets.
- Keep lifecycle, subsystem health and connectivity as separate concepts.

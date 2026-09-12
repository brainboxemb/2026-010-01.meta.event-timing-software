# Software Implementation Planning (SIP)

Status: working draft / non-authoritative

This document is the concrete software implementation sequence derived from `docs/10-SDP-software-development-plan.md`.

The SDP defines the higher-level development approach and phased evolution. This SIP turns that direction into ordered implementation steps, scope, concrete deliverables, demonstrations and exit evidence.

Detailed implementation decisions, tests and evidence for an active step belong in that step's pull request.

Software-item identifiers are stable across the document set:

```text
SI-01  Headless Timing Application
SI-02  Desktop GUI Application
SI-03  Web Operator Application
```

## Step-completion model

Every implementation step should end in something concrete that can be shown, used or reviewed.

Use the following distinction:

- **Goal** — why the step exists;
- **Scope** — what work belongs in the step;
- **Deliverable** — the tangible result that exists when the step is complete;
- **Demonstration** — a short, repeatable walkthrough showing what is newly possible;
- **Evidence / exit criteria** — objective evidence that the result is not merely a successful demo.

The demonstration is deliberately stakeholder-friendly. A manager, developer or reviewer should be able to answer:

> What can the system do now that it could not do before this step?

A demonstration does not replace verification. Automated tests, CI results, measurements and review evidence remain required where applicable.

## Step 1 — Architecture baseline

Status: in progress

### Goal

Define enough software-system/component architecture to start the framework repository deliberately.

### Current scope and outputs

- `docs/03-domain-baseline.md`;
- `docs/04-UC-system-use-cases.md`;
- `docs/30-SSAD-software-system-architecture.md`;
- `docs/31-01-SAD-timing-application-architecture.md`;
- `docs/31-01-SDD-01-timing-system-design.md`;
- `docs/31-01-SDD-02-data-and-display-design.md`;
- `docs/31-01-SDD-03-java-component-design.md`;
- `docs/31-01-SDD-04-runtime-topology-and-configuration.md`;
- `docs/31-01-SDD-05-backoffice-transport-design.md`;
- `docs/31-02-SAD-gui-application-architecture.md`;
- `docs/31-03-SAD-web-operator-application-architecture.md`;
- `docs/50-SVP-software-verification-plan.md`;
- software-item register and system interface catalogue;
- generated architecture/state-model diagrams on `dev/pr-<N>/docs`;
- Maven as accepted build tooling;
- Java 8 as accepted initial baseline for the mandatory original Raspberry Pi Zero target;
- Java 11 as a later evidence-driven upgrade candidate;
- `TimingSystemInstance` as logical total-system isolation boundary;
- registration assets and registration sources as separate concepts;
- serialized execution/threading direction;
- first-class status model;
- fault/recovery architecture direction;
- Pi Zero resource-baseline strategy;
- platform/device ports;
- public/private extension strategy;
- registration and ready-team traceability as separate capabilities;
- in-memory active state with simple file backup/restore;
- transport-independent backoffice boundary with socket and RabbitMQ adapter directions;
- layered system-test strategy (`ST-1` through `ST-4`).

### Deliverable

A reviewable **software architecture baseline package** in GitHub consisting of the domain baseline, use cases, SSAD, software-item SAD/SDDs, SDE/SVP and generated architecture document set.

This package is sufficient to create the first implementation repository without inventing its fundamental boundaries during coding.

### Demonstration

Walk through the generated `dev/pr-<N>/docs` documentation and demonstrate, using the diagrams and documents, that a reviewer can answer at least:

1. What are SI-01, SI-02 and SI-03?
2. How can one SI-01 process host multiple total-system instances?
3. How do registration assets, registration sources and antennas relate?
4. Where are mutable state and threading controlled?
5. How can public stubs and private production implementations use the same contracts?
6. How do console/GUI/web clients reach the same application behaviour?
7. How can backoffice communication use a lightweight socket transport for tests and RabbitMQ for production-shaped integration?
8. What is tested at unit, application, socket-loop, RabbitMQ and hardware levels?

No executable product behaviour is claimed in this step.

### Evidence / exit criteria

- SI-01, SI-02 and SI-03 responsibilities are understandable;
- principal system interfaces are catalogued and future IDD ownership is clear;
- system, runtime, core, adapter and client responsibilities are understandable;
- Maven module/package direction is clear enough to create the framework skeleton;
- registration versus ready-team ownership is explicit;
- registration asset versus registration source ownership is explicit;
- status/lifecycle/fault concepts are separated cleanly;
- public contracts can support stubs and private implementations;
- a verification strategy exists before implementation begins;
- use cases provide an operational bridge toward formal requirements;
- unresolved decisions remain visible rather than being silently assumed;
- generated diagrams and documentation are successfully built and reviewable in GitHub.

## Step 2 — Framework repository skeleton

Status: not started

### Goal

Create the public framework repository and establish build/dependency/test foundations for SI-01/framework development.

### Scope

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

### Deliverable

A clean public Java/Maven framework repository that can be cloned, built and tested independently and produces a minimal runnable headless application artifact.

### Demonstration

From a clean checkout:

```text
mvn verify
    -> all modules compile
    -> unit/architecture checks pass

run timing-app
    -> application starts
    -> configuration is loaded
    -> version/build identity is logged
    -> application shuts down cleanly
```

Show the Maven dependency direction and demonstrate that `timing-core` does not require concrete device/network libraries.

### Evidence / exit criteria

- clean checkout builds on supported development environments;
- GitHub Actions is green;
- Java 8 source/bytecode baseline is enforced;
- initial module dependencies follow the documented architecture;
- minimal startup/shutdown is covered by automated tests where practical;
- README explains build/run/test;
- repository contains the required SDE baseline files.

## Step 3 — Minimal version/status application on development host (SI-01)

Status: not started

### Goal

Prove the public runtime/application boundary with deliberately small behaviour on the primary development environment before introducing target-image complexity.

Windows is the first concrete execution target for this step. Linux-host execution may also be included through CI or developer testing, but Raspberry Pi deployment is deliberately separated into Step 4.

### Scope

- one central version source;
- central application/status model;
- version/status readable through:
  1. local console/shell;
  2. remote terminal/shell;
  3. HTTP/JSON API;
- minimal WebSocket status/event stream;
- minimal configurable `TimingSystemInstance`;
- transport adapters do not own application state;
- application handlers can run synchronously in unit tests;
- logging and externalised settings are active;
- first `ST-1 Application Behaviour` black-box tests through the public application interface;
- GitHub Actions verifies fast tests;
- repeatable Windows execution from built artifacts.

### Deliverable

The first useful SI-01 executable for the development environment: a headless Java application with one shared version/status model exposed through multiple interfaces and a repeatable black-box test path.

### Demonstration

On a Windows development machine, start SI-01 from the built artifact and show:

```text
local console  -> version + status
remote shell   -> same version + equivalent status
HTTP/JSON      -> same version/status model
WebSocket      -> receive a status/event update
```

Then run the `ST-1` black-box scenario against that process.

A useful stakeholder statement is:

> We now have the real headless application running as a separate process and can inspect the same live state through all initial public interfaces.

### Evidence / exit criteria

- automated tests verify shared application behaviour rather than duplicating behaviour in each transport;
- `ST-1` demonstrates the running process through public interfaces;
- GitHub Actions is green;
- Windows execution from produced artifacts is repeatable;
- Linux-host execution is smoke-tested where practical;
- lifecycle/status architecture is not coupled to one client transport;
- no Raspberry Pi-specific code is required to run the application behaviour.

## Step 4 — Raspberry Pi Zero image, target run and update automation

Status: not started

### Goal

Move the already-working SI-01 executable to the mandatory original Raspberry Pi Zero / Zero W using reproducible automation rather than a hand-built target.

This step deliberately introduces target deployment early. It should establish both **clean-device provisioning** and a **fast application-update path** before the rest of the product grows.

### Scope

#### Reproducible target image

- select and pin the supported Raspberry Pi OS/base-image baseline;
- select and pin the ARMv6-capable Java 8 runtime;
- automated construction/customisation of a complete flashable Pi image;
- install SI-01 artifact and required runtime files;
- install service definition/startup configuration;
- include safe default/public configuration only;
- keep deployment secrets and real/proprietary configuration out of the public image source;
- record image/source/application/runtime versions for traceability.

The concrete image technology remains an implementation choice. Candidates may include a Raspberry Pi image-generation toolchain or deterministic customisation of a pinned base image. The requirement is reproducibility, not a specific image builder.

#### Application update path

Normal SI-01 changes should not require reflashing the complete SD image.

Introduce a versioned update artifact/process capable of at least:

- transferring/installing a new SI-01 application build onto an existing prepared Pi;
- stopping/restarting the service safely;
- reporting the running application version;
- preserving configuration/data that should survive an application update;
- supporting an initial rollback/recovery direction.

Full-image rebuilding remains appropriate for OS, Java runtime or image-layout changes.

#### Target verification

- boot the generated image on an original Pi Zero / Zero W;
- automatically start SI-01 as a service;
- run version/status checks over the network;
- establish the first real Pi Zero resource baseline;
- capture startup time, RSS/heap behaviour, CPU, thread count and response latency;
- exercise the application-update path on the same target.

### Deliverable

Two concrete build/deployment artifacts:

1. a **reproducibly generated, flashable Raspberry Pi Zero image** containing the pinned Java runtime and SI-01 service;
2. a **versioned SI-01 application-update artifact/process** for updating an already provisioned target without reflashing the whole image.

The image/update artifacts should be produced by CI or an equally reproducible automated build path rather than committed as source files to normal Git branches.

### Demonstration

Starting from generated artifacts:

1. flash the generated image to an SD card;
2. boot an original Raspberry Pi Zero / Zero W;
3. show that SI-01 starts automatically as a service;
4. query version/status over HTTP from another computer;
5. show the pinned OS/application/Java build identity;
6. record the first Pi Zero resource measurements;
7. build a newer SI-01 version;
8. apply the application update **without reflashing the SD card**;
9. show that the service restarts and reports the new version;
10. demonstrate the initial rollback/recovery route where implemented.

A useful stakeholder statement is:

> We can generate a complete target image automatically, boot it on the weakest supported hardware, and deploy a new application version without rebuilding the device by hand.

### Evidence / exit criteria

- complete image construction is scripted/reproducible from documented inputs;
- image provenance includes OS/base image, Java runtime and SI-01 version/commit;
- the resulting image boots on real original Pi Zero hardware;
- SI-01 starts automatically through the target service manager;
- HTTP version/status is reachable remotely after boot;
- the first Pi Zero resource baseline from the SVP is recorded;
- application update can be repeated without manual file-copy guesswork or full-image reflashing;
- persistent configuration/data required across app updates is preserved;
- no secrets or real proprietary deployment mappings are embedded in the public image recipe;
- CI/build artifacts are retained sufficiently for review/reproduction.

## Step 5 — First Desktop GUI client (SI-02)

Status: not started

### Goal

Prove a separate software item can consume the system-defined application control/status interface, including when SI-01 runs on a different host such as a Raspberry Pi.

### Scope

- connect/disconnect;
- configure/select SI-01 endpoint;
- display application version;
- display application, timing-system and subsystem status;
- show disconnected/stale state;
- no direct dependency on internal SI-01 runtime classes or filesystem;
- verify local development connection and remote Pi connection.

This step is deliberately early because it validates the network/interface boundary before the domain becomes large.

### Deliverable

A separately runnable desktop GUI application that connects to SI-01 only through the defined network interface.

### Demonstration

Run SI-02 on a workstation and:

1. connect to SI-01 running locally;
2. show live version/status;
3. stop SI-01 and show clear disconnected/stale state;
4. reconnect;
5. change the configured endpoint to the Step-4 SI-01 image running on a Raspberry Pi;
6. show the same information without changing GUI business logic.

### Evidence / exit criteria

- GUI and SI-01 build independently;
- GUI contains no direct dependency on SI-01 implementation classes;
- automated interface tests cover connect/status/disconnect where practical;
- local and remote-Pi demonstrations both work;
- the interface model is sufficient to support a genuinely separate client.

## Step 6 — External reference/test project

Status: not started

### Goal

Create a separate public consumer/template project that builds against framework Maven artifacts and becomes the primary integration-learning environment.

### Scope

- complete runnable composition using public/stub adapters;
- deterministic integration scenarios;
- use of `timing-testkit`;
- console/remote/API/WebSocket system tests;
- `ST-1 Application Behaviour` scenarios;
- lightweight `ST-2 Socket Loop` transport and backoffice simulator;
- configurable multiple system instances/assets/sources;
- fault injection through stubs/test-control;
- documentation proving external consumer setup;
- CI that builds without relying on framework-reactor internals.

### Deliverable

A separate public reference repository that consumes published/local Maven framework artifacts exactly as an external project would and can run a fully synthetic timing environment.

### Demonstration

From the reference project only:

1. resolve the framework artifacts;
2. start one SI-01 composition with stub devices;
3. control it through the normal application interface (`ST-1`);
4. start a simple socket backoffice simulator (`ST-2`);
5. configure at least two synthetic registration sources;
6. exchange source-aware messages over the socket boundary;
7. disconnect/reconnect the simulator and show status/recovery;
8. optionally scale the configuration to several `TimingSystemInstance` objects.

### Evidence / exit criteria

- reference project builds without framework reactor internals;
- no framework source copy/fork is required;
- public APIs/SPIs are sufficient to compose the application;
- `ST-1` and `ST-2` run automatically in CI where practical;
- multi-source routing is deterministic;
- test controls exercise normal adapters/queues rather than mutating domain state directly;
- documentation is sufficient for a new consumer to run the project.

## Step 7 — Proprietary extension proof

Status: not started

### Goal

Prove one private implementation can replace a public stub through the same API/SPI contract.

### Scope

Preferred early candidate:

- production RFID antenna adapter shell and/or proprietary tag protocol/decryption component.

### Deliverable

A private component/application composition that replaces at least one public stub using only the supported public framework contracts.

### Demonstration

Run the same reference/application scenario twice:

```text
composition A -> public stub implementation
composition B -> private implementation
```

Demonstrate that the higher-level application behaviour and test interface remain the same and that no public framework source change is required to select the private component.

### Evidence / exit criteria

- public framework source remains unchanged;
- reference and private applications use the same public contract;
- private Maven/dependency consumption works through the chosen secure mechanism;
- private code is not required to compile/test the public framework;
- public verification remains meaningful without exposing proprietary protocol details;
- private identifiers/protocol data do not leak into public repository fixtures.

## Step 8 — Timing-system data/state foundation (SI-01)

Status: not started

### Goal

Implement deterministic local domain behaviour without production hardware.

### Scope

#### Registration

- registration assets and registration sources;
- per-source monotonic sequence number;
- per-source registration ledger/file;
- passage, start, manual, penalty and revocation records;
- traceable correction/revocation relationships;
- local derived result/ranking views.

#### Ready-team

- separate ready-team event journal;
- add/remove actions;
- current ready-team state projection;
- current ordered list for display logic;
- traceable persisted history.

#### Reference data

- start-time repository;
- reserve-tag conversion repository;
- synchronisation/version metadata.

#### Persistence

- in-memory repositories as application API;
- simple file backup/restore;
- source sequence-state recovery;
- explicit backup/restore status;
- fault-injection tests for failed/corrupt backup/restore paths.

#### State/recovery

- explicit `OPEN`/`CLOSED` lifecycle independent from subsystem health;
- RFID lifecycle/recovery model available to the domain/status layer;
- explicit stale/degraded/error status where relevant;
- bounded queue/backpressure behaviour designed and verified before representative load testing.

Promote mature candidate requirements before implementation.

### Deliverable

A locally complete, deterministic timing-domain core that can maintain registrations, source sequences, ready-team state and reference data through public application commands and survive a process restart through the initial persistence mechanism.

### Demonstration

Using only synthetic data and public/test interfaces:

1. start an instance with at least two synthetic registration sources;
2. open the timing-system instance and show the traceable open record;
3. create registrations on both sources and show independent source sequences;
4. add and remove ready-team numbers and show current state plus history;
5. load synthetic start-time/reference data and show a local derived timing/ranking result;
6. stop the application;
7. restart it;
8. demonstrate recovered state and continued source sequences without number reuse;
9. show an injected backup/recovery fault in status.

### Evidence / exit criteria

- deterministic unit tests cover domain/state transitions;
- source sequence and gap/identity rules are tested;
- registration and ready-team stores remain separate;
- backup/restore/restart tests are automated;
- state can be driven without production hardware;
- fault/status behaviour is explicit rather than silent.

## Step 9 — Web/iPad operator application (SI-03)

Status: not started

### Goal

Provide the React-based operational client over the existing HTTP/WebSocket system interface.

### Scope

- SI-01 serves the compiled React bundle;
- show registrations/status;
- open/close timing-system instance;
- start procedure control;
- show/manage ready-team state;
- later manual registrations/penalties where authorised;
- clear stale/disconnected representation;
- reconnect obtains a complete current state before normal live updates continue;
- verify representative iPad/Safari use;
- local browser operation does not require live internet/backoffice when SI-01 remains locally reachable.

Business rules remain server-side in SI-01.

### Deliverable

A browser/iPad operator application served by SI-01 that performs useful timing operations over HTTP/WebSocket without containing authoritative domain logic.

### Demonstration

On an iPad/browser connected to the local network:

1. navigate to SI-01 and download the React application;
2. view current application/system status and registrations;
3. open/close a system instance;
4. perform a start-procedure command;
5. add/remove ready-team entries where in scope;
6. observe live WebSocket updates;
7. interrupt the connection and show stale/disconnected state;
8. reconnect and show a fresh complete snapshot followed by live updates.

### Evidence / exit criteria

- representative Safari/iPad flow works;
- application remains usable on local LAN without internet where required;
- UI actions use the public SI-01 interface;
- reconnect/stale-state behaviour is verified;
- business rules remain server-side.

## Step 10 — Stub-controlled hardware integration

Status: not started

### Goal

Exercise complete device and recovery flows deterministically before production adapters are integrated.

### Scope

Stub/test-control scope may include:

- RFID power/lifecycle and raw reads;
- RFID health/heartbeat;
- RFID boot/reinitialise/error paths;
- encrypted/decrypted test pipeline inputs at appropriate public boundaries;
- CAN bus and discovery;
- keypad team add/remove;
- V1 display discovery/control/reconnect;
- V2 display connection/data synchronisation/reconnect;
- local network/internet/backoffice failures and recovery;
- queue pressure scenarios.

Injected events must follow the same normal application paths as real adapters.

### Deliverable

A controllable synthetic hardware environment capable of driving the complete SI-01 device lifecycle and fault/recovery behaviour through supported adapter contracts.

### Demonstration

Run an automated/manual scenario such as:

```text
RFID initially OFF
-> operator powers RFID on
-> simulate boot delay
-> READY
-> inject several raw observations
-> filtering accepts one registration
-> simulate heartbeat loss
-> status becomes degraded
-> reinitialise RFID
-> READY again

CAN scanner discovers synthetic Display V1
keypad adds/removes teams
Display V1 receives current ready-team list
Display V2 connects, receives snapshot, disconnects and reconnects
```

### Evidence / exit criteria

- scenarios are repeatable without real hardware;
- injected faults enter through normal adapter boundaries;
- timing/domain state is never directly manipulated by test code;
- lifecycle/recovery/status tests are automated where practical;
- same contracts remain suitable for production adapters.

## Step 11 — Production RFID/CAN/display integration

Status: not started

### Goal

Replace proven stubs with real implementations.

### Scope

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

### Deliverable

A hardware-capable SI-01 deployment in which the previously demonstrated synthetic device flows work with representative real RFID, CAN, keypad and display hardware.

### Demonstration

On representative hardware:

1. start SI-01;
2. power/initialise the RFID subsystem and observe health/status;
3. present representative tags and observe filtered registrations;
4. discover supported CAN devices;
5. enter/remove team numbers through the physical keypad and observe Display V1;
6. connect a Display V2 through the network/mDNS path and show data synchronisation;
7. force at least one recoverable device failure/reconnect and demonstrate recovery.

### Evidence / exit criteria

- HIL scenarios from the SVP pass;
- production adapters replace stubs without changing core/domain behaviour;
- proprietary implementation remains private;
- device status/recovery is observable;
- Pi Zero resource behaviour remains viable for representative production topology.

## Step 12 — Backoffice/reference-data integration

Status: not started

### Goal

Connect local operation to the real backoffice while retaining offline capability and validate the production-shaped RabbitMQ transport independently from application semantics.

### Scope

- system-level IDD(s);
- transport-independent backoffice semantic boundary retained;
- RabbitMQ adapter;
- per-source inbound queue consumers;
- per-source outbound routing endpoints;
- start-time synchronisation;
- reserve-tag mapping synchronisation;
- registration outbox/delivery;
- retry/reconnect/idempotency/reconciliation;
- network/link/internet/broker status;
- `ST-3 RabbitMQ Integration` using a disposable Docker/Compose broker with synthetic topology;
- private/production protocol implementation where required;
- fault/recovery verification with network/internet/broker failures separated.

### Deliverable

A backoffice-integrated SI-01 implementation with offline-safe local operation, source-aware inbound/outbound synchronisation and a reproducible RabbitMQ integration-test environment.

### Demonstration

First with the public/synthetic `ST-3` environment:

1. start the RabbitMQ Docker/Compose broker;
2. start SI-01 with at least two synthetic sources;
3. show two independent inbound source consumers over shared broker infrastructure;
4. inject reference data and show local update;
5. create registrations and show source-specific outbound routing;
6. stop RabbitMQ while local registration continues;
7. show pending outbox/status;
8. restart RabbitMQ;
9. show consumer restoration and pending delivery/reconciliation.

Where permitted, repeat the applicable interface scenario with the private/real backoffice configuration without exposing those details in public evidence.

### Evidence / exit criteria

- Docker/Compose RabbitMQ integration suite is automated in CI where practical;
- source isolation/routing is verified;
- local data is not lost during broker outage;
- reconnect restores configured consumers and pending delivery;
- actual proprietary mappings/protocol remain outside the public repository;
- IDD and software-item implementation remain traceable.

## Step 13 — Deployment hardening and operationalisation

Status: not started

### Goal

Turn the early Step-4 image/update automation into a production-supportable deployment lifecycle once the application, devices and backoffice integration are representative.

### Scope

- harden/review the Raspberry Pi image-generation pipeline;
- service startup/restart and watchdog/recovery policy;
- configuration and secret provisioning;
- application update policy and artifact retention;
- rollback/recovery after failed update;
- OS/runtime/image update policy;
- diagnostic/support export;
- longer-running integration and hardware-in-the-loop tests;
- `ST-4 Target / Full-system` scenarios;
- resource budgets promoted from measured baselines where evidence supports useful limits.

### Deliverable

A reproducibly deployable and supportable Raspberry Pi operational environment with documented clean provisioning, configuration, service management, normal application updates, image-level updates, diagnostics and recovery procedures.

### Demonstration

Using the automated deployment pipeline established in Step 4:

1. create/flash a clean target image;
2. provision environment-specific configuration and secrets through the supported mechanism;
3. boot and show automatic service startup;
4. connect SI-02 and/or SI-03 and show normal operation;
5. perform a normal application update;
6. demonstrate rollback/recovery from a deliberately failed update;
7. demonstrate the documented image/OS/runtime upgrade path where applicable;
8. produce a diagnostic/support export;
9. run the representative `ST-4`/HIL operational scenario.

### Evidence / exit criteria

- provisioning and update pipelines are repeatable from documented automation;
- service survives reboot/restart as required;
- configuration/secrets are not embedded in public source or generic image artifacts;
- update/rollback/recovery paths are verified;
- artifacts and versions remain traceable;
- resource measurements remain within accepted/promoted budgets;
- operational diagnostics provide enough information to investigate common faults.

## Java 11 checkpoint

Status: future / evidence-driven

Do not block early development on Java 11.

When the application is representative enough, compare Java 11 with the working Java 8 baseline on the same Pi Zero hardware/workload for runtime availability, deployment, startup, memory, threads, CPU, responsiveness, library compatibility and maintenance support.

### Deliverable

A short evidence-backed architecture decision: retain Java 8, move to Java 11, or defer the decision.

### Demonstration

Run the same representative workload on the same Pi Zero class using the known Java 8 baseline and candidate Java 11 runtime and show the measured comparison.

### Evidence / exit criteria

Only an explicit architecture decision with target-hardware evidence may supersede the Java 8 baseline.

## Planning rules

- Every implementation step should end with a concrete deliverable and repeatable demonstration.
- A successful demonstration is not by itself sufficient evidence for completion.
- Prefer demonstrations that exercise the same public interfaces/adapters intended for normal operation instead of special demo-only bypasses.
- Establish target-image and application-update automation early; do not let manual Pi provisioning become the normal development workflow.
- Prefer fast application updates for ordinary SI-01 changes; rebuild/reflash complete images when OS/runtime/image-level inputs change.
- Do not start a later software step merely because an abstraction already exists.
- Keep fast unit/build checks suitable for normal pull requests.
- Separate longer integration/hardware/deployment pipelines when needed.
- Keep system-level IDDs authoritative for interfaces; software-item SRDs reference them where applicable.
- Keep implementation/evidence details in the active implementation PR.
- Keep registration and ready-team models distinct unless an explicit later requirement defines an interaction.
- Keep registration asset identity, registration-source identity and external deployment mapping distinct.
- Prefer public contracts plus composition over subclass-based/private-source coupling.
- Measure Pi Zero resource behaviour from the first target image and avoid invented numeric budgets without evidence.
- Keep lifecycle state, subsystem health and connectivity status separate concepts.

# Software Development Plan (SDP)

Status: working draft / non-authoritative

This Software Development Plan describes the **high-level development strategy** for the software system: objectives, development approach, major phases/workstreams, resources, dependencies, risks and important unknowns.

It deliberately does **not** contain the detailed implementation sequence. That belongs in `11-SIP-software-implementation-planning.md`.

## Document boundaries

Use the project documents as follows:

```text
SDP  high-level development strategy, phases, risks, resources and assumptions
SIP  concrete implementation steps, deliverables, demonstrations and exit evidence
SDE  development environment, repositories, GitHub workflow, tooling and artifact conventions
SVP  verification strategy, levels, system-test profiles and evidence model
SSAD/SAD/SDD  software architecture and design
```

The SDP should remain understandable without knowing implementation details. When a phase requires detailed tasks, technology setup or commands, the SDP points to the SIP, SDE, SVP or architecture documents rather than duplicating them.

## Development objectives

The development effort should produce a reusable software system that:

- supports reliable event timing and time registration;
- runs on the mandatory original Raspberry Pi Zero / Zero W target;
- separates the headless timing runtime from desktop and browser/iPad presentation clients;
- supports multiple logical timing-system instances in one application process;
- supports configurable registration assets, registration sources and device mappings;
- remains locally useful when external/backoffice connectivity is unavailable;
- keeps traceable registration data and recovery state;
- can be tested extensively without requiring all production hardware or proprietary components;
- allows proprietary implementations to plug into public contracts without forking public framework source;
- provides reproducible build, test, documentation and target-deployment automation early in development.

## Development strategy

### Incremental vertical development

Develop in small, demonstrable increments rather than attempting the complete timing system in one integration step.

Each increment should reduce a meaningful risk and end in a concrete deliverable. Detailed increment definitions and demonstrations belong in the SIP.

### Architecture before irreversible coupling

Define the important system/software-item boundaries, interface ownership, public/private extension model, threading/state model and persistence direction before production implementations make those choices expensive to change.

Architecture remains a tool for implementation, not an excuse to postpone executable software indefinitely.

### Early executable and early target automation

First prove the headless application on a normal development environment, primarily Windows. Once the first useful executable exists, establish automated Raspberry Pi image generation and application update deployment early.

The intent is to prevent manual SD-card preparation or ad-hoc target setup from becoming normal development practice.

### Automation-first engineering

Use GitHub Actions and repository automation from the first implementation repositories for build, test, generated evidence and later target-image/update workflows.

AI-assisted development is part of the development approach, but AI follows the same issue/branch/pull-request/test/review discipline as human development. Detailed repository and AI working rules belong in the SDE and repository `AGENTS.md` files.

### Progressive test realism

Start with deterministic unit/application tests and progressively add process/network boundaries, broker integration and real target/hardware verification.

The exact verification levels and `ST-*` system-test profiles belong in the SVP. The SDP only requires that test realism grows with implementation risk rather than replacing fast tests with only expensive end-to-end testing.

### Public/private separation

Keep reusable framework contracts, testkit/stubs and reference applications public where appropriate. Keep production-specific/proprietary protocol implementations, real deployment identities/mappings and secrets in private repositories or external configuration.

Prove the extension boundary early, before substantial proprietary implementation accumulates.

## High-level development phases

The detailed step numbering, deliverables and demonstrations are maintained in the SIP. These SDP phases are intentionally broader.

### Phase A — Architecture and engineering baseline

Establish the project/document model, domain baseline, use cases, software-item boundaries, system interfaces, development/verification strategy and public/private boundary.

Outcome: implementation can begin without inventing foundational conventions inside the first coding PRs.

### Phase B — Framework and first executable

Create the public Java/Maven framework structure and a minimal SI-01 headless executable on the development environment.

Prove shared version/status behaviour, public application boundaries, basic concurrency/testability direction and CI.

### Phase C — Target deployment foundation

Prove the mandatory Raspberry Pi Zero target early.

Establish reproducible image creation, pinned runtime provisioning, automatic service startup, repeatable application updates and the first target resource baseline.

This is a development foundation, not final deployment hardening.

### Phase D — Client and external-consumer proofs

Introduce a separate desktop GUI software item and an external public reference/test project.

Use these to prove that software-item interfaces and public Maven/API/SPI boundaries work outside the framework reactor and across a real network boundary.

Also prove that private/proprietary implementations can replace public stubs through supported contracts.

### Phase E — Timing-domain and operator capability growth

Implement registration/source state, ready-team state, reference data, local persistence/recovery and meaningful operational behaviour.

Introduce the browser/iPad operator application when sufficient domain capability exists to make it useful.

### Phase F — Device and backoffice integration

Integrate controlled stubs first, then representative production RFID/CAN/display implementations and backoffice communication.

Maintain the same core behaviour and public contracts while replacing test adapters with real implementations.

### Phase G — Operational maturity

Harden target deployment, update/rollback, secrets/configuration handling, diagnostics, long-running verification, hardware-in-the-loop testing and measured resource budgets.

The goal is to mature automation introduced earlier, not to introduce deployment automation only at the end.

## Planning cadence and indicative horizon

The current working planning assumption is approximately **one focused project day per week**.

Effort is estimated in **project days**, not ordinary calendar days. This is useful for a part-time/learning project because a five-project-day task means roughly five focused working sessions even when those sessions are spread across several weeks.

Detailed per-step estimates are maintained as working SIP-roadmap data in `docs/_data/sip-roadmap.json` and are rendered into the generated SIP roadmap. They are planning aids, not commitments or formal requirements.

The current baseline contains approximately **51 focused project days** from the remaining architecture work through deployment hardening. At one project day per week this gives a theoretical baseline of roughly one year. A **25% planning reserve** is currently shown for learning, integration surprises, hardware availability, target-image tooling and proprietary/backoffice unknowns.

The resulting high-level horizon is approximately:

| SDP phase | Indicative target at 1 project day/week | Planning meaning |
| --- | --- | --- |
| Phase A — Architecture and engineering baseline | September 2026 | Architecture/document baseline ready to start implementation. |
| Phase B — Framework and first executable | October 2026 | Public framework skeleton and first SI-01 behaviour running on the development host. |
| Phase C — Target deployment foundation | November 2026 | Reproducible Pi Zero image, service startup and normal application-update path demonstrated. |
| Phase D — Client and external-consumer proofs | December 2026 – January 2027 | Desktop GUI, external reference project and initial private-extension proof available. |
| Phase E — Timing-domain and operator capability growth | February – March 2027 | Local registration/state/recovery behaviour and first useful browser/iPad operator flow available. |
| Phase F — Device and backoffice integration | April – July 2027 | Stub hardware, representative real devices and backoffice integration progressively demonstrated. |
| Phase G — Operational maturity | August – September 2027 | Deployment/update/diagnostic lifecycle hardened against a representative system. |
| Planning reserve | Q4 2027 | Capacity for learning, rework, hardware/protocol uncertainty and slippage without pretending the baseline is a fixed deadline. |

These dates should be reforecast when evidence materially changes the estimate of a SIP step. The roadmap should therefore show both **estimated project days** and **baseline target dates**, while remaining a deliverable/capability roadmap rather than becoming a classical Gantt chart.

A cadence of one project day per week also creates a context-switching risk: work can lose momentum when a difficult investigation spans several weeks. Where possible, steps should therefore remain small enough to reach a demonstrable result within a limited number of focused sessions.

## Development resources and environments

The project should plan explicitly for the environments needed to develop and verify the system.

### Development workstation

At least one normal development workstation is required. The initial development environment is expected to be Windows because that is the primary convenient development host.

It should be capable of:

- Java/Maven development;
- running SI-01 and SI-02 locally;
- running Python project tooling;
- executing normal unit/application/system tests;
- running Docker/Compose when required for integration services such as RabbitMQ, if supported by the selected workstation setup.

### Mandatory target hardware

At least one original Raspberry Pi Zero / Zero W is required for target validation because ARMv6 runtime behaviour cannot be inferred reliably from desktop development alone.

Target use includes:

- validating the selected Java runtime;
- booting generated images;
- measuring startup/memory/CPU/thread behaviour;
- validating service startup and application updates;
- later device/network/hardware integration.

### Possible separate integration/test host

A second PC, Linux host or more capable Raspberry Pi may be useful for:

- hosting RabbitMQ/Docker integration services;
- running backoffice simulators/test drivers while the Pi Zero runs SI-01;
- running longer system tests;
- keeping load from the test infrastructure off the constrained target;
- acting as a reproducible local integration server.

This is currently a **planning option**, not yet a mandatory resource.

An explicit early question is whether the normal development workstation plus one standalone Pi Zero are sufficient for the first phases, or whether a dedicated integration host materially improves repeatability and test realism.

### Representative hardware later

Production-device phases require representative RFID, CAN, keypad and display hardware. These do not need to block the first framework/application phases because stubs/testkit components are part of the strategy.

## Dependencies and assumptions

Current planning assumptions include:

- original Raspberry Pi Zero / Zero W remains a mandatory SI-01 target;
- Java 8 is the initial baseline until an explicit evidence-backed decision changes it;
- Maven is the Java build/dependency baseline;
- GitHub and GitHub Actions remain available for source control and automation;
- public and private repositories can share versioned public contracts/artifacts;
- production secrets and deployment mappings can be provided outside public source control;
- representative hardware and backoffice access will become available when their integration phases begin;
- local operation must not be designed around permanent internet/backoffice availability.

When an assumption proves false, the SDP and affected SIP/architecture material should be revised explicitly.

## Risks and unknowns

The following risks/unknowns should remain visible at SDP level because they can affect overall approach, schedule or feasibility.

| Risk / unknown | Development response |
| --- | --- |
| ARMv6 Java runtime availability/support may constrain dependencies and maintenance. | Pin and test an explicit Java 8 runtime early; retain Java 11 only as an evidence-driven future option. |
| Pi Zero CPU/RAM may make apparently convenient libraries or thread models too heavy. | Measure target resources from the first target image and keep adapters/domain architecture lightweight. |
| Image generation/update automation may be more complex than expected on legacy Pi Zero support. | Introduce it early as its own SIP increment rather than deferring deployment risk. |
| Public/private API boundaries may be wrong or too coupled. | Create external reference and private-extension proofs before proprietary implementation becomes large. |
| Threading/order/timestamp errors could corrupt timing semantics. | Keep mutable state behind controlled serialized boundaries and verify source timestamps/order deterministically. |
| Offline/reconnect behaviour may become complex across persistence and backoffice synchronisation. | Separate local authority/outbox/transport semantics and test disconnect/recovery progressively. |
| Real RFID filtering/decryption/hardware behaviour may differ from simulations. | Keep production adapters replaceable and add HIL evidence once hardware is available. |
| Backoffice/RabbitMQ protocol details may constrain public interfaces. | Keep semantic backoffice ports transport-independent and isolate proprietary protocol mapping. |
| Full-field simulation may stress the runtime differently from normal Pi deployment. | Support configurable multi-instance/source simulations and measure scaling independently from target topology. |
| A single development PC + Pi Zero may be insufficient for repeatable integration/HIL tests. | Evaluate a separate integration host as test infrastructure needs become concrete. |
| One-day-per-week cadence may create context-switching overhead and stretch difficult investigations. | Keep increments demonstrable and reforecast project-day estimates when learning/integration evidence changes uncertainty. |
| AI-assisted development can create large/fast changes that are difficult to review. | Require the same PR-first workflow, tests, generated evidence and source-of-truth discipline for AI work. |

This table is expected to evolve as evidence replaces uncertainty.

## Key development decisions still to be made

Examples of decisions that remain below SDP level but may materially affect the plan include:

- exact ARMv6 Java 8 distribution/runtime;
- Raspberry Pi image-builder technology;
- application-update/rollback mechanism;
- final Java logging/test libraries;
- HTTP/WebSocket/remote-shell technology compatible with Java 8 and Pi Zero;
- exact configuration file format and secret injection model;
- public/private Maven artifact publication mechanism;
- whether a dedicated integration/test host is required;
- when Java 11 evidence is mature enough to reconsider the baseline.

Detailed resolution belongs in the SIP, SDE, architecture or implementation PR depending on the topic.

## Planning and control

The SDP controls **direction**, not day-to-day implementation tasks.

- Use the **SIP** for the ordered implementation steps, deliverables, demonstrations and exit evidence.
- Use the **SDE** for repository structure, GitHub workflow, development tooling, generated-output conventions and environment setup.
- Use the **SVP** for verification levels, test profiles and evidence expectations.
- Use **SSAD/SAD/SDD/IDD/SRD** documents for architecture, interfaces, design and formal requirements.
- Use active pull requests for implementation detail and step-specific evidence.

The SDP should be reviewed when a major assumption, resource need, risk or overall phase strategy changes.

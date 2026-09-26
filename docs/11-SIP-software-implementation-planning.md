# Software Implementation Planning (SIP)

Status: working draft / non-authoritative

This document explains **how the software is expected to grow from the current framework
into a usable timing system**. The roadmap is intended for two audiences:

- a software engineer should be able to understand why the next increment exists, its
  boundaries, dependencies and exit criteria;
- a project reviewer/manager should be able to see what value or uncertainty the step
  addresses, which resources can block it, and what can be demonstrated afterwards.

The SIP is the content source of truth for the generated roadmap and step cards. Detailed
activity history, CI logs and release mechanics live in issues, pull requests, SDE and
generated evidence.

## How to read a step

Each step uses the same small structure, but the text should carry useful information
rather than merely fill headings:

- **Purpose** explains why the step is in this position and which value/risk it addresses.
- **Goal** states the capability to add.
- **Scope** says what work belongs in the step.
- **Not in this step** is used where a boundary prevents accidental scope growth.
- **Needs** names real dependencies or resources that can gate the work.
- **Result** is the short manager-facing outcome shown on the roadmap.
- **Demo** is the practical end demonstration.
- **Done** is the engineering exit criterion.

The roadmap estimates are focused project days. Each step may show its original estimate,
git-derived actual effort and current remaining estimate. These are independent planning
signals: original minus actual does not have to equal remaining. Future phase ends are
shown as concrete Monday boundaries for readability; the underlying cumulative forecast
is calculated before that display rounding. Forecast dates are planning aids, not
commitments.

---

## Step 1 — Architecture baseline

Status: completed

### Purpose

Create enough shared language and ownership before implementation starts. The objective
was not to finish the whole architecture, but to stop the first code changes from
silently deciding domain boundaries, software-item ownership and interface direction.

### Goal

Define the first architecture baseline for the timing software.

### Scope

- domain and TimingNode baseline;
- Headless Timing Application boundary;
- initial interface catalogue;
- Java/Maven and verification direction.

### Needs

- project/domain knowledge;
- architecture/document tooling.

### Result

- First software architecture baseline.
- TimingNode and application ownership are clear.
- Implementation can start deliberately.

### Demo

- Walk through the architecture diagrams.
- Explain TimingNode and application ownership.
- Show where the first executable fits.

### Done

- architecture documents build and are reviewable;
- framework implementation can start without inventing basic ownership;
- unresolved subjects remain explicit rather than being presented as decisions.

---

## Step 2 — Framework repository skeleton

Status: completed

### Purpose

Move from architecture into executable software. A real repository, build and runnable
application provide the foundation on which every later domain, interface and device
increment can be verified.

### Goal

Create the Java repository and prove that it builds and runs independently.

### Scope

- Maven reactor with reusable framework and runnable application;
- Java baseline;
- build/version identity and logging baseline;
- unit tests and Linux/Windows CI;
- minimal application lifecycle.

### Needs

- development workstation;
- GitHub CI.

### Result

- Framework and runnable application artifacts.
- Clean Linux and Windows build/test.
- Traceable build identity and lifecycle.

### Demo

- Build from a clean checkout.
- Produce both artifacts.
- Start, identify and stop the application.

### Done

- clean bootstrap/build works;
- Linux and Windows verification are green;
- release `v0.1.0` is the accepted Step-2 baseline.

---

## Step 3 — Application and Remote API foundation

Status: active

### Purpose

Turn the framework into a useful long-running application before adding timing-domain
complexity. This step establishes the application boundary that later simulation, GUI,
backoffice and hardware work can all use without reaching into SI-01 internals.

### Goal

Build the first useful **Headless Timing Application** (SI-01) on the development host.

### Scope

- external application configuration with at least one TimingNode;
- shared command/query behaviour;
- local console and remote shell;
- Remote API over HTTP/JSON and WebSocket;
- consistent version/status semantics;
- runtime file logging;
- black-box/application testing;
- JavaFX engineering client for manual Remote API integration testing.

### Not in this step

- real timing/domain behaviour beyond the minimum needed for the application shell;
- production timing hardware;
- the planned Desktop GUI Application (SI-02).

### Needs

- Windows development workstation;
- built SI-01 artifacts;
- no Raspberry Pi or timing hardware.

### Result

- SI-01 runs from external configuration.
- Public interfaces share application semantics.
- Black-box testing is repeatable.

### Demo

- Start SI-01 from configuration.
- Inspect version/status through public interfaces.
- Inspect IF-03 with the JavaFX test client.

### Done

- configuration drives application composition;
- initial presentation interfaces use shared application behaviour;
- ST-1 exercises the running application through public interfaces;
- runtime logging and Windows artifact execution are repeatable;
- the step closes on the next accepted `0.2.x` release.

---

## Step 4 — TimingNode state and domain foundation

Status: planned

### Purpose

Put useful timing concepts into software while the environment is still completely
controlled. This is where we learn whether the TimingNode model is pleasant to implement,
without letting hardware protocols or deployment details shape the domain prematurely.

### Goal

Implement the main local TimingNode data/state model with deterministic tests.

### Scope

- registrations and source sequence/history;
- StageStartTimes;
- NextUpTeams;
- RaceData/reference data;
- TimingNode lifecycle/status needed by these capabilities;
- clear state-change ownership and observable results.

### Not in this step

- production RFID/CAN hardware;
- target-platform deployment;
- full persistence/recovery and end-to-end event simulation.

### Needs

- representative synthetic data;
- domain examples/test cases.

### Result

- Core TimingNode state exists in software.
- State changes are deterministic and testable.
- Domain behaviour has no hardware dependency.

### Demo

- Create a TimingNode with synthetic data.
- Update starts, teams and reference data.
- Show registration history and state changes.

### Done

- core state transitions have deterministic tests;
- source identity/sequence rules are represented consistently;
- no production adapter is required to exercise the implemented behaviour.

---

## Step 5 — Simulated timing flow and recovery

Status: planned

### Purpose

Prove a useful timing flow end-to-end **without physical timing hardware**. This step
should expose mistakes in routing, sequencing, persistence and restart behaviour while
the inputs remain easy to reproduce.

It also creates the software baseline against which real hardware can later be compared:
hardware integration should replace a synthetic edge, not invent a second application
path.

### Goal

Run realistic synthetic timing scenarios through the normal SI-01 application paths.

### Scope

- synthetic registration/antenna input through supported I/O boundaries;
- StageTiming / derived timing results;
- multiple TimingNodes/sources where useful;
- persistence and restart/restore for the state that actually needs it;
- reconnect/recovery scenarios at public interfaces;
- stronger ST-1 black-box scenarios.

A small browser test client may be added here only if it materially improves manual
Remote API testing; it is not a product/software item.

### Needs

- deterministic scenario/test data;
- controllable synthetic adapters;
- no target hardware.

### Result

- Complete synthetic timing flow works.
- Restart/recovery behaviour is testable.
- Hardware can later replace simulated inputs.

### Demo

- Feed a repeatable synthetic timing scenario.
- Show derived timing results.
- Restart SI-01 and continue the scenario.

### Done

- normal timing flow is reproducible in automated tests;
- persistence/recovery semantics are explicit for implemented state;
- synthetic inputs use the same application/domain paths intended for real adapters.

---

## Step 6 — Desktop GUI Application

Status: planned

### Purpose

Create the first real external user application once SI-01 has something useful to show.
The GUI is both a product capability and an independent consumer test for the Remote API.

The current JavaFX engineering client does **not** predetermine this GUI technology.

### Goal

Create the first useful **Desktop GUI Application** (SI-02) as a separate Remote API
client.

### Scope

First useful increment:

- GUI technology/runtime/packaging decision;
- endpoint selection and connect/disconnect;
- application and TimingNode status;
- selected timing data from the Step-4/5 model;
- clear connected/disconnected/stale state;
- reconnect behaviour;
- no dependency on SI-01 internal classes/files.

### Needs

- stable enough Remote API and timing model from Steps 3-5;
- development workstation;
- explicit GUI technology decision when the step starts.

### Result

- Real independent desktop GUI exists.
- GUI uses only the Remote API.
- GUI technology is chosen explicitly.

### Demo

- Connect the GUI to a running SI-01.
- Show live timing/status data.
- Disconnect, reconnect and recover state.

### Done

- GUI and SI-01 build independently;
- connection/status behaviour has useful automated coverage;
- GUI technology and packaging choice are documented with their rationale.

---

## Step 7 — Backoffice integration on development infrastructure

Status: planned

### Purpose

Add external data exchange while everything can still run on development machines. This
keeps backoffice failure/reconnect work separate from later target-hardware debugging and
proves that local timing behaviour is not accidentally coupled to broker availability.

### Goal

Connect SI-01 to the required backoffice flows using reproducible test infrastructure.

### Scope

- reference/input data needed locally;
- outbound registrations/results as required;
- source identity/order where relevant;
- disconnect/reconnect/reconciliation behaviour;
- concrete transport adapter when the external contract is known;
- integration tests using synthetic/public test topology.

### Needs

- backoffice/interface information;
- broker/test environment if RabbitMQ is the selected transport;
- synthetic identities and test credentials/configuration.

### Result

- Backoffice data flow works in test.
- Local operation survives a broker outage.
- Transport remains outside domain behaviour.

### Demo

- Exchange representative data.
- Stop the external service.
- Continue locally and reconnect cleanly.

### Done

- implemented flows have repeatable integration tests;
- disconnect/reconnect semantics are explicit;
- transport/proprietary details do not leak into generic domain APIs.

---

## Step 8 — Target hardware and platform study

Status: planned

### Purpose

Choose the physical target **after** the software architecture and main flows are proven.
A Raspberry Pi Zero/Zero W has been the working target, but availability and the complete
hardware need should be treated as project questions rather than assumptions.

This step is a decision/research step, not yet device integration. It should answer
whether suitable off-the-shelf hardware exists or whether a small carrier/custom PCB is
worthwhile.

### Goal

Select a credible target-platform direction and understand cost, availability and
hardware gaps before procurement/prototyping.

### Scope

Investigate at least:

- availability and lifecycle risk of Raspberry Pi Zero-class options and alternatives;
- OS/runtime support for SI-01;
- networking, storage and power needs;
- whether a small local display is useful and practical, including e-ink options;
- RTC need and available RTC solutions;
- CAN controller/transceiver need and integration options;
- required GPIO/I/O/connectors and serviceability;
- off-the-shelf board/stack versus HAT/carrier/custom PCB;
- rough prototype BOM and assembly cost if a custom PCB is justified;
- low-cost PCB assembly services as an option, without selecting a supplier in advance.

### Questions to answer

- Can the required system be assembled from readily available off-the-shelf parts?
- Is a custom PCB solving a real integration/availability problem or merely adding work?
- Which hardware must be procured before the next step?
- Does the platform choice change any already-tested software boundary?

### Needs

- current availability and price research when the step starts;
- candidate board/module datasheets;
- rough electrical/interface requirements;
- small prototype quantity/cost assumptions.

### Result

- Target-platform shortlist and decision.
- Hardware gaps and risks are visible.
- Prototype cost/order path is understood.

### Demo

- Compare credible target options.
- Show the proposed hardware block diagram.
- Show rough BOM/prototype cost and risks.

### Done

- target direction is selected with recorded rationale;
- required hardware/features and procurement risks are explicit;
- off-the-shelf versus custom-PCB choice is justified;
- next-step hardware can be ordered or assembled without reopening basic platform questions.

---

## Step 9 — Target bring-up and deployment proof

Status: planned

### Purpose

Prove SI-01 on the selected physical platform before adding all real timing devices. This
separates OS/runtime/deployment problems from RFID/CAN/display integration problems.

If Step 8 selects a Pi-based solution this is the first deliberate Pi bring-up step. If
another target or a small custom carrier is selected, the same proof applies there.

### Goal

Run the representative software stack on the selected target platform.

### Scope

- acquire/assemble the selected target hardware;
- install/provision the chosen OS/runtime;
- deploy and start SI-01;
- connect through the Remote API and desktop GUI;
- record basic startup/memory/CPU/thread observations;
- decide which deployment/update automation is actually useful.

### Needs

- hardware selected in Step 8;
- storage/power/network accessories;
- representative SI-01 build.

### Result

- SI-01 runs on selected target hardware.
- Real runtime behaviour is measured.
- Deployment needs are known from use.

### Demo

- Boot the target and start SI-01.
- Connect through Remote API/GUI.
- Show runtime observations and restart.

### Done

- target execution is repeatable enough for development;
- selected OS/runtime/install path is recorded;
- actual target limitations, if any, are backed by measurements;
- required deployment automation is identified from experience rather than assumed.

---

## Step 10 — Real timing-device integration

Status: planned

### Purpose

Replace the synthetic edges proven in Step 5 with representative real timing hardware.
Because the application/domain flows already work, failures here can be isolated to
device contracts, electrical integration, drivers and adapter behaviour.

### Goal

Connect the required real timing devices to SI-01 on the selected target platform.

### Scope

Expected areas, refined from the Step-8 platform decision:

- RFID observations and lifecycle;
- CAN and CAN-connected devices where required;
- local display behaviour where selected;
- RTC integration where selected;
- keypad/other local controls where required;
- device status and useful recovery/error behaviour;
- comparison with the equivalent synthetic test flows.

### Needs

- selected target platform;
- representative RFID/CAN/display/RTC hardware as applicable;
- device/protocol information;
- synthetic scenarios retained as regression references.

### Result

- Real timing devices use normal SI-01 paths.
- Device status/recovery is observable.
- Synthetic and real flows remain comparable.

### Demo

- Run a representative real-device flow.
- Show timing data/results through the GUI.
- Demonstrate one device recovery case.

### Done

- implemented adapters use normal application/domain contracts;
- representative hardware behaviour is verified;
- synthetic tests remain usable for fast regression;
- unsupported hardware behaviour remains explicit.

---

## Step 11 — Integrated system and field proof

Status: planned

### Purpose

Bring the already-proven pieces together and learn what remains before treating the
system as an operational baseline. This is where integration/recovery gaps should surface;
it is not intended to reopen architecture choices that earlier steps already proved.

### Goal

Demonstrate the complete representative timing system as one integrated setup.

### Scope

- selected target platform and real timing devices;
- Desktop GUI Application;
- backoffice connection and outage/reconnect behaviour;
- persistence/restart and service recovery;
- useful operational logging/diagnostics;
- representative longer-running timing scenario;
- identify only the hardening work actually exposed by the integrated proof.

### Needs

- outputs of Steps 6-10;
- representative field/test setup;
- access to the required integration services.

### Result

- Representative integrated system works.
- Recovery paths are demonstrated.
- Remaining hardening work is evidence-based.

### Demo

- Run a representative timing session.
- Interrupt one external dependency/device.
- Recover and complete the session.

### Done

- integrated scenario is repeatable;
- important failure/recovery behaviour is visible and verified;
- unresolved operational work is recorded as concrete follow-up rather than speculative roadmap filler;
- a suitable software baseline/release is produced.

---

## Open / later possibilities

These remain options until an earlier step creates a concrete need:

- a small web client for exercising the Remote API;
- more elaborate image/update/rollback automation;
- a dedicated integration host;
- extra public/private extension proofs;
- a later Java runtime baseline;
- additional custom electronics beyond what Step 8 justifies.

## Planning rules

- Do as much useful software work as possible before requiring scarce hardware.
- Do not make the number of roadmap steps determine the project duration.
- Estimates describe effort; planning reserve covers uncertainty and should affect the
  forecast horizon.
- Keep original estimate, git-derived actual and remaining estimate distinct; use their
  differences as re-estimation evidence rather than treating them as time-accounting sums.
- Show at least one concrete end date per phase. Future calculated ends round up to the
  next Monday for presentation only; do not feed that rounded date into later forecasts.
- Explain why a step exists and what uncertainty/value it addresses.
- Name real dependencies/resources before they can become blockers.
- Keep roadmap Result/Demo short; put explanation in Purpose/Scope/Needs.
- Keep planning changes on the per-step detail card, not on the broad roadmap.

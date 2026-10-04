# Software Implementation Plan (SIP)

Status: working draft / non-authoritative


## Purpose

This document explains **how the software is expected to grow from the current application core
into a usable timing system**. The roadmap is intended for two audiences:

- a software engineer should be able to understand why the next increment exists, its
  boundaries, dependencies and exit criteria;
- a project reviewer/manager should be able to see what value or uncertainty the step
  addresses, which resources can block it, and what can be demonstrated afterwards.

The SIP is the content source of truth for roadmap step content and activity identity.
Each activity ID/title shown on a detailed step card is declared in the matching SIP step.
The per-step YAML owns only current activity state, dependencies, estimates and compact
card notes. Detailed activity history, CI logs and release mechanics live in issues, pull
requests, SDE and generated evidence.

## Terms and abbreviations

- **SIP** — Software Implementation Plan
- **D..** — documentation/design activity
- **A..** — application activity
- **V..** — verification activity
- **T..** — tooling activity


## Relationship to other documents

The SDP defines the project-wide development strategy and document conventions. The SIP
uses accepted product/design baselines plus the current implementation state to plan the
implementation sequence. It does not define product requirements or interface semantics.
SDE documents define the engineering environment; SVP/VTS define verification strategy
and cases; issues, pull requests and generated evidence record execution of the plan.

## How to read a step

Each step uses the same small structure, but the text should carry useful information
rather than merely fill headings:

- **Purpose** explains why the step is in this position and which value/risk it addresses.
- **Goal** states the capability to add.
- **Scope** says what work belongs in the step.
- **Not in this step** is used where a boundary prevents accidental scope growth.
- **Needs** names real dependencies or resources that can gate the work.
- **Activities** assigns stable activity IDs/titles used by the detailed SIP card. The
  matching YAML may add status/dependencies/notes but may not rename or invent activities.
- **Result** is the short manager-facing outcome shown on the roadmap.
- **Demo** is the practical end demonstration.
- **Done** is the engineering exit criterion.

Activity IDs are **local to one SIP step**. The prefixes are used consistently on
the SIP detail cards:

- `T..` — tooling / engineering-environment activity;
- `D..` — documentation or design/decision activity;
- `A..` — application/product implementation or integration activity;
- `V..` — verification activity.

For example, Step 3 `V03` and Step 4 `V03` are different activities. A suffix such
as `D02W` may preserve an inserted follow-up without renumbering already referenced
step-local activities.

The roadmap estimates are focused project days. Each step may show its original estimate,
git-derived actual effort and current remaining estimate. These are independent planning
signals: original minus actual does not have to equal remaining. Future phase ends are
shown as concrete Monday boundaries for readability; the underlying cumulative forecast
is calculated before that display rounding. Forecast dates are planning aids, not
commitments.


## Why the roadmap is ordered this way

The roadmap deliberately adds one new source of uncertainty at a time.

1. **Steps 1-3 establish the engineering and application shell.** Later work can then be
   tested through a real running application instead of through isolated classes only.
2. **Steps 4-5 establish local registration behaviour without external systems or real
   timing hardware.** Step 4 proves the durable registration boundary. Step 5 moves the
   input boundary outward to a simulated antenna and measures the runtime behaviour that
   this introduces.
3. **Steps 6-7 add external software around that local core.** The desktop GUI first proves
   that a real independent client can use the API. Backoffice integration then adds
   reference data, source synchronisation, multi-node operation and derived timing.
4. **Steps 8-10 move the proven software onto the target and replace simulated devices with
   real ones.** Platform, deployment and device problems are kept separate where possible.
5. **Step 11 combines the proven pieces in a representative field setup.**

A step should not claim behaviour that depends on a later step. In particular, simulated
input is not the same as a complete simulated event: backoffice-supplied reference data,
multi-node field simulation and real device integration have their own later steps.

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
- Timing Point Application boundary;
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
- application-core implementation can start without inventing basic ownership;
- unresolved subjects remain explicit rather than being presented as decisions.

---

## Step 2 — Application core repository skeleton

Status: completed

### Purpose

Move from architecture into executable software. A real repository, build and runnable
application provide the foundation on which every later domain, interface and device
increment can be verified.

### Goal

Create the Java repository and prove that it builds and runs independently.

### Scope

- Maven reactor with reusable application core and runnable application;
- Java baseline;
- build/version identity and logging baseline;
- unit tests and Linux/Windows CI;
- minimal application lifecycle.

### Needs

- development workstation;
- GitHub CI.

### Activities

| ID | Activity |
| --- | --- |
| `T01` | Java toolchain baseline |
| `T02` | Create tool.java-project |
| `T03` | Maven Wrapper fixture |
| `T04` | Pin Java 8 + Maven baseline |
| `T05` | Linux canonical CI |
| `T06` | Windows compatibility CI |
| `T07` | Canonical artifact + provenance |
| `T08` | Version reusable workflow |
| `A01` | Create SI-01 implementation repository |
| `A02` | Repository baseline files |
| `A03` | Maven reactor / artifact skeleton |
| `A04` | Package / responsibility boundaries |
| `A05` | Minimal runnable app lifecycle |
| `V01` | Generic fixture - Linux verify |
| `V02` | Generic fixture - Windows verify |
| `V03` | Canonical artifact smoke |
| `V04` | Clean-checkout consumer proof |
| `V05` | Architecture/dependency checks |
| `V06` | 0.1.0 release build / identity proof |

### Result

- Application-core and runnable application artifacts.
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

## Step 3 — Application and API foundation

Status: completed

### Purpose

Turn the application core into a useful long-running application before adding timing-domain
complexity. This step establishes the application boundary that later simulation, GUI,
backoffice and hardware work can all use without reaching into SI-01 internals.

### Goal

Build the first useful **Timing Point Application** (SI-01) on the development host.

### Scope

- external application configuration with at least one TimingNode;
- shared command/query behaviour;
- local console and remote shell;
- API over HTTP/JSON and WebSocket;
- consistent version/status semantics;
- runtime file logging;
- black-box/application testing;
- JavaFX engineering client for manual API integration testing.

### Not in this step

- real timing/domain behaviour beyond the minimum needed for the application shell;
- production timing hardware;
- the planned Desktop GUI Application (SI-02).

### Needs

- Windows development workstation;
- built SI-01 artifacts;
- no Raspberry Pi or timing hardware.

### Activities

| ID | Activity |
| --- | --- |
| `A01` | Shared application boundary + build identity |
| `A02` | Application configuration + minimal TimingNode |
| `A03` | Run until shutdown + graceful stop |
| `A04` | Local console |
| `A05` | Remote terminal / shell adapter |
| `A06` | API HTTP / JSON |
| `A07` | API WebSocket events |
| `A08` | Runtime logging + live diagnostics |
| `V01` | Shared behaviour + configuration unit tests |
| `V02` | Adapter equivalence checks |
| `V03` | ST-1 application behaviour black-box test |
| `V04` | Windows development-host execution proof |
| `V05` | Step-3 0.2.x release / identity proof |

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

## Step 4 — First registration-system slice

Status: active

### Purpose

Add the first real timing-domain behaviour only after the application/API shell is stable.
The main risk in this step is not RFID or backoffice integration; it is whether one
TimingNode can own lifecycle, identity, ordering and durable registration history without
those concerns leaking into clients or adapters.

Keeping the input deliberately simple makes that boundary testable before more sources of
failure are introduced.

### Goal

Operate one TimingNode through a controlled registration flow using the public
application boundary.

### Scope

- open a closed TimingNode with the requested `LocationId` as one ordered operation;
- close the TimingNode with explicit lifecycle rules;
- submit an already-accepted registration through an engineering input;
- let the TimingNode assign its own identity, location, sequence and recorded time;
- create immutable TimingData through the shared TimingData contract;
- append committed TimingData to local storage and rebuild the LogBook after restart;
- expose control, bounded history and live updates through IF-03;
- exercise the same public behaviour through the Development Client;
- verify the running application as a separate process.

### Not in this step

- antenna observations, RFID decoding or filtering;
- TagId-to-registration resolution;
- StageStartTimes, StageTiming or ranking;
- multi-TimingNode operation;
- backoffice transport or reference-data synchronisation;
- production timing devices;
- the product Desktop GUI Application.

### Needs

- the Step-3 application/API foundation;
- a deterministic engineering registration input;
- the reference TimingData codec/store;
- the Development Client as test tooling.

### Activities

| ID | Activity |
| --- | --- |
| `D01` | Development Client architecture + UI baseline |
| `D02` | Review first-registration operational use cases |
| `D02W` | Translate private compatibility behaviour |
| `D03` | Establish first TimingData + public control contracts |
| `V01` | Define deterministic first-slice examples |
| `A01` | TimingNode location and lifecycle |
| `A02` | Direct registration + TimingData |
| `A03` | Development Client first-slice control |
| `V02` | First-slice domain verification |
| `V03` | Automated first-registration black-box verification |
| `V04` | Development Client running-system demo |

### Result

- One TimingNode owns a durable, ordered registration stream.
- The same registration behaviour is available through the public API and Development Client.
- Restart rebuilds local registration history without inventing new records.

### Demo

- Open the TimingNode with a LocationId and submit one accepted registration.
- Observe the committed record in history and as a live update.
- Close, restart and confirm that the committed history is recovered.

### Done

- lifecycle and registration ownership rules have deterministic automated coverage;
- a registration cannot bypass TimingNode-owned identity, location, sequence or lifecycle;
- storage/recovery rebuilds the LogBook correctly;
- IF-03 exposes the required control, history and live update behaviour;
- a separate-process black-box test succeeds through IF-03;
- the Development Client can repeat the same flow without using private application state.

---

## Step 5 — Simulated antenna input and runtime behaviour

Status: planned

### Purpose

Move the test input one boundary closer to the real system without adding physical RFID
hardware yet.

Step 4 starts after tag interpretation: it injects an already-accepted registration.
Step 5 starts at the antenna side. A built-in `SimulatedAntenna` can therefore exercise
tag observation, filtering/resolution and registration admission through the same software
path that a later real antenna adapter must use.

This is also the first useful point to measure queueing, allocation and sustained-input
behaviour. Those measurements should guide implementation choices before target-hardware
constraints and device drivers make failures harder to isolate.

### Goal

Process repeatable simulated antenna input through one TimingNode using normal runtime,
domain and persistence paths.

### Scope

- built-in `SimulatedAntenna` through the normal Antenna interface;
- deterministic synthetic tag observations;
- tag interpretation/filtering needed to reach the accepted-registration operation;
- a small synthetic local reference fixture for TagId-to-RegistrationId resolution;
- define and implement TimingNode OPEN/CLOSE as committed TimingData in the same
  TimingNode-owned source stream as registrations;
- promote registration revoke/delete from reserved representation to supported
  TimingData/API behaviour, appending REV without rewriting the original registration;
- the same TimingNode commit, TimingData, LogBook and persistence path proven in Step 4;
- runtime counters/markers needed to understand queue wait, processing and persistence;
- sustained/bursty input tests and basic allocation/GC observations;
- restart/recovery while using the simulated input path;
- prove the typed provider/bootstrap mechanism with built-in and synthetic external providers.

### Not in this step

- production RFID hardware or proprietary reader protocols;
- backoffice delivery of RaceData or StageStartTimes;
- StageTiming, ranking or other results that need backoffice reference data;
- multi-TimingNode/full-field simulation;
- RabbitMQ or another production backoffice transport;
- product GUI work.

### Needs

- the Step-4 registration boundary;
- deterministic synthetic tag/reference fixtures;
- controllable simulated input;
- no target hardware and no private provider implementation.

### Activities

| ID | Activity |
| --- | --- |
| `D01` | Runtime execution and measurement plan |
| `D02` | Define OPEN/CLOSE TimingData semantics and reference mapping |
| `D03` | Define registration revoke semantics and public contract |
| `A01` | Simulated antenna and tag-processing path |
| `A02` | Runtime markers and counters |
| `A03` | Allocation and data-access strategy |
| `A04` | Commit OPEN/CLOSE through the normal TimingData path |
| `A05` | Commit registration revoke through the normal TimingData path |
| `V01` | Single-node load and burst characterization |
| `V02` | Sustained antenna-ingress fairness |
| `V03` | Restart and recovery with simulated input |
| `V04` | Provider bootstrap verification |
| `V05` | OPEN/CLOSE TimingData ordering, persistence and rejection verification |
| `V06` | Registration revoke/API/Development Client verification |

### Result

- Simulated antenna observations reach the normal registration path.
- Successful TimingNode OPEN/CLOSE transitions are represented in the normal committed
  TimingData source stream according to the Step-5 IF-05/IDD update.
- Registration revoke appends REV through the same committed source stream and leaves the
  original ADD history intact.
- Sustained input can be measured without bypassing TimingNode ownership.
- Restart/recovery works with the same simulated input path used by automated tests.

### Demo

- Open one TimingNode and show the committed OPEN TimingData record.
- Feed repeatable tag observations through `SimulatedAntenna` and show which observations
  become committed registrations.
- Revoke one registration and show ADD plus REV in the technical LogBook while the
  interpreted registration remains visible as DELETED.
- Close the TimingNode and show the CLOSE record in the same source sequence.
- Inspect the runtime counters, restart SI-01 and continue using the same simulated input
  configuration without sequence reuse.

### Done

- simulated antenna input uses the same public adapter/domain boundary intended for real antennas;
- accepted observations reach the existing durable registration path without a test-only domain bypass;
- successful OPEN/CLOSE transitions commit according to the Step-5 IF-05/IDD semantics
  without a second lifecycle record owner;
- rejected lifecycle requests do not create unintended TimingData records, and idempotent
  behaviour follows the explicit D02 decision;
- revoke never rewrites/removes committed ADD records and follows the explicit D03
  rejection/idempotence rules through API, LogBook, live event and recovery paths;
- sustained/bursty input has repeatable measurements and does not starve required TimingNode work;
- recovery preserves lifecycle/registration records and sequence continuity;
- provider loading is verified with public built-in/synthetic implementations.

---

## Step 6 — Desktop GUI Application

Status: planned

### Purpose

Introduce the first real operator-facing client only after SI-01 has stable state and
registration behaviour worth presenting.

Building the GUI here tests a different risk from Step 5: whether an independent
application can operate SI-01 using only the public API. Keeping it before backoffice
integration prevents broker/reference-data problems from being mixed with basic client
connection, stale-state and reconnect behaviour.

The Engineering Client remains test tooling and does not decide the product GUI technology.

### Goal

Create the first useful **Desktop GUI Application** (SI-02) as an independent API client.

### Scope

- choose GUI technology, runtime and packaging;
- select/connect to an SI-01 endpoint;
- show application and TimingNode status;
- show the registration/history data available from Steps 4-5;
- execute the supported operator controls;
- make connected, disconnected and stale state explicit;
- rebuild current state after reconnect;
- keep SI-02 independent from SI-01 internal classes and files.

### Needs

- stable IF-03 behaviour from Steps 3-5;
- representative running SI-01 test data;
- an explicit GUI technology decision when the step starts.

### Result

- A separate operator GUI can connect to and operate SI-01 through the public API.
- Connection loss and stale state are visible instead of being hidden.
- SI-02 remains independently buildable from SI-01.

### Demo

- Connect SI-02 to a running SI-01 and operate one TimingNode.
- Show current status and registration history/live updates.
- Disconnect, reconnect and rebuild the current view.

### Done

- SI-02 and SI-01 build independently;
- normal operation uses only public SI-01 interfaces;
- connection/reconnect/stale-state behaviour has useful automated coverage;
- the GUI technology and packaging choice are documented with their rationale.

---

## Step 7 — Backoffice and multi-node integration

Status: planned

### Purpose

Add external reference data and source synchronisation while the whole setup can still run
on development machines.

This is the right point to add multi-TimingNode operation: independent node streams and
routing become important when reference data and committed timing data move between SI-01
and a backoffice test setup. It also provides the missing inputs for StageTiming. Doing
this before target/hardware bring-up keeps protocol, routing and reconciliation failures
separate from physical-device problems.

### Goal

Run a representative multi-node SI-01 setup that exchanges reference/timing data with a
reproducible backoffice test environment.

### Scope

- receive and apply synthetic/public RaceData and StageStartTimes;
- resolve RegistrationId to TeamID for interpreted/operator views where RaceData provides
  that relation, without changing committed TimingData identity;
- resolve the reference data needed for local timing calculations;
- add StageTiming/derived timing behaviour that depends on those references;
- send committed TimingData/results upstream as required by the promoted contract;
- host and address multiple independent TimingNodes in one process;
- keep node lifecycle, sequence, history and reference state isolated;
- exercise a representative multi-node test topology rather than a special simulation bypass;
- handle disconnect, reconnect and required reconciliation/recovery;
- select and test the concrete development transport(s), including RabbitMQ when that contract is ready;
- exercise the typed `UpstreamProtocol` provider boundary using public test implementations.

### Needs

- Steps 4-6 local behaviour and public interfaces;
- backoffice semantic/interface information;
- synthetic/public reference data and identities;
- reproducible broker/socket test infrastructure where required.

### Result

- Multiple TimingNodes keep independent state and ordered data streams.
- Reference data can be received and used for local derived timing and TeamID
  interpretation.
- Local registration continues through a backoffice outage and synchronisation can resume.

### Demo

- Start a small multi-node SI-01 test setup and load reference/start-time data.
- Feed simulated registrations and inspect node-specific derived timing and outbound data.
- Interrupt the backoffice service, continue local work, reconnect and reconcile.

### Done

- multi-node addressing and state isolation have repeatable automated coverage;
- reference-data application and derived timing use explicit domain ownership;
- outbound source identity/order remain intact across the selected transport;
- outage/reconnect behaviour is repeatable and does not stop required local registration;
- transport-specific details remain outside the generic domain contracts.

---

## Step 8 — Target platform decision

Status: planned

### Purpose

Choose the physical target only after the main software flows and their runtime shape are
understood.

A Raspberry Pi Zero-class system is a working direction, not a decision that should force
the design without evidence. By this point the project can compare candidate hardware
against a real application, known interfaces and measured workload instead of against a
speculative feature list.

### Goal

Select the target platform and identify what must be bought or built for target bring-up.

### Scope

- candidate compute platform availability and lifecycle risk;
- supported OS and Java runtime;
- memory, storage, networking and power needs;
- RTC requirement and options;
- CAN controller/transceiver requirements;
- local display/keypad/beeper connection needs where applicable;
- GPIO/connectors and serviceability;
- off-the-shelf stack versus carrier/HAT/custom PCB;
- rough prototype BOM/assembly cost where a custom board solves a real problem.

### Needs

- measured software/runtime behaviour from Step 5;
- known external/device needs from the preceding software work;
- current candidate-board/module information and prices.

### Result

- One target-platform direction is selected with its main risks understood.
- Required prototype hardware and any custom-board need are explicit.
- Step 9 can start without reopening the basic platform choice.

### Demo

- Compare the credible platform options against the known software/device needs.
- Show the selected hardware block diagram.
- Show the prototype parts/cost path and remaining platform risks.

### Done

- target direction and rationale are recorded;
- required hardware/features and procurement risks are explicit;
- off-the-shelf versus custom-board choice is justified;
- the next target prototype can be ordered or assembled.

---

## Step 9 — Target bring-up and deployment proof

Status: planned

### Purpose

Prove the software stack on the selected target before adding real timing devices.

Step 5 characterises software behaviour on a controlled development host. Step 9 answers a
different question: whether the selected target has enough real CPU, memory, storage and
runtime headroom, and whether deployment/restart can be made repeatable.

### Goal

Run the representative SI-01/SI-02 software stack on the selected target platform.

### Scope

- acquire/assemble and provision the selected target;
- install the chosen OS and Java runtime;
- deploy and start SI-01;
- connect through the public API and SI-02;
- repeat representative Step-5/7 workloads on the target;
- record startup, memory, CPU, thread, storage and restart observations;
- tune deployment/runtime settings only where measurements justify it;
- decide which update/deployment automation is actually useful.

### Needs

- Step-8 platform decision and prototype hardware;
- representative SI-01/SI-02 builds;
- the repeatable software workloads established earlier.

### Result

- SI-01 runs repeatably on the selected target.
- Target resource limits are based on measurements rather than desktop assumptions.
- The deployment/start/restart path is known before device integration begins.

### Demo

- Boot/provision the target and start SI-01.
- Connect SI-02 and run a representative simulated/reference-data workload.
- Show target measurements and a clean restart.

### Done

- target execution and restart are repeatable enough for continued development;
- OS/runtime/install choices are recorded;
- important target limitations are backed by measurements;
- deployment/runtime tuning is based on observed need.

---

## Step 10 — Real timing-device integration

Status: planned

### Purpose

Replace the simulated device edges with representative real hardware after the target and
software paths are already proven.

This keeps hardware/protocol faults local to adapters and electrical/device integration.
A real device should feed the same domain path that its simulated counterpart already
exercised; device integration must not create a second timing architecture.

### Goal

Connect the required real timing devices to SI-01 on the selected target platform.

### Scope

Refine the exact list from the Step-8 platform decision, including as required:

- RFID reader/antenna observations and device lifecycle;
- CAN and CAN-connected devices;
- local display behaviour;
- RTC;
- keypad and other local controls;
- device status, reconnect/reset and useful error reporting;
- extension-provided Antenna/CAN/display protocol implementations behind the public provider contracts;
- regression comparison with the equivalent simulated paths.

### Needs

- target platform proven in Step 9;
- representative RFID/CAN/display/RTC hardware as applicable;
- device/protocol information;
- simulated scenarios retained as reference tests.

### Result

- Real devices feed the same application/domain paths already proven with simulation.
- Device health and recovery are observable.
- Simulated tests remain usable as the fast regression baseline.

### Demo

- Run a representative real-device registration/input flow.
- Observe the resulting state/data through SI-02.
- Disconnect or reset one device and demonstrate the supported recovery behaviour.

### Done

- implemented adapters use normal application/domain contracts;
- representative real-device behaviour is verified;
- the equivalent simulated tests still pass;
- unsupported hardware behaviour is explicit rather than hidden in generic code.

---

## Step 11 — Integrated system and field proof

Status: planned

### Purpose

Combine the pieces only after their main failure modes have been tested separately.

The purpose is not to invent another architecture or add speculative hardening. It is to
run a representative system long enough to expose integration, operational and recovery
problems that only appear when target hardware, real devices, GUI and backoffice are used
together.

### Goal

Demonstrate a representative timing system as one integrated setup and turn observed gaps
into concrete follow-up work.

### Scope

- selected target platform and real timing devices;
- Desktop GUI Application;
- backoffice connection plus outage/reconnect behaviour;
- persistence and restart/service recovery;
- operational logging/diagnostics;
- representative longer-running timing session;
- recovery from selected external/device failures;
- record only hardening work exposed by the integrated proof.

### Needs

- completed outputs of Steps 6-10;
- representative field/test setup;
- required integration services.

### Result

- The representative integrated setup can run and recover from selected failures.
- Operators can observe the important system state through normal interfaces.
- Remaining hardening work is based on field/integration evidence.

### Demo

- Run a representative timing session from input through GUI/backoffice.
- Interrupt one external dependency or device.
- Recover and finish the session without losing committed timing history.

### Done

- the integrated scenario is repeatable;
- selected failure/recovery behaviour is visible and verified;
- unresolved operational work is recorded as specific follow-up items;
- a suitable software baseline/release is produced.

---

## Open / later possibilities

These remain options until an earlier step creates a concrete need:

- a small web client for exercising the API;
- more elaborate image/update/rollback automation;
- a dedicated integration host;
- additional extension families beyond the planned TimingData, UpstreamProtocol, Antenna, CAN-protocol and display-protocol provider boundaries;
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

# Software Implementation Planning (SIP)

Status: working draft / non-authoritative

This is the implementation roadmap for the event-timing software. It is structured
enough to keep the project understandable, but each step should also explain **why** it
exists and what is needed to perform it.

This SIP is the content source of truth for the generated roadmap and step cards.

## Step format

Each step contains:

- **Why** — the reason for doing the step now;
- **Goal** — what capability the step should add;
- **Scope** — the main work;
- **Needs** — concrete resources/environment when relevant;
- **Result** — what should exist afterwards;
- **Demo** — a practical way to show it works;
- **Done** — enough to close the step.

Detailed task history, CI logs and release mechanics stay in issues, PRs, SDE and
generated evidence.

---

## Step 1 — Architecture baseline

Status: completed

### Why

Start implementation with shared names and boundaries instead of inventing them inside
the first coding changes.

### Goal

Define enough architecture to start implementation deliberately.

### Scope

- domain and TimingNode baseline;
- Headless Timing Application boundary;
- first interfaces and verification direction;
- Java/Maven and repository direction.

### Needs

- current project/domain knowledge;
- architecture/document tooling.

### Result

- Architecture baseline for the first implementation.
- TimingNode, application and interface boundaries are clear.
- Build/test direction is ready.

### Demo

- Walk through the architecture diagrams.
- Explain TimingNode and application boundaries.
- Show how the first executable fits the architecture.

### Done

- architecture documents build and are reviewable;
- framework implementation can start without inventing basic ownership;
- unresolved subjects are explicitly open.

---

## Step 2 — Framework repository skeleton

Status: completed

### Why

A real repository/build proves more than another round of architecture text and gives all
later work a stable place to land.

### Goal

Create the Java repository and prove that it builds and runs independently.

### Scope

- Maven reactor with framework and runnable application;
- Java baseline;
- build/version identity and logging baseline;
- unit tests and Linux/Windows CI;
- minimal application lifecycle.

### Needs

- development workstation;
- GitHub CI.

### Result

- Reusable framework JAR and runnable application JAR.
- Clean build/test on Linux and Windows.
- Traceable build identity and lifecycle.

### Demo

- Build from a clean checkout.
- Produce both artifacts.
- Start the application, show its version and stop it.

### Done

- clean bootstrap/build works;
- Linux and Windows verification are green;
- release `v0.1.0` is the accepted Step-2 baseline.

---

## Step 3 — Minimal application on development host

Status: active

### Why

Before adding real hardware or target deployment, SI-01 needs to become a useful
long-running application whose public interfaces can be exercised independently.

### Goal

Build the first useful **Headless Timing Application** (SI-01) on the development host.

### Scope

- external application configuration with at least one TimingNode;
- shared command/query behaviour;
- local console and remote shell;
- Remote API over HTTP/JSON and WebSocket;
- version/status consistency across those interfaces;
- runtime file logging;
- black-box/application testing;
- current JavaFX engineering client for manual integration testing.

The JavaFX client is not the planned Desktop GUI Application (SI-02).

### Needs

- Windows development workstation;
- built SI-01 artifacts;
- no Raspberry Pi or production timing hardware required yet.

### Result

- SI-01 starts from external configuration.
- Console, shell and Remote API expose consistent version/status.
- Automated and manual black-box testing are possible.

### Demo

- Start SI-01 on Windows from configuration.
- Inspect version/status through the public interfaces.
- Use the JavaFX engineering client to inspect the Remote API.

### Done

- configuration drives application composition;
- initial presentation interfaces use shared application behaviour;
- ST-1 exercises the running application through public interfaces;
- runtime logging and Windows artifact execution are repeatable;
- the step closes on the next accepted `0.2.x` release.

---

## Step 4 — Raspberry Pi target proof

Status: planned

### Why

The Pi Zero/Zero W is a target, but we should measure real behaviour instead of assuming
in advance that Java, memory or CPU will be a problem.

### Goal

Run the representative SI-01 application on a real Raspberry Pi target.

### Scope

- choose/provision a suitable OS and Java runtime;
- deploy and start SI-01;
- use the existing Remote API for basic remote inspection;
- record simple startup/CPU/memory observations;
- determine what deployment automation is actually useful.

### Needs

- original Raspberry Pi Zero / Zero W;
- suitable storage, power and network connection;
- representative SI-01 build.

### Result

- SI-01 runs on the Pi target.
- Basic target measurements are available.
- Real deployment needs are known rather than guessed.

### Demo

- Start SI-01 on the Pi.
- Query version/status remotely.
- Show runtime measurements and deployment.

### Done

- target execution is repeatable enough for development;
- selected Java/runtime setup is recorded;
- any actual target limitation is documented with evidence.

---

## Step 5 — Desktop GUI Application

Status: planned

### Why

A real independent GUI is both useful to operate the application and a strong proof that
the Remote API is a usable external contract.

### Goal

Create the planned **Desktop GUI Application** (SI-02) as a separate Remote API client.

### Scope

First increment only:

- endpoint selection and connect/disconnect;
- version and basic application/TimingNode status;
- clear connected/disconnected/stale state;
- reconnect behaviour;
- no dependency on SI-01 internal classes/files.

The GUI technology, runtime and packaging are deliberately still open. The current
JavaFX engineering client does not decide this technology.

### Needs

- development workstation;
- stable enough Remote API from SI-01;
- a technology choice made when this step starts.

### Result

- Independent GUI application using only the Remote API.
- Basic SI-01 status visible through the GUI.
- GUI technology is chosen explicitly.

### Demo

- Connect the GUI to a running SI-01.
- Show version/status and disconnect/reconnect.
- Point the same GUI at a local or Pi-hosted SI-01.

### Done

- GUI and SI-01 build independently;
- connection/status behaviour has useful automated coverage;
- implementation technology is documented with its reason.

---

## Step 6 — TimingNode data and timing behaviour

Status: planned

### Why

Once the application/runtime boundary is stable, the next value comes from the timing
behaviour itself rather than more infrastructure.

### Goal

Implement the useful local TimingNode/domain behaviour without depending on production
hardware.

### Scope

- registrations and source sequence/history;
- StageStartTimes;
- NextUpTeams;
- RaceData/reference data;
- StageTiming and derived timing results;
- persistence/restart/restore where needed by this state.

### Needs

- synthetic test data;
- no production RFID/CAN hardware required for the first implementation.

### Result

- Useful timing/domain state and behaviour.
- Timing calculations work with deterministic inputs.
- Required state survives restart where designed.

### Demo

- Feed synthetic registrations.
- Update start/team/reference data.
- Show a derived timing result and restart/restore behaviour.

### Done

- core state transitions and timing rules have deterministic tests;
- behaviour can be exercised without real devices;
- persistence needs are implemented for the chosen state.

---

## Step 7 — Device integration

Status: planned

### Why

After the domain behaviour works with controlled inputs, real device adapters can be
connected without using hardware to define the business logic.

### Goal

Connect the required timing devices to SI-01.

### Scope

Expected device areas include:

- RFID observations and lifecycle;
- CAN/keypad;
- displays where required;
- controllable stubs/simulators where they help development;
- real-device recovery/error behaviour as it becomes known.

Exact adapter order depends on available hardware and project need.

### Needs

- representative RFID/CAN/display hardware for the adapters being implemented;
- protocol/device information;
- synthetic/stub equivalents where useful.

### Result

- Real devices use normal SI-01 paths.
- Device failures are observable and recoverable where supported.

### Demo

- Run SI-01 with representative selected hardware.
- Show a normal device flow.
- Demonstrate one useful recovery/failure scenario.

### Done

- implemented adapters use the normal application/domain contracts;
- representative hardware behaviour is verified;
- unsupported or still-open device behaviour is documented rather than guessed.

---

## Step 8 — Backoffice integration

Status: planned

### Why

Backoffice synchronisation should be added after local operation is useful, so local
timing behaviour does not become dependent on the external transport.

### Goal

Connect SI-01 to the required backoffice data flows.

### Scope

- reference/input data needed locally;
- outbound registrations/results as required;
- source identity/order where relevant;
- disconnect/reconnect/recovery behaviour;
- concrete transport adapter(s) when the external contract is known.

### Needs

- backoffice/interface information;
- broker/test environment if RabbitMQ is the selected transport;
- synthetic test data and credentials/configuration.

### Result

- Required data can move between SI-01 and the backoffice.
- Local operation continues as designed during an outage.
- Transport details remain outside domain behaviour.

### Demo

- Exchange representative data.
- Interrupt the connection.
- Continue the applicable local flow and reconnect cleanly.

### Done

- implemented backoffice flows have integration tests;
- disconnect/reconnect semantics are explicit;
- transport/proprietary details do not leak into generic domain APIs.

---

## Open / later possibilities

These are **not roadmap commitments** yet:

- a small web client for exercising the Remote API;
- more elaborate target-image/update automation;
- a dedicated integration host;
- extra private/public extension proofs;
- Java 11 or another later runtime baseline;
- further operational/deployment hardening.

Promote one of these into a SIP step only when there is a concrete reason to do it.

## Planning rules

- Keep steps small enough to remain understandable between work sessions.
- Explain why a step exists; do not turn a list of possible future ideas into a roadmap.
- Record real resource needs under **Needs**.
- Measure target behaviour before inventing performance constraints.
- Keep the SIP as the source for generated roadmap/card content.

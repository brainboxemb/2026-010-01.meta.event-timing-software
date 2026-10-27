# Engineering Client development and UI baseline

Status: working engineering baseline

Software item: **SI-02 — Engineering Desktop Client**  
Implementation location: `test-client/` in `2026-010-02.java.timing-point-application`


## Purpose

The Development Client is the project's interactive development, integration and
diagnostic application for exercising the public boundaries of the **Timing Point
Application** (SI-01).

It is deliberately **not**:

- the normal field/operator interface; that role belongs to IF-04 Web;
- part of the Java-8 SI-01 runtime;
- an owner of timing/domain state;
- a shortcut that may mutate SI-01 internals directly.

The current implementation is a standalone Java 21 / JavaFX 21 Maven application using
BentoFX 0.16.0 for workbench composition. It remains in the same implementation repository
as SI-01 because its public-interface integration evolves together with SI-01. Repository
co-location does not make it part of the SI-01 software item.

## Terms and abbreviations

- **SDE** — Software Development Environment
- **IF-03** — API interface
- **SI-01** — Timing Point Application


## Relationship to other documents

This SDE defines the Engineering Client development environment, technology and
workbench composition baseline. The maintainable presentation/interaction rules live
in [44-02-GPD](44-02-GPD-engineering-client-design-rules.md).
The software-item requirements and architecture authority is the SI-02 SSD (41-02). Normal operator behaviour and public contracts
remain owned elsewhere:

- IF-03 API semantics are owned by `32-03-ISD-application-control-status.md`;
- normal browser/operator behaviour is owned by UC-001/UC-002 and IF-04;
- IF-06 backend/upstream semantics will be owned by the applicable system ISD;
- SI-01 domain architecture remains owned by `41-01-SSD-timing-application-specification-document.md`;
- transport implementation belongs in the applicable SI-01 SDD;
- the Development Client implementation README owns concrete build/run instructions.

This document defines the SI-02 engineering/UI implementation baseline. IF-03 routes,
payloads, capability semantics and failure codes remain authoritative in
`32-03-ISD-application-control-status.md`; SI-02 conforms to that contract rather than
redefining it.

## Product and operator boundary

The Engineering Client is intentionally a rich desktop engineering tool. It may expose
raw protocol data, negative-path operations, simulation controls, Remote Shell, device
logs, client logs and other diagnostics that are useful during development and
commissioning.

Normal field operators use the browser-facing IF-04 Web Interface. The project does not
maintain a second restricted/safe desktop operator application merely to duplicate that
path.

This distinction is behavioural rather than an excuse to duplicate application
semantics:

- SI-01 remains authoritative for timing/domain state;
- the Engineering Client uses supported public boundaries;
- IF-04 and the Engineering Client may present different workflows for different users
  while relying on the same underlying SI-01 semantics.

## Repository and runtime boundary

Current placement:

```text
2026-010-02.java.timing-point-application/
├── core/            SI-01 reusable Java-8 application core
├── app/             SI-01 executable
├── system-test/     separate-process verification
├── shared/timing-data/ shared TimingData model + codec/provider SPI
└── test-client/     SI-02 Engineering Desktop Client
                    standalone Java 21 + JavaFX 21 + BentoFX application
                    no SI-01 core/app implementation dependency
```

For live SI-01 operation the Development Client communicates only through
supported external interfaces. It does not import `timing-point-core` or
`timing-point-app` implementation classes.

TimingData inspection/conversion is a separate engineering capability. The
Development Client may depend on the small shared `event-timing-data` artifact and
load the same compatible `TimingDataProvider` implementations that SI-01 can
use, without copying provider-specific decoding rules into client code.

Keeping it in the same repository is intentional while interface changes and
development-client changes normally belong to the same development increment. A
separate repository becomes useful only when evidence shows an independent release
cycle, independent ownership, substantial external reuse, or lower coordination cost
from splitting it.

## Step 6 desktop technology baseline

Step 6 D02 selects the following target baseline for the Engineering Desktop Client:

| Concern | Selected baseline |
| --- | --- |
| Language/runtime | Java 21 |
| UI toolkit | JavaFX 21 |
| Workbench | BentoFX 0.16.0 |
| Required styling | application-owned JavaFX CSS |
| Optional theme layer | Transit may be used where it adds value; it is not architecture-critical |
| HTTP/JSON | JDK `java.net.http.HttpClient` |
| WebSocket | JDK `java.net.http.WebSocket` |
| JSON | Jackson |
| Build | Maven |
| First Windows distribution | self-contained `jpackage` application image |
| Module model | classpath/non-JPMS initially |

This baseline is implemented in `test-client` through Java PR #402. The application
uses an instance-scoped `EngineeringSystemContext` for one connected SI-01 target,
keeps the functional JavaFX panes independent from BentoFX APIs and composes those panes
through the BentoFX workbench. Linux CI verifies the standalone client and Windows CI
builds the self-contained `jpackage` app-image. Step 6 V01 verifies the real SI-02
revoke/recovery GUI behaviour against SI-01.

### Development launch boundary

The checked-in NetBeans Run/Debug actions execute SI-02 in a **separate child JVM**
through Maven `exec:exec`. They do not use Maven's in-process `exec:java` goal.
The child executable is resolved from `${java.home}/bin/java`, so the Engineering
Client uses the same Java 21-capable JDK that successfully builds its `release=21`
code. The action supplies the runtime Maven classpath and enables long-classpath
handling for Windows.

Debug launch attaches NetBeans to that child JVM through its JDWP listener/address.
Maven, JGit and ForkJoin build-tool threads therefore belong to the Maven process and
are not part of the SI-02 runtime thread model. This development launch separation does
not change the production/distribution model: the Windows `jpackage` app-image remains
the deployment baseline.

### NetBeans Maven repository indexing

The NetBeans Maven repository index is an **IDE convenience cache**, not part of
the project build or Maven dependency-resolution contract. The project does not
require a complete local Maven Central index to build, test, run or debug SI-01
or SI-02. Maven continues to resolve declared dependencies from the configured
repositories when IDE repository indexing is disabled.

For this development environment the preferred setting is therefore:

```text
Tools > Options > Java > Maven > Indexing
    repository indexing: disabled
```

The wording can vary slightly between NetBeans releases; the Maven output window
can also provide a settings action that opens the same Maven options panel.

Disabling the index may reduce IDE-only artifact search/completion over the full
remote repository. Already declared project dependencies, the local Maven
repository and ordinary Maven builds remain usable.

A message such as **"Unpacking index for Central Repository"** refers to the
NetBeans copy of the Maven Central metadata index; it does not mean the complete
Maven Central artifact repository is being downloaded. A full index rebuild can
occur after an IDE upgrade or cache replacement. If it appears repeatedly in
normal day-to-day use, verify that repository indexing has not been re-enabled
before treating the behaviour as a project or Maven build problem.

### Decision rationale

The decision deliberately builds on qualified project evidence rather than introducing a
second desktop technology stack.

**Java 21 / JavaFX 21** are selected because the existing client, its protocol and
synchronisation services and Experiment 008 already establish the required desktop
behaviour. A .NET, Compose or desktop-web implementation would add another language,
runtime/build toolchain and duplicate client integration without a demonstrated
compensating benefit.

**BentoFX 0.16.0** is selected because the Engineering Client genuinely benefits from a
dockable engineering workbench: logs, terminal, controls, registrations, technical
LogBook and raw inspection are useful simultaneously and across flexible layouts.
Experiment 008 preferred BentoFX to SnapFX because BentoFX's explicit
root/branch/leaf model produced clearer application composition, needed less corrective
adapter/presentation code and resolves through the normal Maven Central path. Plain
JavaFX remains a viable fallback if docking later stops providing useful engineering
value.

BentoFX does not make layout persistence an application/domain contract. Persisted
workbench layout, if later useful, is application-owned desktop state and may be added
without changing the view/service boundary.

The existing **JDK HTTP/WebSocket client plus Jackson** remains the selected IF-03
implementation approach. D02 found no concrete protocol gap that justifies another
HTTP/WebSocket dependency.

The first packaging target is a self-contained Windows **`jpackage` app-image**. This
avoids requiring a separately installed JRE while keeping the first distribution step
smaller than an installer/update programme. MSI/WiX, automatic update and rollback are
added only when a deployment need justifies them.

The client remains **non-modular/classpath-based initially**. Experiment 008's JavaFX
unnamed-module warning is not sufficient reason to introduce JPMS by itself. A module
path/runtime-image change should be driven by a packaging, dependency or maintainability
benefit.

### Application/service boundary

D02 also fixes the service boundary used by the workbench and client-side automation:

```text
JavaFX / BentoFX views ----+
                           |
Lua scripting -------------+--> client/application services --> public SI-01 interfaces
                           |
tests / fakes -------------+
```

Connection/session lifecycle, baseline synchronization, live-event buffering and
state synchronization, command execution, raw-message context and target/system state belong in
client/application services rather than JavaFX event handlers or docking objects.

A connected timing system is modelled as an **instance-scoped client context**, not as
global UI state. The current workbench presents one primary system, while the same
boundary allows the Lua adapter and later multi-system engineering workflows to reuse
client/application services without automating JavaFX controls. Scripts are a generic
tool beside Terminal rather than a Node Controls tab. They may reset the SI-02 client,
connect/disconnect Events or the Central upstream role, inspect boundary state and wait
for a bounded state transition. An intentional disconnect never cancels the script that
requested it.

## Component architecture

<a id="fig-sde03-01"></a>
![Development Client architecture](../../../raw/prod/docs/assets/architecture/engineering-client.svg)
*Figure SDE03-01 — Development Client UI, independent client services and SI-01 engineering boundaries.*

The JavaFX event handlers remain presentation code. Network/protocol work is kept in
small independent client services so the UI does not become the owner of IF-03, shell or
logging protocol semantics.

The current principal services are:

| Service | SI-01 boundary | Role |
| --- | --- | --- |
| `ClientConfig` | local file | target host, per-boundary ports and Development Client presentation/logging settings |
| `ApiClient` | IF-03 HTTP/JSON | version/status queries and supported commands/test control |
| `ApiEventClient` | IF-03 WebSocket | status/event snapshots and live event inspection; in `role=upstream` mode the same connection is full-duplex for ST-2 UpstreamData |
| `RemoteShellClient` | Remote Shell | line-oriented engineering terminal |
| `LiveLogClient` | `LoggingServer` | SI-01 live diagnostic records and temporary runtime log-level control |
| `CentralSystemSimulator` | IF-06 semantic model | Central-owned RaceData sequence/replay state and ACK/REQ/SYNC/PING behavior, independent of concrete transport |
| `ClientLog` | local runtime | Development Client startup/configuration/connection/request/error logging and local log presentation |

The IF-03 HTTP and WebSocket client services share one process-wide JDK
`HttpClient` transport. Repeated UI actions may create short-lived request
objects, but they must not create a new JDK HTTP selector/worker thread group
for every operation.

The Development Client's own asynchronous request worker is named
`dc-request`. JDK-owned transport threads keep their native `HttpClient-*`
names; seeing one stable group is expected, while a new numbered group for
every UI action indicates accidental transport recreation.

The Development Client exposes the capability-gated IF-03 engineering operation for
direct injection of an **already accepted semantic registration**. That control enters
the normal TimingNode registration operation after antenna/decoding/filtering and is
therefore explicitly **not** antenna simulation.

A separate capability-gated simulated-tag control starts a named passage profile before
the antenna-observation boundary. The Development Client requests only the
RegistrationId and profile; SI-01 resolves the configured EventData tags and drives:

```text
SimulatedTag / profile
  -> SimulatedAntenna
  -> AntennaManager
  -> TagProcessor
  -> TimingNode
```

When exercising a running SI-01 through IF-03, the Development Client does not construct
committed TimingData directly and does not choose the TimingNode-owned source identity,
active location or sequence.

For offline/import/export/compatibility inspection, the Development Client may
decode or encode TimingData through the shared TimingData API/provider boundary.
That capability does not make the client an owner of live SI-01 domain state.

Backend/upstream simulation is a separate Engineering Client capability built around
shared `UpstreamData`. One `CentralSystemSimulator` owns Central-side semantic state;
transport is below that model.

For ST-2, the existing `ApiEventClient` is opened at
`/api/v1/events?role=upstream`. That one WebSocket is full-duplex: it receives the
ordinary STATUS_SNAPSHOT/live-event stream and sends/receives semantic UpstreamData.
The status snapshot/change stream is also the Central simulator's authority for the
running TimingNode's current OPEN/CLOSED and LocationId state. TIMING_DATA remains
durable LogBook history; a historical unmatched NODE_OPEN after SI-01 restart never
restores runtime OPEN state in the simulator. No HTTP injection route and no second
SI-02 WebSocket service is used.

For ST-3, the same simulator model later receives a RabbitMQ Central-System transport.
RabbitMQ queue/channel/broker mechanics do not leak into the simulator's RaceData,
RECV/SEQ or PING state.

## Current UI baseline

SI-02 is an **API-first engineering workbench**, not a restricted field/operator
desktop GUI. The SI-02 [Design Rules (44-02-GPD)](44-02-GPD-engineering-client-design-rules.md)
define the selected **flat Windows desktop style**, pane responsibilities,
threading/refresh principles and acceptance path. This SDE owns the technology
and composition baseline, not a second set of visual styling rules.

### Workbench and controls

The layout is composed through BentoFX docking leaves:

| Workbench area | Selected view responsibility |
| --- | --- |
| Systems Explorer | Available TimingNodes and actual status/location/problems, Sync view action |
| TimingNode / API / Registration / Simulation / Scripts tabs | Engineering commands, API version/status, manual/direct registration, simulated tags and client-side Lua |
| Registrations | Interpreted current/open location data (or operator-selected All) |
| LogBook | Committed source history, sequence and raw-record inspection |
| Raw Data / Events | Unmodified API JSON and received WebSocket event JSON |
| Backend | Central System Simulator controls/state: packetNr/RECV delivery, send RaceData changes, SEQ/PING, TimingData replay requests and raw UpstreamData |
| Device Log / Terminal / Client Log | Independent device diagnostics, shell and local client diagnostics |

Permanent tabs are not closable. The standard BentoFX `≡` menu owns tab
position and docking-back operations; `▼` appears when tabs overflow. Empty
leaves can be pruned without leaving a blank column, and View → Reset layout
restores the default dock arrangement without changing SI-01.

Registrations defaults to the currently **OPEN LocationId** of the selected
TimingNode; its header shows `Registrations [LocationId]`,
`Registrations [All]` or `Registrations [–]` when the current location
cannot be relied upon. The BentoFX `≡` menu selects current/all directly.
The selected location, scope, scroll position and dock state are presentation
choices, not new TimingNode domain state.

The toolbar has **Host / Connect–Disconnect / API / Events / Terminal /
Device Log** on one aligned row. API uses a stateless reachability check;
Events, shell and device log use independent persistent connections. A
primary Connect/Disconnect action coordinates those three stateful links;
its color reflects actual connected/partial/disconnected state. Client Log
remains usable offline and needs no connection status button.

### Synchronisation and commands

A freshly started client does not connect automatically. While Events are
disconnected or a baseline is being reconstructed, the Timing view is
NOT SYNCED, SYNCING or STALE and controls that depend on reliable source
state stay disabled. Initial baseline and overlapping committed live
records are merged by stable identity before presenting **LIVE**.
The client does not manufacture SI-01 TimingData from an HTTP command outcome.

UI handlers initiate operations through client/application services.
Blocking I/O is not performed on the JavaFX Application Thread. All source
updates are applied on the FX thread, with obsolete async results discarded
after target/node changes and meaningful UI changes applied idempotently.
The [44-02-GPD](44-02-GPD-engineering-client-design-rules.md) owns concrete
visual/interaction and async presentation review guidance.

### Data/time and technical views

Engineering Client viewer/table timestamps are presented in the host's local
timezone. This includes Registrations, Node/Central LogBook Effective/Recorded,
Central Messages Time/Received, Events and HTTP timestamps. Raw IF-03/IF-05/IF-06
payloads remain unchanged canonical UTC and are the protocol evidence surface.

For Central Messages, TIMING_DATA **Time** comes from IF-05 effective `time`; when one
message carries multiple records, the last record in retained source order supplies
that row's Time. Optional `recTime` remains diagnostic metadata and does not drive the
normal Time column. **Received** remains the separate local WebSocket receive timestamp.
Other message families retain their own source/message timestamp semantics.

A blank trailing table row is **presentation-only** follow-latest state: selecting it
follows new records; inspecting older records pauses automatic follow.

Direct auto-registration is an IF-03 injection of an already accepted
registration and **bypasses** the antenna processing path. Simulated tags
exercise the antenna observation path separately. Device Log receives source
`LoggingServer` messages, Terminal is an independently connected shell,
and Client Log remains local and usable while SI-01 is offline.

### Client-side automation with Lua

SI-02 includes a **Scripts** tab and packages LuaJ only in the Engineering Client
module. The script adapter calls the same client/application services and public IF-03
boundary as the GUI; it does not automate JavaFX controls and does not run in SI-01.

This SDE records only that development/runtime boundary. The supported Lua facade,
worker/cancellation model and safety design are owned by
[43-02-SDD-01](43-02-SDD-01-lua-scripting-design.md). Practical script loading,
Run/Stop use, examples and troubleshooting are owned by
[70-02-SUM](70-02-SUM-engineering-client.md).

## Capability-driven engineering controls

The Development Client must not assume that engineering simulation controls are available
in every SI-01 deployment. The running application advertises each capability separately;
a control is disabled or absent when its capability is unavailable.

`DIRECT_REGISTRATION_SIMULATION` is deliberately a **dev auto-reg** input. It injects
an already accepted automatic registration after antenna/tag processing. It is not
antenna simulation and it is not an upstream backend message.

`TAG_SCENARIO_SIMULATION` is the separate simulated-tag passage capability. The
**Simulated tags** pane provides:

```text
Profile       simple | normal | edge
Count
Number range  from .. to
Order         ascending | random
Seed          used for random order
Interval ms
Start / Stop
Progress
```

The client owns batch selection and pacing only. The interval is between registration
scenario starts. The selected profile owns the TagObservation sequence inside each
passage, including whether one or multiple EventData-mapped tags are observed. Random
selection is seedable so a run can be repeated. **Stop** prevents later scenario starts;
it does not undo a scenario already accepted by SI-01.

Backend/UpstreamData simulation remains a separate capability for inbound RaceData and
outbound timing/synchronization behaviour. Its state belongs to CentralSystemSimulator,
not JavaFX controls. Central RaceData authoring is not scoped by the currently selected
TimingNode: Team Mapping is Central-owned current state, and Stage Start Times are authored
per StageId. The engineering UI supports setting or deleting a contiguous RegistrationId
range for one stage; SET may apply a non-negative interval between successive registration
start times. Under the current event mapping, Stage N finishes at LocationId N, so the
simulator routes Stage N state only to a node whose current runtime status is OPEN at
LocationId N; IF-06 itself remains LocationId-scoped. Large authored changes are emitted through the existing bounded
RACE_DATA delta/RECV flow rather than creating a larger protocol message.

ST-2 uses the full-duplex upstream-role ApiEventClient session; ST-3 later swaps only the
transport below the same simulator model.

## Existing web-application compatibility

The current IF-03/TimingData representation should be compared with the existing web
application's expectations for:

- status/snapshot structure;
- live event/update behaviour;
- identifiers;
- timing-data shape;
- reconnect/resynchronisation behaviour.

The purpose is not to make the legacy web application authoritative. The purpose is to
avoid gratuitous incompatibility where a clean public representation can be reused or
mapped simply. Compatibility should remain achievable through a thin mapping layer where
practical.

## Documentation/demo mode

UI screenshots should be reproducible evidence, not ad-hoc desktop captures.

The intended Development Client documentation mode uses deterministic **public synthetic
fixtures** to populate the UI without requiring a live backend, RabbitMQ broker, timing
hardware or proprietary data.

Rules:

- fixture data exists only for visual/documentation rendering and UI tests;
- fixture mode does not count as protocol or SI-01 integration verification;
- screenshots use fixed, documented window dimensions and deterministic fixture content;
- no secrets, production identities or private schemas appear in screenshots;
- generated screenshots are build/documentation output, not hand-edited source images.

This mode also gives reviewers a stable way to inspect UI states that are hard to
reproduce interactively, such as disconnected, degraded or multi-TimingNode views.

## CI screenshot direction

Automated JavaFX documentation screenshots are engineering documentation evidence, not
a substitute for protocol/system verification. The deterministic screenshot pipeline is:

```text
GitHub Actions / Linux
        |
        +-- JDK 21 + pinned JavaFX dependencies
        +-- virtual display (Xvfb when required by JavaFX toolkit)
        +-- start Development Client in documentation/demo mode
        +-- select a named deterministic view
        +-- render JavaFX scene/window snapshot to PNG
        +-- retain screenshot artifact
        +-- publish selected screenshots with generated documentation
```

Prefer an application-owned JavaFX snapshot hook over generic desktop mouse/keyboard
automation. The former is deterministic, knows when the scene has finished rendering and
does not depend on window-manager coordinates.

Generated documentation views may include:

1. Status / connection baseline;
2. Timing / CLOSED without LocationId;
3. Timing / OPEN with dev auto-reg and a bounded LogBook page;
4. Timing / SYNCING with stale cached data;
5. Logs/Terminal only where those screenshots materially improve user documentation.

The user manual may reference these generated screenshots once this pipeline exists.
A screenshot documents presentation; it does not replace textual requirements or
interface contracts.

## Test strategy

The Development Client remains independently testable:

- service/client classes are unit tested without JavaFX handlers;
- UI presentation can use deterministic fixture models;
- interface integration uses a real running SI-01 through its public interfaces;
- dev auto-reg enters SI-01 through IF-03 and the normal accepted-registration operation,
  never through package-private/internal mutation;
- simulated-tag profile requests enter through IF-03 and are verified through
  SimulatedAntenna -> AntennaManager -> TagProcessor -> TimingNode rather than a direct
  TimingNode shortcut;
- client-side batch planning is unit tested for ascending and seedable pseudo-random
  selection independently of JavaFX event handling;
- screenshot generation verifies stable rendering, not business correctness.

## Development Client boundary

SI-02 is the primary desktop engineering, integration, commissioning and system-test
application for the public SI-01 boundaries described above. Its software-item status does
not grant private access to SI-01 runtime/domain state.

Its engineering responsibilities are:

- exercise IF-03 request/status/history/live behaviour, including negative paths;
- inspect Remote Shell and LoggingServer independently from IF-03;
- keep client-local logging usable while SI-01 is unavailable;
- show interpreted convenience views alongside raw public data;
- make reconnect/stale/resynchronisation behaviour explicit;
- support deterministic documentation/demo fixtures without treating fixture mode as
  integration verification.

Headless black-box verification remains owned by the formal `system-test` boundary and
the VTS. Development Client manual verification uses the same public interfaces rather
than package-private application state.

# Engineering Client development and UI baseline

Status: working engineering baseline

Engineering tool: **Engineering Client**  
Implementation location: `test-client/` in `2026-010-02.java.event-timing-framework`

## Purpose

The Engineering Client is the project's interactive development, integration and
diagnostic application for exercising the public boundaries of the **Timing Point
Application** (SI-01).

It is deliberately **not**:

- the planned **Desktop GUI Application** (SI-02);
- part of the Java-8 SI-01 runtime;
- an owner of timing/domain state;
- a shortcut that may mutate SI-01 internals directly.

The current implementation is a standalone Java-17/JavaFX Maven project. It remains
in the same implementation repository as SI-01 because its interface-inspection role
currently evolves together with SI-01. Repository co-location does not make it part of
the SI-01 software item.

## Document role

This SDE document owns the engineering-tool architecture, UI working baseline and
documentation/screenshot workflow. Product behaviour and public contracts remain owned
elsewhere:

- IF-03 API semantics are owned by `32-03-IDD-application-control-status.md`;
- IF-06 backend/upstream semantics will be owned by the applicable system IDD;
- SI-01 domain architecture remains owned by `41-01-SSD-timing-application-specification-document.md`;
- transport implementation belongs in the applicable SI-01 SDD;
- the Engineering Client implementation README owns concrete build/run instructions.

This document may show UI design before JavaFX implementation exists. IF-03 route,
payload and outcome semantics remain owned by the applicable IDD; this document
defines how the Engineering Client presents and enables those accepted controls.

## Repository and runtime boundary

Current placement:

```text
2026-010-02.java.event-timing-framework/
├── core/            SI-01 reusable Java-8 application core
├── app/             SI-01 executable
├── system-test/     separate-process verification
├── shared/
│   └── timing-data/ shared TimingData model + codec/provider SPI
└── test-client/     Engineering Client
                    standalone Java 17 + JavaFX application
                    may depend on event-timing-data only
                    no SI-01 core/app implementation dependency
```

For live SI-01 operation the Engineering Client communicates only through
supported external interfaces. It does not import `event-timing-core` or
`event-timing-app` implementation classes.

TimingData inspection/conversion is a separate engineering capability. The
Engineering Client may depend on the small shared `event-timing-data` artifact and
load the same compatible `TimingDataProvider` implementations that SI-01 can
use, without copying provider-specific decoding rules into client code.

Keeping it in the same repository is intentional while interface changes and
engineering-client changes normally belong to the same development increment. A
separate repository becomes useful only when evidence shows an independent release
cycle, independent ownership, substantial external reuse, or lower coordination cost
from splitting it.

## Component architecture

<a id="fig-sde03-01"></a>
![Engineering Client architecture](../../../raw/prod/docs/assets/architecture/engineering-client.svg)
*Figure SDE03-01 — Engineering Client UI, independent client services and SI-01 engineering boundaries.*

The JavaFX event handlers remain presentation code. Network/protocol work is kept in
small independent client services so the UI does not become the owner of IF-03, shell or
logging protocol semantics.

The current principal services are:

| Service | SI-01 boundary | Role |
| --- | --- | --- |
| `ApiClient` | IF-03 HTTP/JSON | version/status queries and later supported commands/test control |
| `ApiEventClient` | IF-03 WebSocket | status/event snapshots and live event inspection |
| `RemoteShellClient` | Remote Shell | line-oriented engineering terminal |
| `LiveLogClient` | `LoggingServer` | live diagnostic records and temporary runtime log-level control |

Step 4 adds one narrowly scoped engineering capability through IF-03:
direct injection of an **already accepted semantic registration**. That control
enters the normal TimingNode registration operation after antenna/decoding/filtering.
When exercising a running SI-01 through IF-03, the Engineering Client does not
construct committed TimingData directly and does not choose the TimingNode-owned
source identity, active location or sequence.

For offline/import/export/compatibility inspection, the Engineering Client may
decode or encode TimingData through the shared TimingData API/provider boundary.
That capability does not make the client an owner of live SI-01 domain state.

Backend/upstream injection through a `DebugConnector` remains a useful later
engineering capability, but it is not required by this first registration slice.

## Current UI baseline

The current JavaFX window is approximately 900 x 700 pixels and contains four tabs.

### Status

The Status tab currently provides:

- SI-01 HTTP endpoint selection;
- `Get Version` and `Get Status`;
- parsed application/build identity;
- first TimingNode identity and lifecycle;
- the complete raw JSON response.

The parsed values are an engineering convenience. The raw response remains visible so
interface changes and unexpected fields can be inspected without first changing the UI.

### Events

The Events tab currently provides:

- WebSocket endpoint selection;
- explicit connect/disconnect state;
- latest event type and occurrence time;
- first TimingNode identity/lifecycle from the event snapshot;
- retained-on-screen raw events for the current client session.

A reconnect is expected to recover a complete current snapshot according to IF-03.

### Terminal

The Terminal tab is a small client for the project's line-oriented Remote Shell. It
contains explicit connection controls, a black monospace terminal area and a command
input field.

It is an engineering shell client, not an SSH/Telnet emulator.

### Logs

The Logs tab connects to the separate `LoggingServer` diagnostics boundary. It shows
new log records and can query/change the temporary runtime-global logging level.

Live logs are not IF-03 application events and do not become TimingNode state merely
because they are visible in the same Engineering Client.

## Step-4 Timing view UI baseline

D01 defines the concrete Engineering Client presentation for the first-registration
slice before A03 implements it. The design is deliberately mid-fidelity: control
placement, state, visibility and enablement are specified; production styling,
branding and pixel-perfect JavaFX layout are not.

The existing **Status**, **Events**, **Terminal** and **Logs** tabs remain. Step 4
adds one **Timing** tab. Direct accepted-registration simulation belongs in this
Timing view because it exercises TimingNode registration state; the separate
Upstream/DebugConnector direction remains later work.

<a id="fig-sde03-02"></a>
![Engineering Client Timing view](../../../raw/prod/docs/assets/architecture/engineering-client-timing-view.svg)
*Figure SDE03-02 — Mid-fidelity Timing view in an OPEN/LIVE state. The YAML source is authoritative and generates both SVG and editable draw.io output.*

<a id="fig-sde03-03"></a>
![Timing view control states](../../../raw/prod/docs/assets/architecture/engineering-client-timing-states.svg)
*Figure SDE03-03 — Control-state examples for CLOSED/no-location, CLOSED/located, OPEN and reconnecting/stale.*

### View structure

The Timing tab is one vertically readable workflow rather than several small
modal dialogs:

1. connection/view state and configured TimingNode identity;
2. current lifecycle and LocationId;
3. location/open/close controls;
4. capability-gated accepted-registration input;
5. processed command outcome;
6. committed TimingData history.

The view uses the current single-TimingNode IF-03 endpoint. Multi-node selection
is deliberately not introduced in Step 4.

### Presentation model

The UI keeps three kinds of information visibly distinct:

| UI concern | Source | Presentation rule |
| --- | --- | --- |
| TimingNode identity | IF-03 status | read-only |
| Lifecycle + LocationId | IF-03 authoritative status | current state; stale marker retained during reconnect |
| Direct-registration capability | IF-03 capabilities | controls hidden or disabled when unsupported/disabled |
| Last command result | processed IF-03 command response | transient operation feedback; not treated as TimingData |
| TimingData history | IF-03 committed-history resource | ordered by source sequence |
| Live TimingData | `TIMING_DATA_COMMITTED` | merge into history by stable record key |
| Raw protocol detail | Status/Events diagnostic tabs | remains available for engineering inspection |

### Control enablement

The client shall derive control availability from the latest authoritative state,
not from which button was pressed most recently.

| View state | Location edit / Set | Open | Close | Inject accepted registration |
| --- | --- | --- | --- | --- |
| disconnected | disabled | disabled | disabled | disabled |
| reconnecting / stale | disabled | disabled | disabled | disabled |
| LIVE + CLOSED + no LocationId | enabled | disabled | disabled | disabled |
| LIVE + CLOSED + LocationId | enabled | enabled | disabled | disabled |
| LIVE + OPEN | read-only / disabled | disabled | enabled | enabled only when capability enabled |

A rejected command does not optimistically mutate the local model. The client
shows the returned domain/error outcome and then keeps or refreshes authoritative
status as required.

### Location and lifecycle controls

The LocationId field uses the public numeric LocationId representation. The UI
does not encode concrete allowed event/location ranges itself; event/profile
policy belongs to SI-01/reference configuration.

While CLOSED:

- LocationId is editable;
- **Set location** is enabled when the entered value is structurally valid;
- **Open** becomes enabled only after authoritative status reports a current
  LocationId.

While OPEN:

- LocationId is shown read-only;
- **Set location** and **Open** are disabled;
- **Close** is enabled.

The client still handles server-side conflicts such as `NODE_NOT_CLOSED` or
`NO_LOCATION`; disabled controls reduce avoidable requests but are not the
domain enforcement mechanism.

### Direct accepted-registration control

The first engineering registration control is shown only for the accepted
`DIRECT_REGISTRATION_SIMULATION` capability.

Inputs:

- `RegistrationId` — required opaque shared representation;
- observation time — editable canonical timestamp for deterministic tests;
- **Use current time** — convenience action that fills the input, not a different
  protocol operation;
- **Inject accepted registration** — enabled only while LIVE, OPEN and the
  capability is enabled.

The client does **not** supply:

- TimingNode/source identity;
- LocationId;
- sequence number;
- recordedAt;
- final TimingData JSON.

Those remain SI-01-owned values. The processed command response is displayed as
operation feedback. The resulting committed record is then observed through
history/live TimingData.

### TimingData history

The first history table shows enough semantic data for Step-4 inspection:

- source sequence;
- LocationId captured in the record;
- RegistrationId;
- effective/observation time;
- registration variant/type.

The stable record key remains TimingNodeId + sequence. Selecting a row may later
show full/raw IF-05 JSON, but a separate detail inspector is not required for
the first A03 implementation because raw protocol inspection already exists in
the Status/Events engineering tabs.

History is not cleared by a transient WebSocket disconnect. It becomes visibly
**STALE** until the reconnect rebuild completes.

### Connection and rebuild states

The Timing view uses four user-visible connection/data states:

- **DISCONNECTED** — no authoritative live connection; mutating controls disabled;
- **CONNECTING/RECONNECTING** — transport recovery in progress; previous values may
  remain visible but are marked stale;
- **STALE** — cached status/history is visible but must not drive mutations;
- **LIVE** — status/history rebuild is complete and buffered live events have been
  merged.

Reconnect follows IF-03:

1. reconnect WebSocket and begin buffering later events;
2. apply the new status snapshot;
3. reload committed TimingData history;
4. merge buffered status changes in order;
5. merge buffered `TIMING_DATA_COMMITTED` by stable record key, discarding overlap;
6. only then mark the Timing view LIVE and re-enable controls.

This avoids a misleading interval in which old state is interactive while history
is still rebuilding.

### Error and timeout presentation

Expected command outcomes are shown close to the affected control, plus a compact
**Last command** summary. The UI distinguishes:

- domain conflict/rejection;
- busy/unavailable;
- capability disabled;
- timeout with **outcome unknown**;
- unexpected client/server error.

For `OUTCOME_UNKNOWN`, the client does not immediately repeat the command. It
first refreshes/rebuilds authoritative state/history because accepted work may
still have completed after the caller timeout.

### Deterministic documentation states

The YAML wireframes use only synthetic public values. They are design evidence,
not JavaFX screenshots and not integration verification.

The eventual JavaFX documentation mode should reproduce at least:

1. CLOSED with no LocationId;
2. CLOSED with LocationId;
3. OPEN with direct registration capability enabled and committed history;
4. reconnecting/stale.

The generated YAML → SVG/draw.io wireframes remain the D01 design source even
after JavaFX screenshots become available. Screenshots prove implementation
appearance; they do not replace the UI-state specification.

## Capability-driven engineering controls

The Engineering Client must not assume that direct registration simulation is
available in every SI-01 deployment. The running application advertises whether
that engineering capability is supported and enabled; otherwise the control is
disabled or absent.

For this first slice the engineering control is deliberately a **direct accepted
registration** input. It is not antenna simulation and it is not an upstream
backend message. Broader DebugConnector/upstream simulation is deferred until a
later slice needs inbound backoffice behaviour such as start-time/reference-data
updates.

## Existing web-application compatibility

Before Step-4 IF-03/TimingData representations are fixed, the project will inspect the
existing web application's current expectations for:

- status/snapshot structure;
- live event/update behaviour;
- identifiers;
- timing-data shape;
- reconnect/rebuild behaviour.

The purpose is not to make the legacy web application authoritative. The purpose is to
avoid gratuitous incompatibility where a clean public representation can be reused or
mapped simply. A later prototype should be able to connect the existing web application
with a thin compatibility layer where practical.

## Documentation/demo mode

UI screenshots should be reproducible evidence, not ad-hoc desktop captures.

The intended Engineering Client documentation mode uses deterministic **public synthetic
fixtures** to populate the UI without requiring a live backend, RabbitMQ broker, timing
hardware or proprietary data.

Rules:

- fixture data exists only for visual/documentation rendering and UI tests;
- fixture mode does not count as protocol or SI-01 integration verification;
- screenshots use fixed, documented window dimensions and deterministic fixture content;
- no secrets, production identities or private schemas appear in screenshots;
- generated screenshots are build/documentation output, not hand-edited source images.

This mode also gives reviewers a stable way to inspect planned UI states that are hard
to reproduce interactively, such as disconnected, degraded or multi-TimingNode views.

## CI screenshot direction

The target automated flow is:

```text
GitHub Actions / Linux
        |
        +-- JDK 17 + pinned JavaFX dependencies
        +-- virtual display (Xvfb when required by JavaFX toolkit)
        +-- start Engineering Client in documentation/demo mode
        +-- select a named deterministic view
        +-- render JavaFX scene/window snapshot to PNG
        +-- retain screenshot artifact
        +-- publish selected screenshots with generated documentation
```

Prefer an application-owned JavaFX snapshot hook over generic desktop mouse/keyboard
automation. The former is deterministic, knows when the scene has finished rendering and
does not depend on window-manager coordinates.

CI should initially prove one stable screenshot before multiplying the number of views.
Candidate generated views are:

1. Status / connection baseline;
2. Step-4 Timing view for one closed/open TimingNode;
3. direct accepted-registration simulation with resulting TimingData/history;
4. Logs/Terminal only where those screenshots materially improve user documentation.

The user manual may reference these generated screenshots once this pipeline exists.
A screenshot documents presentation; it does not replace textual requirements or
interface contracts.

## Test strategy

The Engineering Client remains independently testable:

- service/client classes are unit tested without JavaFX handlers;
- UI presentation can use deterministic fixture models;
- interface integration uses a real running SI-01 through its public interfaces;
- direct accepted-registration simulation enters SI-01 through IF-03 and the normal
  TimingNode registration operation, never through package-private/internal mutation;
- screenshot generation verifies stable rendering, not business correctness.

## Step-4 boundary

Step 4 uses the Engineering Client as the primary manual inspection application. It does
**not** add the optional lightweight browser/web test client.

The first Step-4 protocol documents must therefore be sufficient to support:

- the Engineering Client;
- headless black-box/system verification;
- straightforward compatibility with the existing web application where practical;
- later upstream/connector increments without changing the first committed TimingData identity semantics.

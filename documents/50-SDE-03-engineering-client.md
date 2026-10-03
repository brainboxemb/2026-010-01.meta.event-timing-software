<!-- Generated review/output copy. Edit the source document, not this copy. -->

# Engineering Client development and UI baseline

Status: working engineering baseline

Engineering tool: **Engineering Client**  
Implementation location: `test-client/` in `2026-010-02.java.timing-point-application`

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

- IF-03 API semantics are owned by `32-03-ISD-application-control-status.md`;
- IF-06 backend/upstream semantics will be owned by the applicable system ISD;
- SI-01 domain architecture remains owned by `41-01-SSD-timing-application-specification-document.md`;
- transport implementation belongs in the applicable SI-01 SDD;
- the Engineering Client implementation README owns concrete build/run instructions.

This document defines the Engineering Client UI/design baseline only. IF-03 routes,
payloads, capability semantics and failure codes remain authoritative in
`32-03-ISD-application-control-status.md`; this UI must conform to that contract
rather than redefine it.

## Repository and runtime boundary

Current placement:

```text
2026-010-02.java.timing-point-application/
├── core/            SI-01 reusable Java-8 application core
├── app/             SI-01 executable
├── system-test/     separate-process verification
├── shared/timing-data/ shared TimingData model + codec/provider SPI
└── test-client/     Engineering Client
                    standalone Java 17 + JavaFX application
                    may depend on event-timing-data only
                    no SI-01 core/app implementation dependency
```

For live SI-01 operation the Engineering Client communicates only through
supported external interfaces. It does not import `timing-point-core` or
`timing-point-app` implementation classes.

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
![Engineering Client architecture](../assets/architecture/engineering-client.svg)
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

The IF-03 HTTP and WebSocket client services share one process-wide JDK
`HttpClient` transport. Repeated UI actions may create short-lived request
objects, but they must not create a new JDK HTTP selector/worker thread group
for every operation.

The Engineering Client's own asynchronous request worker is named
`ec-request`. JDK-owned transport threads keep their native `HttpClient-*`
names; seeing one stable group is expected, while a new numbered group for
every UI action indicates accidental transport recreation.

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

The current JavaFX window is 1180 x 790 pixels and contains five tabs.

### Status

The Status tab currently provides:

- SI-01 HTTP endpoint selection;
- `Get Version` and `Get Status`;
- parsed application/build identity;
- a compact summary of the first reported TimingNode state;
- the complete raw JSON response.

The parsed values are an engineering convenience. The raw response remains visible so
interface changes and unexpected fields can be inspected without first changing the UI.

### Events

The Events tab currently provides:

- WebSocket endpoint selection;
- explicit connect/disconnect state;
- latest event type and occurrence time;
- TimingNode list/selected node state from the event snapshot;
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

## Step-4 Timing UI baseline — first registration slice

### Implementation alignment status

The Step-4 JavaFX implementation is aligned with the current D01 wireframes and
control/resynchronisation rules in this document. The implemented Timing view now:

- uses the selected TimingNode for node-addressed controls and LogBook reads;
- shows general **Last operation** feedback with the TimingNode controls;
- shows the current `DIRECT_REGISTRATION_SIMULATION` capability state next to
  the auto-reg controls;
- keeps cached values non-authoritative while disconnected, syncing or stale;
- buffers `STATUS_CHANGED` and `TIMING_DATA_COMMITTED` events received during
  resynchronisation, applies the HTTP status/LogBook baseline first, then applies
  the buffered events in delivery order before transitioning to **LIVE**;
- automatically starts resynchronisation after an `OUTCOME_UNKNOWN` result.

The three source YAML wireframes remain the Step-4 presentation/design baseline
published through the engineering portal. Pixel-for-pixel reproduction is not a
verification requirement; control availability, ownership, stale/live meaning
and resynchronisation ordering are the relevant design contract.

This documentation/UI baseline is still under project review. Review comments may
change the D01 proposal before the manual VC-ST1-003/V04 running-system check.

The **Timing** tab is the Step-4 working surface for one **selected** TimingNode.
It combines current authoritative node state, first-slice controls and committed
LogBook data without making the client an owner of domain state.

The user-facing **Sync view** action manually starts the same resynchronisation
used after reconnect. It does **not** rebuild or modify SI-01 domain data. It
reloads current status, capabilities and the bounded LogBook baseline into the
client, reconciles buffered live events and only then marks the view **LIVE**.

IF-03 already represents 1..N TimingNodes. The first Java runtime may still
compose only one node, in which case selection is implicit. The client design
must not bake that runtime limitation into its protocol model; when several
nodes are reported, the same Timing view is addressed to the selected node.

### CLOSED without an operational location

<a id="fig-sde03-02"></a>
![Timing view — CLOSED without location](../assets/architecture/engineering-client-timing-closed.svg)
*Figure SDE03-02 — Timing view while CLOSED and no current LocationId is assigned.*

This is the initial operational state after startup/recovery. The user may enter
a valid event/profile LocationId and apply it. **Open** stays disabled until the
client has resynchronised status showing an assigned LocationId.

The auto-reg controls remain disabled while the node is CLOSED.

### OPEN with LogBook records

<a id="fig-sde03-03"></a>
![Timing view — OPEN with LogBook records](../assets/architecture/engineering-client-timing-open.svg)
*Figure SDE03-03 — Timing view while OPEN with dev auto-reg simulation and a bounded LogBook page.*

While OPEN:

- LocationId is displayed read-only;
- changing LocationId is disabled;
- **Close** is enabled;
- dev auto-reg is enabled only when capability
  `DIRECT_REGISTRATION_SIMULATION` is both supported and enabled;
- the user supplies only `id` plus `time`;
- the optional **Now** action fills the `time` field from the client
  clock for convenience, while an explicit timestamp remains available for
  deterministic testing;
- successful commits appear in the history and through the live event stream.

The client never supplies TimingNodeId, source sequence, active LocationId or
`recordedAt` for dev auto-reg simulation.

### SYNCING / stale state

<a id="fig-sde03-04"></a>
![Timing view — syncing and stale](../assets/architecture/engineering-client-timing-reconnecting.svg)
*Figure SDE03-04 — Cached Timing view while IF-03 state/LogBook gaps are being resynchronised after reconnect or **Sync view**.*

When the IF-03 live connection is lost, cached information remains visible for
diagnosis but is marked **STALE** and all state-changing controls are disabled.

Reconnect and manual **Sync view** handling follow the same D03 resynchronisation sequence:

1. connect the WebSocket and receive the complete status snapshot;
2. begin buffering later live events;
3. query LogBook metadata and fetch only the bounded ranges needed to close any gap;
4. apply buffered status changes in delivery order;
5. merge buffered TimingData events and discard records already present in
   the cached LogBook by stable TimingData record key;
6. only then transition the Timing tab to **LIVE** and re-enable controls.

A reconnect does not visually pretend that cached values are authoritative.

### Control availability

| Client state | Set Location | Open | Close | Auto-reg |
| --- | --- | --- | --- | --- |
| disconnected / syncing / stale | disabled | disabled | disabled | disabled |
| LIVE + CLOSED + no LocationId | enabled | disabled | disabled | disabled |
| LIVE + CLOSED + LocationId assigned | enabled | enabled | disabled | disabled |
| LIVE + OPEN + simulation capability enabled | disabled | disabled | enabled | enabled |
| LIVE + OPEN + simulation capability unsupported/disabled | disabled | disabled | enabled | hidden or disabled with capability explanation |

The UI disables obviously invalid actions, but SI-01 remains authoritative.
A race or stale UI may still produce a domain conflict; the client displays the
processed result and refreshes authoritative state rather than assuming the local
button state was proof of domain acceptance.

### Operation-result presentation

The Timing tab keeps **queue/transport execution** distinct from the **processed
domain result**:

- `UPDATED`, `OPENED`, `CLOSED` and idempotent results are shown as normal
  operation outcomes; successful dev auto-reg shows the returned `seq`;
- domain conflicts such as `NO_LOCATION`, `NODE_NOT_CLOSED` and
  `NODE_NOT_OPEN` are shown inline without treating them as application crashes;
- `BUSY` / `UNAVAILABLE` are shown as execution availability problems;
- `OUTCOME_UNKNOWN` marks the Timing view stale and triggers status/LogBook
  resynchronisation before a state-changing retry is offered;
- unexpected internal failures remain clearly distinct from expected domain
  rejections.

The **Last operation** area in the wireframe is intentionally compact. Detailed
raw response/error JSON remains available for engineering diagnosis.

### LogBook presentation

The first table is a paged view of the selected TimingNode LogBook and shows
committed source order plus the fields most useful during Step-4 integration:

```text
sequence | variant/type | LocationId | RegistrationId | effectiveTime | recordedAt
```

The stable record key is `TimingNodeId + sequenceNumber`. Because the current
view already identifies one TimingNode, the table may omit the repeated
TimingNodeId column while retaining the complete key internally for merge and
deduplication.

Selecting a LogBook row may expose the complete public IF-05 JSON representation
in a detail/raw view. The table itself must not invent event-specific
RegistrationId or LocationId semantics beyond labels supplied by later
profile/reference-data features.

### Documentation/demo fixtures

The three wireframes above define deterministic public synthetic states for D01
review. Later JavaFX documentation-mode screenshots should reproduce these same
states closely enough that differences are intentional UI implementation choices,
not accidental contract drift.


## Capability-driven engineering controls

The Engineering Client must not assume that dev auto-reg is
available in every SI-01 deployment. The running application advertises whether
that engineering capability is supported and enabled; otherwise the control is
disabled or absent.

For this first slice the engineering control is deliberately a **dev auto-reg** input. It is not antenna simulation and it is not an upstream
backend message. Broader DebugConnector/upstream simulation is deferred until a
later slice needs inbound backoffice behaviour such as start-time/reference-data
updates.

## Existing web-application compatibility

The accepted Step-4 IF-03/TimingData representation should still be compared with
the existing web application's current expectations for:

- status/snapshot structure;
- live event/update behaviour;
- identifiers;
- timing-data shape;
- reconnect/resynchronisation behaviour.

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

Automated JavaFX documentation screenshots remain a useful follow-up, but they
are **not a Step-4 V04 pass/fail gate**. For Step 4, the source YAML wireframes are
the maintained design evidence and V04 uses observed running-system behaviour.
A later deterministic screenshot pipeline may replace the wireframes with
implementation screenshots where that improves the engineering portal.

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
2. Timing / CLOSED without LocationId;
3. Timing / OPEN with dev auto-reg and a bounded LogBook page;
4. Timing / SYNCING with stale cached data;
5. Logs/Terminal only where those screenshots materially improve user documentation.

The user manual may reference these generated screenshots once this pipeline exists.
A screenshot documents presentation; it does not replace textual requirements or
interface contracts.

## Test strategy

The Engineering Client remains independently testable:

- service/client classes are unit tested without JavaFX handlers;
- UI presentation can use deterministic fixture models;
- interface integration uses a real running SI-01 through its public interfaces;
- dev auto-reg enters SI-01 through IF-03 and the normal
  TimingNode registration operation, never through package-private/internal mutation;
- screenshot generation verifies stable rendering, not business correctness.

## Step-4 boundary

A03 implementation and the automated VC-ST1-002 black-box verification are
complete. The Engineering Client documentation/UI baseline is still under review.
After review comments are resolved, the remaining execution activity is
VC-ST1-003/V04: the manual running-system Engineering Client demo documented in
`test-client/STEP4-DEMO.md` and tracked by Java issue #127.

Step 4 uses the Engineering Client as the primary manual inspection application. It does
**not** add the optional lightweight browser/web test client.

The first Step-4 protocol documents must therefore be sufficient to support:

- the Engineering Client;
- headless black-box/system verification;
- straightforward compatibility with the existing web application where practical;
- later upstream/connector increments without changing the first committed TimingData identity semantics.

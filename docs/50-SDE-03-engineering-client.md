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

This document may show planned engineering controls before their protocol contract is
final. Such UI direction is not authority for an IF-03 route or an UpstreamProtocol
message shape.

## Repository and runtime boundary

Current placement:

```text
2026-010-02.java.event-timing-framework/
├── framework/       SI-01 reusable Java-8 code
├── app/             SI-01 executable
├── system-test/     separate-process verification
└── test-client/     Engineering Client
                    standalone Maven project
                    Java 17 + JavaFX
                    no framework/app dependency
```

The Engineering Client communicates with a running SI-01 only through supported
external interfaces. It does not import `event-timing-framework` or
`event-timing-app` implementation classes.

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

Step 4 adds an engineering role rather than a second backend transport client:
the Engineering Client uses IF-03 test-control/capability semantics to drive an
SI-01 `DebugConnector`. The injected message must then travel through the normal
`DebugConnector -> UpstreamGateway -> UpstreamProtocol` path. The Engineering
Client does not write directly into `RaceData`, `StageStartTimes`, `TimingData`
or other domain state.

A configured `DebugConnector` may be the only upstream connector in a development
composition or may coexist with a real connector such as `RabbitMqConnector`.
The exact IF-03 test-control resources, capability representation and
UpstreamProtocol message schemas are intentionally deferred to the Step-4 contract
work after use-case and existing-web-application compatibility review.

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

## Step-4 UI direction

The Step-4 UI should grow only enough to inspect and exercise the domain/protocol slice
being implemented. The working layout is:

```text
Engineering Client
┌────────────────────────────────────────────────────────────┐
│ endpoint / connection / advertised engineering capabilities│
├────────────────────────────────────────────────────────────┤
│ Status | Events | Timing | Upstream | Terminal | Logs      │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ selected engineering view                                  │
│                                                            │
│ parsed state + identifiers + records                        │
│ raw/public representation where useful                     │
│                                                            │
├────────────────────────────────────────────────────────────┤
│ connection / command / validation feedback                  │
└────────────────────────────────────────────────────────────┘
```

The exact tab names remain working UI terminology until the Step-4 use cases and public
contracts have been reviewed.

### Timing view

The Step-4 Timing view is expected to make at least the implemented subset of these
concepts inspectable:

- TimingSystem / TimingNode selection where more than one exists;
- TimingNode lifecycle/status;
- `StageStartTimes`;
- `NextUpTeams`;
- `RaceData` reference state relevant to the current slice;
- registration / LogBook history;
- `TimingData` identity such as `TimingNodeId` + sequence;
- raw/public representations useful for interface debugging.

The Engineering Client may keep a display model or temporary cache for rendering, but
SI-01 remains the authoritative owner of the operational state.

### Upstream view

The working Upstream view is an engineering control/inspection surface, not a second
production backend implementation.

It should be able to show:

- whether SI-01 advertises support for backend/upstream simulation;
- whether DebugConnector test control is enabled;
- relevant configured connector/status information exposed by public contracts;
- a controlled way to inject supported semantic upstream test messages;
- observable results/traffic needed to understand what SI-01 emitted or accepted;
- validation/error feedback.

A useful Step-4 example is injecting a synthetic reserve-transponder mapping or other
reference-data message as an upstream message and then observing the resulting SI-01
state through normal public queries/events.

The exact message editor and message types follow the reviewed IF-06/UpstreamProtocol
contract. The UI must not invent fields solely because they are convenient to display.

### Use-case-driven Step-4 UI review scenarios

The existing **Status**, **Events**, **Terminal** and **Logs** tabs are the
implemented JavaFX baseline. The planned **Timing** and **Upstream** views
are review targets, not currently implemented screens.

| Scenario | Planned Engineering Client behaviour | Use case |
| --- | --- | --- |
| Select another TimingNode | Replace the selected instance's displayed state/history instead of combining separate nodes' data. | UC-001, UC-005, UC-009, UC-014 |
| Lose/re-establish event connection | Mark cached information stale/disconnected and rebuild the view from current SI-01 state after reconnect. | UC-008, UC-009 |
| Inspect ordered registration data | Display the owning TimingNode and source sequence separately from WebSocket delivery order, with raw public data available for diagnosis. | UC-003, UC-009, UC-011 |
| Inspect advertised capabilities | Disable or hide unsupported test controls; ordinary status inspection works without DebugConnector. | UC-009 |
| Inject synthetic reference input | Submit only supported semantic input; show submission feedback separately from resulting state/events. | UC-009, UC-010 |
| Run alongside a real connector | Identify engineering-origin traffic without requiring a second independent backend implementation in the client. | UC-009, UC-011 |

D03 owns the actual routes, JSON fields, capability representation, message
schemas and any additional replay/retention policy. This section only specifies
the UI behaviours that should be reviewable when those contracts exist.

## Capability-driven engineering controls

The Engineering Client must not assume every SI-01 build/deployment supports every
engineering action.

The intended pattern is:

```text
Engineering Client
        |
        | query public capabilities
        v
      IF-03
        |
        +-- ordinary status/query capabilities
        +-- optional debug/upstream-test capability
                         |
                         v
                  DebugConnector
                         |
                  UpstreamGateway
                         |
                  UpstreamProtocol
```

The UI enables an engineering control only when the running application advertises the
corresponding supported/enabled capability.

Debug/upstream injection should be disabled or absent by default in normal production
compositions unless explicitly enabled. It may remain useful next to a real RabbitMQ
connector for targeted testing, but debug-origin traffic must remain diagnosable and
must still pass through the supported upstream semantic boundary.

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
2. Step-4 Timing view with two synthetic TimingNodes;
3. Upstream view with DebugConnector capability enabled;
4. Logs/Terminal only where those screenshots materially improve user documentation.

The user manual may reference these generated screenshots once this pipeline exists.
A screenshot documents presentation; it does not replace textual requirements or
interface contracts.

## Test strategy

The Engineering Client remains independently testable:

- service/client classes are unit tested without JavaFX handlers;
- UI presentation can use deterministic fixture models;
- interface integration uses a real running SI-01 through its public interfaces;
- DebugConnector injection enters SI-01 through IF-03 test control and the normal
  upstream path, never through package-private/internal mutation;
- screenshot generation verifies stable rendering, not business correctness.

## Step-4 boundary

Step 4 uses the Engineering Client as the primary manual inspection application. It does
**not** add the optional lightweight browser/web test client.

The first Step-4 protocol documents must therefore be sufficient to support:

- the Engineering Client;
- headless black-box/system verification;
- straightforward compatibility with the existing web application where practical;
- later production connector implementations without changing the core TimingData and
  UpstreamProtocol semantics.

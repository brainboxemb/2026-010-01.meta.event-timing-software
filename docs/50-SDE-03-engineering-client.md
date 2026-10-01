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
├── timing-data-api/ shared TimingData model + codec/provider SPI
└── test-client/     Engineering Client
                    standalone Java 17 + JavaFX application
                    may depend on timing-data-api only
                    no SI-01 framework/app implementation dependency
```

For live SI-01 operation the Engineering Client communicates only through
supported external interfaces. It does not import `event-timing-framework` or
`event-timing-app` implementation classes.

TimingData inspection/conversion is a separate engineering capability. The
Engineering Client may depend on the small shared `timing-data-api` artifact and
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

## Step-4 UI direction — first registration slice

The Step-4 UI grows only enough to exercise and inspect the first registration
slice. The existing **Status**, **Events**, **Terminal** and **Logs** tabs remain
the implemented baseline. A small **Timing** view may be added; a broad
Upstream/reference-data editor is not part of this slice.

The first Timing view should expose:

- the configured TimingNode identity as read-only state;
- the assigned/unassigned location state;
- location editing only while the TimingNode is `CLOSED`;
- explicit `open` and `close` actions with visible accepted/rejected outcomes;
- a capability-gated direct accepted-registration simulation control;
- optional deterministic observation time for repeatable engineering tests;
- committed registration/TimingData history with source sequence;
- raw public representations where useful for interface diagnosis.

The client must not construct or inject a completed TimingData record. Direct
registration simulation enters the public TimingNode registration operation
**after** antenna/decoding/filtering, so the TimingNode remains responsible for
its configured identity, active location, lifecycle validation and source
sequence. A later simulated-antenna increment will enter earlier in the normal
registration path and exercise filtering before reaching the same operation.

### First-slice UI review scenarios

| Scenario | Planned Engineering Client behaviour | Use case |
| --- | --- | --- |
| Inspect a closed TimingNode | Show configured identity, lifecycle and whether a location is assigned. | UC-001, UC-009 |
| Set/change location | Allow only while `CLOSED`; show explicit validation/rejection. | UC-001, UC-002, UC-009 |
| Open/close | Reject open without a valid location; keep the active location fixed until close. | UC-002, UC-009 |
| Inject an accepted registration | When capability-enabled, submit semantic participant identity plus supported observation time; do not supply sequence/source/location fields owned by the node. | UC-003, UC-009 |
| Inspect registration result | Show committed TimingData/history and source sequence separately from the command-submission result. | UC-003, UC-009, UC-011 |
| Lose/re-establish event connection | Mark cached information stale, rebuild current node state and registration data, then resume live updates. | UC-009 |

D03 owns the actual routes, JSON fields, identifier formats, capability
representation and TimingData schema.

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

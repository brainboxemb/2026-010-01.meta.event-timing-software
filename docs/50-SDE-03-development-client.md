# Development Client development and UI baseline

Status: working engineering baseline

Development tool: **Development Client**  
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

The former separate **Desktop GUI Application (SI-02)** product allocation has
been withdrawn. The Development Client is therefore the project's desktop
engineering application rather than a prototype for a second operator product.

The current implementation is a standalone Java-17/JavaFX Maven project. It remains
in the same implementation repository as SI-01 because its interface-inspection role
currently evolves together with SI-01. Repository co-location does not make it part of
the SI-01 software item.

## Terms and abbreviations

- **SDE** — Software Development Environment
- **IF-03** — API interface
- **SI-01** — Timing Point Application


## Relationship to other documents

This SDE document owns the Engineering Client architecture, desktop UI working baseline
and documentation/screenshot workflow. Normal operator behaviour and public contracts
remain owned elsewhere:

- IF-03 API semantics are owned by `32-03-ISD-application-control-status.md`;
- normal browser/operator behaviour is owned by UC-001/UC-002 and IF-04;
- IF-06 backend/upstream semantics will be owned by the applicable system ISD;
- SI-01 domain architecture remains owned by `41-01-SSD-timing-application-specification-document.md`;
- transport implementation belongs in the applicable SI-01 SDD;
- the Development Client implementation README owns concrete build/run instructions.

This document defines the Development Client UI/design baseline only. IF-03 routes,
payloads, capability semantics and failure codes remain authoritative in
`32-03-ISD-application-control-status.md`; this UI must conform to that contract
rather than redefine it.

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
└── test-client/     Development Client
                    standalone Java 17 + JavaFX application
                    may depend on event-timing-data only
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
| `ApiEventClient` | IF-03 WebSocket | status/event snapshots and live event inspection |
| `RemoteShellClient` | Remote Shell | line-oriented engineering terminal |
| `LiveLogClient` | `LoggingServer` | SI-01 live diagnostic records and temporary runtime log-level control |
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

Backend/upstream injection through a `DebugConnector` is a separate engineering
capability. It is added only when an upstream/backoffice simulation use case requires it;
it is not part of the registration-control workbench.

## Current UI baseline

The Development Client is **API-first**. The client exists primarily to
exercise and inspect the public API contract; Events, Remote Shell and diagnostic
logging support that job but do not define the main screen.

<a id="fig-sde03-05"></a>
![API-first Development Client workbench](../../../raw/prod/docs/assets/architecture/engineering-client-api-first.svg)
*Figure SDE03-05 — Current API-first workbench baseline. Ports and connection
states belong to their individual external boundaries; the UI does not predict
whether SI-01 will accept a domain command.*

This is the current Development Client baseline.

The API tab shows one prominent **Timing view** synchronisation state above the
Version/Status controls. The initial state is **NOT SYNCED — connect Events**. Connecting
the IF-03 Events WebSocket immediately starts the HTTP status/capabilities/LogBook
baseline sync; incoming live events, including the initial STATUS_SNAPSHOT, are buffered
and reconciled after that baseline. Only then does the Timing view become **LIVE**.

Open/Close/registration controls remain disabled while the Timing view is NOT SYNCED,
SYNCING or STALE. **Sync view** is available only while Events is connected; it repeats
the same baseline/reconciliation sequence and does not modify SI-01 domain state.

### Target and connection bar

The top of the window represents one active SI-01 target. The Development Client
configuration file supplies the **startup default** host plus the per-boundary ports and
other client defaults; selecting another device during development shall not require
editing that file and restarting the client.

The target bar therefore contains an editable host/IP field plus **Apply target**. Applying
another host changes the host used by all external SI-01 boundaries without rewriting the
configuration file. Any stateful Events, Remote Shell or Device Log connection to the
previous host is disconnected when the target changes; a boundary shall never silently
remain attached to another device than the one shown in the target field.

The bar shows one compact control/status per external boundary:

| Boundary | Display/interaction |
| --- | --- |
| IF-03 HTTP API | configured port plus clickable **CHECK** action and **CHECKING/READY/UNREACHABLE** state; HTTP is stateless and is not presented as a persistent socket connection |
| IF-03 event WebSocket | configured port plus explicit connect/disconnect and connection state |
| Remote Shell | configured port plus explicit connect/disconnect and connection state |
| SI-01 `LoggingServer` | configured port plus explicit **Device log** connect/disconnect and connection state |
| Development Client local log | always local to the client; visible as **Client log ACTIVE**, not confused with SI-01 diagnostics |

A port therefore never appears without saying which boundary it belongs to. A READY or
connected state for one boundary does not imply that the other boundaries are connected.

The configuration file remains the source of startup defaults and port values. Runtime
target editing is one explicit host override in the target bar, not a second configuration
model spread over the tabs.

The configuration baseline needs, at minimum:

- startup-default target host/address;
- IF-03 HTTP port;
- IF-03 event/WebSocket port when it is independently configured;
- Remote Shell port;
- `LoggingServer` port;
- Development Client local-log path/level;
- registration-input presentation defaults such as an initial prefix.

Exact configuration member names and persistence format are implementation design
decisions; this SDE does not turn them into an SI-01 public interface.

### Tab structure

The reviewed top-level tab order is:

```text
API | Events | Device Log | Client Log
```

The Remote Terminal remains a separately connected external boundary, but its
interactive terminal surface is embedded as a tab in the API Timing workbench
rather than occupying a separate top-level application tab.

**API** is the first tab and primary work surface. It combines the useful parts of the
current Status and Timing tabs:

- version/status requests and parsed identity/state;
- selected TimingNode;
- LocationId input used directly by **Open**;
- Open and Close requests;
- engineering registration request;
- committed LogBook/TimingData inspection;
- last processed operation result;
- complete raw API response/error or selected public record.

The separate Status tab is therefore not required in the target layout. Structured
presentation is a convenience; raw public data remains available because the client is
an engineering tool.

**Events** remains a raw/live IF-03 event inspection surface.

**Device Log** is a top-level tab. It shows records received from the connected
SI-01 `LoggingServer` and has its own **current level** and **set level** controls for the
temporary SI-01 runtime level.

**Terminal** remains the Remote Shell client. Its connection is controlled from the
target bar; selecting the workbench **Terminal** tab is not itself a connection side
effect.

**Client Log** is the final top-level tab. It shows the Development Client's own runtime
log and has independent **current level** and **set level** controls for the local runtime
threshold.

Device Log and Client Log remain independent and distinguishable in the UI and in
exported/copied text. Connecting SI-01 logging shall not be required to see, retain or
change the level of the client's own log.

An Upstream/DebugConnector work surface is added only when that engineering capability
exists; the API-first layout does not pre-create domain behaviour for it.

### Deliberately low client intelligence

The Development Client is a protocol/domain **observer and request initiator**, not a
second implementation of TimingNode acceptance rules.

The UI may disable a control when:

- the required transport/boundary is unavailable;
- the running application explicitly reports that the engineering capability does not
  exist or is disabled;
- that same control has an in-flight request and duplicate submission would obscure the
  result.

The UI shall **not** disable Open, Close or a supported registration request merely
because cached state suggests SI-01 will reject it. For example, a developer must be
able to send **Close** while the displayed node is CLOSED and inspect the actual public
result.

There is no separate IF-03 Set Location operation in the current baseline. Normal
**Open** carries the requested LocationId; SI-01 applies location assignment and the
CLOSED-to-OPEN transition as one ordered node operation.

Displayed lifecycle state, LocationId and capability state remain valuable context, but
they are not local permission rules. SI-01 remains authoritative. Expected domain
rejections are shown as first-class operation results together with raw response data.

This deliberately differs from a production operator GUI, where preventing obviously
invalid actions may be desirable. The Development Client must make negative-path and
boundary testing easy.

### Synchronisation and operation results

The Timing view has four authority states:

- **NOT SYNCED** — no authoritative API/event baseline has been established;
- **SYNCING** — baseline status/capabilities/LogBook are being loaded while later live
  events are buffered;
- **LIVE** — the baseline and buffered live events have been reconciled;
- **STALE** — cached information remains visible for diagnosis but shall not be treated as
  authoritative.

Reconnect and manual **Sync view** use the same sequence:

1. connect the IF-03 event stream and receive the complete status snapshot;
2. buffer subsequent live events while baseline recovery is in progress;
3. query current status/capabilities and LogBook metadata/ranges needed for the selected
   TimingNode;
4. apply the authoritative baseline;
5. apply buffered status changes in delivery order;
6. merge buffered `TIMING_DATA_COMMITTED` records by stable
   `TimingNodeId + sequenceNumber`, discarding duplicates already present in history;
7. transition to **LIVE** only after reconciliation is complete.

When the event connection is lost, the view becomes **STALE**. Cached values remain
visible, but state-changing controls are disabled until resynchronisation completes.

Operation presentation keeps transport/execution availability separate from the processed
domain result:

- normal domain outcomes such as `OPENED`, `CLOSED` and idempotent outcomes are shown
  as ordinary results;
- expected domain conflicts are shown inline rather than as application failures;
- `BUSY` / `UNAVAILABLE` remain execution/admission problems;
- `OUTCOME_UNKNOWN` marks the Timing view stale and starts status/LogBook
  resynchronisation before another state-changing retry is offered;
- unexpected internal failures remain distinct from expected domain rejection.

The compact **Last operation** area shows the interpreted outcome while the complete raw
response/error remains available for diagnosis.

### Timing workbench layout

The current Timing workbench separates controls, interpreted registration data and
technical diagnostics in a two-column/two-row layout:

- the compact Timing-view status row above the workbench shows synchronisation state,
  selected TimingNode, node state and LocationId;
- the **upper-left** contains one tab set:
  **TimingNode | Registration | Simulation | Terminal**;
- the **upper-right** contains the compact **API / application identity** row directly
  above **Registrations**;
- the **lower-left** keeps **Device Log** and **Client Log** simultaneously visible,
  stacked vertically rather than hidden behind another tab set;
- the **lower-right** contains **LogBook / committed TimingData**;
- the workbench keeps an approximately 50/50 horizontal split while allowing the lower
  diagnostic row to use more vertical space than the compact input row;
- **Raw response / selected record** remains available below the workbench but is
  collapsed by default because it is a diagnostic detail rather than the primary view.

The full top-level Device Log and Client Log tabs remain available for focused inspection.
The embedded lower-left views mirror those logs so timing work and recent diagnostics can
be seen at the same time.

The two right-hand views are deliberately not duplicates. **Registrations** is a
presentation projection intended to resemble normal timing use. Its compact columns are:

```text
Time | Type | TeamID | Code | <action>
```

**Type** is the registration type (`AUTO` or `MAN`). **Code** is only needed for
manual registrations to describe how the effective registration time was obtained
(`AUTO` or `MAN`). A manual registration with manually entered time therefore
deliberately shows `MAN` twice: Type `MAN`, Code `MAN`. A manual registration
whose effective time was captured automatically by the client shows Type `MAN`, Code
`AUTO`. An automatic registration already carries its meaning in Type `AUTO`, so its
Code cell is empty.

TeamID is an interpreted reference-data value and is not another name for
`RegistrationId`. For the default/reference EventData profile, a normal
RegistrationId `RT-A-NNNN` is displayed as TeamID `NNNN` without a lookup.
A reserve RegistrationId `RT-R-NNNN` requires the current reserve-assignment
reference data and remains unresolved when that assignment is unavailable.

The technical LogBook retains the actual RegistrationId together with committed
sequence, record Type, record Code and profile time values. ADD/REV remain
technical LogBook semantics and are not the interpreted Code column.

For the current default/reference profile the LogBook time remains the canonical
absolute UTC value. The interpreted Registrations view converts it to normal local clock
time using the explicitly displayed client zone.

For an alternative TimingData profile, the technical LogBook/raw view should show
the representation actually committed by that profile. If that representation contains
only event-local time-of-day, the Development Client must use the same configured
provider/codec translation context as SI-01 when it needs the corresponding semantic
`TimingTimestamp`; the client must not reconstruct a missing event date from its own
clock, selected UI date or display zone. The interpreted view may then present normal
event/local clock time while the technical view remains faithful to the external/profile
representation.

A REV record does not remove the interpreted registration. The final table column has no
text heading and contains an icon-only trash action. After REV, that action cell shows
**DELETED** instead of the trash button, while both ADD and REV remain present in the
immutable LogBook. When the connected SI-01 does not expose the public revoke
operation/capability, the trash action remains disabled rather than pretending deletion
is supported.

### Technical LogBook presentation

The technical LogBook view is bounded/paged and preserves committed source order. It
shows the fields needed to inspect the public TimingData contract independently of the
interpreted Registrations projection, including:

```text
sequence | type | code | LocationId | RegistrationId | effectiveTime | recordedAt
```

`type` and `code` are separate values. The stable record key is
`TimingNodeId + sequenceNumber`; because the workbench already identifies the selected
TimingNode, the table may omit the repeated TimingNodeId column while retaining the full
key internally for merge/deduplication.

Selecting a row may expose the complete public IF-05/profile representation in a raw/detail
view. The table does not invent event-specific RegistrationId, TeamID or LocationId
semantics that are not provided by the active profile/reference data.

### Registration input

The ordinary structured registration input is optimized for readable engineering use
without owning event/profile semantics.

Registration ID entry is split into:

- **Prefix** — a short presentation value, optionally initialized from client
  configuration;
- **Number** — a numeric entry field.

The request value is the exact concatenation presented by the client (for example
`N` + `0001` -> `N0001`). The client does not look up teams/participants or decide
whether that Registration ID is valid for the running event/profile.

Time entry is also presentation-oriented:

- date is shown separately from clock time;
- ordinary clock-time input/display uses hundredths of a second for the current
  reference/API path;
- the interpreted client time zone is shown explicitly beside the Time field;
- **Now** captures date/time in that same displayed zone and marks a manual-registration
  request as time source `AUTO`;
- editing the date or time marks a manual-registration request as time source `MAN`;
- both `AUTO` and `MAN` carry the client-supplied effective registration time; SI-01
  does not replace `AUTO` with its own current time;
- for the current API/reference path, the client converts the explicit local civil value
  to the canonical UTC API timestamp when sending, so the conversion is visible rather
  than implicit;
- profile-specific import/export conversion, when used for TimingData inspection or
  interchange, remains owned by the configured `TimingDataCodec` rather than by form
  widgets or Development Client presentation code.

Nanosecond precision remains unnecessary in the ordinary form. The hundredth-second
field matches the current registration presentation/reference-path precision without
narrowing the generic TimingTimestamp representation.

### Logging behaviour

The Development Client shall use the project logging direction for its **own** runtime
records as well as displaying SI-01 diagnostics. Client startup, configuration loading,
connection transitions, request failures and unexpected UI/service errors belong in
the client log.

Both log sources use the same readable line shape:

```text
HH:mm:ss.SSS - [LEVEL] - message - [sourceClass.sourceMethod]
```

The client log source shall identify the actual Development Client source context rather
than use one generic client marker for every line. The dedicated Client Log tab therefore remains separate from Device Log. Client logging
and its runtime level control remain available when
SI-01 is offline, which is especially important when diagnosing why a connection could
not be established. A runtime Client Log level change does not rewrite the configured
startup level; restarting the Development Client restores the configured value.

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

DebugConnector/upstream simulation remains a separate capability for inbound backoffice
behaviour such as start-time/reference-data updates.

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
        +-- JDK 17 + pinned JavaFX dependencies
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

The Development Client is the primary manual development/integration application for the
public SI-01 boundaries described above. It does not become SI-02 and it does not gain
private access to SI-01 runtime/domain state.

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

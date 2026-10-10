# SI-02 Engineering Client Design Rules (GPD)

Status: working project guidance

## Purpose

This guide defines a repeatable design/review baseline for **SI-02 — Engineering
Desktop Client**. A developer should not have to infer the intended UI from
a sequence of screenshots, incremental CSS fixes or previous pull requests.
Equivalent presentation and asynchronous problems should be solved consistently.

It is **guidance, not a requirements document**. The 41-02 SSD determines
required functionality, the 50-SDE-03 defines the development/runtime baseline,
and SI-01/IF-03 own domain and protocol semantics. This guide governs how
SI-02 expresses those requirements in JavaFX/BentoFX.

## Terms and abbreviations

- **SI-02** — Engineering Desktop Client; not the normal IF-04 operator web UI.
- **BentoFX leaf** — one docking region with one or more selected tabs.
- **presentation state** — local selection, filters, viewport, window arrangement and
  other UI-only state; not authoritative TimingNode state.
- **FX thread** — JavaFX Application Thread; sole writer of JavaFX controls/models.
- **source event** — notification from a public SI-01 boundary, not a UI command.
- **request generation** — local identifier used to reject an obsolete async result.

## Relationship to other documents

Read with [41-02 SSD](41-02-SSD-gui-application-specification-document.md),
[50-SDE-03 Engineering Client development baseline](50-SDE-03-development-client.md),
[44-01 SI-01 Java design rules](44-01-GPD-java-design-rules.md) and
[12-GPD documentation guide](12-GPD-documentation-guide.md).
Implementation lives in `2026-010-02.java.timing-point-application/test-client/`.
That module's `engineering-client.css` is the executable style baseline;
any material change to the rules should change the stylesheet/tests together.
Shared SI-01 coding rules about ownership and explicit state transitions also apply
conceptually, but SI-02 must not adopt SI-01's serial lanes or internal types.

## Rules for layout and interaction

### UI-01 — One view has one primary purpose

**Rule:** Present navigation/status in Systems; actions in TimingNode/API/Registration/
Simulation tabs; interpreted results in Registrations; raw history in LogBook/Raw Data/
Events; technical diagnostics in Device Log/Terminal/Client Log. Do not duplicate
the same status toolbar across panes.

**Why:** Engineers can keep several panels open without searching repeated control
rows or mistaking the currently selected view for the active external source.

**Example:** The Registrations dock contains a table, not application/version buttons.
API identity is in the API tab; an OPEN LocationId appears in Systems and in the
Registrations scope title.

**Avoid:** Placing status, version, count and filter toolbars above every table.

### UI-02 — Use one flat desktop visual language

**Rule:** Use application-owned JavaFX CSS with flat surfaces and zero corner radius.
Keep styling in named classes; do not set visual CSS strings in individual view
constructors. Preserve BentoFX's own dock/selection behaviour instead of mimicking it.

**Why:** Separately themed controls and default Modena subcontrols make one
application look like several unrelated tools.

**Example:** Use `.engineering-log` for log text and `.connection-button` for
connection state. ComboBox arrow and popup follow the same flat controls.

**Avoid:** Inline `-fx-control-inner-background: black; ...` in each log pane,
rounded dropdown arrows beside square buttons, or global rules that break
Windows caption controls.

### UI-03 — Use explicit visual tokens

**Rule:** Use the palette and typography below in one CSS ownership point;
reuse semantic looked-up color names rather than new hex values in every selector.

| Role | Token / current baseline |
| --- | --- |
| Main surface | `-si02-surface` = `#f7f7f7` |
| Raised/tab header | `-si02-raised` = `#eeeeee` |
| Border | `-si02-border` = `#cfcfcf` |
| Text | `-si02-text` = `#202020` |
| Selection/focus | `-si02-accent` = `#0078d7` |
| Connected | `-si02-ok-bg` = `#e9f6ed`, border `#5aa273` |
| Busy / partially connected | `-si02-warning-bg` = `#fff4da`, border `#d6a34a` |
| Fault | `-si02-error-bg` = `#fcecec`, border `#c97474` |
| Body/control text | Segoe UI, 13 px (grid column headers 12 px, regular) |
| Raw/log text | Consolas, 12 px; preserve horizontal scrolling |

**Why:** Visual semantics should remain reviewable and consistent after 20 more
feature additions. Semantic colors must always be accompanied by words/tooltips.

**Example:** All connected boundary options share `.connection-ok`, not
one-off green fills.

**Avoid:** Using color alone as the only explanation of connection status;
using bold as a generic distinction between all table headings and data.

### UI-04 — Spacing is deliberate, not a per-pane invention

**Rule:** Standardize compact control bars at **28 px**, main pane gutters
at **2–4 px**, form/group padding at **8 px**, control gaps at **6–8 px**,
and BentoFX title/header spacing in CSS. Exceptions need a concrete layout reason.

**Why:** Large independent padding in each pane compounds in a split workbench.

**Example:** Device Log uses a 2 px margin; Terminal's input is separated
from output by 4 px. Host/buttons align vertically.

**Avoid:** An extra 12 px wrapper inside every nested BentoFX leaf or a disabled
toolbar consuming half a small dock.

### UI-05 — Prefer the framework's dock controls

**Rule:** BentoFX creates split/detached windows, `≡` context menus and `▼`
overflow navigation. Use `DockContainerLeaf.setMenuFactory` for dock options,
`setClosable(false)` for permanent views and `dockBack` for a moved view.

**Why:** Custom header icons and duplicate right-click handlers drift from
BentoFX's actual selected and focused tab semantics.

**Example:** Registrations scope selection is placed directly in the built-in
`≡` menu; permanent tabs have no close X. A relocated tab may be docked back.

**Avoid:** Adding another hand-drawn tab-close/pin control, hiding it only
through CSS, or recreating framework docking with a second layout registry.

### UI-06 — Selected and focused are different

**Rule:** Each dock region may have a selected tab. Only the region containing
keyboard focus should have the active focus accent. Data updates never request
keyboard focus unless the operator requested it.

**Why:** A registration can refresh Registrations and LogBook without pretending
that Device Log or Terminal was focused or manually selected.

**Example:** Style `.header:selected` neutrally; style focused active headers
with a clear, restrained accent.

**Avoid:** Calling `requestFocus()` in an HTTP/WebSocket completion handler
or coloring every selected tab like the focused pane.

### UI-07 — Persistent choices have explicit ownership

**Rule:** Selected TimingNode, registration scope, log level, follow-latest state
and dock layout are **SI-02 presentation choices**. Only changes originating
from the operator or meaningful source state may update them.

**Why:** A source refresh is not permission to replace the operator's selection
or scroll position.

**Example:** The Registrations tab reads `Registrations [4]` for selected
OPEN location 4, `Registrations [All]` for explicit all-scope, and
`Registrations [–]` if no OPEN location is currently reliable.
Default scope follows the selected node's open location.

**Avoid:** Reassigning ComboBox items or selecting the trailing row on every
unrelated source update, resetting scope after restoring a dock.

### UI-08 — Distinguish warnings from routine connected state

**Rule:** Healthy/live status is expressed by effective controls and per-boundary
status, not by a large repeated **LIVE** banner. NOT SYNCED, SYNCING and STALE
must remain prominent enough to prevent unsafe interpretation of cached data.

**Why:** Status labels belong where they help a decision.

**Example:** Hide Systems' redundant LIVE label while keeping STALE visible.
A Connect toggle shows Connect/Disconnect text and observed state; API HTTP
remains a separate stateless CHECK.

**Avoid:** Repeating a bold LIVE label in multiple panels or green-only
connectivity clues.

### UI-09 — Raw data and interpreted data have separate jobs

**Rule:** Normal Registrations uses local civil time and TeamID; LogBook/Events
retain source record semantics/sequence; Raw Data shows actual public JSON.

**Why:** An interpreted convenience view must not masquerade as a canonical
SI-01 domain history.

**Example:** Selecting a real LogBook row shows that row's raw JSON. A blank
follow-latest row has no delete action, source identity or raw payload.

**Avoid:** Formatting source JSON into an undocumented alternative protocol
or counting sentinel rows as committed records.

### UI-10 — App identity and Windows integration are one coherent surface

**Rule:** The SI-02 application has a distinct PNG Stage icon and multi-resolution
Windows ICO. The Windows-integrated main caption shows icon, flat menu,
name/version and usable native-like window controls without overlap; docked
floating stages retain their normal decorated frame.

**Why:** Hand-built title bars can break window drag/Snap/menu hit-testing or
display the generic Java icon if resources are missing.

**Example:** Keep `WindowsIntegratedTitleBar` behind an explicit optional
integration with a normal native-frame fallback. Recheck scaling and taskbar
pinning on a Windows machine after icon changes.

**Avoid:** Copying Win32 hacks into individual views, claiming JavaFX menus are
native OS menus, or treating jpackage success as pixel-perfect visual proof.

## Rules for updates, threading and verification

### UI-11 — FX thread is the only presentation writer

**Rule:** Public-interface I/O, API queries and blocking operations run on the
client worker/service; results are *marshalled once* to the FX thread before
touching model/presentation controls. Keep network callbacks short.

**Why:** Updating JavaFX controls off-thread creates nondeterministic behaviour
and can block external source event delivery.

**Example:** HTTP `supplyAsync(..., requests)`, then a single
`Platform.runLater(...)` for current-result model application.

**Avoid:** Running HTTP from a button handler or calling `TableView.setItems`
from a WebSocket transport callback.

### UI-12 — Invalidate results from obsolete operations

**Rule:** Any asynchronous request tied to a connection or selected node must
carry a request-generation/owner token. Disconnect, reconnect, new sync or
node change invalidates older results. Check generation and selected context
*before* updating model, history, status, raw data or feedback.

**Why:** An old HTTP completion can arrive after disconnect or a newer sync,
otherwise turning stale history back into LIVE or showing the wrong node.

**Example:** Begin sync with generation 17; disconnect moves it to 18;
when generation 17 completes, silently ignore it.

**Avoid:** Setting `viewState(LIVE)` unconditionally in every completion
callback regardless of active connection and selected-node context.

### UI-13 — Apply meaningful changes, not callback counts

**Rule:** Update only affected views and only when semantic state changes.
HTTP response and WebSocket echo of the same committed record are idempotent.
Multiple wake signals may be coalesced, but *committed history events must
not be dropped*.

**Why:** Rebuilding tab items, table projections and tree selections after
every status frame produces focus churn and excessive FX pulses.

**Example:** STATUS update → changed status/controls/Systems; committed
TimingData → Registrations/LogBook only; identical status → no redraw.

**Avoid:** One universal `refreshEverything()` path for every event type,
or dropping records while debouncing visual updates.

### UI-14 — Protect commands and their outcomes

**Rule:** A command's in-flight state owns disabled controls until that command
completes. The command outcome is distinct from observed TimingNode/registration
state. An unknown outcome requires resynchronisation, not optimistic success.

**Why:** An unrelated status event must not enable controls halfway through
the original request.

**Example:** Submit direct auto-reg → disable relevant controls → show accepted
sequence on confirmed commit; render LogBook only from SI-01 committed history.

**Avoid:** Re-enabling all controls in a generic status callback or treating
client-side HTTP submission as a committed TimingData entry.

### UI-15 — Bound queued UI work and preserve inspection

**Rule:** Keep UI dispatch per burst bounded where data semantics allow it.
Batch display-only log append work, avoid redundant scheduled scroll/focus
operations, and preserve the viewport when the user reviews history.
Never batch by silently discarding committed TimingData.

**Why:** A high-volume log/event stream should not create an unbounded
`Platform.runLater` backlog or lock users out of historical inspection.

**Example:** Merge live records by stable identity and schedule one table
render per FX turn; a user who scrolls up pauses follow-latest.

**Avoid:** One unbounded appended UI task for every debug message with
an unconditional `scrollTo` for every callback.

### UI-16 — Verification has layers and evidence

**Rule:** Verify pure state and source-selection rules with unit tests,
client services with deterministic fakes, public-boundary integration
separately, and Windows docking/focus/caption with a real packaged UI.

**Why:** JavaFX compilation and jpackage startup do not prove mouse popups,
focus, Snap or scaled icon geometry.

**Example:** Unit-test selection/status/reconnect generation and idempotent
history; CI test JavaFX version consistency and packaged Windows startup;
use a small named Windows acceptance path below.

**Avoid:** Calling a visual issue done solely because Maven tests are green,
or storing transient acceptance notes in stable design rules.

## Windows acceptance path

Use the current packaged **main** app image, note Windows scaling and test:
1. Open the client: one flat menu/title row; no overlapping caption controls,
   expected icon in taskbar/Alt-Tab; minimize, restore and Snap work.
2. Inspect the Host/Connect controls: one baseline, readable keyboard focus,
   accurate independent interface states; no auto-connection at startup.
3. Connect Events and wait for baseline: NOT SYNCED → SYNCING → LIVE; Systems
   reports node state; no stale data presented as live.
4. Open a node, submit one registration and revoke it: Registrations/LogBook
   update once per meaningful change; Device Log only displays actual device logs;
   unrelated dock tabs do not steal focus.
5. Inspect history: scroll up pauses following; select blank final row resumes;
   all/current-location filter and Registrations scope title reflect the source.
6. Detach, re-dock and reset a pane; standard BentoFX `≡` and `▼` menus
   remain usable at normal and increased DPI.
7. Disconnect/reconnect or switch node *during an in-flight baseline load*:
   obsolete completion does not change status back to LIVE or restore old rows.

Record actual failures as issues with a screenshot/log and source revision.
Do not inflate this guide with dated PR histories.

## Rule maintenance

Review this document when a *design rule* changes; edit CSS, presentational
model/tests and documentation as one coherent review unit. Track changes in
planning/PR history instead of appending retired designs to this guide.

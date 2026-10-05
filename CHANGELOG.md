# Changelog

All notable changes to this repository are documented here.

The repository is currently in its planning and research phase.

## Unreleased

- Define the central typed `ApplicationConfiguration` model: compiled defaults plus IF-11 startup overrides, read-only/dynamic configuration views with typed change notifications, TimingNode-local TagProcessor policy ownership, and IF-03 runtime query/override/change-event semantics.

- Synchronize Step-5 A01 planning with the completed D04-aligned antenna runtime lifecycle/composition implementation.

- Bind each Engineering Explorer source-definition pane to the selected engineering object ID and render the exact authored MyST Need block instead of an arbitrary surrounding line window.

- Keep colon-fenced Need option metadata (`:id:`, `:status:`, relations and similar options) on separate GitHub-rendered source lines with CommonMark hard breaks.

- Keep MyST colon-fence Need openers as GitHub hard-break lines so the following `:id:` option renders visibly on its own source-review line without changing Sphinx-Needs semantics.

- Make Engineering Explorer architecture/detail panes user-resizable with persisted proportions, and keep inline Source definition disclosure square, compact and icon-free.

- Use MyST colon fences for engineering Needs so UC/requirement/interface/verification source remains readable and wraps normally during direct GitHub Markdown review, while retaining the same Sphinx-Needs semantics and generated traceability.

- Synchronize Figure SI01-01 with the accepted Java execution design by replacing the stale SerialWorker with SerialExecutor and SerialScheduledExecutor while retaining higher-level Application responsibilities.

- Move registration duplicate suppression ahead of passage aggregation after tag-to-registration mapping; use `TimingNode.offer(...)` as the bounded fire-and-forget handoff and start the duplicate window only after immediate `ACCEPTED` admission.

- Align runtime metric ownership: rename `TagProcessingCounters` to `TagProcessingMetrics`, group executor measurements under nested `SerialExecutor.Metrics` / `SerialScheduledExecutor.Metrics` snapshots, and keep hot-path updates component-owned and low-allocation.

- Align D04/D05 with the queued TagProcessor implementation: make observation input-queue capacity part of TagProcessingPolicy and measure ingress FULL/not-running separately from TimingNode admission outcomes.

- Align execution primitives with the JDK-backed design: rename TimingNode `SerialWorker` to `SerialExecutor` backed by a one-thread bounded `ThreadPoolExecutor`, and define separate `SerialScheduledExecutor` for TagProcessor queue draining and housekeeping.

- Correct D04 TagProcessor execution ownership: make TagProcessor an active object with a bounded observation input queue separate from its single execution lane, with scheduled housekeeping on that same lane, using a narrow JDK-backed execution capability and one fixed-delay housekeeping registration while timed state exists; custom lower-level execution and any role-specific thread priorities require Step-5 performance evidence.

- Correct D04 passage identity: antennas expose `DecryptedTagId`, TagProcessor maps it to `RegistrationId` before passage aggregation, and multiple tags for one registration share the same strongest-RSSI burst without retaining the full observation list.

- Define the internal runtime measurement boundary for Step 5: component-owned primitive counters, pull-based TimingNode/TagProcessingCounters/JVM snapshots through `RuntimeMeasurementReader`, and no engineering metrics on the public TimingNode/IF-03 contract.

- Clarify D04 tag-processing execution ownership: TagProcessor owns passive filters and a periodic task handle, while `platform.execution.PeriodicExecutor` provides the scheduling mechanism and `runtime.Composition` remains construction/wiring only.

- Define the Step-5 antenna/input architecture: Event-based TagObservation with RSSI/time, AntennaManager lifecycle/probe/inventory control, TagProcessor RSSI/duplicate filtering, and an injected TagId-to-RegistrationId mapper instead of a mandatory lookup table.
- Keep local registration independent from presentation, diagnostic logging and backoffice delivery; keep Java thread priority as measured tuning rather than a correctness mechanism.

- Restore SDD-02 narrative coherence: separate runtime thread policy from SerialWorker design, move cross-cutting Pi/runtime resource rules to the SI-01 SSD, and remove remaining implementation-history wording from current design.

- Let VTS `{vc}` objects own testcase ID/title structure instead of duplicating each case as a Markdown heading, keeping Sphinx-Needs and traceability views aligned.

- Adopt the shared BrainboxEmb repository-documentation entrypoint model: make the root README concise, add docs/README.md as the authored-document overview, and move documentation/SIP-actual operating guidance into SDE-01.

- Restore SVP/VTS as current verification authority: express runtime characterization as a reusable method and VC-ST1-003 as a stable Development Client case without SIP-step/demo execution history.

- Restore the Development Client SDE to one current API-first UI baseline: fold active synchronization/result/LogBook rules into that baseline and remove superseded Step-4 wireframe and execution-history narration.

- Restore the focused SDDs as current-state design books: remove implementation-step chronology, keep execution/persistence/artifact alternatives as present design criteria, and move runtime measurement planning out of SDD-02 to its SIP/SDE/SVP owners.

- Restore use cases, interface documents and software-item specifications as current-state authority by removing roadmap/implementation-log narration while preserving active contract maturity and reserved mappings.

- Audit documentation roles so planning/history stays in planning/evidence records while requirements, interfaces, design and verification books describe the current authoritative state; reopen Step-5 D01 as a reviewable SIP planning gate.

- Complete Step-5 A02 on Java revision `f205e55d9af907a631f346261bdc04ba3e487a6d` and activate A03 measurement-driven allocation/data-access strategy.

- Complete Step-5 A01 on Java revision `3a173235a2a823e6fbbec8397a2e2649841b4a0f` and activate A02 runtime markers/counters.

- Start SIP Step 5 D01 with a single-TimingNode runtime measurement/evidence baseline; keep default JVM scheduling as the baseline, gate batching/pooling/caching/concurrency changes on measurements, and activate simulated-antenna A01 after the decision.

- Add a reviewed API-first Engineering Client UI baseline: config-driven per-boundary connection controls, client + SI-01 logging, low local domain intelligence, clearer registration/time entry and a primary API work surface.

- Assign TimingNode OPEN/CLOSE TimingData explicitly to Step 5 with separate contract, implementation and verification activities while leaving the current IF-05 contract unchanged until Step-5 D02 executes.

- Expand linear child branches when opening a traceability document so one click exposes the first useful choices without flattening sibling branches.

- Start Engineering Explorer and Traceability Comparison neutrally when no object is requested, remove the implicit TimingNode preference, add a small balanced tree base inset, and qualify the specific SSD requirements smart-expansion path.

- Increase custom engineering workbench typography by an exact 1px while preserving the compact spacing and pane geometry.

- Auto-expand linear Traceability Comparison heading chains on disclosure so authored hierarchy stays visible without requiring repeated clicks through single-choice levels.

- Add a subtle non-layout-affecting boundary around the Traceability Comparison tree pane while preserving the compact edge alignment.

- Tighten Traceability Comparison tree edges/indentation, add a compact `Collapse all` control beside the type filter, and align the Engineering Explorer with the same dense full-width workbench styling without changing its architecture/detail behavior.

- Make the Traceability Comparison tree fully portal-owned: remove remaining Material navigation classes that interfered with disclosure/indentation, eliminate unnecessary tree-pane padding, tighten workspace top spacing, and qualify real collapsed/open/closed child visibility in Chrome.

- Keep the Traceability Comparison browser interaction probe isolated from the publishable portal tree so CI can exercise disclosure/resizing without mutating production HTML.

- Make the Traceability Comparison a true resizable split-pane workbench: reliable custom tree disclosure controls, tighter left alignment/indentation, a wider default tree pane, draggable/keyboard-accessible separators, and persisted pane proportions.

- Build the Traceability Comparison navigation as a MkDocs view component from native Sphinx-Needs document/section metadata, preserving authored heading/source order and using Material-style nested navigation instead of duplicating section classifications in engineering objects.

- Replace the Traceability Comparison's card-like source browser with a conventional compact expandable tree: source-document nodes use disclosure chevrons, child engineering objects are indented borderless rows, and the selected object receives one subtle row highlight while existing filters/order/scroll behavior remain intact.

- Make the Traceability Comparison substantially denser for desktop engineering use: smaller typography/controls, independent scroll panes for tree/root/compare views, reliable hidden filtering, type counts/result counts, and automatic pane reset to each newly selected object heading.

- Restore the Engineering Explorer's pre-comparison composition with the architecture context on the left and the selected engineering object visible on the right; replace the Traceability Comparison's flat root selector with a source-ordered document tree plus search/type filters.

- Split the Engineering Portal interaction into two explicit pages: keep the full clickable SI-01 architecture visible in the Engineering Explorer, and provide a separate Traceability Comparison workspace with an in-page root-object selector for fixed-left / related-right Incoming/Outgoing review.

- Rename the Application-layer presentation entry point from `CommandHandler` to `PresentationGateway`; define gateway names by the adjacent side whose traffic they mediate, keeping `PresentationGateway` transport-independent and distinct from the I/O-owned `UpstreamGateway` transport/integration boundary.

- Restore the Engineering Explorer's primary side-by-side traceability workflow: keep the selected engineering object on the left, open clicked Incoming/Outgoing/one-hop relations on the right, keep per-object source links, and retain the clickable architecture only as an additional selection aid.

- Align Java naming with the software boundary: keep Event Timing as the family/shared namespace, rename SI-01-specific Maven artifacts to `timing-point-*`, and define the `tp-<owner>-<role>[-<identity>]` convention for project-owned Timing Point runtime threads while leaving JDK/third-party thread names unchanged.

- Refine TimingNode operation semantics around one serialized mutable-state ownership boundary: synchronous state-dependent commands wait for their processed domain result while Java Future mechanics stay internal; submission-only ingress remains explicit; timeout reports unknown outcome rather than rollback; consistency-sensitive reads use TimingNode-owned queries/snapshots; add concrete runtime sequence examples and restore SDD-01 to the Architecture Book.

- Define the JavaFX `test-client/` as the project **Engineering Client**: document its independent external-client architecture, current/Step-4 UI baseline, API-controlled DebugConnector role, same-repository boundary and deterministic CI screenshot/documentation direction.

- Clarify Engineering Portal navigation: exact Markdown source links now force GitHub source view (`?plain=1#L…`), explorer actions are named `Open details & relations` / `Open source definition`, and the explorer/object pages explain the distinction between derived portal views and authored engineering source.

- Define application profiles as versioned default-composition templates resolved before `ApplicationBootstrap`; keep profile, platform and operating mode as independent selectors and let explicit deployment configuration override allowed non-secret defaults without publishing deployment-specific profile definitions.

- Show **Runtime** explicitly in Figure SI01-01 with `TimingApplication` above Infrastructure / cross-cutting; order infrastructure as `LoggingServer -> Logging -> ApplicationBootstrap -> Build/version identity` and align the logging dependency arrow with the current Java dependency direction.

- Rename SI-01 to **Timing Point Application**, define `io.github.brainboxemb.eventtiming.timingpoint` as its Java package root, and align the detailed design with separate `infra.logging` and `infra.loggingserver` components while preserving `TimingNode` as the internal domain aggregate.

- Rename IF-03 from **Remote API** to **API** across system/interface architecture, configuration (`presentation.api`) and Java component naming, while keeping HTTP/WebSocket wire behavior unchanged; also remove the overlapping `live records / level control` edge label from the layered architecture overview.

- Close SIP Step 3 on accepted `v0.2.2`, mark its implementation/verification activities done, record the release completion date and activate Step 4 — TimingNode state and domain foundation.

- Move SIP Step 3 to a v0.2.2 release-closure candidate: all functional/verification Done criteria are satisfied and the accepted v0.2.2 release remains the explicit closure gate.

- Map the existing IF-03-owned `VC-ST1-001` into the ST-1 automated verification profile as a verification-only separate-process `system-test` that imports no product Java classes and runs on Linux/Windows verification paths.

- Treat the Engineering Explorer as a full-width workspace: hide the persistent MkDocs navigation sidebar on that page only and replace it with a compact horizontal portal navigation row, leaving normal navigation unchanged elsewhere.

- Improve the Engineering Explorer desktop balance by giving the SI01-01 architecture substantially more width and reducing supporting detail-panel typography while preserving the narrow-screen single-column layout.

- Thin the executable boundary further by moving the default YAML `ApplicationConfig` loader and embedded build-identity interpretation into `event-timing-framework`; keep the executable-owned filtered provenance resource, provider selection and packaging as concrete app build concerns.

- Simplify primary Remote API class names inside `presentation.interfaces.remoteapi`: `HttpEndpoint`, `WebSocketEndpoint` and `MessageWriter`, keeping the function-first package and IF-03 semantics unchanged.

- Refine A08 retained logging to timestamped per-session/rotation text files and a compact operator-facing line format; make file creation safe when a Raspberry Pi starts before network time synchronisation by treating wall-clock filenames as non-unique and protecting the active file; keep reusable logging implementation and component-owned configuration under framework `infra.logging` with explicit `Logging` and `LoggingServer`, while SLF4J provider selection remains an executable-composition concern and live diagnostics remain separate from IF-03.

- Remove the project-local `docs/01-handoff.md` and use the shared `brainboxemb.meta/docs/20-20-new-session-handoff.md` as the single session-start handoff; keep project state in the owning plan/specification documents, active PRs and CI/generated evidence rather than duplicating it in a second operating manual.

- Define a Java-8-compatible typed extension/provider boundary for implementation families that may be public, vendor-specific or private: `TimingDataProvider`, `UpstreamProtocolProvider`, `AntennaProvider`, `CanProtocolProvider` and `DisplayProtocolProvider`; keep `SimulatedAntenna` built in and always available, keep class-loader discovery in bootstrap/infra, add IF-11/SVP provider selection and verification rules, re-estimate the 11-step roadmap from 55d to 59d before reserve, and refresh the 29 September actual-effort indication to about 56.4 hours / 7.1 project days.

- Refine the SI-01 domain architecture around recorded timing data: let one `TimingApplication` host 1..N internal `TimingSystem` aggregates with 1..N `TimingNode`s each, give both TimingSystem and TimingNode their own semantic `UpstreamMessagePort`, make `SystemStatus` a dedicated per-TimingSystem Domain component owning the complete operational overview, add a per-TimingSystem `TimeSource` for controllable simulation time, keep `LogBook` contained inside TimingNode, relate TimingNode explicitly to canonical `TimingData`/`TimingDataRecord`, scope `UpstreamProtocol` to one TimingSystem, and treat the logical I/O composition as per TimingSystem while keeping transport mechanics in I/O.

- Rename the per-TimingNode `Journal` responsibility to `LogBook` across the current domain/architecture views, and add a transport-neutral `Beeper` role under SI-01 `Devices` without prematurely assigning it to CAN or another concrete device network.

- Reorganized the authored documentation into numbered document ranges: 00–09 context, 10–19 planning, 20–29 external inputs, 30–39 software-system documents, software-item `40-<SI>-UC`, `41-<SI>-SRD/SSD`, `42-<SI>-SAD`, `43-<SI>-SDD-<N>`, 50–59 engineering environment, 60–69 verification and 70–79 user/operations.

- Locally migrate document control to an acyclic specification hierarchy: reserve `32` for software-system IDDs with the stable interface ID as the second segment (`32-03-IDD`, `32-11-IDD`), use the stable software-item ID as the second segment for SI-owned document families, use a final sequence only when several documents share the same family/scope, and number the generic SDE family as `50-SDE-01`, `50-SDE-02`, ... . Planning and verification documents remain downstream/control references rather than requirement inputs.

- Rename the future SI-01 messaging component family to upstream terminology: `UpstreamGateway`, `UpstreamMessageRouter` and `UpstreamMessagePort`. `Upstream` names the bidirectional relationship with the central/external system rather than a per-message direction; keep the I/O capability named `Messaging`. Also compact the three Application-layer cards in Figure SI01-01 without changing their label font size.

- Complete Migration 013 Step 4 on the bounded 17-object / 34-relation
  native MyST/Sphinx-Needs slice, pin released `tool.eng-docs v0.4.0`, retain
  generated inverse/backlinks and shared diagram engineering identities, and
  qualify the released graph boundary through the merged real consumer.
- Add the Migration 013 Step-5 production engineering portal canary: derive a
  Material static site from the normalized engineering graph and real generated
  SI-01 SVG, with search, generated object pages, one-hop context, exact source
  links, clickable architecture, full selected use-case narratives and
  browser-qualified workspace behavior while
  retaining the existing Book as a separate first-class output.

- Retain the Migration 013 Step-3 production result as the behaviour baseline:
  requirements own `derived_from`, design owns `satisfies`, verification owns
  `verifies`, and inverse context is generated rather than authored. The
  original anchor + hidden-`eng` syntax is superseded by the native
  MyST/Sphinx-Needs authoring decision.


- Compact Figure SI01-01 by aligning the main architecture canvas with the fixed title origin, reducing unused horizontal layer width and right-side whitespace, and increase secondary diagram text from 11 px to 12 px for readability.

- Pin released `tool.eng-docs v0.3.11` and give the first SI-01 architecture nodes stable engineering `object_id` metadata (`TimingNode`, `CommandHandler`, `Conductor`, `RemoteApi`), with CI verifying that normal generated SVG and editable draw.io output preserve those identities without changing the visible Figure SI01-01 design.

- Define the Step-3 A08 logging architecture: keep framework logging provider-neutral through SLF4J, let the executable configure JUL with rotating retained file output, add an optional client-initiated live diagnostics socket for the JavaFX engineering client, and allow a temporary runtime-global log-level override without mutating deployment configuration or mixing logs into IF-03 status/events.

- Refine backend messaging into an I/O `Messaging / BackendGateway` boundary, application-level `BackendMessageRouter` for backend-only target resolution, and bidirectional per-TimingNode `BackendMessagePort`; make the layered view show router relations to Domain and I/O Messaging, and define one Web presentation binding/port per configured TimingNode.

- Introduce `ApplicationBootstrap` as a reusable framework-owned cross-cutting startup/composition component, keep the effective configuration model with that framework bootstrap, keep concrete YAML/build-resource loaders in the thin executable artifact, and define component-root Java package readability rules without adding a separate Runtime box to the architecture view.

- Pin `tool.eng-docs` v0.3.10 and refine Figure SI01-01 into complementary Domain/I/O polygons with a visible gap: enlarge Domain for breathing room, fully enclose raised Devices in an I/O shoulder, and compact the normal I/O cards/band.

- Refine the main SI-01 layered architecture view with explicit Web presentation, shared Console/Remote Shell terminal handling, and bullet-level I/O refinement for Storage, Devices, BackendGateway and Device Networks.

- Refine device/network architecture: separate functional `Devices` from `Device Networks`, keep `CanNetworkController` for active CAN management, replace `WifiNetworkController` with bidirectional `NetworkDeviceService`, and keep smart-display rendering/synchronisation outside SI-01.

- Refine SI-01 backend messaging architecture: add distinct `ApplicationId`, introduce `BackendGateway` over 1..N transport connectors, place `MessageHandler` with each TimingNode, and keep application-level message handling deferred until a concrete use case exists.

- Track approximate git-derived actual effort per SIP step using explicit merged-PR boundaries; show original estimate, actual and remaining estimate as independent planning signals and at that point, refresh the project snapshot to about 5.1 project days.

- Show concrete end dates for every SIP phase: keep actual completion dates for completed steps and round future cumulative forecast boundaries up to Monday for presentation without feeding that rounding into later calculations.

- Make SIP roadmap document indicators cumulative and scope-honest: render maturity/completeness as `R-60`, define completeness against expected project-wide document scope, include system use cases in the progression, and show use cases/SRD/IDD/design/verification growing across later implementation steps instead of marking first-slice documents as 100% complete.

- Make SIP actual-effort planning reproducible with a two-repository merged-PR commit-window calculator; use 30-minute overlapping activity windows, refresh the 26 September snapshot to about 38.2 hours / 4.8 project days, and add a manually dispatched GitHub Action that can create a draft snapshot-update PR.

- Rework the SIP into a software-first 11-step roadmap: restore the initial planning horizon to 55 estimated project days before reserve, add a target-hardware/platform study before procurement, split platform study from target bring-up, defer real devices until after domain/simulation/GUI/backoffice work, apply planning reserve to forecast months, and keep planning-change history only on per-step detail boards.

- Correct speculative planning/documentation: keep SI-02 as the planned real GUI with technology open, classify the current JavaFX client as manual engineering test tooling, remove SI-03/iPad as a committed product item, treat a web client only as optional Remote API test tooling, and make Raspberry Pi performance/resource concerns measurement-driven rather than assumed.

- Simplify the SDP into a lighter high-level development-direction document; move detailed release mechanics, calendar planning and step execution back to the SDE/SIP where they belong.

- Improve architecture readability by using software-item names before SI labels in running prose and replacing unnecessary `authoritative`/in-memory repository wording with direct state-ownership language.

- Reframe IF-03 as the general Remote API, organise SI-01 presentation by functional interface first (`remoteapi`, console, shell) and nest A06/A07 HTTP/WebSocket configuration under `presentation.remoteApi`.

- Select Java-WebSocket 1.6.0 for A07 on a dedicated Java-8 listener, require snapshot-on-connect/reconnect, and defer black-box `STATUS_CHANGED` verification until a real public status transition exists.

- Align IF-03 first-executable `/status` with TimingNode-owned status by removing the redundant application lifecycle/start-time fields, and document the Java 17 development test client baseline.

- Simplify the active I/O model: SI-01 composes 0..N `Antenna` instances and 0..N `BackofficeConnector` instances directly in I/O; their TimingNode routing/binding is configuration rather than a separate router component, and the former `RegistrationAsset` / `RegistrationRouter` layer is removed from the software/configuration model.

- Rename the primary logical timing aggregate from `Waypoint` to `TimingNode` and its stable identity from `UniqueID` to `TimingNodeId`; keep antenna and backoffice-connector mappings in I/O so one antenna may feed 1..N TimingNodes and one application may compose 0..N backoffice connectors.

- Refresh Step-3 planning and handoff around the current `v0.2.1` / `0.2.2-SNAPSHOT` baseline and IF-11 configuration work, while leaving the already-correct roadmap status (`Step 3: active`) unchanged.

- Define IF-11 application configuration as the SI-01 deployment/composition contract: keep TimingNode, hardware and presentation identities separate; use base + platform + optional profile overlays; treat simulation as adapter composition; keep secrets external; and prefer framework composition over a `BaseApplication` inheritance hierarchy.

- Rename the external adapter responsibility to `I/O`, organise it around hardware/messaging/storage, reserve Java `infra` for cross-cutting technical support, and shorten the active SAD/Java SDD while retaining the diagrams and copyable package/responsibility blocks.

- Make the TimingNode concurrency contract concrete and reviewable: state plainly how serial execution protects mutable domain state, document concurrency edge cases, separate IF-03 wire shapes from Java class design, keep small enums with their owning object, and place build provenance such as `BuildIdentity` under cross-cutting `infra` rather than application semantics.

- Record first Java implementation feedback in the SI-01 SAD/SDD: keep layers logical rather than represented by marker objects, use the small shared `CommandHandler` boundary for the authoritative version query, and keep `TimingApplication.Builder` as composition-only infrastructure.

### Changed

- Aligned SI-01 command and execution architecture around a transport-independent `CommandHandler`, explicit per-`TimingNode` state-lane ownership, and boundary-owned target resolution; removed the separate `TimingSystemDispatcher` architecture component and remaining current-design `TimingSystemInstance` terminology.
- Route project agent guidance through `brainboxemb.meta/AGENTS.md`, make dependency-owner AGENTS explicitly non-inherited, and keep event-timing-specific documentation/privacy boundaries local.

### Added

- Initial repository purpose and navigation.
- Persistent agent guidance.
- Agent work plan and reusable handoff document.
- Brainstorm document for early software ideas and unresolved questions.
- Domain baseline covering registration-system identities, locations, source-scoped monotonic registration sequences, team/tag identity and locally synchronised reference data.
- System use-case catalogue linking operational intent to later requirements/interfaces and verification.
- Software Development Plan (SDP), Software Implementation Planning (SIP), and Software Development Environment (SDE).
- Software-item register for the headless timing application and planned desktop GUI application.
- Initial Software System Architecture Document (SSAD) with system-interface catalogue, status, threading/testability, fault/recovery, connectivity, resource-baseline and public/private extension direction.
- Software-item architecture and detailed-design documents for the timing application and desktop GUI, plus focused data/display, Java/Maven component, runtime/configuration and backoffice design notes.
- Initial Software Verification Plan (SVP) covering unit, component, interface, integration, hardware-in-the-loop, fault-injection and target-runtime observations.
- TimingNode systems, registration hardware/assets, data-source identities and antennas as distinct configurable concepts, with software/domain, hardware/deployment and configuration/mapping views kept separate.
- Registration/data-source and prepare-team models as separate traceable capabilities; registration records use a monotonic sequence per data source.
- In-memory application/domain state with simple file backup/restore as the initial persistence direction.
- Transport-independent backoffice boundary with lightweight socket-loop and RabbitMQ integration directions.
- Layered system-test profiles from application black-box testing through socket-loop, RabbitMQ and target/HIL testing.
- Generated software documentation workflow producing GitHub-readable Markdown, SVG and editable draw.io output.
- Pull-request generated documentation on `dev/pr-<N>/docs` and merged/default-branch documentation on `prod/docs`.
- Generated architecture/state/data diagrams including software-item boundaries, threading, TimingNode lifecycle, registration-hardware topology, configuration mapping, RFID lifecycle, connectivity layers, source-sequence traceability and V1/V2 display/data flow.
- Generated SIP roadmap with project-day estimates, calendar projection, scope-aware documentation maturity, editable SVG/draw.io output and printable A3 tiled/A2 vector PDFs.
- Reference-material index and collection area, including an illustrative layered embedded architecture reference.

### Changed

- Clarified the SI-01 software architecture around `TimingNode`, separating software/domain decomposition from registration hardware/deployment topology and configuration/data-source identity mapping; refined responsibility names including `TagProcessor`, `StageStartTimes`, `TimingNodeJournal`, `NextUpTeams`, `RaceData`, and `StageTiming`.
- Documentation producers now retain the released `brainboxemb.execution-evidence` v1 envelope under `evidence/executions/<execution-id>/`, while current Moon materialization evidence remains separate under `orchestration/`.
- Documentation CI and preview cleanup now consume `tool.git-project v0.2.4`, including the released execution-evidence schema contract.
- Refined planning-document responsibilities so SDP owns high-level strategy/risks/resources, SIP owns implementation increments/deliverables/demonstrations, SDE owns the engineering environment/workflow, and SVP owns verification strategy.
- Changed source collection from a mandatory blocking phase to capability-driven supporting work.
- Defined just-in-time document maturity so requirements/IDDs become concrete when their capability approaches implementation rather than all documentation being completed up front.
- Closed AP-0 repository bootstrap and scoped AP-1 around formalising only the first SI-01 executable slice.
- Clarified the handoff so active work is resolved across the meta, SI-01 implementation and reusable tooling repositories instead of assuming the current meta PR is always the implementation PR.
- Moved ownership of the SI-01 layered responsibility architecture to the software-item SAD and refocused the Java detailed design on Java package, Maven artifact, contract-placement and composition detail.
- Refocused the SSAD on software-system context, software-item relationships, system interfaces, deployment relationships and cross-item constraints; SI-01 runtime/threading/messaging/persistence/device detail now belongs to the SI-01 SAD.
- Restructured the SI-01 SAD as the primary current technical design document, including logical/process/development/deployment views plus concrete threading, messaging, logging, configuration, persistence and technology-decision directions.
- Retired the former TimingSystem SDD and runtime-topology/configuration SDD after consolidating their useful architecture into the SAD and stable domain facts into the domain baseline.
- Renumbered the remaining SI-01 SDDs after those retirements so the current sequence is contiguous: `SDD-01` data/display, `SDD-02` Java component/package/artifact, and `SDD-03` backoffice transport.
- Reduced the active architecture book to the SSAD, software-item SADs and the focused Java component/package/artifact SDD; data/display and backoffice transport SDDs remain deferred working notes outside the active architecture book until implementation justifies detailed design.

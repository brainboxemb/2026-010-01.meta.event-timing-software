# Changelog

All notable changes to this repository are documented here.

The repository is currently in its planning and research phase.

## Unreleased

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

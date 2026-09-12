# Changelog

All notable changes to this repository are documented here.

The repository is currently in its planning and research phase.

## Unreleased

### Added

- Initial repository purpose and navigation.
- Persistent agent guidance.
- Agent work plan and reusable handoff document.
- Brainstorm document for early software ideas and unresolved questions.
- Domain baseline covering registration-system identities, locations, source-scoped monotonic registration sequences, team/tag identity and locally synchronised reference data.
- System use-case catalogue linking operational intent to later requirements/interfaces and verification.
- Software Development Plan (SDP), Software Implementation Planning (SIP), and Software Development Environment (SDE).
- Software-item register for the headless timing application, desktop GUI, and React/browser/iPad operator application.
- Initial Software System Architecture Document (SSAD) with system-interface catalogue, status, threading/testability, fault/recovery, connectivity, resource-baseline and public/private extension direction.
- Software-item architecture and detailed-design documents for the timing application, desktop GUI, web operator application, TimingSystem internals, data/display behaviour, Java/Maven component structure, runtime topology/configuration and transport-independent backoffice design.
- Initial Software Verification Plan (SVP) covering unit, component, interface, integration, hardware-in-the-loop, fault-injection and Raspberry Pi Zero resource evidence.
- Registration assets, registration sources and antennas as distinct configurable concepts; a timing-system instance may contain multiple assets/sources and one application may run multiple instances.
- Registration and ready-team models as separate traceable capabilities; registration records use a monotonic sequence per registration source.
- In-memory authoritative state with simple file backup/restore as the initial persistence direction.
- Transport-independent backoffice boundary with lightweight socket-loop and RabbitMQ integration directions.
- Layered system-test profiles from application black-box testing through socket-loop, RabbitMQ and target/HIL testing.
- Generated software documentation workflow producing GitHub-readable Markdown, SVG and editable draw.io output.
- Pull-request generated documentation on `dev/pr-<N>/docs` and merged/default-branch documentation on `prod/docs`.
- Generated architecture/state/data diagrams including software-item boundaries, threading, TimingSystem lifecycle, RFID lifecycle, connectivity layers, source-sequence traceability and V1/V2 display/data flow.
- Generated SIP roadmap with project-day estimates, calendar projection, scope-aware documentation maturity, editable SVG/draw.io output and printable A3 tiled/A2 vector PDFs.
- Reference-material index and collection area, including an illustrative layered embedded architecture reference.

### Changed

- Refined planning-document responsibilities so SDP owns high-level strategy/risks/resources, SIP owns implementation increments/deliverables/demonstrations, SDE owns the engineering environment/workflow, and SVP owns verification strategy.
- Changed source collection from a mandatory blocking phase to capability-driven supporting work.
- Defined just-in-time document maturity so requirements/IDDs become concrete when their capability approaches implementation rather than all documentation being completed up front.
- Closed AP-0 repository bootstrap and scoped AP-1 around formalising only the first SI-01 executable slice.
- Clarified the handoff so active work is resolved across the meta, SI-01 implementation and reusable tooling repositories instead of assuming the current meta PR is always the implementation PR.
- Moved ownership of the SI-01 layered responsibility architecture to the software-item SAD and refocused SDD-03 on Java package, Maven artifact, contract-placement and composition detail.

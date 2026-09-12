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
- Software Development Plan (SDP), Software Implementation Planning (SIP), and Software Development Environment (SDE).
- Software-item register for the headless timing application, desktop GUI, and React/browser/iPad operator application.
- Initial Software System Architecture Document (SSAD) with system-interface catalogue, status, threading/testability, fault/recovery, connectivity, resource-baseline and public/private extension direction.
- Software-item architecture and detailed-design documents for the timing application, desktop GUI, web operator application, TimingSystem internals, data/display behaviour, and Java/Maven component structure.
- Initial Software Verification Plan (SVP) covering unit, component, interface, integration, hardware-in-the-loop, fault-injection and Raspberry Pi Zero resource evidence.
- Registration and ready-team models as separate traceable capabilities; registration records use a monotonic sequence per registration system/source.
- In-memory authoritative state with simple file backup/restore as the initial persistence direction.
- Generated software documentation workflow producing GitHub-readable Markdown, SVG and editable draw.io output.
- Pull-request generated documentation on `dev/pr-<N>/docs` and merged/default-branch documentation on `prod/docs`.
- Generated architecture/state/data diagrams including software-item boundaries, threading, TimingSystem lifecycle, RFID lifecycle, connectivity layers, source-sequence traceability and V1/V2 display/data flow.
- Reference-material index and collection area, including an illustrative layered embedded architecture reference.

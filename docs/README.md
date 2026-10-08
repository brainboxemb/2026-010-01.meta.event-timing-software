# Event Timing Software documentation

This directory is the authored engineering-document collection for the Event Timing
Software project. The root README is the GitHub entrypoint; this page is the navigation
authority for the maintained source documents.

The project keeps its specialized software-engineering document model for planning,
system/interface specifications, software-item design and formal verification. The shared
BrainboxEmb README insight applies at the entrypoint level; it does not replace this
software-project structure.

Detailed numbering and document-family rules are owned by
[12-GPD — Documentation guide](12-GPD-documentation-guide.md).

## Reading routes

| Need | Start here |
| --- | --- |
| Current implementation sequence | [11-SIP](11-SIP-software-implementation-plan.md) |
| Development direction | [10-SDP](10-SDP-software-development-plan.md) |
| System behaviour | [30-UC](30-UC-system-use-cases.md) and [31-SSSD](31-SSSD-software-system-specification-document.md) |
| SI-01 specification/architecture | [41-01-SSD](41-01-SSD-timing-application-specification-document.md) |
| SI-01 detailed design | [43-01-SDD-01](43-01-SDD-01-data-and-display-design.md), [43-01-SDD-02](43-01-SDD-02-java-component-design.md), [43-01-SDD-03](43-01-SDD-03-backoffice-transport-design.md) |
| SI-01 Java design/review rules | [44-01-GPD](44-01-GPD-java-design-rules.md) |
| Development environment/tooling | [50-SDE-01](50-SDE-01-software-development-environment.md), [50-SDE-02](50-SDE-02-java-build-test-toolchain.md), [50-SDE-03](50-SDE-03-development-client.md), [50-SDE-04](50-SDE-04-runtime-characterization.md) |
| Verification | [60-SVP](60-SVP-software-verification-plan.md) and [61-01-VTS](61-01-VTS-timing-application-verification-test-specification.md) |
| User guidance | [70-01-SUM](70-01-SUM-headless-timing-application.md) |
| Documentation rules | [12-GPD](12-GPD-documentation-guide.md) |
| Engineering traceability model and Sphinx-Needs integration | [13-GPD](13-GPD-engineering-traceability.md) |
| Unresolved ideas | [00-brainstorm](00-brainstorm.md) |

## Working context

- [00-brainstorm](00-brainstorm.md) — unresolved ideas and alternatives.
- [02-agent-plan](02-agent-plan.md) — meta-repository coordination using AP-*.
- [03-domain-baseline](03-domain-baseline.md) — shared domain facts and terminology.
- [20-EXT](20-EXT-external-system-inputs.md) — controlled external/parent-system inputs.

Working context does not replace promoted requirements, interfaces or design.

## System interfaces

- [32-03-ISD — Application control/status](32-03-ISD-application-control-status.md)
- [33-03-IDD — API HTTP/WebSocket design](33-03-IDD-api-http-websocket.md)
- [32-04-ISD — Web interface](32-04-ISD-web-interface.md)
- [32-05-ISD — TimingData interchange](32-05-ISD-timingdata-interchange.md)
- [33-05-IDD — TimingData reference design](33-05-IDD-timingdata-interchange.md)
- [32-11-ISD — Application configuration](32-11-ISD-application-configuration.md)

## Software items

### SI-01 — Timing Point Application

- [41-01-SSD](41-01-SSD-timing-application-specification-document.md)
- [43-01-SDD-01](43-01-SDD-01-data-and-display-design.md)
- [43-01-SDD-02](43-01-SDD-02-java-component-design.md)
- [43-01-SDD-03](43-01-SDD-03-backoffice-transport-design.md)
- [44-01-GPD — Java design rules](44-01-GPD-java-design-rules.md)

### SI-02 — Desktop GUI Application

- [41-02-SSD](41-02-SSD-gui-application-specification-document.md)

## Generated views

Merged source is published to
[prod/docs](https://github.com/brainboxemb/2026-010-01.meta.event-timing-software/tree/prod/docs).

Useful generated entrypoints:
- [Engineering portal](https://brainboxemb.github.io/2026-010-01.meta.event-timing-software/)
- [Architecture/specification book](https://github.com/brainboxemb/2026-010-01.meta.event-timing-software/blob/prod/docs/documents/architecture-book.md)
- [Complete software document set](https://github.com/brainboxemb/2026-010-01.meta.event-timing-software/blob/prod/docs/documents/software-document-set.md)
- [Generated SIP planning](https://github.com/brainboxemb/2026-010-01.meta.event-timing-software/tree/prod/docs/planning)

Generated material is review/navigation output. Edit the authored source documents here,
not generated branches.

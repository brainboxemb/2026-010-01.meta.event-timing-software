# 2026-010-01.meta.event-timing-software

Planning and research for a reusable Java framework for event timing and time registration.

## Purpose

This repository is the coordination and research space for the project. It is used to collect source material, explore ideas, structure decisions, define the development/verification environment, and prepare implementation work before software-specific repositories are created or changed.

Ideas and unresolved software topics belong in [`docs/00-brainstorm.md`](docs/00-brainstorm.md) first. Stable requirements and architecture should only be introduced after the relevant topics have been discussed and promoted deliberately. Early planning/design documents may contain explicitly marked working drafts used to prepare those later authoritative documents.

## Working documents

- [`AGENTS.md`](AGENTS.md) — persistent guidance for coding and research agents.
- [`docs/00-brainstorm.md`](docs/00-brainstorm.md) — working area for ideas, questions, alternatives, and early software thoughts.
- [`docs/01-handoff.md`](docs/01-handoff.md) — reusable context handoff for starting a new chat or agent session.
- [`docs/02-agent-plan.md`](docs/02-agent-plan.md) — meta-project/agent plan; uses `AP-*` identifiers to remain distinct from SIP software steps.
- [`docs/03-domain-baseline.md`](docs/03-domain-baseline.md) — working domain facts/terminology such as registration-system IDs, locations, source sequences, team/tag identity and reference data.
- [`docs/10-SDP-software-development-plan.md`](docs/10-SDP-software-development-plan.md) — high-level phased software development plan.
- [`docs/11-SIP-software-implementation-planning.md`](docs/11-SIP-software-implementation-planning.md) — concrete implementation sequence, scope and exit criteria.
- [`docs/12-SDE-software-development-environment.md`](docs/12-SDE-software-development-environment.md) — common development environment, GitHub/AI workflow and repository conventions.
- [`docs/30-SSAD-software-system-architecture.md`](docs/30-SSAD-software-system-architecture.md) — software-item register, interface catalogue and software-system architecture working draft.
- [`docs/31-01-SAD-timing-application-architecture.md`](docs/31-01-SAD-timing-application-architecture.md) — software item 01, headless timing application architecture.
- [`docs/31-01-SDD-01-timing-system-design.md`](docs/31-01-SDD-01-timing-system-design.md) — software item 01 detailed timing-system design.
- [`docs/31-01-SDD-02-data-and-display-design.md`](docs/31-01-SDD-02-data-and-display-design.md) — software item 01 detailed data/display design.
- [`docs/31-01-SDD-03-java-component-design.md`](docs/31-01-SDD-03-java-component-design.md) — software item 01 Java/Maven component/package design.
- [`docs/31-02-SAD-gui-application-architecture.md`](docs/31-02-SAD-gui-application-architecture.md) — software item 02, desktop GUI architecture.
- [`docs/31-03-SAD-web-operator-application-architecture.md`](docs/31-03-SAD-web-operator-application-architecture.md) — software item 03, React/browser/iPad operator architecture.
- [`docs/50-SVP-software-verification-plan.md`](docs/50-SVP-software-verification-plan.md) — system-level verification strategy including Pi Zero/resource and fault-injection evidence.
- [`reference/README.md`](reference/README.md) — index and conventions for collected reference material.
- [`CHANGELOG.md`](CHANGELOG.md) — notable repository changes.

Generated documentation for an active pull request is published to `dev/pr-<N>/docs`; merged/default-branch documentation is published to `prod/docs`.

## Document ordering convention

Software documents use numeric prefixes so GitHub presents them predictably. Established abbreviations include:

- `SDP` — Software Development Plan;
- `SIP` — Software Implementation Planning;
- `SDE` — Software Development Environment;
- `SRD` — Software Requirements Document;
- `SSAD` — Software System Architecture Document;
- `SAD` — Software Architecture Document;
- `SDD` — Software Detailed Design;
- `IDD` — Interface Design/Description Document;
- `SVP` — Software Verification Plan.

Current top-level document families:

```text
00-09  working context / brainstorm / handoff / agent coordination / domain baseline
10-19  development planning and development environment
20-29  requirements / SRDs
30-39  architecture and detailed design
40-49  software-system interface documents (IDDs)
50-59  verification and validation planning
```

### Software-item numbering

Within software-item documentation, the software-item number is stable across requirements and design documents.

Current working software-item register:

```text
SI-01  Headless Timing Application
SI-02  Desktop GUI Application
SI-03  Web Operator Application (React/browser/iPad)
```

Examples:

```text
20-01-SRD-...                 requirements for software item 01
20-02-SRD-...                 requirements for software item 02
20-03-SRD-...                 requirements for software item 03

31-01-SAD-...                 architecture for software item 01
31-01-SDD-01-...              first detailed-design document for software item 01
31-01-SDD-02-...              second detailed-design document for software item 01

31-02-SAD-...                 architecture for software item 02
31-03-SAD-...                 architecture for software item 03
```

The software-item number therefore does not change merely because another SDD is added.

## Documentation levels

The project intentionally separates:

- **brainstorm** — ideas, candidate requirements, alternatives and unresolved questions;
- **domain baseline** — supplied domain facts/terminology that later requirements/design must preserve or explicitly revise;
- **SDP** — overall development approach and phased evolution;
- **SIP** — concrete implementation sequence and exit criteria;
- **SDE** — common tooling, repository and development-process environment;
- **system requirements / SSAD / IDDs** — software-system-level behaviour, architecture and interfaces;
- **software-item SRD / SAD / SDD** — requirements, architecture and detailed design for each software item;
- **SVP** — system-level verification strategy and evidence model;
- **agent plan (`AP-*`)** — coordination steps for work performed in this meta repository and across agent/chat sessions.

Detailed implementation evidence for an active software step should live primarily in that step's pull request rather than turning long-term planning documents into activity logs.

## Traceability direction

The intended chain is:

```text
system/domain source
  -> system requirement
  -> system IDD where applicable
  -> software-item SRD
  -> SAD / SDD
  -> implementation
  -> verification case/evidence
```

System-level IDDs own interface definitions; software-item SRDs reference applicable interface obligations instead of duplicating them.

## Workflow

Normal changes follow the PR-first workflow defined in the SDE: issue/work item → `feature/pr-N-...` branch → draft PR → implementation/test/evidence → review → merge.

The repository intentionally starts with structure, brainstorming, planning and architecture exploration. Candidate requirements and current design documents remain non-authoritative until explicitly promoted.

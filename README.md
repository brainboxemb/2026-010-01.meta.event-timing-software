# 2026-010-01.meta.event-timing-software

Planning and research for a reusable Java framework for event timing and time registration.

## Purpose

This repository is the coordination and research space for the project. It is used to collect source material, explore ideas, structure decisions, and prepare implementation work before software-specific repositories are created or changed.

Ideas and unresolved software topics belong in [`docs/00-brainstorm.md`](docs/00-brainstorm.md) first. Stable requirements and architecture should only be introduced after the relevant topics have been discussed and promoted deliberately. Early planning documents may contain explicitly marked working drafts used to prepare those later authoritative documents.

## Working documents

- [`AGENTS.md`](AGENTS.md) — persistent guidance for coding and research agents.
- [`docs/00-brainstorm.md`](docs/00-brainstorm.md) — working area for ideas, questions, alternatives, and early software thoughts.
- [`docs/01-handoff.md`](docs/01-handoff.md) — reusable context handoff for starting a new chat or agent session.
- [`docs/02-agent-plan.md`](docs/02-agent-plan.md) — current phased meta-project/agent plan and progress source of truth.
- [`docs/10-SDP-software-development-plan.md`](docs/10-SDP-software-development-plan.md) — phased high-level software development plan.
- [`docs/11-software-implementation-roadmap.md`](docs/11-software-implementation-roadmap.md) — concrete current sequence of software increments.
- [`docs/30-SSAD-software-system-architecture.md`](docs/30-SSAD-software-system-architecture.md) — working software-system architecture document.
- [`docs/31-SAD-timing-system-architecture.md`](docs/31-SAD-timing-system-architecture.md) — architecture detail for one logical timing system.
- [`docs/32-SDD-data-and-display-design.md`](docs/32-SDD-data-and-display-design.md) — detailed design for traceable data, ready-team state and display behaviour.
- [`docs/33-SDD-java-component-structure.md`](docs/33-SDD-java-component-structure.md) — Java/Maven component, package and public/private extension structure.
- [`reference/README.md`](reference/README.md) — index and conventions for collected reference material.
- [`CHANGELOG.md`](CHANGELOG.md) — notable repository changes.

Generated architecture diagrams for an active pull request are published to `dev/pr-<N>/docs`; merged/main documentation is published to `prod/docs`.

## Document ordering convention

Software documents use a numeric prefix so GitHub presents them in a predictable lifecycle-oriented order. Stable document-type abbreviations are used where the type is meaningful:

- `SDP` — Software Development Plan;
- `SDE` — Software Development Environment;
- `SSAD` — Software System Architecture Document;
- `SAD` — Software Architecture Document;
- `SDD` — Software Detailed Design;
- `IDD` — Interface Design/Description Document;
- `SVP` — Software Verification Plan.

Current number ranges are intended as stable document families rather than strict execution phases:

```text
00-09  working context / brainstorm / handoff / agent coordination
10-19  development planning and development environment
20-29  requirements
30-39  architecture and detailed design
40-49  system-level interface documents (IDDs)
50-59  verification and validation planning
```

This leaves room to add documents later without renaming the complete set.

## Planning levels

The project intentionally keeps three planning levels separate:

- **brainstorm** — ideas, possible requirements, alternatives, and unresolved questions;
- **software development plan/roadmap** — staged product/software evolution and concrete implementation increments;
- **agent plan** — coordination steps for work performed in this meta repository and across chat/agent sessions.

Detailed implementation evidence for an active software step should live primarily in that step's pull request rather than turning the long-term planning documents into activity logs.

## Workflow

Normal changes follow a pull-request-first workflow. Work should start from a numbered issue/draft pull request, continue on a matching feature branch, and keep discussion and evidence attached to that pull request.

The repository intentionally starts with structure, brainstorming, planning, and architecture exploration. Candidate requirements and the current architecture/design documents are not yet treated as final system requirements or authoritative architecture.

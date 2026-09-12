# 2026-010-01.meta.event-timing-software

Planning and research for a reusable Java framework for event timing and time registration.

## Purpose

This repository is the coordination and research space for the project. It is used to collect source material, explore ideas, structure decisions, and prepare implementation work before software-specific repositories are created or changed.

Ideas and unresolved software topics belong in [`docs/brainstorm.md`](docs/brainstorm.md) first. Stable requirements and architecture should only be introduced after the relevant topics have been discussed and promoted deliberately. Early planning documents may contain explicitly marked working drafts used to prepare those later authoritative documents.

## Working documents

- [`AGENTS.md`](AGENTS.md) — persistent guidance for coding and research agents.
- [`docs/agent-plan.md`](docs/agent-plan.md) — current phased meta-project/agent plan and progress source of truth.
- [`docs/handoff.md`](docs/handoff.md) — reusable context handoff for starting a new chat or agent session.
- [`docs/brainstorm.md`](docs/brainstorm.md) — working area for ideas, questions, alternatives, and early software thoughts.
- [`docs/software-architecture-sketch.md`](docs/software-architecture-sketch.md) — non-authoritative first system architecture sketch used to prepare implementation.
- [`docs/timing-system-architecture.md`](docs/timing-system-architecture.md) — detailed non-authoritative `TimingSystem` architecture, pseudocode, device/network flows, and candidate requirements.
- [`docs/data-and-display-architecture.md`](docs/data-and-display-architecture.md) — refinement for in-memory repositories with simple file backup, start-time synchronisation, keypad add/remove behaviour, and V1/V2 display semantics.
- [`docs/software-plan.md`](docs/software-plan.md) — staged high-level software evolution plan.
- [`docs/software-planning.md`](docs/software-planning.md) — concrete current sequence of software increments.
- [`reference/README.md`](reference/README.md) — index and conventions for collected reference material.
- [`CHANGELOG.md`](CHANGELOG.md) — notable repository changes.

Generated architecture diagrams for an active pull request are published to `dev/pr-<N>/docs`; merged/main documentation is published to `prod/docs`. This keeps source documents reviewable on the normal branch while making generated SVG/draw.io output directly inspectable during review.

## Planning levels

The project intentionally keeps three planning levels separate:

- **brainstorm** — ideas, possible requirements, alternatives, and unresolved questions;
- **software plan/planning** — staged product/software evolution and concrete implementation increments;
- **agent plan** — coordination steps for work performed in this meta repository and across chat/agent sessions.

Detailed implementation evidence for an active software step should live primarily in that step's pull request rather than turning the long-term planning documents into activity logs.

## Workflow

Normal changes follow a pull-request-first workflow. Work should start from a numbered issue/draft pull request, continue on a matching feature branch, and keep discussion and evidence attached to that pull request.

The repository intentionally starts with structure, brainstorming, planning, and architecture exploration. Candidate requirements and the architecture sketch are not yet treated as final system requirements or authoritative architecture.

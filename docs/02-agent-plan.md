# Agent plan

This document is the current phased work plan for the meta project.

Agent-plan steps use the prefix `AP-` so they cannot be confused with numbered software implementation steps in the SIP.

## Working rules

- Work one agent-plan step at a time unless a later step is needed to correct the plan itself.
- Record software ideas and unresolved design topics in `docs/00-brainstorm.md` before promoting them into authoritative documents.
- Keep this repository focused on planning, research, coordination, and decision preparation.
- Keep project documentation generic and independent of any specific real-world event.
- Keep detailed current-step work and evidence in the active pull request rather than expanding this plan into an activity log.

## AP-0 — Repository bootstrap

Status: in progress

Goal: establish a stable repository structure and working method before the first implementation repository is created.

Scope:

- repository purpose and navigation;
- `AGENTS.md`;
- `CHANGELOG.md`;
- this agent plan;
- reusable handoff document;
- brainstorm document;
- ordered software-document convention;
- reference-material area;
- PR-first working method;
- generated documentation/review output;
- initial non-authoritative SDP, SIP, SDE, SVP and architecture/design working documents needed to prepare later formalisation.

Exit criteria:

- the core documents exist and have clearly separated responsibilities;
- a new chat can continue from `AGENTS.md`, this plan, `docs/01-handoff.md`, and the current PR state;
- early software discussion has a defined landing place in `docs/00-brainstorm.md`;
- the document set has a predictable numbering/type convention;
- software-item numbering and system/software-item document ownership are understandable;
- generated documentation can be reviewed from `dev/pr-<N>/docs`;
- early requirements/architecture/design material remains explicitly non-authoritative until promoted;
- no implementation repository is created accidentally as part of bootstrap.

## AP-1 — Collect and structure source material

Status: not started

Goal: gather the existing documents and other source material relevant to the future framework and make them traceable and reviewable.

Expected work:

- collect source documents;
- index each source with origin, date/version where known, and relevance;
- identify overlaps, contradictions, assumptions, and missing information;
- capture emerging software questions in `docs/00-brainstorm.md` rather than resolving them prematurely.

Detailed scope will be refined after the initial document set is known.

## AP-2 — Formalise software/domain direction

Status: not started

Goal: use the collected source material, brainstorm, SDP, architecture working drafts, candidate requirements, interface catalogue, and verification strategy to determine what is mature enough to promote into authoritative software-system requirements, software-item SRDs, architecture, and IDDs.

Do not automatically promote every candidate requirement or design idea. Explicitly resolve conflicts and open questions first.

## Later agent-plan steps

Implementation-repository creation, formal software-item decomposition, and implementation execution will be planned only when the meta-project evidence is mature enough. The SDP/SIP may describe likely software phases before those agent steps are activated, but that does not authorise agents to implement them early.

# Agent plan

This document is the current phased work plan for the meta project.

Agent-plan steps use the prefix `AP-` so they cannot be confused with numbered software implementation steps in the SIP.

## Working rules

- Work one agent-plan step at a time unless a later step is needed to correct the plan itself.
- Record software ideas and unresolved design topics in `docs/00-brainstorm.md` before promoting them into authoritative documents.
- Keep this repository focused on planning, research, coordination, and decision preparation.
- Keep project documentation generic and independent of any specific real-world event.
- Keep detailed current-step work and evidence in the active pull request rather than expanding this plan into an activity log.
- Do not create documents merely to satisfy a process pattern; new documents need a distinct engineering purpose and consumer as defined by `AGENTS.md`.
- Mature requirements, interfaces and design **just in time for the capability being implemented**. Future capability documentation may remain outline-level until a later SIP step needs it.

## AP-0 — Repository bootstrap

Status: completed

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

### AP-0 closure evidence

The closure review was performed in PR #1.

At closure:

- SDP, SIP, SDE and SVP responsibilities are separated explicitly;
- public/private information boundaries are recorded in `AGENTS.md` and the architecture/design working drafts;
- generated Markdown, diagrams, architecture books and the printable SIP roadmap build successfully in CI;
- the SIP roadmap includes effort/calendar planning plus scope-aware documentation maturity for REQ/SRD, IDD, SAD/SDD and SVP/evidence;
- generated A3 roadmap pages were visually inspected rather than accepted from CI status alone;
- unresolved topics remain visible as working/open items;
- formal requirements and IDDs for later capabilities remain deliberately deferred;
- the next meta-project step is scoped around only the first executable slice rather than broad speculative formalisation.

## AP-1 — Formalise the first executable slice

Status: not started

Goal: make only the requirements, interfaces and verification material needed for the first SI-01 executable sufficiently concrete to begin implementation without inventing externally visible behaviour inside implementation PRs.

This step is intentionally **just-in-time**. It does not attempt to formalise the full future timing system.

Expected scope:

- identify the use cases and behaviours needed by SIP Steps 2–3;
- create the initial `20-01-SRD` scope for SI-01 startup/shutdown, build/version identity, status, minimal lifecycle/configuration and other first-executable behaviour;
- create the first system-level application-control/status IDD needed by the executable and later clients;
- establish a traceable example from use case → system requirement → IDD where applicable → SI-01 requirement → SAD/SDD → verification case;
- make the relevant ST-1/SVP verification material concrete enough for the first executable;
- update SAD/SDD working drafts only where the formalised slice exposes a conflict or ambiguity;
- collect/index source material only where it is needed to resolve this slice;
- keep RFID, CAN, displays, backoffice and other later capability requirements/IDDs at outline level unless this step exposes a true foundational dependency.

Deliverable:

> A small, reviewable first-executable requirements/interface/verification baseline that is sufficient to start SI-01 implementation without prematurely formalising later capabilities.

Exit criteria:

- the first executable's externally visible behaviour is traceable and reviewable;
- the application-control/status interface boundary is concrete enough for implementation and ST-1 verification;
- implementation can begin without inventing core public semantics in the implementation repository;
- later capability requirements remain explicitly deferred rather than being expanded for completeness alone;
- relevant generated documentation and traceability views are reviewable in the active PR.

## AP-2 — Bootstrap the public implementation repository

Status: not started

Goal: after AP-1 is accepted, create the public implementation repository and execute the SIP framework-skeleton step using the approved SDE and first-executable baseline.

Expected direction:

- create the repository through the normal issue → branch → draft PR workflow;
- establish the SDE repository baseline (`README.md`, `AGENTS.md`, `CHANGELOG.md`);
- create the Maven/Java 8 framework skeleton from the documented component architecture;
- keep detailed implementation work/evidence in the implementation repository PR;
- feed material architecture/process corrections back to this meta repository through separate scoped work when needed.

## Ongoing supporting activity — source collection

Source collection is continuous and capability-driven rather than a mandatory stage that blocks all implementation.

When a current AP/SIP step needs source evidence:

- collect relevant source documents;
- index origin, date/version where known, and relevance;
- identify conflicts, assumptions and missing information;
- capture unresolved software questions in `docs/00-brainstorm.md`;
- avoid collecting or formalising unrelated material merely for completeness.

## Later agent-plan steps

Later formalisation, implementation increments, interface promotion and verification work should follow SIP/document-maturity needs. Add a new AP step when a distinct coordination goal has a clear deliverable; do not create AP steps merely to mirror every SIP step.
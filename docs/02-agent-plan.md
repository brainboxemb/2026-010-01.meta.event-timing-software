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

Status: completed — PR #2

Goal: make only the requirements, interfaces and verification material needed for the first SI-01 executable sufficiently concrete to begin implementation without inventing externally visible behaviour inside implementation PRs.

This step is intentionally **just-in-time**. It does not attempt to formalise the full future timing system.

Expected scope:

- identify the use cases and behaviours needed by the first executable;
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

### AP-1 closure evidence

PR #2 established the first reviewable SRD/IDD slice without expanding later product capabilities.

At closure:

- `20-01-SRD-timing-application-requirements.md` defines only startup/shutdown, external configuration, build/version identity, first status semantics and externally testable application behaviour;
- `40-01-IDD-application-control-status.md` owns IF-03 with concrete `/api/v1/version`, `/api/v1/status` and `/api/v1/events` contracts;
- IF-03 defines stable first build/status JSON fields, explicit error responses, compatibility rules and reconnect/resynchronisation behaviour;
- first-executable authentication is deliberately deferred while default network exposure remains loopback-only unless remote access is explicitly configured;
- the first operational timing instance remains `CLOSED`; open/close and later domain behaviour are not partially invented for this baseline;
- `VC-ST1-001` traces representative status/version behaviour from existing use cases through SI-01/IF-03 obligations to a black-box running-process verification scenario;
- remote-shell technology remains an implementation/support-adapter choice and does not receive an unnecessary standalone IDD yet;
- RFID, CAN, display, registration-domain and backoffice requirements remain deliberately deferred;
- generated documentation successfully published the review candidate to `dev/pr-2/docs` from the AP-1 head commit.

## AP-2 — Define reusable Java build/test toolchain baseline

Status: in progress — PR #3

Goal: establish the generic Java/Maven engineering toolchain before the first SI-01 implementation repository is bootstrapped.

This step was introduced deliberately after AP-1 because a source repository alone does not guarantee a reproducible cross-platform build/test environment.

Expected scope:

- define build/test **roles** separately from physical machines;
- define the initial Windows developer, GitHub Linux CI, GitHub Windows CI, Raspberry Pi target and optional integration-host matrix;
- adopt Maven Wrapper as the repository-owned Maven entry point;
- define Java 8 canonical build/source/bytecode policy;
- define one canonical platform-neutral Java artifact where feasible;
- define Linux canonical build and Windows compatibility/artifact-smoke responsibilities;
- define build provenance and artifact evidence;
- define the reusable `tool.java-project` boundary and versioned workflow-consumption direction;
- keep self-hosted build/test infrastructure optional until a real need is demonstrated;
- keep Docker outside the normal Java compile/unit-test path;
- decide what must exist before SI-01 can become the first real toolchain consumer.

Deliverable:

> A reviewable Java toolchain baseline that tells a future implementation repository how a clean checkout is built, tested and packaged across the first supported environments, and what reusable tooling belongs outside the product repository.

Exit criteria:

- Maven Wrapper policy is explicit;
- canonical build/artifact producer is explicit;
- Windows and Linux build/test responsibilities are explicit;
- target Pi execution is separated from normal hosted CI build responsibility;
- reusable-tool ownership and versioning/pinning direction are explicit;
- no timing-domain/product behaviour is moved into generic tooling;
- dedicated self-hosted infrastructure remains optional until justified;
- generated SDE documentation is reviewable and green.

## AP-3 — Implement reusable Java toolchain repository

Status: not started

Goal: realise the AP-2 baseline as a reusable public Java engineering-tool repository before SI-01 becomes its first product consumer.

Working repository name:

```text
tool.java-project
```

Expected direction:

- create the tool repository through the normal issue → branch → draft PR workflow;
- provide versioned reusable GitHub Actions workflow(s) for Java 8 verification/artifact production;
- validate Maven Wrapper use rather than requiring runner-global Maven;
- define/pin the initial hosted JDK distribution and Maven version through tested configuration;
- produce build/test reports plus artifact provenance;
- verify Linux canonical build and Windows compatibility paths with a minimal generic fixture/reference consumer;
- prove that the exact canonical artifact can be downloaded and executed by a compatibility job once the fixture contains a runnable Java artifact;
- document workflow inputs/outputs and consumer pinning/version policy;
- keep timing-domain, Pi-image and proprietary integration logic out of the reusable tool repository.

Deliverable:

> A versioned reusable Java toolchain with its own green CI and a minimal generic consumer/fixture that proves the workflow can be adopted independently of SI-01.

Exit criteria:

- generic toolchain repository exists and follows the SDE repository baseline;
- Linux and Windows workflow paths execute successfully;
- Maven/JDK versions are explicit and reproducible;
- toolchain output includes useful reports/artifact provenance;
- a consumer can pin an immutable toolchain version/ref;
- no SI-01 source is required to test the generic toolchain;
- the toolchain is ready for SI-01 to become its first real consumer.

## AP-4 — Bootstrap the public SI-01 implementation repository

Status: not started

Goal: after AP-1 through AP-3 are accepted, create the public SI-01/framework implementation repository and execute the SIP framework-skeleton increment using the proven reusable Java toolchain.

Expected direction:

- create the repository through the normal issue → branch → draft PR workflow;
- consume the versioned Java toolchain rather than inventing CI/build conventions locally;
- establish the SDE repository baseline (`README.md`, `AGENTS.md`, `CHANGELOG.md`);
- include the Maven Wrapper in the implementation repository;
- create the Maven/Java 8 framework skeleton from the documented component architecture;
- keep detailed implementation work/evidence in the implementation repository PR;
- feed material architecture/process/toolchain corrections back to the appropriate coordination/tool repository through separate scoped work when needed.

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
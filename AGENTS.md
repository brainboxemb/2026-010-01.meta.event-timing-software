# Repository agent guidance

Persistent guidance for automated agents working in `2026-010-01.meta.event-timing-software`.

## Purpose

This repository coordinates planning, research, source collection, development/verification-environment definition, and decision preparation for a reusable Java framework for event timing and time registration.

It is a meta repository. Do not treat it as the implementation repository for the framework itself unless the project plan explicitly changes that boundary.

## Documentation boundary

Keep repository documentation generic. Do not identify or name a specific real-world event that motivated the project.

This is a public repository. Do not copy live/proprietary deployment inventory into it merely because those details were supplied in a chat or private source. In particular, keep the following out of public source/documentation unless publication is explicitly approved:

- real registration-box/asset names;
- concrete external registration-system/source IDs and their actual mappings;
- reserve/virtual source assignments;
- real deployment topology/inventory;
- proprietary protocol values/field mappings;
- credentials, encryption keys or secrets.

When such details are useful for architecture reasoning, capture only the reusable structural rule in the public repository and use generic placeholders such as `asset-01`, `source-01`, `system-01`, or `RS-<asset-key>-ANT1`. Actual deployment mappings belong in private repositories or external/private configuration.

Software ideas, possible requirements, technology choices, architecture options, and unresolved questions must first be captured in `docs/00-brainstorm.md`.

Stable domain facts/terminology supplied by project sources or the user may be consolidated in `docs/03-domain-baseline.md`. That document is not itself a formal requirements specification; later SRDs/IDDs/designs must preserve or explicitly revise those facts. Apply the public/private boundary above when consolidating domain knowledge.

System-level operational goals and actor scenarios may be consolidated in `docs/04-UC-system-use-cases.md`. Use cases are inputs to later requirements/interfaces and verification; they are not themselves implementation design or test cases.

Do not promote brainstorm content into authoritative requirements or architecture merely because it sounds plausible. Promotion should happen only after explicit discussion or a plan step that calls for it.

Working drafts such as the UC, SDP, SIP, SDE, SSAD, SAD, SDD and SVP documents may organise already-discussed direction before formal requirements/architecture exist. They must remain clearly marked as non-authoritative until explicitly promoted.

## Document naming and ordering

Use the repository's numbered document families. Do not add new unnumbered software documents when an existing family applies.

```text
00-09  working context / brainstorm / handoff / agent coordination / domain baseline / use cases
10-19  development planning and development environment
20-29  requirements / SRDs
30-39  architecture and detailed design
40-49  software-system interface documents (IDDs)
50-59  verification and validation planning
```

Use established abbreviations when applicable, including `UC`, `SDP`, `SIP`, `SDE`, `SRD`, `SSAD`, `SAD`, `SDD`, `IDD`, and `SVP`.

When a software-item number is used, keep it stable across that software item's requirements/design documents.

Current working software-item register:

```text
SI-01  Headless Timing Application
SI-02  Desktop GUI Application
SI-03  Web Operator Application
```

The agent plan uses `AP-*` identifiers so its coordination steps cannot be confused with SIP implementation steps.

## Sources of truth

Use these documents for their specific roles:

```text
README.md                                          repository purpose and navigation
AGENTS.md                                          persistent agent rules
docs/00-brainstorm.md                              ideas, candidate requirements, alternatives
docs/01-handoff.md                                 reusable session handoff
docs/02-agent-plan.md                              AP-* meta-project/agent work plan and progress
docs/03-domain-baseline.md                         supplied domain facts/terminology and unresolved mappings
docs/04-UC-system-use-cases.md                     system operational goals/use cases and alternative flows
docs/10-SDP-software-development-plan.md           high-level phased software development
docs/11-SIP-software-implementation-planning.md    concrete software implementation sequence
docs/12-SDE-software-development-environment.md    common tooling/GitHub/AI/repository workflow
docs/30-SSAD-software-system-architecture.md       software-item register, interface catalogue and system architecture
docs/31-01-SAD-timing-application-architecture.md  SI-01 architecture
docs/31-01-SDD-*                                   SI-01 detailed design
docs/31-02-SAD-gui-application-architecture.md     SI-02 architecture
docs/31-03-SAD-web-operator-application-architecture.md  SI-03 architecture
docs/50-SVP-software-verification-plan.md          system-level verification strategy
reference/                                         collected source material and its index
CHANGELOG.md                                       notable repository changes
```

Future system-level IDDs in the `40-49` family own interface definitions. Software-item SRDs may reference applicable IDD obligations but should not duplicate interface definitions.

When documents disagree, prefer the more specific source for that topic. Do not silently resolve material conflicts; record or surface them. A material conflict with `03-domain-baseline.md` or an established use-case goal must be made explicit rather than silently designing around it.

## Working method

1. Read `AGENTS.md` and `docs/02-agent-plan.md` before substantial work.
2. Read `docs/01-handoff.md` when continuing work from another session.
3. Check the relevant open pull request and the latest completed pull request as directed by the handoff.
4. Read `docs/03-domain-baseline.md` when work depends on domain identifiers, registration semantics, tag/team identity, locations, or source sequencing.
5. Read `docs/04-UC-system-use-cases.md` when work changes externally meaningful system behaviour, actor flows, failure/recovery scenarios or system-test intent.
6. Read `docs/12-SDE-software-development-environment.md` before changing repository/workflow/tooling conventions.
7. Read the SSAD/software-item design and SVP relevant to the current work.
8. Capture genuinely new software ideas in `docs/00-brainstorm.md` before turning them into decisions.
9. Use the SDP for high-level staged evolution and the SIP for the current software implementation sequence.
10. Keep research and verification evidence traceable to its source.
11. Update the plan when a step is completed, materially changed, or blocked.
12. Keep implementation details in the future implementation repository rather than duplicating them here.

## Pull-request-first workflow

Follow the SDE. In summary:

1. reserve/use a work number through an issue where appropriate;
2. create `feature/pr-N-<short-slug>` from the intended target branch;
3. create/promote the work into a draft PR early;
4. continue implementation on the same branch while the draft PR remains open;
5. keep implementation detail, tests, discussion and evidence in that PR;
6. inspect generated `dev/pr-N/...` outputs where relevant;
7. mark ready and merge only when the scoped work and evidence are complete.

Do not perform normal work directly on `main`.

## Generated output

Generated branches such as `dev/pr-N/docs` and `prod/docs` are build output. Do not hand-edit them as source.

Use generated output as review evidence: inspect actual rendered/generated artifacts before merge where visual or generated behaviour matters.

## AI development discipline

AI agents use the same controlled GitHub workflow as human developers. Do not create an AI-only bypass around issues, branches, pull requests, tests or review evidence.

Do not claim tests, generated output inspection or hardware verification occurred unless it actually occurred.

When private/proprietary details are present in the working conversation, use them only to derive the required generic architecture/contract unless the target repository is explicitly private and those details belong there.

## Document lifecycle

While the project is consolidating source/domain knowledge, use cases and design documents may remain `working draft / non-authoritative`.

Preferred future lifecycle:

```text
working draft
review candidate
accepted / authoritative
superseded
```

Promotion is explicit. Generated review copies do not become authoritative merely because they render successfully.

## Change discipline

Prefer small, reviewable steps. Do not introduce implementation code, framework dependencies, or premature directory structures while the project is still in the planning/research phase unless the active plan explicitly calls for them.

When collecting documents or external information:

- preserve original files where appropriate;
- add enough metadata to identify the source and relevance;
- distinguish source facts from project interpretation;
- avoid copying volatile facts into multiple documents;
- avoid copying proprietary deployment identities from private sources into public repository documents.

## Handoff discipline

Before ending a substantial work session, update `docs/02-agent-plan.md` if progress changed and keep `docs/01-handoff.md` usable as a stable entry point for the next session. The handoff should point to sources of truth rather than attempting to duplicate the complete current state.

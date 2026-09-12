# Repository agent guidance

Persistent guidance for automated agents working in `2026-010-01.meta.event-timing-software`.

## Purpose

This repository coordinates planning, research, source collection, and decision preparation for a reusable Java framework for event timing and time registration.

It is a meta repository. Do not treat it as the implementation repository for the framework itself unless the project plan explicitly changes that boundary.

## Documentation boundary

Keep repository documentation generic. Do not identify or name a specific real-world event that motivated the project.

Software ideas, possible requirements, technology choices, architecture options, and unresolved questions must first be captured in `docs/00-brainstorm.md`.

Do not promote brainstorm content into authoritative requirements or architecture merely because it sounds plausible. Promotion should happen only after explicit discussion or a plan step that calls for it.

Working drafts such as the software development plan, implementation roadmap, and architecture/design documents may organise already-discussed direction before formal requirements/architecture exist. They must remain clearly marked as non-authoritative until explicitly promoted.

## Document naming and ordering

Use the repository's numbered document families. Do not add new unnumbered software documents when an existing family applies.

```text
00-09  working context / brainstorm / handoff / agent coordination
10-19  development planning and development environment
20-29  requirements
30-39  architecture and detailed design
40-49  system-level interface documents (IDDs)
50-59  verification and validation planning
```

Use established document abbreviations when applicable, including `SDP`, `SDE`, `SSAD`, `SAD`, `SDD`, `IDD`, and `SVP`.

## Sources of truth

Use these documents for their specific roles:

```text
README.md                                      repository purpose and navigation
AGENTS.md                                      persistent agent rules
docs/00-brainstorm.md                          ideas, candidate requirements, alternatives, early thinking
docs/01-handoff.md                             reusable session handoff
docs/02-agent-plan.md                          meta-project/agent work plan and progress
docs/10-SDP-software-development-plan.md       phased high-level software development
docs/11-software-implementation-roadmap.md     current concrete software increment sequence
docs/30-SSAD-software-system-architecture.md   software-system architecture working draft
docs/31-SAD-timing-system-architecture.md      timing-system architecture detail
docs/32-SDD-data-and-display-design.md         detailed data/display design
docs/33-SDD-java-component-structure.md        Java/Maven component and package design
reference/                                     collected source material and its index
CHANGELOG.md                                   notable repository changes
```

When documents disagree, prefer the more specific source for that topic. Do not silently resolve material conflicts; record or surface them.

## Working method

1. Read `AGENTS.md` and `docs/02-agent-plan.md` before substantial work.
2. Read `docs/01-handoff.md` when continuing work from another session.
3. Check the relevant open pull request and the latest completed pull request as directed by the handoff.
4. Capture new software ideas in `docs/00-brainstorm.md` before turning them into decisions.
5. Use `docs/10-SDP-software-development-plan.md` for high-level staged software evolution and `docs/11-software-implementation-roadmap.md` for the current increment sequence.
6. Keep research evidence traceable to its source.
7. Update the plan when a step is completed, materially changed, or blocked.
8. Keep implementation details in the future implementation repository rather than duplicating them here.

## Pull-request-first workflow

Use the same generic PR-first discipline used by the project's tooling repositories:

1. reserve a number with an issue when issue-to-PR conversion is available;
2. create `feature/pr-N-<short-slug>` from the current target branch;
3. make the smallest useful initial change;
4. convert that exact issue into draft pull request `#N`;
5. continue work on the same branch while the draft PR remains open;
6. attach validation, discussion, and evidence to that PR;
7. mark ready and merge only when the scoped work is complete.

If issue-to-PR conversion is unavailable, use a descriptive feature branch and a normal draft PR. Never fabricate number alignment.

## Change discipline

Prefer small, reviewable steps. Do not introduce implementation code, framework dependencies, or premature directory structures while the project is still in the planning/research phase unless the active plan explicitly calls for them.

When collecting documents or external information:

- preserve original files where appropriate;
- add enough metadata to identify the source and relevance;
- distinguish source facts from project interpretation;
- avoid copying volatile facts into multiple documents.

## Handoff discipline

Before ending a substantial work session, update `docs/02-agent-plan.md` if progress changed and keep `docs/01-handoff.md` usable as a stable entry point for the next session. The handoff should point to sources of truth rather than attempting to duplicate the complete current state.

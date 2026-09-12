# Handoff

Use this document as the stable entry point when continuing the project in a new chat or agent session.

## Start here

Read, in order:

1. `AGENTS.md`
2. `docs/agent-plan.md`
3. `docs/brainstorm.md`
4. any source documents or references explicitly named by the active plan step

Then continue only with the currently active plan step unless later work is required to correct the plan itself.

## Reusable handoff message

> Work from `2026-010-01.meta.event-timing-software` as the coordination and research source.
>
> Read `AGENTS.md`, `docs/agent-plan.md`, `docs/handoff.md`, and `docs/brainstorm.md`.
>
> Continue with the currently active step in `docs/agent-plan.md`. Do not start later steps unless the active step requires a correction to the plan.
>
> New software ideas, possible requirements, architecture choices, and unresolved questions must first be captured in `docs/brainstorm.md`. Do not present them as settled design unless they have explicitly been promoted.
>
> Keep repository documentation generic and do not name the specific real-world event that motivated the project.
>
> At the end of the work, update plan status/evidence and the changelog where useful, while keeping implementation details out of this meta repository.

## Session-end check

Before handing off substantial work:

- update the active plan step when its status or evidence changed;
- add unresolved software topics to `docs/brainstorm.md`;
- add or update reference metadata when new source material was used;
- update `CHANGELOG.md` for notable repository changes;
- leave the repository in a state that another session can understand from the sources of truth above.

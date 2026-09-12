# Handoff

Use this document as the stable entry point when continuing the project in a new chat or agent session.

## Start here

Read and inspect, in order:

1. `AGENTS.md`
2. the current GitHub pull-request state for this repository
3. `docs/agent-plan.md`
4. `docs/brainstorm.md`
5. `docs/software-architecture-sketch.md`
6. `docs/software-plan.md`
7. `docs/software-planning.md`
8. any source documents or references explicitly named by the active plan step

### Pull-request state check

Before deciding what work is current, inspect GitHub rather than relying only on the Markdown documents:

1. list the currently open pull requests;
2. identify the open/draft pull request that represents the active work, if one exists;
3. read its description, commits/changed files, discussion, and recorded evidence that are relevant to the active step;
4. also identify the most recently closed or merged pull request and inspect it when it provides the immediate predecessor context;
5. if no relevant pull request is open, use the most recently completed pull request together with `docs/agent-plan.md` to determine the next step.

Treat the pull request as the detailed work/evidence record for the active step. Treat `docs/agent-plan.md` as the longer-lived coordination plan. Treat `docs/software-plan.md` and `docs/software-planning.md` as the software-evolution plan rather than as agent/session activity logs. Do not assume that a branch name or an old handoff statement is current without checking GitHub state.

Then continue only with the currently active agent-plan step unless later work is required to correct the plan itself.

## Reusable handoff message

> Work from `2026-010-01.meta.event-timing-software` as the coordination and research source.
>
> Read `AGENTS.md`, `docs/handoff.md`, `docs/agent-plan.md`, `docs/brainstorm.md`, `docs/software-architecture-sketch.md`, `docs/software-plan.md`, and `docs/software-planning.md`.
>
> Before deciding what is current, inspect the repository's pull requests. Check which PR is currently open/draft and read the relevant description, changes, discussion, and evidence. Also inspect the most recently closed/merged PR when it provides predecessor context. If no relevant PR is open, use the most recently completed PR together with `docs/agent-plan.md` to determine the next agent step.
>
> Continue with the currently active step in `docs/agent-plan.md`. Do not start later agent steps unless the active step requires a correction to the plan.
>
> Use `docs/software-plan.md` for the staged software direction and `docs/software-planning.md` for the current software increment sequence. Keep software-step implementation details and evidence in the corresponding implementation pull request.
>
> New software ideas, possible requirements, architecture choices, and unresolved questions must first be captured in `docs/brainstorm.md`. Do not present them as settled design unless they have explicitly been promoted.
>
> Keep repository documentation generic and do not name the specific real-world event that motivated the project.
>
> At the end of the work, update plan status/evidence and the changelog where useful. Keep detailed active-step work and evidence in the pull request rather than turning the long-term plans into activity logs.

## Session-end check

Before handing off substantial work:

- make sure the active pull request contains enough description/evidence for the next session to understand the current step;
- update the active agent-plan step when its status or high-level evidence changed;
- update software planning only when the staged software roadmap itself changed;
- add unresolved software topics to `docs/brainstorm.md`;
- add or update reference metadata when new source material was used;
- update `CHANGELOG.md` for notable repository changes;
- leave the repository in a state that another session can reconstruct from the current PR state plus the sources of truth above.

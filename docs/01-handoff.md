# Handoff

Use this document as the stable entry point when continuing the project in a new chat or agent session.

## Start here

Read and inspect, in order:

1. `AGENTS.md`
2. the current GitHub pull-request state for this repository
3. `docs/02-agent-plan.md`
4. `docs/00-brainstorm.md`
5. `docs/10-SDP-software-development-plan.md`
6. `docs/11-SIP-software-implementation-planning.md`
7. `docs/12-SDE-software-development-environment.md`
8. `docs/30-SSAD-software-system-architecture.md`
9. the relevant software-item `SRD` / `SAD` / `SDD` documents for the current topic
10. applicable system-level `IDD` documents when they exist
11. `docs/50-SVP-software-verification-plan.md` when verification/evidence/testability is relevant
12. any source documents or references explicitly named by the active plan step

### Pull-request state check

Before deciding what work is current, inspect GitHub rather than relying only on Markdown documents:

1. list the currently open pull requests;
2. identify the open/draft pull request that represents the active work, if one exists;
3. read its description, commits/changed files, discussion, and recorded evidence relevant to the active step;
4. also identify the most recently closed or merged pull request and inspect it when it provides immediate predecessor context;
5. inspect generated `dev/pr-<N>/...` output for the active PR when generated artifacts are part of the review;
6. if no relevant pull request is open, use the most recently completed pull request together with `docs/02-agent-plan.md` to determine the next step.

Treat the pull request as the detailed work/evidence record for the active step. Treat `docs/02-agent-plan.md` as the longer-lived **AP-*** coordination plan. Treat the SDP/SIP as software-evolution planning, the SDE as the common development-environment/workflow definition, and the SVP as the common verification strategy. Do not assume that a branch name or an old handoff statement is current without checking GitHub state.

Then continue only with the currently active `AP-*` agent-plan step unless later work is required to correct the plan itself.

## Current software-item register

```text
SI-01  Headless Timing Application
SI-02  Desktop GUI Application
SI-03  Web Operator Application (React/browser/iPad)
```

The software-item number is stable across that item's SRD/SAD/SDD documents. It is not a document sequence number.

The SSAD owns the current software-item/interface catalogue. System-owned interfaces are documented through IDDs and may be referenced as applicable requirements by software-item SRDs.

## Reusable handoff message

> Work from `2026-010-01.meta.event-timing-software` as the coordination and research source.
>
> Read `AGENTS.md`, `docs/01-handoff.md`, `docs/02-agent-plan.md`, `docs/00-brainstorm.md`, `docs/10-SDP-software-development-plan.md`, `docs/11-SIP-software-implementation-planning.md`, `docs/12-SDE-software-development-environment.md`, `docs/30-SSAD-software-system-architecture.md`, the relevant software-item design documents, and `docs/50-SVP-software-verification-plan.md` when applicable.
>
> Before deciding what is current, inspect the repository's pull requests. Check which PR is currently open/draft and read the relevant description, changes, discussion and evidence. Also inspect the most recently closed/merged PR when it provides predecessor context. Inspect the generated `dev/pr-N/...` branch when the active PR generates review artifacts. If no relevant PR is open, use the most recently completed PR together with `docs/02-agent-plan.md` to determine the next agent step.
>
> Continue with the currently active `AP-*` step in `docs/02-agent-plan.md`. Do not start later agent steps unless the active step requires a correction to the plan.
>
> Use the SDP for staged software direction, the SIP for the implementation sequence, the SDE for GitHub/tooling/AI/repository workflow, and the SVP for verification strategy. Keep implementation details and evidence in the corresponding implementation PR.
>
> New software ideas, possible requirements, architecture choices and unresolved questions must first be captured in `docs/00-brainstorm.md`. Do not present them as settled design unless they have explicitly been promoted.
>
> Keep repository documentation generic and do not name the specific real-world event that motivated the project.
>
> At the end of the work, update plan status/evidence and the changelog where useful. Keep detailed active-step work and evidence in the PR rather than turning long-term plans into activity logs.

## Session-end check

Before handing off substantial work:

- make sure the active PR contains enough description/evidence for the next session to understand the current step;
- inspect generated review output when applicable;
- update the active `AP-*` step when its status or high-level evidence changed;
- update SDP/SIP only when the staged software direction itself changed;
- update SDE only when common tooling/workflow/environment rules changed;
- update SVP when verification strategy/evidence expectations materially change;
- add unresolved software topics to `docs/00-brainstorm.md`;
- add/update reference metadata when new source material was used;
- update `CHANGELOG.md` for notable repository changes;
- leave the repository in a state that another session can reconstruct from current PR state plus the sources of truth above.

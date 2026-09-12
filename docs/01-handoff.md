# Handoff

Use this document as the stable entry point when continuing the project in a new chat or agent session.

## Start here

Read and inspect, in order:

1. `AGENTS.md`
2. resolve the active work repository and GitHub pull-request state using the rules below
3. `docs/02-agent-plan.md`
4. `docs/00-brainstorm.md`
5. `docs/03-domain-baseline.md`
6. `docs/10-SDP-software-development-plan.md`
7. `docs/11-SIP-software-implementation-planning.md`
8. `docs/12-SDE-software-development-environment.md`
9. `docs/30-SSAD-software-system-architecture.md`
10. the relevant software-item `SRD` / `SAD` / `SDD` documents for the current topic
11. applicable system-level `IDD` documents when they exist
12. `docs/50-SVP-software-verification-plan.md` when verification/evidence/testability is relevant
13. any source documents or references explicitly named by the active plan step

### Repository resolution

`brainboxemb/2026-010-01.meta.event-timing-software` is the **coordination and research repository**. Start here to determine the active AP/SIP scope, but do not assume that the active implementation pull request is also in this repository.

Current repository map:

```text
brainboxemb/2026-010-01.meta.event-timing-software
  coordination, planning, requirements, architecture, verification direction

brainboxemb/2026-010-02.java.event-timing-framework
  public SI-01 Java framework/application implementation

brainboxemb/tool.eng-docs
  reusable engineering-documentation tooling

brainboxemb/tool.java-project
  reusable Java build/test tooling

brainboxemb/tool.git-project
  reusable Git/repository tooling
```

Resolve the active work repository as follows:

1. start in this meta repository and inspect the active `AP-*` / SIP scope plus any open meta PR;
2. identify every implementation/tool repository explicitly named by that active plan step, issue, PR description or handoff context;
3. inspect the open/draft PR in the named implementation/tool repository before deciding what work is current;
4. when the active work is SI-01 implementation, use `brainboxemb/2026-010-02.java.event-timing-framework` as the current public implementation repository;
5. when the active work is the engineering-document extraction/tooling, use `brainboxemb/tool.eng-docs`;
6. inspect `tool.java-project`, `tool.git-project`, or another supporting repository only when the active work explicitly depends on or changes it;
7. do not infer that the newest PR in this meta repository is automatically the active implementation PR.

A single project step may therefore have a coordination PR here and an implementation PR in another repository. The implementation PR owns detailed implementation/test evidence; the meta repository owns longer-lived cross-project coordination and software-system documentation.

### Pull-request state check

Before deciding what work is current, inspect GitHub rather than relying only on Markdown documents:

1. list the currently open pull requests in the meta repository;
2. resolve the active implementation/tool repository using the repository-resolution rules above;
3. list the open pull requests there and identify the open/draft PR that represents the active work, if one exists;
4. read its description, commits/changed files, discussion, and recorded evidence relevant to the active step;
5. also identify the most recently closed or merged pull request in the relevant repository and inspect it when it provides immediate predecessor context;
6. inspect generated `dev/pr-<N>/...` output for the active PR when generated artifacts are part of the review;
7. if no relevant pull request is open, use the most recently completed PR together with `docs/02-agent-plan.md` and the SIP to determine the next step and repository.

Treat the relevant pull request as the detailed work/evidence record for the active step. Treat `docs/02-agent-plan.md` as the longer-lived **AP-*** coordination plan. Treat `docs/03-domain-baseline.md` as working domain knowledge/terminology rather than formal requirements. Treat the SDP/SIP as software-evolution planning, the SDE as the common development-environment/workflow definition, and the SVP as the common verification strategy. Do not assume that a branch name or an old handoff statement is current without checking GitHub state.

Then continue only with the currently active `AP-*` / SIP scope unless later work is required to correct the plan itself.

## Current software-item register

```text
SI-01  Headless Timing Application
SI-02  Desktop GUI Application
SI-03  Web Operator Application (React/browser/iPad)
```

The software-item number is stable across that item's SRD/SAD/SDD documents. It is not a document sequence number.

The SSAD owns the current software-item/interface catalogue. System-owned interfaces are documented through IDDs and may be referenced as applicable requirements by software-item SRDs.

## Reusable handoff message

> Work from `brainboxemb/2026-010-01.meta.event-timing-software` as the coordination and research source. Do not assume that the active implementation PR is in the meta repository.
>
> Read `AGENTS.md`, `docs/01-handoff.md`, `docs/02-agent-plan.md`, `docs/00-brainstorm.md`, `docs/03-domain-baseline.md`, `docs/10-SDP-software-development-plan.md`, `docs/11-SIP-software-implementation-planning.md`, `docs/12-SDE-software-development-environment.md`, `docs/30-SSAD-software-system-architecture.md`, the relevant software-item design documents, and `docs/50-SVP-software-verification-plan.md` when applicable.
>
> First inspect the meta repository's current PR/AP/SIP state. Then resolve every implementation/tool repository named by the active work and inspect its open/draft PR before deciding what is current. SI-01 public implementation lives in `brainboxemb/2026-010-02.java.event-timing-framework`; reusable engineering-document tooling lives in `brainboxemb/tool.eng-docs`. Inspect `tool.java-project`, `tool.git-project`, or another supporting repository only when the active work explicitly uses or changes it.
>
> Read the relevant active PR description, changes, discussion and evidence. Also inspect the most recently closed/merged PR in that repository when it provides predecessor context. Inspect generated `dev/pr-N/...` output when the active PR generates review artifacts. If no relevant PR is open, use the most recently completed PR together with `docs/02-agent-plan.md` and the SIP to determine the next step and repository.
>
> Continue with the currently active `AP-*` / SIP scope. Do not start later work unless the active step requires a correction to the plan.
>
> Use the domain baseline for supplied domain facts/terminology, the SDP for staged software direction, the SIP for the implementation sequence, the SDE for GitHub/tooling/AI/repository workflow, and the SVP for verification strategy. Keep implementation details and evidence in the corresponding implementation PR.
>
> New software ideas, possible requirements, architecture choices and unresolved questions must first be captured in `docs/00-brainstorm.md`. Do not present them as settled design unless they have explicitly been promoted.
>
> Keep repository documentation generic and do not name the specific real-world event that motivated the project.
>
> At the end of the work, update plan status/evidence and the changelog where useful. Keep detailed active-step work and evidence in the PR rather than turning long-term plans into activity logs.

## Session-end check

Before handing off substantial work:

- make sure the active PR in each repository involved contains enough description/evidence for the next session to understand the current step;
- inspect generated review output when applicable;
- update the active `AP-*` step when its status or high-level evidence changed;
- update the domain baseline when new domain facts/terminology are supplied or corrected;
- update SDP/SIP only when the staged software direction itself changed;
- update SDE only when common tooling/workflow/environment rules changed;
- update SVP when verification strategy/evidence expectations materially change;
- add unresolved software topics to `docs/00-brainstorm.md`;
- add/update reference metadata when new source material was used;
- update `CHANGELOG.md` for notable repository changes;
- leave the project in a state that another session can reconstruct from the meta coordination state plus the active implementation/tool PRs and sources of truth above.

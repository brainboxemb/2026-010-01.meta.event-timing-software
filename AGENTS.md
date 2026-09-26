# Repository agent guidance

This repository is the project-family coordination authority for the event-timing
software project. It owns planning, requirements, architecture, interface design,
verification strategy and cross-repository coordination. Product implementation
belongs in the implementation repositories.

Before substantial work:

1. read [README.md](README.md) for repository purpose/navigation;
2. read [docs/02-agent-plan.md](docs/02-agent-plan.md) and, when continuing work,
   [docs/01-handoff.md](docs/01-handoff.md);
3. read the current shared BrainboxEmb agent entrypoint:
   [brainboxemb.meta/AGENTS.md](https://github.com/brainboxemb/brainboxemb.meta/blob/main/AGENTS.md).

The shared entrypoint owns current generic Git/commit/PR/CI working rules and
routes to portfolio repository-tooling conventions such as GitHub Actions
workflow naming.

Do not inherit `AGENTS.md` from pinned tools or implementation dependencies as
working policy for this repository. Exact pinned dependency behaviour comes from
this repository's configuration/gitlinks/immutable workflow refs plus the pinned
dependency's README, docs, source and tests.

## Local project authorities

Use the numbered project documents for their specific roles:

- [docs/00-brainstorm.md](docs/00-brainstorm.md) — ideas, alternatives and unresolved questions;
- [docs/03-domain-baseline.md](docs/03-domain-baseline.md) — stable domain facts/terminology;
- [docs/04-UC-system-use-cases.md](docs/04-UC-system-use-cases.md) — operational goals/use cases;
- [docs/10-SDP-software-development-plan.md](docs/10-SDP-software-development-plan.md) — development strategy/risks;
- [docs/11-SIP-software-implementation-planning.md](docs/11-SIP-software-implementation-planning.md) — implementation sequence/deliverables/evidence;
- [docs/12-SDE-software-development-environment.md](docs/12-SDE-software-development-environment.md) — local repository/workflow/tooling/environment conventions;
- [docs/30-SSAD-software-system-architecture.md](docs/30-SSAD-software-system-architecture.md) — software-system architecture/item register/interfaces;
- [docs/31-01-SAD-timing-application-architecture.md](docs/31-01-SAD-timing-application-architecture.md) — SI-01 architecture;
- [docs/31-01-SDD-02-java-component-design.md](docs/31-01-SDD-02-java-component-design.md) — active Java component/package/artifact design;
- [docs/31-02-SAD-gui-application-architecture.md](docs/31-02-SAD-gui-application-architecture.md) — desktop GUI architecture;
- [docs/50-SVP-software-verification-plan.md](docs/50-SVP-software-verification-plan.md) — verification strategy/evidence model;
- [reference/README.md](reference/README.md) — collected source-material index;
- [CHANGELOG.md](CHANGELOG.md) — notable repository changes.

When repository/workflow/tooling conventions change, read the SDE **and** the
current shared BrainboxEmb guidance before editing.

## Documentation and architecture discipline

The documentation is leading during the current architecture/brainstorm phase.
Existing implementation/API/class names do not constrain the intended model;
implementation migrations can follow accepted documentation.

New software ideas, candidate requirements, technology choices and unresolved
architecture options start in the brainstorm unless an existing authoritative
project document already owns the decision.

Do not silently promote plausible brainstorm content into requirements or
architecture. Stable domain facts/use cases/design decisions must be promoted
deliberately into their owning documents.

Keep implementation detail in the implementation repository. This repository
may define intended architecture/contracts and cross-repository evidence, but
should not become a second implementation source tree.

### Software-item naming in prose

In running architecture text, prefer the readable software-item name first and keep the
formal identifier after it, for example **Headless Timing Application** (SI-01),
**Desktop GUI Application** (SI-02). The current JavaFX client is engineering test tooling, not SI-02; an optional web test client is not a separate software item.
Use bare SI identifiers mainly in compact tables, diagrams, filenames and other formal
references.

Prefer plain application language over governance-heavy terms such as
`authoritative state` when normal ownership wording is sufficient. State what keeps or
owns the data directly, for example "timing state remains in the Headless Timing
Application". Reserve terms such as `authoritative` for cases where competing sources
of truth are actually being distinguished.

### Architecture figure references

Architecture figures use a visible stable label plus a Markdown anchor so reviews and
design text can refer to a figure unambiguously.

Use scope-based labels such as `Figure SYS-01` for the system SSAD and
`Figure SI01-01` for the SI-01 SAD. Put an anchor immediately before the image,
for example `<a id="fig-si01-01"></a>`, and a visible caption immediately after
it. Refer to it as `[Figure SI01-01](#fig-si01-01)` when linking within the same
document.

Figure identifiers are stable references: do **not** renumber existing figures when a
new diagram is inserted. Assign the next unused number in that document/scope. Where a
generated diagram has an authored source/title, include the same figure label in the
rendered title when practical.

## Public/private boundary

This is a public repository. Keep real/proprietary deployment identities,
external source mappings, reserve assignments, production topology, proprietary
protocol values, credentials, encryption keys and secrets out of public source
and documentation.

Use generic placeholders when concrete deployment examples are needed. Private
inventory/configuration stays in private/external sources.

## Working method

- inspect current issues, pull requests, CI and generated evidence live; do not
  reconstruct current state from old chat history;
- follow the local SDE for this repository's issue/branch/PR mechanics;
- use shared BrainboxEmb guidance for generic Git/commit/CI/tooling conventions;
- read the relevant architecture/verification documents before changing their
  domain;
- update the agent plan/handoff when a substantial work-session materially
  changes active progress;
- inspect generated `dev/pr-N/docs` output when visual/generated behaviour is
  part of the review question.

Keep this file as an entrypoint/navigation layer. Durable engineering knowledge
belongs in the owning project documents rather than being duplicated here.

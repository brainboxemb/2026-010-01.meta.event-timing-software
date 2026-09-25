# 2026-010-01.meta.event-timing-software

Planning and research for a reusable Java framework for event timing and time registration.

## Purpose

This repository is the coordination and research space for the project. It is used to collect source material, explore ideas, structure decisions, define the development/verification environment, and prepare implementation work before software-specific repositories are created or changed.

Ideas and unresolved software topics belong in [`docs/00-brainstorm.md`](docs/00-brainstorm.md) first. Stable requirements and architecture should only be introduced after the relevant topics have been discussed and promoted deliberately. Early planning/design documents may contain explicitly marked working drafts used to prepare those later authoritative documents.

## Generated documentation

The merged/default-branch documentation build is published to the generated [`prod/docs`](https://github.com/brainboxemb/2026-010-01.meta.event-timing-software/tree/prod/docs) branch. Useful entry points include:

- [architecture book](https://github.com/brainboxemb/2026-010-01.meta.event-timing-software/blob/prod/docs/documents/architecture-book.md) — assembled architecture/design view with generated diagrams;
- [complete software document set](https://github.com/brainboxemb/2026-010-01.meta.event-timing-software/blob/prod/docs/documents/software-document-set.md) — assembled generated document set;
- [planning output](https://github.com/brainboxemb/2026-010-01.meta.event-timing-software/tree/prod/docs/planning) — continuous SIP roadmap, four A4-landscape roadmap pages/PDF and A4-portrait step details;
- [generated architecture diagrams](https://github.com/brainboxemb/2026-010-01.meta.event-timing-software/tree/prod/docs/architecture) — SVG and editable draw.io outputs.

`prod/docs` is generated publication/review output. The authored source on `main` remains the source of truth and generated files should not be hand-edited. Active pull-request builds use `dev/pr-<N>/docs`.

### Local documentation tooling

Repository tooling is pinned through the shared project-file dependency model. From a normal clone, initialise the exact committed tooling revisions first:

```bash
./bootstrap.sh
```

or on Windows:

```powershell
.\bootstrap.ps1
```

`project.yml` owns the managed `tool.eng-docs` revision and `tools/tool.git-project` is the committed bootstrap gitlink. After bootstrap, install the Python documentation environment from the managed checkout:

```bash
python -m pip install -r tools/requirements-docs.txt
python -m pip install ./tools/tool.eng-docs
```

The GitHub documentation workflow follows the same path before invoking `eng-docs diagrams` and the project-specific generators. Do not replace this with an independently chosen `git+https` tool version in local setup or CI.

## Working documents

- [`AGENTS.md`](AGENTS.md) — persistent guidance for coding and research agents.
- [`docs/00-brainstorm.md`](docs/00-brainstorm.md) — working area for ideas, questions, alternatives, and early software thoughts.
- [`docs/01-handoff.md`](docs/01-handoff.md) — reusable context handoff for starting a new chat or agent session.
- [`docs/02-agent-plan.md`](docs/02-agent-plan.md) — meta-project/agent plan; uses `AP-*` identifiers to remain distinct from SIP software steps.
- [`docs/03-domain-baseline.md`](docs/03-domain-baseline.md) — working domain facts/terminology such as registration assets/sources, locations, source sequences, team/tag identity and reference data, while keeping real deployment identities private.
- [`docs/04-UC-system-use-cases.md`](docs/04-UC-system-use-cases.md) — system-level operational use cases connecting domain goals to later requirements, interfaces and verification scenarios.
- [`docs/10-SDP-software-development-plan.md`](docs/10-SDP-software-development-plan.md) — high-level development strategy: objectives, broad phases, risks, assumptions, resources and major unknowns.
- [`docs/11-SIP-software-implementation-planning.md`](docs/11-SIP-software-implementation-planning.md) — concrete implementation sequence with scope, deliverables, demonstrations and exit evidence.
- [`docs/12-SDE-software-development-environment.md`](docs/12-SDE-software-development-environment.md) — concrete engineering environment: repositories, GitHub workflow, tooling, CI, generated-output and development-host conventions.
- [`docs/13-SDE-java-build-test-toolchain.md`](docs/13-SDE-java-build-test-toolchain.md) — Java-specific refinement of the SDE covering build/test roles, Maven Wrapper, canonical artifacts, cross-platform CI and the reusable `tool.java-project` boundary.
- [`docs/20-01-SRD-timing-application-requirements.md`](docs/20-01-SRD-timing-application-requirements.md) — AP-1 working requirement baseline for the first SI-01 executable slice; later capabilities remain deliberately deferred.
- [`docs/30-SSAD-software-system-architecture.md`](docs/30-SSAD-software-system-architecture.md) — software-item register, interface catalogue and software-system architecture working draft.
- [`docs/31-01-SAD-timing-application-architecture.md`](docs/31-01-SAD-timing-application-architecture.md) — software item 01, headless timing application architecture and primary current technical design document.
- [`docs/31-01-SDD-01-data-and-display-design.md`](docs/31-01-SDD-01-data-and-display-design.md) — deferred software item 01 data/display detailed-design note.
- [`docs/31-01-SDD-02-java-component-design.md`](docs/31-01-SDD-02-java-component-design.md) — active focused software item 01 Java/Maven component/package detailed design.
- [`docs/31-01-SDD-03-backoffice-transport-design.md`](docs/31-01-SDD-03-backoffice-transport-design.md) — deferred software item 01 transport-independent backoffice detailed-design note.
- [`docs/31-02-SAD-gui-application-architecture.md`](docs/31-02-SAD-gui-application-architecture.md) — software item 02, desktop GUI architecture.
- [`docs/31-03-SAD-web-operator-application-architecture.md`](docs/31-03-SAD-web-operator-application-architecture.md) — software item 03, React/browser/iPad operator architecture.
- [`docs/40-01-IDD-application-control-status.md`](docs/40-01-IDD-application-control-status.md) — AP-1 working IF-03 application-control/status contract for the first executable slice.
- [`docs/40-02-IDD-application-configuration.md`](docs/40-02-IDD-application-configuration.md) — SI-01 deployment/configuration contract for TimingNodes, I/O assets, presentation bindings, platform/profile overlays and secret references.
- [`docs/50-SVP-software-verification-plan.md`](docs/50-SVP-software-verification-plan.md) — system-level verification strategy, test profiles and evidence model including Pi Zero/resource and fault-injection verification.
- [`docs/60-01-SUM-headless-timing-application.md`](docs/60-01-SUM-headless-timing-application.md) — release-oriented SI-01 user manual with build/run instructions and compatibility matrix.
- [`reference/README.md`](reference/README.md) — index and conventions for collected reference material.
- [`CHANGELOG.md`](CHANGELOG.md) — notable repository changes.

Generated documentation for an active pull request is published to `dev/pr-<N>/docs`; merged/default-branch documentation is published to `prod/docs`.

## Document ordering convention

Software documents use numeric prefixes so GitHub presents them predictably. Established abbreviations include:

- `UC` — system use cases / operational scenarios;
- `SDP` — Software Development Plan;
- `SIP` — Software Implementation Planning;
- `SDE` — Software Development Environment;
- `SRD` — Software Requirements Document;
- `SSAD` — Software System Architecture Document;
- `SAD` — Software Architecture Document;
- `SDD` — Software Detailed Design;
- `IDD` — Interface Design/Description Document;
- `SVP` — Software Verification Plan;
- `SUM` — Software User Manual.

Current top-level document families:

```text
00-09  working context / brainstorm / handoff / agent coordination / domain baseline / use cases
10-19  development planning and development environment
20-29  requirements / SRDs
30-39  architecture and detailed design
40-49  software-system interface documents (IDDs)
50-59  verification and validation planning
60-69  software user / operator manuals
```

### Software-item numbering

Within software-item documentation, the software-item number is stable across requirements and design documents.

Current working software-item register:

```text
SI-01  Headless Timing Application
SI-02  Desktop GUI Application
SI-03  Web Operator Application (React/browser/iPad)
```

Examples:

```text
20-01-SRD-...                 requirements for software item 01
20-02-SRD-...                 requirements for software item 02
20-03-SRD-...                 requirements for software item 03

31-01-SAD-...                 architecture for software item 01
31-01-SDD-01-...              first current detailed-design document for software item 01
31-01-SDD-02-...              second current detailed-design document for software item 01

31-02-SAD-...                 architecture for software item 02
31-03-SAD-...                 architecture for software item 03

60-01-SUM-...                 release/user manual for software item 01
```

The software-item number therefore does not change merely because another SDD is added. During the current working-draft phase, retiring an SDD also compacts the SDD sequence so the current document set does not retain obsolete numbering gaps. Historical names remain available through Git history.

## Documentation levels

The project intentionally separates:

- **brainstorm** — ideas, candidate requirements, alternatives and unresolved questions;
- **domain baseline** — supplied domain facts/terminology that later requirements/design must preserve or explicitly revise;
- **use cases** — externally meaningful operational goals and scenarios used as input to requirements/interfaces and later verification;
- **SDP** — development management view: objectives, broad approach/phases, risks, assumptions, required resources/environments and major unknowns;
- **SIP** — implementation execution view: ordered steps, concrete deliverables, demonstrations and exit evidence;
- **SDE** — engineering-environment view: repository layout, GitHub/branch/PR workflow, tooling, CI, generated artifacts, developer/target environment conventions;
- **system requirements / SSAD / IDDs** — software-system-level behaviour, architecture and interfaces;
- **software-item SRD / SAD / SDD** — requirements, architecture and detailed design for each software item;
- **SVP** — verification strategy, levels/test profiles and evidence model;
- **SUM** — release/user view: compatible runtime/tool baselines plus install, configuration, run/stop and troubleshooting guidance for a software item;
- **agent plan (`AP-*`)** — coordination steps for work performed in this meta repository and across agent/chat sessions.

The SDP should not duplicate the detailed SIP sequence, and the SDE should not become a second development plan. Detailed implementation evidence for an active software step should live primarily in that step's pull request.

## Traceability direction

The intended chain is:

```text
system/domain source
  -> system use case where applicable
  -> system requirement where a distinct system-level obligation needs to be owned
  -> system IDD where applicable
  -> software-item SRD
  -> SAD / SDD
  -> implementation
  -> verification case/evidence
```

Use cases capture operational intent and may lead to multiple system/software requirements and verification scenarios. System-level IDDs own interface definitions; software-item SRDs reference applicable interface obligations instead of duplicating them. Do not introduce an additional requirements document when it would only duplicate an already well-owned software-item or interface obligation.

## Workflow

Normal changes follow the PR-first workflow defined in the SDE: issue/work item → `feature/pr-N-...` branch → draft PR → implementation/test/evidence → review → merge.

The repository intentionally starts with structure, brainstorming, planning and architecture exploration. Candidate requirements and current design documents remain non-authoritative until explicitly promoted.

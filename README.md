# 2026-010-01.meta.event-timing-software

Planning and research for a reusable Java framework for event timing and time registration.

## Purpose

This repository is the coordination and research space for the project. It is used to collect source material, explore ideas, structure decisions, define the development/verification environment, and prepare implementation work before software-specific repositories are created or changed.

Ideas and unresolved software topics belong in [`docs/00-brainstorm.md`](docs/00-brainstorm.md) first. Stable requirements and architecture should only be introduced after the relevant topics have been discussed and promoted deliberately. Early planning/design documents may contain explicitly marked working drafts used to prepare those later authoritative documents.

## Generated documentation

The merged/default-branch documentation build is published to the generated [`prod/docs`](https://github.com/brainboxemb/2026-010-01.meta.event-timing-software/tree/prod/docs) branch. Useful entry points include:

- [architecture book](https://github.com/brainboxemb/2026-010-01.meta.event-timing-software/blob/prod/docs/documents/architecture-book.md) — assembled architecture/design view with generated diagrams;
- [complete software document set](https://github.com/brainboxemb/2026-010-01.meta.event-timing-software/blob/prod/docs/documents/software-document-set.md) — assembled generated document set;
- [engineering portal publication](https://github.com/brainboxemb/2026-010-01.meta.event-timing-software/tree/prod/docs/portal) — derived Material static site with search, generated object pages and a clickable SI-01 engineering explorer;
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


### Refresh the SIP actual-effort snapshot

The committed roadmap snapshot stays deterministic and is not recalculated during the documentation build.

The normal project workflow is GitHub-native: run **Actions → Refresh SIP actuals → Run workflow**. By default the workflow uses the current date in `Europe/Amsterdam`, recalculates the planning indication across both event-timing repositories, validates the updated planning source and creates a **draft pull request** only when the rounded snapshot changes. A different inclusive snapshot date can be supplied as `YYYY-MM-DD`, and update creation can be disabled for a report-only run.

The update flow uses repository secret `SNAPSHOT_TOKEN`, shared with the daily-snapshot automation. For SIP actuals it needs **Contents: write** and **Pull requests: write** permission. The calculation itself uses normal read-only GitHub API access.

For local development/debugging, the same calculation can be run directly:

```bash
python tools/calculate_sip_actuals.py --through YYYY-MM-DD
python tools/calculate_sip_actuals.py --through YYYY-MM-DD --update
```

The calculator uses commits from merged pull requests in the meta and implementation repositories, gives each commit a 30-minute activity window, merges overlapping windows, and divides the resulting hours by 8. The project total merges all repository activity. Per-step actuals use the same method after assigning PRs through the explicit SIP-step PR boundaries in `sip-roadmap.yaml`.

The roadmap deliberately treats **original estimate**, **actual** and **remaining estimate** as separate planning signals. `original - actual` is therefore not expected to equal `remaining`; a difference is useful re-estimation evidence. The result remains a planning indication, not time registration.

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
- [`docs/20-SSSD-software-system-specification-document.md`](docs/20-SSSD-software-system-specification-document.md) — combined software-system requirements and architecture, software-item allocation and interface catalogue.
- [`docs/21-03-IDD-application-control-status.md`](docs/21-03-IDD-application-control-status.md) — system-owned IF-03 Remote API contract.
- [`docs/21-11-IDD-application-configuration.md`](docs/21-11-IDD-application-configuration.md) — system-owned IF-11 deployment/configuration contract.
- [`docs/30-01-SISD-timing-application-specification-document.md`](docs/30-01-SISD-timing-application-specification-document.md) — combined SI-01 requirements and architecture.
- [`docs/30-02-SISD-gui-application-specification-document.md`](docs/30-02-SISD-gui-application-specification-document.md) — SI-02 specification/architecture working baseline.
- [`docs/31-01-SDD-01-data-and-display-design.md`](docs/31-01-SDD-01-data-and-display-design.md) — deferred software item 01 data/display detailed-design note.
- [`docs/31-01-SDD-02-java-component-design.md`](docs/31-01-SDD-02-java-component-design.md) — active focused software item 01 Java/Maven component/package detailed design.
- [`docs/31-01-SDD-03-backoffice-transport-design.md`](docs/31-01-SDD-03-backoffice-transport-design.md) — deferred software item 01 transport-independent backoffice detailed-design note.
- [`docs/50-SVP-software-verification-plan.md`](docs/50-SVP-software-verification-plan.md) — system-level verification strategy, test profiles and evidence model.
- [`docs/60-01-SUM-headless-timing-application.md`](docs/60-01-SUM-headless-timing-application.md) — release-oriented SI-01 user manual with build/run instructions and compatibility matrix.
- [`reference/README.md`](reference/README.md) — index and conventions for collected reference material.
- [`CHANGELOG.md`](CHANGELOG.md) — notable repository changes.

Generated documentation for an active pull request is published to `dev/pr-<N>/docs`; merged/default-branch documentation is published to `prod/docs`.

## Document ordering convention

Software documents use numeric prefixes to show **authority level before document subtype**.

Established abbreviations include:

- `UC` — system use cases / operational scenarios;
- `SDP` — Software Development Plan;
- `SIP` — Software Implementation Planning;
- `SDE` — Software Development Environment;
- `SSSD` — Software System Specification Document;
- `IDD` — Interface Design/Description Document;
- `SISD` — Software Item Specification Document;
- `SDD` — Software Detailed Design;
- `SVP` — Software Verification Plan;
- `SUM` — Software User Manual.

Current top-level document families:

```text
00-09  working context / domain baseline / system use cases
10-19  development planning and development environment
20-29  software-system specification and system-owned interface documents
30-39  software-item specifications and focused detailed design
50-59  verification and validation planning
60-69  software user / operator manuals
```

### System and software-item numbering

The system specification is deliberately separated from software-item specifications:

```text
20-SSSD                    software-system requirements + architecture
21-03-IDD                  first system-owned detailed interface contract
21-11-IDD                  second system-owned detailed interface contract

30-01-SISD                 software item 01 requirements + architecture
30-02-SISD                 software item 02 requirements + architecture
31-01-SDD-01               first focused detailed design for software item 01
31-01-SDD-02               second focused detailed design for software item 01

60-01-SUM                  release/user manual for software item 01
```

`21-xx-IDD` uses the **system interface number** as `xx`: IF-03 is `21-03-IDD`, IF-11 is `21-11-IDD`. The IDD document number therefore stays aligned with the interface catalogue rather than creating a second interface numbering scheme.

The software-item number remains stable across that item's SISD/SDDs. During the current
working-draft phase, retiring an SDD may still compact the SDD sequence; historical names
remain available through Git history.

## Documentation levels

The project intentionally separates:

- **brainstorm/domain/use cases** — source knowledge and externally meaningful operational intent;
- **SDP/SIP/SDE** — project/development control. These documents schedule and govern work but are not product-requirement inputs merely because they mention a capability;
- **SSSD** — combined software-system requirements and architecture, including software-item/interface allocation;
- **system IDDs** — system-owned interface contracts. Externally imposed IDDs may precede the SSSD; internally allocated IDDs normally follow the SSSD and then constrain affected SISDs;
- **SISD** — combined requirements and architecture for one software item;
- **SDD** — focused detailed design downstream of the owning SISD;
- **SVP** — verification strategy and coverage/evidence model downstream of requirements/interfaces;
- **SUM** — release/user guidance for a released software item;
- **agent plan (`AP-*`)** — coordination history/work for this meta repository.

The exact normative dependency/release rules are owned by the SDP.

## Traceability direction

The normal product-document authority chain is:

```text
domain / use cases / external protocol or interface specification
                -> SSSD
                -> allocated system IDD(s)
                -> affected SISD(s)
                -> focused SDD(s)
                -> implementation
                -> verification evidence
```

An externally imposed IDD may sit before the SSSD instead of after it. Planning and
verification documents can reference this chain without becoming upstream product
authority.

## Workflow

Normal changes follow the PR-first workflow defined in the SDE: issue/work item → `feature/pr-N-...` branch → draft PR → implementation/test/evidence → review → merge.

The repository intentionally starts with structure, brainstorming, planning and architecture exploration. Candidate requirements and current design documents remain non-authoritative until explicitly promoted.

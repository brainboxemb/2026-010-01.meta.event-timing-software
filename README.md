# 2026-010-01.meta.event-timing-software

Planning and research for a reusable Java framework for event timing and time registration.

## Purpose

This repository is the coordination and research space for the project. It is used to collect source material, explore ideas, structure decisions, define the development/verification environment, and prepare implementation work before software-specific repositories are created or changed.

Ideas and unresolved software topics belong in [`docs/00-01-brainstorm.md`](docs/00-01-brainstorm.md) first. Stable requirements and architecture should only be introduced after the relevant topics have been discussed and promoted deliberately. Early planning/design documents may contain explicitly marked working drafts used to prepare those later authoritative documents.

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
- [`docs/00-01-brainstorm.md`](docs/00-01-brainstorm.md) — working area for ideas, questions, alternatives and early software thoughts.
- [`docs/00-02-handoff.md`](docs/00-02-handoff.md) — reusable context handoff for starting a new chat or agent session.
- [`docs/00-03-agent-plan.md`](docs/00-03-agent-plan.md) — meta-project/agent plan; uses `AP-*` identifiers to remain distinct from SIP software steps.
- [`docs/00-04-domain-baseline.md`](docs/00-04-domain-baseline.md) — working domain facts and terminology.
- [`docs/10-01-SDP-software-development-plan.md`](docs/10-01-SDP-software-development-plan.md) — development direction plus the generic document-category/dependency convention.
- [`docs/10-02-SIP-software-implementation-planning.md`](docs/10-02-SIP-software-implementation-planning.md) — concrete implementation sequence with scope, deliverables, demonstrations and exit evidence.
- [`docs/20-01-EXT-external-system-inputs.md`](docs/20-01-EXT-external-system-inputs.md) — register/baseline for requirements, IDDs, protocols and other controlled inputs owned by a parent or external system.
- [`docs/30-01-UC-system-use-cases.md`](docs/30-01-UC-system-use-cases.md) — software-system operational use cases.
- [`docs/30-02-SSSD-software-system-specification-document.md`](docs/30-02-SSSD-software-system-specification-document.md) — combined software-system requirements and architecture, software-item allocation and interface catalogue.
- [`docs/30-03-IDD-03-application-control-status.md`](docs/30-03-IDD-03-application-control-status.md) — system-owned IF-03 Remote API contract.
- [`docs/30-03-IDD-11-application-configuration.md`](docs/30-03-IDD-11-application-configuration.md) — system-owned IF-11 deployment/configuration contract.
- [`docs/40-01-01-SSD-timing-application-specification-document.md`](docs/40-01-01-SSD-timing-application-specification-document.md) — combined SI-01 requirements and architecture.
- [`docs/40-02-01-SSD-gui-application-specification-document.md`](docs/40-02-01-SSD-gui-application-specification-document.md) — SI-02 specification/architecture working baseline.
- [`docs/40-01-02-SDD-data-and-display-design.md`](docs/40-01-02-SDD-data-and-display-design.md) — deferred SI-01 data/display detailed-design note.
- [`docs/40-01-03-SDD-java-component-design.md`](docs/40-01-03-SDD-java-component-design.md) — active focused SI-01 Java/Maven component/package detailed design.
- [`docs/40-01-04-SDD-backoffice-transport-design.md`](docs/40-01-04-SDD-backoffice-transport-design.md) — deferred SI-01 transport-independent backoffice detailed-design note.
- [`docs/50-01-SDE-software-development-environment.md`](docs/50-01-SDE-software-development-environment.md) — repository/workflow/tooling/environment conventions.
- [`docs/50-02-SDE-java-build-test-toolchain.md`](docs/50-02-SDE-java-build-test-toolchain.md) — Java-specific build/test/toolchain refinement.
- [`docs/60-01-SVP-software-verification-plan.md`](docs/60-01-SVP-software-verification-plan.md) — verification strategy, test profiles and evidence model.
- [`docs/70-01-SUM-headless-timing-application.md`](docs/70-01-SUM-headless-timing-application.md) — release-oriented SI-01 user manual.
- [`reference/README.md`](reference/README.md) — index and conventions for collected reference material.
- [`CHANGELOG.md`](CHANGELOG.md) — notable repository changes.

Generated documentation for an active pull request is published to `dev/pr-<N>/docs`; merged/default-branch documentation is published to `prod/docs`.

## Document ordering convention

The first two digits are a **document category**, not an encoded dependency order. The SDP owns the detailed rule; the repository uses these categories consistently:

```text
00  working/project context
10  planning
20  external / parent-system inputs
30  software-system specification and design
40  software-item specification and design
50  development environment / engineering
60  verification and validation
70  user / operational documentation
```

Examples:

```text
10-01-SDP
10-02-SIP
20-01-EXT
30-01-UC
30-02-SSSD
30-03-IDD-03
30-03-IDD-11
40-01-01-SSD
40-01-SDD-01
40-02-01-SSD
50-01-SDE
50-02-SDE
60-01-SVP
70-01-SUM
```

For software-item documents, the software-item segment remains stable: `40-01-...` belongs to SI-01 and `40-02-...` to SI-02. Optional software-item use cases may use the same item segment, for example `40-01-UC-...`, when item-level behavioural decomposition adds value.

For system-owned IDDs, `30-03` identifies the IDD subgroup and the IDD suffix keeps the system interface identity, for example `IDD-03` for IF-03 and `IDD-11` for IF-11. External/parent-system IDDs keep their external identity and are registered under the category-20 external-input baseline rather than being renumbered as locally owned interfaces.

## Documentation levels

The project intentionally separates:

- **working context** — brainstorm, handoff, agent coordination and domain baseline;
- **planning** — SDP and SIP;
- **external/parent-system inputs** — controlled requirements, interface contracts, protocols and standards owned outside the current software-system scope;
- **software-system specification/design** — system use cases, SSSD and system-owned IDDs;
- **software-item specification/design** — optional item use cases, SSD and focused SDDs;
- **development environment/engineering** — SDE and toolchain/environment refinements;
- **verification/validation** — SVP and later verification specifications/cases/reports where a distinct document is justified;
- **user/operations** — release/user/operator guidance such as SUM;
- **agent plan (`AP-*`)** — coordination history/work for this meta repository.

Category numbers make those families easy to scan. Normative authority/release dependencies are expressed through document `Inputs` and traceability, not inferred from the numeric prefix.

## Traceability direction

A typical internally defined product-document chain is:

```text
domain baseline / system use cases / applicable parent-system inputs
                         -> SSSD
                         -> allocated system-owned IDD(s)
                         -> affected software-item use cases where useful
                         -> affected SSD(s)
                         -> focused SDD(s)
                         -> implementation
                         -> verification evidence
```

An externally owned requirement, IDD, protocol or standard remains upstream authority and may constrain the SSSD and, where allocated directly, an affected SSD. The category-20 register records that dependency without copying ownership into this repository.

Planning, engineering-environment and verification documents may reference this chain without becoming upstream product authority merely because of their document number.

## Workflow

Normal changes follow the PR-first workflow defined in the SDE: issue/work item → `feature/pr-N-...` branch → draft PR → implementation/test/evidence → review → merge.

The repository intentionally starts with structure, brainstorming, planning and architecture exploration. Candidate requirements and current design documents remain non-authoritative until explicitly promoted.

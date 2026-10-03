# 2026-010-01.meta.event-timing-software

Planning and research for the reusable Java core and applications for event timing and time registration.

## Purpose

This repository is the coordination and research space for the project. It is used to collect source material, explore ideas, structure decisions, define the development/verification environment, and prepare implementation work before software-specific repositories are created or changed.

Ideas and unresolved software topics belong in [`docs/00-brainstorm.md`](docs/00-brainstorm.md) first. Stable requirements and architecture should only be introduced after the relevant topics have been discussed and promoted deliberately. Early planning/design documents may contain explicitly marked working drafts used to prepare those later authoritative documents.

## Generated documentation

The merged/default-branch documentation build is published to the generated [`prod/docs`](https://github.com/brainboxemb/2026-010-01.meta.event-timing-software/tree/prod/docs) branch. Useful entry points include:

- [architecture book](https://github.com/brainboxemb/2026-010-01.meta.event-timing-software/blob/prod/docs/documents/architecture-book.md) — assembled architecture/design view with generated diagrams;
- [complete software document set](https://github.com/brainboxemb/2026-010-01.meta.event-timing-software/blob/prod/docs/documents/software-document-set.md) — assembled generated document set;
- [live engineering portal](https://brainboxemb.github.io/2026-010-01.meta.event-timing-software/) — derived Material site with search, generated object pages and the clickable SI-01 engineering explorer; [retained generated publication](https://github.com/brainboxemb/2026-010-01.meta.event-timing-software/tree/prod/docs/portal);
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

For a fresh ChatGPT/agent session, use the shared
[BrainboxEmb new-session handoff](https://github.com/brainboxemb/brainboxemb.meta/blob/main/docs/20-20-new-session-handoff.md).
This repository deliberately does not maintain a project-local handoff copy; current
state is reconstructed from the repository, active PRs, CI/evidence and the owning
project documents.

- [`AGENTS.md`](AGENTS.md) — persistent guidance for coding and research agents.
- [`docs/00-brainstorm.md`](docs/00-brainstorm.md) — working area for ideas, questions, alternatives and early software thoughts.
- [`docs/02-agent-plan.md`](docs/02-agent-plan.md) — meta-project/agent plan; uses `AP-*` identifiers to remain distinct from SIP software steps.
- [`docs/03-domain-baseline.md`](docs/03-domain-baseline.md) — working domain facts and terminology.
- [`docs/10-SDP-software-development-plan.md`](docs/10-SDP-software-development-plan.md) — project development direction, phases, resources and risks.
- [`docs/11-SIP-software-implementation-plan.md`](docs/11-SIP-software-implementation-plan.md) — concrete implementation sequence with scope, deliverables, demonstrations and exit evidence.
- [`docs/12-GPD-documentation-guide.md`](docs/12-GPD-documentation-guide.md) — document families, numbering, relationships and the rules for using [`docs/templates/`](docs/templates/README.md).
- [`docs/20-EXT-external-system-inputs.md`](docs/20-EXT-external-system-inputs.md) — register/baseline for requirements, IDDs, protocols and other controlled inputs owned by a parent or external system.
- [`docs/30-UC-system-use-cases.md`](docs/30-UC-system-use-cases.md) — software-system operational use cases.
- [`docs/31-SSSD-software-system-specification-document.md`](docs/31-SSSD-software-system-specification-document.md) — combined software-system requirements and architecture, software-item allocation and interface catalogue.
- [`docs/32-03-ISD-application-control-status.md`](docs/32-03-ISD-application-control-status.md) — system-owned IF-03 API semantic contract.
- [`docs/33-03-IDD-api-http-websocket.md`](docs/33-03-IDD-api-http-websocket.md) — IF-03 HTTP/JSON + WebSocket design.
- [`docs/32-04-ISD-web-interface.md`](docs/32-04-ISD-web-interface.md) — system-owned IF-04 Web interface contract.
- [`docs/32-05-ISD-timingdata-interchange.md`](docs/32-05-ISD-timingdata-interchange.md) — system-owned IF-05 TimingData specification.
- [`docs/33-05-IDD-timingdata-interchange.md`](docs/33-05-IDD-timingdata-interchange.md) — IF-05 default/reference JSON + JSON Lines design.
- [`docs/32-11-ISD-application-configuration.md`](docs/32-11-ISD-application-configuration.md) — system-owned IF-11 deployment/configuration contract.
- [`docs/41-01-SSD-timing-application-specification-document.md`](docs/41-01-SSD-timing-application-specification-document.md) — combined SI-01 requirements and architecture.
- [`docs/41-02-SSD-gui-application-specification-document.md`](docs/41-02-SSD-gui-application-specification-document.md) — SI-02 specification/architecture working baseline.
- [`docs/43-01-SDD-01-data-and-display-design.md`](docs/43-01-SDD-01-data-and-display-design.md) — active SI-01 data/runtime detailed design, including TimingNode ownership, operation flows, persistence and query isolation.
- [`docs/43-01-SDD-02-java-component-design.md`](docs/43-01-SDD-02-java-component-design.md) — active focused SI-01 Java/Maven component/package detailed design.
- [`docs/43-01-SDD-03-backoffice-transport-design.md`](docs/43-01-SDD-03-backoffice-transport-design.md) — deferred SI-01 transport-independent backoffice detailed-design note.
- [`docs/50-SDE-01-software-development-environment.md`](docs/50-SDE-01-software-development-environment.md) — repository/workflow/tooling/environment conventions.
- [`docs/50-SDE-02-java-build-test-toolchain.md`](docs/50-SDE-02-java-build-test-toolchain.md) — Java-specific build/test/toolchain refinement.
- [`docs/50-SDE-03-development-client.md`](docs/50-SDE-03-development-client.md) — Development Client architecture, UI baseline and reproducible screenshot/documentation direction.
- [`docs/60-SVP-software-verification-plan.md`](docs/60-SVP-software-verification-plan.md) — verification strategy, test profiles and evidence model.
- [`docs/61-01-VTS-timing-application-verification-test-specification.md`](docs/61-01-VTS-timing-application-verification-test-specification.md) — concrete SI-01 verification cases and expected results; execution status stays in retained evidence.
- [`docs/70-01-SUM-headless-timing-application.md`](docs/70-01-SUM-headless-timing-application.md) — release-oriented SI-01 user manual.
- [`reference/README.md`](reference/README.md) — index and conventions for collected reference material.
- [`CHANGELOG.md`](CHANGELOG.md) — notable repository changes.

Generated documentation for an active pull request is published to `dev/pr-<N>/docs`; merged/default-branch documentation is published to `prod/docs`.

## Document ordering convention

The leading number is a **document number/range**, not an encoded dependency order. The documentation guide owns the detailed rule; the repository uses these categories consistently:

```text
00–09  working/project context
10–19  project planning / guidance
20–29  external / parent-system inputs
30–39  software-system specification and design
40      software-item use cases
41      software-item requirements / combined specification
42      software-item architecture
43      software-item detailed design
50–59  development environment / engineering
60–69  verification and validation
70–79  user / operational documentation
```

Examples:

```text
00-brainstorm
02-agent-plan
03-domain-baseline
10-SDP
11-SIP
12-GPD-documentation-guide
20-EXT
30-UC
31-SSSD
32-03-ISD
32-04-ISD
32-05-ISD
32-11-ISD
33-03-IDD
33-05-IDD
40-01-UC        # reserved/optional SI-01 use-case document
41-01-SSD
41-02-SSD
43-01-SDD-01
43-01-SDD-02
50-SDE-01
50-SDE-02
50-SDE-03
60-SVP
61-01-VTS
70-01-SUM
```

The segment immediately after a reserved document-family number identifies the
**scope** when that family has a natural stable scope identifier. Software-item
families therefore use the SI identifier: `40-<SI>-UC`, `41-<SI>-SSD/SRD`,
`42-<SI>-SAD`, `43-<SI>-SDD[-<N>]` and `70-<SI>-SUM`. System-owned ISDs
use the same rule with the interface identifier, so IF-03 is `32-03-ISD` and
IF-11 is `32-11-ISD`. Optional interface design descriptions use family `33`,
for example `33-05-IDD` for IF-05.

When a repeatable generic family has no natural scope identifier, a document
sequence follows the type instead. The SDE family therefore uses
`50-SDE-01`, `50-SDE-02`, ... . A singular generic document such as
`60-SVP` does not need a synthetic sequence. Software-item verification test
specifications use `61-<SI>-VTS`, for example `61-01-VTS` for SI-01.

A final sequence distinguishes multiple documents that share the same family
and scope, for example `43-01-SDD-01`, `43-01-SDD-02`, ... for SI-01.
External/parent-system documents keep the identifier/version assigned by their
owner and are registered through document 20 rather than being locally
renumbered.
## Documentation levels

The project intentionally separates:

- **working context** — brainstorm, agent coordination and domain baseline;
- **planning** — SDP and SIP;
- **external/parent-system inputs** — controlled requirements, interface contracts, protocols and standards owned outside the current software-system scope;
- **software-system specification/design** — system use cases, SSSD, system-owned ISDs and optional IDDs;
- **software-item specification/design** — optional item use cases; either a combined SSD or separate SRD + SAD; and focused SDDs;
- **development environment/engineering** — SDE and toolchain/environment refinements;
- **verification/validation** — SVP for strategy, VTS for concrete cases, and retained/generated evidence for actual executions;
- **user/operations** — release/user/operator guidance such as SUM;
- **agent plan (`AP-*`)** — coordination history/work for this meta repository.

Document numbers and ranges make those families easy to scan. Normative authority/release dependencies are expressed through document `Inputs` and traceability, not inferred from the numeric prefix.

## Traceability direction

A typical internally defined product-document chain is:

```text
domain baseline / system use cases / applicable parent-system inputs
                         -> SSSD
                         -> allocated system-owned ISD(s)
                         -> optional interface IDD(s) where concrete design needs a separate baseline
                         -> affected software-item use cases where useful
                         -> affected software-item SRD/SSD
                         -> SAD when architecture is separate
                         -> focused SDD(s)
                         -> implementation
                         -> 61-<SI>-VTS verification case
                         -> executable verification
                         -> retained verification evidence
```

An externally owned requirement, IDD, protocol or standard remains upstream authority and may constrain the SSSD and, where allocated directly, an affected SSD. The document-20 register records that dependency without copying ownership into this repository.

Planning, engineering-environment and verification documents may reference this chain without becoming upstream product authority merely because of their document number.

## Workflow

Normal changes follow the PR-first workflow defined in the SDE: issue/work item → `feature/pr-N-...` branch → draft PR → implementation/test/evidence → review → merge.

The repository intentionally starts with structure, brainstorming, planning and architecture exploration. Candidate requirements and current design documents remain non-authoritative until explicitly promoted.

# Software Development Environment (SDE)

Status: working draft / non-authoritative

This Software Development Environment document defines the common development environment, repository conventions, GitHub workflow, automation model, and AI/agent working method for the software system.

The SDE is **project/software-system level**. It applies across software items and implementation repositories unless a repository documents a justified exception.

## Purpose

The development environment should make work:

- reproducible;
- reviewable;
- traceable from issue through implementation and verification;
- usable by both human developers and AI agents;
- consistent across public and private repositories;
- suitable for generated documentation and build artifacts;
- simple enough to use on a small project without losing engineering discipline.

## Primary development services and tools

Current baseline:

- **GitHub** — source control, issues, pull requests, review history and CI/CD;
- **GitHub Actions** — automated build, test, generated documentation and later deployment workflows;
- **Git** — source/version control;
- **Maven** — accepted Java build/dependency-management baseline;
- **Java 8** — initial runtime/language baseline for software item 01 because the original Raspberry Pi Zero is mandatory;
- **Python** — project tooling/document generation where it provides a simple reproducible solution;
- **draw.io + generated SVG** — editable and GitHub-readable architecture diagrams generated from project-controlled source where practical;
- **Docker / Docker Compose** — for reproducible integration-test dependencies such as RabbitMQ where running a real external service materially improves verification.

Individual software items may add development tools, but system-wide choices should remain documented and deliberate.

## Repository baseline

Every implementation or coordination repository is expected to contain at least:

```text
README.md
AGENTS.md
CHANGELOG.md
```

### `README.md`

The README should provide the human entry point and normally include:

- repository purpose;
- relationship to the wider software system/project;
- current status where useful;
- basic build/run/test instructions or links to them;
- important document/navigation links;
- generated-output links where applicable.

### `AGENTS.md`

`AGENTS.md` contains persistent repository-specific instructions for AI/coding agents.

It should define or reference:

- repository purpose and boundaries;
- sources of truth;
- active development/workflow rules;
- files/documents that must be read before substantial work;
- privacy/public-private boundaries;
- test/build expectations;
- rules that prevent agents from silently jumping to later plan steps.

Agent instructions should not contradict the engineering process used by human developers. AI is an implementation/research aid inside the same controlled workflow.

### `CHANGELOG.md`

The changelog records notable repository changes at an appropriate level. It is not intended to replace Git history or PR evidence.

## Documentation layout

Repositories should prefer predictable, reviewable Markdown documentation. This meta repository uses numbered document families so GitHub sorts them meaningfully.

Project-level examples include:

```text
10-SDP-...   Software Development Plan
11-SIP-...   Software Implementation Planning
12-SDE-...   Software Development Environment
20-xx-...    Requirements / SRDs
30-SSAD-...  Software System Architecture
31-01-...    Software item 01 design family
31-02-...    Software item 02 design family
40-xx-IDD... system-level interface documents
50-xx-SVP... verification planning
```

The second-level software-item number, where used, identifies the software item rather than the sequence of the document.

## GitHub issue → branch → pull-request workflow

Normal development follows a PR-first workflow.

The intended lifecycle is:

```text
issue / work item
      |
      v
feature branch
      |
      v
draft pull request
      |
      | implementation + discussion + tests + evidence
      v
ready-for-review pull request
      |
      v
merge to target branch
```

### 1. Issue/work-item creation

Use a GitHub issue when useful to reserve/identify the work and provide a stable work-item number.

Where supported by the project workflow, the issue number is reused as the pull-request/work number.

### 2. Feature branch

Create a branch from the intended target branch using:

```text
feature/pr-<N>-<short-slug>
```

Example:

```text
feature/pr-12-add-status-api
```

Do not perform normal implementation work directly on `main`.

### 3. Promote/convert to draft PR

Create or promote the work item into the corresponding draft pull request as early as practical.

The draft PR becomes the active work container for:

- scope;
- design discussion specific to the change;
- implementation commits;
- test results;
- generated evidence;
- deviations from the plan;
- review conversation.

Long-lived planning documents should not be turned into minute-by-minute implementation logs when the PR can carry that detail.

### 4. Continue on the PR branch

All work for that scope continues on the same feature branch while the draft PR is open.

The PR should remain draft until its intended scope and evidence are sufficiently complete.

### 5. Review and merge

Before merge:

- required automated checks should be green;
- relevant generated outputs should have been visually/reviewed where applicable;
- important evidence should be recorded in the PR;
- documentation and changelog should be updated when required;
- unresolved scope should be explicitly deferred rather than silently omitted.

## Branch protection direction

The default branch should be protected through a repository/ruleset configuration appropriate for a solo developer while still enforcing PR-first work.

Expected baseline direction:

- require a pull request before merging to the default branch;
- prevent force pushes to the protected default branch;
- restrict deletion of the protected default branch;
- use zero required approving reviewers when appropriate for a solo-maintainer repository;
- add required CI checks once the repository has stable meaningful checks;
- automatically delete merged feature branches where appropriate.

Avoid process mechanisms such as merge queues unless they solve a real project need.

## Generated-output branches

Generated artifacts should not pollute normal source branches when they are build output.

The project uses the same general pattern as the CAD projects:

```text
source branch / pull request
          |
          | CI
          v
dev/pr-<N>/<output-type>
          |
          | after merge to main
          v
prod/<output-type>
```

For generated documentation in this meta repository:

```text
dev/pr-<N>/docs
prod/docs
```

Rules:

- generated branches are build output, not hand-edited source;
- the PR branch remains the source of truth;
- PR-generated branches allow both human and AI review of the actual rendered/generated result before merge;
- the corresponding `dev/pr-N/...` output branch should be removed when the PR closes;
- `prod/...` represents output generated from merged/default-branch source.

This pattern may also be used for future build/test/package outputs when it is useful, but should not be introduced without a clear purpose.

## Generated documentation

Source documentation remains Markdown and generated-diagram source on normal branches.

The documentation build may create a generated document set containing:

- complete GitHub-readable Markdown documents;
- local SVG diagram assets;
- editable draw.io files;
- combined review documents/books where useful.

The generated form is for review/publication. The source documents remain authoritative and editable.

## AI-assisted development

AI agents are expected to follow the same repository process as other developers.

Before substantial work an agent should:

1. read `AGENTS.md`;
2. read the repository handoff/active plan where present;
3. inspect the current open/draft PR state;
4. inspect the most recently completed PR when it supplies predecessor context;
5. identify the currently active plan/work step;
6. work only inside that scope unless correcting the plan itself is necessary.

An agent should not:

- bypass pull requests by writing normal changes directly to `main`;
- treat brainstorm ideas as approved requirements automatically;
- silently make major architectural decisions without recording them;
- duplicate private/proprietary information into public repositories;
- edit generated output branches as though they were source;
- claim tests/evidence were performed when they were not.

AI-generated implementation is expected to be reviewable through normal source diffs, tests and generated evidence.

## Handoff between AI sessions

A repository intended for agent-assisted work should make it possible for a new session to reconstruct current state without relying on hidden conversational history.

Preferred sources are:

```text
AGENTS.md
current open/draft PR
most recently completed PR where relevant
active agent/implementation plan
requirements / architecture / IDDs
README.md
CHANGELOG.md
```

Detailed active-step evidence belongs primarily in the active PR. Persistent rules belong in `AGENTS.md`; long-term sequencing belongs in the appropriate plan.

## Build and test principles

Implementation repositories should introduce CI from the first useful executable increment.

Expected direction:

- fast compile/unit-test checks on normal PRs;
- application-level system tests through the public application interface from the first useful executable;
- lightweight socket/network system tests without external broker dependencies;
- separate RabbitMQ integration jobs/workflows when the production-shaped transport is introduced;
- hardware-specific tests separated from ordinary hosted-runner tests;
- generated artifacts retained/published when they materially improve review or traceability;
- dependency/runtime choices validated against the mandatory target platform rather than desktop development machines alone;
- real external-service integration tests use reproducible disposable dependencies where this adds meaningful evidence.

For software item 01, Raspberry Pi Zero compatibility must remain visible in Java/runtime/library choices.

## Automated system-test profiles

The common verification environment should support the profiles defined in the SVP:

```text
ST-1  application behaviour
      real SI-01 process
      public application interface
      controlled stub dependencies

ST-2  socket loop/network
      real SI-01 process
      simple socket backoffice simulator
      no RabbitMQ/Docker requirement

ST-3  RabbitMQ integration
      real SI-01 process
      disposable RabbitMQ broker
      Docker/Compose

ST-4  target/full-system
      Raspberry Pi Zero and/or real hardware/services
```

ST-1 should be inexpensive enough for normal pull requests. ST-2 should provide a real communication boundary while staying lightweight. ST-3 deliberately adds the external broker only where RabbitMQ-specific behaviour is under test.

Scenario concepts should be reusable across profiles where possible so the same functional behaviour can be checked with progressively more realistic infrastructure.

## Containerized integration services

Docker/Compose is appropriate when an integration test needs a real external service with meaningful protocol, connection, persistence or recovery behaviour.

RabbitMQ is the first identified example and belongs primarily to ST-3, not ST-1/ST-2.

The future implementation/reference repository should provide a small, disposable test environment, conceptually:

```text
compose.yaml
  rabbitmq-test
```

Possible later services may be added only when they are genuinely required by integration tests.

Rules for containerized test services:

- use synthetic/public test topology and credentials;
- do not embed production queue names, source IDs, broker endpoints or secrets;
- pin image versions/tags deliberately rather than floating silently;
- expose a health check so test startup waits for service readiness;
- allow the same environment to run locally and in GitHub Actions where practical;
- make cleanup/disposal simple;
- keep service startup separate from unit/ST-1/ST-2 tests so most tests do not require Docker;
- include stop/restart scenarios when recovery behaviour is part of the interface contract.

For RabbitMQ, ST-3 should eventually prove multi-source consumers, publishing, disconnect/reconnect and local-outbox recovery against a real broker. Detailed design is in `31-01-SDD-05-backoffice-transport-design.md`.

Docker is **not** automatically required for every tool. Small deterministic project tooling such as the current Python documentation generators should run directly when that is simpler and equally reproducible.

## Public and private repositories

The system is expected to contain both public and private components.

Development-environment rules should preserve that separation:

- public framework repositories must build/test without private source;
- private implementations consume public contracts/artifacts;
- secrets and credentials must not be committed;
- proprietary protocols/hardware implementations stay in the intended private repository;
- real registration-asset/source/broker mappings stay in private/external deployment configuration;
- public ST-1/ST-2/ST-3 tests use generic synthetic identities/topology;
- the public reference/test project should prove external consumption of public framework artifacts independently from private code.

## Secrets and configuration

Credentials, tokens, encryption keys and environment-specific secrets must not be hard-coded or committed to source control.

Use repository/environment secret mechanisms and runtime configuration appropriate to the deployment environment. Exact application configuration/secret design belongs in the relevant architecture/SDD/IDD documents.

Public example configuration must use synthetic placeholders rather than real production identifiers.

## Tooling reproducibility

Prefer tooling that is easy to reproduce in GitHub Actions and locally.

Start with the simplest adequate mechanism:

- pinned/action-versioned CI steps;
- Maven for Java builds;
- Python standard-library tooling where sufficient;
- simple native socket test harnesses for ST-2 where possible;
- Docker/Compose for non-trivial external service dependencies such as RabbitMQ ST-3 integration tests;
- dedicated custom Docker build images only where they provide meaningful reproducibility or isolate a substantial toolchain.

Do not introduce a custom Docker image merely because a build contains Python or a small script. Introduce containers when they solve a concrete environment/reproducibility problem.

## Repository-specific extensions

Each repository may extend this system-level SDE through its own `AGENTS.md`, README, build files and local documentation.

Repository-specific rules may add constraints, but should not silently weaken core traceability/workflow rules. Material deviations should be documented explicitly.

## Open SDE topics

- exact Java/JDK distribution provisioning for developer machines and Raspberry Pi Zero;
- Maven repository/publication strategy for public and private artifacts;
- standard Java formatting/static-analysis choices;
- standard unit-test and integration-test frameworks;
- exact branch/ruleset templates to replicate across repositories;
- release/versioning conventions across framework, reference app and private integrations;
- whether a reusable repository bootstrap/template should be created once the conventions stabilise;
- standard mechanism for deployment credentials and target inventory;
- exact public test-driver mechanism for ST-1;
- exact socket framing/tooling for ST-2;
- exact Docker/Compose versioning/pinning policy for ST-3 integration services;
- whether generated document output later also includes PDF/HTML in addition to GitHub Markdown.

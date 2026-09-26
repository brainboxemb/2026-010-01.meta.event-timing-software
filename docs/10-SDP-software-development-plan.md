# Software Development Plan (SDP)

Status: working draft / non-authoritative

This plan describes the **development direction** for the event-timing software. It is
intentionally high level: enough structure to keep the project coherent without turning
a serious hobby project into a management exercise.

The ordered implementation steps live in the SIP. Repository workflow, release mechanics
and tooling live in the SDE. Verification detail lives in the SVP.

## What this plan is for

The SDP answers a few broad questions:

- what kind of software system are we trying to build;
- how do we want to grow it without creating avoidable coupling;
- which development phases and environments matter;
- which assumptions and risks can materially change the approach.

It does **not** own implementation tasks, commands, CI evidence or release checklists.

## Development goals

The project should result in a reusable timing system that:

- supports reliable event timing and registration;
- runs on the original Raspberry Pi Zero / Zero W;
- separates the **Headless Timing Application** (SI-01) from desktop and web clients;
- supports multiple logical `TimingNode` instances in one application;
- keeps local operation useful when backoffice/internet connectivity is unavailable;
- keeps registrations and recovery state traceable;
- can be tested without requiring all production hardware;
- allows private implementations to plug into public contracts;
- has reproducible build, test, documentation and deployment tooling.

## Development approach

### Build in small demonstrable steps

Prefer useful vertical increments over building all layers in isolation first.

Each SIP step should end in something concrete that can be run, shown or verified. The
SIP owns the exact steps, result, demo and done criteria.

### Keep architecture ahead of expensive coupling

Define important boundaries before production implementations make them difficult to
change:

- software-item and interface ownership;
- TimingNode/domain ownership;
- threading and state-change boundaries;
- public/private extension points;
- persistence and recovery direction.

Architecture should support implementation, not delay executable software.

### Get to executable software and the real target early

First make the headless application useful on the development host. Then prove the
original Raspberry Pi Zero early enough that runtime, memory or deployment constraints
can still influence design choices.

Image generation and normal application updates should become repeatable before manual
SD-card preparation turns into routine workflow.

### Automate repeatable work

Use repository automation for builds, tests, generated documentation/evidence and later
target images/updates.

AI-assisted work follows the same repository workflow and review/testing rules as other
changes. The SDE and repository guidance own those details.

### Increase test realism gradually

Start with fast deterministic tests. Add process/network boundaries, broker integration,
real Raspberry Pi execution and hardware-in-the-loop tests as the corresponding risks
become relevant.

The SVP owns the detailed verification model and `ST-*` profiles.

### Keep public and private concerns separate

Reusable contracts, stubs/testkit and reference applications can remain public. Private
protocol implementations, real deployment identities, mappings, credentials and secrets
stay outside public source.

Prove that replacement boundary before proprietary code becomes large.

### Use releases as useful baselines

When a SIP step produces a meaningful software baseline, close it with a verified,
identifiable release. Detailed version/tag/artifact mechanics belong in the SDE and
repository tooling rather than here.

Planning-only steps do not need artificial software releases.

## Broad development phases

These phases are intentionally broader than the SIP steps.

### A — Architecture and engineering baseline

Establish the domain model, software items, interfaces, development environment,
verification direction and public/private boundary.

### B — Framework and first useful application

Create the Java/Maven framework and the first long-running **Headless Timing Application**
(SI-01) on the development host, including configuration and basic remote interfaces.

### C — Raspberry Pi deployment foundation

Prove the original Pi Zero target with a repeatable image, service startup, application
update path and initial resource measurements.

### D — Independent clients and extension proofs

Add the **Desktop GUI Application** (SI-02), an external reference/test consumer and a
small private-extension proof to verify that public contracts work outside the framework
repository.

### E — Timing-domain and web operator behaviour

Grow the useful TimingNode/domain behaviour, persistence/recovery and the browser/iPad
**Web Operator Application** (SI-03).

### F — Device and backoffice integration

Move from deterministic stubs to representative RFID/CAN/display hardware and backoffice
integration while keeping the same application/domain boundaries.

### G — Operational maturity

Harden provisioning, updates/rollback, configuration/secrets, diagnostics, longer-running
tests and measured resource limits.

## Pace and planning horizon

The working assumption is about **one focused project day per week**. Estimates are
project days, not promises about calendar dates.

The SIP roadmap owns the detailed estimates and target dates in
`docs/_data/sip-roadmap.yaml`. Re-estimate when implementation evidence materially
changes uncertainty.

The overall project is expected to span many months rather than being treated as a fixed
deadline. Keeping steps small and demonstrable is more useful than maintaining a detailed
long-range schedule.

## Development resources

The expected minimum setup is:

- a normal Windows development workstation for Java/Maven, documentation tooling and
  local/integration tests;
- at least one original Raspberry Pi Zero / Zero W for real target validation;
- representative RFID/CAN/keypad/display hardware when hardware integration begins.

A separate integration host may be added later if broker services, longer tests or test
drivers make that useful. It is not a current requirement.

## Current assumptions

- original Raspberry Pi Zero / Zero W remains a required target;
- Java 8 is the initial target baseline until measurements justify changing it;
- Maven remains the Java build/dependency baseline;
- GitHub/GitHub Actions remain available for source and automation;
- public and private repositories can share versioned public contracts/artifacts;
- secrets and real deployment mappings stay outside public source;
- representative hardware/backoffice access will be available when those phases begin;
- local timing operation must not depend on permanent backoffice/internet connectivity.

If an assumption becomes false and affects direction, update this plan and the relevant
SIP/architecture documents.

## Main risks and unknowns

| Risk / unknown | Response |
| --- | --- |
| ARMv6 Java/runtime support constrains libraries or maintenance. | Prove the chosen runtime on a real Pi Zero early; reconsider Java only from measured evidence. |
| Pi Zero CPU/RAM is too limited for convenient designs. | Measure real resource use early and keep the runtime architecture lean. |
| Image/update automation is harder than expected. | Treat target deployment as an early capability rather than end-of-project packaging. |
| Public/private boundaries are wrong. | Use external-consumer and private-replacement proofs before proprietary code grows. |
| Ordering/threading/timestamp mistakes affect timing results. | Keep state changes controlled and verify ordering/timestamps deterministically. |
| Offline/reconnect behaviour becomes complex. | Keep local operation, persistence and transport concerns separate and test recovery progressively. |
| Real hardware differs from simulations. | Use replaceable adapters and add representative HIL tests when hardware becomes available. |
| Backoffice details leak into public/domain APIs. | Keep semantic application ports separate from transport/proprietary mappings. |
| Part-time cadence causes loss of context. | Prefer small demonstrable steps and keep current decisions/evidence easy to recover. |

## Decisions still to resolve

Important choices still expected during implementation include:

- exact ARMv6 Java runtime/distribution;
- Raspberry Pi image-builder and update/rollback approach;
- later logging/test-library choices where not already settled;
- configuration/secrets refinement as more adapters are added;
- public/private artifact publication;
- whether a dedicated integration host becomes worthwhile;
- whether Java 11 ever provides enough benefit to replace the Java 8 target baseline.

These decisions belong in the SIP, SDE, architecture or implementation work when they
become concrete.

## When to update this plan

Change the SDP when the **development direction** changes: a major target assumption,
phase strategy, resource need or project-level risk.

Do not update it for ordinary activity progress. That belongs in the SIP, issues, pull
requests and generated evidence.

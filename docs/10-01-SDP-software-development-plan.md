# Software Development Plan (SDP)

Status: working draft / non-authoritative

This document records the **current development direction**. It should stay short and
should distinguish decisions from things that still need discussion or evidence.

The SIP owns the implementation steps. The SDE owns the development/release environment.
The SVP owns verification detail.

## Documentation structure and dependency discipline

### Document categories and numbering

The numeric prefix groups documents by **engineering role**. It is primarily a navigation/readability convention; it does not by itself define normative dependency order.

```text
00  working / project context
10  planning
20  external / parent-system inputs
30–39  software-system specification and design
40  software-item specification
41  software-item detailed design
50  development environment / engineering
60  verification and validation
70  user / operational documentation
```

Current examples are:

```text
00-01-brainstorm
00-02-handoff
00-03-agent-plan
00-04-domain-baseline

10-01-SDP
10-02-SIP

20-01-EXT-external-system-inputs

30-UC-system-use-cases
31-SSSD-software-system-specification-document
32-IDD-03-application-control-status
33-IDD-11-application-configuration

40-01-SSD-timing-application-specification-document
40-02-SSD-gui-application-specification-document

41-01-SDD-01-data-and-display-design
41-01-SDD-02-java-component-design
41-01-SDD-03-backoffice-transport-design

50-01-SDE-software-development-environment
50-02-SDE-java-build-test-toolchain

60-01-SVP-software-verification-plan

70-01-SUM-headless-timing-application
```

Numbering rules:

- the leading two-digit value is the stable document **number/range**;
- within category 00/10/20/50/60, the next segment is a category-local document sequence;
- document number `40` is reserved for software-item SSDs; the next segment is the stable software-item identifier, for example `40-01-SSD` for SI-01 and `40-02-SSD` for SI-02;
- document number `41` is reserved for software-item SDDs; the next segment is the stable software-item identifier and a final sequence distinguishes multiple SDDs for the same item, for example `41-01-SDD-01`, `41-01-SDD-02`, ...;
- an optional software-item use-case document receives its own dedicated range if/when such documents are introduced; do not reuse the category-40 SSD or category-41 SDD ranges merely because the use case belongs to a software item;
- software-system documents use one leading document number each. System-owned IDDs therefore receive their own document number while the IDD suffix retains the interface identity, for example `32-IDD-03-...` for IF-03 and `33-IDD-11-...` for IF-11;
- category 70 item-specific documents use the stable software-item segment where applicable, for example `70-01-SUM-...` for SI-01;
- an externally owned document keeps the identifier/version assigned by its owner. Category 20 records the external input and its applicable revision; it does not renumber the external authority as if this project owned it.

A new document should fit an existing category before another category is invented. The category structure is intentionally roomy enough for later verification specifications/reports and additional engineering-environment documents without mixing them into planning or product design.

### External and parent-system inputs

The software system defined here is itself a subsystem of a larger operational system. Some requirements and interface contracts can therefore be defined **above the current software-system scope**.

`20-01-EXT-external-system-inputs.md` records those controlled upstream inputs: parent-system requirements, externally owned IDDs, protocols, standards or equivalent contracts, including the exact version/revision when known and the part of this software system they constrain.

The external source remains the authority. The local category-20 record is a baseline/traceability index and must not silently copy, weaken or reinterpret an externally controlled contract. Private/proprietary source material may remain outside this public repository while its applicable identity/revision is recorded generically when that can be done safely.

### Normative authority and release dependencies

Product-document `Inputs` are **authority/release dependencies**, not a list of every document that was useful while writing. Ordinary downstream references belong under traceability/related-document sections and do not make the referenced document an input.

The generic direction is:

```text
parent / external system requirements, IDDs, protocols
                         |
                         v
            20 external-input baseline
                         |
domain baseline ---------+------> 30 system use cases
                         |                 |
                         +-----------------+
                                           v
                                      31 SSSD
                                           |
                                 allocates interfaces/items
                                           |
                      +--------------------+--------------------+
                      |                                         |
                      v                                         v
          32/33 system-owned IDD(s)             optional software-item UC(s)
                      |                                         |
                      +--------------------+--------------------+
                                           |
                                           v
                                     40-<SI>-SSD
                                           |
                                           v
                                     41-<SI>-SDD-<N>
                                           |
                                           v
                                      implementation
                                           |
                                           v
                                  verification evidence
```

The diagram shows the normal internal decomposition, not a rule that every input must pass through every box. An externally imposed requirement/IDD/protocol may directly constrain the SSSD and an affected SSD when the allocation is already explicit.

Document roles:

- **SSSD** — combines software-system requirements and software-system architecture and owns software-item/interface allocation.
- **System-owned IDD** — defines a contract allocated/owned by this software system. Once released, it constrains every affected SSD.
- **Software-item UC** — optional behavioural decomposition of one or more system use cases after responsibility has been allocated to a software item.
- **SSD** — combines a software item's requirements and architecture. It consumes the SSSD plus applicable external and system-owned interface obligations.
- **SDD** — focused detailed design downstream of the owning SSD.
- **SVP/verification cases** — consume requirements and interface contracts for coverage; verification planning is not a requirement input.
- **SDP/SIP** — project/development-control documents. They plan direction and implementation sequence but do not define product requirements by being listed as an input.
- **SDE** — engineering-environment authority. It is deliberately in its own category rather than being treated as a third planning document.
- **SUM** — release/user guidance downstream of the released software/configuration baseline.

For independently released documents, a released document records the exact version/revision of every normative input. In the current repository-wide release model, one repository release/tag/commit may identify the coherent local document baseline, but the dependency graph must remain acyclic so independent document release remains possible later.


## Current direction

The project currently centres on the **Headless Timing Application** (SI-01):

- Java application with one or more `TimingNode` instances;
- external configuration;
- console, remote shell and a programmable Remote API;
- timing/domain behaviour added incrementally;
- hardware and backoffice adapters added when their contracts become concrete;
- Windows as the convenient development host;
- Raspberry Pi Zero / Zero W as a target to run and verify on real hardware.

A separate **Desktop GUI Application** (SI-02) is planned as a real Remote API client.
Its implementation technology has not yet been selected.

The current JavaFX application is **not SI-02**. It is an engineering tool for manual
integration testing of the Remote API.

A small web client may also be useful later for exercising the Remote API. That is
currently a test-tool idea, not a separate product/software item.

## Development approach

### Keep the next step concrete

Prefer a small runnable increment over a large future design. Each SIP step should say
why it exists, what it needs and what can be demonstrated when it is done.

### Add architecture when it solves a real problem

Keep the important domain/application/I/O/presentation boundaries clear, but do not add
layers, services or product clients only because they might become useful later.

### Measure before optimising

The Raspberry Pi target should be tested with representative software. We currently do
**not** assume that one Java timing application is too heavy for it.

CPU, memory, startup time and thread count are useful measurements. They become design
constraints only if measurements show a problem.

### Keep interfaces independently testable

Console, shell, Remote API and later GUI behaviour should use the same application
semantics where appropriate.

Engineering clients may use a different runtime or technology from SI-01. They should
still use public interfaces rather than internal SI-01 classes.

### Automate repeatable work

Builds, tests, generated documentation and releases should be repeatable. Detailed Git,
CI and release rules live in the SDE/repository guidance rather than here.

## Broad phases

These are direction markers, not a fixed schedule.

### A — Architecture and framework baseline

Establish the useful domain/application boundaries and a buildable Java framework.

### B — First useful Headless Timing Application

Grow SI-01 on the development host: configuration, lifecycle, Remote API, logging and
basic black-box testing.

### C — Raspberry Pi target proof

Run the representative application on the Pi Zero/Zero W and learn what, if anything,
the target requires in deployment or runtime design.

### D — Desktop GUI

Build SI-02 as a real independent client of the Remote API. The GUI technology remains
an open choice until this phase becomes active.

### E — Timing/domain behaviour

Implement registrations, StageStartTimes, NextUpTeams, RaceData, StageTiming and the
persistence/recovery needed by those capabilities.

### F — Device and backoffice integration

Add representative RFID/CAN/display and backoffice behaviour as their interfaces become
concrete.

## Resources

Known or expected resources are modest:

- normal Windows development workstation;
- original Raspberry Pi Zero / Zero W when target work starts;
- representative RFID/CAN/display hardware when those integrations are implemented;
- a broker/backoffice test environment when backoffice integration starts.

A dedicated integration host is an option only if a real need appears.

## Open points

These should remain questions until we have a reason to decide them:

- target-platform choice, including Raspberry Pi availability and OTS versus custom hardware;
- whether local e-ink display, RTC and CAN belong on the target platform;
- exact Raspberry Pi/target OS, image and update approach;
- exact Java runtime on the Pi target;
- whether target measurements reveal any meaningful CPU/RAM/thread limitations;
- technology and packaging for the real Desktop GUI Application (SI-02);
- whether a small web Remote-API test client is useful in addition to the JavaFX tool;
- exact persistence format/strategy as domain state grows;
- exact device and backoffice transports where not already fixed by external systems;
- whether a separate integration host is worthwhile;
- whether there is ever a reason to move the SI-01 Java baseline beyond Java 8.

## Main risks

Only risks that can materially change the direction belong here.

| Risk / unknown | Current response |
| --- | --- |
| Target hardware availability or lifecycle blocks the preferred platform. | Keep software development hardware-independent; study Pi-class alternatives and OTS/custom options before procurement. |
| Pi/target deployment/runtime differs materially from development-host behaviour. | Run the representative application on selected real hardware and measure before changing architecture. |
| Timing/order/threading mistakes affect results. | Keep state changes controlled and verify timing/ordering behaviour deterministically. |
| Hardware behaviour differs from simulations. | Keep adapters replaceable and verify against representative hardware when available. |
| Backoffice details leak into application/domain APIs. | Keep application semantics separate from transport/proprietary mappings. |
| Part-time cadence loses context. | Keep steps small, demonstrable and documented at their actual decision points. |

## When to update this plan

Change the SDP when the **development direction** changes: target, major software item,
broad phase or project-level risk.

Ordinary task progress belongs in the SIP, issues and pull requests.

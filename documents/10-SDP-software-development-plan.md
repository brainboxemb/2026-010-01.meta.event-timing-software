<!-- Generated review/output copy. Edit the source document, not this copy. -->

# Software Development Plan (SDP)

Status: working draft / non-authoritative

This document records the **current development direction**. It should stay short and
should distinguish decisions from things that still need discussion or evidence.

The SIP owns the implementation steps. The SDE owns the development/release environment.
The SVP owns verification strategy and profiles. Concrete SI-01 verification cases are
specified in the VTS; execution results belong to retained verification evidence.

## Documentation structure and dependency discipline

### Document categories and numbering

The following abbreviations are canonical for this project:

| Abbreviation | Full name | Primary role |
| --- | --- | --- |
| SDP | Software Development Plan | project-wide development strategy |
| SIP | Software Implementation Plan | implementation steps, roadmap and exit evidence |
| EXT | External Inputs | register of parent/external normative sources |
| UC | Use Cases | externally meaningful behaviour/use cases |
| SSSD | Software System Specification Document | software-system requirements + architecture |
| ISD | Interface Specification Document | normative system-owned interface requirements and semantics |
| IDD | Interface Design Description | optional concrete interface design/representation implementing an ISD |
| SRD | Software Requirements Document | software-item requirements when split from architecture |
| SSD | Software Specification Document | software-item requirements + architecture combined |
| SAD | Software Architecture Document | software-item architecture when split from requirements |
| SDD | Software Design Description | focused detailed software-item design |
| SDE | Software Development Environment | repositories, tooling, build/development environment |
| SVP | Software Verification Plan | verification strategy, levels, environments and evidence rules |
| VTS | Verification Test Specification | concrete stable verification cases and expected results |
| SUM | Software User Manual | technical user/release guidance |

The numeric prefix groups documents by **engineering role**. It is primarily a navigation/readability convention; it does not by itself define normative dependency order.

```text
00–09  working / project context
10–19  planning
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

Current examples are:

```text
00-brainstorm
02-agent-plan
03-domain-baseline

10-SDP
11-SIP

20-EXT-external-system-inputs

30-UC-system-use-cases
31-SSSD-software-system-specification-document
32-03-ISD-application-control-status
32-05-ISD-timingdata-interchange
32-11-ISD-application-configuration
33-05-IDD-timingdata-interchange

40-01-UC                         reserved / optional for SI-01
41-01-SSD-timing-application-specification-document
41-02-SSD-gui-application-specification-document

43-01-SDD-01-data-and-display-design
43-01-SDD-02-java-component-design
43-01-SDD-03-backoffice-transport-design

50-SDE-01-software-development-environment
50-SDE-02-java-build-test-toolchain
50-SDE-03-engineering-client

60-SVP-software-verification-plan
61-01-VTS-timing-application-verification-test-specification

70-01-SUM-headless-timing-application
```

Numbering rules:

- the leading two-digit value identifies the document category or reserved document family; it is not a dependency-order number;
- where a reserved family has a natural stable scope identifier, that scope is the second segment. Software-item families use the software-item ID, for example `41-01-SSD` and `43-01-SDD-02`;
- document family `32` is reserved for software-system-owned Interface Specification Documents (ISDs). Its second segment is the stable interface ID, so IF-03 is `32-03-ISD` and IF-11 is `32-11-ISD`; the number is not a document sequence;
- document family `33` is reserved for optional Interface Design Descriptions (IDDs). Use the same interface ID, for example `33-05-IDD` implements design choices for IF-05. Do not create an IDD when the ISD is sufficient;
- document number `40` is reserved for optional software-item use cases, for example `40-01-UC` for SI-01;
- document number `41` is reserved for software-item requirements/specification: use `41-<SI>-SSD` when requirements and architecture are combined, or `41-<SI>-SRD` when they are split;
- document number `42` is reserved for a separate software-item architecture document `42-<SI>-SAD`; omit it when `41-<SI>-SSD` already combines requirements and architecture;
- document number `43` is reserved for software-item detailed design. When several SDDs share the same software-item scope, a final sequence follows the type: `43-01-SDD-01`, `43-01-SDD-02`, ...;
- a repeatable generic family without a natural scope identifier puts its sequence after the type. The generic SDE family therefore uses `50-SDE-01`, `50-SDE-02`, ...;
- a singular generic document does not gain a synthetic sequence merely for symmetry, for example `60-SVP`;
- document family `61` is reserved for software-item verification test specifications; use the software-item ID as scope, for example `61-01-VTS` for SI-01. The VTS specifies stable verification cases; it does not record current execution status or retained run evidence;
- range 70–79 item-specific documents use the stable software-item segment where applicable, for example `70-01-SUM` for SI-01;
- an externally owned document keeps the identifier/version assigned by its owner. Document 20 records the external input and its applicable revision; it does not renumber the external authority as if this project owned it.

A new document should fit an existing category/family before another one is
invented. Scope identifiers and document sequences have different meanings and
must not trade places merely to keep filenames numerically contiguous.
### External and parent-system inputs

The software system defined here is itself a subsystem of a larger operational system. Some requirements and interface contracts can therefore be defined **above the current software-system scope**.

`20-EXT-external-system-inputs.md` records those controlled upstream inputs: parent-system requirements, externally owned IDDs, protocols, standards or equivalent contracts, including the exact version/revision when known and the part of this software system they constrain.

The external source remains the authority. The local document-20 record is a baseline/traceability index and must not silently copy, weaken or reinterpret an externally controlled contract. Private/proprietary source material may remain outside this public repository while its applicable identity/revision is recorded generically when that can be done safely.

### Normative authority and release dependencies

Product-document `Inputs` are **authority/release dependencies**, not a list of every document that was useful while writing. Ordinary downstream references belong under traceability/related-document sections and do not make the referenced document an input.

The generic direction is:

```text
parent / external system requirements, interface contracts/designs, protocols
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
          32-<IF>-ISD(s)             40-<SI>-UC(s)
                      |                                         |
              +-------+-------+                                 |
              |               |                                 |
              v               v                                 |
      optional 33-<IF>-IDD     +-------------------------------+
              |                                                 |
              |                       +-------------------------+
              |                       |
              |             +---------+------------------+
              |             |                            |
              |             v                            v
              |      combined route                 split route
              |      41-<SI>-SSD                 41-<SI>-SRD
              |             |                            |
              |             |                            v
              |             |                     42-<SI>-SAD
              +-------------+-------------+--------------+
                                          |
                                          v
                                    43-<SI>-SDD-<N>
                                           |
                                           v
                                      implementation
                                           |
                                           +----------------------+
                                           |                      |
                                           v                      v
                                  61-<SI>-VTS case      executable product
                                           |
                                           v
                                  executable verification
                                           |
                                           v
                                  verification evidence
```

The diagram shows the normal internal decomposition, not a rule that every input must pass through every box. An externally imposed requirement/IDD/protocol may directly constrain the SSSD and an affected software-item SRD/SSD when the allocation is already explicit.

Document roles:

- **SSSD** — combines software-system requirements and software-system architecture and owns software-item/interface allocation.
- **System-owned ISD** — defines the normative contract allocated/owned by this software system. Once released, it constrains every affected SRD/SSD.
- **System-owned IDD** — optional design description downstream of an ISD. It records concrete representation/design choices and is primarily an input to affected SDDs; it does not replace the ISD as the source of interface requirements.
- **Software-item UC** — optional behavioural decomposition of one or more system use cases after responsibility has been allocated to a software item.
- **SSD** — combines a software item's requirements and architecture. It consumes the SSSD plus applicable external and system-owned interface obligations.
- **SRD / SAD** — the split alternative: the SRD owns software-item requirements and the SAD owns the corresponding architecture. Do not maintain an SSD and SRD/SAD pair for the same scope.
- **SDD** — focused detailed design downstream of the owning SSD or SAD.
- **SVP / VTS** — the SVP defines verification strategy; the VTS defines concrete stable cases. Both consume product requirements/interfaces and are downstream, not requirement inputs.

### Requirement maturity

Requirements use the standard Sphinx-Needs `status` field. Author only the
compact codes below; generated reader views expand them to the full word. Use
the same convention for software and interface requirements:

| Status | Meaning |
| --- | --- |
| `D` | Draft — still being developed; wording, scope and even existence may change |
| `R` | Review — proposed requirement is ready for focused review |
| `A` | Approved — accepted normative requirement for the current engineering baseline |
| `O` | Obsolete — no longer active; retained only where its ID/history is needed for traceability |

A requirement written with `shall` is normative **at its stated maturity**.
`status: D` therefore does not mean the requirement has already been
accepted or frozen.

Move a requirement back to `D` when a review causes a material change in
scope or meaning. Use `O` rather than silently reusing an approved
requirement ID for a different meaning.

Every software and interface requirement shall carry an explicit status.
New requirements therefore receive `D`, `R`, `A` or `O` when they are
created; CI rejects a requirement without one.
- **SDP/SIP** — project/development-control documents. They plan direction and implementation sequence but do not define product requirements by being listed as an input.
- **SDE** — engineering-environment authority. It is deliberately in its own category rather than being treated as a third planning document.
- **SUM** — release/user guidance downstream of the released software/configuration baseline.

For independently released documents, a released document records the exact version/revision of every normative input. In the current repository-wide release model, one repository release/tag/commit may identify the coherent local document baseline, but the dependency graph must remain acyclic so independent document release remains possible later.


## Current direction

The project currently centres on the **Timing Point Application** (SI-01):

- Java application with one or more `TimingNode` instances;
- external configuration;
- console, remote shell and a programmable API;
- timing/domain behaviour added incrementally;
- hardware and backoffice adapters added when their contracts become concrete;
- Windows as the convenient development host;
- Raspberry Pi Zero / Zero W as a target to run and verify on real hardware.

A separate **Desktop GUI Application** (SI-02) is planned as a real API client.
Its implementation technology has not yet been selected.

The current JavaFX application is **not SI-02**. It is an engineering tool for manual
integration testing of the API.

A small web client may also be useful later for exercising the API. That is
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

Console, shell, API and later GUI behaviour should use the same application
semantics where appropriate.

Engineering clients may use a different runtime or technology from SI-01. They should
still use public interfaces rather than internal SI-01 classes.

### Automate repeatable work

Builds, tests, generated documentation and releases should be repeatable. Detailed Git,
CI and release rules live in the SDE/repository guidance rather than here.

## Broad phases

These are direction markers, not a fixed schedule.

### A — Architecture and application-core baseline

Establish the useful domain/application boundaries and a buildable Java application core.

### B — First useful Timing Point Application

Grow SI-01 on the development host: configuration, lifecycle, API, logging and
basic black-box testing.

### C — Raspberry Pi target proof

Run the representative application on the Pi Zero/Zero W and learn what, if anything,
the target requires in deployment or runtime design.

### D — Desktop GUI

Build SI-02 as a real independent client of the API. The GUI technology remains
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

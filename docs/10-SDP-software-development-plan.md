# Software Development Plan (SDP)

Status: working draft / non-authoritative

This document records the **current development direction**. It should stay short and
should distinguish decisions from things that still need discussion or evidence.

The SIP owns the implementation steps. The SDE owns the development/release environment.
The SVP owns verification detail.

## Document dependency and release discipline

Product-document `Inputs` are **authority/release dependencies**, not a list of every
document that was useful while writing. Ordinary downstream references belong under
traceability/related-document sections and do not make the referenced document an input.

The generic document-type direction is:

```text
domain / use cases / externally imposed interface specifications
                         |
                         v
                 SSSD (system)
        requirements + system architecture
                         |
                  allocates interfaces
                         |
             +-----------+-----------+
             |                       |
             v                       v
 system-owned IDD(s)          SISD(s) (software item)
             |              requirements + architecture
             +-----------+-----------+
                         |
                         v
                  focused SDD(s)
                         |
                         v
                  implementation
                         |
                         v
               verification evidence
```

Rules:

- **SSSD** — Software System Specification Document; combines software-system
  requirements and software-system architecture.
- **IDD** — system-owned interface contract. An externally imposed/protocol IDD may
  already exist and be an input to the SSSD. An IDD for an interface allocated by the
  SSSD normally follows that allocation and then becomes an input to every affected SISD.
- **SISD** — Software Item Specification Document; combines a software item's
  requirements and architecture. It consumes the SSSD and applicable released IDDs.
- **SDD** — focused detailed design; consumes the owning SISD and applicable IDDs.
- **SVP/verification cases** consume requirements and interface contracts for coverage;
  verification planning is not an input to SSSD/SISD requirements.
- **SDP/SIP/SDE** are project/development-control documents. They may plan when a
  capability or document is produced, but they do not define product requirements or
  architecture by being listed as an input.
- **SUM** is release/user guidance and is downstream of the released software/configuration
  baseline.

For independently released documents, a released document records the exact
version/revision of every normative input. In the current repository-wide release model,
one repository release/tag/commit may identify the coherent document baseline, but the
dependency graph must still remain acyclic so independent document release remains
possible later.

A normal release order for internally defined contracts is therefore:

```text
SSSD baseline
  -> allocated system IDDs
  -> affected SISDs
  -> focused SDDs
  -> implementation / verification evidence
```

External/protocol IDDs are the deliberate exception: because their contract originates
outside this decomposition, they may precede and constrain the SSSD.

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

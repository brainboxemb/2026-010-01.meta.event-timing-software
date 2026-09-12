# Software System Architecture Document (SSAD)

Status: working draft / non-authoritative

This document defines the architecture of the software system as a whole. Its purpose is to show the software items, their responsibilities and relationships, the system-owned interfaces, deployment relationships and constraints that apply across software-item boundaries.

It deliberately does **not** define the internal threading, messaging, persistence, package structure, device processing or implementation technology of SI-01. Those concerns belong in the applicable software-item SAD and, only where justified later, a focused detailed-design document.

Stable working domain facts and terminology are consolidated in `03-domain-baseline.md` and should not be silently reinterpreted here.

## Document role

The intended architecture hierarchy is:

```text
system/domain source knowledge
        |
        v
system requirements + system interfaces
        |
        v
30-SSAD  software-system architecture
        |
        +--> 31-01-SAD  SI-01 Timing Application Architecture
        +--> 31-02-SAD  SI-02 Desktop GUI Application Architecture
        +--> 31-03-SAD  SI-03 Web Operator Application Architecture
                    |
                    +--> focused SDD only when separate detailed design is useful
```

The SSAD answers questions such as:

- which software items exist and what does each own;
- how the software items communicate;
- which external systems/devices form system boundaries;
- where the software items execute;
- which architectural constraints must remain consistent across software items.

The software-item SADs answer how each software item is internally structured and implemented.

## Architecture drivers

The software-system architecture is driven by these system-level concerns:

- SI-01 remains the authoritative local timing/registration runtime;
- desktop and browser operator clients are separate software items and communicate with SI-01 over a system-defined network boundary;
- local timing/device operation must not depend on a connected desktop or browser client;
- external devices and backoffice systems are explicit system interfaces rather than hidden implementation dependencies;
- public framework/reference code and private/proprietary implementations must meet common supported contracts without private source leaking into public code;
- deployments must support constrained field hardware as well as development/test hosts;
- system interfaces and software-item ownership should remain stable even when internal implementation technology changes.

## Software-item register

The second-level number used in SRD/SAD/SDD filenames identifies the software item.

| Software item | Name | Current status | Primary responsibility | Expected deployment |
| --- | --- | --- | --- | --- |
| **SI-01** | Headless Timing Application | working architecture | Authoritative local timing/registration runtime, device integration, local state, status, persistence and backoffice synchronisation | Raspberry Pi Zero/Zero W; Linux/Windows development/test/runtime |
| **SI-02** | Desktop GUI Application | working architecture | Desktop operator client for status and control through the system interface | Operator workstation/laptop |
| **SI-03** | Web Operator Application | working architecture | Browser/iPad operator client using the SI-01 network interface | Browser/iPad on the local network |

Supporting framework modules, adapters, testkits/reference projects and private implementation repositories are engineering components, not automatically separate product software items.

## System context

```text
                         Operator
                       /          \
                      v            v
             SI-02 Desktop GUI   SI-03 Web/iPad
                      \            /
                       \          /
                        v        v
                    SI-01 Timing Application
                    /      |       \
                   v       v        v
             field devices local   Backoffice
             RFID / CAN     state   integration
             / displays
```

The desktop GUI and browser clients may disconnect without transferring authoritative timing-domain ownership away from SI-01.

![Software items and principal system interfaces](../../../raw/prod/docs/assets/architecture/software-item-system-overview.svg)

## Software-item relationships

### SI-01 ↔ SI-02

SI-02 is a network client of SI-01. It presents operator status and control but does not access SI-01 memory, files or Java objects directly.

### SI-01 ↔ SI-03

SI-03 is a browser-based network client. SI-01 exposes the system-defined control/status/event interface required by the browser application.

### SI-01 ↔ backoffice

SI-01 exchanges race/reference data, registration information, status and reconciliation information with the backoffice through a system-owned semantic interface. The concrete transport and codec are SI-01/integration design concerns unless they change the external system contract.

### SI-01 ↔ field devices

RFID, CAN, keypad and display equipment are external device boundaries of SI-01. Device semantics belong in system/device interfaces; internal adapter lifecycle, threads and processing pipelines belong in the SI-01 architecture/design.

## System interface catalogue

This catalogue identifies system-owned boundaries before all individual IDDs are mature. IDs are working identifiers but should remain stable once promoted.

| Interface | Parties | Current transport/direction | Purpose | Planned documentation |
| --- | --- | --- | --- | --- |
| **IF-01 Local Operator Console** | Operator ↔ SI-01 | local console/shell | Local version, status and operator commands | operator/application interface material |
| **IF-02 Remote Shell** | Operator/service tool ↔ SI-01 | remote terminal/shell, technology TBD | Remote status and commands using shared semantics | IDD candidate |
| **IF-03 Application Control & Status** | SI-02/SI-03 ↔ SI-01 | HTTP/JSON + WebSocket direction | Network command/query/status/event boundary | `40-01-IDD-application-control-status.md` candidate |
| **IF-04 Desktop Operator HMI** | Operator ↔ SI-02 | desktop GUI | Desktop screens, controls and operator feedback | GUI/HMI IDD candidate |
| **IF-05 Web Operator HMI** | Operator ↔ SI-03 | browser/iPad | Browser screens, controls and feedback | Web HMI IDD candidate |
| **IF-06 Backoffice Integration** | SI-01 ↔ Backoffice | transport implementation below semantic boundary | Race/reference-data sync, registrations, reconciliation/status | system IDD; proprietary wire details may remain private |
| **IF-07 RFID Integration** | SI-01 ↔ RFID subsystem | hardware/protocol adapter | RFID observations, lifecycle and health | device/semantic contract candidate |
| **IF-08 CAN Device Integration** | SI-01 ↔ CAN bus/devices | CAN | Discovery, Display V1 and keypad interaction | system/device IDD candidate |
| **IF-09 Smart Display V2** | SI-01 ↔ Display V2 | LAN/Wi-Fi | Synchronised display/domain data | system IDD candidate |
| **IF-10 Test Control** | test/reference tooling ↔ public stubs | development-only | Inject device/network/fault behaviour through supported boundaries | SDE/SVP/test design |

System-level IDDs own interface semantics. Software-item SRDs and SADs reference those obligations rather than redefining the wire/system contract independently.

## Cross-software-item interaction principles

The following rules apply across software-item boundaries:

- operator behaviour exposed through console, desktop and browser should converge on shared system semantics rather than implementing different business rules per client;
- network clients observe and control SI-01 but do not become the authority for timing state;
- loss of SI-02 or SI-03 must not by itself stop local SI-01 operation;
- interface versioning and compatibility must be explicit once interfaces become authoritative;
- transport-specific implementation detail should not leak into the semantic system interface unless that transport is itself part of the external contract;
- system status must let clients distinguish an unavailable client/network path from failure of authoritative local timing operation.

## System deployment view

The principal device/network relationships are a **software-system concern** because they show where SI-01, the operator software items, external field devices, local network and backoffice meet. Internal SI-01 adapters, scanners, status services and protocol-processing mechanics are intentionally not shown here.

![System device and network topology](../../../raw/prod/docs/assets/architecture/system-device-network-topology.svg)

Representative deployment relationships are:

```text
Field host
  SI-01 Headless Timing Application
    |
    +-- RFID subsystem
    +-- CAN devices / keypad / Display V1
    +-- local persistent state
    +-- local LAN/Wi-Fi

Operator workstation
  SI-02 Desktop GUI
    |
    +-- IF-03 over local network --> SI-01

Browser / iPad
  SI-03 Web Operator Application
    |
    +-- IF-03 over local network --> SI-01

Smart Display V2
  network client
    |
    +-- IF-09 over local LAN/Wi-Fi --> SI-01

Backoffice
  external system
    |
    +-- IF-06 over external connectivity --> SI-01
```

The exact process/thread topology, internal runtime cardinality, queueing model, service composition and adapter implementation are intentionally outside this SSAD.

## Cross-system architectural constraints

### Authority and disconnected operation

SI-01 owns authoritative local operational state. GUI/browser availability and temporary loss of external connectivity must not silently transfer that authority or fabricate healthy synchronisation.

### Public/private implementation boundary

System contracts used by public framework/reference code must allow private production implementations to plug in without public code depending on private source or proprietary identities.

### Interface-first separation

Software-item interaction is defined in terms of system-owned semantics. Internal implementation choices such as RabbitMQ libraries, HTTP servers, logging frameworks, executors or file formats are owned by the relevant software-item architecture unless the choice becomes part of an external contract.

### Deployment portability

The architecture must support constrained field deployment and normal Linux/Windows development/test environments without changing the software-item boundaries.

## Relationship to software-item architecture

The SI-01 SAD owns, among other things:

- layered application responsibilities;
- `TimingSystemInstance`, registration asset/source and other internal runtime abstractions;
- threading/concurrency and internal messaging;
- status architecture and lifecycle handling;
- persistence and restore strategy;
- logging/configuration/composition choices;
- Java/framework/library decisions;
- RFID/CAN/display adapter architecture behind the system device interfaces;
- backoffice transport implementation behind IF-06;
- resource-budget implications of those choices.

The SI-02 and SI-03 SADs similarly own their internal architectures while conforming to the system interfaces defined here and in applicable IDDs.

## Architecture review model

The project uses the 4+1 architectural view model as a review aid, not as a requirement for five documents. At system level, the SSAD primarily provides system context and deployment/relationship views. The software-item SADs provide the coherent logical, process, development and deployment views of each item and reference selected use cases as scenarios.

Reference: `reference/README.md`.

## Open system-architecture questions

- final system interface/IDD breakdown and ownership;
- authentication, authorisation and secure transport requirements across software-item boundaries;
- compatibility/versioning policy for IF-03 and IF-06;
- final deployment ownership for serving SI-03 assets;
- which device semantics require system-level IDDs versus software-item-only design;
- required behaviour when LAN, internet or backoffice connectivity is unavailable;
- final system-level availability/recovery requirements.

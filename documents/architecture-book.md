# Software specification and architecture document set

Generated review/output book containing the SSSD, software-item SSDs and currently active focused detailed designs. The numbered source documents on the source branch remain authoritative.

## Contents

- [Software System Specification Document (SSSD)](31-SSSD-software-system-specification-document.md)
- [API Interface Specification (ISD)](32-03-ISD-application-control-status.md)
- [TimingData Interchange Interface Specification (ISD)](32-05-ISD-timingdata-interchange.md)
- [TimingData Interchange Interface Design Description (IDD)](33-05-IDD-timingdata-interchange.md)
- [Application Configuration Interface Specification (ISD)](32-11-ISD-application-configuration.md)
- [Timing Application Specification Document (SSD)](41-01-SSD-timing-application-specification-document.md)
- [Data and display detailed design](43-01-SDD-01-data-and-display-design.md)
- [Java component, package and artifact detailed design](43-01-SDD-02-java-component-design.md)
- [Desktop GUI Application Specification Document (SSD)](41-02-SSD-gui-application-specification-document.md)

---

## Software System Specification Document (SSSD)

**Source document:** [31-SSSD-software-system-specification-document.md](31-SSSD-software-system-specification-document.md)

Status: working draft / non-authoritative

This Software System Specification Document combines the current **software-system requirements baseline** with the **software-system architecture**. It defines the software items, their allocated responsibilities, system-owned interfaces, deployment relationships and constraints that apply across software-item boundaries.

It deliberately does **not** define the internal threading, messaging, persistence, package structure, device processing or implementation technology of the **Timing Point Application** (SI-01). Those concerns belong in the applicable software-item specification and, only where justified, a focused detailed-design document.

Stable working domain facts and terminology are consolidated in `03-domain-baseline.md` and should not be silently reinterpreted here.

### Inputs

The SSSD is derived from upstream system intent, not from software-item design, implementation planning or verification planning:

- `03-domain-baseline.md` for stable domain terminology and facts;
- `30-UC-system-use-cases.md` for externally meaningful behaviour within this software-system scope;
- `20-EXT-external-system-inputs.md` for the controlled register of applicable parent-system requirements, externally owned IDDs, protocols and standards;
- the exact externally owned source revisions identified by that register when they impose requirements or interface obligations on this software system.

The category-20 register does not replace an external authority. It records which external source/revision applies and where it constrains this system.

A system-owned ISD created from an interface allocation made by this SSSD is downstream of the SSSD. Once released, that ISD becomes a normative input to the software-item specification(s) that implement or consume the interface. A separate system-owned IDD may then elaborate concrete interface design for affected detailed design.

The SIP, SDE, software-item SSDs/SDDs and SVP may reference the SSSD, but they are not inputs to it merely because they discuss the same capability.

### Document role

The normal product-document authority direction is:

```text
parent / external system contracts
              |
              v
20-01 external-input baseline
              |
domain --------+----> 30-UC system use cases
              |                 |
              +-----------------+
                                v
                         31-SSSD
                                |
                    allocates items/interfaces
                                |
                 +--------------+--------------+
                 |                             |
                 v                             v
      32-<IF> system-owned ISDs       optional software-item UC
                 |                             |
                 +--------------+--------------+
                                |
                                v
                         41-<SI>-SSD
                                |
                                v
                         43-<SI>-SDD-<N>
```

An externally imposed/parent-system contract may legitimately precede and constrain the SSSD and, where its allocation is already explicit, an affected SSD. An ISD first allocated and owned by this SSSD follows the SSSD and then becomes a normative input to the affected software-item SSDs. An optional IDD is downstream of that ISD.

Planning, engineering-environment and verification documents are separate control/evidence documents. They may schedule, enable or verify this specification but do not define its product requirements or architecture by document order.

The SSSD answers questions such as:

- which software-system requirements must be allocated;
- which software items exist and what each owns;
- how the software items communicate;
- which external systems/devices form system boundaries;
- where the software items execute;
- which architectural constraints must remain consistent across software items.

The software-item SSDs define the requirements and architecture of each software item.

### Software-system requirements baseline

The current migrated baseline records only obligations already present in the
pre-migration architecture/use-case model; it does not invent a new capability set merely because requirements
and architecture now share one document.

- The **Timing Point Application** (SI-01) keeps local timing/registration state.
- The planned **Desktop GUI Application** (SI-02) is a separate software item and uses
  a system-owned interface rather than SI-01 internals.
- Local timing/device operation shall not depend on a connected GUI or engineering/test client.
- External devices and the upstream system are explicit software-system boundaries.
- Public/reference and private/proprietary implementations shall meet the same supported
  system contracts without requiring private source in public implementation code.
- Software-system interfaces shall remain independent of incidental deployment topology
  where the interface itself only requires an available IP/network path.

### Architecture drivers

The software-system architecture is driven by these system-level concerns:

- the **Timing Point Application** (SI-01) keeps the local timing/registration state and runs the timing/device functions;
- the planned **Desktop GUI Application** (SI-02) is a separate software item and communicates with the Timing Point Application through the API;
- local timing/device operation must not depend on a connected GUI or engineering/test client;
- external devices and upstream systems are explicit system interfaces rather than hidden implementation dependencies;
- public reference/core implementation code and private/proprietary implementations must meet common supported contracts without private source leaking into public code;
- deployments should support the intended field target and normal development/test hosts; target limits are measured rather than assumed;
- system interfaces and software-item ownership should remain stable even when internal implementation technology changes;
- IP-based system interfaces must not require a particular router or Wi-Fi topology merely to exercise the interface.

### Software-item register

Software-item identity is stated by the document and traceability metadata; the numeric segment in category 40/41 is a document sequence and does not encode the software-item number.

| Software item | Name | Current status | Primary responsibility | Expected deployment |
| --- | --- | --- | --- | --- |
| **SI-01** | Timing Point Application | working specification | Local timing/registration runtime, device integration, state, status, persistence and upstream synchronisation | Raspberry Pi Zero/Zero W; Linux/Windows development/test/runtime |
| **SI-02** | Desktop GUI Application | planned / technology open | Desktop client for status and later control through the API | Operator workstation/laptop |

Supporting core modules, adapters and engineering/test clients are not automatically separate product software items. The current JavaFX API client is engineering support, not SI-02. A small web test client may be added later without creating another software item.

Application profiles are deployment/composition templates of **the same SI-01 Timing Point Application**. A profile may select different default topology/capabilities, but it is not a separate software item and does not create different TimingNode/domain semantics. Concrete deployment profile definitions are outside this public system baseline until an explicit public requirement owns them.

### System context

```text
                         Operator
                            |
                            v
                    SI-02 Desktop GUI
                            |
                            v
                    SI-01 Timing Point Application
                       ^            ^
                       |            |
              engineering/test   scripts / optional
              JavaFX client      web test client
                    /      |       \
                   v       v        v
             field devices local   Backend
             RFID / CAN     state   integration
             / displays
```

GUI and engineering/test clients may disconnect without changing where timing state is kept: it remains in the **Timing Point Application** (SI-01).

<a id="fig-sys-01"></a>
![Software items and principal system interfaces](../assets/architecture/software-item-system-overview.svg)
*Figure SYS-01 — Software items and principal system interfaces.*

### Software-item relationships

#### **Timing Point Application** (SI-01) ↔ **Desktop GUI Application** (SI-02)

The **Desktop GUI Application** (SI-02) is an IP network client of the **Timing Point Application** (SI-01). It presents operator status and control but does not access the application's memory, files or Java objects directly. The logical IF-03 relationship does not require a Wi-Fi router: a direct, same-host, point-to-point or normal LAN/Wi-Fi IP path may carry the interface.


#### **Timing Point Application** (SI-01) ↔ backend

The **Timing Point Application** (SI-01) exchanges race/reference data, timing records, status and reconciliation information with the upstream system through a system-owned semantic interface. SI-01 owns the semantic `TimingData` representation and `UpstreamProtocol` behaviour; concrete transport/session technology and deployment-specific wire routing remain implementation/integration concerns unless they change the external system contract.

#### **Timing Point Application** (SI-01) ↔ field devices

RFID, CAN, keypad, beeper and display equipment are external device boundaries of the **Timing Point Application** (SI-01). Device semantics belong in system/device interfaces; internal device/network-controller lifecycle, discovery, threads and processing pipelines belong in the **Timing Point Application** (SI-01) architecture/design.

The beeper is currently a transport-neutral device role; its concrete transport/interface allocation remains deferred rather than being assumed to be CAN.

The two display generations deliberately have different ownership. DisplayRev1Can is a passive CAN device actively driven by SI-01. DisplayRev2Wifi is a smart external client: SI-01 advertises a local data service, the display discovers and connects to it, and the display owns its own rendering and synchronisation behaviour.

### System interface catalogue

This catalogue identifies system-owned boundaries before all individual IDDs are mature. IDs are working identifiers but should remain stable once promoted.

| Interface | Parties | Current transport/direction | Purpose | Planned documentation |
| --- | --- | --- | --- | --- |
| **IF-01 Local Operator Console** | Operator ↔ SI-01 | local console/shell | Local version, status and operator commands | operator/application interface material |
| **IF-02 Remote Shell** | Operator/service tool ↔ SI-01 | remote terminal/shell, technology TBD | Remote status and commands using shared semantics | ISD candidate |
| **IF-03 API** | SI-02 / engineering & test clients ↔ SI-01 | HTTP/JSON + WebSocket over an available IP path | General remote query/control/diagnostics/test API; first slice is version/status/events | `32-03-ISD-application-control-status.md` candidate |
| **IF-04 Desktop Operator HMI** | Operator ↔ SI-02 | desktop GUI | Desktop screens, controls and operator feedback | GUI/HMI ISD candidate |
| **IF-05 TimingData Interchange** | SI-01 / engineering & test tools / compatible data consumers | append-only file / record interchange | Canonical timing-record semantics, identity, ordering, versioning and reference encoding | `32-05-ISD-timingdata-interchange.md` + `33-05-IDD-timingdata-interchange.md` |
| **IF-06 Backend Integration** | SI-01 ↔ Backend | transport implementation below semantic boundary | Race/reference-data sync, registrations, reconciliation/status | system ISD; proprietary wire/design details may remain private |
| **IF-07 RFID Integration** | SI-01 ↔ RFID subsystem | hardware/protocol adapter | RFID observations, lifecycle and health | device/semantic contract candidate |
| **IF-08 CAN Device Integration** | SI-01 ↔ CAN bus/devices | CAN | CAN discovery/state, DisplayRev1Can and keypad interaction | system/device ISD candidate |
| **IF-09 Smart Display V2** | DisplayRev2Wifi → SI-01 service | mDNS discovery + IP session; direct or LAN/Wi-Fi deployment | Discover SI-01 and consume timing/status/reference data; smart display owns render/sync | system ISD candidate |
| **IF-10 Test Control** | test/reference tooling ↔ public stubs | development-only | Inject device/network/fault behaviour through supported boundaries | SDE/SVP/test design |
| **IF-11 Application Configuration** | Deployment/configuration source → SI-01 | built-in profile/platform/mode defaults + explicit deployment overrides + secret references | Resolve deployed TimingNodes, I/O assets, presentation bindings and runtime composition inputs | `32-11-ISD-application-configuration.md` |

System-level ISDs own normative interface semantics. Software-item requirements reference those obligations rather than redefining the system contract independently. Optional IDDs describe concrete interface design where a separate design baseline is justified.

### Cross-software-item interaction principles

The following rules apply across software-item boundaries:

- operator and engineering clients should use shared application semantics rather than implement different business rules per client;
- network clients read state from and send commands to the **Timing Point Application** (SI-01); timing state remains in that application;
- loss of the **Desktop GUI Application** (SI-02) or an engineering/test client must not by itself stop local operation of the **Timing Point Application** (SI-01);
- IF-03 and IF-09 are endpoint-to-endpoint logical interfaces and must not make a physical Wi-Fi router an architectural prerequisite;
- development and automated integration verification may use loopback, same-host or direct IP connectivity while exercising the same system interface semantics;
- interface versioning and compatibility must be explicit once interfaces become stable contracts;
- transport-specific implementation detail should not leak into the semantic system interface unless that transport is itself part of the external contract;
- system status must distinguish local IP availability, configured network-infrastructure state, external reachability and backend/session health where those distinctions affect operator decisions.

### System deployment view

The principal device/interface relationships are a **software-system concern** because they show where the **Timing Point Application** (SI-01), the operator software items, external field devices and backend meet. The lines in this view are logical system-interface relationships: they deliberately do not force traffic through a router node.

<a id="fig-sys-02"></a>
![System device and logical interface topology](../assets/architecture/system-device-network-topology.svg)
*Figure SYS-02 — System device and logical interface topology.*

Representative relationships are:

```text
Deployment/configuration source
  +-- IF-11 --> SI-01

Field host
  SI-01 Timing Point Application
    |
    +-- IF-07 --> RFID subsystem
    +-- IF-08 --> CAN devices / keypad / DisplayRev1Can
    +-- IF-05 --> canonical TimingData file/interchange

SI-02 Desktop GUI
  +-- IF-03 over available IP path --> SI-01

Engineering/test clients
  +-- IF-03 over available IP path --> SI-01

DisplayRev2Wifi / Smart Display V2
  +-- discovers SI-01 service through mDNS
  +-- IF-09 client session --> SI-01

Backend
  +-- IF-06 over configured external path --> SI-01
```

An available IP path may be direct/point-to-point, same-host or loopback during development/test, or may run over normal LAN/Wi-Fi infrastructure in a field deployment. A Wi-Fi router/access point is therefore **optional deployment infrastructure**, not part of the semantic definition of IF-03 or IF-09.

#### Connectivity and reachability state

Network health is not one boolean and should not be modeled as one mandatory chain. The system needs to expose separately observable states because they answer different operational questions.

<a id="fig-sys-03"></a>
![Network connectivity status — separate observations](../assets/architecture/system-connectivity-status.svg)
*Figure SYS-03 — Network connectivity status — separate observations.*

At minimum distinguish:

- **local IP connectivity** — network interface/link of the **Timing Point Application** (SI-01) and its ability to communicate with local peers;
- **configured router/AP connectivity** — whether the deployment is connected/associated with the configured local router or access point; this may legitimately be **N/A** for direct/development/test compositions;
- **external network reachability** — whether connectivity beyond the local network is available;
- **backend connectivity** — whether the configured backend endpoint/transport/session is healthy.

These states must not be conflated. For example, local timing and direct local clients may remain fully operational while the router, external uplink or backend is unavailable. Conversely, a configured field deployment may need to report that it has lost its expected router/AP even before external reachability is tested.

The exact process/thread topology, internal runtime cardinality, queueing model, service composition, connectivity probing mechanism and adapter implementation are intentionally outside this SSSD.

### Cross-system architectural constraints

#### State ownership and disconnected operation

The **Timing Point Application** (SI-01) keeps the local operational state. Losing a GUI/test client or external connection must not move that state elsewhere or make synchronisation appear healthy when it is not.

#### Public/private implementation boundary

System contracts used by public reference/core implementation code must allow private production implementations to plug in without public code depending on private source or proprietary identities.

Selected implementation families may be supplied by Java-8-compatible extension providers behind those stable contracts. The expected extension families are timing-data representation/codec, upstream protocol, antenna implementation, CAN protocol and display protocol. Extension discovery and provider selection are SI-01 implementation/composition concerns; they must not change the software-system interfaces or require proprietary source in the public repositories. Public/reference compositions must remain executable with synthetic/reference implementations so the public system can be built and verified independently.

#### Interface-first separation

Software-item interaction is defined in terms of system-owned semantics. Internal implementation choices such as RabbitMQ libraries, HTTP servers, logging frameworks, executors or file formats are owned by the relevant software-item architecture unless the choice becomes part of an external contract.

#### Deployment portability

The architecture must support constrained field deployment and normal Linux/Windows development/test environments without changing the software-item boundaries. Automated integration verification must be able to exercise network interfaces without provisioning a physical Wi-Fi router unless the test explicitly targets router/AP behaviour.

### Relationship to software-item architecture

The SSD for the **Timing Point Application** (SI-01) owns, among other things:

- layered application responsibilities;
- `TimingNode` software/domain decomposition, separate registration-hardware topology, and their configuration/data-source identity mapping;
- threading/concurrency and internal messaging;
- status architecture and lifecycle handling;
- persistence and restore strategy;
- logging/configuration/composition choices;
- Java/core/library decisions;
- RFID/CAN/display adapter architecture behind the system device interfaces;
- upstream transport implementation behind IF-06;
- resource-budget implications of those choices.

The SSD for the planned **Desktop GUI Application** (SI-02) owns its requirements/internal architecture while conforming to the API and applicable IDDs.

### Architecture review model

The project uses the 4+1 architectural view model as a review aid, not as a requirement for five documents. At system level, the SSSD primarily provides system context and deployment/relationship views. The software-item SSDs provide the coherent logical, process, development and deployment views of each item and reference selected use cases as scenarios.

Reference: `reference/README.md`.

### Open system-architecture questions

- final system interface ISD/IDD breakdown and ownership;
- authentication, authorisation and secure transport requirements across software-item boundaries;
- compatibility/versioning policy for IF-03 and IF-06;
- which device semantics require system-level IDDs versus software-item-only design;
- required behaviour when local IP, configured router/AP, external network or backend connectivity is unavailable;
- final system-level availability/recovery requirements.


---

## API Interface Specification (ISD)

**Source document:** [32-03-ISD-application-control-status.md](32-03-ISD-application-control-status.md)

Status: review candidate / AP-1 first-executable slice

System interface: **IF-03 — API**

### Purpose

This Interface Specification Document owns the general programmable remote contract between SI-01 and the planned SI-02 GUI, engineering/service tools and automated ST-1 black-box/integration tooling.

For AP-1 it defines only the first-executable subset needed to expose build/version identity, current status and status-change events. The interface is intentionally broader than "status": later supported remote control, test and diagnostic operations may extend IF-03 when their SIP increments require them.

A simple browser-based test client may consume IF-03 later, just like the current JavaFX engineering client. It is not currently a separate product interface.

### Inputs

IF-03 is a system-owned interface allocated by
`31-SSSD-software-system-specification-document.md`. Its detailed contract is
therefore downstream of that allocation and upstream of both participating software-item
specifications. Applicable system use cases supply operational intent.

The SI-01/GUI SSDs and the SVP may trace to this ISD; they are not inputs to it.

### Parties

```text
client side
  planned SI-02 GUI / engineering client
  headless ST-1 / integration test driver
  other supported remote tooling
        |
        | IF-03 API
        v
SI-01 Timing Point Application
```

SI-01 keeps the TimingNode/status state. Clients observe/query it and later submit permitted commands; cached responses do not move that state into the client.

### Transport baseline

The first-executable transport contract is:

- HTTP with JSON for request/response queries;
- WebSocket for live status/event delivery;
- API major version represented in the resource path as `/api/v1`;
- network boundary usable when SI-01 and the client run on different hosts;
- the same semantic application model may also be represented through local console/remote-shell adapters, but those transports are not owned by this ISD.

The contract must remain compatible with the current Java 8 SI-01 baseline and the selected runtime on the Raspberry Pi target. HTTP and WebSocket may use separate configured listeners/ports in the first executable; the resource paths and semantics remain one IF-03 contract.

### First-executable resources

```text
GET /api/v1/version
GET /api/v1/status
WS  /api/v1/events
```

Only `GET` is required for the two HTTP resources in this slice. Later application commands may add other methods/resources without changing the ownership principle.

### Common compatibility rules

- JSON member names defined by this first slice are stable within API major version `v1`.
- Clients shall tolerate additional/unknown JSON members so the status model can grow compatibly.
- A breaking representation/semantic change requires a new API major path such as `/api/v2` or an explicitly documented compatible migration mechanism.
- Unknown event types shall not corrupt client state; a client may ignore/log an event type it does not understand and can always re-query `/status`.
- UTF-8 is used for JSON text.
- timestamps in the public contract use ISO-8601 UTC text form;
- the API major version is carried by the `/api/v1` resource namespace and is not repeated in every JSON object; `/version` still reports `apiVersion` as build/interface identity.

### Build/version identity

The stable first-executable build identity is:

```json
{
  "application": "timing-application",
  "version": "<project-version>",
  "revision": "<source-revision>",
  "sourceRef": "<branch-tag-or-ref>",
  "buildOrigin": "local|github-actions",
  "dirty": false,
  "apiVersion": "1"
}
```

Field semantics:

- `application` — stable application identity for SI-01;
- `version` — project/application version from the produced build;
- `revision` — exact source revision used to produce the running artifact, normally the Git commit SHA;
- `sourceRef` — source branch, tag or CI ref associated with the build;
- `buildOrigin` — stable build-environment class such as `local` or `github-actions`;
- `dirty` — whether uncommitted source changes were present when the artifact was built;
- `apiVersion` — IF-03 major API version represented by this contract.

The embedded identity deliberately excludes wall-clock build time, CI run/build number,
actor/user and other per-run metadata. Those values would make otherwise identical build
inputs produce different artifacts merely because a build was repeated. `revision` remains the
exact source authority; `sourceRef` and `buildOrigin` provide the human diagnostic context
needed when testing an artifact. A `dirty=true` local build is explicitly not fully described
by its commit SHA alone.

### Current status response

The status resource is intentionally compact. Build identity is queried through
`/version`; status carries only current operational state.

> This is an external interface shape. It does not prescribe a Java class with
> the same structure or a class named `ApplicationStatusSnapshot`. The
> implementation may assemble this response from the application objects that
> exist when the HTTP/status adapter is implemented.

```json
{
  "nodes": [
    {
      "id": "<configured-timing-node-id>",
      "locationId": null,
      "state": "CLOSED"
    }
  ],
  "problems": []
}
```

The first executable does not expose a separate application lifecycle state in
`/status`. A successful query already establishes that the IF-03 service is
running; startup/shutdown process lifecycle remains an internal/runtime concern
for this slice.

Internally SI-01 may host 1..N `TimingSystem` aggregates, each with its own
`SystemStatus`, but `TimingSystemId` is deliberately not part of this external
IF-03 shape. The `nodes` array aggregates the configured TimingNodes.
`TimingNodeId` is application-wide unique and is represented as `id` in the
compact IF-03 node object, so node-specific resources can use
`/api/v1/node/{id}/...` without exposing an internal TimingSystem identifier.

In the Step-4 first-registration slice, `locationId` is either `null` while
no operational location is assigned or the positive current IF-05 `LocationId`
value. `state` is `CLOSED` or `OPEN`. A closed node may retain its last
selected location during the same runtime session; startup/recovery does not
invent a current operational location from historical TimingData.

Problem entries use:

```json
{
  "code": "<stable-machine-code>",
  "severity": "WARNING|ERROR",
  "message": "<human-readable-summary>"
}
```

Clients must not make business decisions by parsing the human-readable `message`; `code` and structured status fields are the machine-readable contract.

### First-executable semantic operations

#### IF03-OP-001 — Get build/version identity

HTTP mapping:

```text
GET /api/v1/version
```

Successful response:

- HTTP `200`;
- `application/json`;
- body is the build/version identity defined above.

Semantics:

- returns the authoritative application build/version identity;
- does not derive a separate client-specific version value;
- remains stable for the lifetime of one running application build;
- is equivalent in meaning to version identity shown by first-executable console/remote-shell views.

#### IF03-OP-002 — Get current status

HTTP mapping:

```text
GET /api/v1/status
```

Successful response:

- HTTP `200`;
- `application/json`;
- body contains the current TimingNode status using the schema above.

Later subsystem/device/backoffice fields may extend the model without changing the ownership principle.

#### IF03-OP-004 — Get public/engineering capabilities

HTTP mapping:

```text
GET /api/v1/capabilities
```

Successful response:

```json
{
  "capabilities": [
    {
      "id": "DIRECT_REGISTRATION_SIMULATION",
      "supported": true,
      "enabled": true
    }
  ]
}
```

Unknown capability IDs added within API v1 are ignored by clients that do not
understand them. The direct-registration engineering command below is available
only when `DIRECT_REGISTRATION_SIMULATION` is both supported and enabled.

#### IF03-OP-005 — Set current operational location

HTTP mapping:

```text
PUT /api/v1/node/{id}/location
```

Request:

```json
{
  "locationId": 24
}
```

The value uses the shared IF-05 `LocationId` representation. Concrete allowed
values remain event/profile/deployment policy outside IF-03.

Successful response is HTTP `200`:

```json
{
  "result": "UPDATED"
}
```

The operation is accepted only while the TimingNode is CLOSED. A successful
change is reflected by subsequent status queries and a `STATUS_CHANGED` event.

#### IF03-OP-006 — Open registration

HTTP mapping:

```text
POST /api/v1/node/{id}/open
```

The request has no semantic body. Successful HTTP `200` results are
`OPENED` or `ALREADY_OPEN`. OPEN without a configured current LocationId is
a domain conflict and does not change state.

#### IF03-OP-007 — Close registration

HTTP mapping:

```text
POST /api/v1/node/{id}/close
```

The request has no semantic body. Successful HTTP `200` results are
`CLOSED` or `ALREADY_CLOSED`. A successful state change is followed by a
`STATUS_CHANGED` event.

#### IF03-OP-008 — Simulate an automatic registration

This is an engineering capability, not a replacement RFID or manual-entry
interface. The short `auto-reg` resource name is a Step-4 review label; the
semantic injection boundary is the important contract decision.

HTTP mapping:

```text
POST /api/v1/dev/node/{id}/auto-reg
```

Request:

```json
{
  "id": "N001",
  "time": "2026-10-01T12:00:00.000000000Z"
}
```

The path `{id}` addresses the TimingNode. The request-body `id` is the
already-resolved shared `RegistrationId`; `N001` is only a short deterministic
example and does not define a required prefix or format. `time` is the accepted observation
time. SI-01 supplies source identity, current LocationId, next committed sequence
and recordedAt and executes the same accepted-registration operation used after
normal RFID interpretation/filtering.

Successful HTTP `200` response:

```json
{
  "seq": 1
}
```

The returned sequence identifies the newly committed record within the addressed
TimingNode. The committed record becomes visible through IF03-OP-009 and a
`TIMING_DATA_COMMITTED` event.

#### IF03-OP-009 — Query committed LogBook

The LogBook resource is node-addressed and bounded. A client does not need to
download the complete history merely to learn its size.

HTTP mappings:

```text
GET /api/v1/node/{id}/logbook
GET /api/v1/node/{id}/logbook?from=101&limit=100
GET /api/v1/node/{id}/logbook?last=100
```

Without query parameters the response is metadata only:

```json
{
  "count": 12457,
  "first": 1,
  "last": 12457
}
```

For an empty LogBook, `count` is `0` and `first`/`last` are `null`.

`from` is an inclusive committed source sequence. `limit` is the maximum
number of records returned. `last` requests the newest records while preserving
source-sequence order. `last` cannot be combined with `from` or `limit`.
The Step-4 v1 baseline limits `limit` and `last` to 1..1000.

A record-bearing response is:

```json
{
  "count": 12457,
  "next": 201,
  "records": []
}
```

`count` is the total committed record count at response time. `next` is the
next source sequence to request when more records are available, otherwise
`null`. Each `records` element uses the public IF-05 TimingData JSON field
semantics. Records are returned in committed source-sequence order; queued or
uncommitted work is never exposed as LogBook content.

#### IF03-OP-003 — Subscribe to status/event updates

WebSocket mapping:

```text
/api/v1/events
```

The first executable may expose this path on a dedicated configured WebSocket listener rather than the A06 HTTP listener. Clients therefore configure the WebSocket endpoint independently while the path and payload semantics remain stable.

After the WebSocket connection is established SI-01 shall immediately send a complete `STATUS_SNAPSHOT` event before normal change events are relied upon.

Event envelope:

```json
{
  "eventType": "STATUS_SNAPSHOT",
  "occurredAt": "<ISO-8601 UTC>",
  "payload": {}
}
```

Step-4 event types:

```text
STATUS_SNAPSHOT
STATUS_CHANGED
TIMING_DATA_COMMITTED
```

For `STATUS_SNAPSHOT`, `payload` contains the complete current status representation.

For `STATUS_CHANGED`, `payload` also contains a complete current status
representation. SI-01 emits this event only after an actual authoritative
location/lifecycle/status change; it shall not manufacture periodic or duplicate
changes merely to exercise the transport.

For `TIMING_DATA_COMMITTED`, `payload` is the committed public IF-05 TimingData
record. It is emitted only after durable local append and LogBook visibility.
Recovery does not replay old records as new live events.

WebSocket delivery order is sufficient within one connected session. The stable
TimingData record key, rather than a separate transient WebSocket sequence,
provides deduplication when history and live delivery overlap.

### Reconnect and resynchronisation

Reconnect semantics rebuild authoritative current state/LogBook gaps before the
client declares its view live:

1. client reconnects to `/api/v1/events`;
2. SI-01 sends a complete `STATUS_SNAPSHOT`; the client begins buffering later
   WebSocket events;
3. the client replaces its cached status from the snapshot;
4. for each selected/cached node, the client queries
   `GET /api/v1/node/{id}/logbook` and fetches only required bounded ranges,
   normally continuing from the last cached sequence;
5. the client applies buffered `STATUS_CHANGED` events in WebSocket order;
6. buffered `TIMING_DATA_COMMITTED` records already present in the rebuilt
   LogBook view are discarded by stable TimingData record key; later records are
   appended in source-sequence order;
7. only after this merge is complete does the client mark the view live.

No durable WebSocket replay across disconnected sessions is required. The
authoritative LogBook is the recovery source for committed TimingData missed
while disconnected.

### Error responses

HTTP failures use a JSON envelope:

```json
{
  "error": {
    "code": "<stable-machine-code>",
    "message": "<human-readable-summary>"
  }
}
```

Step-4 mapping:

| HTTP status | Stable example codes / meaning |
| --- | --- |
| `400` | `MALFORMED_REQUEST`, `INVALID_VALUE` |
| `403` | `CAPABILITY_NOT_ENABLED` |
| `404` | `NOT_FOUND`, `NODE_NOT_FOUND` |
| `405` | `METHOD_NOT_ALLOWED` |
| `409` | domain-state conflict such as `NO_LOCATION`, `NODE_NOT_CLOSED`, `NODE_NOT_OPEN` |
| `503` | `BUSY`, `UNAVAILABLE`, or expected commit dependency failure |
| `504` | `OUTCOME_UNKNOWN` after the caller-side operation guard timeout |
| `500` | unexpected internal interface failure |

A timeout response explicitly means that the accepted operation may still execute;
the transport shall not cancel already accepted TimingNode work. Before retrying a
state-changing command whose outcome is unknown, the client resynchronises current
status/history.

A normal reported problem represented by `/status` is not converted into HTTP
`500` merely because a problem entry is present.

### Network access and first-executable security policy

Authentication/authorisation is explicitly **deferred** for the first executable development baseline. This is a deliberate scope decision, not an assumption that the final product is unauthenticated.

Until a later security/interface increment defines authentication:

- the default IF-03 listen address shall be loopback/local-only;
- non-loopback binding must require explicit configuration;
- remote first-executable demonstrations shall run only on a trusted development/test network;
- deployment/prod exposure outside that controlled environment is out of scope;
- CORS/browser-origin policy is deferred until a browser-based client is actually needed.

This allows ST-1, engineering-client and later SI-02 development without prematurely inventing production security while preventing accidental default exposure.

### First-executable contract rules

<a id="IF03-REQ-001"></a>

**IF03-REQ-001 — Shared semantics**

HTTP/JSON and WebSocket representations shall map to the
shared SI-01 application/status semantics rather than
implement independent business/status state in the transport
adapter.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-022`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-022), [`SI01-REQ-030`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-030)
- **Satisfied by:** [`Api`](41-01-SSD-timing-application-specification-document.md#Api), [`CommandHandler`](41-01-SSD-timing-application-specification-document.md#CommandHandler)

---


<a id="IF03-REQ-002"></a>

**IF03-REQ-002 — Remote-host operation**

The interface shall support operation across a normal IP
network boundary when non-loopback access is explicitly
configured, so a client can run on a workstation while SI-01
runs on another host such as a Raspberry Pi.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-031`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-031)
- **Satisfied by:** [`Api`](41-01-SSD-timing-application-specification-document.md#Api)

---


<a id="IF03-REQ-003"></a>

**IF03-REQ-003 — Version query**

The interface shall provide `GET /api/v1/version` representing `IF03-OP-001`.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-010`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-010), [`SI01-REQ-011`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-011)
- **Verified by:** [`VC-ST1-001`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-001)

---


<a id="IF03-REQ-004"></a>

**IF03-REQ-004 — Status query**

The interface shall provide `GET /api/v1/status`
representing `IF03-OP-002`.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-020`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-020), [`SI01-REQ-021`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-021), [`SI01-REQ-022`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-022)
- **Satisfied by:** [`Api`](41-01-SSD-timing-application-specification-document.md#Api), [`CommandHandler`](41-01-SSD-timing-application-specification-document.md#CommandHandler)
- **Verified by:** [`VC-ST1-001`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-001)

---


<a id="IF03-REQ-005"></a>

**IF03-REQ-005 — Live status/event delivery**

The interface shall provide WebSocket `/api/v1/events` representing `IF03-OP-003` for the first executable.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-023`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-023)
- **Verified by:** [`VC-ST1-001`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-001)

---


<a id="IF03-REQ-006"></a>

**IF03-REQ-006 — Reconnect to current state**

A client that connects/reconnects shall receive a complete current status snapshot before relying on subsequent live events.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-023`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-023)
- **Verified by:** [`VC-ST1-001`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-001)

---


<a id="IF03-REQ-007"></a>

**IF03-REQ-007 — Machine-readable representation**

The HTTP query representation shall be machine-readable JSON suitable for SI-02, engineering clients and automated ST-1 verification.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-031`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-031)

---


<a id="IF03-REQ-008"></a>

**IF03-REQ-008 — Explicit failure response**

Unsupported or invalid HTTP requests shall produce the explicit JSON failure outcome defined in this ISD rather than a successful response containing silently invalid data.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-031`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-031)

---


<a id="IF03-REQ-009"></a>

**IF03-REQ-009 — Safe default listen scope**

Without explicit configuration the first-executable IF-03 service shall bind only to a local/loopback interface.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-032`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-032)

---


<a id="IF03-REQ-010"></a>

**IF03-REQ-010 — Compatible extension**

Clients shall be able to ignore unknown response members/event types within API major version `v1`; breaking contract changes shall not silently redefine existing `v1` semantics.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-033`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-033)

---


<a id="IF03-REQ-011"></a>

**IF03-REQ-011 — Step-4 location and lifecycle control**

IF-03 shall expose 1..N application-wide-unique TimingNode identities with current
optional LocationId and OPEN/CLOSED state and shall provide node-addressed
IF03-OP-005/006/007 location/open/close control using the shared SI-01
application/domain semantics.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-040`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-040)
- **Verified by:** [`VC-ST1-002`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-002)

---


<a id="IF03-REQ-012"></a>

**IF03-REQ-012 — Engineering capability discovery**

IF-03 shall provide IF03-OP-004 so the Engineering Client can determine whether
direct registration simulation is supported and enabled before presenting or
using that control.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-043`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-043)
- **Verified by:** [`VC-ST1-002`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-002)

---


<a id="IF03-REQ-013"></a>

**IF03-REQ-013 — Dev auto-reg control**

When the advertised capability is supported and enabled, IF-03 shall provide
IF03-OP-008 and pass only `id` plus `time` to the normal SI-01
accepted-registration operation.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-041`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-041), [`SI01-REQ-043`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-043)
- **Verified by:** [`VC-ST1-002`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-002)

---


<a id="IF03-REQ-014"></a>

**IF03-REQ-014 — Committed LogBook query**

IF-03 shall provide IF03-OP-009 as a node-addressed LogBook metadata and bounded
range query in source-sequence order using public IF-05 field semantics.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-042`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-042)
- **Verified by:** [`VC-ST1-002`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-002)

---


<a id="IF03-REQ-015"></a>

**IF03-REQ-015 — Live committed TimingData delivery**

The IF-03 WebSocket event stream shall emit `TIMING_DATA_COMMITTED` only after
the corresponding TimingData record is committed and visible in the authoritative
LogBook.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-042`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-042)
- **Verified by:** [`VC-ST1-002`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-002)

---


<a id="IF03-REQ-016"></a>

**IF03-REQ-016 — Rebuild LogBook before live presentation**

A reconnecting client shall be able to combine the current status snapshot,
bounded authoritative LogBook ranges and buffered live events using stable
TimingData record keys before declaring its view live.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-044`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-044)
- **Verified by:** [`VC-ST1-003`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-003)

---


### Relationship to SI-01 SSD

Each IF-03 requirement owns its upstream SI-01 traceability through its
`derived_from` relation. That relation is authored once with the requirement and
the generated engineering reader/graph provides the inverse context back to IF-03.

The SI-01 SSD references this contract instead of duplicating transport-level
requirements.

### Verification references

IF-03 owns the transport contract and acceptance semantics above. Concrete
verification procedures are downstream and are specified in
`61-01-VTS-timing-application-verification-test-specification.md`.

Current ST-1 cases using IF-03 include:

- `VC-ST1-001` — query version/status, connect/reconnect the event stream and
  verify a complete current status snapshot through the running executable;
- `VC-ST1-002` — exercise the first-registration control/history/live flow
  through the running executable.

The VTS maps each case to the applicable SSD/ISD requirements. Execution status,
PASS/FAIL, logs and persisted test artifacts belong to generated verification
evidence rather than this ISD.

### Remote shell scope

The first executable may expose equivalent version/status semantics through a remote-shell adapter as required by the SIP, but AP-1 does **not** introduce a separate system ISD for that transport.

Reason:

- the public programmable contract needed by the planned SI-02 GUI, engineering tooling and ST-1 is IF-03;
- remote-shell technology is an implementation/support adapter concern at this stage;
- it must reuse the shared version/status application queries and must not own a separate status model.

If the remote shell later becomes a stable externally consumed system interface, it should receive an appropriate ISD then.

### Deferred interface scope

The following IF-03 capabilities are visible in later use cases/architecture but intentionally outside this AP-1 baseline:

- start procedure;
- RFID power/reinitialisation commands;
- ready-team add/remove;
- manual registration/penalty/revocation beyond the dev auto-reg path;
- reference-data administration;
- backoffice controls;
- detailed diagnostics/support export;
- production authentication/role-based authorisation;
- browser CORS/origin policy if a browser-based test/client tool is later added.

They should be added when their corresponding SIP capability approaches implementation.

### Remaining AP-1 implementation choices

The following are implementation/toolchain selections rather than unresolved interface semantics and may be chosen in the implementation repository/toolchain step:

- concrete Java HTTP/WebSocket library;
- concrete remote-shell library/technology;
- concrete JSON library;
- concrete configuration library;
- exact JDK/Maven/toolchain provisioning.

Changing one of these libraries must not silently change the contract defined above.


---

## TimingData Interchange Interface Specification (ISD)

**Source document:** [32-05-ISD-timingdata-interchange.md](32-05-ISD-timingdata-interchange.md)

Status: draft / Step 4 D03 TimingData interface

System interface: **IF-05 — TimingData Interchange**

### Purpose

This Interface Specification Document defines the normative TimingData
interchange contract.

It defines **what** every conforming TimingData representation must preserve:

- record identity and source ordering;
- Node ID, Location ID and Registration ID semantics;
- automatic and manual registration semantics;
- time semantics defined by record types;
- compatibility rules for the default/reference representation and alternative
  product/event-specific representations.

Concrete encoding choices for the current default/reference representation are
defined in `33-05-IDD-timingdata-interchange.md`.

IF-05 does not define Java classes, provider/factory APIs, worker threads,
storage classes or UI behaviour. Those are software-item design concerns.

The current slice does not define TimingNode OPEN/CLOSE as TimingData records and
does not enable registration revocation at runtime. A future design may add
revoke records without changing the identity/order principles defined here.

### Inputs

IF-05 is a system-owned interface allocated by
`31-SSSD-software-system-specification-document.md`.

Applicable system use cases provide the operational intent. Software-item
specifications and detailed designs consume this ISD and shall not redefine the
interface semantics independently.

### Interface scope

IF-05 owns:

- the semantic values carried by TimingData records;
- stable record identity;
- source ordering;
- registration identity and registration-family semantics;
- timestamp semantics;
- compatibility obligations across concrete representations;
- requirements on the public/default reference representation.

IF-05 does **not** own:

- RFID/tag decoding or source-resolution algorithms;
- TimingNode lifecycle implementation;
- sequence-allocation implementation;
- persistence classes or filesystem APIs;
- application queues/threads;
- query/read-model implementation;
- UI rendering;
- upstream transport/session mechanics;
- Java provider/factory/codec design.

### Common TimingData semantics

Every TimingData record has a small common envelope:

| Semantic value | Presence | Meaning |
| --- | --- | --- |
| Node ID | Always | identifies the TimingNode that owns the source stream |
| sequence number | Always | record number within that Node ID stream |
| Location ID | Always | location captured with the record |
| record type | Always | identifies how the remaining record data shall be interpreted |
| Registration ID | By record type | required by registration record types |
| time | By record type | time value defined by the selected record type |
| code | By record type | additional record-type-specific classification/meaning |

`By record type` does not mean optional when that record type is selected. For
example, Registration ID and time are required for a registration
record, but are not fields of a future OPEN/CLOSE or other unrelated record
type.

A committed record captures its Location ID. Later TimingNode reconfiguration
does not change that historical value.

Within a TimingSystem, the combination of Node ID and sequence number identifies
one committed TimingData record. Sequence numbers are local to one Node ID
stream; they are not one application-wide counter.

The default/reference development-v1 design maps the currently supported record
types to JSON in `33-05-IDD-timingdata-interchange.md`.

### Record identity and sequence

Sequence rules:

- numbering is scoped per Node ID;
- the authoritative local source stream advances by exactly one for each
  committed record;
- a new source stream starts at **1**;
- sequence number **0 is reserved**;
- changing Location ID does not reset the sequence;
- sequence is an ordering/traceability value, not a timestamp;
- a committed sequence number is never reused within the same Node ID stream;
- the sequence does not wrap;
- an authoritative complete local stream is contiguous;
- partial/imported/exported subsets may contain visible gaps, but records are not
  renumbered and such a subset shall not be presented as a complete contiguous
  authoritative stream.

How software allocates and durably commits the next sequence is outside IF-05.

### Registration semantics

IF-05 currently defines registration semantics for:

- **automatic registration** — a registration originating from the automatic
  observation path;
- **manual registration** — a registration initiated manually by an
  operator/tool.

A registration record carries a **Registration ID** and **time**.
These values are specific to registration records; they are not common
TimingData-envelope values.

Registration semantics shall support:

- adding a registration; and
- revoking a previously added registration.

A revocation is represented by a new TimingData record and does not modify the
original committed registration record. It refers to the registration being
withdrawn using the Registration ID and time associated with that registration.

Whether further disambiguation is needed when the same Registration ID/time
combination can occur more than once remains a draft/open interface decision.

The concrete representation of add/revoke, automatic/manual registration and
time-source metadata belongs to the IDD.

### Registration ID boundary

Registration ID is a provider-neutral value used by registration record
families. It is not required for TimingData record types that do not
represent a registration.

For registration records, the common semantic form is a non-empty string.
Event/profile-specific allowed values, number ranges, tag mappings and
participant/reference-data rules remain outside IF-05.

Registration ID is separate from record identity (Node ID + sequence number).

### Time

For the current registration record types, `time` represents the absolute
instant assigned to that registration.

The current interface direction is to preserve that instant across conforming
representations. The exact textual representation belongs to the IDD.

Other TimingData record types may give `time` a different defined meaning, or
may not use a time value at all. `time` is therefore record-type-dependent,
not part of the always-present envelope.

### Default/reference representation

The project provides one default/reference representation for development,
engineering/test tooling and compatible consumers. Its concrete JSON/JSON Lines
design is documented by `33-05-IDD-timingdata-interchange.md`.

The reference representation is a design of the IF-05 semantic model; its JSON
member names, line framing, version field and optional metadata are not common
TimingData-envelope values.

### Alternative representations

A product/event-specific implementation may use another concrete representation,
including a different text, fixed-field, binary or proprietary format.

Such a representation does not need to reuse the default filename extension,
record framing or member names. Its interface conformance is assessed against
the applicable IF-05 requirements and the semantics of the record types it
supports.

### IF-05 requirements

These requirements are still under development. Their per-requirement maturity
is shown by `status`: `D` = Draft, `R` = Review, `A` = Approved,
`O` = Obsolete.

Concrete JSON member names, JSON Lines framing, code arrays, optional metadata
and representation-version conventions belong to the IDD and are not IF-05
requirements by themselves.

<a id="IF05-REQ-001"></a>

**IF05-REQ-001 — Common TimingData envelope**

Every TimingData record shall identify its Node ID, sequence number, Location ID
and record type. Values required in addition to this common envelope shall be
defined by the record type.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Source for:** [`SI01-REQ-045`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-045)

---


<a id="IF05-REQ-002"></a>

**IF05-REQ-002 — Record identity within a TimingSystem**

Within one Node ID stream, committed TimingData records shall have unique
sequence numbers. Within a TimingSystem, Node ID together with sequence number
shall uniquely identify a committed TimingData record.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Source for:** [`SI01-REQ-045`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-045), [`SI01-REQ-047`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-047)

---


<a id="IF05-REQ-003"></a>

**IF05-REQ-003 — Sequence progression**

For each Node ID stream, committed sequence numbers shall start at 1 and increase
by one for each subsequent committed TimingData record. Sequence number 0 shall
not identify a committed record.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Source for:** [`SI01-REQ-045`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-045), [`SI01-REQ-047`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-047)

---


<a id="IF05-REQ-004"></a>

**IF05-REQ-004 — Automatic and manual registration**

IF-05 registration records shall distinguish automatic registration from manual
registration.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Source for:** [`SI01-REQ-045`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-045)

---


<a id="IF05-REQ-005"></a>

**IF05-REQ-005 — Registration record values**

An added or revoked registration record shall identify the Registration ID and
time of the registration to which it refers.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Source for:** [`SI01-REQ-045`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-045)

---


<a id="IF05-REQ-006"></a>

**IF05-REQ-006 — Registration add and revoke**

IF-05 shall support adding a registration and revoking a previously added
registration. A revocation shall be represented by a new TimingData record and
shall refer to the registration being withdrawn using its Registration ID and
time; it shall not modify the original committed record.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Source for:** [`SI01-REQ-045`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-045)

---


<a id="IF05-REQ-007"></a>

**IF05-REQ-007 — Committed record immutability**

A committed TimingData record shall not be modified or renumbered. A later
operation that changes the meaning of earlier data shall be represented by a new
TimingData record.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Source for:** [`SI01-REQ-045`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-045), [`SI01-REQ-047`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-047)

---


### Deferred from this first slice

- TimingNode OPEN/CLOSE TimingData representation;
- revoke disambiguation beyond Registration ID + time, if later needed;
- start-procedure record type and payload;
- penalty/correction record types and payloads;
- unknown-registration semantics;
- source/tag provenance fields;
- filename/directory policy, retention, rotation and filesystem-specific
  durability primitives;
- upstream transport/session/reconciliation semantics owned by IF-06;
- further IF-03 resources that create or inspect future record types.


---

## TimingData Interchange Interface Design Description (IDD)

**Source document:** [33-05-IDD-timingdata-interchange.md](33-05-IDD-timingdata-interchange.md)

Status: draft / development-v1 reference representation

System interface: **IF-05 — TimingData Interchange**

Implements: `32-05-ISD-timingdata-interchange.md`

### Purpose

This Interface Design Description defines the current **default/reference
development-v1 representation** of IF-05 TimingData.

The ISD owns the normative TimingData semantics and requirements. This IDD
describes how that contract is represented as compact JSON records in an
append-only JSON Lines file.

This document deliberately does not define Java classes, factories, providers,
threads, queues or storage implementation classes.

### Design overview

The reference design uses:

- one compact JSON object per TimingData record;
- one complete JSON object per JSON Lines record;
- one Node ID source stream per file;
- monotonically increasing `seqNr`;
- explicit record type in `recType`;
- compact semantic codes in `code`;
- absolute UTC timestamp text;
- per-record integer representation version `v`.

<a id="fig-if05-01"></a>
![TimingData v1 interchange model](../assets/architecture/timingdata-interchange-model.svg)

*Figure IF05-01 — IF-05 semantics mapped to development-v1 JSON and JSON Lines.*

### Semantic-to-JSON mapping

| Semantic value | Presence | v1 JSON member |
| --- | --- | --- |
| representation version | Always | `v` |
| Node ID | Always | `nodeId` |
| sequence number | Always | `seqNr` |
| Location ID | Always | `locId` |
| record type | Always | `recType` |
| time | By record type | `time` |
| Registration ID | By record type | `regId` |
| code | By record type | `code` |
| record creation time metadata | Optional | `recTime` |

The stable IF-05 record key `(Node ID, sequence number)` is represented by
`(nodeId, seqNr)`.

### Registration record mapping

#### AUTO_REG

Automatic registration add:

```text
recType = AUTO_REG
code    = [ADD]
```

The record type already carries the automatic-registration meaning, so `AUTO`
is not repeated in `code`.

Reserved future revoke mapping:

```text
recType = AUTO_REG
code    = [REV]
same regId
same time
```

#### MAN_REG

Manual registration using system-assigned time:

```text
recType = MAN_REG
code    = [ADD, AUTO]
```

Manual registration using operator-entered time:

```text
recType = MAN_REG
code    = [ADD, MAN]
```

Reserved future revoke mappings:

```text
[ADD, AUTO] -> [REV, AUTO]
[ADD, MAN]  -> [REV, MAN]
```

Canonical writer output places the action (`ADD` or future `REV`) first.
Array order is not semantic to a reader; the valid code combination is.
Duplicate, contradictory or unknown codes for a known record type are invalid.

A future revoke record repeats the original `regId` and `time`, receives a
new `seqNr` and `recTime`, and never rewrites the original record.

### Development-v1 record matrix

| Record type | Current add code | Required registration data | Reserved future revoke code |
| --- | --- | --- | --- |
| `AUTO_REG` | `["ADD"]` | `regId`, `time` | `["REV"]` |
| `MAN_REG` | `["ADD","AUTO"]` or `["ADD","MAN"]` | `regId`, `time` | `["REV","AUTO"]` or `["REV","MAN"]` |

### Development-v1 JSON contract

Known members use the following JSON types and validation rules.

| Member | JSON type | Presence | v1 design rule |
| --- | --- | --- | --- |
| `v` | integer | Always | exactly `1` for the current development format |
| `nodeId` | string | Always | non-empty Node ID |
| `seqNr` | integer | Always | `1..9007199254740991`; plain decimal; v1 reference-design limit |
| `locId` | integer | Always | positive Location ID representation |
| `recType` | string | Always | identifies the concrete v1 record type |
| `time` | string | By record type | required for `AUTO_REG` and `MAN_REG`; canonical time text |
| `regId` | string | By record type | required for `AUTO_REG` and `MAN_REG`; non-empty Registration ID |
| `code` | array of strings | By record type | required for `AUTO_REG` and `MAN_REG`; labels/codes valid for the selected `recType` |
| `recTime` | string | Optional | canonical record-creation time metadata when emitted |

Canonical writer member order:

```text
v
nodeId
seqNr
locId
recType
time
regId
code
recTime   # when present
```

Validation rules:

- every `Always` member is present and non-null;
- every `By record type` member required by the selected `recType` is present and non-null;
- `Optional` members such as `recTime` may be omitted;
- `nodeId` is not normalized, case-folded or derived by the reference reader/writer;
- `AUTO_REG` currently accepts exactly `["ADD"]`;
- `MAN_REG` currently accepts `ADD` plus exactly one of `AUTO` or `MAN`;
- readers may accept a valid `code` combination in another array order;
- canonical writer output always emits action first;
- `seqNr` remains authoritative source order; no chronological ordering is
  inferred from `time` or `recTime`.

### Timestamp encoding

Canonical development-v1 timestamp text for registration `time`, and for
optional `recTime` when present, is:

```text
YYYY-MM-DDTHH:mm:ss[.fraction]Z
```

Rules:

- literal `Z` represents UTC;
- fractional seconds are optional and contain **1 to 9 digits** when present;
- canonical writer output omits the fractional part for a whole second;
- unnecessary trailing fractional zeroes are removed;
- offsets such as `+02:00`, implicit local time and timezone names are not
  canonical v1 values.

Examples:

```text
2026-10-01T12:00:00Z
2026-10-02T10:57:43.444Z
2026-10-02T10:57:43.444123789Z
```

`recTime`, when present, is optional record-creation metadata. It is not a
durable-commit marker and is not part of the common IF-05 record envelope.

### JSON Lines file design

The default/reference development-v1 file uses UTF-8 JSON Lines (`.jsonl`) and
contains records from exactly one `nodeId` source stream.

Rules:

- encoding is UTF-8 without BOM;
- there is no file header, footer or comment syntax;
- `v` is carried by every record;
- one complete TimingData JSON object is written per physical line;
- all records in one file use the same `nodeId`;
- canonical writer line ending is **LF** (`0x0A`);
- a reader may accept **CRLF** (`0x0D 0x0A`);
- a line terminator completes the record boundary;
- valid JSON bytes at EOF without LF/CRLF are an incomplete trailing record and
  are not committed;
- blank lines are invalid input;
- every complete line is independently JSON-decodable;
- canonical writer output is compact single-line JSON;
- insignificant JSON whitespace and member ordering are not semantic to readers;
- committed records are append-only and are not rewritten;
- valid complete records before an incomplete trailing line remain readable;
- recovery/import validates Node ID and sequence ordering and reports gaps,
  duplicates or regressions explicitly.

The exact filename, directory mapping, rotation/retention policy and filesystem
durability primitive are outside IF-05. A different TimingData representation
does not have to use `.jsonl`.

### Reference JSON examples

Automatic registration:

```json
{"v":1,"nodeId":"Test","seqNr":1,"locId":24,"recType":"AUTO_REG","time":"2026-10-01T12:00:00Z","regId":"N0001","code":["ADD"],"recTime":"2026-10-02T10:57:43.444Z"}
```

Manual registration using system-assigned time:

```json
{"v":1,"nodeId":"Test","seqNr":2,"locId":24,"recType":"MAN_REG","time":"2026-10-01T12:00:05Z","regId":"N0002","code":["ADD","AUTO"],"recTime":"2026-10-02T10:57:45.1Z"}
```

Manual registration using operator-entered time:

```json
{"v":1,"nodeId":"Test","seqNr":3,"locId":24,"recType":"MAN_REG","time":"2026-10-01T11:59:58.25Z","regId":"N0003","code":["ADD","MAN"],"recTime":"2026-10-02T10:57:46Z"}
```

Reserved future revoke examples:

```json
{"v":1,"nodeId":"Test","seqNr":4,"locId":24,"recType":"AUTO_REG","time":"2026-10-01T12:00:00Z","regId":"N0001","code":["REV"],"recTime":"2026-10-02T11:05:12.123Z"}
{"v":1,"nodeId":"Test","seqNr":5,"locId":24,"recType":"MAN_REG","time":"2026-10-01T11:59:58.25Z","regId":"N0003","code":["REV","MAN"],"recTime":"2026-10-02T11:05:14Z"}
```

The Registration IDs above are synthetic test/example data. Four numeric digits
are used so examples remain convenient for later test sets containing up to
2000 teams; IF-05 does not impose that display convention on Registration ID.

### Compatibility and versioning design

Development v1 includes explicit per-record representation versioning through
an integer `v` member and uses the odd/even maturity convention below. Both are
design choices of this reference representation, not additional IF-05
requirements.

The default/reference representation uses integer format versions:

- **odd** values are development/unstable formats;
- **even** values are released/stable formats;
- current working format: `v = 1`;
- first frozen/released contract: expected `v = 2`;
- later incompatible development work starts at `v = 3`, then may freeze as
  `v = 4`;
- decimal/minor versions such as `1.1` are not used.

Within one supported baseline:

- a canonical writer emits only members defined by the version it implements;
- a reader tolerates additional JSON members when all required known fields
  remain valid;
- an unknown `recType` in an otherwise supported version is retained/reported
  as unsupported rather than reinterpreted as a known type;
- malformed JSON, missing required fields, invalid field types/values, invalid
  `code` combinations and sequence violations are explicit invalid-record
  conditions;
- an unsupported integer `v` is an explicit semantic-decoding compatibility
  failure;
- raw unsupported lines may be retained/exported but are not interpreted using
  another version's semantics;
- compatible additions do not silently change existing member/code meaning.

A stable even-numbered format is not silently redefined. Breaking work starts in
the next odd-numbered development format.

### ISD requirement realization

| ISD requirement | development-v1 design realization |
| --- | --- |
| IF05-REQ-001 | `nodeId`, `seqNr`, `locId` and `recType` form the common JSON envelope |
| IF05-REQ-002 | Node ID + `seqNr` identify a record when streams are combined |
| IF05-REQ-003 | `seqNr` starts at 1 and advances contiguously per Node ID source stream |
| IF05-REQ-004 | `recType` distinguishes `AUTO_REG` and `MAN_REG` |
| IF05-REQ-005 | registration records carry `regId` and `time` |
| IF05-REQ-006 | `code[]` represents ADD/REV while revoke repeats `regId` + `time` in a new record |
| IF05-REQ-007 | JSON Lines persistence is append-only; an existing committed record is not rewritten |

JSON Lines completion rules, unknown-member handling, integer `v`, the v1
`seqNr` limit, odd/even version-number convention and optional `recTime`
are concrete reference-design choices. They are intentionally not additional
IF-05 requirements.


---

## Application Configuration Interface Specification (ISD)

**Source document:** [32-11-ISD-application-configuration.md](32-11-ISD-application-configuration.md)

Status: review candidate / SIP Step-3 configuration baseline

System interface: **IF-11 — Application Configuration**

### Purpose

This Interface Specification Document defines the deployment/configuration contract consumed by SI-01. It describes how a deployment identifies internal TimingSystems and their TimingNodes, I/O assets, presentation bindings, runtime settings and secret references before application composition starts.

It deliberately does **not** define domain behaviour, a Java class hierarchy, a specific YAML library or production secret values.

### Inputs

IF-11 is a system-owned deployment/configuration interface allocated by
`31-SSSD-software-system-specification-document.md`. Applicable system use cases and
deployment constraints provide upstream intent. The SI-01 SSD consumes this contract;
its internal architecture and Java SDD are downstream and are not inputs to the ISD.

### Boundary

```text
deployment configuration
        |
        | IF-11
        v
SI-01 configuration loading
        |
        v
effective ApplicationConfig
        |
        v
validation
        |
        v
application composition
```

Build provenance is outside IF-11. `BuildIdentity` comes from the built application artifact and remains separate from deployment configuration.

### Effective configuration model

The logical **effective** configuration root is:

```text
ApplicationConfig
├── applicationId
├── timingSystems
│   └── <timingSystem>
│       ├── timingSystemId
│       ├── timingDataProvider
│       ├── upstreamProtocolProvider
│       └── timingNodes
├── io
│   ├── devices
│   │   └── antennaManager
│   │       └── antennas
│   ├── deviceNetworks
│   │   ├── can
│   │   └── network
│   ├── registrationRouting
│   ├── messaging
│   │   └── upstream
│   │       └── connectors
│   └── storage
│       └── timingData
│           └── path
├── presentation
├── logging
├── runtime
└── security
```

The structure is a contract for configuration ownership. It does not require one Java POJO for every node before a running slice needs it.

#### Application profile and baseline capabilities

A Timing Point Application may use a selected **application profile** as a
versioned default composition template. A profile can supply topology,
capability and compatibility defaults without introducing another domain model,
Java application subclass or software item.

This public baseline deliberately does not define concrete event/deployment
profile IDs, fixed TimingNode counts, device combinations or allowed LocationId
sets. Those details are added only when an explicit public requirement owns them;
private deployment profiles and compatibility mappings remain outside this
repository.

Explicit deployment configuration may override profile defaults where the
profile contract allows it. It must not bypass compatibility rules owned by the
selected profile.

Console, Remote Shell and API are baseline Timing Point Application capabilities,
not implicitly tied to one profile. Deployment configuration still controls
concrete listener/binding settings and may explicitly leave a network listener
unbound/disabled where appropriate.

Web remains a separate browser-facing capability whose per-TimingNode bindings
are composed when that capability is used.

#### Application identity

`ApplicationId` identifies the configured Timing Point Application instance.
It is a separate identity/type from `TimingNodeId`.

For the current single-TimingNode deployment style, the intended starting
convention is to configure the same string value for `ApplicationId` and the
single `TimingNodeId`. This equality is a deployment convention, not identity
aliasing: multi-TimingNode deployments may use one application id with several
different TimingNode ids.

Representative direction:

```text
applicationId: timing-node-01
```

#### TimingSystems and TimingNodes

The application composes 1..N internal `TimingSystem` contexts. Each
TimingSystem owns 1..N TimingNodes plus its own system-status/upstream-protocol
state. `TimingSystemId` is a local composition/simulation identity and is not
part of the upstream functional addressing contract.

Representative fields:

```text
timingSystems
  timing-system-01
    timingSystemId
    timingDataProvider: reference
    upstreamProtocolProvider: reference
    timingNodes
      timing-node-01
        timingNodeId
        locationId
```

Rules:

- `TimingSystemId` distinguishes hosted/simulated TimingSystem contexts locally;
- each TimingSystem contains 1..N TimingNodes;
- `TimingNodeId` identifies the logical TimingNode and remains application-wide unique in the current configuration baseline;
- `LocationId` identifies the configured physical/event location and is not derived from `TimingNodeId`;
- each configured `LocationId` must satisfy any compatibility constraint of the selected built-in application profile;
- presentation transport settings such as HTTP ports do not belong to the TimingNode;
- the internal TimingSystem grouping does not add a TimingSystem identifier to TimingData or upstream wire messages.

#### I/O

I/O configuration selects concrete external I/O implementations and their
TimingNode mappings.

Representative device configuration direction:

```text
io
  devices
    antennaManager
      antennas
        ANT1
          provider: simulated
          type: rfid
          timingNodes: [timing-node-01, timing-node-02]
        ANT2
          provider: simulated
          type: rfid
          timingNodes: [timing-node-02]

  deviceNetworks
    can
      enabled: true
      protocolProvider: reference

    network
      enabled: true
      displayProtocolProvider: reference
```

`AntennaManager` is the configured owner of the antenna set and may define 0..N antennas. `AntennaId` is distinct from
`TimingNodeId`. One antenna may intentionally map to 1..N TimingNodes; this
fan-out does not merge their state or sequence streams.

The `deviceNetworks.can` section configures the network owned by
`CanNetworkController`; exact bus/driver/discovery fields are added when that
implementation slice exists.

The `deviceNetworks.network` section configures `NetworkDeviceService`, the
bidirectional network-device boundary. Detailed service discovery,
listen/session and protocol-framing settings are added only when IF-09 becomes
concrete. IF-09 remains an IP/network interface and does not require a physical
Wi-Fi router or WLAN. Exact mDNS service naming and network application protocol
remain deferred rather than being invented in IF-11 now.

Concrete antenna configuration owns its driver/protocol/device settings. Its
`provider` value selects a registered `AntennaProvider`; `simulated` is the
built-in provider and therefore requires no external extension JAR. A separate
registration-asset identity is not part of the active software configuration
model.

Provider IDs are implementation-selection keys, not domain/device identities.
The same rule applies to configured TimingData, UpstreamProtocol, CAN-protocol
and display-protocol providers.

For `timingDataProvider`, `reference` selects the built-in implementation of
the canonical IF-05 representation. An alternate/private TimingData provider may
select another external representation/translator, but it still realises the
same IF-05 `TimingDataRecord` semantics; provider selection does not select a
different public record model.

Public examples use generic/reference provider IDs; private provider names and
protocol values remain outside this repository.

#### Upstream messaging

**Upstream** identifies the central/external system relationship from SI-01's
perspective; it does not define the direction of each message. The relationship
is bidirectional.

When upstream messaging is enabled, configuration associates each upstream
gateway/protocol context with exactly one internal `TimingSystem`. That context
may use 1..N connectors. Lower transport resources may later be shared when that
does not blur the semantic system boundary.

Representative direction:

```text
io
  messaging
    upstream
      gateways
        upstream-01
          timingSystem: timing-system-01
          connectors
            connector-01
              type: rabbitmq
              credentials: rabbitmq-main
            connector-02
              type: socket
```

The `timingSystem` reference is local composition information; it is not added
to the upstream protocol merely for routing. `UpstreamGateway` owns the
external transport/session boundary. The associated Domain `UpstreamProtocol`
handles system-level protocol semantics such as ping/synchronisation, while
`UpstreamMessageRouter` resolves TimingNode-targeted messages by
`TimingNodeId` to the corresponding bidirectional `UpstreamMessagePort`.

A connector owns transport resources such as RabbitMQ connections/channels or a
socket session. It does not own Domain/TimingNode selection or message
semantics. The router is upstream-specific and is not used as a generic internal
application message bus.

Storage settings remain under I/O because they configure external persistence.

#### Step-4 TimingData storage

The Step-4 single-TimingNode executable adds the first concrete storage setting:

```yaml
io:
  storage:
    timingData:
      path: data/timing-data.jsonl
```

`io.storage.timingData.path` identifies the authoritative append-only TimingData
file used by the current configured TimingNode. It is deployment/composition
configuration, not TimingNode domain state.

Rules:

- the path is required when the reference TimingData file store is composed;
- the path may be relative to the application working directory or absolute;
- the configured path selects the file location only; IF-05 and the Java
  persistence design own record encoding, append ordering, recovery and
  corruption handling;
- startup recovery opens/validates this file and rebuilds committed LogBook
  state before the TimingNode begins accepting operational work;
- public examples use generic local paths and do not disclose deployment paths;
- this first slice intentionally does not define a generalized per-node storage
  registry or multi-TimingNode file mapping. That topology is added when the
  multi-node runtime slice requires it.

The storage path does not contain a LocationId or RegistrationId policy. Those
identifier domains remain event/profile/reference-data concerns.

#### Presentation

Presentation configuration follows the same function-first ownership as the presentation architecture. Transport configuration is nested under the functional interface that owns it.

Representative direction:

```text
presentation
  web
    endpoints (1 per TimingNode)
      web-timing-node-01
        timingNodeId: timing-node-01
        bindAddress
        port
      ...
  api
    http
    webSocket
  remoteShell
```

The intended Web topology has exactly one configured Web binding for each
configured TimingNode. Each binding references a `TimingNodeId` and owns its
own bind address/port; a multi-TimingNode process therefore exposes 1..N Web
ports. Those listener settings remain Presentation configuration and do not
become fields of the TimingNode domain object.

A TimingNode therefore does not need to know that an HTTP listener, WebSocket, shell or external GUI/test client exists. Presentation interfaces map their requests to the application boundary.

The currently implemented A05-A07 subset is:

```yaml
presentation:
  remoteShell:
    bindAddress: 127.0.0.1
    port: 8023
  api:
    http:
      bindAddress: 127.0.0.1
      port: 8081
    webSocket:
      bindAddress: 127.0.0.1
      port: 8082
```

Remote Shell and API are baseline software capabilities. Their concrete network
bindings are deployment settings rather than profile choices. A deployment may
explicitly omit/disable a listener binding; when an API HTTP/WebSocket binding is
present it requires its `bindAddress` and `port`. The committed development
example uses loopback for all listeners. External GUI/test clients connect to the
API and do not require their own SI-01 presentation configuration section. These
settings configure presentation listeners and do not become TimingNode fields.

#### Logging

Logging is cross-cutting deployment configuration and is not TimingNode/domain state.
The A08 baseline configures a startup level, a retained file sink and an optional
engineering live-diagnostics listener.

Representative direction:

```yaml
logging:
  level: INFO
  file:
    path: logs
    rotateBytes: 1048576
    retainedFiles: 5
  live:
    bindAddress: 127.0.0.1
    port: 8030
```

Rules:

- `level` is the configured global startup level; the implementation accepts the
  semantic levels `TRACE`, `DEBUG`, `INFO`, `WARN` and `ERROR`;
- `file.path` identifies the directory used for retained operational text logs;
  the executable creates it when needed;
- each new runtime log file uses local wall-clock date/time in the filename,
  normally `yyyyMMdd-HHmmss.txt` (for example `20250514-101657.txt`);
- retained log records use `HH:mm:ss.SSS - [LEVEL] - message - [sourceClass.sourceMethod]`
  as the compact first-line format; exception stack traces follow when present;
- `rotateBytes` starts a new timestamped file when the current file reaches the configured size,
  and `retainedFiles` limits the number of timestamped files kept in the configured directory;
  both values must be positive;
- `live` is optional and owns its own bind address/listen port. The development
  example is loopback-only;
- an engineering client initiates the live connection to SI-01 and may query/set
  a temporary runtime log-level override on that diagnostics connection;
- runtime level overrides are process state only: they are not written back into
  IF-11 configuration and restart restores the configured `logging.level`;
- live log delivery is best effort and is not the durable log store;
- this diagnostics listener is separate from Presentation/IF-03 status/events;
  configuring it does not add fields to a TimingNode.

Per-package levels, persistent runtime overrides and general-purpose diagnostics
routing are deliberately outside the A08 baseline.

#### Runtime

Runtime configuration contains process/executor/queue settings that affect application execution but are not domain identity.

Exact fields remain capability-driven and should be added when the corresponding runtime behaviour exists.

#### Security and credentials

Committed configuration may state **which** credential is required, but not contain production secrets.

Example:

```text
rabbitmq
  host: rabbit.example
  port: 5672
  virtualHost: /timing
  username: timing-node
  passwordSecret: RABBITMQ_PASSWORD
```

The referenced secret value is resolved from environment/deployment secret storage at startup. The same principle applies later to HTTP authentication, upstream/backoffice credentials, certificates and similar sensitive values.

This baseline does not require a general `SecretProvider` hierarchy.

### Configuration sources and precedence

The application resolves configuration **from defaults toward explicit deployment
intent**. Explicit deployment values win over built-in default values, but they
do not override built-in profile compatibility constraints.

```text
selected built-in application profile defaults
        ↓
selected platform defaults
        ↓
selected operating-mode defaults
        ↓
explicit deployment application.yml overrides
        ↓
secret resolution
        ↓
effective ApplicationConfig
```

This is deliberately not arbitrary inheritance. The three default sources answer
orthogonal questions:

- **application profile** — what Timing Point topology/capabilities are normally
  composed for the selected deployment family;
- **platform** — the execution/deployment environment, such as Pi Zero or Windows;
- **operating mode** — how concrete adapters are realised, such as normal/real
  operation versus simulation.

A representative source layout may eventually be:

```text
built-in defaults/
  profile/
    <profile-id>.yml
  platform/
    pi-zero.yml
    windows.yml
  mode/
    normal.yml
    simulation.yml

config/
  application.yml       explicit deployment overrides
```

The default source files above are conceptual/versioned application resources;
their exact storage form is an implementation decision. The external IF-11
deployment contract remains independent of a particular YAML merge library.

General recursive inheritance, arbitrary include graphs, profile-to-profile
inheritance and Kubernetes-like overlay machinery are intentionally outside this
baseline.

### Application profile, platform and operating-mode semantics

The three selectors are intentionally independent:

- **application profile** selects topology/capability defaults;
- **platform** selects execution-environment defaults;
- **operating mode** selects how concrete adapters are realised, for example
  normal operation versus simulation.

Simulation changes concrete adapter/provider defaults while preserving the same
application/domain model:

```text
normal:     TimingNode -> configured Antenna provider
simulation: TimingNode -> built-in SimulatedAntenna
```

A profile may provide a topology skeleton/cardinality, capability defaults and
compatibility constraints. Deployment-specific externally meaningful identities
and locations must either be supplied explicitly or follow a separately
specified deterministic public rule; profile resolution must not invent
ambiguous functional identities.

The exact selector syntax and any concrete public profile set are deferred until
a real configuration consumer and its public requirements need them.

### Validation

SI-01 validates the complete effective configuration before normal application composition proceeds.

Validation includes, where applicable:

- missing/invalid `ApplicationId`;
- missing/invalid or duplicate internal `TimingSystemId` values;
- TimingSystems without at least one configured TimingNode;
- duplicate application-wide `TimingNodeId` values;
- a configured TimingNode `LocationId` that violates an explicitly defined compatibility rule of the selected application profile;
- references to unknown TimingSystems or TimingNodes;
- invalid/duplicate `AntennaId` values;
- empty or invalid antenna-routing targets;
- duplicate discovered provider IDs;
- unknown configured TimingData/UpstreamProtocol/Antenna/CAN/display provider IDs;
- provider/configuration combinations rejected by the selected provider;
- invalid CAN device-network settings when CAN is enabled;
- invalid network-device service settings when the network device service is enabled;
- duplicate/conflicting upstream connector identifiers;
- upstream message mappings/targets that reference unknown TimingNodes;
- conflicting presentation/logging listener bind address/port combinations;
- invalid logging level, file rotation/retention values or live-listener settings;
- unsupported adapter/driver types;
- missing required secret references or unresolved required secret values;
- invalid runtime values such as impossible queue/executor settings;
- missing/blank `io.storage.timingData.path` when the reference TimingData file
  store is part of the effective composition.

Configuration loading, configuration validation and application composition are distinct responsibilities even when the initial implementation keeps them small.

### Startup contract

Conceptually startup is:

```text
main()
  -> obtain BuildIdentity from the built artifact
  -> select built-in application profile / platform / operating-mode defaults
  -> apply explicit IF-11 deployment overrides
  -> resolve secrets
  -> produce effective ApplicationConfig
  -> discover built-in and configured external extension providers
  -> validate effective configuration, profile constraints and provider references
  -> configure executable runtime logging
  -> ApplicationBootstrap composes TimingApplication and selected implementations
  -> recover configured TimingData storage into the TimingNode LogBook
  -> start application lifecycle
```

The executable may use a dedicated `ApplicationConfigLoader` once real configuration loading/overlay behaviour exists. A class must not be introduced merely to mirror this document before it owns real behaviour.

Reusable application/runtime behaviour should be shared through composition. IF-11 does not define or require a `BaseApplication` inheritance hierarchy.

### Public/private boundary

Public configuration examples use synthetic identities and endpoints.

Real deployment identities, production topology, credentials, encryption keys, proprietary mappings, private provider names and private protocol values remain outside the public repositories. Public examples use only generic/reference provider IDs and synthetic configuration.

### Implemented configuration slices

Step 3 introduced only the configuration fields needed by the first executable:

- external configuration loading;
- stable application/TimingNode identity;
- first IF-03 presentation bindings;
- logging configuration and startup failure reporting.

Step 4 adds the first concrete storage consumer:

- `io.storage.timingData.path` for the authoritative append-only TimingData
  file used by the current single-TimingNode reference composition;
- storage recovery before operational work is accepted.

Hardware, upstream messaging, security and multi-node storage mapping remain
capability-driven later slices.

### Traceability

| IF-11 concern | SI-01 SSD requirement / architecture |
| --- | --- |
| external effective configuration | SI01-REQ-001 |
| built-in application-profile defaults + explicit deployment overrides | SI01-REQ-001 / configuration-composition architecture |
| configured TimingSystem/TimingNode composition | SI01-REQ-003 |
| presentation listen/binding settings | SI01-REQ-032 + IF-03 |
| TimingData storage path + startup recovery | SI01-REQ-042 + IF-05 / Java persistence design |
| deployment/composition separation | SI-01 SSD configuration/composition architecture |
| Java composition/type growth | SI-01 Java component SDD |


---

## Timing Application Specification Document (SSD)

**Source document:** [41-01-SSD-timing-application-specification-document.md](41-01-SSD-timing-application-specification-document.md)

Status: working/review baseline

Software item: **SI-01 — Timing Point Application**

This document combines the SI-01 requirements and architecture in one baseline.
Requirements keep their `SI01-REQ-...` identifiers. Detailed SDDs build on this
architecture instead of repeating it.

### Inputs

The SI-01 specification consumes the software-system allocation and the interface obligations that apply to SI-01:

- `31-SSSD-software-system-specification-document.md` for SI-01 allocation and software-system constraints;
- `32-03-ISD-application-control-status.md` for IF-03 obligations;
- `32-05-ISD-timingdata-interchange.md` for IF-05 TimingData obligations;
- `32-11-ISD-application-configuration.md` for IF-11 obligations;
- applicable parent/external-system inputs registered by `20-EXT-external-system-inputs.md` when an obligation is allocated directly to SI-01.

`30-UC-system-use-cases.md` provides operational traceability. If SI-01 behaviour later benefits from a separate software-item use-case decomposition, that may be added as an optional software-item use-case document and referenced here; its numbering range will be assigned when such documents are actually introduced, rather than reusing the SSD/SDD ranges.

`03-domain-baseline.md` supplies shared terminology/domain facts. It is supporting source knowledge rather than a substitute for a released requirement/interface baseline.

The **SIP is not an input** to this specification: it chooses when accepted capability is implemented. The **SDE** enables the engineering environment but is not product authority. The **SVP is not an input** either: it defines how accepted requirements and interfaces are verified. Focused SDDs are downstream design refinements of this SSD.

When documents are independently released, each released SSD shall identify the exact revision/version of its SSSD, applicable external inputs and ISD inputs. While this repository releases the local document set together, the repository release/tag/commit is the shared local baseline identifier.

### Document roles

Use this SSD for the **requirements and architecture** of SI-01: what the main
parts are responsible for, how they relate, and which constraints detailed
design must respect.

Implementation detail is split over focused SDDs:

| Document | What belongs there |
| --- | --- |
| `43-01-SDD-01-data-and-display-design.md` | internal data/runtime behaviour: LogBook recording, commit ordering, persistence/recovery algorithms, query isolation, prepare-team/reference/display data |
| `43-01-SDD-02-java-component-design.md` | concrete Java realisation: modules, packages, classes/interfaces, queue/executor/thread choices, provider discovery and dependency enforcement |
| `43-01-SDD-03-backoffice-transport-design.md` | concrete transport realisation below the system/upstream semantic boundary |
| applicable ISD | externally visible interface/file/protocol requirements/semantics; an SDD shall not redefine them |

An SDD may choose the concrete mechanism, as long as it still fits this SSD and
the applicable ISD. Keep class names, queue types, worker threads, file-recovery
steps and package layout out of the SSD unless they change the architecture.

### Software-item requirements

#### Requirement identifier convention

Requirements in this slice use:

```text
SI01-REQ-<number>
```

Identifiers in this review candidate are intended to remain stable. A later capability should add requirements without renumbering these merely for document neatness.

#### First-executable requirements

##### Process lifecycle and configuration

<a id="SI01-REQ-001"></a>

**SI01-REQ-001 — Start from external configuration**

SI-01 shall start using externally supplied configuration rather than requiring production/deployment values to be compiled into application code. The deployment/configuration contract is defined by IF-11.

— — —

- **Type:** Requirement
- **Status:** Review
- **Verified by:** [`VC-ST1-001`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-001)

---


<a id="SI01-REQ-002"></a>

**SI01-REQ-002 — Clean process shutdown**

SI-01 shall support a controlled shutdown path that terminates the first-executable runtime without requiring forced process termination during normal operation/testing.

— — —

- **Type:** Requirement
- **Status:** Review
- **Verified by:** [`VC-ST1-001`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-001)

---


<a id="SI01-REQ-003"></a>

**SI01-REQ-003 — Minimal TimingSystem / TimingNode composition**

The first executable shall support configuration of at least
one internal `TimingSystem` containing at least one
`TimingNode` with a stable `TimingNodeId` that can be
represented in application status.

— — —

- **Type:** Requirement
- **Status:** Review
- **Derived from:** [`UC-001`](30-UC-system-use-cases.md#UC-001), [`UC-014`](30-UC-system-use-cases.md#UC-014)
- **Satisfied by:** [`TimingNode`](41-01-SSD-timing-application-specification-document.md#TimingNode)
- **Verified by:** [`VC-ST1-001`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-001)

---


IF-11 defines the internal TimingSystem/TimingNode configuration hierarchy and how a configured TimingNode is referenced from presentation and I/O configuration while keeping `TimingSystemId` internal and `TimingNodeId`, antenna identity and location identity distinct. Detailed operational RFID behaviour remains outside this first slice.

##### Build and version identity

<a id="SI01-REQ-010"></a>

**SI01-REQ-010 — Single application build identity**

A running SI-01 process shall expose one authoritative application build/version identity derived from the produced application artifact/build.

— — —

- **Type:** Requirement
- **Status:** Review
- **Source for:** [`IF03-REQ-003`](32-03-ISD-application-control-status.md#IF03-REQ-003)
- **Verified by:** [`VC-ST1-001`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-001)

---


<a id="SI01-REQ-011"></a>

**SI01-REQ-011 — Consistent identity across interfaces**

The build/version identity exposed through supported first-executable operator/application interfaces shall represent the same underlying build identity rather than interface-specific copies.

— — —

- **Type:** Requirement
- **Status:** Review
- **Source for:** [`IF03-REQ-003`](32-03-ISD-application-control-status.md#IF03-REQ-003)

---


The public representation and required fields are defined by IF-03.

##### Status

<a id="SI01-REQ-020"></a>

**SI01-REQ-020 — Authoritative current status snapshot**

SI-01 shall maintain an authoritative current application
status model that is separate from log output.

— — —

- **Type:** Requirement
- **Status:** Review
- **Derived from:** [`UC-001`](30-UC-system-use-cases.md#UC-001), [`UC-008`](30-UC-system-use-cases.md#UC-008)
- **Source for:** [`IF03-REQ-004`](32-03-ISD-application-control-status.md#IF03-REQ-004)
- **Satisfied by:** [`TimingNode`](41-01-SSD-timing-application-specification-document.md#TimingNode)
- **Verified by:** [`VC-ST1-001`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-001)

---


<a id="SI01-REQ-021"></a>

**SI01-REQ-021 — Minimum first-executable status content**

The first-executable status shall expose enough information
to determine at least:

- application/build identity;
- application state;
- configured `TimingNode` `TimingNodeId` value(s);
- the current minimal lifecycle state represented for those
  TimingNodes;
- explicit degraded/error information for first-executable
  configuration/startup failures that remain observable
  while the process can continue serving status.

— — —

- **Type:** Requirement
- **Status:** Review
- **Derived from:** [`UC-001`](30-UC-system-use-cases.md#UC-001), [`UC-008`](30-UC-system-use-cases.md#UC-008)
- **Source for:** [`IF03-REQ-004`](32-03-ISD-application-control-status.md#IF03-REQ-004)
- **Satisfied by:** [`TimingNode`](41-01-SSD-timing-application-specification-document.md#TimingNode)
- **Verified by:** [`VC-ST1-001`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-001)

---


The concrete IF-03 contract/schema is defined by `32-03-ISD-application-control-status.md`.

<a id="SI01-REQ-022"></a>

**SI01-REQ-022 — Equivalent status semantics across first interfaces**

Local console, remote-shell and IF-03
application-control/status representations shall be derived
from the same application status semantics. A transport
adapter shall not maintain a separate authoritative status
model.

— — —

- **Type:** Requirement
- **Status:** Review
- **Derived from:** [`UC-008`](30-UC-system-use-cases.md#UC-008)
- **Source for:** [`IF03-REQ-001`](32-03-ISD-application-control-status.md#IF03-REQ-001), [`IF03-REQ-004`](32-03-ISD-application-control-status.md#IF03-REQ-004)
- **Satisfied by:** [`CommandHandler`](41-01-SSD-timing-application-specification-document.md#CommandHandler)

---


<a id="SI01-REQ-023"></a>

**SI01-REQ-023 — Status-change publication**

SI-01 shall publish first-executable status-change information through IF-03 WebSocket/event delivery from the same authoritative status model used for status queries.

— — —

- **Type:** Requirement
- **Status:** Review
- **Source for:** [`IF03-REQ-005`](32-03-ISD-application-control-status.md#IF03-REQ-005), [`IF03-REQ-006`](32-03-ISD-application-control-status.md#IF03-REQ-006)

---


On connection/reconnection the client shall be able to recover a complete authoritative snapshot according to the IF-03 contract.

##### Application boundary and testability

<a id="SI01-REQ-030"></a>

**SI01-REQ-030 — Shared application behaviour**

Transport-specific adapters shall invoke shared SI-01
application commands/queries rather than implementing
independent copies of version/status behaviour.

— — —

- **Type:** Requirement
- **Status:** Review
- **Source for:** [`IF03-REQ-001`](32-03-ISD-application-control-status.md#IF03-REQ-001)
- **Satisfied by:** [`CommandHandler`](41-01-SSD-timing-application-specification-document.md#CommandHandler)

---


<a id="SI01-REQ-031"></a>

**SI01-REQ-031 — Externally testable executable**

The produced SI-01 application shall support ST-1
verification as a separate running process through its
public application interface without direct test mutation of
internal application/domain state.

— — —

- **Type:** Requirement
- **Status:** Review
- **Source for:** [`IF03-REQ-002`](32-03-ISD-application-control-status.md#IF03-REQ-002), [`IF03-REQ-007`](32-03-ISD-application-control-status.md#IF03-REQ-007), [`IF03-REQ-008`](32-03-ISD-application-control-status.md#IF03-REQ-008)
- **Satisfied by:** [`Api`](41-01-SSD-timing-application-specification-document.md#Api), [`CommandHandler`](41-01-SSD-timing-application-specification-document.md#CommandHandler)
- **Verified by:** [`VC-ST1-001`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-001)

---


<a id="SI01-REQ-032"></a>

**SI01-REQ-032 — Safe default network exposure**

The first-executable IF-03 service shall default to local/loopback-only access. Non-loopback listening shall require explicit configuration until a later security/interface baseline defines production exposure and authentication policy.

— — —

- **Type:** Requirement
- **Status:** Review
- **Source for:** [`IF03-REQ-009`](32-03-ISD-application-control-status.md#IF03-REQ-009)

---


<a id="SI01-REQ-033"></a>

**SI01-REQ-033 — Compatible first API evolution**

SI-01 shall implement IF-03 `v1` such that compatible additions can be made without requiring clients to understand every newly added JSON member or event type; breaking interface semantics shall not silently redefine the existing `v1` contract.

— — —

- **Type:** Requirement
- **Status:** Review
- **Source for:** [`IF03-REQ-010`](32-03-ISD-application-control-status.md#IF03-REQ-010)

---


##### Step-4 first-registration operation

<a id="SI01-REQ-040"></a>

**SI01-REQ-040 — Operational location and lifecycle**

SI-01 shall expose the current operational `LocationId` and `OPEN`/`CLOSED`
state, allow the location to be assigned or changed only while CLOSED, require a
valid current location before OPEN succeeds, and keep that location fixed while
OPEN.

— — —

- **Type:** Requirement
- **Status:** Review
- **Derived from:** [`UC-001`](30-UC-system-use-cases.md#UC-001), [`UC-002`](30-UC-system-use-cases.md#UC-002), [`UC-008`](30-UC-system-use-cases.md#UC-008), [`UC-009`](30-UC-system-use-cases.md#UC-009)
- **Source for:** [`IF03-REQ-011`](32-03-ISD-application-control-status.md#IF03-REQ-011)
- **Verified by:** [`VC-ST1-002`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-002)

---


<a id="SI01-REQ-041"></a>

**SI01-REQ-041 — Accepted semantic registration operation**

SI-01 shall provide one application/domain operation for an already-accepted
semantic registration. The caller supplies the resolved `RegistrationId` and
accepted time; SI-01 supplies its own source identity, active `LocationId` and
next committed sequence before committing the TimingData value.

— — —

- **Type:** Requirement
- **Status:** Review
- **Derived from:** [`UC-003`](30-UC-system-use-cases.md#UC-003), [`UC-009`](30-UC-system-use-cases.md#UC-009)
- **Source for:** [`IF03-REQ-013`](32-03-ISD-application-control-status.md#IF03-REQ-013)
- **Verified by:** [`VC-ST1-002`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-002)

---


<a id="SI01-REQ-042"></a>

**SI01-REQ-042 — Committed registration observability**

SI-01 shall make committed registration TimingData observable through current
history and live post-commit notification without exposing uncommitted records
as committed state.

— — —

- **Type:** Requirement
- **Status:** Review
- **Derived from:** [`UC-003`](30-UC-system-use-cases.md#UC-003), [`UC-009`](30-UC-system-use-cases.md#UC-009), [`UC-011`](30-UC-system-use-cases.md#UC-011)
- **Source for:** [`IF03-REQ-014`](32-03-ISD-application-control-status.md#IF03-REQ-014), [`IF03-REQ-015`](32-03-ISD-application-control-status.md#IF03-REQ-015)
- **Verified by:** [`VC-ST1-002`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-002)

---


<a id="SI01-REQ-043"></a>

**SI01-REQ-043 — Capability-gated dev auto-reg**

The dev auto-reg control shall be usable only when
SI-01 advertises that the corresponding engineering capability is both supported
and enabled. This control enters at the accepted semantic registration boundary
and shall not let the client supply final TimingData, source sequence, active
LocationId or source identity.

— — —

- **Type:** Requirement
- **Status:** Review
- **Derived from:** [`UC-009`](30-UC-system-use-cases.md#UC-009)
- **Source for:** [`IF03-REQ-012`](32-03-ISD-application-control-status.md#IF03-REQ-012), [`IF03-REQ-013`](32-03-ISD-application-control-status.md#IF03-REQ-013)
- **Verified by:** [`VC-ST1-002`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-002)

---


<a id="SI01-REQ-044"></a>

**SI01-REQ-044 — Reconnect rebuild before live presentation**

After IF-03 reconnect, an engineering/operator client shall be able to rebuild
current status and committed registration history before treating subsequent
updates as a live view. Duplicate TimingData observed through history plus live
delivery shall be identifiable by Node ID together with sequence number.

— — —

- **Type:** Requirement
- **Status:** Review
- **Derived from:** [`UC-009`](30-UC-system-use-cases.md#UC-009)
- **Source for:** [`IF03-REQ-016`](32-03-ISD-application-control-status.md#IF03-REQ-016)
- **Verified by:** [`VC-ST1-003`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-003)

---


<a id="SI01-REQ-045"></a>

**SI01-REQ-045 — Reference TimingData representation support**

SI-01 shall support the current reference TimingData representation defined by
`33-05-IDD-timingdata-interchange.md` for local persistence and engineering
interchange. For every supported record type, encoding and decoding shall
preserve the applicable IF-05 semantic values.

— — —

- **Type:** Requirement
- **Status:** Draft
- **Derived from:** [`IF05-REQ-001`](32-05-ISD-timingdata-interchange.md#IF05-REQ-001), [`IF05-REQ-002`](32-05-ISD-timingdata-interchange.md#IF05-REQ-002), [`IF05-REQ-003`](32-05-ISD-timingdata-interchange.md#IF05-REQ-003), [`IF05-REQ-004`](32-05-ISD-timingdata-interchange.md#IF05-REQ-004), [`IF05-REQ-005`](32-05-ISD-timingdata-interchange.md#IF05-REQ-005), [`IF05-REQ-006`](32-05-ISD-timingdata-interchange.md#IF05-REQ-006), [`IF05-REQ-007`](32-05-ISD-timingdata-interchange.md#IF05-REQ-007), [`UC-011`](30-UC-system-use-cases.md#UC-011)

---


<a id="SI01-REQ-046"></a>

**SI01-REQ-046 — Write TimingData before commit completion**

SI-01 shall successfully write one complete TimingData record to the configured
local TimingData store before completing that TimingData commit. Only after
that write succeeds may SI-01 add the record to committed LogBook state,
publish a committed live event or report the commit as successful.

If the write fails or remains incomplete, the commit shall fail and the record
shall not be treated as committed.

— — —

- **Type:** Requirement
- **Status:** Draft
- **Derived from:** [`UC-003`](30-UC-system-use-cases.md#UC-003), [`UC-012`](30-UC-system-use-cases.md#UC-012)

---


<a id="SI01-REQ-047"></a>

**SI01-REQ-047 — Restore committed TimingData after restart**

On startup, SI-01 shall rebuild each configured TimingNode's committed TimingData
history from valid complete persisted records in sequence-number order before
accepting new TimingData commit work for that TimingNode. The next sequence
shall be 1 when no committed record exists, otherwise the last committed
sequence plus 1.

Recovery of committed TimingData shall not by itself restore the previous
operational Location ID or OPEN state.

— — —

- **Type:** Requirement
- **Status:** Draft
- **Derived from:** [`IF05-REQ-002`](32-05-ISD-timingdata-interchange.md#IF05-REQ-002), [`IF05-REQ-003`](32-05-ISD-timingdata-interchange.md#IF05-REQ-003), [`IF05-REQ-007`](32-05-ISD-timingdata-interchange.md#IF05-REQ-007), [`UC-013`](30-UC-system-use-cases.md#UC-013)
- **Verified by:** [`VC-ST1-002`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-002)

---


<a id="SI01-REQ-048"></a>

**SI01-REQ-048 — Reject invalid TimingData recovery input**

When recovering the current reference representation, SI-01 shall not treat an
incomplete trailing record as committed. A malformed complete record,
unsupported representation version, Node ID mismatch, duplicate sequence,
sequence gap or sequence regression shall produce an explicit recovery failure
for that TimingNode rather than being silently skipped or renumbered.

— — —

- **Type:** Requirement
- **Status:** Draft
- **Derived from:** [`UC-013`](30-UC-system-use-cases.md#UC-013)

---


#### Step-4 lifecycle interpretation

The Step-4 first-registration slice extends the first executable with the first
real TimingNode operational state while preserving the existing application
lifecycle/status boundary.

Therefore:

- at least one configured TimingNode is represented;
- `LocationId` assignment and OPEN/CLOSE are operational TimingNode state
  transitions; they are not TimingData records in this Step-4 slice;
- a restarted TimingNode begins `CLOSED` with no current operational location;
- a `LocationId` can be assigned or changed while CLOSED;
- OPEN requires a current valid location;
- the current location cannot change while OPEN;
- an accepted semantic registration can commit only while OPEN;
- the first persisted TimingData record may therefore be registration sequence 1,
  provided a LocationId was assigned and the TimingNode was opened first;
- committed registration history and live post-commit updates are observable
  through IF-03;
- physical RFID observation/filtering remains a later input slice.

#### Explicitly deferred requirements

The following areas are intentionally not made concrete by this SSD slice:

- RFID power/read/filter/decryption behaviour before the accepted-registration boundary;
- TagId/TeamId/reference-data resolution and provider-specific identity mapping;
- ready-team/start/penalty behaviour;
- CAN/keypad/Display V1;
- smart Display V2;
- backup/export/retention policy and abrupt-power-loss guarantees beyond the local TimingData append/restart-recovery baseline;
- backoffice semantic/protocol behaviour;
- RabbitMQ-specific behaviour;
- target-image/update/rollback requirements beyond what the later Pi deployment increment needs;
- production authentication/authorisation and final security policy;
- browser-specific CORS/origin policy.

These areas remain in the use-case/working-specification baseline until a later planned increment promotes their requirements.

#### Traceability view

| Requirement | Upstream authority | Interface/design allocation | Planned verification |
| --- | --- | --- | --- |
| SI01-REQ-001/002 | UC-001; SSSD deployment/operability allocation | IF-11 + SI-01 composition/runtime | build/start/stop + ST-1 process control |
| SI01-REQ-003 | UC-001/014; SSSD software-item topology | IF-11 + SI-01 runtime composition | `VC-ST1-001` status inspection |
| SI01-REQ-010/011 | UC-008/009; SSSD IF-03 allocation | IF-01/02/03; shared query boundary | V2/V3 + `VC-ST1-001` |
| SI01-REQ-020/021/022 | UC-001/008/009; SSSD status/control allocation | Status service/model + IF-01/02/03 | V1/V2 + `VC-ST1-001` |
| SI01-REQ-023 | UC-008/009; IF-03 live-event obligation | IF-03 WebSocket/event adapter | V2/V3 + `VC-ST1-001` |
| SI01-REQ-030/031 | UC-008/009/014; SSSD interface/testability separation | shared application boundary | architecture/component checks + `VC-ST1-001` |
| SI01-REQ-032 | IF03-REQ-002/009 | API binding/configuration | configuration/interface verification |
| SI01-REQ-033 | IF03-REQ-010 | interface compatibility/evolution | contract/component verification |
| SI01-REQ-040 | UC-001/002/008/009 | TimingNode + IF-03 control/status | V1/V2 + Step-4 ST-1 |
| SI01-REQ-041/043 | UC-003/009 | TimingNode accepted-registration operation + IF-03 dev auto-reg control | V2 + `VC-ST1-002` |
| SI01-REQ-042/044 | UC-003/009/011 | LogBook/TimingData event + IF-03 bounded LogBook/WebSocket | V2/V3 + `VC-ST1-002` / `VC-ST1-003` |
| SI01-REQ-045 | UC-011 + IF05-REQ-001..007 + 33-05-IDD | reference TimingData codec/persistence boundary | codec/provider tests + persisted-file evidence |
| SI01-REQ-046 | UC-003/012 | local TimingData commit ordering | persistence/registration component tests |
| SI01-REQ-047 | UC-013 + IF05-REQ-002/003/007 | startup TimingData recovery | `VC-ST1-002` second-process run |
| SI01-REQ-048 | UC-013 + 33-05-IDD | reference-store recovery validation | codec/persistence recovery tests |

#### AP-1 decisions resolved by this baseline

The following are now fixed for the first-executable contract:

- build/version identity fields are owned by IF-03: `application`, `version`, `revision`, `sourceRef`, `buildOrigin`, `dirty`, `apiVersion`;
- minimal application status/lifecycle semantics are defined in IF-03 and the lifecycle interpretation above;
- IF-03 HTTP resources are `/api/v1/version` and `/api/v1/status`;
- IF-03 WebSocket endpoint is `/api/v1/events`;
- WebSocket connect/reconnect starts with a complete status snapshot;
- first-executable change events carry complete current status rather than a patch/replay protocol;
- explicit JSON error responses and initial HTTP status mapping are defined in the ISD;
- authentication/authorisation is explicitly deferred for the first executable while default network binding remains loopback-only;
- verification-case identifiers use `VC-<profile>-<number>` for the first baseline;
- no separate remote-shell ISD is required by AP-1 because that adapter reuses shared version/status semantics and is not yet a stable software-to-software contract.

#### Remaining implementation/toolchain choices

The following do **not** block this requirement baseline and belong in the implementation/toolchain increments:

- concrete Java HTTP/WebSocket library;
- concrete remote-shell implementation;
- JSON/configuration/logging libraries;
- Maven/JDK provisioning details;
- concrete code/package classes implementing the shared status model;
- exact mechanism used to cause the first deterministic status transition in `VC-ST1-001`.

A chosen implementation technology must satisfy this SSD and IF-03 rather than redefining them.

### Software-item architecture

#### Architecture drivers

The **Timing Point Application** (SI-01) architecture is driven by these concerns:

- run on the original Raspberry Pi Zero / Zero W target; actual runtime/resource constraints are established by measurement;
- remain usable on Linux/Windows development and test hosts;
- keep timing/domain state in the application;
- support 1..N internal TimingSystems, each with 1..N logical TimingNodes, without state leakage;
- preserve deterministic ordering of state-changing work;
- isolate external I/O concurrency from application/domain state mutation;
- preserve unambiguous time semantics across local time zones, daylight-saving transitions and wall-clock corrections;
- remain testable without production RFID, CAN, upstream/backoffice or proprietary implementations;
- expose one coherent command/query/status/event model to local and network presentation adapters;
- support local persistence/recovery and disconnected operation;
- keep the public reference/core implementation independent of private production source;
- allow selected concrete implementations to be supplied through a small Java-8-compatible provider/extension mechanism without making normal domain/application code plugin-aware;
- avoid reusable-core or extension complexity that is not justified by the application.

#### +1 scenarios used to validate the architecture

The existing use cases in `30-UC-system-use-cases.md` are the scenario source. The SSD should not create a second competing use-case catalogue.

Representative architecture-validation scenarios include:

1. start the **Timing Point Application** (SI-01), load configuration, expose version/status and shut down cleanly;
2. accept an operator command through local or network presentation and route it to the correct logical TimingNode;
3. accept a device observation from an external callback without allowing that callback thread to change application state directly;
4. persist accepted operational state and recover it after restart;
5. continue local operation while a GUI/test client or upstream connection is unavailable;
6. host several independent TimingSystems, each with one or more TimingNodes, in a development/simulation composition without state leakage;
7. substitute public stubs for production devices/transports while exercising the same application/domain paths;
8. capture and process observations correctly when local civil time crosses a daylight-saving transition or the operating-system wall clock is corrected forwards/backwards.

These scenarios are used to check the logical, process, development and deployment views below.

#### Logical view

##### Layered application architecture

The primary logical view is a responsibility/layer view. It describes semantic ownership and dependency direction; it does **not** prescribe one Maven artifact per layer.

<a id="Composition"></a>

**Composition — Composition**

`Composition` is the Runtime component that owns construction of the concrete
running SI-01 object graph from validated effective configuration. It selects
and constructs the required Presentation, I/O, Platform and Infrastructure
objects together with the reusable application/domain objects. Those objects
retain their own layer ownership; Runtime only knows how this executable is
assembled.

— — —

- **Type:** Architecture Element

---


<a id="Application"></a>

**Application — Application**

`Application` is the top-level reusable Runtime object for one running SI-01
composition. It owns the application lifecycle and references the currently
composed application/domain runtime state. It is deliberately shown in a
separate **Runtime** block rather than inside the Application layer: Runtime is
the running container/assembly context, not application/business behaviour.

— — —

- **Type:** Architecture Element

---


`Composition` constructs and starts `Application` from validated configuration and owns the startup/cleanup wiring for the selected concrete endpoints. Normal application/domain interactions do not route through `Composition` after startup. Presentation, I/O, Platform and Infrastructure objects keep their semantic layer ownership even though Runtime composition creates and coordinates them.

The compact software/domain ownership model is intentionally also kept as copyable text:

```text
Application
  +-- ApplicationId
  |
  +-- 1..N TimingSystem
        +-- TimingSystemId        internal composition/simulation identity
        +-- SystemStatus          complete current system overview
        +-- UpstreamMessagePort   system-level upstream messages
        +-- UpstreamProtocol
        |     +-- heartbeat / ping
        |     +-- synchronisation / reconciliation
        +-- TimeSource             absolute time / controllable test offset
        |
        +-- 1..N TimingNode
              +-- TimingNodeId   functional upstream/timing-data identity
              +-- LocationId
              +-- lifecycle / status
              +-- UpstreamMessagePort
              +-- TagProcessor
              +-- StageStartTimes
              +-- LogBook
              |     +-- 0..N TimingData
              +-- NextUpTeams
              +-- RaceData
              +-- StageTiming
              +-- uses / produces TimingData

Shared Domain contract:
  +-- TimingData
```

<a id="fig-si01-01"></a>
![SI-01 layered architecture](../assets/architecture/layered-architecture.svg)
*Figure SI01-01 — SI-01 layered architecture.*

The source for this view is `docs/_diagrams/layered-architecture.yaml`.

In Figure SI01-01, `TimingSystem` and `TimingNode` are shown as UML-style
component/aggregate containers. They are the architecture identities themselves,
not UML class declarations. A small neutral inner property block lists the
important identity/state concepts owned by each aggregate, without its own title,
stereotype or component glyph; it therefore does not prescribe Java fields or a
concrete class shape. Geometric containment plus the `TimingNode (1..N)` label
expresses that one TimingSystem owns 1..N TimingNodes.

The Domain/I/O boundary is deliberately **shaped rather than a rigid horizontal
layer cake**. Domain has extra space below its contained components and yields
through a lower-right polygon cut-away. I/O uses a complementary polygon with a
raised right shoulder around Devices. A small visible gap remains between both
layer outlines, so neither responsibility appears to overlap the other. This
expresses architectural proximity/cohesion only; it does not permit Domain to
depend on concrete I/O.

##### Presentation

Presentation owns client-facing interfaces and their external representations. Its structure is **functional interface first, transport second**:

```text
presentation/
  interfaces/
    console/
    shell/
    web/
    api/        primary API transport/message classes
  common/
    terminal/         behaviour genuinely shared by console + shell
```

<a id="Api"></a>

**Api — API**

The **API** is the general programmable interface of
the **Timing Point Application** (SI-01) for remote
clients, engineering tools and headless
black-box/integration tests. A06/A07 implement only its
first version/status/event slice; later supported control
and diagnostic operations grow inside the same functional
interface.

— — —

- **Type:** Architecture Element
- **Satisfies:** [`IF03-REQ-001`](32-03-ISD-application-control-status.md#IF03-REQ-001), [`IF03-REQ-002`](32-03-ISD-application-control-status.md#IF03-REQ-002), [`IF03-REQ-004`](32-03-ISD-application-control-status.md#IF03-REQ-004), [`SI01-REQ-031`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-031)

---


<a id="Web"></a>

**Web — Web**

**Web** is the browser-facing presentation interface of SI-01. Each configured
`TimingNode` has exactly one Web binding and therefore one configured Web
listener port. The binding targets that TimingNode; its bind address/port remains
Presentation configuration and is not a property of the TimingNode domain
aggregate. A multi-TimingNode process therefore exposes 1..N Web ports. Web may
reuse application queries/events and transport facilities, but it is not
collapsed into the API merely because both can use HTTP/WebSocket
technology.

— — —

- **Type:** Architecture Element

---


<a id="Console"></a>

**Console — Console**

`Console` is the local text presentation interface. It delegates common
terminal parsing/session behaviour to `SharedTerminalHandler` and reaches
application behaviour through the shared `CommandHandler`; it does not own
application/domain state.

— — —

- **Type:** Architecture Element

---


<a id="RemoteShell"></a>

**RemoteShell — RemoteShell**

`RemoteShell` is the remote text presentation interface. It shares terminal
session behaviour with Console through `SharedTerminalHandler` while remaining
a separate external interface and transport concern.

— — —

- **Type:** Architecture Element

---


<a id="SharedTerminalHandler"></a>

**SharedTerminalHandler — SharedTerminalHandler**

`SharedTerminalHandler` owns command parsing and terminal-session behaviour that
is genuinely shared by Console and RemoteShell. It converges those interfaces on
the same `CommandHandler` used by other presentation interfaces.

— — —

- **Type:** Architecture Element

---


`presentation.common` is reserved for behaviour genuinely shared across
presentation interfaces. Terminal behaviour shared by Console and RemoteShell
belongs under `presentation.common.terminal`. API HTTP, WebSocket and
wire-message mapping remain together at the `interfaces.api` component
package root while that implementation is still small; deeper transport/message
subpackages are introduced only when they contain a real cohesive decomposition.

Presentation converts external requests to application calls and application results to client representations. It does not own mutable application/domain state.

##### Application

The application responsibility coordinates use cases:

```text
application/
  Conductor
    lifecycle and application-wide coordination

  CommandHandler
    shared presentation command/query boundary

  UpstreamMessageRouter
    upstream-only application/domain target resolution and routing
```

<a id="Conductor"></a>

**Conductor — Conductor**

`Conductor` coordinates application-wide lifecycle and the 1..N active `TimingSystem` aggregates, including their TimingNodes.

— — —

- **Type:** Architecture Element

---


<a id="CommandHandler"></a>

**CommandHandler — CommandHandler**

`CommandHandler` is the shared entry point for presentation
requests. It may serve simple application reads such as
`version()`. Application-wide operations delegate to
`Conductor` where lifecycle or cross-node coordination is
required. When a presentation command or query targets a TimingNode, `CommandHandler` resolves the owning `TimingSystem` and target `TimingNode`, then calls that node's application/domain operation. The TimingNode owns the crossing of its serial execution boundary; presentation code does not submit directly to its queue or read its mutable state. Operations whose result depends on current TimingNode state return only after that operation has executed on the node's ordered path. `Conductor` is not a mandatory hop for TimingNode-scoped work.

— — —

- **Type:** Architecture Element
- **Satisfies:** [`IF03-REQ-001`](32-03-ISD-application-control-status.md#IF03-REQ-001), [`IF03-REQ-004`](32-03-ISD-application-control-status.md#IF03-REQ-004), [`SI01-REQ-022`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-022), [`SI01-REQ-030`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-030), [`SI01-REQ-031`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-031)

---


Once code is executing for a TimingNode, normal direct Java calls are preferred;
do not introduce messages merely to preserve a layer diagram.

<a id="UpstreamMessageRouter"></a>

**UpstreamMessageRouter — UpstreamMessageRouter**

`UpstreamMessageRouter` owns target resolution for messages exchanged with the
upstream system at application scope. **Upstream** describes that external
system relationship, not the direction of an individual message; the exchange is
bidirectional. The upstream wire contract does not need to expose
`TimingSystemId`. Each configured upstream protocol/gateway context belongs
internally to one `TimingSystem`; node-scoped messages are routed functionally
by `TimingNodeId` to that system's addressed TimingNode. Protocol-level
messages such as ping/heartbeat can be handled by
`TimingSystem`/`UpstreamProtocol` without involving a TimingNode.

The router is deliberately **not** a generic application message bus or mediator
for normal collaboration between domain components.

— — —

- **Type:** Architecture Element

---


##### Domain

The domain owns timing semantics, per-TimingSystem system semantics and
TimingNode state. The main responsibilities are deliberately not represented as
one parent/child tree:

```text
TimingSystem (1..N per Application)
  TimingSystemId              internal only
  SystemStatus                complete current system overview
  UpstreamMessagePort         system-level upstream messages
  UpstreamProtocol
    TimingData transfer
    synchronisation / reconciliation
    ping / pong and other protocol messages
  TimeSource                   absolute time / controllable test offset
  1..N TimingNode
    TimingNodeId              functional protocol/data identity
    LocationId
    State
    UpstreamMessagePort       TimingNode-level upstream messages
    TagProcessor
    StageStartTimes
    LogBook
      0..N TimingData
    NextUpTeams
    RaceData
    StageTiming
    uses / produces TimingData

TimingData
  common semantic contracts
  configured concrete profile
  factory / codec / compatibility
```

`TimingSystem` is the parent logical domain aggregate. One `Application` hosts 1..N TimingSystems; each TimingSystem owns an internal `TimingSystemId`, a complete `SystemStatus` overview, a system-level `UpstreamMessagePort`, one `UpstreamProtocol` context, one `TimeSource` and 1..N TimingNodes. `TimingSystemId` exists to separate local runtime/simulation instances and is not assumed to be visible to the upstream peer. This lets one process simulate or host multiple independent timing systems without changing the functional TimingNode-oriented external contract.

`TimingNode` is the per-location domain aggregate inside one `TimingSystem`. It owns its
identity (`TimingNodeId` and `LocationId`), lifecycle/state and the per-node
components shown inside the TimingNode aggregate in Figure SI01-01.

A TimingNode is also the **active serialization and ownership boundary** for mutable per-node
state. State-dependent commands and consistency-sensitive reads enter one bounded serial
execution path and are processed in order. Code outside that boundary does not directly
read or mutate the node's lifecycle/location state or the mutable contents of its contained
`LogBook`, `NextUpTeams`, `StageStartTimes` and `RaceData` objects. Those objects remain
passive and do not receive their own workers. A short operation on the node lane may publish
an immutable snapshot/read view for longer work outside the lane. The LogBook keeps 0..N
committed immutable `TimingData` values and does not own a second worker or second timing-record
representation.

Both aggregate levels expose a bidirectional semantic `UpstreamMessagePort`.
The two roles share the same semantic concept but have distinct engineering
identities in Figure SI01-01 so interactive selection remains unambiguous.

<a id="SystemUpstreamMessagePort"></a>

**SystemUpstreamMessagePort — TimingSystem UpstreamMessagePort**

The TimingSystem-level `UpstreamMessagePort` receives and emits system-level
operations such as status/heartbeat and synchronisation control that do not
target one TimingNode. It does not own transport connections, connector
lifecycle or cross-aggregate target resolution.

— — —

- **Type:** Architecture Element

---


<a id="TimingNodeUpstreamMessagePort"></a>

**TimingNodeUpstreamMessagePort — TimingNode UpstreamMessagePort**

The TimingNode-level `UpstreamMessagePort` receives and emits node-scoped
operations after `UpstreamMessageRouter` has resolved the owning TimingSystem
and target `TimingNodeId`. It does not own transport connections or
cross-aggregate target resolution.

— — —

- **Type:** Architecture Element

---


<a id="TagProcessor"></a>

**TagProcessor — TagProcessor**

`TagProcessor` owns TimingNode-local processing of decoded tag observations and
the registration semantics needed by the TimingNode. It does not write files
from the antenna callback. State-changing registration work crosses the
TimingNode's bounded serial execution boundary and is completed by that node's
worker.

— — —

- **Type:** Architecture Element

---


<a id="StageStartTimes"></a>

**StageStartTimes — StageStartTimes**

`StageStartTimes` owns the stage-start reference values used by one TimingNode.

— — —

- **Type:** Architecture Element

---


<a id="NextUpTeams"></a>

**NextUpTeams — NextUpTeams**

`NextUpTeams` owns the ordered/expected teams that are next for one TimingNode.

— — —

- **Type:** Architecture Element

---


<a id="RaceData"></a>

**RaceData — RaceData**

`RaceData` owns participant, team and tag reference data needed by one
TimingNode's timing behaviour.

— — —

- **Type:** Architecture Element

---


<a id="StageTiming"></a>

**StageTiming — StageTiming**

`StageTiming` derives running-time and ranking results from the TimingNode's
accepted timing state and reference data.

— — —

- **Type:** Architecture Element

---


`LogBook` is passive state contained by one TimingNode and keeps that node's
committed timing history as 0..N immutable `TimingData` values. Concrete objects
may come from different compatible TimingData profiles; LogBook does not maintain
a second logbook-specific record representation.

`TimingData` is the SI-01/domain capability that realises the system-owned
IF-05 TimingData Interchange contract. IF-05 defines the common semantic
contracts, identity/ordering rules and compatibility obligations. A configured
TimingData profile supplies the concrete immutable TimingData classes plus the
matching factory and codec.

A `TimingDataProvider` supplies that coherent profile family. Its factory is
stateless and constructs concrete TimingData values from explicit construction
values; it does not own TimingNode lifecycle policy, sequence allocation,
persistence or event publication. The same common provider/API boundary is
reusable by SI-01 and engineering tools such as the JavaFX Engineering Client;
normal domain users remain unaware of provider discovery mechanics.

`UpstreamProtocol` is a Domain responsibility owned in the context of one `TimingSystem`. It uses `TimingData` for timing-record transfer and additionally defines semantic messages needed for synchronisation, reconciliation, heartbeat/ping and other upstream-system exchanges. It is therefore broader than the TimingData record format itself. Protocol-level activity that is not about one TimingNode stays here rather than leaking into each TimingNode. A concrete protocol implementation may be selected through an `UpstreamProtocolProvider`; the semantic boundary remains the same whether the implementation is built in or extension-provided.

`TimeSource` is the Domain-owned absolute-time source of one `TimingSystem`.
Production composition may delegate it to the platform wall clock; simulation
and tests can provide a controlled source with an independent offset or stepped
time. This keeps simulated clock behaviour scoped to the TimingSystem rather
than global to the Java process.

Detailed domain semantics belong in `03-domain-baseline.md`.

##### Reusable runtime mechanics

Reusable execution mechanics support the layered architecture but are not a
separate logical layer in Figure SI01-01:

```text
serial execution
lifecycle mechanics
scheduling
asynchronous completion
```

##### I/O

I/O contains adapters that move data between the application and the outside world. Figure SI01-01 shows one logical I/O layer, but the runtime composition is per `TimingSystem`: with 1..N TimingSystems, the corresponding Storage/Devices/Messaging/DeviceNetworks composition is instantiated 1..N times unless a lower-level implementation explicitly multiplexes a shared physical resource.

```text
io/
  Devices
    AntennaManager
      Antenna (0..N)
        SimulatedAntenna
    Display
      Rev1CanDisplay
      Rev2WifiDisplay
    Keypad
      Rev1CanKeypad
    Beeper

  DeviceNetworks
    CanNetworkController
    NetworkDeviceService

  Messaging
    UpstreamGateway
      Connector (1..N)
        RabbitMqConnector
        SocketConnector

  Storage
    file
    db
```

Presentation stays separate because it owns client-facing API/view semantics.
I/O owns the external boundary and its mapping to TimingNodes. In Figure SI01-01
Domain and I/O both use explicit polygon outlines. The I/O outline rises around
Devices, so Devices remains completely inside its owning layer while being drawn
beside the lower Domain area. The normal I/O band and its Storage, Messaging and
DeviceNetworks cards stay compact because they no longer need to inherit the
height required by Devices. The contained Storage, Devices, Messaging and
DeviceNetworks elements carry packaging-component notation where the
package-like ownership/decomposition semantics are meaningful. For compactness,
Figure SI01-01 shows their contained software components as an indented hierarchy
rather than as nested component boxes.

<a id="Storage"></a>

**Storage — Storage**

`Storage` owns generic lower-layer persistence mechanisms plus backup/restore mechanics. Storage contracts are independent of higher Application/Domain types. TimingData-specific encoding, identity/sequence validation and commit semantics remain above Storage; Runtime composition connects that semantic persistence component to the selected generic file/database mechanism.

— — —

- **Type:** Architecture Element

---


<a id="Devices"></a>

**Devices — Devices**

`Devices` groups the software components that represent external device roles in
SI-01. `AntennaManager` owns the configured 0..N `Antenna` components and the
coordination needed when multiple physical antennas form one registration input
path. `SimulatedAntenna` is the built-in reference/simulation implementation.
`Display`, `Keypad` and `Beeper` name software-facing device roles; their
concrete variants remain subordinate to this package/component boundary.

— — —

- **Type:** Architecture Element

---


<a id="DeviceNetworks"></a>

**DeviceNetworks — DeviceNetworks**

`DeviceNetworks` owns communication/network responsibilities used to reach
devices. `CanNetworkController` owns CAN-bus lifecycle, discovery/scanning,
online state and CAN-device communication. `NetworkDeviceService` owns the
bidirectional network-device boundary for smart/network-attached devices.

Service discovery, connection/session handling and protocol framing are
subordinate design concerns of `NetworkDeviceService`, not peer high-level
components. The boundary is not Wi-Fi specific and does not own smart-display
rendering/domain behaviour.

— — —

- **Type:** Architecture Element

---


<a id="Messaging"></a>

**Messaging — Messaging**

`Messaging` owns the external upstream transport/session package. When upstream
messaging is configured it contains one `UpstreamGateway`; the gateway uses
1..N connectors and concrete connectors own transport resources,
delivery/session mechanics and transport-specific addressing.

The semantic `UpstreamProtocol` remains in Domain. Messaging may transport an
encoded protocol representation without interpreting `TimingData` fields or
reimplementing synchronisation rules; after protocol decoding,
`UpstreamMessageRouter` owns application-level target resolution.

— — —

- **Type:** Architecture Element

---


#### Nested I/O component identities

The compact I/O cards in Figure SI01-01 keep their subordinate software
components as structured rows rather than expanding each component into a
separate box. The following rows are nevertheless stable architecture objects
and use the same engineering identity model as top-level diagram nodes.

<a id="AntennaManager"></a>

**AntennaManager — AntennaManager**

`AntennaManager` coordinates the configured 0..N Antenna components that form
one registration input path, including coordination across multiple physical
readers where required by the selected implementation.

— — —

- **Type:** Architecture Element

---


<a id="Antenna"></a>

**Antenna — Antenna**

`Antenna` is the software-facing RFID antenna/reader role consumed by
AntennaManager. Concrete vendor or simulated implementations remain behind this
role.

— — —

- **Type:** Architecture Element

---


<a id="SimulatedAntenna"></a>

**SimulatedAntenna — SimulatedAntenna**

`SimulatedAntenna` is the built-in controllable Antenna implementation used for
development, simulation and hardware-independent verification.

— — —

- **Type:** Architecture Element

---


<a id="VendorAntenna"></a>

**VendorAntenna — VendorAntenna**

`VendorAntenna` is the generic architecture role for an extension-provided
production Antenna implementation beside the built-in simulator. It establishes
that production/vendor implementations use the same Antenna contract and
AntennaProvider extension path; an actual vendor integration may receive a more
specific implementation name when selected.

— — —

- **Type:** Architecture Element

---


<a id="Display"></a>

**Display — Display**

`Display` is the software-facing output-device role for presenting timing
information without coupling Domain/Application behaviour to one physical
display generation or transport.

— — —

- **Type:** Architecture Element

---


<a id="Rev1CanDisplay"></a>

**Rev1CanDisplay — Rev1CanDisplay**

`Rev1CanDisplay` is the CAN-connected revision-1 implementation of the Display
role.

— — —

- **Type:** Architecture Element

---


<a id="Rev2WifiDisplay"></a>

**Rev2WifiDisplay — Rev2WifiDisplay**

`Rev2WifiDisplay` is the network-attached revision-2 implementation of the
Display role.

— — —

- **Type:** Architecture Element

---


<a id="Keypad"></a>

**Keypad — Keypad**

`Keypad` is the software-facing operator-input device role used for keypad
events without making the timing domain depend on a concrete bus implementation.

— — —

- **Type:** Architecture Element

---


<a id="Rev1CanKeypad"></a>

**Rev1CanKeypad — Rev1CanKeypad**

`Rev1CanKeypad` is the CAN-connected revision-1 implementation of the Keypad
role.

— — —

- **Type:** Architecture Element

---


<a id="Beeper"></a>

**Beeper — Beeper**

`Beeper` is the transport-neutral audible-feedback device role. A concrete
connection/implementation is selected only when required by deployment design.

— — —

- **Type:** Architecture Element

---


<a id="CanNetworkController"></a>

**CanNetworkController — CanNetworkController**

`CanNetworkController` owns CAN-bus lifecycle, discovery/scanning, online state
and CAN-device communication for the DeviceNetworks package.

— — —

- **Type:** Architecture Element

---


<a id="NetworkDeviceService"></a>

**NetworkDeviceService — NetworkDeviceService**

`NetworkDeviceService` owns the bidirectional boundary for
network-attached/smart devices, including data sent outward and device-originated
messages/events received inward.

— — —

- **Type:** Architecture Element

---


<a id="UpstreamGateway"></a>

**UpstreamGateway — UpstreamGateway**

`UpstreamGateway` is the Messaging-owned external upstream transport/session
boundary. It owns connector coordination but not UpstreamProtocol semantics.

— — —

- **Type:** Architecture Element

---


<a id="Connector"></a>

**Connector — Connector**

`Connector` is the transport/session role used 1..N times by UpstreamGateway.
Concrete connectors own transport resources, delivery/session mechanics and
transport-specific addressing.

— — —

- **Type:** Architecture Element

---


<a id="RabbitMqConnector"></a>

**RabbitMqConnector — RabbitMqConnector**

`RabbitMqConnector` is the RabbitMQ implementation of the Connector role for
production-shaped upstream messaging.

— — —

- **Type:** Architecture Element

---


<a id="DebugConnector"></a>

**DebugConnector — DebugConnector**

`DebugConnector` is the development/debug implementation of the Connector role.
It provides a production-semantics-preserving upstream transport path that an
independent engineering desktop/debug tool can use without becoming part of
SI-01 or bypassing UpstreamGateway/UpstreamProtocol. The concrete debug transport
and desktop-tool interaction are refined by downstream design rather than by
Figure SI01-01.

— — —

- **Type:** Architecture Element

---


##### Platform

Platform is the small technical foundation below the application, domain and I/O
responsibilities. It contains JDK-only reusable primitives and low-level
execution-environment abstractions:

```text
bounded serial execution (SerialWorker)
local typed events (Event<T>)
clock / time source
filesystem / path primitives
executors / threads
process / runtime information
network / OS primitives
```

A domain or I/O component may compose a Platform primitive such as
`SerialWorker` or `Event<T>`; the primitive itself remains unaware of
TimingNode, TimingData, presentation or external I/O semantics.

The layered view groups Platform into three small technical responsibilities:

<a id="PlatformExecution"></a>

**PlatformExecution — PlatformExecution**

`PlatformExecution` owns reusable execution primitives such as bounded serial
execution and the low-level executor/thread abstractions behind them. It does not
own TimingNode state or domain policy.

— — —

- **Type:** Architecture Element

---


<a id="PlatformEvents"></a>

**PlatformEvents — PlatformEvents**

`PlatformEvents` supplies the small typed local-event mechanism used for
post-fact notifications. Event instances remain owned by the component that
publishes them; Platform does not provide a central event bus.

— — —

- **Type:** Architecture Element

---


<a id="PlatformEnvironment"></a>

**PlatformEnvironment — PlatformEnvironment**

`PlatformEnvironment` groups low-level clock/time, filesystem/path,
process/runtime and network/OS abstractions. Concrete class and threading
behaviour belongs to SDD-02.

— — —

- **Type:** Architecture Element

---


##### Runtime and infrastructure

The right-hand side of the layered view separates two technical responsibilities:

- **Runtime** — the running `Application`, concrete `Composition` and lifecycle coordination;
- **Infrastructure / cross-cutting** — supporting technical facilities such as logging, diagnostics, build identity, configuration mapping and extension discovery.

##### Cross-cutting concerns

Cross-cutting technical concerns include logging, diagnostics, metrics and
build/version identity. In Java, `infra` is reserved for concrete cross-cutting
support such as `BuildIdentity`; it is not the I/O layer.

<a id="Logging"></a>

**Logging — Logging**

`Logging` is reusable runtime logging infrastructure owned by the core artifact. Reusable
application-core/domain code emits records through SLF4J; the default executable selects
`slf4j-jdk14 -> java.util.logging` and starts the core-provided logging composition.
Logging owns backend/sink lifecycle and the current global logging level; it does not own
application or domain state.

— — —

- **Type:** Architecture Element

---


<a id="LoggingServer"></a>

**LoggingServer — LoggingServer**

`LoggingServer` is the optional external engineering interface for live log records and
temporary global-level control. The engineering client initiates the connection. This
logging-specific TCP boundary is separate from the IF-03 API/status/event
interface and live delivery remains best effort.

— — —

- **Type:** Architecture Element

---


`Composition` belongs to Runtime because it contains concrete knowledge of the running application graph. Infrastructure remains supporting/cross-cutting: the default YAML loader maps deployment input to effective runtime configuration, logging and diagnostics provide technical services, and extension discovery supplies selected implementations. The executable supplies the configuration path rather than owning the parser. `LoggingServer` depends on the narrow `Logging` surface for level control/common formatting; `Logging` does not depend on or own `LoggingServer`.

#### Principal runtime abstractions

<a id="TimingSystem"></a>

**TimingSystem — TimingSystem**

A `TimingSystem` is an internal parent domain aggregate.
One **Timing Point Application** (SI-01) may host 1..N
TimingSystems, for example to run multiple independent
simulation contexts. Each TimingSystem owns a complete
`SystemStatus` overview, a system-level
`UpstreamMessagePort`, one `UpstreamProtocol` context, one
`TimeSource` and 1..N TimingNodes. Its internal `TimingSystemId` is not
assumed to be part of the upstream wire contract.

— — —

- **Type:** Architecture Element

---


<a id="SystemStatus"></a>

**SystemStatus — SystemStatus**

`SystemStatus` is a dedicated Domain component contained by one
`TimingSystem`. It owns the complete current operational overview of that
system, including TimingNode state plus semantic device, device-network,
storage, upstream-connectivity and synchronisation status. Concrete adapter
objects remain outside Domain and contribute status through typed semantic
inputs.

— — —

- **Type:** Architecture Element

---


<a id="TimingNode"></a>

**TimingNode — TimingNode**

A `TimingNode` is the independently addressed
operational/domain aggregate at one timing location. It
belongs to exactly one `TimingSystem` and is the active
serialization boundary for that node's mutable state.
Its contained state objects are passive; the upstream and
TimingData contracts remain centred on `TimingNodeId`.

— — —

- **Type:** Architecture Element
- **Satisfies:** [`SI01-REQ-003`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-003), [`SI01-REQ-020`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-020), [`SI01-REQ-021`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-021)

---



<a id="LogBook"></a>

**LogBook — LogBook**

A `LogBook` is passive state contained by one TimingNode.
It holds that node's committed immutable `TimingData` values.
The current design does not introduce a second
logbook-specific timing-record representation.

— — —

- **Type:** Architecture Element

---


<a id="TimingData"></a>

**TimingData — TimingData**

`TimingData` is the shared Domain capability that realises
system-owned IF-05 inside SI-01. It exposes the typed
common `TimingData` semantic interfaces plus configured factory/codec services needed
by application code. Canonical record/file semantics and
compatibility remain defined by IF-05; Storage, Web and upstream
protocol code consume that contract without redefining it.

— — —

- **Type:** Architecture Element

---


<a id="UpstreamProtocol"></a>

**UpstreamProtocol — UpstreamProtocol**

Each TimingSystem owns one `UpstreamProtocol` context. It uses
TimingData for timing-record transfer and owns protocol-level
synchronisation, reconciliation and ping/heartbeat semantics so
those concerns do not leak into individual TimingNodes.

— — —

- **Type:** Architecture Element

---



<a id="TimeSource"></a>

**TimeSource — TimeSource**

`TimeSource` is owned by one `TimingSystem` and provides the absolute current
time used by that system's timing semantics. Production composition can delegate
to the platform wall clock; simulation/test composition can use a controlled
source with an independently programmable offset or stepped time. Multiple
TimingSystems in one process therefore do not have to share the same simulated
wall-clock view.

— — —

- **Type:** Architecture Element

---


The architecture deliberately uses **separate views** for software/domain decomposition, hardware/deployment topology and configuration/identity mapping. These views must not be collapsed into one ownership tree.

##### Software/domain decomposition

```text
Application
  +-- ApplicationId
  |
  +-- 1..N TimingSystem
        +-- TimingSystemId        internal composition/simulation identity
        +-- SystemStatus          complete current system overview
        +-- UpstreamMessagePort   system-level upstream messages
        +-- UpstreamProtocol
        |     +-- heartbeat / ping
        |     +-- synchronisation / reconciliation
        +-- TimeSource             absolute time / controllable test offset
        |
        +-- 1..N TimingNode
              +-- TimingNodeId   functional upstream/timing-data identity
              +-- LocationId
              +-- lifecycle / status
              +-- UpstreamMessagePort
              +-- TagProcessor
              +-- StageStartTimes
              +-- LogBook
              |     +-- 0..N TimingData
              +-- NextUpTeams
              +-- RaceData
              +-- StageTiming
              +-- uses / produces TimingData

Shared Domain contract:
  +-- TimingData
```

`ApplicationId` identifies the running Timing Point Application instance. `TimingSystemId` is an internal identity used only to distinguish 1..N hosted TimingSystem contexts. `TimingNodeId` remains the functional identity used by TimingData and upstream node addressing and scopes the node's registration sequence and synchronisation semantics. `LocationId` is the separately configured physical event location. The upstream contract therefore does not gain a TimingSystem identifier merely because one process can host multiple systems.

<a id="fig-si01-02"></a>
![SI-01 software/domain decomposition](../assets/architecture/timing-node-software-decomposition.svg)
*Figure SI01-02 — SI-01 software/domain decomposition.*

The exact Java class/package boundaries may evolve as implementation evidence appears, but the `TimingNode` aggregate is the semantic owner of the operational TimingNode state. The physical registration asset is not a child component of this software tree.

##### Devices and device-network topology

The high-level I/O model separates device concepts from the communication
responsibilities that serve them:

```text
Devices
  +-- Antenna (0..N)
  +-- Rev1CanDisplay
  +-- Keypad
  +-- Beeper
  +-- Rev2WifiDisplay

Device Networks
  +-- CanNetworkController
  +-- NetworkDeviceService
```

An `Antenna` remains an I/O source with its own `AntennaId` and concrete
driver/connection settings. Grouping it under Devices does not change its
TimingNode routing semantics: one antenna may intentionally feed one or more
TimingNodes.

`CanNetworkController` represents the actively managed CAN network rather than
one particular CAN device. `NetworkDeviceService` represents the general
bidirectional service boundary for network-attached devices. It may support
outbound SI-01 data and inbound device requests/events without requiring the
device/domain object itself to know about sockets, discovery or transport
sessions.

The current smart-display direction remains client initiated: SI-01 makes its
service discoverable and Rev2WifiDisplay connects to it. The exact discovery,
listener/session and packet-framing design belongs below this high-level view.

##### Configuration, routing and identity mapping

Configuration connects identities without collapsing them:

```text
Application
    +-- ApplicationId

Devices
    +-- Antenna (0..N)
    |     +-- each Antenna -> 1..N TimingNodeId
    +-- Rev1CanDisplay
    +-- Keypad
    +-- Beeper
    +-- Rev2WifiDisplay

Device Networks
    +-- CanNetworkController
    +-- NetworkDeviceService

Messaging
    +-- UpstreamGateway
          +-- Connector (1..N)
                +-- RabbitMqConnector
                +-- DebugConnector

UpstreamMessageRouter
    +-- system-level message -> TimingSystem.UpstreamMessagePort
    +-- TimingNodeId -> TimingNode.UpstreamMessagePort
    +-- TimingSystemId remains internal composition context
```

<a id="fig-si01-03"></a>
![TimingNode, hardware and upstream-system messaging routing](../assets/architecture/timing-node-routing-mapping.svg)
*Figure SI01-03 — TimingNode, hardware and upstream-system messaging routing.*

`TimingNodeId` is the stable identity of a `TimingNode` and scopes its sequence, persistence and synchronisation semantics. `LocationId` and `AntennaId` are separate namespaces.

Configured antenna mappings associate each `AntennaId` with one or more TimingNodes. Fan-out is explicit: if one antenna feeds two TimingNodes, each target TimingNode processes the observation through its own serialized state boundary and keeps its own TimingNodeId-scoped sequence/state while the original `AntennaId` remains available as context.

CAN and smart-network controllers are not alternate presentation layers. They are
I/O/device-network responsibilities. A keypad, beeper or display may interact with or present information
to a human, but it is still an external device from SI-01's architecture
perspective.

`UpstreamGateway` is the I/O upstream-messaging boundary. It exchanges transport-neutral messages with its configured connectors but does not own protocol semantics. Each configured gateway/protocol context is associated internally with one `TimingSystem`. `UpstreamMessageRouter` routes system-level semantic operations to `TimingSystem.UpstreamMessagePort` and resolves TimingNode-targeted operations by `TimingNodeId` to `TimingNode.UpstreamMessagePort`; `UpstreamProtocol` owns protocol semantics such as ping, status exchange and synchronisation. No external `TimingSystemId` field is required.

Connectors do not route directly to Domain or TimingNodes and do not own domain
semantics. A connector-specific external name or routing key may participate in
boundary mapping, but it does not replace the stable functional `TimingNodeId`.
Internal `TimingSystemId` is local composition context rather than a new
upstream routing identity. One gateway may use multiple connectors and one
TimingNode may exchange messages through more than one connector via the gateway,
router and its bidirectional port. `RabbitMqConnector` represents the
production-shaped transport; `DebugConnector` provides an engineering/debug
transport to an external desktop/debug tool while preserving the same gateway
and protocol boundary.

`ApplicationId` remains a runtime/application identity and is not assumed to be an upstream protocol address. Protocol-level exchanges are scoped by the configured TimingSystem/gateway context; TimingNode-specific exchanges remain addressed by `TimingNodeId`.

Runtime-wide infrastructure may be shared where that does not leak mutable TimingNode state. Candidates include backing executors, logging infrastructure, HTTP server infrastructure, shared connector infrastructure, configuration loading and network monitoring.

Stable domain facts behind these views are maintained in `03-domain-baseline.md`; this SSD owns their software-architecture composition and execution implications.

#### Command, query and event model

All presentation transports should converge on one shared application model. The first Java implementation proves this with a deliberately small `CommandHandler.version()` query rather than a generic messaging framework; future request methods should be added only when a real client use case requires them.

```text
local console ----------------+
remote shell -----------------+
API HTTP/JSON ---------+--> typed command/query boundary --> application runtime
API WebSocket <---------+<--------------------------------------------+
future Web interface ----------+
```

Working rules:

- commands request state changes;
- a state-dependent command may wait for the domain result produced when that command reaches the TimingNode's ordered execution path;
- submission-only ingress is explicit: acceptance means only that bounded work was accepted for later processing;
- queries do not become alternate owners of state; consistency-sensitive reads run on the TimingNode's ordered path or use an immutable snapshot published from that path;
- events report facts/results that have occurred;
- queue admission, domain result and caller wait timeout are different outcomes and shall not be represented as though they mean the same thing;
- a caller timeout does not prove rejection or rollback of already accepted work; until state is queried or another result is observed, the final outcome is unknown to that caller;
- external protocol DTOs are mapped at the presentation/I/O boundary rather than used as the internal domain model;
- messages crossing thread/process boundaries should be immutable where practical;
- post-fact notifications may use a small typed `Event<T>` abstraction with explicit `subscribe` / `unsubscribe` / `emit`; commands and queries are not routed through that mechanism.

The event mechanism is deliberately local and simple. The generic `Event<T>`
mechanism is a small reusable Platform primitive; a producing component owns a concrete
event such as `newTimingDataEvent : Event<TimingData>` and interested listeners
subscribe directly to that event. There are no string topics, central event
dispatcher or global static bus. Emitting an event reports that a fact has
already occurred; it does not transfer ownership of TimingNode state.

#### Process view: ordering and concurrency

SI-01 receives work from several places at once: operator interfaces, devices,
timers and upstream connections. State changes for one `TimingNode` still have
to happen in a clear order.

Architecture rules:

- callbacks do not change TimingNode state directly;
- resolve the target TimingNode before state-dependent work enters its ordered path;
- code outside a TimingNode does not directly inspect or mutate that node's mutable state;
- two state changes for the same TimingNode do not run over each other;
- the TimingNode behaves as an active object: one bounded serial execution
  boundary owns state-dependent command ordering and consistency-sensitive reads;
- state-dependent validation is performed when the operation executes against the current ordered state, not from a stale pre-queue read;
- the contained LogBook, NextUpTeams, StageStartTimes and RaceData objects remain
  passive and do not each receive their own execution thread;
- short read operations may capture immutable snapshots for longer calculations outside the TimingNode lane;
- different TimingNodes may make progress at the same time;
- file writes must not hold up RFID/device/operator callbacks;
- a slow query or ranking calculation must not hold up LogBook commits;
- a slow network connection must not hold up a local commit;
- queues/resources are bounded and overload is visible instead of silently dropping work;
- during shutdown, stop new input first and give accepted work time to finish.

The primary latency risk is therefore **producer backpressure**, not whether every TimingNode operation is asynchronous. Device/RFID/TagProcessor ingress must use the submission-only path and return after bounded-queue admission; it does not wait for persistence or a domain result. Presentation/application callers may use a result-bearing command path when they need that result.

Short consistency-sensitive queries are allowed to occupy the TimingNode lane for a bounded period. The design does not require a copied snapshot as the default read mechanism. Read/query implementations may traverse contained state directly on the ordered lane, use a compact derived/indexed representation, or copy data only when measurement shows that the copy is the better trade-off. Longer ranking/formatting work must still avoid becoming a second writer or unboundedly holding up timing commits. Synchronous persistence may also occupy the lane initially, but its impact is controlled through bounded queues and observable queue/store latency.

Post-commit listeners are subject to the same rule: network/backpressure work must not execute synchronously on the TimingNode lane unless the adapter is proven to enqueue/buffer and return promptly.

The SSD only sets these rules. SDD-01 describes state ordering, persistence and
consumer visibility. SDD-02 chooses the Java queue/worker implementation. The
current direction is the Active Object pattern implemented by composition, not a
mandatory `TimingNode extends ActiveObject` class hierarchy.

External ingress still keeps its functional routing responsibilities:

- `CommandHandler` routes presentation commands/queries;
- configured device/antenna mappings resolve device observations to TimingNodes;
- `UpstreamMessageRouter` resolves system-level versus TimingNode-targeted
  upstream messages;
- scheduled work retains its owning target.

There is no central dispatcher through which commands and queries must pass. Components may expose local typed events such as `newTimingDataEvent` for post-fact notification; those events are not the owner or execution path for TimingNode state.

<a id="fig-si01-04"></a>
![SI-01 runtime dispatch process](../assets/architecture/runtime-dispatch-process.svg)
*Figure SI01-04 — Concurrent ingress resolves to ordered TimingNode state-change boundaries; concrete execution mechanics belong to detailed design.*

The source for this process view is
`docs/_diagrams/runtime-dispatch-process.yaml`.

#### Time and clock architecture

Time is an explicit architecture concern rather than an incidental use of `Date`, `Calendar`, `LocalDateTime`, Java/SQL timestamp classes or raw millisecond values throughout the codebase.

##### `TimingTimestamp` value

The **Timing Point Application** (SI-01) uses one dedicated immutable application/domain class named `TimingTimestamp` for externally meaningful **absolute event times** such as observations, accepted registrations and persisted/synchronised event timestamps. A race/stage start definition is not required to be an absolute timestamp: it may be supplied as local time-of-day without a date, or with an explicit date when that information is available.

Working semantics:

- `TimingTimestamp` represents an absolute point on a UTC-based time line;
- it does not contain an implicit local time zone or daylight-saving state;
- conversion to/from local civil time happens at explicit presentation/configuration/integration boundaries;
- its precision and external serialisation are explicit rather than inherited accidentally from a Java API or wire codec;
- domain/application APIs pass `TimingTimestamp` rather than arbitrary `long`, `Date`, generic Java timestamp classes or local-date/time values where an absolute event time is intended.

The dedicated class may internally delegate to a suitable Java primitive such as `Instant`, but its public semantic contract remains project-owned. Protocol-specific formatting/parsing and deployment-specific zone conversion belong in boundary adapters/codecs rather than in `TimingTimestamp` itself. Time-only race/start definitions are a separate domain/reference-data concept and shall not be forced into `TimingTimestamp` by inventing a date.

When a race/stage start is defined only by local time-of-day, elapsed-time calculation shall resolve that clock time against the accepted registration timestamp using the configured event/race time zone. The resolved start is the most recent valid occurrence of that time-of-day that is not after the registration. This deliberately supports one civil-day rollover: a start at `23:59:50` followed by a registration at `00:00:10` resolves to an elapsed time of 20 seconds rather than a negative value. If an explicit start date is supplied, that date is authoritative. A time-only definition cannot by itself distinguish elapsed durations of 24 hours or more; such cases require an explicit date or another higher-level race-day reference.

##### Time sources

Code that needs the current absolute time receives it through the Domain-level `TimeSource` owned by the relevant `TimingSystem`. Production composition can delegate that source to the operating-system wall clock; deterministic tests can supply a controlled source that can be advanced, stepped or given a per-system offset explicitly. This allows multiple TimingSystems hosted by one process to run against different simulated absolute times without changing TimingNode logic.

Elapsed durations, retry intervals, filtering windows, scheduling delays and timeout measurements should use a **monotonic time source** where their semantics are duration-based. On Java 8 this can be backed by `System.nanoTime()` behind a small platform abstraction. A monotonic mark is process-local and is not a persisted event timestamp.

The distinction is therefore:

```text
TimingTimestamp / wall-clock source
  absolute event time
  persistence / synchronisation / external semantics

monotonic time source
  elapsed duration
  timeout / retry / filtering windows
  process-local only

TimingNodeId + SequenceNumber
  stable stream ordering / gap detection
```

A source sequence is not derived from a timestamp. Two registrations may have equal timestamps, and a wall-clock correction may even make a later observation carry an earlier absolute timestamp; source ordering must remain recoverable from source sequence semantics.

##### Architecture risk — wall-clock discontinuity and local-time ambiguity

This is an explicit architecture risk because timing software can produce plausible but incorrect results when local civil time and elapsed time are conflated.

| Risk | Possible consequence | Architectural mitigation / open work |
| --- | --- | --- |
| daylight-saving transition repeats or skips local civil times | ambiguous/non-existent local timestamps and wrong ordering if local time is persisted directly | persist/use absolute `TimingTimestamp` for events; resolve time-only race/start definitions through an explicit event-zone rule and require more context where a local time is ambiguous/non-existent; add DST transition tests |
| NTP, manual correction or platform synchronisation steps wall clock backwards/forwards | negative/large elapsed differences; a later observation can have an earlier wall-clock timestamp | use monotonic time for durations; source sequence for ordering; expose/inject wall clock; define correction/health policy |
| clock offset/drift differs between the application and external systems | incorrect elapsed/race-time calculations or reconciliation disagreement | define clock synchronisation/offset acceptance requirements and verification before timing accuracy is accepted |
| restart loses monotonic origin | process-local duration marks cannot be compared across restart | never persist monotonic marks as event timestamps; restore from absolute `TimingTimestamp` plus domain/source state |

Daylight-saving time by itself does **not** change UTC/absolute time; the ambiguity appears when a local civil time is treated as if it were an absolute timestamp. Conversely, using an absolute `TimingTimestamp` does not make the operating-system clock monotonic: a wall-clock correction can still cause newly captured absolute timestamps to move backwards.

Before physical timing behaviour is accepted, the project must decide how an active timing system reacts to a material clock correction: whether it is merely diagnosed, blocks/marks the system degraded, records an audit event, or uses an explicit correction/offset mechanism. That policy needs requirements and verification evidence rather than being hidden inside the `TimingTimestamp` class.

#### Internal messaging direction

Internal messaging exists at asynchronous/ownership boundaries; it is **not** a requirement to turn ordinary in-lane Java calls into messages.

Working semantic categories are:

```text
state-dependent command
  request a state change
  caller may wait for the processed domain result

submission-only input
  request bounded admission for later processing
  admission is not the later domain result

consistency-sensitive query
  capture/read current TimingNode state on the ordered path

event
  report an observation, fact, completion or failure that has occurred
```

These are interaction semantics, not a requirement for public `Command` or `Query`
classes. The caller-facing TimingNode API may remain ordinary synchronous methods.
A Future/Promise is a suitable internal Active Object mechanism for connecting a
queued operation to a caller that waits for its result; that mechanism need not
appear in the public application/domain API.

Rules:

- use typed internal work only where work crosses an asynchronous or TimingNode execution boundary;
- resolve command/query targets explicitly; do not route commands or mutable-state access through events; local typed events are only for post-fact notification;
- once running in a TimingNode's serial execution lane, use normal direct Java calls;
- do not call a blocking public TimingNode operation recursively from that same lane;
- submit asynchronous I/O completion back to the owning TimingNode before changing its state;
- RabbitMQ is external I/O, not an in-process message bus.

SDD-01 illustrates the interaction cases. SDD-02 owns the concrete Java Future,
queue, timeout and worker mechanics.

#### Status and diagnostics architecture

Status is a first-class current-state model and is distinct from logging.

Status should allow presentation and diagnostics to observe application, timing-system and subsystem health without parsing log text. Representative areas include:

- application version / uptime / overall health;
- TimingNode lifecycle;
- registration asset/source state;
- TimingNode queue depth/high-water/overload health;
- RFID power/startup/protocol/heartbeat;
- CAN/device availability;
- persistence/backup state;
- race-data freshness;
- local clock/time-source health where relevant to timing validity;
- network/upstream connectivity;
- inbound/outbound synchronisation state.

Each `TimingSystem` contains its own dedicated Domain `SystemStatus` component. This is a complete current-state
overview of that TimingSystem, not an `OK`/error flag. It aggregates the
TimingSystem lifecycle and protocol state, its 1..N TimingNode statuses and the
semantic status of composed I/O relevant to operation: for example antenna
availability, whether a display is connected, keypad/beeper availability,
device-network health, storage availability, upstream connectivity and
synchronisation state. Domain owns the meaning of this overview; concrete CAN,
socket, vendor-device and persistence implementations remain in I/O and report
semantic status without leaking adapter classes into Domain.

`SystemStatus` does not bypass TimingNode ownership to inspect node internals.
A TimingNode supplies a semantic immutable status/result from its own ordered
state boundary; SystemStatus may retain/aggregate that representation together
with system/I/O health. An application-wide status response may therefore use
published node-status snapshots, or obtain a consistency-sensitive node status
through the normal TimingNode query operation when that stronger ordering is
required.

An application-facing status view may aggregate the 1..N TimingSystem statuses
and application/runtime problems into one response; that aggregation does not
move SystemStatus ownership back to the Application.

Status returned to a client is read-only from that client's point of view. The transport response does not define the internal Java class structure used to produce it.

Logging records diagnostic/history information; status represents current operational state. One must not be used as a substitute for the other.

#### Logging architecture

Logging is a SSD architecture-level cross-cutting technology decision because it affects almost every
component, operational diagnostics, footprint and engineering support.

The A08 baseline keeps application-core logging calls independent from the concrete runtime backend:

```text
application core / domain code
        |
        v
      SLF4J API
        |
        v
application-core infrastructure: Logging
        |
        +-- initial provider: slf4j-jdk14
                         |
                         v
                  java.util.logging
                     |
                     +-- ConsoleHandler
                     +-- TimestampedFileLogHandler
                     +-- LiveLogHandler
                              |
                              v
                       LoggingServer
                              ^
                              |
                    engineering client connects
```

Working decisions:

- reusable application-core code logs through the SLF4J API;
- `timing-point-core.jar` depends on `slf4j-api` only and must not impose a provider/backend on consumers;
- the executable composition selects exactly one provider;
- the initial Java-8/Pi-Zero application composition uses `slf4j-jdk14`, delegating SLF4J records to the JDK `java.util.logging` backend configured by the core-provided `Logging` infrastructure;
- `timing-point-core.jar` provides reusable `io.github.brainboxemb.eventtiming.timingpoint.infra.logging.Logging` and separate `io.github.brainboxemb.eventtiming.timingpoint.infra.loggingserver.LoggingServer` infrastructure; both use JDK JUL facilities and introduce no external backend dependency because JUL is part of the Java runtime;
- the startup configuration defines one global semantic log level; the A08 baseline uses the normal `TRACE / DEBUG / INFO / WARN / ERROR` vocabulary and maps it to the selected backend;
- `LoggingControl` owns the current global level and may apply a **temporary runtime override**. A runtime override is intentionally not written back to `application.yml` and resets to the configured level on restart;
- the durable operational sink is a human-readable rotating `TimestampedFileLogHandler` with configured size limit and retained generations; its wall-clock filename is for operator readability, not uniqueness, so stale/repeated Raspberry Pi startup time must never overwrite an existing log or cause retention to prune the active file;
- console logging remains available for local startup/development feedback;
- an optional `LoggingServer` is independently composed beside `Logging`, attaches its own live handler, accepts a connection initiated by the JavaFX engineering client and streams new log records through a dedicated diagnostics channel;
- the same diagnostics connection may query/change the temporary runtime log level; this control remains logging-specific rather than becoming a generic application command bus;
- live delivery is best effort: a missing, slow or disconnected engineering client must not block TimingNode/application execution, and live records need not be retained for later replay;
- the file sink is the retained source for historical operational logs; A08 does not add an in-memory log-history model or ring buffer;
- the live diagnostics channel is **separate from IF-03 `/api/v1/events`**. Log records are diagnostics, not application/domain status events;
- high-frequency observations should not automatically produce one INFO record per observation; detailed per-observation diagnostics belong at controlled diagnostic levels while current health/counters remain part of status/metrics;
- stable TimingNode/data-source/device/correlation identifiers should be represented consistently in diagnostic messages/context, without making logging context the owner of application state;
- logging is not the mechanism for application status, registration history, audit/domain records or upstream synchronisation state;
- Logback/reload4j or another backend is not part of the baseline unless later operational requirements justify it.

<a id="fig-si01-05"></a>
![Runtime logging and live diagnostics](../assets/architecture/runtime-logging.svg)
*Figure SI01-05 — Runtime logging, retained file sink and engineering live diagnostics.*

The exact default file size, retention count and production log level remain deployment choices
and must be measured on the target platform before being treated as accepted field defaults.
Per-package levels, persistent runtime overrides, JSON file logging and a general-purpose
diagnostics framework are outside A08.

SLF4J 2.0.x is compatible with the Java-8 baseline; the implementation repository should pin
the API/provider patch version together through Maven dependency management.

#### Configuration and composition architecture

Configuration describes deployment/composition rather than domain behaviour hard-coded in source. The concrete deployment/configuration contract is owned by **IF-11** in `32-11-ISD-application-configuration.md`.

The main configuration groups are:

```text
ApplicationConfig
├── applicationId
├── timingSystems
│   └── <timingSystem>
│       ├── timingSystemId
│       └── timingNodes
├── io
│   ├── devices
│   │   └── antennas
│   ├── deviceNetworks
│   │   ├── can
│   │   └── network
│   ├── registrationRouting
│   ├── messaging
│   │   └── upstream
│   │       └── connectors (1..N when UpstreamGateway is configured)
│   └── storage
├── presentation
├── logging
├── runtime
└── security
```

The identity boundaries are deliberate:

- the application owns a stable `ApplicationId`;
- the application composes 1..N internal `TimingSystem` contexts, each with an internal `TimingSystemId`;
- each TimingSystem owns 1..N TimingNodes;
- a `TimingNode` owns its stable functional `TimingNodeId` and configured `LocationId`;
- `TimingSystemId` is local composition/simulation identity and is not added to TimingData/upstream addressing;
- the high-level I/O model separates Devices from Device Networks;
- Devices names the functional device endpoints/concepts, including antennas, keypads, beepers, passive CAN devices and smart network devices;
- the application may compose 0..N configured antennas; each antenna has its own `AntennaId` and may map to 1..N `TimingNodeId` targets;
- Device Networks contains `CanNetworkController` for the actively managed CAN network and `NetworkDeviceService` for bidirectional network-device communication;
- when upstream messaging is configured for a TimingSystem, its protocol/gateway context uses 1..N connectors; multiple hosted TimingSystems keep those semantic contexts separate;
- connector-specific external names/routing identities do not replace `TimingNodeId`;
- presentation endpoints reference TimingNodes explicitly; an HTTP port, tablet or shell binding is not a property of the TimingNode domain object.

Deployment composition is intentionally small and default-driven:

```text
built-in application profile defaults
        +
platform defaults
        +
operating-mode defaults
        +
explicit deployment overrides
        +
resolved secret values
        =
effective ApplicationConfig
```

The selected **application profile** defines a topology/capability template for
the Timing Point Application. Concrete deployment profile IDs, TimingNode counts,
device combinations and compatibility mappings are not defined by this public
architecture unless an explicit public requirement owns them.

Profiles do not create different application/domain models. They resolve to the
same TimingSystem/TimingNode architecture and may be combined with platform and
operating-mode defaults plus explicit deployment configuration within the
profile's compatibility rules.

Platform and operating mode remain independent dimensions. Simulation may replace
concrete adapters while preserving the same TimingNode/domain implementation.

Console, Remote Shell and API form the baseline control/automation capability set
of the Timing Point Application and are not selected by the application profile.
Deployment configuration still controls concrete listener/binding settings. Web
remains a separate per-TimingNode browser-facing capability.

Startup follows distinct responsibilities:

```text
select defaults
  -> apply explicit deployment overrides
  -> resolve effective typed configuration
  -> validate references/settings
  -> runtime Composition composes the application
```

Profile/platform/mode resolution is configuration infrastructure. It is complete
before `Composition` receives the effective runtime `Config`; composition
does not contain profile-specific branches.

Build provenance remains separate from deployment configuration. `BuildIdentity` describes the built artifact; it is not loaded from IF-11 deployment settings. Core `EmbeddedBuildIdentityLoader` interprets the standard embedded provenance resource, while the concrete executable owns and filters that resource with its own application/build values. The embedded provenance contains stable build inputs/context — version, exact revision, source ref, build origin and dirty-state — but deliberately omits wall-clock build time, CI run identifiers and actor/user data. This keeps the artifact self-identifying for test/support work without introducing per-run variability solely from timestamp/run metadata.

Working rules:

- keep secrets/credentials out of committed configuration and store only secret references there;
- prefer explicit/manual composition initially rather than adding a dependency-injection framework without a demonstrated need;
- keep overlay rules deliberately limited rather than creating general inheritance/includes;
- use YAML as the current default IF-11 file syntax and keep its SnakeYAML parser/mapping inside application-core infrastructure; the logical IF-11 contract is not coupled to the SnakeYAML API;
- create Java configuration types only as real executable slices need them rather than mirroring the entire conceptual tree in advance.

#### Data and persistence architecture

Keep the data roles simple:

- `LogBook` is passive state and holds committed immutable `TimingData` values;
- `NextUpTeams`, `StageStartTimes` and `RaceData` are separate passive
  per-node state objects;
- the TimingNode worker is the single writer for those mutable per-node objects;
- each state type that needs persistence owns its semantic persistence rules above the lower Storage layer;
- `TimingDataPersistence` is the durable/recovery semantic boundary for committed timing data;
- lower Storage contracts remain generic and contain no TimingData/TimingNode semantics;
- future NextUpTeams/StageStartTimes/RaceData persistence follows the same dependency direction rather than adding Domain interfaces implemented by I/O;
- queries read consistent state without becoming another owner of it.

For example, StageStartTimes may be sent again when a TimingNode is opened after
a reboot, while the separately stored historical snapshots remain useful for
post-event analysis.

The first implementation can use simple local files; an embedded database is not
required. SDD-01 defines ordering, commit/visibility and the different persistence
roles. SDD-02 defines the Java worker and store boundaries.

Practical detailed-design work includes a half-written last TimingData record,
corrupt-file reporting, durable flush/fsync behaviour, file rotation and bounded
consumer reads. Analysis stores may use simpler append/snapshot formats because
they do not define the TimingData commit point.

#### Integration architecture

The **external device and network topology is owned by the SSSD**, because RFID/CAN devices, local LAN clients, displays and the upstream system are system-level deployment/interface relationships. This SSD starts at the **Timing Point Application** (SI-01) boundary and explains how the application realises those system interfaces internally through ports, adapters, callbacks, status handling and transport implementations.

##### Upstream messaging

Upstream messaging is a semantic system boundary, not a RabbitMQ API.
`UpstreamProtocol` in Domain defines the messages and state semantics exchanged
with the upstream system. It uses `TimingData` for timing-record payloads and
also owns synchronisation/reconciliation and system-level protocol messages such
as ping/pong.

`UpstreamGateway` and its 1..N connectors remain I/O responsibilities. They
carry the encoded protocol representation and own transport/session resources;
they do not become owners of TimingData fields or upstream protocol semantics.
`UpstreamMessageRouter` owns application-level target resolution after semantic
protocol decoding. A system-level operation is delivered through the owning
`TimingSystem.UpstreamMessagePort`; a TimingNode-targeted operation is resolved
by `TimingNodeId`, submitted through that TimingNode's serial boundary and
enters/leaves through `TimingNode.UpstreamMessagePort`. Protocol-level
operations such as heartbeat/status and synchronisation control therefore do
not need to be forced through a TimingNode.

```text
external upstream system
        |
        +--> RabbitMqConnector --+
        +--> DebugConnector -----+--> UpstreamGateway
                                      |
                                      | encoded UpstreamProtocol
                                      v
                               UpstreamProtocol
                                 /          \
                                /            +--> TimingData
                               v
                      UpstreamMessageRouter
                         |              |
                         v              +--> TimingNodeId
                   TimingSystem                |
              UpstreamMessagePort              v
               status / ping              TimingNode
                                       UpstreamMessagePort
```

Exact RabbitMQ connection/channel topology, routing keys and retry mechanics are
connector-level decisions. Product/deployment-specific upstream-system names and
private transport details remain outside the public architecture documentation.
Public protocol semantics and TimingData compatibility remain owned by Domain.

`TimingSystemId` and `ApplicationId` are not required on the upstream wire. `UpstreamMessageRouter` provides target resolution without becoming a generic internal message bus. Protocol messages that belong to the configured TimingSystem use its `UpstreamMessagePort` and `UpstreamProtocol`/`SystemStatus`; they do not need to be forced through a TimingNode.

##### RFID

RFID integration is an adapter boundary. Raw callbacks/protocol data do not directly mutate application state. The adapter is responsible for protocol/device interaction and turns accepted observations/health changes into typed application-facing messages.

Decoding must preserve the source/provider semantics required by the public input contract while proprietary encoding details stay behind the provider boundary. Source-specific mapping or policy must not be guessed by a generic adapter.

Power/startup/recovery lifecycle and filtering semantics are architectural concerns where they affect application behaviour; exact protocol commands, crypto/proprietary codecs and retry sequences remain implementation/private detail.

##### CAN, keypad, beeper and displays

`CanNetworkController` owns the active CAN network: bus lifecycle, discovery/scanning,
device online state and communication. CAN/device callbacks do not mutate
TimingNode state directly; accepted work crosses the normal application/serial
boundary.

`Rev1CanDisplay` is the passive CAN display generation. SI-01 owns the
display-specific `DisplayModel` for this path and actively translates that model
into CAN/device commands. The display does not own the ready-team/domain model.

`Rev2WifiDisplay` is deliberately different. It is a smart external client with
its own rendering and synchronisation behaviour. `NetworkDeviceService` provides the bidirectional network-device boundary.
In the current IF-09 design it makes the SI-01 data service discoverable and
accepts the session initiated by Rev2WifiDisplay. Rev2WifiDisplay owns
reconnect/resynchronisation behaviour. The concrete discovery/listener/session
mechanics are detailed below the high-level architecture rather than represented
as additional peer components.

SI-01 therefore publishes current timing/status/reference data to smart clients;
it does **not** drive Rev2WifiDisplay through the passive-display `DisplayModel`
and does not need to know how that smart display renders the data. Exact mDNS
service names and the application protocol (for example TCP/WebSocket) remain
deferred until IF-09 implementation needs them.

##### Connectivity

Status must distinguish at least local network reachability from external/upstream session health where those distinctions affect operator decisions. Temporary external connectivity loss must not silently invalidate otherwise available local operation.

#### Development view

##### Development boundaries

The development structure shall preserve the architecture dependency direction
without assuming that every architecture layer is a package or Maven artifact.

Architecture-level boundaries are:

- SI-01 has a reusable application-core implementation and a deployable
  executable application;
- the public IF-05 Java contract must be independently consumable by SI-01 and
  engineering/test tooling without depending on SI-01 internal Domain packages;
- dependencies normally follow the layer order downward; lower I/O code does not import Application/Domain types;
- higher layers may use generic lower-layer I/O contracts while Runtime composition selects concrete I/O implementations;
- public reference/core implementation code compiles and verifies without private
  production implementations.

The exact Maven reactor, artifact names, Java package layout, shared
`timing-data-api` placement and dependency checks are owned by SDD-02.

##### Public/private extension model

Private repositories may provide production device control, protocol implementations, deployment mappings and production data/codecs. Public core/reference implementation code defines supported contracts and must compile/test without those private implementations.

SI-01 uses one small **typed provider/extension mechanism** for implementation families that may cross the public/private boundary. The currently expected provider contracts are:

```text
TimingDataProvider
UpstreamProtocolProvider
AntennaProvider
CanProtocolProvider
DisplayProtocolProvider
```

The provider contracts are capability-specific; there is no generic domain-level
`Plugin` abstraction. Infrastructure extension-discovery support finds built-in and external providers at startup; `Composition` uses the resulting typed registry, validates configured provider IDs and then builds the normal runtime graph. Runtime/domain components receive normal typed
interfaces and never interact with class loaders or provider discovery.

Provider discovery/loading is a startup/composition responsibility. Provider IDs
must remain unambiguous and configuration errors must fail explicitly. The
concrete Java discovery/class-loading mechanism is detailed in SDD-02.

Built-in reference/simulation implementations remain part of the normal public
software where they are needed for development and verification. In particular,
`SimulatedAntenna` is always built in. Figure SI01-01 labels the generic
extension-provided alternative `VendorAntenna`; that label is illustrative, not
a fixed public implementation type. A deployment can select an
extension-provided implementation without changing the application/domain path
used by the built-in implementation. IF-11 owns provider selection in deployment
configuration; the concrete external-JAR packaging/search path remains a detailed
implementation concern.

#### Technology decision register

This table intentionally lives in the architecture section of this SSD because these choices shape the whole **Timing Point Application** (SI-01) architecture.

| Concern | Current direction | Status / next evidence |
| --- | --- | --- |
| Java baseline | Java SE 8 is the current SI-01 baseline | accepted for current implementation; verify the selected runtime on the Pi target |
| Extension mechanism | typed capability-specific provider contracts with startup composition; runtime/domain code remains provider-discovery agnostic | concrete Java discovery/loading is owned by SDD-02 |
| Build | Maven | accepted |
| Concurrency | TimingNode is an active object with one bounded serial execution boundary; contained state objects stay passive; callbacks, long queries and slow delivery remain outside that worker | SDD-02 uses composition for the first Java worker and keeps executor implementation replaceable |
| Internal messaging | typed immutable command/event/query objects only at async/ownership boundaries + explicit TimingNode mapping/routing at the owning boundary; no central generic dispatcher; direct calls inside a TimingNode task | architecture baseline selected; refine first consumer API signatures during implementation |
| Time model | dedicated `TimingTimestamp` + per-TimingSystem `TimeSource` for absolute time + separate monotonic duration source | IF-05 fixes canonical external timestamp serialization; controlled per-system offset/stepping supports simulation; clock synchronisation/correction policy remains to be completed |
| Dependency injection | explicit/manual composition initially | working direction; add framework only if complexity justifies it |
| Logging | SLF4J API in reusable application core; initial executable provider `slf4j-jdk14` / `java.util.logging` | architecture baseline selected; refine handlers/retention when runtime needs are known |
| Configuration | IF-11 effective `ApplicationConfig`: base + platform + optional profile + secret resolution | file syntax/library and first Java type set still open |
| Persistence | Domain-owned TimingDataPersistence over generic lower-layer storage; file/database mechanisms do not import Domain/Application types | ordering and visibility in SDD-01; Java storage/persistence split in SDD-02; record contract in IF-05 |
| API HTTP | JDK `HttpServer` for the first IF-03 request/response slice | A06 baseline selected; transport belongs to the API functional interface |
| API WebSocket | `org.java-websocket:Java-WebSocket:1.6.0` on a dedicated configured listener | A07 baseline selected; Java 8+, pure Java/NIO and existing SLF4J boundary; keep A06 JDK `HttpServer` unchanged |
| Remote shell | Java 8 JDK `ServerSocket`, line-oriented TCP, shared A04 command semantics | A05 development/service baseline selected; one active session, reconnect allowed; SSH/Telnet/authentication deferred |
| Upstream messaging | semantic ports + socket test adapter + RabbitMQ production-shaped adapter | architecture direction established; implementation detail deferred |
| Test doubles | public controllable stubs through the same supported ports | established direction |

Technology choices should fit the actual application and target. Pi compatibility is verified on real hardware; memory/thread footprint becomes a design concern only when measurements make it one.

#### Physical/deployment view

Representative **Timing Point Application** (SI-01) deployments are:

```text
Production field host
  Raspberry Pi Zero / Zero W
    one Timing Point Application process
      one or more TimingSystem aggregates
        each with 1..N TimingNodes
      local devices + local files
      optional network/upstream connectivity

Development/test host
  Linux or Windows
    same Timing Point Application core/application behaviour
    real or stub adapters
    may host multiple independent TimingSystems for simulation
```

The architecture should not require a different domain implementation for simulation. Different compositions select different adapters/topologies around the same application/domain behaviour. The system-level placement of the Timing Point Application relative to devices, operator clients, LAN/Wi-Fi and the upstream system is defined in the SSSD rather than duplicated here.

#### Testability and failure/recovery architecture


Testability is an architecture property. Application/domain code should where practical:

- avoid uncontrolled threads and global mutable state;
- receive absolute time through an injectable abstraction;
- receive duration/timeout measurements through a controllable monotonic abstraction where needed;
- include tests that step the wall clock forwards/backwards and cross representative DST/local-time transitions;
- exercise per-TimingNode ordering/non-overlap, independent-node progress and bounded-ingress overload behaviour deterministically;
- depend on semantic ports rather than concrete device/network libraries;
- keep protocol parsing in adapters;
- use deterministic handlers that can run synchronously in unit tests;
- expose observable status for degraded/failure conditions;
- avoid `Thread.sleep()` as a domain timing mechanism.

Failures should stay visible and should not silently lose timing history. Retry
counts, timeouts and the exact durability guarantee are detailed-design choices
once we have real implementation/measurement evidence.

Detailed verification strategy belongs in `60-SVP-software-verification-plan.md`.

#### Detailed-design documents

Keep this SSD at architecture level. Put implementation detail in the focused
SDDs below instead of repeating it here.

Current focused SDDs:

```text
43-01-SDD-01-data-and-display-design.md
  internal data/runtime algorithms:
  LogBook recording, TimingData persistence/recovery, query isolation,
  prepare-team/reference/display behaviour

43-01-SDD-02-java-component-design.md
  concrete Java realisation:
  Maven artifacts, packages, classes/interfaces, queue/thread/executor choices,
  provider discovery and dependency checks

43-01-SDD-03-backoffice-transport-design.md
  transport realisation below the upstream semantic boundary
```

IDDs define the external/file/API contracts. The SDDs use those contracts; they
do not define a second version of them.

#### Open architecture decisions

Only keep questions here if the answer could change the SI-01 architecture.
Implementation questions go in the relevant SDD.

Open architecture questions include:

- production authentication/authorisation and final network exposure policy;
- operational policy for material wall-clock corrections when it affects timing
  correctness or operator action;
- final upstream/backoffice semantic responsibilities as IF-06 is promoted;
- whether measured multi-TimingNode/Pi resource behaviour ever requires changing
  the current ordered-per-node responsibility model;
- any target-runtime limitation that forces a change to the Java-8/application
  architecture baseline.

Queue sizes, Java signatures, executor choice, fsync/atomic file operations,
rotation and LogBook indexes belong in SDD-01/SDD-02, not here.


---

## Data and display detailed design

**Source document:** [43-01-SDD-01-data-and-display-design.md](43-01-SDD-01-data-and-display-design.md)

Status: working draft / focused detailed design

Software item: **SI-01 — Timing Point Application**

This SDD explains **how the data flows inside SI-01**: how LogBook entries are
recorded, when a TimingData record is committed, how restart/recovery works, and
how queries, prepare-team data and display data use that state.

The SSD still defines the architecture. IF-05 still defines the TimingData
record/file format. SDD-02 chooses the concrete Java classes, queues and worker
threads.

The first version does **not** need an embedded database. Committed LogBook
entries are written as append-only IF-05 TimingData. After a restart, SI-01 can
read those records back and rebuild the LogBook. Other state, such as RaceData or
prepare-team state, can use its own simpler backup/sync mechanism.

Identifiers and known ranges come from `03-domain-baseline.md`. This SDD only
describes how SI-01 uses them.

### Design scope and data ownership

#### Two traceable information models

Two information flows must not be conflated:

1. **registration stream/ledger** — timing and operational entries that are synchronised as an ordered source stream;
2. **prepare-team registry history/state** — keypad/operator actions that prepare/remove teams and drive current display state.

Both need traceability and persistence, but they have different semantics and sequence scopes.

#### TimingNode source and location identity

Every `TimingNode` has a `TimingNodeId`. A registration fact also captures
the applicable configured `LocationId`.

`TimingNodeId`, `LocationId` and `AntennaId` are separate namespaces. I/O
configuration relates observations to TimingNodes; code must not infer one
identity from another.

The shared `LocationId` Java value type owns only the common positive numeric
representation. Concrete event/profile LocationId meaning, allowed sets and
source-to-node mappings are deployment/reference information and are not defined
by this public SDD.

#### LogBook and IF-05 TimingData

The runtime `LogBook` stores committed immutable `TimingData` values.
The current design does not add a second logbook-specific timing-data type.

That choice is deliberate. The old/reference software already treats one LBR
record as both the logged timing fact and the object consumers read. The new
design keeps that useful property while giving the file format a clear IF-05
contract.

The system-owned **IF-05 TimingData Interchange** contract is defined by
`32-05-ISD-timingdata-interchange.md`. It owns the common TimingData semantics, shared `LocationId` and
`RegistrationId` value representations, sequence/key semantics and compatibility
rules. The configured event/profile/reference model owns the concrete identifier
domains, while the configured TimingData profile owns its concrete classes and
matching representation/codec. The default/reference JSON + JSON Lines representation is described separately by `33-05-IDD-timingdata-interchange.md`.

The same immutable `TimingData` object can therefore be:

- appended by `TimingDataStore`;
- added to `LogBook` after that append is durable;
- read by runtime consumers;
- offered to downstream/upstream delivery.

A `TimingDataProvider` supplies the configured concrete TimingData factory and
codec. Different profiles may return different concrete classes while SI-01
continues to use the common TimingData interfaces.

#### Registration identity resolution

All participant registrations are committed with one shared `RegistrationId`
representation defined by IF-05. The concrete RegistrationId domain and meaning
may be event/profile-specific.

`TagId` and `TeamId` are resolved to that canonical value before the
definitive TimingData record is created:

```text
TagId  -----> RaceData/reference resolution ----\
                                                  +--> RegistrationId
TeamId -----> RaceData/reference resolution ----/
```

`TagId` belongs to the RFID/tag input path. `TeamId` belongs to the
team/reference-data/manual path. Only the resolved `RegistrationId` is passed
to the TimingData factory. The resolution may use current `RaceData` when
reference data is required.
Concrete source encoding, categories, ranges, allowed RegistrationId values and
mapping tables remain outside this public SDD. A provider may translate an
external representation; the active event/reference profile supplies the concrete
identity semantics while IF-05 keeps the shared boundary representation stable.

### TimingNode serial execution and timing-data commit

#### Active-object boundary

A `TimingNode` is the active serialization boundary for all mutable state that
belongs to one timing point. The contained state objects stay passive:

```text
TimingNode  <<active object>>
  +-- bounded serial work queue
  +-- one serial worker (first implementation)
  |
  +-- LogBook           passive, committed TimingData history
  +-- NextUpTeams       passive
  +-- StageStartTimes   passive
  +-- RaceData          passive
  +-- lifecycle/location state
  |
  +-- TimingDataStore
  +-- NextUpTeamsStore
  +-- StageStartTimesStore
  +-- RaceDataStore
```

The Active Object wording describes the behaviour, not a required Java base
class. SDD-02 uses composition for the first implementation.

Public/application calls stay ordinary methods. The TimingNode hides the
asynchronous hand-off used by its Active Object implementation.

For a state-dependent operation such as `setLocation(...)`, `open()`,
`close()` or a consistency-sensitive status query, the public call does not
report success merely because work entered the queue. The TimingNode queues an
internal work item, executes it later against the then-current ordered state and
returns the processed result to the caller. A Java implementation may connect
those two moments with an internal `Future`; that Future is not part of the
caller-facing domain API.

Submission-only ingress is a separate contract. A device callback may need only
to know whether bounded work was admitted so that the callback thread can
continue immediately. In that case `ACCEPTED` means only accepted for later
processing.

The contained state objects are passive but not globally readable. Lifecycle,
location, LogBook, NextUpTeams, StageStartTimes and RaceData are accessed through
the TimingNode ownership boundary. The single TimingNode worker gives one clear
order across registrations, reference-data updates and lifecycle changes. No
producer lock is required around sequence allocation because only this worker
performs the commit step.

#### TimingData commit and sequence

A producer may have completed work that belongs before the TimingNode boundary,
such as device decoding/filtering or translation into a semantic registration
request. That does not let the producer decide state-dependent TimingNode
conditions from outside the node.

When the work item reaches the serial lane, the TimingNode checks the current
state needed by that operation. Examples include whether the node is open, which
location is active and which current reference data is needed. Only then does the
worker create/commit the resulting TimingData.

For a caller that waits for a registration result, successful return therefore
means the registration operation has reached its defined commit/visibility point;
for submission-only device ingress there is no synchronous caller waiting for
that later result.

Only when the worker is ready to commit does it ask the LogBook for the next
sequence. Sequence is therefore not assigned when work is placed on the queue.

Conceptually:

```java
void processRegistration(RegistrationInput input) {
    long sequence = logBook.nextSequence();

    TimingDataFactory.Context context =
        timingDataContext(sequence, activeLocationId, input.effectiveTime(), timeSource.now());

    RegistrationId registrationId = raceData.resolveRegistrationId(input);

    TimingData data;
    if (input.isAutomatic()) {
        data = timingDataFactory.createAutomaticRegistration(context, registrationId);
    } else {
        data = timingDataFactory.createManualRegistration(
                context, registrationId, input.timeSource());
    }

    timingDataStore.append(data);     // returns after durable append
    logBook.add(data);                // consumer visibility point
    newTimingDataEvent.emit(data);
}
```

`LogBook.nextSequence()` is based on committed state:

```text
empty LogBook                  -> 1
last committed sequence = N    -> N + 1
```

Calling `nextSequence()` does not consume the number. If persistence fails,
the record is not added to LogBook and the next attempt still uses the same
sequence. A later work item may not overtake the failed timing-data commit.

The important ordering is:

```text
TimingNode worker
  -> choose next sequence
  -> build typed immutable registration TimingData through configured factory
  -> TimingDataStore.append(record)
  -> durable
  -> LogBook.add(record)            <-- committed domain state
  -> newTimingDataEvent.emit(record)
  -> subscribed listeners are notified
```

There is no direct producer-to-store path and no second TimingNode serial worker.

![TimingNode producers and durable TimingData commit path](../assets/architecture/timingdata-producer-pipeline.svg)

*Figure SDD01-TD01 — State-changing input enters the TimingNode serial boundary; the concrete TimingData value created by the configured factory becomes visible only after durable persistence.*

#### Other TimingNode state and per-type stores

Not every state type has the same durability semantics.

`TimingDataStore` is special: successful durable append is part of the timing
record commit. The LogBook is rebuilt from committed TimingData after restart.

`NextUpTeamsStore`, `StageStartTimesStore` and `RaceDataStore` serve a
different first purpose: preserve accepted state changes/snapshots for
post-event analysis. Their stored data lets engineers later answer questions
such as which teams were next-up or which stage-start times/reference data were
known when a timing decision was made.

Those files are not automatically the runtime source after reboot. For example,
StageStartTimes can be sent again when the node is opened. Keeping its historical
file is still valuable for later analysis.

All state changes are ordered by the TimingNode worker. The first implementation
may also perform these small/infrequent store writes on that worker. If target
measurements show an analysis-store write can delay registration unacceptably,
the immutable snapshot can later be handed to a bounded persistence executor.
That optimization must not change TimingNode state ordering and must not
introduce an unbounded hidden queue.

#### Query/consumer visibility

Consumers do not read mutable TimingNode-owned objects directly.

A consistency-sensitive query enters the TimingNode serial lane and captures the
state it needs at a defined point in the same ordering as state changes. If the
query requires expensive calculation, only the short snapshot step runs on the
lane; the calculation continues on the caller/query execution context after the
snapshot has been returned.

Conceptually:

```text
query caller
  -> TimingNode query
       -> ordered serial lane
       -> capture immutable/read-only state view
       -> return view/result
  -> optional long calculation outside lane
```

For LogBook history the first implementation may capture a shallow immutable
reference view because `TimingData` values are immutable. The exact
representation and allocation strategy belong to SDD-02 and measurement on the
target. A reusable internal buffer is acceptable only if callers cannot observe
it being mutated/reused after the query returns.

A query that is ordered before a new commit may legitimately see the earlier
state; a query ordered after that commit sees the new state. A separately
published immutable status/read snapshot may later serve high-frequency readers,
but it must have explicit freshness semantics and does not make the underlying
mutable state globally readable.

![TimingNode asynchronous ownership and query isolation](../assets/architecture/timingdata-async-ownership.svg)

*Figure SDD01-TD02 — TimingNode refinement: one serial execution boundary owns mutable state; short reads return immutable views and `newTimingDataEvent` provides post-fact notification without exposing mutable state.*

#### Runtime flows

The sequence diagrams below show the different caller contracts explicitly.
They deliberately distinguish queue admission from the domain result produced
when work executes against current TimingNode state. SDD-02 owns the concrete
Java queue, Future and worker mechanism.

##### Automatic RFID registration

![Automatic RFID registration sequence](../assets/architecture/timingdata-sequence-auto-registration.svg)

*Figure SDD01-TD03 — A device callback receives only bounded admission status and returns; later TimingNode processing uses current state and has no synchronous callback waiting for the domain result.*

##### Manual registration

![Manual registration sequence](../assets/architecture/timingdata-sequence-manual-registration.svg)

*Figure SDD01-TD04 — A presentation-driven registration call waits for its actual processed/committed result while the Future remains internal to TimingNode.*

##### Long query while registrations continue

![LogBook query isolation sequence](../assets/architecture/timingdata-sequence-query-isolation.svg)

*Figure SDD01-TD05 — The query captures its read view on the TimingNode lane and performs longer calculation outside the lane; it does not read LogBook directly.*

##### Later producers

![Generic TimingNode producer sequence](../assets/architecture/timingdata-sequence-generic-producer.svg)

*Figure SDD01-TD06 — Later state-dependent operations use the same TimingNode ownership/ordering boundary; their caller contract must still state whether they wait for a result or are submission-only.*

##### State-dependent OPEN waits for its processed result

![TimingNode OPEN sequence](../assets/architecture/timingnode-sequence-open.svg)

*Figure SDD01-TD07 — `open()` returns only after the queued operation has executed against current TimingNode state; the internal Future is not exposed to the caller.*

##### Concurrent OPEN and SET_LOCATION are ordered by the TimingNode

![TimingNode OPEN / SET_LOCATION ordering sequence](../assets/architecture/timingnode-sequence-open-set-location.svg)

*Figure SDD01-TD08 — State-dependent validation happens when each operation reaches the serial lane, so SET_LOCATION cannot rely on an earlier external read of CLOSED state.*

##### Timeout means outcome unknown, not rollback

![TimingNode timeout sequence](../assets/architecture/timingnode-sequence-timeout.svg)

*Figure SDD01-TD09 — A caller timeout stops waiting but does not cancel already accepted work; the caller re-queries state before deciding what happened.*

##### Thread/ownership responsibilities

| Execution role | May block on | Must not do |
| --- | --- | --- |
| presentation caller waiting for a state-dependent result | bounded TimingNode operation wait | read/mutate TimingNode-owned state directly |
| device/callback ingress | short validation + bounded submission | wait for durable commit, run long domain work, read node state directly |
| TimingNode serial worker | ordered domain operation; required local persistence; short snapshot capture | client rendering, slow network retry, long ranking calculation |
| query caller/worker | long calculation on returned immutable view | retain a mutable internal buffer or bypass TimingNode ownership |
| signalling/upstream worker | its own delivery/retry policy | mutate TimingNode state directly or block TimingNode commit |

For the first one-node implementation, one dedicated worker is the simplest
mechanism. A later multi-node runtime may share executor threads only if each
TimingNode still processes at most one work item at a time, preserves FIFO order
and retains the same caller-visible operation semantics.

### TimingData persistence and recovery

This design implements `SI01-REQ-045..048` together with the applicable IF-05
semantics and the reference representation in
`33-05-IDD-timingdata-interchange.md`.

#### Recovering the next sequence

We do not need a separate sequence-counter file in the first implementation.
The TimingData file already tells us the last committed sequence:

```text
no committed records       -> nextSequence = 1
last committed sequence N  -> nextSequence = N + 1
```

At startup:

- read complete IF-05 records in order;
- check that the file belongs to one TimingNode;
- check that the committed sequence increases without duplicates or unexpected gaps;
- ignore/remove only a half-written final record that has no complete line ending;
- never reuse a committed `(TimingNodeId, SequenceNumber)`.

A half-written **last** record after power loss is recoverable: truncate back to
the last complete record and continue from there.

A corrupt **complete** record, duplicate sequence or gap is different. Do not
silently skip or renumber it. Stop recovery for that TimingNode and report the
problem so support/operator tooling can see it.

If we later add a cached sequence-counter file for faster startup, it is only a
cache. The committed TimingData file remains the source used to check/rebuild it.

#### Persistence roles

TimingData has the strongest rule:

- a TimingData record is committed only after writing its complete reference
  representation to the configured local store has completed successfully;
- only then is the same concrete `TimingData` value added to LogBook, published
  as a committed live event or returned as a successful commit result;
- the TimingData file is used to rebuild LogBook after restart.

Other per-node stores have a different first purpose:

- `NextUpTeamsStore` preserves accepted next-up state/history for analysis;
- `StageStartTimesStore` preserves accepted start-time snapshots for analysis;
- `RaceDataStore` preserves accepted reference-data snapshots/versions for
  analysis.

Those historical stores do not automatically restore live state after reboot.
The live protocol may resend the current data, for example when a TimingNode is
opened. Recovery semantics can be promoted later if an operational requirement
needs them.

The successful write above is the software commit boundary. The stronger
guarantee against sudden power loss depends on the concrete filesystem and flush
primitive and remains a target-specific design/verification point.

Implementation points to verify on the target Pi:

- what exact flush/fsync call provides the required power-loss durability level;
- what happens if power disappears halfway through the final line;
- whether truncating the incomplete tail is safe on the target filesystem;
- how a corrupt complete record is reported instead of silently ignored;
- file rotation/retention for TimingData and analysis stores;
- whether any non-critical store write needs asynchronous offload after
  measurement.

We do not need a database just to solve these cases.

#### Startup flow

The first startup flow is intentionally straightforward:

```text
start process
   |
   v
load configuration
   |
   v
open TimingData file for each configured TimingNode
   |
   v
read and validate complete IF-05 records
   |
   +--> half-written final line: truncate to last complete record + report
   |
   +--> corrupt complete record / duplicate / gap: recovery error, do not append
   |
   v
nextSequence = last committed sequence + 1
   |
   v
rebuild LogBook
   |
   v
load other saved/reference state
   |
   v
start interfaces/devices
   |
   v
connect/synchronise upstream when available
```

A new/empty TimingData file starts at sequence 1.

Rebuilding the LogBook does **not** automatically reopen a TimingNode. For
example, if the last historical state record says `OPEN`, a process restart must
not start accepting new observations merely because that old record exists. The
open/closed restart policy belongs to lifecycle/control requirements.

If prepare-team or reference-data backup is corrupt, report that explicitly too;
do not silently present the system as healthy.

### Prepare-team and reference data

#### Prepare-team registry

Keypad input indicates which teams should prepare at the timing node/exchange point. A keypad action is not itself a passage/start/penalty registration.

The keypad can:

```text
add team to prepare registry
remove team from prepare registry
```

Those actions must remain traceable so operator history is auditable and the registry can be recovered after restart.

Conceptually:

```text
PrepareTeamRegistry
  current teams to prepare: [456]

  internal traceable history:
    501  TEAM_ADDED     123
    502  TEAM_ADDED     456
    503  TEAM_REMOVED   123
```

The registry owns both:

- **current state** — which teams must currently prepare at the timing node/exchange point;
- **traceable history** — the keypad/operator add/remove mutations needed for audit and restore.

The history is an internal persistence/state aspect of the registry, not a separate architecture component.

Illustrative internal history record:

```java
final class PrepareTeamEvent {
    private long sequenceNumber;
    private TimingNodeId timingNodeId;
    private PrepareTeamEventType type; // ADDED / REMOVED
    private TeamNumber teamNumber;
    private Instant createdAt;
    private InputSource source;         // keypad / UI / API / test
}
```

The prepare-team history sequence is a separate design question from the `TimingNodeId`-scoped sequence. It may use its own internal registry sequence or later a broader operational-event sequence, but it must not accidentally consume/alter a `TimingNodeId` registration sequence unless requirements explicitly make a prepare-team action a registration-stream entry.

#### Reference-data synchronisation

Start-time and participant/reference mappings supplied by an external system may also need to be available locally.

The start-time semantic model must remain compatible with sources that define a race/stage start as **time-of-day only**. An optional date/race-day value may be carried when available, but consumers shall not require it. Accepted registration observations remain absolute `TimingTimestamp` values. For elapsed-time calculation, a time-only start is resolved in the configured event/race time zone to the most recent valid occurrence not after the registration timestamp, so a midnight crossing is handled as the next civil day rather than as a negative elapsed time.

The application maintains local in-memory repositories and synchronises accepted data from the backoffice.

A useful model is snapshot/version based:

```text
Backoffice
   |
   | ReferenceDataSnapshot(version, entries)
   v
Backoffice adapter
   |
   v
TimingSystem/application message queue
   |
   v
ReferenceDataService
   |
   +--> validate version/content
   +--> replace/update repositories
   +--> write simple backup file
   +--> publish status/data-changed event
```

Pseudocode:

```java
void handle(StartTimeSnapshotReceived message) {
    StartTimeSnapshot incoming = message.getSnapshot();

    if (!startTimeValidator.accept(incoming, startTimes.snapshot())) {
        status.referenceData().recordRejectedUpdate(incoming.getVersion());
        return;
    }

    startTimes.replace(incoming);
    referenceBackup.save(referenceData.snapshot());
    status.referenceData().recordStartTimesSynced(incoming.getVersion());
    displayService.referenceDataChanged();
}
```

The same pattern can be used for other participant/reference mappings. Full-snapshot versus delta updates, version identifiers and correction semantics still need requirements/ISD design.

#### Keypad behaviour

The CAN keypad can both add and remove team numbers from prepare-team registry.

Possible incoming messages:

```text
KeypadTeamAddRequested(teamNumber)
KeypadTeamRemoveRequested(teamNumber)
```

Both enter the normal serialized state-change path. The handler mutates `PrepareTeamRegistry`; the registry records the traceable mutation and updates its current set atomically from the application/domain point of view. The handler then rebuilds/publishes display data.

```java
void handle(KeypadTeamAddRequested command) {
    prepareTeams.add(
        command.getTeamNumber(),
        KEYPAD,
        clock.instant());

    backupCoordinator.prepareTeamsChanged(prepareTeams);
    displayService.prepareTeamsChanged(prepareTeams.currentTeams());
}
```

Removing a team follows the same path with `REMOVED`.

The application, not the keypad, remains authoritative for current prepare-team registry. Duplicate-add, remove-not-present, ordering and capacity behaviour need explicit requirements.

### Display data

#### Display model

Display data is derived from **current state**, not by forwarding keypad history directly.

```text
PrepareTeamRegistry         StageStartTimeRegistry
      |                          |
      +--------------------------+
      |                          |
      +----> DisplayModelBuilder <+
                    |
                    v
              DisplayModel
              /          \
             v            v
      V1 CAN adapter    V2 data session
```

![In-memory data, backup and V1/V2 display behaviour](../assets/architecture/data-display-flow.svg)

A conceptual model might contain:

```java
final class DisplayModel {
    private List<TeamDisplayData> prepareTeams;
    private Instant generatedAt;
    private long revision;
}

final class TeamDisplayData {
    private TeamNumber teamNumber;
    private StartTime startTime;
    private Duration elapsedTime;
    private LocalRank rank;
}
```

Fields are illustrative. The display ISD will ultimately define the system contract; a separate IDD is needed only if concrete design deserves its own baseline.

#### Display V1 — passive CAN display

Display V1 is relatively passive and must be actively driven by the timing application.

V1 does not reconstruct add/remove history. The application derives the **current prepare-team list** and writes the appropriate complete/current display state.

```java
void refreshV1() {
    DisplayModel current = displayModelService.current();
    canDisplayV1.apply(current);
}
```

Implications:

- `TEAM_ADDED` updates `PrepareTeamRegistry`, then triggers a refreshed current list;
- `TEAM_REMOVED` updates `PrepareTeamRegistry`, then triggers a refreshed current list;
- after discovery/reconnect/reset, send a full refresh from current state;
- a V1 reset does not destroy application prepare-team registry;
- status distinguishes discovered/reachable/last successfully updated.

#### Display V2 — smart Wi-Fi display

Display V2 is a smarter network client. The timing application communicates domain/display **data**, while V2 owns presentation/rendering behaviour.

Intended connection direction:

1. timing application advertises an mDNS service;
2. V2 discovers the service;
3. V2 connects to the timing application;
4. application sends current ready-team/reference/result data;
5. application and V2 keep data synchronised while connected.

The data can be represented as a revisioned snapshot/model even though V2 renders it differently from V1.

```java
void onDisplayV2Connected(DisplaySession session) {
    session.send(displayModelService.current());
}
```

A later optimisation may send deltas, but reconnect must always be recoverable through a complete current snapshot.

#### Registration versus ready-team display state

These flows remain separate:

```text
RFID / manual / lifecycle / later start / penalty logic
          |
          v
      TimingNode
   bounded serial work
          |
          v
    TimingData
          |
          +--> TimingDataStore (durable)
          +--> LogBook (visible after durable append)
          +--> StageTiming / ranking inputs
          +--> downstream integration

keypad/UI prepare/remove team
          |
          v
    PrepareTeamRegistry
      current state + internal history
          |
          +--> V1 current list
          +--> V2 synchronised data
```

A team can be ready for display without having produced a registration, and a registration can exist independently from whether that team is currently ready.

Later interactions (for example automatically removing a team after a successful start/passage) must be explicit domain requirements rather than accidental display side effects.

### Rules when implementing IF-05

The TimingData record/file contract is not re-specified here. SI-01 design shall
conform to **IF05-REQ-001..007** in
`32-05-ISD-timingdata-interchange.md`.

The following temporary design constraints cover only the internal realisation
needed around that interface:

#### TimingNode state and record pipeline

- **CAND-PIPE-001** — Each TimingNode shall provide one bounded serial execution
  boundary for its mutable per-node state. Contained state objects such as
  LogBook, NextUpTeams, StageStartTimes and RaceData shall remain passive.
- **CAND-PIPE-002** — Registration sequence shall be selected by the TimingNode
  worker immediately before commit, not when ingress work is queued.
- **CAND-PIPE-003** — A TimingData record shall become visible in LogBook only
  after `TimingDataStore` reports the complete append durable.
- **CAND-PIPE-004** — The LogBook shall hold the same canonical
  immutable `TimingData` values used by the TimingData persistence/interchange
  boundary; no second logbook-specific timing-record type is required.
- **CAND-PIPE-005** — Potentially long queries and network delivery/retry shall
  execute outside the TimingNode serial worker.
- **CAND-PIPE-006** — Consumers needing a stable LogBook view shall use a short
  read/copy operation and perform long calculations after releasing LogBook
  synchronization; implementations should avoid unnecessary per-query garbage.

#### Identity resolution before IF-05 commit

- **CAND-ID-001** — An automatic/tag registration shall resolve its `TagId`
  to the canonical IF-05 `RegistrationId` before the definitive TimingData
  value is created.
- **CAND-ID-002** — A manual/reference-data registration shall resolve its
  `TeamId` to the same canonical `RegistrationId` concept before TimingData
  creation.
- **CAND-ID-003** — Concrete source encodings, category/range rules and mapping
  tables shall stay behind their provider/reference-data boundary unless a public
  interface requirement explicitly promotes them.

#### Local data and per-type stores

- **CAND-DATA-001** — The initial implementation shall maintain committed
  LogBook state, next-up state and reference state in typed in-memory objects
  without requiring an external database engine.
- **CAND-DATA-002** — `TimingDataStore` shall be the durable/recovery source
  for committed TimingData.
- **CAND-DATA-003** — NextUpTeams, StageStartTimes and RaceData shall each use a
  type-specific store when their accepted state/snapshots are preserved for
  analysis; these stores shall not be treated as runtime recovery authority
  unless a requirement explicitly says so.
- **CAND-DATA-004** — TimingData recovery faults and analysis-store failures
  shall be visible in system status/diagnostics.
- **CAND-DATA-005** — The system shall track enough reference-data
  synchronisation metadata to determine whether local data is current/stale
  relative to the latest accepted update.

#### Ready-team/keypad data

- **CAND-READY-001** — The system shall maintain prepare-team registry logically separate from timing/registration records.
- **CAND-READY-002** — Adding or removing a team from prepare-team registry shall create a traceable persisted ready-team event.
- **CAND-READY-003** — Ready-team events shall be processed through the normal controlled state-change path.
- **CAND-READY-004** — Prepare-team registry state shall be recoverable after application restart from locally persisted information.
- **CAND-READY-005** — The keypad shall be able to request both addition and removal of a team number.

#### Displays

- **CAND-DISP-004** — The application shall derive display data from current timing/reference/prepare-team registry rather than requiring displays to reconstruct operational event history.
- **CAND-DISP-005** — Display V1 shall be actively controlled by the application and shall receive current ready-team display state/list after relevant changes or reconnect.
- **CAND-DISP-006** — Display V2 shall consume synchronised timing/ready-team/reference data from the application and shall own local presentation/rendering behaviour.
- **CAND-DISP-007** — When Display V2 connects or reconnects, the application shall be able to provide a complete current data snapshot independent of previously delivered incremental updates.
- **CAND-DISP-008** — Display data shall support a revision/version mechanism or equivalent means of detecting stale/missed state.

### Open questions

- What exact identifiers represent virtual registration systems?
- How are physical producers mapped to one or more `TimingNodeId` values in deployment configuration?
- What exact filesystem durability primitive/policy is required before a completed append is considered durable on each deployment platform?
- Which additional producer/domain paths should emit future IF-05 record families after their requirements are promoted?
- Should ready-team events use their own sequence stream or a broader operational event sequence?
- Should ready-team recovery use an append persistent file, a current-state snapshot, or both?
- How frequently may simple backup files be written without unnecessary SD-card wear?
- Should reference data use one combined backup snapshot or separate files per data set?
- Is start-time synchronisation always a full snapshot, or can the backoffice send deltas/corrections?
- What is the keypad protocol for distinguishing add versus remove?
- What should happen on duplicate add or removal of a team that is not ready?
- Is ready-team ordering significant and, if so, is it insertion order, start-time order, or another rule?
- How many teams can be ready concurrently?
- Should a successful start/passage automatically affect the prepare-team list, or must that always be an explicit action?
- Does V1 retain any useful state across reconnect/power interruption or must every connection be treated as blank/unknown?
- What exact data fields does V2 need, and which presentation decisions belong exclusively inside V2?


---

## Java component, package and artifact detailed design

**Source document:** [43-01-SDD-02-java-component-design.md](43-01-SDD-02-java-component-design.md)

Status: working draft / focused detailed design

Software item: **SI-01 — Timing Point Application**

This SDD describes the **Java implementation** of the SI-01 design: Maven
modules, packages, classes/interfaces, composition, queues/threads and provider
loading.

The SSD says what the architecture must do. SDD-01 describes the LogBook/data
flow. IDDs such as IF-05 define external/file contracts. This document picks the
Java mechanisms that implement those decisions.

### Why this SDD exists

This detail is separate because module/package choices directly affect the Java
repository, dependencies and what can be reused by other applications.

The central rule is:

> **An architecture layer or Java package is not automatically a Maven artifact.**

Keep these concepts distinct:

1. **Architecture responsibility** — semantic ownership and dependency direction, defined by the SSD architecture.
2. **Java package** — cohesive source organisation and enforceable dependency discipline.
3. **Maven artifact** — reusable library or deployable application with a concrete consumer/lifecycle reason to exist.
4. **Application composition** — assembly of application-core code and selected implementations into an executable.
5. **Contract/port** — semantic boundary placed with the responsibility that owns its meaning.

A separate artifact is justified only by a real consumer, reuse, dependency, lifecycle, deployment, ownership, public/private, release or versioning boundary.

### Initial Maven reactor

The current reactor has two reusable artifacts plus one executable application.
The shared TimingData library artifact is justified by the independent SI-01 and
Engineering Client consumers. It intentionally remains one artifact containing the
semantic contracts, default/reference profile, codec and factory/provider; these
responsibilities are not split into separate API/default JARs:

```text
reactor/
├── pom.xml                    timing-point-parent
├── shared/
│   └── timing-data/
│       └── pom.xml            event-timing-data.jar
├── core/
│   └── pom.xml                timing-point-core.jar
└── app/
    └── pom.xml                timing-point-app.jar
```

Working coordinates:

```text
groupId: io.github.brainboxemb.eventtiming

parent:          timing-point-parent
TimingData:      event-timing-data
core:            timing-point-core
executable:      timing-point-app
```

The root POM only groups/configures the build; it is not a runtime component.

The `core/` Maven module is the reusable **application core of SI-01**. It contains
the main application, domain, presentation, I/O, infrastructure, runtime and
Platform implementation that is shared by executable compositions. The name
`core` is an artifact/source boundary only: it does **not** reintroduce a
separate Core architecture layer in Figure SI01-01. The executable `app/`
module stays deliberately thin and adds the launcher, concrete runtime-provider
selection and packaging needed to run that core.

The Maven `groupId` remains the **event-timing software-system/product-family** coordinate. SI-01 Java code is more specific: the reusable application core and default executable live under `io.github.brainboxemb.eventtiming.timingpoint`. `TimingPoint` names the local software/deployment role; it does **not** replace the internal `TimingNode` domain aggregate. One Timing Point Application process may host 1..N TimingSystems and therefore multiple TimingNodes.

### Package direction

The current Java structure should grow from real code, not from the architecture
diagram.

Likely top-level packages are:

```text
io.github.brainboxemb.eventtiming/timingpoint/
  application/
  domain/
  platform/
    execution/
    events/
    environment/
  presentation/
    interfaces/
      api/
      console/
      shell/
      web/
    common/
      terminal/
  io/
    devices/
      antenna/
      display/
      keypad/
      beeper/
    devicenetworks/
      can/
      network/
    messaging/
    storage/
  infra/
    config/
    logging/
    loggingserver/
  runtime/
    config/
```

Presentation subpackages are organised by **functional interface first**. Console, Remote Shell, Web and API are separate presentation interfaces. The intended Web topology is one configured Web endpoint/binding per TimingNode (1..N), each with its own presentation port and a `TimingNodeId` reference. HTTP/WebSocket are implementation transports inside a functional interface, not global presentation categories. The primary API classes stay directly at `presentation.interfaces.api` while that component is small; a one-class `http`, `websocket` or `messages` package would hide the component overview without adding a useful boundary. `presentation.common.terminal` contains only terminal handling genuinely shared by Console and Remote Shell; `presentation.common` is not a generic dumping ground.

These are source-organisation boundaries, not automatically Maven modules.

Use these rules:

- create a class only when current behaviour needs it;
- keep small enums with the object that owns them until reuse justifies a
  separate type;
- do not create marker classes to represent layers;
- place a type by what it means, not by which layer happens to call it;
- keep primary component/capability classes visible at that component package
  root so opening the package gives a useful architecture overview;
- do not introduce a subpackage merely to classify one class by transport,
  message shape or implementation role;
- use a deeper subpackage for a cohesive supporting family when it materially
  improves navigation, or when multiple real sub-capabilities need their own
  namespace;
- preserve Java encapsulation when choosing package boundaries: subpackages do
  not share package-private access, so do not split implementation helpers only
  to make a tree look tidy if that would force a wider API;
- use capability-oriented subpackages when a domain concept has a main object plus
  closely related value/supporting types; keep that small group together rather
  than introducing generic `helper`, `model` or single-type `identity`
  subpackages;
- reserve `platform` for small JDK-only reusable primitives and execution-environment abstractions, including bounded/serial execution and typed local events;
- reserve `infra` for concrete cross-cutting technical support such as `BuildIdentity`, logging, diagnostics and configuration/extension adapters;
- reserve `runtime` for concrete application composition, the running application container and lifecycle;
- use `io` for external hardware, messaging and storage adapters.

The shared TimingData artifact has its own package root:

```text
shared/timing-data/
  io.github.brainboxemb.eventtiming.timingdata/
    TimingData.java
      AutomaticRegistration
      ManualRegistration
      ManualTimeSource
      RecordKey
    LocationId.java
    RegistrationId.java
    TimingTimestamp.java
    TimingDataFactory.java
      Context
    TimingDataCodec.java
      CodecException
    TimingDataProvider.java
    defaultprofile/
      DefaultTimingDataFactory.java
      DefaultTimingDataCodec.java
      private automatic/manual default value implementations
```

`TimingDataFactory.Context` is the one immutable value-only construction context for
fields shared by every TimingData variant. Do not mirror the semantic type tree
with `AutomaticRegistrationContext`, `ManualRegistrationContext` or nested
per-variant context types.

For example, the first TimingNode implementation is grouped as:

```text
application/
  ApplicationId.java
  UpstreamMessageRouter.java       when upstream messaging is implemented

domain/
  system/
    TimingSystem.java                   parent aggregate for 1..N TimingNodes
    TimingSystemId.java                 internal composition/simulation identity
    SystemStatus.java                   complete current TimingSystem overview
    UpstreamMessagePort.java            system-level upstream messages
    TimeSource.java                     per-system absolute time / test control
  timing/
    TimingNode.java
    TimingNodeId.java
    UpstreamMessagePort.java            TimingNode-level upstream messages
    NextUpTeams.java                    passive per-node state
    NextUpTeamsStore.java               persistence port for next-up analysis history
    StageStartTimes.java                passive per-node reference state
    StageStartTimesStore.java           persistence port for start-time analysis history
    RaceData.java                       passive per-node reference state
    RaceDataStore.java                  persistence port for race/reference analysis history
  logbook/
    LogBook.java                        passive committed TimingData history
  timingdata/
    TimingDataPersistence.java          TimingData-specific persistence contract
    DefaultTimingDataPersistence.java   TimingData codec/identity/sequence mapping
  upstream/
    UpstreamProtocol.java               TimingData + sync/reconcile/ping semantics
    UpstreamProtocolProvider.java       typed extension provider contract

io/
  devices/
    antenna/
      Antenna.java                      stable antenna contract
      AntennaProvider.java              typed extension provider contract
      SimulatedAntenna.java             built-in reference/simulation implementation
    display/
      DisplayProtocolProvider.java      typed protocol-extension provider contract
      Rev1CanDisplay.java               passive CAN display support when implemented
    keypad/                        only when device-specific code justifies it
    beeper/                         transport-specific implementation only when justified

  devicenetworks/
    can/
      CanNetworkController.java    CAN lifecycle, discovery and device state
      CanProtocolProvider.java     typed protocol-extension provider contract
    network/
      NetworkDeviceService.java    bidirectional network-device boundary

  messaging/
    UpstreamGateway.java            when upstream messaging is implemented
    Connector.java                 only if multiple transports justify a shared contract
    rabbitmq/
      RabbitMqConnector.java
      DebugConnector.java                 engineering/debug connector when implemented
  storage/
    AppendOnlyRecordStore.java             generic opaque-record storage contract
    FileAppendOnlyRecordStore.java         LF framing • file append/recovery
    # later generic lower-layer storage mechanisms only as real needs appear

platform/
  execution/
    SerialWorker.java                     bounded one-at-a-time execution primitive
  events/
    Event.java                            owner-side typed emit primitive
    EventSource.java                      subscription-only consumer view
  environment/                            low-level environment adapters only when real types justify them
```

The names above record ownership/direction, not a requirement to create empty
types early. Lower layers expose generic contracts that do not import higher
layers. TimingData-specific persistence semantics stay in Domain and use the
generic `io.storage.AppendOnlyRecordStore`; the file implementation remains
completely unaware of TimingData, TimingNode and Domain types.
`SerialWorker` is a small reusable execution primitive under `platform.execution`,
composed into TimingNode rather than used as a Domain superclass. It has no
TimingNode or persistence semantics of its own.

`TimingNode` remains the visible Domain component boundary used by higher layers. It owns serialized access through `SerialWorker`, operation admission/timeout mapping and post-commit event publication. Package-private `TimingNodeLogic` contains the mutable node state and domain decisions: lifecycle, current `LocationId`, LogBook interaction and TimingData commit behaviour. `TimingNodeLogic` is an implementation detail of the TimingNode component, not a second architecture component.

A production `TimingNode` is always constructed as a complete capability. `TimingDataPersistence`, `TimingDataFactory` and `TimeSource` are required constructor dependencies; there is no lifecycle-only or partially configured production node. The only non-public construction seam exists for deterministic TimingNode execution-boundary tests and is documented as test-only in code.

`TimingNodeTypes` is only a Java source-code grouping for the public TimingNode status/result/exception value types. It has no runtime state, lifecycle or architectural responsibility and therefore does not appear as another component in Figure SI01-01.

The application `CommandHandler` is always composed with a complete
`TimingNode`; there is no status-only or partially configured production
handler. Presentation tests use complete test fixtures rather than adding a
second production construction mode.

Status-change detection is owned by the same serial boundary. A state-changing
command compares authoritative status before and after the domain operation on
that TimingNode lane. A real difference emits the TimingNode status event before
the result leaves the ordered command execution. `CommandHandler` maps that fact
to `ApplicationStatus`; it does not perform a second before/after query outside
the ordered boundary.

The visible component boundary uses typed commands and queries rather than mirroring every `TimingNodeLogic` method:

```java
TimingNodeTypes.OpenResult opened =
        node.invoke(TimingNodeCommands.open());

TimingNodeTypes.CommandAdmission admitted =
        node.submit(
                TimingNodeCommands.commitAutomaticRegistration(
                        registrationId,
                        observationTime));

TimingNodeTypes.Status status =
        node.query(TimingNodeQueries.status());
```

`invoke(command)` is the result-bearing path: presentation/application callers may wait for the processed domain result. `submit(command)` is the producer path: it returns only immediate bounded-queue admission and deliberately does not wait for the later domain result. RFID/TagProcessor-style ingress uses this form so a device callback cannot be held up by persistence, LogBook work or another queued TimingNode operation.

`query(query)` is the consistency-sensitive read path. Short reads run in the same ordering as commands. The ordering boundary is the required property; a copied LogBook snapshot is not. Query implementations should avoid routine list copies when direct bounded traversal on the node lane is cheaper, and may introduce compact derived/indexed state only when measurement justifies it. Typed command/query objects are local operation descriptions, not another component, central dispatcher or generic message bus.

The commit boundary is named `commitAutomaticRegistration(...)`. The fact that the observation already passed source-specific interpretation/filtering is a precondition, not the operation name. The manual counterpart is `commitManualRegistration(...)`; the IF-03 engineering route may keep its separate short `auto-reg` resource name. `ApplicationId`, internal `TimingSystemId` and functional
`TimingNodeId` are separate Java identities. `TimingSystemId` distinguishes
multiple hosted/simulated systems locally; it is not automatically serialized
into TimingData or exposed as an upstream address.

Each `TimingSystem` owns one Domain `TimeSource`. The production implementation
may delegate to a Platform wall-clock abstraction; tests/simulations may provide
a controllable implementation with a per-system offset or stepped time. The
Domain contract returns project-owned absolute `TimingTimestamp` values rather
than exposing a platform clock API directly. Monotonic duration/time-out sources
remain separate Platform/runtime concerns.

The I/O package structure is logical; executable composition is per
`TimingSystem`. Hosting 1..N TimingSystems therefore normally constructs 1..N
corresponding I/O compositions, each with its own configured Storage, Devices,
Messaging and DeviceNetworks objects. Explicit lower-level multiplexing may share
a physical resource, but the owning TimingSystem contexts stay separate.

`CanNetworkController` owns CAN-network lifecycle/discovery and CAN-device
communication. `NetworkDeviceService` owns the general bidirectional
network-device boundary. It may expose application data outward and accept
device-originated messages/events inward.

The high-level architecture deliberately stops there. Service discovery,
connection/listener/session handling and protocol framing are lower-level design
concerns below `NetworkDeviceService`. Likewise, a smart-display/domain handler
should not acquire socket, mDNS or transport knowledge merely because it is
reached through this service. The smart display remains an external client and
therefore does not require a `Rev2WifiDisplay` class inside SI-01 merely to
mirror the hardware name.

`TimingNode` contains its passive `LogBook` as part of the TimingNode
aggregate. LogBook keeps 0..N committed `TimingData` values. The current
design deliberately avoids a second logbook-specific record type because there
is no different domain shape that needs one.

`TimingData` remains the Domain capability/contract name and becomes the small
shared Java interface implemented by concrete profile values. The default profile
and validation/codec services realise the system-owned IF-05 contract. Concrete
storage, Web and messaging adapters may carry that record or its encoded form
without redefining field semantics.

`UpstreamProtocol` is a Domain capability owned by one `TimingSystem` and built partly on `TimingData`. It adds synchronization/reconciliation and protocol-level messages such as ping/pong so individual TimingNodes do not need to implement those concerns. `UpstreamGateway` owns the external transport boundary and uses 1..N concrete connectors. A connector such as `RabbitMqConnector` or `DebugConnector` owns transport/session mechanics, not TimingData or UpstreamProtocol semantics. `DebugConnector` is the engineering transport intended for an independent desktop/debug tool; that tool remains an external consumer rather than part of SI-01. `UpstreamMessageRouter` resolves semantic work inside the already selected TimingSystem context: system-level work uses `TimingSystem.UpstreamMessagePort`, while node-level work is resolved by `TimingNodeId` to `TimingNode.UpstreamMessagePort`. `TimingSystemId` is not required on the wire.

If the TimingNode capability later grows into several cohesive areas, deeper
packages such as `timing/registration` or `timing/stage` may become useful.
Do not create those packages before the corresponding code exists.

The Domain-level `SystemStatus` is a dedicated component contained by one `TimingSystem`. It is a semantic aggregate, not a wrapper around
concrete adapter objects and not merely an `OK` flag. It can represent current
TimingNode state together with operational I/O state such as antenna/display
connectivity, keypad/beeper availability, device-network health, storage,
upstream connectivity and synchronisation. Concrete I/O components expose or
publish semantic status inputs; `SystemStatus` must not depend on classes such
as `Rev1CanDisplay`, socket/session implementations or vendor antenna drivers.

TimingNode status reaches this aggregate as an immutable semantic snapshot/result
created through the TimingNode ownership boundary. `SystemStatus` does not call
into `LogBook`, lifecycle fields, location fields or other mutable TimingNode
internals directly.

An external interface response shape does not require an equally shaped internal Java object.
For example, the status JSON does not by itself require classes named
`ApplicationStatusSnapshot` or `ApplicationStatusModel`.

### Contract placement

Place contracts with the responsibility that owns their meaning:

```text
presentation
  functional client interfaces / transport mapping / wire messages

application
  commands, queries and application-level ports

domain
  domain model, semantic ports, per-TimingSystem TimeSource, TimingData representation/codec and UpstreamProtocol semantics

io
  hardware, messaging and storage adapters

infra
  concrete cross-cutting technical support, including logging, diagnostics,
  configuration mapping and extension discovery

runtime
  concrete application composition, top-level running application and lifecycle

platform
  small JDK-only reusable primitives and execution-environment abstractions,
  including serial execution and local typed events
```

Do not create one generic top-level `api` package merely to collect
interfaces.

### Internal dependency direction

```text
presentation --> application
application  --> domain / I/O / platform
domain       --> I/O / platform
io           --> platform / JDK
runtime      --> application / domain / presentation / I/O / infra / platform
infra        --> owned support contracts + platform / JDK / selected support libraries
platform     --> JDK and low-level environment only
```

The normal dependency direction follows the layer order and is intentionally
easy to read from imports. A lower layer does not import a higher layer merely
to implement one of its interfaces. Domain may depend on a generic I/O contract,
but not on a concrete I/O implementation; Runtime composition selects the
concrete implementation.

For example:

```text
TimingNodeLogic
  -> TimingDataPersistence
       -> AppendOnlyRecordStore
            <- FileAppendOnlyRecordStore selected by Runtime
```

`AppendOnlyRecordStore` contains only opaque-record storage semantics.
`DefaultTimingDataPersistence` owns TimingData codec, TimingNodeId and sequence
validation. This keeps `io.storage` independent from Domain.
Executable composition may depend on the complete supported application-core surface
and selected external libraries.

### Logging dependency placement

Logging follows the same library-versus-executable composition boundary.

```text
timing-point-core.jar
  -> slf4j-api only
  -> io.github.brainboxemb.eventtiming.timingpoint.infra.logging
       +-- Logging
       +-- LoggingConfig / LoggingLevel / LoggingFileConfig
       +-- LoggingControl
       +-- ConsoleHandler
       +-- TimestampedFileLogHandler + CompactLogFormatter
  -> io.github.brainboxemb.eventtiming.timingpoint.infra.loggingserver
       +-- LoggingServer
       +-- LoggingServerConfig
       +-- LiveLogHandler
       +-- client-initiated live diagnostics + temporary level control

timing-point-app.jar
  -> selects exactly one SLF4J provider
  -> initial provider: slf4j-jdk14
  -> delegates SLF4J records to java.util.logging
  -> starts/stops core-provided Logging
  -> independently starts/stops optional LoggingServer
```

Working rules:

- application-core code may compile against the SLF4J API but must not force a concrete provider/backend on consumers;
- provider-neutral deployment values stay component-owned: `LoggingConfig` contains `LoggingLevel` and `LoggingFileConfig`; optional `LoggingServerConfig` belongs to `LoggingServer`; runtime `Config` may reference both as composition data;
- the executable application chooses and configures the provider/backend before `runtime.Composition` starts normal application composition;
- the initial Java-8/Pi-Zero baseline uses `slf4j-jdk14` so the provider delegates to JDK `java.util.logging` without introducing Logback;
- concrete JUL backend/file lifecycle stays under `timingpoint.infra.logging`; the live diagnostics handler/socket lifecycle stays under `timingpoint.infra.loggingserver`; neither package defines domain/application contracts;
- `infra.logging` must not depend on `infra.loggingserver` or `runtime.config`; the thin executable starts the two infrastructure components separately before handing control to runtime composition. `infra.loggingserver` may depend on the narrow public `Logging` runtime surface for current level control and record formatting, but the logging component does not construct or own the server;
- `LoggingServerConfig` belongs to the `LoggingServer` component and carries its listener values (`bindAddress`, `port`); the default YAML loader maps the external `logging.live` syntax to that component-owned type;
- `LoggingLevel` is a logging-domain value rather than `LoggingConfig.Level`, so live level control does not depend on an umbrella configuration class;
- the core artifact owns that reusable implementation because it has no dependency on executable-specific YAML/resource loading and uses only JDK facilities plus component-owned logging configuration;
- `Logging` is the primary runtime logging infrastructure component and owns backend setup, console/file handler composition, record formatting and the current global-level control;
- `LoggingServer` is the separate externally reachable live-diagnostics component; it owns the live JUL handler plus logging-specific socket/protocol boundary, delegates temporary level changes to `Logging`, and is not a Presentation/IF-03 endpoint;
- the default retained file sink uses the local wall-clock start/rotation timestamp as a human-readable filename, normally `yyyyMMdd-HHmmss.txt`; this timestamp is not treated as a unique or monotonic session identity;
- Raspberry Pi startup must not assume that wall-clock time is already network-synchronised: the clock may repeat or move backwards across restarts, so retained log creation must use non-overwriting create semantics, add a collision suffix when necessary, and protect the active log from retention decisions regardless of timestamp ordering;
- retained text records use the compact operator-facing form `HH:mm:ss.SSS - [LEVEL] - message - [sourceClass.sourceMethod]`; exception stack traces follow the record line when present;
- `LoggingControl` owns the configured global level plus an optional temporary runtime override; applying an override changes the running logger threshold without mutating deployment configuration;
- the optional diagnostic listener is a logging-specific engineering facility. The test client initiates its TCP connection, log delivery is best effort, and network failure must not be allowed to block ordinary log publishers;
- the live diagnostics protocol is separate from the IF-03 status/event wire model;
- another executable/private consumer may select another compatible provider later without changing core/domain source;
- exactly one provider should be present in a runtime composition;
- provider/backend versions are pinned centrally by Maven dependency management rather than scattered through modules.

This keeps provider selection replaceable at the executable boundary while allowing the reusable
application core to provide the default JUL logging infrastructure and its configuration contract.

### Default executable application

`timing-point-app` is the first executable consumer of the application-core library.

Its executable package is deliberately thin:

```text
io.github.brainboxemb.eventtiming.timingpoint.app/
  Main.java
```

The application core owns the reusable SI-01 runtime and supporting infrastructure:

```text
io.github.brainboxemb.eventtiming/timingpoint/
  runtime/
    Application.java
    Composition.java
    Lifecycle.java
    config/
      Config.java
      Presentation.java
      Api.java
      YamlLoader.java
  infra/
    BuildIdentity.java
    EmbeddedBuildIdentityLoader.java
    logging/
      Logging.java
      LoggingConfig.java
      LoggingLevel.java
      LoggingFileConfig.java
      LoggingControl.java
      TimestampedFileLogHandler.java
      CompactLogFormatter.java
    loggingserver/
      LoggingServer.java
      LoggingServerConfig.java
      LiveLogHandler.java
```

`runtime/` owns knowledge of the concrete running application: `Application`, `Composition`, `Lifecycle` and the effective composition configuration. Figure SI01-01 shows this explicitly as the **Runtime** block. Runtime is not another business/domain layer; it is where the executable object graph is assembled and its lifecycle is coordinated.

The package namespace carries the context, so runtime class names stay short. There is no second bootstrap component and no `Application.Builder`: `Composition` constructs the current application graph directly. Presentation, I/O, Platform and Infrastructure objects keep their own architectural ownership even when runtime composition creates or starts them.

The executable artifact remains deliberately thin. Its launcher/input adapter stays under `...eventtiming.app`; reusable logging remains Infrastructure support. The IF-11 YAML mapper stays with `runtime.config` because it knows the concrete runtime configuration schema.

```text
timing-point-core.jar
  io.github.brainboxemb.eventtiming.timingpoint.infra/
    BuildIdentity.java
    EmbeddedBuildIdentityLoader.java

  io.github.brainboxemb.eventtiming.timingpoint.runtime/
    Application.java
    Composition.java
    Lifecycle.java
    config/
      Config.java
      Presentation.java
      Api.java
      YamlLoader.java

timing-point-app.jar
  io.github.brainboxemb.eventtiming.timingpoint.app/
    Main.java
```

`timing-point-core.jar` contains the JUL-based default logging infrastructure but still does **not** select an SLF4J provider. Provider selection remains an executable-composition concern: the default app contributes `slf4j-jdk14` at runtime, while another consumer may choose another compatible composition and omit the default `Logging` component.

The target executable startup/configuration flow is:

```text
main()
  -> core EmbeddedBuildIdentityLoader
       -> executable-provided filtered build resource
  -> configuration resolution
       -> selected built-in application-profile defaults
       -> selected platform defaults
       -> selected operating-mode defaults
       -> explicit IF-11 YAML deployment overrides
       -> secret resolution
       -> validated effective runtime Config
  -> Logging
       -> configure JUL level + console/file handlers
  -> optional LoggingServer
       -> attach live handler + diagnostics listener
       -> use Logging for current level / common formatting
  -> core runtime.Composition
       -> select/construct concrete presentation/I/O/platform/infra objects
       -> create reusable application/domain/runtime objects
       -> install/start presentation and shutdown handling
  -> runtime.Application
```

The current `runtime.config.YamlLoader` implements only the explicit
YAML subset already needed by the running application. Profile/platform/mode
resolution is the next configuration responsibility; the architecture does not
require a new public Java type for each source before that behaviour is
implemented.

`BuildIdentity` and runtime `Config` are different inputs. Build identity is artifact provenance; application configuration is deployment composition defined by IF-11. The executable embeds deterministic provenance fields (`application`, `version`, exact `revision`, `sourceRef`, `buildOrigin`, `dirty`, `apiVersion`). Wall-clock build time, CI run/build id and actor/user are not embedded because they are per-run metadata rather than stable build inputs/context.

Reusable application behaviour should not migrate into the executable merely because the architectural responsibility is called `application`. When a reusable application-core runtime object becomes justified by real shared behaviour, executables should **compose** that object rather than extend a `BaseApplication` hierarchy.

The application core uses one explicit runtime composition boundary. There is no builder layered on top of another bootstrap object. `runtime.Composition` constructs the current graph and returns/starts `runtime.Application`.

The default IF-11 file syntax is YAML and its parser/mapping stays beside the effective runtime configuration model. `runtime.config.YamlLoader` maps external YAML into `runtime.config.Config`; it is not a generic Infrastructure YAML utility. As profile support is implemented, configuration support resolves built-in profile/platform/mode defaults plus explicit deployment YAML before runtime composition starts.

The resolver responsibility must remain data/composition oriented:

- application profiles are data/default templates, not Java subclasses;
- do not introduce profile-specific Application subclasses or a
  profile-specific domain hierarchy;
- profile defaults may select topology/cardinality and capability defaults;
- platform defaults may select environment-specific values;
- operating-mode defaults may replace real providers with simulated providers;
- explicit IF-11 deployment values have highest non-secret precedence;
- `runtime.Composition` consumes only the resolved/validated runtime `Config` and contains no profile-name switches.

SnakeYAML is therefore an application-core implementation dependency; the IF-11 contract
remains independent of SnakeYAML APIs and another input adapter may construct the
same typed effective runtime `Config` without YAML.

Build-identity interpretation is reusable for the same reason. The application core owns
`BuildIdentity` and `EmbeddedBuildIdentityLoader`. The concrete executable still owns
the filtered `event-timing-build.properties` resource and build-time provenance injection,
because those values identify that executable artifact. The core loader only interprets
the classpath resource and has no dependency on `app.Main` or another app class.

The implemented presentation structure is:

```text
presentation/
  interfaces/
    console/
      LocalConsole
    shell/
      RemoteShellServer
    api/
      HttpEndpoint
      WebSocketEndpoint
      MessageWriter
  common/
    terminal/
      TerminalSession
```

Console and remote shell are separate presentation interfaces. They share only the
line-oriented command-session behaviour in `presentation.common.terminal`; both call
the same `CommandHandler` and shutdown callback.

Console, Remote Shell and API are baseline Timing Point Application capabilities.
Application profiles do not add/remove or redefine their command/status semantics.
Concrete network listener bindings remain deployment configuration, so a listener
may still be explicitly left unbound/disabled without creating another profile.

A06/A07 are the first slice of the functional **API**:

```text
HttpEndpoint
  +-- GET /api/v1/version
  +-- GET /api/v1/status
            \
             +--> CommandHandler.version() / status()
            /
WebSocketEndpoint
  +-- WS /api/v1/events
  +-- STATUS_SNAPSHOT on connect/reconnect
  +-- STATUS_CHANGED only for real status changes
```

`MessageWriter` owns the IF-03 wire/JSON representation shared by the Remote
API HTTP and WebSocket transports. It is not application/control logic and therefore
does not live in the application layer or in global presentation common code.

The local class names deliberately omit the `Api` prefix because the enclosing `presentation.interfaces.api` package already supplies that functional context. `Endpoint` is used rather than `Server` for the transport-facing classes; in particular, `HttpServer` is avoided because the implementation uses `com.sun.net.httpserver.HttpServer` internally.

The first WebSocket implementation uses `Java-WebSocket 1.6.0` in the reusable
application core and keeps the accepted A06 JDK HTTP server unchanged rather than replacing
both transports with a larger combined stack.

A browser-based engineering client, if added, should consume the API like any other external client. It does not require a separate SI-01 `presentation.web` package.

Manual inspection is provided by an independent development tool:

```text
test-client/
  TestClientApplication      plain Java launcher
          |
          v
  TestClientFxApplication    JavaFX development view
          |
          +-- ApiClient          HTTP/JSON client
          +-- ApiEventClient       Java 17 WebSocket client
          +-- RemoteShellClient          A05 raw TCP shell client
          |
          v
        SI-01
```

`test-client/` is a standalone Java-17 application and does not depend on
`timing-point-core` or `timing-point-app` implementation code. It may,
however, depend on the separately reusable `event-timing-data` artifact because
TimingData codec/provider reuse is now a real cross-executable requirement. This
preserves the external-client boundary while allowing SI-01 and the Engineering
Client to exercise the exact same public or proprietary TimingData translator.

The Engineering Client remains engineering support rather than the planned SI-02
GUI, and its JavaFX choice does not select the SI-02 GUI technology.

The shared presentation/application boundary remains small:
`CommandHandler.version()` returns build identity and
`CommandHandler.status()` obtains the current TimingNode status through the
TimingNode query/ownership boundary used by the current presentation adapters;
it does not assemble status by reading node-owned fields directly.

### TimingNode active-object execution and persistence

The Java design implements the **Active Object pattern** for each TimingNode,
but does not make `TimingNode` inherit from an `ActiveObject` base class.

The architectural rule is simple:

```text
TimingNode
  +-- one bounded serial execution boundary
  +-- one worker active at a time
  |
  +-- passive LogBook
  +-- passive NextUpTeams
  +-- passive StageStartTimes
  +-- passive RaceData
  |
  +-- per-type store ports
```

This gives one writer for all mutable per-node state and one clear ordering
between registration, lifecycle, next-up and reference-data changes.

#### Why composition instead of an ActiveObject base class

A reusable base class such as `TimingNode extends ActiveObject<Work>` is
possible, but it would couple the domain type to one threading mechanism.
Composition keeps that choice replaceable and lets the public TimingNode API stay
synchronous and domain-oriented.

For state-dependent operations the caller waits for the result produced on the
TimingNode lane. Queue admission and the processed operation result are represented
separately:

```java
final class TimingNode {
    private final TimingNodeLogic logic;
    private final SerialWorker serialWorker;

    <R> R invoke(TimingNodeCommand<R> command) {
        // admit + wait for the processed result
    }

    CommandAdmission submit(TimingNodeCommand<?> command) {
        // admit only; producer returns immediately
    }

    <R> R query(TimingNodeQuery<R> query) {
        // ordered consistency-sensitive read
    }
}

final class TimingNodeLogic {
    private Lifecycle lifecycle = Lifecycle.CLOSED;
    private LocationId locationId;
    private final LogBook logBook;

    OpenResult open() {
        // domain decision only; no queue/future/timeout mechanics here
    }
}
```

The visible `TimingNode` keeps execution mechanics around the component boundary, while `TimingNodeLogic` keeps the stateful domain behaviour readable. Queue admission and the processed domain result remain separate; moving the mutable logic out of the boundary does not make `TimingNodeLogic` externally addressable.

The public methods above are illustrative signatures, not a requirement to use
those exact result class names. The important split is:

```text
open / close / setLocation / consistency-sensitive query
    -> queued internally
    -> execute against current ordered TimingNode state
    -> caller receives processed domain result

device/callback ingress that is explicitly submission-only
    -> bounded queue admission result
    -> callback may continue immediately
    -> later processing has no synchronous caller waiting for its domain result
```

A queue-admission result is never used as a substitute for the domain result of
a state-dependent command.

The Future used to connect the queued work with a waiting caller is an internal
Active Object mechanism. It does not appear in the normal TimingNode
application/domain interface. In Java 8 a plain `Future<R>` is sufficient for
this first design; `CompletionStage` is not required by the current synchronous
caller contract.

Code already running on the TimingNode lane uses direct private/domain methods
such as `doOpen()` rather than calling the blocking public `open()` method
again. Re-entering a public blocking operation from the same serial lane would
wait on work that cannot run until the current work item finishes.

#### Operation results and execution failures

Keep domain outcomes separate from failures of the execution boundary.

For example:

```text
OpenResult
  OPENED
  ALREADY_OPEN
  NO_LOCATION

submission/execution failure
  queue full
  node stopping/unavailable
  unexpected internal failure

wait timeout
  caller stopped waiting
  operation may still be queued or executing
  final domain outcome is unknown to that caller
```

A domain rejection such as `NO_LOCATION` is a normal processed result. Queue
full or a stopping worker means the operation was not admitted and belongs to an
operation/execution exception rather than `OpenResult`.

A timeout is different again. It means only that the caller did not receive the
processed result within the configured guard time. TimingNode timeout handling
must not automatically cancel or interrupt an already accepted state change.
The caller must treat the final outcome as unknown and re-query/reconcile state
before assuming that the command did not happen.

The first implementation may expose a small TimingNode-specific exception family
rather than leaking `TimeoutException`, `ExecutionException` or
`InterruptedException` from `java.util.concurrent` through the domain API.
Keep that family small and add distinct exception types only where callers need
different recovery behaviour. Timeout is a useful distinct case because its
outcome semantics differ from definite submission rejection.

#### First SerialWorker implementation

The first implementation remains a small composed worker backed by one bounded
queue and one dedicated thread. Its public result types make the two result
moments explicit:

Project-owned SI-01 runtime threads use the diagnostic name form
`tp-<owner>-<role>[-<identity>]`. The prefix makes Timing Point Application
threads easy to separate from JDK, Maven/JGit and third-party library threads in
a debugger, profiler or thread dump. The owner abbreviations used by the current
runtime are `prl` (Presentation), `dml` (Domain), `inf` (Infrastructure) and
`run` (Runtime/composition).

Examples:

```text
tp-prl-console
tp-prl-api-http
tp-prl-remote-shell
tp-inf-live-log
tp-inf-live-log-writer
tp-run-shutdown
tp-dml-node-<NodeId>
```

Name a thread for the functional component that owns the work, not merely the
low-level helper that allocates the Java `Thread`. The TimingNode serial lane is
therefore `tp-dml-node-<NodeId>` even though `SerialWorker` is a Platform
primitive. The final suffix is the configured NodeId, not a worker/index number.
Threads owned by the JDK or external libraries keep their own names.

```java
final class SerialWorker implements AutoCloseable {
    enum AdmissionResult {
        ACCEPTED,
        FULL,
        NOT_RUNNING
    }

    static final class SubmitResult<R> {
        AdmissionResult admission();
        Future<R> futureResult();
    }

    <R> SubmitResult<R> submit(Callable<R> work) {
        // Non-blocking queue admission.
        // futureResult() exists only when admission() == ACCEPTED.
    }

    AdmissionResult offer(Runnable work) {
        // Submission-only producer path: queue admission is the only result.
    }
}
```

Usage rules:

- `AdmissionResult` answers only whether the bounded serial lane accepted the
  work item;
- `SubmitResult.futureResult()` is the Java `Future<R>` for the later
  processed result and is available only for accepted work;
- a successful `ACCEPTED` admission must never be interpreted as a successful
  domain operation;
- `offer(Runnable)` is reserved for producer paths that intentionally need no
  synchronous processed result;
- result-bearing TimingNode operations normally convert FULL/NOT_RUNNING into
  their small operation/execution failure model, then wait on the Future with
  the configured guard timeout.

The TimingNode wrapper exposes the same distinction semantically:

- `invoke(command)` uses the result-bearing `SerialWorker.submit(Callable)` path;
- `submit(command)` uses the admission-only `SerialWorker.offer(Runnable)` path;
- ordinary submission-only command failures occur after the producer has returned and therefore must be reported through diagnostics/status rather than silently disappearing;
- `query(query)` is result-bearing and normally uses the same ordered lane for consistency-sensitive reads.

The concrete internal queue/task implementation and shutdown-loop details may
change. The required behaviour is:

- queue capacity is visible and bounded;
- FIFO order is preserved for one TimingNode;
- at most one work item for that TimingNode executes at a time;
- state-dependent validation happens in that ordered execution context;
- result-bearing work has an internal Future that is completed by execution;
- submission-only ingress can observe definite queue admission without waiting
  for later domain processing;
- one ordinary work-item failure must not silently kill the worker;
- an unexpected failure is reported and completes a waiting operation as a
  technical failure; the worker may continue only when TimingNode state is known
  to remain consistent;
- shutdown stops new admission first and lets already accepted work drain within
  the controlled shutdown policy.

The worker starts only after the TimingNode has completed construction/recovery
and before the node is exposed for normal operation. During controlled shutdown,
new work is rejected before the worker drains accepted work and stops. An
operation waiting for a result may therefore complete normally during draining;
an operation that cannot be admitted because shutdown has started fails
immediately as unavailable.

Do **not** use `Executors.newSingleThreadExecutor()` for this boundary: its
normal work queue is unbounded and hides the overload behaviour we need to
control.

A `ThreadPoolExecutor` configured with one thread and an
`ArrayBlockingQueue` can implement the same semantics. It remains a valid
alternative, especially if several TimingNodes later share a small executor.
The first dedicated `SerialWorker` is chosen for transparency, not because the
JDK executor framework is unsuitable.

If the implementation later moves to a shared executor, these invariants remain:

```text
per TimingNode:
  FIFO order
  at most one work item executing
  bounded queued work
  visible overload
  Future result corresponds to execution on that ordered lane
```

#### TimingData commit

The queue does not contain a pre-numbered TimingData record. Sequence is chosen
on the worker immediately before persistence:

```java
private void processRegistration(RegistrationInput input) {
    long sequence = logBook.nextSequence();

    TimingDataFactory.Context context =
        timingDataContext(sequence, activeLocationId, input.effectiveTime(), timeSource.now());

    RegistrationId registrationId = raceData.resolveRegistrationId(input);

    TimingData data;
    if (input.isAutomatic()) {
        data = timingDataFactory.createAutomaticRegistration(context, registrationId);
    } else {
        data = timingDataFactory.createManualRegistration(
                context, registrationId, input.timeSource());
    }

    timingDataStore.append(data);    // durable before return
    logBook.add(data);               // committed domain state
    newTimingDataEvent.emit(data);
}
```

Only the TimingNode worker calls this commit path, so a producer lock around
sequence allocation is unnecessary.

`LogBook.nextSequence()` reads committed state and does not consume the value.
If append fails, LogBook is unchanged and retry uses the same next sequence. The
worker must not process a later timing record ahead of that failed record.

#### Passive LogBook and TimingNode-owned reads

`LogBook` has no worker thread. It stores immutable `TimingData` values,
but it is contained mutable TimingNode state rather than a globally readable
repository.

Code outside the TimingNode ownership boundary does not read the mutable
LogBook list directly. A consistency-sensitive query enters the TimingNode lane
and performs its bounded read in the same ordering as state changes.

The read representation is deliberately not fixed to a copied list. The current
Step-4 bounded IF-03 range/latest implementation traverses the owned LogBook
records directly on the TimingNode lane and builds only the final response
representation; no temporary LogBook `List` copy escapes the owner. Network
write/send remains outside the TimingNode lane.

For future range/latest/ranking-style access, prefer direct bounded traversal of
the owned records when that avoids unnecessary allocation and GC pressure. A query may
instead use compact derived/indexed state, reusable scratch storage or a copied
view when measurements show that approach is cheaper overall.

The important guarantees are:

- each consistency-sensitive read has a defined place in the same ordering as
  state changes;
- no external consumer retains a mutable collection owned by TimingNode;
- long or blocking I/O work does not execute on the TimingNode lane;
- read strategy is selected from measured CPU, allocation/GC and lane-occupancy
  behaviour rather than convenience alone.

A high-frequency status/read path may later use a worker-published immutable
snapshot when measurement justifies it. Such a published snapshot is an
explicit read model with known freshness semantics, not permission for callers
to read TimingNode-owned mutable objects directly.

#### Per-type stores

Use a separate persistence boundary for each state type whose history/snapshots
need to be kept:

| Store | First purpose | Commit role |
| --- | --- | --- |
| `TimingDataPersistence` | append/load canonical TimingData | durable append is required before LogBook visibility; source for LogBook rebuild |
| future per-type persistence components | preserve accepted analysis history/snapshots | do not make the lower storage layer own domain semantics |

The lower I/O layer exposes storage mechanics rather than domain-specific store
interfaces. The first implementation uses:

```text
Domain
  DefaultTimingDataPersistence
    - TimingDataCodec
    - TimingNodeId validation
    - sequence validation
           |
           v
I/O
  AppendOnlyRecordStore
           ^
           |
  FileAppendOnlyRecordStore
    - LF/CRLF framing
    - incomplete-tail repair
    - directory/file handling
    - FileChannel.force(true)
```

Runtime composition creates the file store and supplies it to
`DefaultTimingDataPersistence`. No class under `io.storage` imports a Domain
or Application class.

The TimingNode worker fixes the order in which state changes execute against the node-owned state. The
first implementation may call the small/infrequent analysis-store writes on the
same worker. If measurements show that one of those writes delays registrations,
the worker can hand an immutable snapshot to a bounded storage executor. Do not
add one thread per state object and do not introduce an unbounded background
queue.

For the first registration path, synchronous persistence on the node lane is an accepted design trade-off because producer callbacks do not wait for that work: they return after command admission. The remaining risk is queue growth and increased command latency when storage stalls. Measure store latency, queue high-water and registration burst behaviour before moving durability work off-lane; any later asynchronous persistence design must preserve the commit-before-LogBook/event ordering contract.

For example, a StageStartTimes update may be:

```text
TimingNode worker
  -> validate received snapshot
  -> replace StageStartTimes live state
  -> StageStartTimesStore.append(snapshot for analysis)
```

After a reboot, the live protocol can send the current StageStartTimes again
(for example as part of OPEN handling). The historical file is still retained
for analysis.

#### Simple typed events

Post-fact notifications use a small local `Event<T>` abstraction rather than a
central event bus. The reusable mechanism lives under `platform.events` because it
is a small JDK-only reusable primitive rather than domain semantics, external I/O
or concrete infrastructure.

Conceptually:

```java
interface EventSource<T> {
    boolean subscribe(Consumer<T> listener);
    boolean unsubscribe(Consumer<T> listener);
}

final class Event<T> implements EventSource<T> {
    DeliveryReport emit(T value);
}
```

A component owns the mutable `Event<T>` instance and is the only code that emits
the fact. Consumers receive an `EventSource<T>` subscription-only view, so they
subscribe directly without gaining permission to publish the event.

For TimingData the component owns:

```java
private final Event<TimingData> newTimingDataEvent = new Event<>();

public EventSource<TimingData> newTimingData() {
    return newTimingDataEvent;
}
```

The commit path is therefore:

```text
TimingNode serial lane
  -> persist TimingData
  -> update committed LogBook state
  -> newTimingDataEvent.emit(timingData)
       |
       +--> subscribed listener
       +--> subscribed listener
```

The first design has no central dispatcher or string/topic routing; listeners subscribe directly to the exposed event source they need.

The event says that new TimingData is now available. The fact that
`newTimingDataEvent` is emitted only after successful persistence and LogBook
update is part of the event contract; it does not need to be encoded in a longer
event name.

Listeners must not become alternate owners of TimingNode mutable state. Slow
network delivery or retry work must also not block the TimingNode serial lane;
a listener that needs such work hands the TimingData value to its own bounded
execution/delivery mechanism.

The `Event<T>` listener registry is thread-safe and uses snapshot iteration, so
subscribe/unsubscribe may race safely with delivery. Delivery itself is
synchronous on the emitting thread and `Event<T>` does not serialize concurrent
`emit(...)` calls. An owner that requires ordering or non-overlapping callbacks
must emit from its own ordered execution boundary. TimingNode status-change and
committed-TimingData events are therefore emitted from the TimingNode serial
lane.

This is part of the same ingress/latency risk analysis: a synchronous local listener is acceptable only when it is demonstrably short and non-blocking. A WebSocket or other transport adapter must enqueue/buffer its outbound work and return quickly, or introduce its own bounded delivery executor. The TimingNode lane is not a network backpressure mechanism.

If listener notification fails after the record is committed, that does not
roll back the TimingData commit. A consumer that needs reliable recovery uses
authoritative persisted/LogBook state and its own reconciliation/delivery
mechanism.

Other local events may use the same `Event<T>` abstraction when a real consumer
needs them. Do not introduce events merely to replace ordinary direct method
calls.

#### Multiple TimingNodes

The semantic requirement is one serial execution lane per TimingNode, not
permanently one operating-system thread per node.

For the first one-node application:

```text
1 TimingNode
  -> 1 SerialWorker
       -> 1 bounded queue
       -> 1 dedicated worker thread
  -> passive state objects
  -> store dependencies
```

If a later multi-node application shows that one thread per node is too
expensive, multiple SerialWorkers may share a small executor while preserving
the per-node invariants above.

#### Raspberry-Pi implementation rules

For the initial Pi-oriented runtime:

- keep each TimingNode work queue bounded;
- prefer explicit bounded queues over hidden/unbounded executor queues;
- keep contained domain state passive and single-writer where practical;
- keep concrete TimingData values immutable after creation;
- avoid routine LogBook list copies or deep copies when direct bounded traversal is sufficient;
- consider reusable scratch storage, compact indexes or incremental derived state only when measurement shows a clear benefit;
- move blocking network/retry work behind capability-specific output boundaries;
- add asynchronous analysis-store writing only when measurement justifies it;
- measure queue high-water, store latency, LogBook copy time, heap/GC behaviour
  and query latency before increasing concurrency.

### Shared TimingData library and concrete profiles

Both SI-01 and the Engineering Client need common TimingData contracts without
depending on the whole SI-01 application core. The shared artifact therefore
owns the semantic interfaces and value types that every supported TimingData
profile must implement; it does **not** require one concrete record class for all
profiles.

The first traced Java semantic model is intentionally small:

```text
shared/timing-data
  TimingData
    common TimingNodeId / sequence / LocationId / time access
    AutomaticRegistration
      RegistrationId
    ManualRegistration
      RegistrationId
      ManualTimeSource
    ManualTimeSource
    RecordKey
  LocationId
  RegistrationId
  TimingTimestamp
  TimingDataFactory
    Context
  TimingDataCodec
    CodecException
  TimingDataProvider

default profile
  DefaultTimingDataFactory
    private automatic/manual immutable implementations
  DefaultTimingDataCodec

test / product-specific profile
  DummyEventTimingDataFactory
    private profile-specific immutable implementations
  DummyEventTimingDataCodec
```

There is no intermediate public `RegistrationData` interface. Automatic and
manual registration are already the useful type-safe variants, so another level
would add hierarchy without giving callers a stronger contract.

`LocationId` and `RegistrationId` are standalone shared value types because
they are used at boundaries beyond one concrete TimingData subtype. They define
stable Java/IF-05 representations and only minimal structural validity. Concrete
event/profile/reference-data meaning and allowed values remain outside the shared
library.

Likewise, `TimingNodeStateData` and `RegistrationRevokedData` are not created
from old record-enum values. UC-002 still defers OPEN/CLOSE-as-TimingData and the
current use-case baseline does not require revocation. Add those semantic types
only after a promoted requirement justifies them.

The semantic interfaces are common. A configured profile supplies simple
immutable implementing classes:

```java
TimingData.AutomaticRegistration automatic =
        timingDataFactory.createAutomaticRegistration(context, registrationId);

TimingData.ManualRegistration manual =
        timingDataFactory.createManualRegistration(
                context, registrationId, TimingData.ManualTimeSource.OPERATOR_ENTERED);
```

The return types preserve variant type safety even when the configured provider
returns a different concrete implementation.

#### Stateless TimingData factory

`TimingDataFactory` is a stateless construction service. It does not validate
TimingNode lifecycle policy, allocate sequence numbers, resolve `TagId` or
`TeamId`, commit data, own a LogBook or publish events. Those responsibilities
stay with the TimingNode and its contained domain components.

Source/reference resolution happens before factory construction:

```text
TagId  -----> RaceData ----\
                         +--> RegistrationId
TeamId -----> RaceData ----/
```

The factory receives the already selected common construction values in one
generic context and only the extra values required by the requested variant:

```java
TimingData.AutomaticRegistration createAutomaticRegistration(
        TimingDataFactory.Context context,
        RegistrationId registrationId);

TimingData.ManualRegistration createManualRegistration(
        TimingDataFactory.Context context,
        RegistrationId registrationId,
        TimingData.ManualTimeSource timeSource);
```

```text
TimingDataFactory.Context
  timingNodeId
  sequenceNumber
  locationId
  effectiveTime
  recordedAt
```

For the current manual variant, `TimingData.ManualTimeSource` is constrained to
`SYSTEM_ASSIGNED` or `OPERATOR_ENTERED`. Automatic registration uses observed
time by definition, so callers do not pass an `origin` or `OBSERVED` flag
merely to restate the return type.

The context contains values only. It does not contain `TimingNode`, `LogBook`,
stores, services or other mutable collaborators.

The first implementation does not need an abstract TimingData base class.
Concrete immutable implementations may delegate to `TimingDataFactory.Context`.
Introduce a private/protected helper only when multiple real implementations show
enough repeated behaviour to justify it; such a helper remains implementation
reuse, not an additional public semantic layer.

#### Provider boundary

A `TimingDataProvider` supplies a coherent family:

```text
TimingDataProvider
  stable provider/profile id
  TimingDataFactory
  TimingDataCodec
```

The factory creates the concrete in-memory TimingData objects. The codec
encodes/decodes the same profile family.
The built-in default/reference codec uses Jackson's streaming API only; JSON Lines
record framing, durable append and incomplete-tail recovery remain store responsibilities. Provider discovery and configuration
remain bootstrap/infrastructure concerns.

The provider therefore does more than representation translation, but it still
does not own TimingNode business rules. It chooses the concrete TimingData
implementation and its representation while preserving the common semantic
contracts defined by IF-05.

Both the Java-8 SI-01 runtime and Java-17 Engineering Client can depend on
`event-timing-data`. The Engineering Client may inspect the common interfaces
without depending on SI-01 Domain classes. Profile-specific inspection can be
added only where a real consumer needs it.

The first implementation keeps the default/reference profile inside the shared
TimingData library while the design is still changing; do not create another
production Maven artifact solely to mirror the conceptual profile split. A dummy
event-specific implementation in tests is sufficient to prove that the common
contract does not accidentally depend on the default concrete classes. A
separate provider artifact becomes justified when a real independently deployed
profile exists.

This artifact contains no SI-01 runtime/application classes and no JavaFX code.
Its Java API must remain usable from both the Java-8 SI-01 baseline and the
Java-17 Engineering Client.

### Derived consumers

The application core is deliberately not tied to one executable topology. Plausible consumers include:

```text
single-system application
multi-system / simulation application
public reference/test application
private/product application
```

These are consumer possibilities, not modules to create now.

### Java 8 extension/provider mechanism

A concrete public/private extension requirement now exists, so provider discovery
is no longer merely a future possibility. Keep the mechanism narrow and
composition-oriented:

```text
runtime.Composition
  -> infra extension discovery support
       -> discover built-in providers
       -> discover external provider JARs
  -> ExtensionRegistry
       TimingDataProvider
       UpstreamProtocolProvider
       AntennaProvider
       CanProtocolProvider
       DisplayProtocolProvider
  -> validate configured provider IDs
  -> create normal typed implementations
  -> compose runtime.Application
```

For the Java 8 baseline, external discovery can use a dedicated `URLClassLoader`
plus standard `ServiceLoader` SPI metadata. Discovery happens during startup;
runtime hot reload/unload is deliberately out of scope. The provider registry
combines built-in and external providers and rejects duplicate provider IDs.

Provider contracts belong with the capability whose meaning they create;
class-loader/discovery mechanics belong under application-core Infrastructure support. Domain,
application and I/O runtime code must not depend on `URLClassLoader`,
`ServiceLoader` or a generic `Plugin` interface.

`SimulatedAntenna` and its provider are built into the public baseline and are
always available. External antenna JARs add alternative `AntennaProvider`
implementations. The same typed pattern is available for concrete TimingData,
UpstreamProtocol, CAN-protocol and display-protocol implementations where a
public/private or vendor boundary requires it.

IF-11 selects providers by stable provider ID. Missing providers, duplicate IDs
or an incompatible provider/configuration combination fail during validation or
startup rather than silently falling back to another implementation.

The exact external-JAR directory/layout, dependency isolation strategy and
whether the provider contracts eventually justify a separately versioned SPI
artifact remain implementation/evidence-driven decisions.

### Public/private composition

Expected private/product-specific areas may include:

- production RFID control/protocol details;
- product-specific I/O/protocol implementations;
- production asset/source inventory and mappings;
- production upstream/backoffice schemas/codecs where sensitive;
- deployment-specific composition/policies.

Prefer normal composition and constructor/factory injection. Do not introduce a subclass-based `BaseApplication` extension model. The provider mechanism above is the explicit runtime-extension boundary; do not generalise it into arbitrary plugin access from domain/application code.

### Possible future artifacts

Create future artifacts only when a real boundary requires them. Candidates might eventually include:

- RabbitMQ/messaging I/O;
- Linux/Raspberry-Pi platform support;
- public/private RFID/CAN I/O implementations;
- separately versioning `event-timing-data` if binary compatibility/release evidence later requires an independent release cycle;
- reusable test support.

Splitting later is preferred over speculative libraries, provided package/responsibility boundaries remain clean enough to extract.

### Architecture/dependency checks

Useful automated rules may include:

- presentation packages do not own or persist application state;
- domain services do not reference presentation or concrete I/O classes;
- platform packages do not depend on event-timing application/domain behaviour;
- wire/protocol classes stay with their presentation or I/O capability;
- semantic contracts are not moved into transport packages merely because transport code uses them;
- public code contains no real deployment mappings or proprietary values;
- domain/application/runtime components do not depend on extension class-loader mechanics;
- duplicate provider IDs and unknown configured provider IDs fail deterministically;
- the executable consumes `timing-point-core` rather than copying/forking application-core source;
- the core artifact does not carry a concrete SLF4J provider/backend transitively;
- an executable runtime contains exactly one intended SLF4J provider.

### Open detailed-design decisions

- exact package granularity after real application/domain classes exist;
- final package naming where capability-oriented packages prove clearer than layer names;
- exact reusable boundary between single-instance runtime mechanics and multi-system application orchestration;
- exact bounded TimingNode work-queue capacity and queue-full operational policy after Raspberry-Pi burst/latency measurement;
- exact guard timeout for synchronous TimingNode operations and how it is configured/exposed diagnostically;
- concrete immutable TimingNode read-view representation and compact LogBook indexing required by the first ranking/query implementation;
- exact external extension-JAR directory/layout and dependency-isolation policy;
- private Maven artifact publication/consumption mechanism;
- version alignment between public core/provider contracts and private implementations;
- which I/O capabilities eventually deserve independent artifacts;
- whether and when provider contracts deserve a dedicated independently versioned SPI artifact;
- exact field logging configuration/rotation/retention policy in the default executable.


---

## Desktop GUI Application Specification Document (SSD)

**Source document:** [41-02-SSD-gui-application-specification-document.md](41-02-SSD-gui-application-specification-document.md)

Status: working draft / non-authoritative

Software item: **SI-02 — Desktop GUI Application**

This SSD is intentionally architecture-heavy today because SI-02 implementation has not
started. Software-item requirements will be promoted into this same document as the GUI
capability approaches implementation; no separate requirements/architecture document pair is planned.

### Inputs

The SI-02 specification consumes:

- `31-SSSD-software-system-specification-document.md` for SI-02 allocation and software-system constraints;
- `32-03-ISD-application-control-status.md` for the SI-01/SI-02 API contract;
- applicable parent/external-system inputs registered by `20-EXT-external-system-inputs.md` where an obligation is allocated directly to SI-02;
- a future system-owned GUI/HMI ISD when that contract is defined.

`30-UC-system-use-cases.md` provides system-level operational traceability. A separate software-item use-case document is optional and should be introduced only if decomposing GUI-specific actor/goal behaviour makes the SSD clearer. Its document range is assigned when such documents are actually introduced.

The SIP may schedule SI-02 work but is not requirement/design authority.

### Software-item requirements status

No stable SI-02 requirement set has yet been promoted. The existing text below remains
the working specification/architecture direction until that requirement slice is ready.

### Software-item architecture

Software item: **Desktop GUI Application** (SI-02)

This Software Architecture Document describes the initial architecture direction for the planned desktop GUI. The GUI is a separate software item from the **Timing Point Application** (SI-01) and communicates with it through system-defined network interfaces.

### Purpose

The GUI provides an operator-facing desktop application for monitoring and controlling the timing application.

The GUI must be able to connect to a timing application running:

- locally during development;
- in a public reference/test application;
- remotely on a Raspberry Pi target;
- remotely on another Windows/Linux host where applicable.

It must not depend on in-process Java calls, internal runtime classes or direct access to timing-application files.

### Software-item relationship

```text
Software item 02
Desktop GUI Application
        |
        | system-defined application-control/status interface
        | HTTP/JSON + WebSocket are current architecture candidates
        v
Software item 01
Timing Point Application
        |
        +-- local development host
        +-- Raspberry Pi Zero target
        +-- Windows/Linux target
```

The transport and message contracts ultimately belong in a system-level ISD rather than being owned by either software item.

### Relationship to the current JavaFX test client

The current JavaFX test client is an engineering/manual-integration tool for IF-03. It is
**not** the first implementation of SI-02 and does not select the GUI toolkit, runtime or
packaging for SI-02.

### First increment

The first GUI increment should remain deliberately small and validate the software-item/interface boundary:

- configure/select a timing-application endpoint;
- connect/disconnect;
- query/display application version;
- show connection state;
- show central application status;
- show available `TimingSystem` status;
- show stale/disconnected state explicitly;
- reconnect cleanly after temporary network loss.

This is enough to verify that the GUI can operate against a timing application running on a Raspberry Pi before adding operational timing controls.

### Later operator capabilities

As system requirements and IDDs mature, the GUI may add:

- open/close a timing system;
- RFID power and reinitialisation controls;
- start procedure control;
- registration overview;
- manual registration;
- penalty registration/revocation;
- ready-team overview/control;
- device/network/backoffice status and diagnostics.

These operations are handled by the **Timing Point Application** (SI-01). The GUI sends commands and presents state; it does not duplicate timing-domain business rules.

### GUI ISD as system input

The graphical user interface should be treated as a **system-level interface** rather than allowing the implementation to invent screens ad hoc.

A system-level GUI ISD can define items such as:

- screen/navigation structure;
- information that must be visible;
- operator actions and control availability;
- status/state representations;
- warnings/errors/confirmation behaviour;
- update/staleness behaviour;
- terminology and identifiers;
- interaction flows for open/close/start/RFID recovery and later registration operations.

The future SSD for the **Desktop GUI Application** (SI-02) can reference the applicable GUI-ISD clauses as requirements instead of copying the interface definition into the software-item requirements.

### Software-to-software interface ISD

A separate system-level ISD should define the communication interface between the **Desktop GUI Application** (SI-02) and **Timing Point Application** (SI-01).

Current direction:

- HTTP/JSON for commands, queries and initial snapshots;
- WebSocket for live status/data events;
- explicit versioning/compatibility of the interface;
- connection/reconnection semantics;
- authentication/authorisation when defined;
- stale-data behaviour;
- errors/result semantics.

The same interface is also used by engineering/test tools. A small browser-based test client may consume it later without becoming another software item.

### Internal GUI layering

A possible GUI structure is:

```text
GUI bootstrap
    |
    +-- presentation / views
    |
    +-- presentation models / view models
    |
    +-- GUI application services
    |      connection state
    |      status subscriptions
    |      command execution
    |
    +-- timing-application client port
           |
           +-- HTTP/WebSocket implementation
           +-- fake/stub implementation for GUI tests
```

Views should depend on presentation/application models rather than directly on HTTP/WebSocket libraries. This allows most GUI behaviour to be unit tested without a live timing application.

### Testability

The GUI should support at least three test levels:

1. **unit tests** using a fake timing-application client;
2. **integration tests** against the public reference/test application;
3. **system tests** against a real timing application, including one running on a Raspberry Pi.

The fake client should be able to produce version/status changes, disconnects, stale state and command results deterministically.

### Technology choices still open

- desktop GUI toolkit/framework;
- packaging/distribution model;
- HTTP/WebSocket client library compatible with the selected GUI runtime;
- whether the GUI uses the same Java baseline as the **Timing Point Application** (SI-01) or can use a newer runtime;
- configuration storage for known endpoints;
- authentication/credential storage;
- update mechanism.

The Raspberry Pi Java-8 constraint applies to the headless timing application. It does **not automatically require** the desktop GUI to use Java 8; that should be a separate software-item decision.


---

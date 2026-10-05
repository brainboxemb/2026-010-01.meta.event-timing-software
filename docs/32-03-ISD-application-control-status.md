# API Interface Specification (ISD)

Status: review candidate

System interface: **IF-03 — API**


## Purpose

This Interface Specification Document defines the **semantic contract** between the
**Timing Point Application** (SI-01) and independent software clients such as the
planned **Desktop GUI Application** (SI-02), the Development Client and automated
integration tooling.

IF-03 defines what clients can query, command and observe. It deliberately does not
define concrete HTTP resource paths, JSON member names, WebSocket envelope fields or
HTTP status-code mappings. The current development-v1 HTTP/JSON + WebSocket realization
is defined by `33-03-IDD-api-http-websocket.md`.

A browser/tablet operator interface served directly by SI-01 is a different system
interface: **IF-04 — Web Interface**.

## Terms and abbreviations

- **IF** — system interface
- **ISD** — Interface Specification Document
- **IDD** — Interface Design Description
- **OP** — Operation
- **SI** — Software Item


## Relationship to other documents

IF-03 is allocated by
`31-SSSD-software-system-specification-document.md` and implements the operator and
engineering intent described by the applicable system use cases, especially UC-001,
UC-002, UC-008 and UC-009.

The affected software-item specifications consume this interface contract. They shall
not independently redefine IF-03 semantics.

## Parties

```text
SI-02 Desktop GUI / Development Client / test tooling
                         |
                         | IF-03 API
                         v
              SI-01 Timing Point Application
```

SI-01 owns TimingNode state, committed TimingData and command acceptance. A client may
cache presentation state, but cached state is not the source of domain truth.

## Interface model

IF-03 has two semantic interaction styles:

- **request/response** for queries and commands;
- **live event delivery** for current-state and committed-data changes.

The concrete network transports and wire representation are design choices of the
current IF-03 realization and belong to the IDD.

TimingNode-specific operations address an application-wide-unique `TimingNodeId`.
`TimingSystemId` remains internal to SI-01 and is not part of the public IF-03 model.

## Build/version identity

IF-03 exposes build identity with these semantic values:

- application identity;
- software version;
- exact source revision;
- source reference;
- build-origin class;
- dirty/modified-source indication;
- IF-03 major interface version.

The identity remains stable for one running application build. Repeating a build does
not require wall-clock build time, CI run number or actor identity to become part of the
product identity.

## Current status

The current status model exposes 1..N TimingNodes. For each node it provides:

- `TimingNodeId`;
- current operational `LocationId`, or no assigned location;
- operational state `CLOSED`, `OPEN` or `ERROR`.

`ERROR` means the TimingNode is not available for normal operational commands because
a contained node-local failure prevented safe operation. The first such case is startup
TimingData recovery failure.

Status can also expose machine-readable problem entries. A problem has a stable code,
severity and human-readable explanation. A TimingNode-scoped problem identifies the
affected TimingNode. Clients shall make decisions from the machine-readable state/code,
not by parsing human-readable problem text.

For the current recovery-containment baseline, a TimingData startup-recovery failure
uses problem code `TIMING_DATA_RECOVERY_FAILED` with severity `ERROR`.

A restarted TimingNode begins `CLOSED` with no current operational LocationId unless a
later requirement explicitly defines another recovery rule. Historical TimingData does
not by itself recreate live operational state.

## Operation identifiers

Operations use the identifier form `IF03-OP-<number>`, where **OP** means
**Operation**. The identifier names a stable semantic interface operation; it is
independent of a concrete HTTP route, message name or other wire representation.

## Semantic operations

### IF03-OP-001 — Get build/version identity

Returns the build/version identity defined above.

### IF03-OP-002 — Get current status

Returns the complete current IF-03 status model.

### IF03-OP-003 — Subscribe to live application events

A newly connected or reconnected client first receives a complete current status snapshot
before relying on later change events.

The current semantic event set includes:

- current status snapshot;
- status changed;
- committed TimingData.

A status-change event is emitted only after an actual authoritative status change.
Committed TimingData is exposed as a live event only after the record is committed and is
visible in the TimingNode LogBook. Recovery of an existing record does not present that
record as a new live commit.

### IF03-OP-004 — Get public/engineering capabilities

Returns the supported/enabled state of optional IF-03 capabilities. Clients use this to
avoid assuming that an engineering or optional function exists merely because a client
knows how to display it.

The current capability set includes direct accepted-registration simulation.

### IF03-OP-005 — Open registration at a location

Inputs:

- addressed `TimingNodeId`;
- requested `LocationId`.

For a `CLOSED` TimingNode, applying the requested LocationId and changing lifecycle to
`OPEN` are one application/domain operation. IF-03 has no separate Set Location
operation in the current baseline.

The operation therefore has one externally observable ordering point relative to other
state-changing operations on the same TimingNode. Another presentation client cannot
observe or insert a different location change between the LocationId selection and the
corresponding CLOSED-to-OPEN transition.

Successful semantic outcomes include:

- `OPENED`;
- `ALREADY_OPEN`.

The exact idempotency rule for an OPEN request that supplies a *different* LocationId
while the TimingNode is already `OPEN` remains an explicit interface review point.
Until that rule is fixed, clients shall not rely on such a request changing the active
LocationId.

IF-03 models LocationId selection and the CLOSED-to-OPEN transition as one semantic
operation. A device or transport architecture that separates those responsibilities does
not change this interface contract.

### IF03-OP-006 — Close registration

Inputs:

- addressed `TimingNodeId`.

Successful semantic outcomes include:

- `CLOSED`;
- `ALREADY_CLOSED`.

A successful state change becomes visible through current status and live status-change
delivery.

### IF03-OP-007 — Simulate an accepted automatic registration

This is an engineering capability, not the normal RFID input interface.

Inputs:

- addressed `TimingNodeId`;
- automatic-registration action;
- resolved `RegistrationId`;
- accepted `time`.

The current engineering capability supports action `ADD`. Additional actions such as
REV require their semantics to be defined by the TimingData/IF-05 contract before they
become supported IF-03 inputs.

SI-01 supplies its own source identity, active LocationId, next source sequence and any
other TimingNode-owned commit context. The operation uses the same accepted-registration
path used after normal input interpretation/filtering.

The operation is available only when its advertised capability is enabled.

### IF03-OP-008 — Query committed LogBook

A client can:

- query LogBook metadata without downloading all records;
- request a bounded source-sequence range;
- request a bounded newest-record range.

Returned records use public IF-05 TimingData semantics and remain in committed
source-sequence order. Queued or uncommitted work is not LogBook content.

## Operation ordering and concurrency

Presentation clients may submit commands concurrently. IF-03 therefore requires
state-changing operations for one TimingNode to have a deterministic application-owned
order and to expose no partially applied compound operation.

In particular, IF03-OP-005 is one operation: LocationId selection and the
CLOSED-to-OPEN transition are not two independently interleavable presentation commands.

This requirement defines externally observable semantics. It does not prescribe a Java
mutex, worker class or thread implementation.

## Reconnect and resynchronisation

After a live connection is interrupted, a client rebuilds its view from SI-01 state rather
than assuming that its cache remained current.

A conforming client can:

1. obtain a complete current status snapshot;
2. query LogBook metadata/ranges for missed committed records;
3. combine the recovered baseline with later live events;
4. deduplicate overlapping committed records by stable TimingData record identity;
5. mark its view live only after that reconciliation is complete.

No durable replay of every transient live event is required while a client is disconnected.
Committed TimingData is recovered through the LogBook.

## Failure semantics

IF-03 distinguishes at least:

- malformed or invalid request;
- unsupported operation/resource;
- unknown TimingNode;
- capability not enabled;
- domain-state conflict;
- busy/unavailable processing;
- interrupted/failed processing;
- operation timeout with **outcome unknown**;
- unexpected internal interface failure.

A timeout does not imply that already accepted work was cancelled. Before blindly retrying
a state-changing operation whose outcome is unknown, a client resynchronises relevant
state/history.

Human-readable failure text is diagnostic. Stable machine-readable failure categories own
program behaviour.

## Compatibility

Within one compatible IF-03 major version:

- additions shall not silently change the meaning of existing semantic values or operations;
- clients shall be able to ignore additions they do not understand where the IDD marks them
  as compatible extensions;
- a breaking semantic change requires a new major interface version or an explicitly
  documented compatible migration.

Concrete version encoding and unknown-member/event handling belong to the IDD.

## Network exposure and security baseline

The first development realization is usable across a normal IP network path when remote
access is explicitly configured.

The current deployment baseline assumes a trusted closed network and does not require
application-level authentication or authorisation for IF-03.

- default development exposure remains local/loopback only;
- non-loopback exposure requires explicit configuration;
- remote operation is limited to the trusted deployment/development network.

## IF-03 requirements

:::{ifreq} Shared application semantics  
:id: IF03-REQ-001
:status: R
:derived_from: UC-001, UC-002, UC-008, UC-009

IF-03 operations and events shall use the shared SI-01 application/domain semantics
rather than implement independent business or lifecycle state in an interface adapter.
:::

:::{ifreq} Remote-host operation  
:id: IF03-REQ-002
:status: R
:derived_from: UC-008, UC-009

IF-03 shall support operation across a normal IP network boundary when non-loopback
access is explicitly configured.
:::

:::{ifreq} Version query  
:id: IF03-REQ-003
:status: R
:derived_from: UC-001, UC-009

IF-03 shall provide IF03-OP-001.
:::

:::{ifreq} Status query  
:id: IF03-REQ-004
:status: R
:derived_from: UC-001, UC-008, UC-009

IF-03 shall provide IF03-OP-002.
:::

:::{ifreq} Live status and committed-data delivery  
:id: IF03-REQ-005
:status: R
:derived_from: UC-008, UC-009

IF-03 shall provide IF03-OP-003.
:::

:::{ifreq} Reconnect to current state  
:id: IF03-REQ-006
:status: R
:derived_from: UC-001, UC-009

A connecting or reconnecting client shall be able to establish complete current status
before relying on later live changes.
:::

:::{ifreq} Machine-readable API realization  
:id: IF03-REQ-007
:status: R
:derived_from: UC-008, UC-009

The IF-03 realization shall provide a machine-readable representation suitable for SI-02,
engineering clients and automated test tooling.
:::

:::{ifreq} Explicit failure outcome  
:id: IF03-REQ-008
:status: R
:derived_from: UC-002, UC-008, UC-009

Unsupported, invalid or rejected IF-03 operations shall expose an explicit failure outcome
rather than silently reporting success.
:::

:::{ifreq} Safe default listen scope  
:id: IF03-REQ-009
:status: R
:derived_from: UC-008, UC-009

Without explicit remote-access configuration, the network realization of IF-03 shall be
local/loopback only.
:::

:::{ifreq} Compatible extension  
:id: IF03-REQ-010
:status: R
:derived_from: UC-008, UC-009

Compatible additions within one IF-03 major version shall not silently redefine existing
operation or value semantics.
:::

:::{ifreq} TimingNode location and lifecycle control  
:id: IF03-REQ-011
:status: R
:derived_from: UC-001, UC-002, UC-009

IF-03 shall expose application-wide-unique TimingNode identities with current optional
LocationId and OPEN/CLOSED state and shall provide IF03-OP-005/006. IF03-OP-005
shall carry the requested LocationId and represent location selection plus the
CLOSED-to-OPEN transition as one ordered TimingNode operation.
:::

:::{ifreq} Engineering capability discovery  
:id: IF03-REQ-012
:status: R
:derived_from: UC-009

IF-03 shall provide IF03-OP-004 so engineering clients can determine whether optional
engineering commands are supported and enabled.
:::

:::{ifreq} Direct accepted-registration simulation  
:id: IF03-REQ-013
:status: R
:derived_from: UC-003, UC-009

When its advertised capability is enabled, IF-03 shall provide IF03-OP-007 using an
explicit supported automatic-registration action, resolved RegistrationId and accepted
time while leaving TimingNode-owned commit context inside SI-01.
:::

:::{ifreq} Committed LogBook query  
:id: IF03-REQ-014
:status: R
:derived_from: UC-009, UC-011

IF-03 shall provide IF03-OP-008 as a node-addressed bounded LogBook query in committed
source-sequence order using public IF-05 semantics.
:::

:::{ifreq} Live committed TimingData delivery  
:id: IF03-REQ-015
:status: R
:derived_from: UC-009, UC-011

IF03-OP-003 shall expose a committed TimingData event only after the corresponding record
is committed and visible in the TimingNode LogBook.
:::

:::{ifreq} Rebuild committed history before live presentation  
:id: IF03-REQ-016
:status: R
:derived_from: UC-009, UC-011

A reconnecting client shall be able to combine current status, bounded committed LogBook
history and later live events using stable TimingData record identity before declaring its
view live.
:::


:::{ifreq} Degraded TimingNode status  
:id: IF03-REQ-017
:status: D
:derived_from: UC-020

IF03-OP-002 and the complete status snapshot from IF03-OP-003 shall represent a
contained TimingNode startup failure using node state `ERROR` and a machine-readable
problem associated with the affected TimingNodeId.

A TimingData startup-recovery failure shall use problem code
`TIMING_DATA_RECOVERY_FAILED` with severity `ERROR`. Normal state-changing or
registration operations addressed to a TimingNode in `ERROR` shall return an explicit
failure outcome rather than being accepted as normal operation.
:::


## Open points

- define the exact result when OPEN is requested with a different LocationId while
  the TimingNode is already OPEN.

# Backend Integration Interface Specification (ISD)

Status: draft

System interface: **IF-06 — Backend Integration**

## Purpose

This Interface Specification Document defines the semantic contract between the
**Timing Point Application (SI-01)** and an external backend.

The interface is expressed in terms of **UpstreamData**. UpstreamData is the
transport-independent message model used to exchange:

- committed TimingData;
- node-scoped reference data;
- data synchronization information;
- backend/link status information.

UpstreamData is deliberately a small semantic layer around existing data models.
It does not replace TimingData and it does not redefine TimingData record identity,
ordering or registration semantics.

The concrete public/default JSON representation is defined in
`33-06-IDD-upstreamdata-json.md`. Other deployment-specific representations may
implement the same semantic contract behind the UpstreamData representation/codec
boundary.

IF-06 does not define RabbitMQ queues/exchanges, HTTP routes, WebSocket event names,
Java classes, provider discovery or private deployment protocol details.

## Terms and abbreviations

- **IF** — system interface
- **ISD** — Interface Specification Document
- **IDD** — Interface Design Description
- **SI-01** — Timing Point Application
- **Backend** — external race/event backend system
- **TimingData** — committed timing record model defined by IF-05
- **UpstreamData** — transport-independent semantic message exchanged through IF-06
- **reference data** — backend-owned or backend-synchronized race/event data used by SI-01

## Relationship to other documents

IF-06 is allocated by
`31-SSSD-software-system-specification-document.md`.

TimingData semantics remain owned by
`32-05-ISD-timingdata-interchange.md`. When IF-06 carries TimingData, it carries
those same semantic values and record identities; it does not define another timing
record format.

SI-01 requirements consuming this interface are in
`41-01-SSD-timing-application-specification-document.md`.

The connector/transport design is elaborated by
`43-01-SDD-03-backoffice-transport-design.md`.

The public/default JSON representation is defined by
`33-06-IDD-upstreamdata-json.md`.

## Parties

```text
Backend
   ^
   | IF-06 UpstreamData
   v
SI-01 Timing Point Application
```

Both directions are supported. The meaning of a message is defined by its
UpstreamData family, not by the selected transport.

## Interface model

### UpstreamData

UpstreamData is the common semantic boundary between application behaviour and
backend transports. The public/reference representation uses **one message model
in both directions**. A TimingData/log-record value is carried *inside* a
TIMING_DATA message as payload, rather than being a separate wire-message format.
PING requests/answers, reference-data and synchronization exchanges use the
same message model with their respective message types and payloads. A deployment-specific adapter may encode
the inbound and outbound wire directions differently, without changing the
shared semantic UpstreamData model.

The current semantic families are:

| Family | Typical direction | Purpose |
| --- | --- | --- |
| TimingData transfer | SI-01 -> Backend | transfer one or more committed TimingData records |
| ReferenceData update | Backend -> SI-01 | provide node-scoped race/event reference data |
| Data synchronization | bidirectional | compare or advance known source state without redefining TimingData identity |
| Ping request / answer | bidirectional | one PING family with REQ/ANS op and an optional HB heartbeat mode; mode absence denotes a manual check |
| Status | bidirectional | expose backend/source synchronization and connector health relevant to integration |

The public RaceData and StageStartTimes reference-data semantics are defined below.
Synchronization payload semantics remain a Step-7 D03 decision. Their representations
must remain compatible with the common requirements in this ISD.

### TimingData relationship

When an UpstreamData message carries TimingData:

- the contained value is the same semantic TimingData defined by IF-05;
- Node ID + sequence number remains the TimingData record identity;
- the TimingData sequence remains the authoritative source order;
- batching or transport delivery does not renumber records;
- transport/message identifiers do not become TimingData record identifiers;
- retransmission of an already committed record does not create a new TimingData
  record merely because it is sent again.

A transport may batch multiple TimingData records into one delivery, but the
contained records retain their individual IF-05 identity and ordering.

### ReferenceData relationship

ReferenceData messages update race/event state owned by one addressed TimingNode.
The public v1 semantic datasets are `RACE_DATA` and `STAGE_START_TIMES`.

Both datasets use **complete snapshot** semantics. Each snapshot carries a positive
monotone revision for its TimingNode + dataset scope.
Application rules are:

- a higher revision is validated as a whole and, when valid, atomically replaces
  the current snapshot for that scope;
- a lower revision is stale and is not applied;
- an equal revision with semantically equal content is an idempotent duplicate and
  does not change state;
- an equal revision with different content is conflicting and is rejected;
- an empty valid snapshot explicitly clears the current live dataset;
- validation failure never partially changes the current snapshot.

`RACE_DATA` owns **live participant assignment** that is not stable EventData.
Its public v1 payload is a set of `RegistrationId -> TeamId` assignments. A
RegistrationId that already resolves to a stable TeamId through the configured
`EventData` profile shall not be remapped by RaceData. This keeps stable
event/profile identity separate from event-time race state.

`STAGE_START_TIMES` owns the current `TeamId -> stage start definition` snapshot
for the TimingNode. A start definition contains a local race time-of-day and may
also contain an explicit local date. Time-zone resolution is SI-01 domain/application
behaviour; it is not owned by the transport or codec.

ReferenceData therefore always defines:

- addressed TimingNode;
- dataset;
- monotone revision;
- complete snapshot payload;
- complete acceptance, stale/duplicate no-op, or explicit rejection outcome.

Connector/source identity does not create a second reference-data state. Multiple
transport paths that deliver the same node/dataset revision therefore converge on the
same semantic TimingNode state.

### Data synchronization

Synchronization is metadata around semantic source state. It is not a second
TimingData stream and it does not introduce delivery sequence numbers.

For TimingData, each side advertises the **highest contiguous IF-05 source sequence**
it currently knows for one NodeId:

- SI-01 advertises its highest locally committed sequence;
- the backend advertises its highest contiguously accepted sequence;
- sequence 0 means no TimingData is known yet for that node.

The backend-advertised contiguous sequence is the semantic acknowledgement boundary.
A transport/session acknowledgement, publisher confirm, HTTP success or queue delivery
receipt does **not** by itself advance semantic synchronization state.

For each configured logical upstream target and NodeId, SI-01 derives pending TimingData
from its committed LogBook and the backend's advertised sequence. If local head is 42 and
the backend knows through 39, records 40..42 are pending. A reconnect or backend recovery
may report a lower sequence than SI-01 saw previously; SI-01 shall then replay the
retained committed records after that sequence rather than assuming the older transport
session was authoritative.

Retransmission uses the original TimingData values unchanged. A repeated record with the
same NodeId + sequence and the same semantic content is idempotent. The same record key
with different semantic content is a synchronization conflict and shall not overwrite
either source silently. New records shall advance backend progress only through a
contiguous source sequence; a gap cannot advance the contiguous acknowledgement point.

SYNC may also advertise current reference-data revisions. For SI-01 these are the
accepted RaceData and StageStartTimes revisions; for the backend they are its current
authoritative revisions. Reference-data mismatch is repaired through REFERENCE_DATA
snapshots rather than embedding reference payloads in SYNC.

Multiple configured upstream targets maintain independent synchronization progress.
Target/session identity never becomes TimingData identity.

### PING request / answer lifecycle

`PING` is one bidirectional UpstreamData message family used to verify that the
configured upstream connection remains operational. A PING exchange has:

- **op** (required): `REQ` initiates a check; `ANS` responds to it;
- **mode** (optional): `HB` marks an automatically scheduled heartbeat; when
  `mode` is absent, the request is an explicitly initiated/manual check.

A receiver of a valid PING `op = REQ` replies with one PING `op = ANS`. The
answer preserves the request's `mode`, including its absence for a manual
request. This applies in both directions: SI-01 may initiate a request and
receive the backend's answer, and SI-01 also answers requests received from
the backend. There is no separate PONG message type in the default model.
A request/correlation identifier is not part of the mandatory IF-06 semantic
contract; an implementation may use one to associate answers with requests.

For each active upstream connector initiated by SI-01:

- when the connector first reaches its operational **CONNECTED** state, SI-01 sends one
  **heartbeat** PING immediately;
- while that connection remains operational, SI-01 sends another **heartbeat** PING every **30 seconds**;
- when the connector leaves the operational connected state, periodic PING generation
  stops;
- after a later reconnect, a new cycle begins with another immediate PING followed by
  the 30-second period.

A **manual** PING may be explicitly initiated by either party; it does not change,
reset or replace SI-01's scheduled heartbeat cycle.

PING REQUEST/ANSWER is connection/upstream activity. It is **not TimingData**,
does not consume a TimingData sequence number and does not create or modify a
LogBook record.

The timeout/failure policy for an unanswered PING is intentionally not fixed yet. A
transport may also have a lower-level keepalive mechanism, but that does not replace the
semantic PING request/answer exchange.

## Operation identifiers

Operations use stable semantic identifiers independent from transport.

| Operation | Direction | Meaning |
| --- | --- | --- |
| `IF06-OP-01 DELIVER_TIMING_DATA` | SI-01 -> Backend | deliver committed TimingData without changing IF-05 identity/order |
| `IF06-OP-02 APPLY_REFERENCE_DATA` | Backend -> SI-01 | offer node-scoped reference data for validation/application |
| `IF06-OP-03 SYNC` | bidirectional | exchange data-synchronization state |
| `IF06-OP-04 STATUS` | bidirectional | exchange/observe integration status |
| `IF06-OP-05 PING_REQUEST` | bidirectional | initiate PING with op REQ and optional HB mode |
| `IF06-OP-06 PING_ANSWER` | bidirectional | answer a PING request with op ANS, retaining the request's optional mode |

These identifiers describe semantic interaction. A concrete transport may map them
to messages, routes, topics, requests or events without changing their meaning.

## Semantic operations

### IF06-OP-01 DELIVER_TIMING_DATA

Input:

- one or more already committed TimingData records;
- source/node scope sufficient to route the records.

Required behaviour:

- preserve each record's IF-05 semantic values and record key;
- preserve source ordering;
- permit retransmission for synchronization;
- never imply that transport delivery rewrites local committed data.

### IF06-OP-02 APPLY_REFERENCE_DATA

Input:

- addressed TimingNode;
- dataset `RACE_DATA` or `STAGE_START_TIMES`;
- positive monotone revision;
- complete semantic snapshot for that dataset.

Outcome:

- accepted and atomically applied;
- accepted as an idempotent equal-revision duplicate with no state change;
- not applied because the revision is stale;
- rejected because the equal revision conflicts, the target/dataset is unsupported,
  or the snapshot is semantically invalid.

A rejected snapshot shall not be partially applied.

### IF06-OP-03 SYNC

This bidirectional operation advertises the sender's current semantic state for one
addressed TimingNode:

- highest contiguous TimingData sequence known by the sender, where 0 means none;
- current known/accepted RaceData revision, when any;
- current known/accepted StageStartTimes revision, when any.

The receiver compares that state with its own source state. SI-01 uses backend TimingData
progress to derive pending outbound records and replay them in source order. Reference
revision differences are reconciled by sending the applicable REFERENCE_DATA snapshot.

SYNC state is cumulative state, not a request/response correlation protocol. It may be
sent on initial connection, reconnect, after meaningful progress, or when either peer
needs to re-establish synchronization.

### IF06-OP-04 STATUS

Integration status may expose:

- connector/backend availability;
- source/node synchronization state;
- pending outbound work;
- last accepted/rejected reference-data update;
- last successful inbound/outbound semantic exchange.

Transport-specific diagnostic detail may be added by an implementation, but the
common semantic status shall remain transport-independent.

### IF06-OP-05 PING_REQUEST

A PING request has `op = REQ`. An automatically generated heartbeat
request adds `mode = HB`; a manually initiated request omits `mode`.
It has no TimingData payload or record identity.
Neither a legacy wire-level marker nor a sequence/correlation number is mandated
by IF-06.

For the SI-01 initiated heartbeat, the first PING REQUEST follows the connector
transition to operational CONNECTED immediately. Subsequent heartbeat requests
are generated at a 30-second period while that same connection remains operational.
Manual PING requests do not affect that schedule.

### IF06-OP-06 PING_ANSWER

The receiver of a valid PING REQUEST responds with one PING message carrying
`op = ANS` and the request's unchanged optional `mode`. If the
request omits `mode`, the answer also omits it. An answer has no TimingData
payload or record identity and must not trigger another answer.

A PING ANSWER confirms receipt and handling of a liveness request.
Implementations may add correlation identifiers to match individual requests
and answers. IF-06 does not yet define how many unanswered PING requests,
or what elapsed time, changes connector health/state.

## Failure semantics

Stable semantic failure categories include:

- invalid or unsupported UpstreamData;
- unknown/unmapped source or node;
- unsupported reference-data family;
- stale/conflicting reference-data update;
- unsupported representation/version;
- backend/transport unavailable;
- delivery outcome unknown;
- synchronization incomplete.

Transport failure is not equivalent to failure of the local TimingData commit that
produced outbound work.

A caller/connector shall not claim semantic acceptance merely because bytes were
successfully written to a transport.

## Representation and transport independence

IF-06 separates three concerns:

```text
semantic UpstreamData
        |
UpstreamData representation / codec
        |
connector / transport
```

The public/default implementation uses the JSON representation defined by
`33-06-IDD-upstreamdata-json.md`.

Alternative representations may be supplied for a deployment through the same
UpstreamData representation/codec boundary. Such an implementation may use another
text, binary, fixed-field or proprietary representation as long as it preserves the
applicable IF-06 semantics.

The selected representation is independent from the transport selection. For
example, the default JSON UpstreamData representation may be carried through an
engineering API transport or RabbitMQ.

## Compatibility

Compatible representation extensions shall not silently change existing UpstreamData
semantics.

A concrete representation shall expose enough version/type information to reject
unsupported input deterministically.

A deployment-specific representation may support only the semantic families required
by that deployment, but unsupported required families shall be reported explicitly and
shall not be reinterpreted as another message family.

## IF-06 requirements

:::{ifreq} Transport-independent UpstreamData semantics  
:id: IF06-REQ-001  
:status: D  

IF-06 shall define backend integration in terms of transport-independent UpstreamData
rather than RabbitMQ-, HTTP-, WebSocket- or deployment-specific wire messages.
:::

:::{ifreq} Preserve TimingData semantics  
:id: IF06-REQ-002  
:status: D  

When UpstreamData carries TimingData, it shall preserve every applicable IF-05 semantic
value, including Node ID, sequence number and record-type values, without renumbering or
rewriting the committed TimingData record.
:::

:::{ifreq} Keep transport identity separate from TimingData identity  
:id: IF06-REQ-003  
:status: D  

Transport, delivery, batch or session identifiers shall not replace the IF-05
TimingData record key or source sequence.
:::

:::{ifreq} Support node-scoped reference data  
:id: IF06-REQ-004  
:status: D  

IF-06 shall support backend-to-SI-01 reference-data updates with explicit semantic scope,
dataset/type and sufficient freshness/version information for SI-01 to determine whether
the update can be applied.
:::

:::{ifreq} Explicit reference-data outcome  
:id: IF06-REQ-005  
:status: D  

A reference-data update shall have an observable accepted/applied or rejected/not-applied
outcome with enough semantic reason/status information for synchronization diagnosis.
:::

:::{ifreq} Synchronization preserves source identity  
:id: IF06-REQ-006  
:status: D  

Data synchronization shall preserve the authoritative identities/order of
the data being synchronized and shall not create a second source sequence for committed
TimingData.
:::

:::{ifreq} Local TimingData commit independent from backend delivery  
:id: IF06-REQ-007  
:status: D  

Backend transport/session unavailability shall not by itself invalidate or roll back an
already successful local TimingData commit. Pending backend synchronization shall
remain separately representable.
:::

:::{ifreq} Public default JSON representation  
:id: IF06-REQ-008  
:status: D  

The public/reference implementation shall provide a versioned JSON representation of
UpstreamData suitable for development, engineering and integration verification. The
same UpstreamData message structure shall be used in both directions; committed
TimingData records shall be nested in a TIMING_DATA message payload rather than
being transmitted as standalone legacy log-line messages.
:::

:::{ifreq} Alternative representation support  
:id: IF06-REQ-009  
:status: D  

A deployment may provide an alternative UpstreamData representation behind the supported
representation/codec boundary without requiring the public application/domain model to
depend on deployment-specific wire-format classes or private source.
:::

:::{ifreq} Connector transport independence  
:id: IF06-REQ-010  
:status: D  

The same applicable UpstreamData semantics shall be usable through different configured
backend connectors/transports. Selecting another transport shall not redefine TimingData,
reference-data or synchronization semantics.
:::

:::{ifreq} Synchronize by contiguous TimingData source sequence  
:id: IF06-REQ-017  
:status: D  

For one NodeId, SYNC shall represent the sender's highest contiguous TimingData
source sequence. Sequence 0 shall mean no TimingData is known. The backend's value
shall act as the semantic acknowledgement boundary used by SI-01 to determine which
committed records remain pending for that upstream target.
:::

:::{ifreq} Keep transport acknowledgement separate from semantic acknowledgement  
:id: IF06-REQ-018  
:status: D  

Transport/session delivery success shall not by itself mark committed TimingData as
semantically synchronized. Pending state may advance only from backend semantic state
that identifies accepted source progress.
:::

:::{ifreq} Make TimingData retransmission idempotent by record identity  
:id: IF06-REQ-019  
:status: D  

Retransmission shall preserve the original NodeId, source sequence and TimingData
content. Re-receiving the same record key with the same semantic content shall be
idempotent. Re-receiving the same record key with different semantic content shall
be treated as a synchronization conflict and shall not silently overwrite data.
:::

:::{ifreq} Reconcile reference-data freshness through SYNC state  
:id: IF06-REQ-020  
:status: D  

SYNC shall be able to advertise the known RaceData and StageStartTimes revisions for
the addressed TimingNode. Revision mismatch shall be reconciled using the applicable
REFERENCE_DATA snapshot and shall not create another reference-data revision namespace.
:::

:::{ifreq} Re-establish synchronization after connection changes  
:id: IF06-REQ-021  
:status: D  

When an upstream semantic connection is established or re-established, the peers
shall exchange fresh SYNC state for the applicable TimingNodes before treating that
connection as synchronized. Progress remembered from an earlier transport/session
shall not by itself prove current backend state. A backend TimingData sequence greater
than SI-01's local committed head is a synchronization conflict and shall not cause
SI-01 to invent or skip source records.
:::

:::{ifreq} Atomic revisioned reference snapshots  
:id: IF06-REQ-014  
:status: D  

REFERENCE_DATA shall identify one TimingNode, one supported dataset and a positive
monotone revision. A valid higher-revision snapshot shall replace that dataset
atomically; stale lower revisions shall not apply; an equal-revision equal-content
snapshot shall be idempotent; and an equal-revision different-content snapshot
shall be rejected as conflicting. Invalid snapshots shall not be partially applied.
:::

:::{ifreq} Separate stable EventData from live RaceData  
:id: IF06-REQ-015  
:status: D  

The public `RACE_DATA` dataset shall carry live RegistrationId-to-TeamId
assignments that are not stable EventData profile identity. It shall not redefine
a stable RegistrationId-to-TeamId mapping supplied by EventData.
:::

:::{ifreq} Define StageStartTimes reference semantics  
:id: IF06-REQ-016  
:status: D  

The public `STAGE_START_TIMES` dataset shall carry TeamId-scoped stage start
definitions for the addressed TimingNode. Each start definition shall contain
a local race time-of-day and may contain an explicit local date; transport and
codec layers shall not perform elapsed-time or race-time-zone calculation.
:::

:::{ifreq} Immediate upstream PING on connect  
:id: IF06-REQ-011  
:status: D  

When a configured upstream connector reaches its operational connected state, SI-01
shall send one PING UpstreamData message with `op = REQ` and
`mode = HB` immediately.
:::

:::{ifreq} Periodic upstream PING while connected  
:id: IF06-REQ-012  
:status: D  

While a configured upstream connector remains operationally connected after its initial
heartbeat PING, SI-01 shall send a further heartbeat PING every 30 seconds. Scheduled
PING generation shall stop when that connector is no longer operationally connected
and shall restart with an immediate heartbeat PING after a later reconnect.
An explicitly initiated manual PING shall not reset this schedule. PING shall not
consume TimingData sequence identity or create TimingData/LogBook records.
:::

:::{ifreq} PING request op, answer and optional heartbeat mode  
:id: IF06-REQ-013  
:status: D  

IF-06 shall use one PING semantic message family with required
`op = REQ | ANS` and optional `mode = HB`. A PING REQUEST
without `mode` denotes an explicitly initiated/manual check; no `MANUAL`
value is required. The receiver of a valid PING REQUEST shall send one
PING ANSWER preserving the request's `mode` (including its absence)
as part of processing the request, without waiting for the 30-second
heartbeat schedule. A PING with `op = ANS` shall not itself be answered. This applies in
both directions. Unknown `mode` values shall not silently be treated as manual
checks. No separate PONG message type, PING sequence number or correlation
identifier is mandated by the interface; a representation/implementation may add
optional correlation. PING REQUEST/ANSWER shall not consume TimingData sequence
identity or create TimingData/LogBook records.
:::

## Open points

- Whether later RaceData or StageStartTimes versions need patch/delta operations in
  addition to the v1 complete-snapshot model.
- Exact operational retry/backoff timing; semantic replay/idempotency and pending-work
  rules are defined, while connector-specific retry timing remains a D04/implementation
  concern.
- Whether all status is exchanged as UpstreamData or some connector diagnostics remain
  local-only implementation status.
- Timeout/health policy for missing or late PING ANSWER messages.

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
backend transports.

The current semantic families are:

| Family | Typical direction | Purpose |
| --- | --- | --- |
| TimingData transfer | SI-01 -> Backend | transfer one or more committed TimingData records |
| ReferenceData update | Backend -> SI-01 | provide node-scoped race/event reference data |
| Data synchronization | bidirectional | compare or advance known source state without redefining TimingData identity |
| Status | bidirectional | expose backend/source synchronization and connector health relevant to integration |

The exact type-specific reference-data and synchronization payloads are refined by
Step-7 design activities D02 and D03. Their eventual representation must remain
compatible with the common requirements in this ISD.

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

ReferenceData messages update node-scoped race/event state used by SI-01. The
current allocated data includes RaceData and StageStartTimes.

Reference-data semantics shall define at least:

- addressed TimingNode or explicit broader scope;
- dataset/type;
- freshness/version information where applicable;
- complete acceptance or explicit rejection outcome.

Concrete dataset fields and update/snapshot rules are owned by the applicable
Step-7 semantic design and shall not be inferred from a transport encoding.

### Data synchronization

Synchronization is metadata around semantic source state. It is not a second
TimingData stream.

Synchronization may refer to TimingData source progress, reference-data freshness
or pending outbound work, but shall preserve the source identities owned by those
data models.

The detailed acknowledgement, retry, duplicate/idempotency and pending-work rules
are refined by Step-7 D03. They shall not use transient transport/session identity
as a replacement for committed TimingData identity.

## Operation identifiers

Operations use stable semantic identifiers independent from transport.

| Operation | Direction | Meaning |
| --- | --- | --- |
| `IF06-OP-01 DELIVER_TIMING_DATA` | SI-01 -> Backend | deliver committed TimingData without changing IF-05 identity/order |
| `IF06-OP-02 APPLY_REFERENCE_DATA` | Backend -> SI-01 | offer node-scoped reference data for validation/application |
| `IF06-OP-03 SYNC` | bidirectional | exchange data-synchronization state |
| `IF06-OP-04 STATUS` | bidirectional | exchange/observe integration status |

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

- reference-data family/type;
- scope/address;
- freshness/version information where required;
- semantic payload for that dataset.

Outcome:

- accepted and applied;
- rejected with a diagnosable reason;
- not applied because the message is stale/unsupported where the dataset contract
  defines such an outcome.

The detailed RaceData and StageStartTimes payload semantics are refined separately.

### IF06-OP-03 SYNC

This operation exchanges enough semantic state to determine whether either side has
pending or missing integration work.

The operation may refer to TimingData source progress and reference-data freshness,
but it shall not renumber TimingData or substitute transport/session counters for the
IF-05 source sequence.

Detailed acknowledgement and retry policy remains a D03 design decision.

### IF06-OP-04 STATUS

Integration status may expose:

- connector/backend availability;
- source/node synchronization state;
- pending outbound work;
- last accepted/rejected reference-data update;
- last successful inbound/outbound semantic exchange.

Transport-specific diagnostic detail may be added by an implementation, but the
common semantic status shall remain transport-independent.

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
UpstreamData suitable for development, engineering and integration verification.
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

## Open points

- Exact RaceData semantic fields and snapshot/update rules (Step-7 D02).
- Exact StageStartTimes semantic fields and correction/freshness rules (Step-7 D02).
- Acknowledgement, retry, duplicate/idempotency and pending-sync rules
  (Step-7 D03).
- Whether all status is exchanged as UpstreamData or some connector diagnostics remain
  local-only implementation status.

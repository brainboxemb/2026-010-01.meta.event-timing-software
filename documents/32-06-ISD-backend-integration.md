<!-- Generated review/output copy. Edit the source document, not this copy. -->

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

The project-wide odd/even maturity convention for integer JSON `v` fields is guidance
owned by `12-GPD-documentation-guide.md`; IF-06 does not redefine that convention.

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
backend transports. The current packet-oriented contract separates delivery from
message meaning:

- `UP_PACKET` carries one semantic message from SI-01 to the Central System;
- `DN_PACKET` carries one semantic message from the Central System to SI-01.

Both packet directions have a `packetNr`. `packetNr` is the delivery/debug number and must not be confused with the IF-05/LogBook TimingData sequence. The
public/default representation includes packet numbers in both directions because they
make traces, logs and engineering inspection unambiguous. In the current contract only
a positive `DN_PACKET.packetNr` participates in `RECV`/resend handling. A normal
`UP_PACKET.packetNr` is not itself acknowledged.

The public/default JSON representation also carries integer `v`, separate from
`packetNr`. `v` is the representation version: odd values denote a development/
unstable representation and even values denote a stable/released representation.
It is not packet-delivery state, is not acknowledged by RECV, is not a replay cursor
and does not replace the TIMING_DATA/LogBook sequence. Delivery retry keeps the same
`packetNr` and semantic content; packet ordering or stability must not be inferred
from `v` or from packet-number parity.

The current semantic message families carried by those packets are:

| Message | Typical direction | Purpose |
| --- | --- | --- |
| `TIMING_DATA` | SI-01 -> Central System | transfer committed TimingData records using their existing LogBook/IF-05 sequence |
| `TIMING_DATA_REQ` | Central System -> SI-01 | request TimingData beginning at one IF-05/LogBook sequence |
| `SEQ` | bidirectional | request, answer or notify the current TIMING_DATA position |
| `TEAM_ASSIGNMENTS` | Central System -> SI-01 | deliver current RegistrationId -> TeamId assignments; no independent replay sequence is created |
| `STAGE_STARTS` | Central System -> SI-01 | deliver current RegistrationId-scoped stage starts; no independent replay sequence is created |
| `RECV` | SI-01 -> Central System | confirm the last successfully processed normal downstream packet or request a full downstream state resend |
| `PING` | bidirectional | immediate REQ/ANS liveness exchange without normal RECV handling |
| `STATUS` | bidirectional | expose upstream and connector health relevant to integration |

A deployment-specific adapter may encode the two packet directions differently while
preserving these semantics. Concrete private framing, field widths and legacy message
codes are outside this public contract.

### TimingData relationship

When an UpstreamData message carries TimingData:

- the contained value is the same semantic TimingData defined by IF-05;
- Node ID + sequence number remains the TimingData record identity;
- the TimingData sequence remains the authoritative source order;
- batching or transport delivery does not renumber records;
- transport/message identifiers do not become TimingData record identifiers;
- retransmission of an already committed record does not create a new TimingData
  record merely because it is sent again.

One TIMING_DATA UpstreamData message carries **1..16** TimingData records. The
contained records retain their individual IF-05 identity and ordering. A larger
replay is split into multiple ordered TIMING_DATA messages; batching never creates
another TimingData sequence.


### Current reference data relationship

`TEAM_ASSIGNMENTS` and `STAGE_STARTS` are two independent Central-owned current-state
message families for one addressed TimingNode. Neither is a durable historical stream and
neither has a source sequence. The containing `DN_PACKET.packetNr` provides delivery
numbering only.

`TEAM_ASSIGNMENTS` carries only live RegistrationId -> TeamId changes. Stable EventData
remains authoritative for RegistrationIds that already have a fixed TeamId mapping.

`STAGE_STARTS` carries only RegistrationId -> stage-start changes. A stage-start value
has no LocationId or StageId in IF-06. Which TimingNode receives the current value, and
whether its currently open WP projection uses it, is application/runtime routing outside
the stage-start value itself.

Each message uses explicit `SET` or `DEL` changes and carries **1..16** changes of its
own type. The two message families are not combined into one atomic unit and do not share
one message-size budget.

Normal Central-to-node delivery uses stop-and-wait semantics. For each TimingNode, Central
keeps at most one positive-numbered DN_PACKET outstanding. It does not send the next normal
positive-numbered DN_PACKET until the current one has been confirmed by RECV. If confirmation
is not received, Central may resend the **same packet with the same packetNr and semantic
content**.

SI-01 validates and applies one complete TEAM_ASSIGNMENTS or STAGE_STARTS message before
confirming its containing downstream packet with RECV. If that RECV is lost and the same
DN_PACKET is received again, SI-01 must not apply the same changes twice; it repeats the
confirmation for the already processed packet.

Central therefore needs no retained history of old TEAM_ASSIGNMENTS or STAGE_STARTS
packets. It keeps current downstream state plus the exact outstanding packet needed for
retry. A full downstream-state resend is requested with RECV position 0; Central rebuilds
the applicable current TEAM_ASSIGNMENTS and STAGE_STARTS state rather than replaying a
historical source sequence.

### TimingData sequence and replay

Application-data synchronization in the current baseline applies only to
`TIMING_DATA`. The authoritative sequence is the existing IF-05/LogBook sequence for
one NodeId; IF-06 does not create another TimingData source sequence.

`SEQ` exchanges the current TIMING_DATA position and has three operations:

- `REQ`: ask the peer for its current TIMING_DATA position;
- `ANS`: answer a preceding REQ with `seq = N`;
- `NTF`: proactively notify the peer that the sender's current position is `seq = N`.

The meaning of the position follows the direction:

- SI-01 reports its current LogBook/IF-05 source head;
- Central reports the highest contiguous TIMING_DATA sequence it has accepted/processed.

Sequence 0 means that side currently has no TIMING_DATA position. REQ itself carries no
sequence. ANS and NTF carry the current sequence.

Either peer may send `SEQ REQ`. This allows Central to ask how many committed LogBook
records currently exist and allows SI-01 to ask how far Central has processed. SI-01 may
also send `SEQ NTF` when its LogBook head advances.

Actual record replay is a separate `TIMING_DATA_REQ` operation. Central sends
`TIMING_DATA_REQ(fromSeq=N)` to request retained TimingData beginning at IF-05 sequence
N. SI-01 answers with one or more bounded TIMING_DATA messages containing the original
records and identities.

The LogBook remains the replay source. On an available upstream session, proactive
live TIMING_DATA forwarding is normally enabled. After a fresh connection SI-01 publishes
its current source head through SEQ. Central compares that position with its highest
contiguous processed TIMING_DATA sequence. When Central is behind, it sends
TIMING_DATA_REQ from its next expected sequence. When both positions are equal, Central
does not need to send a synchronization message back.

When SI-01 handles an actual TIMING_DATA_REQ, that replay synchronization temporarily
pauses proactive live forwarding. SI-01 captures its current LogBook head and replays
from `fromSeq` through that captured head. Records committed after the captured head are
not interleaved into the replay range. After replay completes, proactive live forwarding
resumes from the sequence after the captured head. SEQ position exchange itself does not
enable, disable or gate live forwarding.

Loss does not require a second durable TimingData outbox. Central can request retained
TimingData again from the LogBook. Retransmission preserves the original IF-05 record
identity and content.

TEAM_ASSIGNMENTS and STAGE_STARTS are deliberately not synchronized by SEQ. Their recovery uses DN_PACKET delivery,
RECV/resend and, when the node no longer trusts its downstream state, an explicit full
state resend request.


### PING request / answer lifecycle

`PING` is one bidirectional semantic message used to verify that the configured
upstream connection remains operational. A PING exchange has:

- **op** (required): `REQ` initiates a check; `ANS` responds to it;
- **mode** (optional): `HB` marks an automatically scheduled heartbeat; when
  `mode` is absent, the request is an explicitly initiated/manual check.

A receiver of a valid PING `op = REQ` replies immediately with one PING
`op = ANS`. The answer preserves the request's `mode`, including its absence for
a manual request. This applies in both directions.

PING is deliberately outside normal downstream confirmation. A packet carrying PING
uses packetNr 0 and is not followed by RECV. A PING packet carries no other semantic
message. The PING answer also uses packetNr 0. This keeps liveness response independent
from a normal positive-numbered DN_PACKET that may still be awaiting confirmation.

There is no separate PONG message type in the default model. A request/correlation
identifier is not part of the mandatory semantic contract; a representation may expose
one for engineering visibility.

For each active upstream connector initiated by SI-01:

- when the connector first reaches its operational **CONNECTED** state, SI-01 sends one
  heartbeat PING immediately;
- while that connection remains operational, SI-01 sends another heartbeat PING every
  **30 seconds**;
- when the connector leaves the operational connected state, periodic PING generation
  stops;
- after a later reconnect, a new cycle begins with another immediate PING followed by
  the 30-second period.

A manual PING may be initiated by either party and does not reset the heartbeat cycle.
PING is not TimingData, does not consume a TimingData sequence and does not create or
modify a LogBook record.

The timeout/failure policy for an unanswered PING is intentionally not fixed yet. A
transport may also have a lower-level keepalive mechanism, but that does not replace the
semantic PING request/answer exchange.

## Operation identifiers

Operations use stable semantic identifiers independent from transport.

| Operation | Direction | Meaning |
| --- | --- | --- |
| `IF06-OP-01 DELIVER_TIMING_DATA` | SI-01 -> Central System | deliver committed TimingData without changing IF-05 identity/order |
| `IF06-OP-02 APPLY_TEAM_ASSIGNMENTS` | Central System -> SI-01 | validate and apply current RegistrationId-to-TeamId assignments carried by one downstream packet |
| `IF06-OP-09 APPLY_STAGE_STARTS` | Central System -> SI-01 | validate and apply current RegistrationId-scoped stage starts carried by one downstream packet |
| `IF06-OP-03 TIMING_DATA_SEQUENCE` | bidirectional | request, answer or notify the current TIMING_DATA sequence position |
| `IF06-OP-04 STATUS` | bidirectional | exchange/observe integration status |
| `IF06-OP-05 PING_REQUEST` | bidirectional | initiate PING with op REQ and optional HB mode |
| `IF06-OP-06 PING_ANSWER` | bidirectional | answer a PING request with op ANS, retaining the request's optional mode |
| `IF06-OP-07 RECV` | SI-01 -> Central System | confirm the last processed normal DN_PACKET or request full downstream state resend |
| `IF06-OP-08 REQUEST_TIMING_DATA` | Central System -> SI-01 | request retained TimingData beginning at sequence N |

These identifiers describe semantic interaction. A concrete transport may map them to
messages, routes, topics, requests or events without changing their meaning.

## Semantic operations

### IF06-OP-01 DELIVER_TIMING_DATA

Input:

- **1..16** already committed TimingData records;
- source/node scope sufficient to route the records.

Required behaviour:

- preserve each record's IF-05 semantic values and record key;
- preserve source ordering;
- permit retransmission for synchronization;
- never imply that packet delivery rewrites local committed data.

### IF06-OP-02 APPLY_TEAM_ASSIGNMENTS

Input:

- addressed TimingNode;
- **1..16** RegistrationId-to-TeamId SET/DEL changes;
- containing DN_PACKET delivery number.

Outcome:

- a new valid packet: validate and apply all assignment changes as one unit, then confirm
  the containing downstream packet with RECV;
- a resend of an already processed packet: do not apply again; repeat RECV;
- invalid semantic content: do not advance the accepted downstream packet position and
  expose a diagnosable rejection/conflict.

TEAM_ASSIGNMENTS has no source sequence and no historical replay obligation.

### IF06-OP-09 APPLY_STAGE_STARTS

Input:

- addressed TimingNode;
- **1..16** RegistrationId-scoped stage-start SET/DEL changes;
- containing DN_PACKET delivery number.

Outcome:

- a new valid packet: validate and apply all stage-start changes as one unit, then confirm
  the containing downstream packet with RECV;
- a resend of an already processed packet: do not apply again; repeat RECV;
- invalid semantic content: do not advance the accepted downstream packet position and
  expose a diagnosable rejection/conflict.

STAGE_STARTS carries no LocationId or StageId. It has no source sequence and no
historical replay obligation.

### IF06-OP-03 TIMING_DATA_SEQUENCE

This bidirectional operation uses the SEQ message:

- `op = REQ`: ask the peer for its current TIMING_DATA position;
- `op = ANS, seq = N`: answer a request;
- `op = NTF, seq = N`: notify a new/current position without a request.

For SI-01, N is its LogBook/IF-05 source head. For Central, N is the highest contiguous
TIMING_DATA sequence it has accepted/processed. Sequence 0 means no position yet.

### IF06-OP-07 RECV

RECV refers to downstream delivery, not to TimingData source identity. A positive value
confirms the last normal DN_PACKET that SI-01 has successfully processed. Central keeps
at most one positive-numbered downstream packet outstanding and resends that exact packet when
confirmation is absent.

If SI-01 observes that the current downstream delivery cannot be advanced because an
earlier packet is still missing, it reports the last successfully processed downstream
packet. Under normal stop-and-wait delivery Central never sends packet N+1 before N is
confirmed.

RECV position 0 is not acknowledgement of a normal packet. It requests a full resend of
the current Central-owned downstream state.

### IF06-OP-08 REQUEST_TIMING_DATA

TIMING_DATA_REQ carries:

- addressed TimingNode;
- `fromSeq >= 1`.

Central uses it to request LogBook TimingData beginning at IF-05 sequence `fromSeq`.
The request does not create another source sequence. SI-01 serves the range from retained
LogBook data in bounded TIMING_DATA messages.

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

<a id="IF06-REQ-001"></a>

**IF06-REQ-001 — Transport-independent UpstreamData semantics**

IF-06 shall define backend integration in terms of transport-independent UpstreamData
rather than RabbitMQ-, HTTP-, WebSocket- or deployment-specific wire messages.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Required by:** [`SI01-REQ-064`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-064)
- **Verified by:** [`VC-ST1-010`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-010)

---


<a id="IF06-REQ-002"></a>

**IF06-REQ-002 — Preserve TimingData semantics**

When UpstreamData carries TimingData, it shall preserve every applicable IF-05 semantic
value, including Node ID, sequence number and record-type values, without renumbering or
rewriting the committed TimingData record.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Required by:** [`SI01-REQ-064`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-064)
- **Verified by:** [`VC-ST1-010`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-010)

---


<a id="IF06-REQ-003"></a>

**IF06-REQ-003 — Keep transport identity separate from TimingData identity**

Transport, delivery, batch or session identifiers shall not replace the IF-05
TimingData record key or source sequence.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Required by:** [`SI01-REQ-064`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-064)
- **Verified by:** [`VC-ST1-010`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-010)

---


<a id="IF06-REQ-004"></a>

**IF06-REQ-004 — Support node-scoped reference data**

IF-06 shall support Central System-to-SI-01 TEAM_ASSIGNMENTS and STAGE_STARTS messages.
Both are addressed to one NodeId and carry incremental RegistrationId-scoped current
state. Neither message shall carry LocationId or create an independent historical
source sequence.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Required by:** [`SI01-REQ-063`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-063)
- **Verified by:** [`VC-ST1-011`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-011)

---


<a id="IF06-REQ-005"></a>

**IF06-REQ-005 — Explicit reference-data outcome**

A TEAM_ASSIGNMENTS or STAGE_STARTS message shall be validated and applied before SI-01
confirms its containing DN_PACKET with RECV. A resend of an already processed DN_PACKET
shall not apply the same current-state change twice. Invalid content shall not advance
the accepted downstream packet position and shall remain diagnosable.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Required by:** [`SI01-REQ-063`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-063)
- **Verified by:** [`VC-ST1-011`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-011)

---


<a id="IF06-REQ-006"></a>

**IF06-REQ-006 — Synchronization preserves source identity**

Data synchronization shall preserve the authoritative identities/order of
the data being synchronized and shall not create a second source sequence for committed
TimingData.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Required by:** [`SI01-REQ-065`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-065)

---


<a id="IF06-REQ-007"></a>

**IF06-REQ-007 — Local TimingData commit independent from backend delivery**

Backend transport/session unavailability shall not by itself invalidate or roll back an
already successful local TimingData commit. Pending backend synchronization shall
remain separately representable.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Required by:** [`SI01-REQ-065`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-065)

---


<a id="IF06-REQ-008"></a>

**IF06-REQ-008 — Public default JSON representation**

The public/reference implementation shall provide a versioned JSON representation of
UpstreamData suitable for development, engineering and integration verification. It
shall represent the two directions explicitly as UP_PACKET and DN_PACKET, each with a
packetNr for traceability. Committed TimingData records shall be nested in a TIMING_DATA
message payload rather than being transmitted as standalone legacy log-line messages.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Verified by:** [`VC-ST1-010`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-010)

---


<a id="IF06-REQ-009"></a>

**IF06-REQ-009 — Alternative representation support**

A deployment may provide an alternative UpstreamData representation behind the supported
representation/codec boundary without requiring the public application/domain model to
depend on deployment-specific wire-format classes or private source.

— — —

- **Type:** Interface Requirement
- **Status:** Draft

---


<a id="IF06-REQ-010"></a>

**IF06-REQ-010 — Connector transport independence**

The same applicable UpstreamData semantics shall be usable through different configured
backend connectors/transports. Selecting another transport shall not redefine TimingData,
reference-data or synchronization semantics.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Required by:** [`SI01-REQ-064`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-064)
- **Verified by:** [`VC-ST1-010`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-010)

---


<a id="IF06-REQ-017"></a>

**IF06-REQ-017 — Exchange the TimingData sequence position**

For one NodeId, SEQ shall exchange only the TIMING_DATA position. SEQ REQ asks the peer
for its current position; SEQ ANS returns that position; SEQ NTF reports it without a
request. SI-01's position is its current IF-05/LogBook source head. Central's position
is the highest contiguous TIMING_DATA sequence it has accepted/processed. Sequence 0
means no position yet.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Required by:** [`SI01-REQ-081`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-081), [`SI01-REQ-084`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-084)
- **Verified by:** [`VC-ST1-012`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-012)

---


<a id="IF06-REQ-018"></a>

**IF06-REQ-018 — Separate packet numbering from TimingData synchronization**

Both public/default packet directions shall carry a packet number for traceability.
A positive DN_PACKET packetNr shall participate in RECV/resend handling; an UP_PACKET
packetNr shall not itself require acknowledgement in the current baseline. Packet numbering shall not replace or advance the IF-05/LogBook TIMING_DATA sequence.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Required by:** [`SI01-REQ-084`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-084)
- **Verified by:** [`VC-ST1-010`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-010), [`VC-ST1-011`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-011)

---


<a id="IF06-REQ-019"></a>

**IF06-REQ-019 — Make TimingData retransmission idempotent by record identity**

Retransmission shall preserve the original NodeId, source sequence and TimingData
content. Re-receiving the same record key with the same semantic content shall be
idempotent. Re-receiving the same record key with different semantic content shall
be treated as a synchronization conflict and shall not silently overwrite data.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Required by:** [`SI01-REQ-082`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-082)
- **Verified by:** [`VC-ST1-012`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-012)

---


<a id="IF06-REQ-020"></a>

**IF06-REQ-020 — Request retained TimingData by source sequence**

Central System shall be able to request TIMING_DATA beginning at an inclusive
IF-05/LogBook sequence with TIMING_DATA_REQ. A request from sequence 1 means replay
from the retained beginning of the LogBook. TEAM_ASSIGNMENTS or STAGE_STARTS shall not use this replay
mechanism.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Required by:** [`SI01-REQ-082`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-082)
- **Verified by:** [`VC-ST1-012`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-012)

---


<a id="IF06-REQ-021"></a>

**IF06-REQ-021 — Re-establish TimingData synchronization after connection changes**

When an upstream semantic connection is established or re-established, SI-01 shall
first publish its current downstream receive position through RECV and shall publish its
current TIMING_DATA source head through SEQ. RECV position 0 means this SI-01 runtime
has not processed a normal DN_PACKET and therefore requests a full current-state resend.
A positive RECV position N means SI-01 has already processed DN_PACKET N; a Central peer
that has no local downstream baseline shall continue normal numbering at N+1 rather than
restart at packet 1. This receive-position announcement preserves TimingNode-owned
downstream state across transport reconnects and Central-process restarts.

When Central is behind the reported TIMING_DATA source head, Central shall send
TIMING_DATA_REQ from its next expected sequence. When Central's processed position already
equals SI-01's source head, Central need not send either an empty TIMING_DATA_REQ or an
equal-position SEQ notification.

Proactive live TIMING_DATA forwarding shall normally remain enabled while the session is
available. When SI-01 handles a TIMING_DATA_REQ it shall temporarily pause proactive live
forwarding, capture its current LogBook head, replay through that captured head, and
resume proactive live forwarding from the next sequence only after that replay completes.
SEQ position exchange itself shall not gate proactive live forwarding.

TEAM_ASSIGNMENTS and STAGE_STARTS recovery shall not depend on a retained Central source
sequence. When SI-01 cannot trust its downstream state it may request a full resend of
the current Central-owned downstream state through RECV position 0.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Required by:** [`SI01-REQ-085`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-085)
- **Verified by:** [`VC-ST1-012`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-012)

---


<a id="IF06-REQ-022"></a>

**IF06-REQ-022 — Bound IF-06 data-message size**

One TIMING_DATA message shall carry at most 16 TimingData records. One TEAM_ASSIGNMENTS
message shall carry at most 16 assignment changes. One STAGE_STARTS message shall carry
at most 16 stage-start changes. A producer with more retained TimingData shall split it
without changing the underlying IF-05 sequence. Larger current-state delivery may require
multiple confirmed DN_PACKET turns; it shall not create another source sequence.

— — —

- **Type:** Interface Requirement
- **Status:** Draft

---


<a id="IF06-REQ-014"></a>

**IF06-REQ-014 — Confirm downstream packets with stop-and-wait delivery**

For one TimingNode, Central shall keep at most one normal positive-numbered DN_PACKET
unconfirmed. It shall not send the next normal positive-numbered DN_PACKET until RECV confirms
the current one. If confirmation is absent, Central may resend the exact same packet
with the same packetNr and semantic content. SI-01 shall not apply a resent already
processed packet twice.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Required by:** [`SI01-REQ-078`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-078)
- **Verified by:** [`VC-ST1-011`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-011)

---


<a id="IF06-REQ-015"></a>

**IF06-REQ-015 — Separate stable EventData from live current reference data**

TEAM_ASSIGNMENTS shall carry incremental RegistrationId-to-TeamId assignments that are
not stable EventData profile identity.
The semantic contract is generic and does not classify an assignment by tag type.
It shall not redefine a stable RegistrationId-to-TeamId mapping supplied by EventData.
Physical TagIds remain resolved to their RegistrationId by EventData.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Required by:** [`SI01-REQ-077`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-077), [`SI01-REQ-078`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-078)

---


<a id="IF06-REQ-016"></a>

**IF06-REQ-016 — Define StageStartTimes reference semantics**

Central shall retain StageStartTimes source state by StageId and RegistrationId. STAGE_STARTS
shall carry the routed current-stage projection as incremental RegistrationId-scoped
stage-start-time changes. The message itself carries neither LocationId nor StageId.

Under the current event mapping, Stage N finishes at LocationId N. Central uses the addressed
TimingNode's current OPEN LocationId to select Stage N before constructing STAGE_STARTS. The
RegistrationId is the timing-domain identity whose start is being defined; consumers shall not
need an intermediate TeamId lookup to match a registration to its stage start.
A SET shall carry one `TimingTimestamp` value containing at least local race
time-of-day. The timestamp may also contain a local date or already be absolute
when the source knows that information. A source that knows only time-of-day
shall remain valid; no transport or codec layer shall invent a date or time zone.
DEL removes the current definition. Elapsed-time and race-time-zone interpretation
belong to SI-01 domain behaviour, not to transport or codec layers.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Required by:** [`SI01-REQ-079`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-079)

---



<a id="IF06-REQ-011"></a>

**IF06-REQ-011 — Immediate upstream PING on connect**

When a configured upstream connector reaches its operational connected state, SI-01
shall send one PING message with `op = REQ` and `mode = HB` immediately
in a packet with packetNr 0. PING packets shall not use RECV.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Required by:** [`SI01-REQ-075`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-075)
- **Verified by:** [`VC-ST1-009`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-009)

---


<a id="IF06-REQ-012"></a>

**IF06-REQ-012 — Periodic upstream PING while connected**

While a configured upstream connector remains operationally connected after its initial
heartbeat PING, SI-01 shall send a further heartbeat PING every 30 seconds. Scheduled
PING generation shall stop when that connector is no longer operationally connected
and shall restart with an immediate heartbeat PING after a later reconnect.
An explicitly initiated manual PING shall not reset this schedule. PING shall not
consume TimingData sequence identity or create TimingData/LogBook records.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Required by:** [`SI01-REQ-075`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-075)
- **Verified by:** [`VC-ST1-009`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-009)

---


<a id="IF06-REQ-013"></a>

**IF06-REQ-013 — PING request op, answer and optional heartbeat mode**

IF-06 shall use one PING semantic message family with required
`op = REQ | ANS`, optional `mode = HB` and optional absolute UTC message
`time`. A PING REQUEST without `mode` denotes an explicitly initiated/manual
check; no `MANUAL` value is required. When present, `time` denotes the creation/send
time of that specific PING message. A PING ANSWER therefore creates its own message
time and shall not reuse the request's time as the answer time.

The receiver of a valid PING REQUEST shall send one PING ANSWER preserving the
request's `mode` (including its absence) as part of processing the request, without
waiting for the 30-second heartbeat schedule. A PING with `op = ANS` shall not itself
be answered. This applies in both directions. Unknown `mode` values shall not silently
be treated as manual checks. No separate PONG message type, PING sequence number or
correlation identifier is mandated by the interface; a representation/implementation
may add optional correlation. Reference producers should populate `time`, while
readers remain compatible with PING messages that omit it. PING REQUEST/ANSWER shall
not consume TimingData sequence identity or create TimingData/LogBook records.

— — —

- **Type:** Interface Requirement
- **Status:** Draft
- **Required by:** [`SI01-REQ-075`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-075), [`SI01-REQ-076`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-076)
- **Verified by:** [`VC-ST1-009`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-009)

---


## Open points

- Exact producer-side rules for advancing  around a multi-packet state
  mutation/snapshot; the parity meaning is fixed (even stable, odd unstable), but the
  transition boundary still needs to be made explicit in the implementation design.

- Exact retry/backoff timing for an unconfirmed normal DN_PACKET; stop-and-wait
  identity/resend semantics are defined while connector timing remains an implementation
  concern.
- Whether all status is exchanged as UpstreamData or some connector diagnostics remain
  local-only implementation status.
- Timeout/health policy for missing or late PING ANSWER messages.

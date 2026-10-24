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
backend transports. The current packet-oriented contract separates delivery from
message meaning:

- \`UP_PACKET\` carries one semantic message from SI-01 to the Central System;
- \`DN_PACKET\` carries one semantic message from the Central System to SI-01.

Both packet directions have a \`packetId\`. The packet identifier is delivery identity
and must not be confused with the IF-05/LogBook TimingData sequence. The public/default
representation includes packet identifiers in both directions because they make traces,
logs and engineering inspection unambiguous. In the current contract only a positive
\`DN_PACKET.packetId\` participates in \`RECV\`/resend handling. A normal
\`UP_PACKET.packetId\` is not itself acknowledged.

The current semantic message families carried by those packets are:

| Message | Typical direction | Purpose |
| --- | --- | --- |
| \`TIMING_DATA\` | SI-01 -> Central System | transfer committed TimingData records using their existing LogBook/IF-05 sequence |
| \`TIMING_DATA_REQ\` | Central System -> SI-01 | request TimingData beginning at one IF-05/LogBook sequence |
| \`SEQ\` | bidirectional | request, answer or notify the current TIMING_DATA position |
| \`RACE_DATA\` | Central System -> SI-01 | deliver current race-state changes; no independent replay sequence is created |
| \`RECV\` | SI-01 -> Central System | confirm the last successfully processed normal downstream packet or request a full downstream state resend |
| \`PING\` | bidirectional | immediate REQ/ANS liveness exchange without normal RECV handling |
| \`STATUS\` | bidirectional | expose upstream and connector health relevant to integration |

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


### RaceData relationship

\`RACE_DATA\` carries Central-owned live race-state changes for one addressed TimingNode.
It is **not** a durable historical stream and does not have a second source sequence.
The containing \`DN_PACKET.packetId\` provides delivery identity; it does not become a
RaceData revision or a TimingData sequence.

Each RACE_DATA message carries one message-level \`LocationId\`. The LocationId identifies
the WP context for which Central created that message; individual team/stage-start
changes remain keyed by RegistrationId and do not repeat LocationId.

The current RaceData payload can contain one or more incremental change sections:

- \`teamAssignments\` changes the live RegistrationId -> TeamId assignment;
- \`stageStartTimes\` changes RegistrationId-scoped stage-start definitions.

Each change uses an explicit operation such as \`SET\` or \`DEL\`. One RACE_DATA message
carries **1..16 changes total** across all supported sections. Absence of a section means
no change to that part of RaceData.

The reserve mapping is keyed by RegistrationId rather than physical TagId because stable
EventData already resolves physical tags to the registration identity. RaceData supplies
only the live RegistrationId -> TeamId assignment. A RegistrationId that already resolves
to a stable TeamId through EventData shall not be remapped by RaceData.

Normal Central-to-node delivery uses stop-and-wait semantics. For each TimingNode, Central
keeps at most one positive-ID DN_PACKET outstanding. It does not send the next normal
positive-ID DN_PACKET until the current one has been confirmed by RECV. If confirmation
is not received, Central may resend the **same packet with the same packetId and semantic
content**.

SI-01 applies a new RACE_DATA packet only after the complete message has validated. It
then confirms the containing downstream packet with RECV. If that RECV is lost and the
same DN_PACKET is received again, SI-01 must not apply the same changes twice; it repeats
the confirmation for the already processed packet.

Central therefore does not need a retained history of old RACE_DATA packets. It keeps its
current race state plus the exact outstanding downstream packet needed for retry. Changes
to Central state while a packet is outstanding make later output dirty; they do not mutate
the outstanding packet. After the outstanding packet is confirmed, Central can construct
the next packet from its current state.

A full downstream state resend is explicitly requested with RECV position 0. Central then
rebuilds the applicable current downstream state rather than replaying a historical
RACE_DATA sequence. Exact snapshot segmentation is a representation/design concern, but
a state change during that resend must not rewrite an already sent packet.


### TimingData sequence and replay

Application-data synchronization in the current baseline applies only to
\`TIMING_DATA\`. The authoritative sequence is the existing IF-05/LogBook sequence for
one NodeId; IF-06 does not create another TimingData source sequence.

\`SEQ\` exchanges the current TIMING_DATA position and has three operations:

- \`REQ\`: ask the peer for its current TIMING_DATA position;
- \`ANS\`: answer a preceding REQ with \`seq = N\`;
- \`NTF\`: proactively notify the peer that the sender's current position is \`seq = N\`.

The meaning of the position follows the direction:

- SI-01 reports its current LogBook/IF-05 source head;
- Central reports the highest contiguous TIMING_DATA sequence it has accepted/processed.

Sequence 0 means that side currently has no TIMING_DATA position. REQ itself carries no
sequence. ANS and NTF carry the current sequence.

Either peer may send \`SEQ REQ\`. This allows Central to ask how many committed LogBook
records currently exist and allows SI-01 to ask how far Central has processed. SI-01 may
also send \`SEQ NTF\` when its LogBook head advances.

Actual record replay is a separate \`TIMING_DATA_REQ\` operation. Central sends
\`TIMING_DATA_REQ(fromSeq=N)\` to request retained TimingData beginning at IF-05 sequence
N. SI-01 answers with one or more bounded TIMING_DATA messages containing the original
records and identities.

The LogBook remains the replay source. After a fresh connection/sequence exchange,
Central sends TIMING_DATA_REQ from its next expected sequence even when it is already
caught up. That request is the replay-to-live handoff barrier. When SI-01 handles it,
SI-01 captures its current LogBook head and replays from \`fromSeq\` through that captured
head. Records committed after the captured head are sent only after that replay range has
completed. When \`fromSeq\` is exactly one greater than the captured head, the replay
range is empty and the handoff completes immediately.

Loss does not require a second durable TimingData outbox. Central can request retained
TimingData again from the LogBook. Retransmission preserves the original IF-05 record
identity and content.

RACE_DATA is deliberately not synchronized by SEQ. Its recovery uses DN_PACKET delivery,
RECV/resend and, when the node no longer trusts its downstream state, an explicit full
state resend request.

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
| \`IF06-OP-01 DELIVER_TIMING_DATA\` | SI-01 -> Central System | deliver committed TimingData without changing IF-05 identity/order |
| \`IF06-OP-02 APPLY_RACE_DATA\` | Central System -> SI-01 | validate and apply current RaceData carried by one downstream packet |
| \`IF06-OP-03 TIMING_DATA_SEQUENCE\` | bidirectional | request, answer or notify the current TIMING_DATA sequence position |
| \`IF06-OP-04 STATUS\` | bidirectional | exchange/observe integration status |
| \`IF06-OP-05 PING_REQUEST\` | bidirectional | initiate PING with op REQ and optional HB mode |
| \`IF06-OP-06 PING_ANSWER\` | bidirectional | answer a PING request with op ANS, retaining the request's optional mode |
| \`IF06-OP-07 RECV\` | SI-01 -> Central System | confirm the last processed normal DN_PACKET or request full downstream state resend |
| \`IF06-OP-08 REQUEST_TIMING_DATA\` | Central System -> SI-01 | request retained TimingData beginning at sequence N |

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

### IF06-OP-02 APPLY_RACE_DATA

Input:

- addressed TimingNode;
- message-level LocationId identifying the WP context;
- **1..16** current RaceData changes total across all change sections;
- containing DN_PACKET delivery identity.

Outcome:

- a new valid packet: apply all changes as one unit, then confirm the containing
  downstream packet with RECV;
- a resend of an already processed packet: do not apply again; repeat RECV;
- invalid semantic content: do not advance the accepted downstream packet position and
  expose a diagnosable rejection/conflict.

RACE_DATA itself has no source sequence and no historical replay obligation.

### IF06-OP-03 TIMING_DATA_SEQUENCE

This bidirectional operation uses the SEQ message:

- \`op = REQ\`: ask the peer for its current TIMING_DATA position;
- \`op = ANS, seq = N\`: answer a request;
- \`op = NTF, seq = N\`: notify a new/current position without a request.

For SI-01, N is its LogBook/IF-05 source head. For Central, N is the highest contiguous
TIMING_DATA sequence it has accepted/processed. Sequence 0 means no position yet.

### IF06-OP-07 RECV

RECV refers to downstream delivery, not to TimingData source identity. A positive value
confirms the last normal DN_PACKET that SI-01 has successfully processed. Central keeps
at most one positive-ID downstream packet outstanding and resends that exact packet when
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
- \`fromSeq >= 1\`.

Central uses it to request LogBook TimingData beginning at IF-05 sequence \`fromSeq\`.
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

IF-06 shall support Central System-to-SI-01 RACE_DATA messages with explicit NodeId,
message-level LocationId, positive ordered source sequence and incremental race-state
changes. LocationId supplies the WP context for the whole message while individual
changes remain RegistrationId-scoped. RaceData source ordering shall be independent
from TimingData source ordering.
:::

:::{ifreq} Explicit reference-data outcome  
:id: IF06-REQ-005  
:status: D  

A RACE_DATA message shall have an observable applied, duplicate, gap or rejected
outcome. SI-01 shall acknowledge only contiguously applied RaceData and shall expose
enough reason/status information to diagnose a gap or invalid change.
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

For one NodeId, SYNC shall advertise the current source head of one ordered stream.
TIMING_DATA uses the TimingNode's existing IF-05/LogBook sequence and RACE_DATA uses
the Central System's RaceData source sequence. Sequence 0 shall mean that the selected
source stream currently contains no data. A receiver behind that head shall use REQ
from its first missing sequence.
:::

:::{ifreq} Keep transport acknowledgement separate from semantic acknowledgement  
:id: IF06-REQ-018  
:status: D  

Transport/session delivery success shall not replace source-sequence synchronization.
For RACE_DATA, only successful ordered semantic application advances the ACK point.
For TIMING_DATA, retained LogBook records remain replayable until the Central System
no longer requests them during source synchronization.
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

IF-06 shall support bidirectional REQ by source sequence. Central System shall be able
to request TIMING_DATA from an IF-05/LogBook sequence and SI-01 shall be able to request
RACE_DATA from a Central source sequence. A request from sequence 1 shall mean replay
from the retained beginning of that stream.
:::

:::{ifreq} Re-establish synchronization after connection changes  
:id: IF06-REQ-021  
:status: D  

When an upstream semantic connection is established or re-established, the peers
shall exchange fresh SYNC source-head state for the applicable TimingNodes. For
TIMING_DATA, Central System shall answer each fresh SI-01 source-head SYNC with REQ from
its next expected sequence even when Central is already caught up. SI-01 shall capture
its current LogBook head when handling that REQ, replay through that captured head, and
shall not proactively send later committed TimingData until that replay handoff has
completed. For RACE_DATA, a receiver that is behind shall request missing data with REQ.
Progress remembered from an earlier transport/session shall not cause either source
sequence to be skipped.
:::

:::{ifreq} Bound IF-06 data-message size  
:id: IF06-REQ-022  
:status: D  

One TIMING_DATA message shall carry at most 16 TimingData records. One RACE_DATA
message shall carry at most 16 incremental changes total across all supported change
sections. A producer with more retained records or changes shall split them across
multiple ordered messages without changing the underlying TimingData or RACE_DATA
source sequences.
:::

:::{ifreq} Ordered RaceData application and acknowledgement  
:id: IF06-REQ-014  
:status: D  

Each node-scoped RACE_DATA message shall carry a positive Central-owned source sequence.
SI-01 shall apply only the next expected sequence, advance its contiguous RaceData
position only after successful application, and then acknowledge that applied sequence.
A duplicate shall not be applied twice. A sequence gap shall not be skipped and shall
cause a RACE_DATA request from the first missing sequence.
:::

:::{ifreq} Separate stable EventData from live RaceData  
:id: IF06-REQ-015  
:status: D  

RACE_DATA shall be able to carry incremental TeamAssignments changes as
RegistrationId-to-TeamId assignments that are not stable EventData profile identity.
The semantic contract is generic and does not classify an assignment by tag type.
It shall not redefine a stable RegistrationId-to-TeamId mapping supplied by EventData.
Physical TagIds remain resolved to their RegistrationId by EventData.
:::

:::{ifreq} Define StageStartTimes reference semantics  
:id: IF06-REQ-016  
:status: D  

RACE_DATA shall be able to carry incremental RegistrationId-scoped stage-start-time changes.
The message-level LocationId supplies the WP context in which those definitions are sent;
the individual change remains keyed by RegistrationId. The RegistrationId is the timing-domain
identity whose start is being defined; consumers shall not need an intermediate TeamId lookup
to match a registration to its stage start.
A SET shall carry one `TimingTimestamp` value containing at least local race
time-of-day. The timestamp may also contain a local date or already be absolute
when the source knows that information. A source that knows only time-of-day
shall remain valid; no transport or codec layer shall invent a date or time zone.
DEL removes the current definition. Elapsed-time and race-time-zone interpretation
belong to SI-01 domain behaviour, not to transport or codec layers.
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
:::

## Open points

- Exact operational retry/backoff timing for repeated REQ/ACK when a peer remains
  unavailable; source ordering and replay semantics are defined while connector timing
  remains an implementation concern.
- Whether all status is exchanged as UpstreamData or some connector diagnostics remain
  local-only implementation status.
- Timeout/health policy for missing or late PING ANSWER messages.

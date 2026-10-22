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
| TimingData transfer | SI-01 -> Central System | transfer committed TimingData records using their existing LogBook/IF-05 sequence |
| RaceData transfer | Central System -> SI-01 | transfer ordered incremental race-state changes using a Central-owned source sequence |
| SYNC | bidirectional | advertise the current source head of one ordered stream |
| ACK | SI-01 -> Central System | acknowledge contiguously applied RaceData through a sequence number |
| REQ | bidirectional | request retransmission of TIMING_DATA or RACE_DATA from a sequence number |
| Ping request / answer | bidirectional | one PING family with REQ/ANS op and an optional HB heartbeat mode; mode absence denotes a manual check |
| Status | bidirectional | expose upstream/source synchronization and connector health relevant to integration |

The public RaceData and synchronization semantics are defined below. Their
representations must remain compatible with the common requirements in this ISD.

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

### RaceData relationship

`RACE_DATA` is the ordered Central System -> SI-01 stream for live race-state
changes owned by one addressed TimingNode. It is **not** a complete snapshot and
does not carry a separate revision number.

Each RACE_DATA message carries one positive source `seq` for that NodeId. The
Central System allocates this sequence monotonically starting at 1. SI-01 keeps the
highest contiguously applied RaceData sequence for each TimingNode.

The current v1 RaceData payload can contain one or more incremental change sections:

- `teamAssignments` changes the live RegistrationId -> TeamId assignment;
- `stageStartTimes` changes RegistrationId-scoped stage-start definitions.

Each change uses an explicit operation such as `SET` or `DEL`. Absence of a
section means no change to that part of RaceData. Receiving a RACE_DATA message
therefore never implies that omitted state must be cleared.

The reserve mapping is keyed by RegistrationId rather than physical TagId because
stable EventData already resolves both reserve tags, for example
`TT-R-0001-1/2 -> RT-R-0001`. RaceData supplies only the live
`RT-R-0001 -> TeamId` assignment. A RegistrationId that already resolves to a
stable TeamId through EventData shall not be remapped by RaceData.

A RACE_DATA message is validated as one ordered unit before its sequence advances:

- `seq = lastApplied + 1`: validate and apply all changes; only after successful
  application advance `lastApplied` and send ACK for that sequence;
- `seq <= lastApplied`: do not apply the changes again; the receiver may repeat
  its current cumulative ACK;
- `seq > lastApplied + 1`: a gap exists; do not apply the out-of-order message and
  request RACE_DATA again from `lastApplied + 1`.

This makes loss detectable without repeatedly sending the full race state. If SI-01
does not persist RaceData across a restart, it starts with RaceData sequence 0 and
can rebuild state by requesting RACE_DATA from sequence 1.

### Data synchronization

Synchronization uses the **existing source sequence of each stream**. IF-06 does not
create one generic delivery sequence over all message types.

The two ordered streams are:

- `TIMING_DATA`: SI-01 -> Central System, ordered by the existing IF-05/LogBook
  `seqNr` for one NodeId;
- `RACE_DATA`: Central System -> SI-01, ordered by the Central-owned RACE_DATA
  `seq` for one NodeId.

`SYNC` advertises the sender's current source head for one stream. Sequence 0 means
that source currently has no records/messages for the addressed TimingNode.

The receiving peer compares that source head with its own highest contiguous received
or applied sequence. When it is behind, it sends `REQ` for that stream from the first
missing sequence:

- Central System -> SI-01: `REQ(stream=TIMING_DATA, fromSeq=N)` requests LogBook
  TimingData beginning at IF-05 `seqNr=N`;
- SI-01 -> Central System: `REQ(stream=RACE_DATA, fromSeq=N)` requests Central
  RaceData beginning at RACE_DATA `seq=N`.

`fromSeq=1` therefore means “send the complete retained stream from its beginning”.
A deployment-specific legacy codec may map this semantic request to an older special
wire value such as a RECV/package-id value of `0000`; that legacy sentinel is not
the public source sequence itself.

For RaceData, `ACK(stream=RACE_DATA, seq=N)` confirms that SI-01 has successfully
applied the stream contiguously through N. ACK is sent only after semantic application;
transport/session delivery acknowledgement is not a substitute. A sequence gap causes
REQ rather than advancement of the ACK point.

For TimingData, the LogBook remains the authoritative replay source. SI-01 may publish
newly committed records proactively, but loss does not require a second durable outbox:
after reconnect or SYNC, the Central System can request any retained TimingData sequence
again through REQ. Retransmission preserves the original IF-05 record identity and
content.

PING, ACK, REQ and SYNC are control messages. They do not consume TimingData `seqNr`
or RaceData `seq` values themselves.

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
| `IF06-OP-01 DELIVER_TIMING_DATA` | SI-01 -> Central System | deliver committed TimingData without changing IF-05 identity/order |
| `IF06-OP-02 APPLY_RACE_DATA` | Central System -> SI-01 | validate and apply one ordered incremental RaceData message |
| `IF06-OP-03 SYNC` | bidirectional | advertise one source stream's current head sequence |
| `IF06-OP-04 STATUS` | bidirectional | exchange/observe integration status |
| `IF06-OP-05 PING_REQUEST` | bidirectional | initiate PING with op REQ and optional HB mode |
| `IF06-OP-06 PING_ANSWER` | bidirectional | answer a PING request with op ANS, retaining the request's optional mode |
| `IF06-OP-07 ACK` | SI-01 -> Central System | acknowledge contiguously applied RACE_DATA through sequence N |
| `IF06-OP-08 REQ` | bidirectional | request TIMING_DATA or RACE_DATA retransmission from sequence N |

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

### IF06-OP-02 APPLY_RACE_DATA

Input:

- addressed TimingNode;
- positive Central-owned RACE_DATA `seq`;
- one or more incremental RaceData changes.

Outcome:

- next expected sequence and all changes valid: apply the message as one ordered unit,
  advance the contiguous RaceData sequence and emit ACK;
- duplicate/already-applied sequence: do not apply again; cumulative ACK may be repeated;
- sequence gap: do not apply the message and issue REQ RACE_DATA from the first missing
  sequence;
- semantically invalid change: do not advance the sequence and expose a diagnosable
  rejection/conflict.

### IF06-OP-03 SYNC

This bidirectional operation advertises one source stream's current head for an
addressed TimingNode:

- `stream = TIMING_DATA`: the TimingNode's current LogBook/IF-05 source head;
- `stream = RACE_DATA`: the Central System's current RaceData source head.

Sequence 0 means no data currently exists in that source stream. A receiver that is
behind requests the missing range with IF06-OP-08 REQ. SYNC itself does not replay
payloads and does not consume either source sequence.

### IF06-OP-07 ACK

ACK confirms semantic application of an ordered source stream. In public v1 the
required use is SI-01 acknowledging RACE_DATA. The ACK carries the addressed NodeId,
`stream = RACE_DATA` and the highest contiguous sequence successfully applied.

### IF06-OP-08 REQ

REQ is bidirectional and carries:

- addressed TimingNode;
- `stream = TIMING_DATA | RACE_DATA`;
- `fromSeq >= 1`.

Central System uses TIMING_DATA REQ to request LogBook records beginning at IF-05
sequence `fromSeq`. SI-01 uses RACE_DATA REQ to request Central messages beginning
at RaceData sequence `fromSeq`. `fromSeq=1` means resend the retained stream from
its beginning.

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
positive ordered source sequence and incremental race-state changes. RaceData source
ordering shall be independent from TimingData source ordering.
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
shall exchange fresh SYNC source-head state for the applicable TimingNodes. Each
receiver shall compare the advertised source head with its own highest contiguous
received/applied position and request missing data with REQ. Progress remembered from
an earlier transport/session shall not cause either source sequence to be skipped.
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
The RegistrationId is the timing-domain identity whose start is being defined; consumers shall
not need an intermediate TeamId lookup to match a registration to its stage start.
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

- Exact operational retry/backoff timing for repeated REQ/ACK when a peer remains
  unavailable; source ordering and replay semantics are defined while connector timing
  remains an implementation concern.
- Whether all status is exchanged as UpstreamData or some connector diagnostics remain
  local-only implementation status.
- Timeout/health policy for missing or late PING ANSWER messages.

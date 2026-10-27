# UpstreamData JSON Interface Design Description (IDD)

Status: draft

Representation: **default/reference v1 JSON**

System interface: **IF-06 — Backend Integration**

## Purpose

This Interface Design Description defines the public/default JSON representation of
IF-06 UpstreamData.

The matching ISD owns the semantic contract. This IDD defines only the public/reference
representation used by development, SI-02 engineering tooling and integration tests.

The representation is deliberately generic. It does not encode deployment-specific
queue names, private identifiers or proprietary protocol fields.

## Relationship to other documents

This IDD implements the public/default representation of
`32-06-ISD-backend-integration.md`.

Contained TimingData values conform to IF-05 and its public/default JSON mapping in
`32-05-ISD-timingdata-interchange.md` and
`33-05-IDD-timingdata-interchange.md`.

Connector/session realization belongs to
`43-01-SDD-03-backoffice-transport-design.md`.

The shared odd/even maturity convention for integer JSON `v` fields is defined by
`12-GPD-documentation-guide.md`. This IDD remains the authority for the concrete IF-06
representation.


## Design baseline

The packet-oriented default/reference representation is version **1**. It uses one
UTF-8 JSON packet shape with an explicit direction:

- `UP_PACKET`: SI-01 -> Central System;
- `DN_PACKET`: Central System -> SI-01.

Each packet carries exactly one semantic message in v1. Keeping one semantic message per
packet makes packet numbering unambiguous and makes the PING isolation rule explicit.

A normal packet has this shape:

```json
{
  "v": 1,
  "type": "DN_PACKET",
  "nodeId": "A",
  "pckNr": 42,
  "msg": {
    "type": "SEQ",
    "data": {
      "op": "ANS",
      "seq": 1186
    }
  }
}
```

Top-level members:

| Member | Type | Meaning |
| --- | --- | --- |
| `v` | integer | IF-06 JSON representation version; current development value is 1 |
| `type` | `UP_PACKET` or `DN_PACKET` | packet direction |
| `nodeId` | string | TimingNode owning/addressed by this packet |
| `pckNr` | integer | packet delivery/debug number; 0 is reserved for PING |
| `msg` | object | exactly one semantic IF-06 message |

The wire name `pckNr` denotes packet delivery/debug number (`packetNr` in the typed Java model), while `seqNr` remains the IF-05 TimingData/LogBook sequence. The RECV wire name `rcvPckNr` denotes `receivedPacketNr` in the typed semantic model.

The packet number is separate from TimingData identity. In particular,
`pckNr=42` does not imply TimingData sequence 42.

Both directions use packet numbers because they materially improve engineering traces and
message inspection. In the current baseline only positive DN_PACKET numbers participate in
RECV/resend. UP_PACKET numbers are visible delivery/debug numbers and are not themselves
acknowledged.

Normal positive DN_PACKET numbers advance in send order. Central keeps at most one positive
DN_PACKET unconfirmed for a TimingNode. It does not advance to the next normal downstream
packet until the outstanding packet has been confirmed. A resend uses the same packetNr
and the same semantic message.

Packet number 0 is reserved for PING packets. A PING packet does not consume the normal
positive packet counter and is not confirmed with RECV.

## Message families

The semantic message object reserves:

- `TIMING_DATA`;
- `TIMING_DATA_REQ`;
- `SEQ` (REQ, ANS and NTF);
- `TEAM_ASSIGNMENTS`;
- `STAGE_STARTS`;
- `RECV`;
- `PING` (REQ and ANS);
- `STATUS`.

### TIMING_DATA

TIMING_DATA ordinarily travels in an UP_PACKET and carries **1..16** committed
TimingData values as elements of its `data` array.

```json
{
  "v": 1,
  "type": "UP_PACKET",
  "nodeId": "A",
  "pckNr": 57,
  "msg": {
    "type": "TIMING_DATA",
    "data": [
      {
        "v": 1,
        "nodeId": "A",
        "seqNr": 42,
        "locId": 1,
        "recType": "AUTO_REG",
        "time": "2026-10-13T08:00:00.00Z",
        "regId": "A0042",
        "code": ["ADD"],
        "recTime": "2026-10-13T08:00:00.123Z"
      }
    ]
  }
}
```

The child values are the public IF-05 TimingData records themselves; IF-06 does not
define a second record mapping. In the default writer their record timestamps therefore
remain canonical UTC: `time` is the IF-05 effective time. Optional `recTime` is
record-creation/debug metadata when present. Both use literal `Z`. Batching never creates another TimingData
sequence; the original `seqNr` remains the record identity/order.

### TIMING_DATA_REQ

Central requests retained TimingData with a normal DN_PACKET:

```json
{
  "v": 1,
  "type": "DN_PACKET",
  "nodeId": "A",
  "pckNr": 41,
  "msg": {
    "type": "TIMING_DATA_REQ",
    "data": {
      "fromSeq": 1171
    }
  }
}
```

`fromSeq` is inclusive and uses the IF-05/LogBook sequence. The request itself has no
TimingData source sequence.

Because this is a normal positive-numbered DN_PACKET, SI-01 confirms processing of the request
with RECV in its own UP_PACKET. Serving the requested TIMING_DATA remains a separate
semantic action from confirming receipt of the request packet.

### SEQ

SEQ exchanges the current TIMING_DATA position and has one required `op`:

| op | seq | Meaning |
| --- | --- | --- |
| `REQ` | absent | ask the peer for its current TIMING_DATA position |
| `ANS` | required | answer a SEQ REQ |
| `NTF` | required | notify the peer of the sender's current position |

Request:

```json
{
  "v": 1,
  "type": "DN_PACKET",
  "nodeId": "A",
  "pckNr": 42,
  "msg": {
    "type": "SEQ",
    "data": {
      "op": "REQ"
    }
  }
}
```

Answer:

```json
{
  "v": 1,
  "type": "UP_PACKET",
  "nodeId": "A",
  "pckNr": 58,
  "msg": {
    "type": "SEQ",
    "data": {
      "op": "ANS",
      "seq": 1186
    }
  }
}
```

The same family works in either direction. SI-01's sequence value is its current
LogBook/IF-05 head. Central's sequence value is the highest contiguous TIMING_DATA
sequence it has accepted/processed. `seq=0` means no position yet.

A SEQ message never refers to TEAM_ASSIGNMENTS or STAGE_STARTS.

On a fresh or re-established upstream session, SI-01 may notify its current source head
with SEQ NTF. Central compares that value with its highest contiguous processed position.
If Central is behind it requests the missing suffix with TIMING_DATA_REQ. If both values
are equal, Central does not need to send a synchronization message back. SEQ reports
positions; it does not itself pause or resume proactive live TIMING_DATA forwarding.
A real TIMING_DATA_REQ temporarily pauses live forwarding while its captured replay range
is served, after which live forwarding resumes from the next sequence.

### TEAM_ASSIGNMENTS

TEAM_ASSIGNMENTS travels in a normal DN_PACKET and carries current live
RegistrationId-to-TeamId assignment changes for the addressed TimingNode.

```json
{
  "v": 1,
  "type": "DN_PACKET",
  "nodeId": "A",
  "pckNr": 43,
  "msg": {
    "type": "TEAM_ASSIGNMENTS",
    "data": [
      {
        "op": "SET",
        "regId": "R0001",
        "teamId": "0042"
      }
    ]
  }
}
```

One TEAM_ASSIGNMENTS message carries **1..16** SET/DEL changes. The message has no
LocationId: an assignment is node-scoped current state keyed by RegistrationId, not by
the currently open WP.

TEAM_ASSIGNMENTS is current-state delivery, not retained source-history synchronization.
Central therefore need not retain old assignment packets after confirmation. It keeps the
current assignment state plus the exact outstanding packet required for retry.

### STAGE_STARTS

STAGE_STARTS travels in a normal DN_PACKET and carries current RegistrationId-scoped
stage-start definitions for the addressed TimingNode.

```json
{
  "v": 1,
  "type": "DN_PACKET",
  "nodeId": "A",
  "pckNr": 44,
  "msg": {
    "type": "STAGE_STARTS",
    "data": [
      {
        "op": "SET",
        "regId": "R0001",
        "start": "23:59:50.00"
      }
    ]
  }
}
```

One STAGE_STARTS message carries **1..16** SET/DEL changes. It carries neither
LocationId nor StageId. Central source state is nevertheless StageId-scoped. Before
constructing the message, Central selects the stage applicable to the addressed TimingNode's
current runtime context; under the current event mapping, OPEN LocationId N selects Stage N.
The message then carries only that stage's RegistrationId-scoped start projection.

A resent DN_PACKET is identified by the same pckNr and must not cause the same changes
to be applied twice. STAGE_STARTS has no independent source sequence and no historical
replay obligation.

### RECV

RECV is an UP_PACKET semantic message referring to downstream delivery:

```json
{
  "v": 1,
  "type": "UP_PACKET",
  "nodeId": "A",
  "pckNr": 59,
  "msg": {
    "type": "RECV",
    "data": {
      "rcvPckNr": 43
    }
  }
}
```

The outer `pckNr=59` identifies this upstream packet for tracing. The inner
`rcvSeqNr=43` is the downstream packet position being reported.

For a positive value, `rcvPckNr` is the last normal DN_PACKET that SI-01 has
successfully processed. In the normal stop-and-wait flow it equals Central's outstanding
packet number and confirms that packet. If confirmation is lost and Central resends the same
packet, SI-01 repeats RECV without reapplying the semantic message.

A receiver that detects it cannot advance because an earlier downstream packet is still
missing reports its last successfully processed downstream packet. Under the normal
stop-and-wait rule Central never sends packet N+1 before N is confirmed.

`rcvSeqNr=0` is special: it is not acknowledgement of a normal DN_PACKET. It
requests that Central rebuild and resend the applicable current downstream state. It
does not request historical TEAM_ASSIGNMENTS or STAGE_STARTS by source sequence.

### PING

PING is carried in a packet with `pckNr=0` in either direction. It has `op=REQ|ANS`,
optional `mode=HB`, optional absolute UTC `time` and optional `pingId`.

Request:

```json
{
  "v": 1,
  "type": "UP_PACKET",
  "nodeId": "A",
  "pckNr": 0,
  "msg": {
    "type": "PING",
    "data": {
      "op": "REQ",
      "mode": "HB",
      "time": "2026-10-24T14:12:00.123Z"
    }
  }
}
```

Answer:

```json
{
  "v": 1,
  "type": "DN_PACKET",
  "nodeId": "A",
  "pckNr": 0,
  "msg": {
    "type": "PING",
    "data": {
      "op": "ANS",
      "mode": "HB",
      "time": "2026-10-24T14:12:00.130Z"
    }
  }
}
```

A PING REQ is answered immediately. PING packets are not followed by RECV and do not
consume the normal positive packet-id sequence. Each packet already carries one
semantic message, so a PING packet cannot contain another message.

### STATUS

STATUS payload members remain an open design point. STATUS, when defined, uses an
ordinary UP_PACKET or DN_PACKET according to direction.


## JSON rules

The packet-oriented default/reference writer:

- emits UTF-8 JSON without BOM;
- emits integer `v = 1` for the current unstable/development representation;
- emits top-level `type = UP_PACKET | DN_PACKET`;
- emits one NodeId and one packetNr;
- emits exactly one semantic `msg`;
- uses positive pckNr for ordinary packets and pckNr 0 only for PING;
- emits at most 16 TimingData records, 16 TEAM_ASSIGNMENTS changes, or 16 STAGE_STARTS changes in one semantic message;
- does not copy transport-specific routing/session metadata into semantic message content.

The reader:

- rejects malformed JSON;
- rejects missing required members;
- rejects unsupported `v` representation versions;
- rejects pckNr 0 for non-PING messages;
- rejects a positive-numbered PING packet;
- rejects unknown semantic message types as unsupported rather than reinterpreting them;
- may ignore unknown additional members when all required known members remain valid.

## TimingData composition

The public UpstreamData codec shall compose the public TimingData representation rather
than invent another timing-record mapping.

Conceptually:

```text
DefaultUpstreamDataCodec
        |
        +--> DefaultTimingDataCodec
```

This relationship is representation composition only. IF-05 remains the semantic
authority for TimingData.

## Transport mapping

The same UpstreamData JSON envelope is used for inbound and outbound
messages; only its `type`, payload and any type-dependent scope differ. The
encoded semantic object can be carried by different connector transports.
Transport-specific or deployment-specific direction-dependent framing belongs
in the adapter/codec rather than defining a second default message format.

### Engineering IF-03 transport

The Engineering API connector may map inbound UpstreamData to an IF-03 HTTP request and
outbound UpstreamData to a typed IF-03 WebSocket event.

The WebSocket event carries structured UpstreamData JSON; it does not tunnel a
pre-serialized RabbitMQ/private message as an opaque string.

### RabbitMQ transport

The RabbitMQ connector may use the encoded UpstreamData JSON as its public/reference
message body while RabbitMQ exchanges, queues, routing keys, delivery tags and connection
state remain transport metadata outside the UpstreamData JSON object.

SI-02 may use the same JSON representation when acting as the backend-side RabbitMQ test
peer.

## Provider / codec boundary

The public/default implementation is expected to expose a typed provider/codec family
parallel to the existing TimingData representation boundary:

```text
UpstreamDataProvider
  id()
  createCodec()

UpstreamDataCodec
  encode(UpstreamData)
  decode(bytes)
```

The built-in public provider uses stable id `reference` and the JSON v1 codec.

A deployment-specific provider may supply a different representation without changing
the public UpstreamData semantic model or requiring private representation classes in
public application/domain code.

Concrete Java package/API details remain SI-01 detailed design and are not normative
IF-06 interface requirements.


## Compatibility and versioning

The integer `v` identifies the default UpstreamData JSON representation version.

This project uses the shared representation-maturity convention from
`12-GPD-documentation-guide.md`: odd versions are development/unstable and even
versions are stable/released. The current IF-06 packet representation is therefore
`v = 1` while the contract remains under active development. Stabilizing this
representation will use the corresponding even version.

The earlier flat implementation shape with SYNC/ACK/REQ control families is not a
released compatibility baseline. It is superseded by this packet model and may be
migrated directly while IF-06 remains on the unstable development version.

A custom representation is not required to use JSON or this `v` member. It conforms
through preservation of the applicable IF-06 semantics, not by copying the default wire
format.

## ISD mapping

| IF-06 requirement | Default JSON realization |
| --- | --- |
| IF06-REQ-001 | v1 represents transport-independent IF-06 packet/message semantics |
| IF06-REQ-002 | TIMING_DATA embeds IF-05-compatible TimingData values |
| IF06-REQ-003 | pckNr remains separate from NodeId + IF-05 sequence identity |
| IF06-REQ-004/005 | TEAM_ASSIGNMENTS and STAGE_STARTS carry node-scoped current changes and are confirmed through their DN_PACKET |
| IF06-REQ-014 | positive DN_PACKET uses stop-and-wait RECV/resend |
| IF06-REQ-015 | TEAM_ASSIGNMENTS carries live RegistrationId -> TeamId SET/DEL changes |
| IF06-REQ-016 | STAGE_STARTS carries RegistrationId-scoped SET/DEL changes without LocationId |
| IF06-REQ-006/017 | SEQ REQ/ANS/NTF exchanges only the TIMING_DATA position |
| IF06-REQ-018 | both packet directions expose packetNr; only downstream packetNr participates in current RECV handling |
| IF06-REQ-019 | TIMING_DATA replay reuses original TimingData identity/content |
| IF06-REQ-020 | TIMING_DATA_REQ uses inclusive `fromSeq` |
| IF06-REQ-021 | fresh SEQ reports TIMING_DATA positions; Central uses TIMING_DATA_REQ only for a missing suffix, and replay temporarily pauses otherwise-live forwarding; RECV 0 requests current downstream-state resend |
| IF06-REQ-022 | TIMING_DATA, TEAM_ASSIGNMENTS and STAGE_STARTS each have their own 16-item message bound |
| IF06-REQ-007 | representation does not couple local TimingData commit to delivery |
| IF06-REQ-008 | v1 JSON is the packet-oriented public/default representation |
| IF06-REQ-009 | provider/codec boundary permits alternative representations |
| IF06-REQ-010 | the same packet/message semantics can be mapped to IF-03 or RabbitMQ |
| IF06-REQ-011/012/013 | PING uses pckNr 0, immediate REQ/ANS and no RECV |

## Open design points

- Final common STATUS JSON members.
- Whether TIMING_DATA remains single-source per message or permits an explicit
  multi-source batch envelope in a later version.

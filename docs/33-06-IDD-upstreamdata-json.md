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

## Design baseline

The default/reference representation uses **one UTF-8 JSON message format for
both directions** of IF-06. Every exchange uses the same envelope; its `type`
selects the message family and its `data` contains the type-specific payload.
The envelope is the message. A TimingData record (the semantic counterpart of
an individual log entry) is an item *inside* the `data` payload of a
`TIMING_DATA` message; it is not a second, unrelated top-level wire format.

The common envelope is intentionally small:

| Member | Type | Meaning |
| --- | --- | --- |
| `v` | integer | UpstreamData representation version |
| `type` | string | semantic message family/type |
| `nodeId` | string, type-dependent | addressed/owning TimingNode when the message is node-scoped |
| `data` | object/array, type-dependent | semantic payload |

The representation does not require a transport/delivery/session identifier in the
semantic envelope. A concrete transport may carry such metadata outside the encoded
UpstreamData object.

## Message families

The current public v1 design reserves these semantic families:

- `TIMING_DATA`;
- `REFERENCE_DATA`;
- `SYNC`;
- `PING` (REQUEST and ANSWER);
- `STATUS`.

Only fields whose semantics are promoted by the IF-06 ISD and its Step-7 refinements
become normative public members.

### TIMING_DATA

A TIMING_DATA message carries one or more committed TimingData values as elements
of its `data` array. The same envelope applies regardless of direction; this
family ordinarily flows from SI-01 to the backend. For example, one committed
record is one child of an UpstreamData message:

Conceptual JSON:

```json
{
  "v": 1,
  "type": "TIMING_DATA",
  "nodeId": "A",
  "data": [
    {
      "v": 1,
      "nodeId": "A",
      "seqNr": 42,
      "locId": 1,
      "recType": "AUTO_REG",
      "time": "2026-10-13T08:00:00.00Z",
      "regId": "RT-A-0042",
      "code": ["ADD"]
    }
  ]
}
```

The nested TimingData objects use the applicable public IF-05 JSON mapping. The
UpstreamData wrapper does not change their record key or source sequence.
The JSON representation does not serialize a LogBook file, nor wrap old LBR
text lines as opaque strings. It represents committed IF-05 records as structured
child objects of one UpstreamData message.

A batch may contain multiple records only from a semantically compatible source scope.
Batching is delivery convenience and never creates another TimingData sequence.

### REFERENCE_DATA

The envelope and type are reserved in v1. Exact RaceData/StageStartTimes members are
defined only after Step-7 D02 promotes their semantic contract.

### SYNC

The envelope and type are reserved in v1. Exact progress/acknowledgement members are
defined only after Step-7 D03 promotes synchronization semantics.

### PING (REQUEST / ANSWER)

PING uses the **same UpstreamData message type** in both directions and for both
request and answer. The `data` object has one required field and two optional fields:

| Member | Values | Meaning |
| --- | --- | --- |
| `action` | `REQUEST`, `ANSWER` (required) | initiates a check or answers one |
| `mode` | `HEARTBEAT` (optional) | marks a scheduled heartbeat; absence means a manual/explicit check |
| `pingId` | string (optional) | reference correlation token for a specific exchange |

PING is system/upstream-scoped and does not require `nodeId`. A receiver of
`action = REQUEST` issues one `action = ANSWER`. The answer preserves the
request's optional `mode`: if absent in the request, it is absent in the
answer. Neither party shall answer an ANSWER. A REQUEST may originate from
SI-01 or from the backend.

Heartbeat REQUEST:

```json
{
  "v": 1,
  "type": "PING",
  "data": {
    "action": "REQUEST",
    "mode": "HEARTBEAT"
  }
}
```

Heartbeat ANSWER:

```json
{
  "v": 1,
  "type": "PING",
  "data": {
    "action": "ANSWER",
    "mode": "HEARTBEAT"
  }
}
```

Manual REQUEST (no `mode`):

```json
{
  "v": 1,
  "type": "PING",
  "data": {
    "action": "REQUEST"
  }
}
```

Manual ANSWER:

```json
{
  "v": 1,
  "type": "PING",
  "data": {
    "action": "ANSWER"
  }
}
```

The default v1 reader accepts missing `mode` as manual/explicit. It rejects an
unsupported `mode` value rather than guessing it means manual. A manual request
does not reset the periodic heartbeat cycle. There is **no separate PONG
message family** in the default representation.

A reference implementation may include optional `pingId` on a REQUEST and
echo it on the corresponding ANSWER, for example `"pingId": "p-0001"`.
It is not mandatory IF-06 semantics, TimingData identity or transport sequence.
Legacy fixed-field protocol positions are not normative public JSON fields.

PING REQUEST/ANSWER carries no TimingData record and consumes no TimingData
sequence identity. Its lifecycle/timing semantics are defined by
IF06-REQ-011/012/013.

### STATUS

The envelope and type are reserved in v1. Common semantic status members are added only
when their interface meaning is stable.

## JSON rules

The default/reference v1 writer:

- emits UTF-8 JSON without BOM;
- emits integer `v = 1`;
- emits a known `type`;
- emits only members defined by the selected message family;
- emits semantic payload values without embedding transport-specific routing metadata.

The reader:

- rejects malformed JSON;
- rejects missing required members;
- rejects unsupported representation versions;
- reports unknown message types as unsupported rather than reinterpreting them;
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

Compatible additions may add optional members whose absence preserves existing meaning.
Breaking changes require another representation version.

A custom representation is not required to use JSON or this version member. It conforms
through preservation of the applicable IF-06 semantics, not by copying the default wire
format.

## ISD mapping

| IF-06 requirement | Default JSON realization |
| --- | --- |
| IF06-REQ-001 | JSON represents transport-independent UpstreamData |
| IF06-REQ-002 | TIMING_DATA embeds IF-05-compatible TimingData values |
| IF06-REQ-003 | no transport/session ID replaces Node ID + sequence |
| IF06-REQ-004/005 | REFERENCE_DATA family reserved for D02-defined semantic payload |
| IF06-REQ-006 | SYNC family reserved for D03-defined progress semantics |
| IF06-REQ-007 | representation does not couple local commit to transport delivery |
| IF06-REQ-008 | v1 JSON is the public/default representation |
| IF06-REQ-009 | provider/codec boundary permits alternative representations |
| IF06-REQ-010 | same JSON semantics can be mapped to IF-03 or RabbitMQ |
| IF06-REQ-011/012/013 | PING carries required action REQUEST/ANSWER and optional mode HEARTBEAT (omission means manual); optional `pingId` supports reference correlation without consuming TimingData identity |

## Open design points

- Final REFERENCE_DATA JSON members after D02.
- Final SYNC JSON members after D03.
- Final common STATUS JSON members.
- Whether TIMING_DATA remains single-source per message or permits an explicit
  multi-source batch envelope in a later version.

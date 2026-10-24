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
| `locationId` | integer, type-dependent | message-level WP context; required by RACE_DATA in public v1 |
| `seq` | integer, type-dependent | source sequence for an ordered top-level data stream; currently RACE_DATA |
| `data` | object/array, type-dependent | semantic payload |

The representation does not require a transport/delivery/session identifier in the
semantic envelope. A concrete transport may carry such metadata outside the encoded
UpstreamData object.

## Message families

The current public v1 design reserves these semantic families:

- `TIMING_DATA`;
- `RACE_DATA`;
- `SYNC`;
- `ACK`;
- `REQ`;
- `PING` (REQ and ANS);
- `STATUS`.

Only fields whose semantics are promoted by the IF-06 ISD and its Step-7 refinements
become normative public members.

### TIMING_DATA

A TIMING_DATA message carries **1..16** committed TimingData values as elements
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
      "regId": "A0042",
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

A batch contains at most 16 records and may contain records only from a
semantically compatible source scope. Batching is delivery convenience and never
creates another TimingData sequence. Larger replay ranges are split into multiple
TIMING_DATA messages.

### RACE_DATA

RACE_DATA is the ordered Central System -> SI-01 live race-state stream. It is
node-scoped and requires `nodeId`, one positive message-level `locationId`
and a positive top-level `seq`. The LocationId identifies the WP context for
the whole RACE_DATA message; individual changes remain keyed by RegistrationId.

Example:

```json
{
  "v": 1,
  "type": "RACE_DATA",
  "nodeId": "A",
  "locationId": 7,
  "seq": 123,
  "data": {
    "teamAssignments": [
      {
        "op": "SET",
        "regId": "R0001",
        "teamId": "0042"
      }
    ],
    "stageStartTimes": [
      {
        "op": "SET",
        "regId": "R0001",
        "start": "23:59:50.00"
      }
    ]
  }
}
```

`locationId` is the WP context in which Central created the message. It belongs
to the RACE_DATA message, not to every individual change. `seq` is the
Central-owned source order for RACE_DATA of the addressed TimingNode. It starts
at 1 and increases by one for each RaceData message. The JSON-safe range is
1..9007199254740991.

The `data` object contains **incremental changes**, not a complete snapshot. Supported
v1 sections are optional:

| Section | Key | Operations |
| --- | --- | --- |
| `teamAssignments` | `regId` | `SET` with `teamId`; `DEL` removes the assignment |
| `stageStartTimes` | `regId` | `SET` with one `start` TimingTimestamp value; `DEL` removes the definition |

At least one non-empty supported change section is required. One RACE_DATA
message contains **at most 16 changes total** across all supported sections.
A larger logical update is split into multiple consecutively sequenced
RACE_DATA messages. An omitted section means “no change”; it never means
“clear that entire state”.

Reserve-tag mapping example for removal:

```json
{
  "v": 1,
  "type": "RACE_DATA",
  "nodeId": "A",
  "locationId": 7,
  "seq": 124,
  "data": {
    "teamAssignments": [
      {
        "op": "DEL",
        "regId": "R0001"
      }
    ]
  }
}
```

Both RACE_DATA sections use `regId` as their timing-domain key. The top-level
`locationId` supplies the common WP context and is therefore not repeated
inside `teamAssignments` or `stageStartTimes`. EventData resolves physical
TagIds to RegistrationId, while `teamAssignments` optionally supplies a live
RegistrationId-to-TeamId relationship. A stage start belongs directly to the RegistrationId;
its lookup does not depend on whether a TeamId is fixed in EventData or assigned live.
The UpstreamData contract does not classify a live assignment as a special reserve-tag concept.

Because the public/reference v1 contract is still draft, this correction changes draft v1
directly. A `stageStartTimes` item that carries only `teamId` does not conform and is rejected;
there is no compatibility alias that silently restores the old key.

`start` is one textual `TimingTimestamp` value. The default v1 profile accepts:
- time-only: `HH:mm:ss[.fraction]`;
- local date/time: `YYYY-MM-DDTHH:mm:ss[.fraction]`;
- absolute UTC: `YYYY-MM-DDTHH:mm:ss[.fraction]Z`.

A source may provide time-only data; the codec shall not invent a date or zone.
SI-01 StageTiming owns any event/race-time-zone and rollover interpretation needed
to calculate an absolute start.

One RACE_DATA message is validated and applied as one ordered unit. A sequence gap is
not silently skipped and the message is not partially applied before its ACK point
advances.

### SYNC

SYNC advertises the source head of one ordered stream for one `nodeId`.

TimingNode -> Central System:

```json
{
  "v": 1,
  "type": "SYNC",
  "nodeId": "A",
  "data": {
    "stream": "TIMING_DATA",
    "seq": 42
  }
}
```

Central System -> TimingNode:

```json
{
  "v": 1,
  "type": "SYNC",
  "nodeId": "A",
  "data": {
    "stream": "RACE_DATA",
    "seq": 123
  }
}
```

Members:

| Member | Values | Meaning |
| --- | --- | --- |
| `stream` | `TIMING_DATA`, `RACE_DATA` | source stream being advertised |
| `seq` | integer 0..9007199254740991 | current highest source sequence; 0 means the source stream is empty |

For TIMING_DATA, `seq` is the TimingNode's LogBook/IF-05 source head. For RACE_DATA,
`seq` is the Central System's RaceData source head. A receiver that is behind uses
REQ from its first missing sequence.

For the SI-01 -> Central TIMING_DATA stream, Central also sends REQ when it is already
caught up: `fromSeq = centralHead + 1`. This empty-range request is the explicit
replay-to-live handoff barrier. SI-01 captures its current LogBook head while handling
the REQ, so a record committed after SYNC but before REQ joins replay rather than
arriving early as live data. Proactive live TIMING_DATA resumes only after that captured
replay range has completed.

SYNC carries no stream payload and consumes no source sequence itself.

### ACK

ACK confirms ordered semantic application. Public v1 requires ACK for the
Central System -> SI-01 RACE_DATA stream.

```json
{
  "v": 1,
  "type": "ACK",
  "nodeId": "A",
  "data": {
    "stream": "RACE_DATA",
    "seq": 123
  }
}
```

`seq` means that SI-01 has successfully applied RACE_DATA contiguously through that
sequence. ACK is emitted only after semantic application. Re-receiving an already
applied RaceData message does not apply it again; SI-01 may repeat its cumulative ACK.

### REQ

REQ is bidirectional and requests retransmission from one source sequence.

Central System requests TimingData:

```json
{
  "v": 1,
  "type": "REQ",
  "nodeId": "A",
  "data": {
    "stream": "TIMING_DATA",
    "fromSeq": 41
  }
}
```

TimingNode requests RaceData:

```json
{
  "v": 1,
  "type": "REQ",
  "nodeId": "A",
  "data": {
    "stream": "RACE_DATA",
    "fromSeq": 121
  }
}
```

`fromSeq` is in the range 1..9007199254740991 and is inclusive. `fromSeq = 1`
means replay from the retained beginning of the selected stream. For TIMING_DATA,
Central sends `fromSeq = centralHead + 1` after each fresh source-head SYNC, including
when the advertised source head equals `centralHead`. SI-01 captures its current
LogBook head on that request and completes replay through the captured head before
proactive live forwarding resumes.

A deployment-specific legacy codec may map the semantic request

```text
REQ stream=TIMING_DATA fromSeq=1
```

to a legacy “receive all” sentinel such as `RECV package-id = 0000`, and decode
that sentinel back to the same semantic request. The public source sequence still
starts at 1; `0000` remains a legacy wire representation detail. Arbitrary
`fromSeq` values are available only when the selected legacy representation can
express them.

### PING (REQUEST / ANSWER)

PING uses the **same UpstreamData message type** in both directions and for both
request and answer. The `data` object has one required field and two optional fields:

| Member | Values | Meaning |
| --- | --- | --- |
| `op` | `REQ`, `ANS` (required) | request or answer |
| `mode` | `HB` (optional) | scheduled heartbeat; absence means manual/explicit |
| `pingId` | string (optional) | reference correlation token for a specific exchange |

PING is system/upstream-scoped and does not require `nodeId`. A receiver of
`op = REQ` issues one `op = ANS`. The answer preserves the
request's optional `mode`: if absent in the request, it is absent in the
answer. Neither party shall answer an `ANS`. A `REQ` may originate from
SI-01 or from the backend.

Heartbeat request (`REQ`):

```json
{
  "v": 1,
  "type": "PING",
  "data": {
    "op": "REQ",
    "mode": "HB"
  }
}
```

Heartbeat answer (`ANS`):

```json
{
  "v": 1,
  "type": "PING",
  "data": {
    "op": "ANS",
    "mode": "HB"
  }
}
```

Manual request (`REQ`, no `mode`):

```json
{
  "v": 1,
  "type": "PING",
  "data": {
    "op": "REQ"
  }
}
```

Manual answer (`ANS`):

```json
{
  "v": 1,
  "type": "PING",
  "data": {
    "op": "ANS"
  }
}
```

The default v1 reader accepts missing `mode` as manual/explicit. It rejects an
unsupported `mode` value rather than guessing it means manual. A manual request
does not reset the periodic heartbeat cycle. There is **no separate PONG
message family** in the default representation.

A reference implementation may include optional `pingId` on a `REQ` and
echo it on the corresponding `ANS`, for example `"pingId": "p-0001"`.
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
- emits top-level `locationId` only for RACE_DATA in public v1;
- emits no more than 16 TimingData records or 16 combined RaceData changes in one data message;
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
| IF06-REQ-004/005 | RACE_DATA carries NodeId + message-level LocationId + ordered incremental changes and explicit application outcome |
| IF06-REQ-014 | top-level RACE_DATA `seq` + cumulative ACK realize ordered application |
| IF06-REQ-015 | `teamAssignments` carries live `regId` -> `teamId` SET/DEL changes |
| IF06-REQ-016 | `stageStartTimes` carries RegistrationId-scoped SET/DEL changes |
| IF06-REQ-006 | SYNC/REQ preserve the authoritative source identity/order of each stream |
| IF06-REQ-017 | SYNC uses `stream` + current source-head `seq` |
| IF06-REQ-018 | transport acknowledgement does not replace RACE_DATA semantic ACK/source sync |
| IF06-REQ-019 | TIMING_DATA replay reuses original TimingData identity/content |
| IF06-REQ-020 | REQ uses `stream` + inclusive `fromSeq` in either direction |
| IF06-REQ-021 | every fresh TIMING_DATA SYNC receives a next-expected REQ handoff before live forwarding resumes |
| IF06-REQ-022 | TIMING_DATA is limited to 16 records/message and RACE_DATA to 16 combined changes/message |
| IF06-REQ-007 | representation does not couple local commit to transport delivery |
| IF06-REQ-008 | v1 JSON is the public/default representation |
| IF06-REQ-009 | provider/codec boundary permits alternative representations |
| IF06-REQ-010 | same JSON semantics can be mapped to IF-03 or RabbitMQ |
| IF06-REQ-011/012/013 | PING carries required op REQ/ANS and optional mode HB (omission means manual); optional `pingId` supports reference correlation without consuming TimingData identity |

## Open design points

- Final common STATUS JSON members.
- Whether TIMING_DATA remains single-source per message or permits an explicit
  multi-source batch envelope in a later version.

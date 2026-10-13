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

The default/reference representation uses one UTF-8 JSON object per UpstreamData
message.

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
- `PING`;
- `PONG`;
- `STATUS`.

Only fields whose semantics are promoted by the IF-06 ISD and its Step-7 refinements
become normative public members.

### TIMING_DATA

A TIMING_DATA message carries one or more committed TimingData values.

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

A batch may contain multiple records only from a semantically compatible source scope.
Batching is delivery convenience and never creates another TimingData sequence.

### REFERENCE_DATA

The envelope and type are reserved in v1. Exact RaceData/StageStartTimes members are
defined only after Step-7 D02 promotes their semantic contract.

### SYNC

The envelope and type are reserved in v1. Exact progress/acknowledgement members are
defined only after Step-7 D03 promotes synchronization semantics.

### PING / PONG

PING and PONG are system/upstream-scoped messages and therefore do not require `nodeId`.
The public/default v1 representation identifies the PING purpose with `purpose`
(`HEARTBEAT` or `MANUAL`). The optional `pingId` is a reference-implementation
extension for correlating individual exchanges; it is not an IF-06 semantic
requirement. When present, the PONG echoes it unchanged.

PING:

```json
{
  "v": 1,
  "type": "PING",
  "data": {
    "purpose": "HEARTBEAT",
    "pingId": "p-0001"
  }
}
```

Matching PONG:

```json
{
  "v": 1,
  "type": "PONG",
  "data": {
    "purpose": "HEARTBEAT",
    "pingId": "p-0001"
  }
}
```

The message `type` distinguishes request (`PING`) from answer (`PONG`), while
`purpose` independently distinguishes scheduled heartbeat from explicit manual check.
These are separate concerns; the legacy answer marker and heartbeat marker are not
copied into the public JSON representation.

`purpose` is mandatory in the default JSON mapping, and PONG preserves the PING
purpose. `HEARTBEAT` denotes an automatically scheduled check; `MANUAL` denotes
an explicitly initiated one. A manual exchange does not reset the periodic heartbeat.

The optional `pingId` illustrates reference-implementation correlation. When
supplied, the PONG echoes it; when omitted, purpose-preserving PING/PONG remains valid.
It is not a TimingData or transport sequence. No legacy wire-field positions are
standardized here.

PING/PONG carries no TimingData record and consumes no TimingData sequence identity. Its
lifecycle/timing semantics are defined by IF06-REQ-011/012/013.

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

The same encoded semantic object can be carried by different connector transports.

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
| IF06-REQ-011/012/013 | PING/PONG carry heartbeat/manual purpose; optional `pingId` supports reference correlation; neither consumes TimingData identity |

## Open design points

- Final REFERENCE_DATA JSON members after D02.
- Final SYNC JSON members after D03.
- Final common STATUS JSON members.
- Whether TIMING_DATA remains single-source per message or permits an explicit
  multi-source batch envelope in a later version.

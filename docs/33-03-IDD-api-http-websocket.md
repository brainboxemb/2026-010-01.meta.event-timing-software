# API HTTP/WebSocket Interface Design Description (IDD)

Status: draft / development-v1 realization

System interface: **IF-03 — API**



## Purpose

This Interface Design Description maps the semantic IF-03 operations to the current
HTTP/JSON + WebSocket development-v1 realization.

The ISD owns operation and state semantics. This document owns concrete wire design:
resource paths, HTTP methods, JSON member names, event envelopes, concrete result/error
strings and status-code mapping.

## Terms and abbreviations

- **IDD** — Interface Design Description
- **ISD** — Interface Specification Document
- **IF** — system interface
- **OP** — Operation defined by the ISD
- **HTTP** — Hypertext Transfer Protocol


## Relationship to other documents

This IDD implements the concrete development-v1 realization of
`32-03-ISD-application-control-status.md`. The ISD remains the semantic IF-03 contract;
this document defines how that contract is represented over HTTP/JSON and WebSocket.
Software-item design, implementation, clients and interface tests consume this design
where the concrete v1 representation matters.

## Transport baseline

The development-v1 realization uses:

- HTTP with UTF-8 JSON for request/response operations;
- WebSocket for live event delivery;
- API major version in the resource namespace `/api/v1`;
- separately configurable HTTP and WebSocket listeners/ports;
- normal IP networking, including loopback/same-host use during development.

The default development configuration binds locally/loopback unless remote access is
explicitly configured.

## Common JSON and compatibility rules

- JSON text is UTF-8.
- Clients tolerate additional unknown response members within compatible v1 extensions.
- Unknown live event types may be ignored/logged; clients can re-query current state.
- Existing member/result meaning is not silently changed within v1.
- Breaking changes require another major API namespace or an explicitly documented
  compatible migration.

## Resource summary

```text
GET  /api/v1/version
GET  /api/v1/status
GET  /api/v1/capabilities
GET  /api/v1/configuration

POST /api/v1/node/{id}/open
POST /api/v1/node/{id}/close

GET  /api/v1/node/{id}/logbook
GET  /api/v1/node/{id}/logbook?from=...&limit=...
GET  /api/v1/node/{id}/logbook?last=...

POST /api/v1/dev/node/{id}/auto-reg
POST /api/v1/node/{id}/configuration/tag-processing

WS   /api/v1/events
```

The path `{id}` is the public TimingNodeId.

## IF03-OP-001 — Build/version identity

HTTP mapping:

```text
GET /api/v1/version
```

Successful response:

```json
{
  "application": "timing-application",
  "version": "<project-version>",
  "revision": "<source-revision>",
  "sourceRef": "<branch-tag-or-ref>",
  "buildOrigin": "local|github-actions",
  "dirty": false,
  "apiVersion": "1"
}
```

The response is HTTP `200` with `application/json; charset=utf-8`.

## IF03-OP-002 — Current status

HTTP mapping:

```text
GET /api/v1/status
```

Response shape:

```json
{
  "nodes": [
    {
      "id": "TN-01",
      "locationId": null,
      "state": "CLOSED"
    }
  ],
  "problems": []
}
```

`locationId` is `null` when no operational location is assigned. `state` is
`CLOSED`, `OPEN` or `ERROR`.

Problem entries use:

```json
{
  "code": "<stable-machine-code>",
  "severity": "WARNING|ERROR",
  "nodeId": "TN-01",
  "message": "<human-readable-summary>"
}
```

`nodeId` is present for a TimingNode-scoped problem and omitted for an
application-wide problem.

A contained TimingData recovery failure is represented for example as:

```json
{
  "nodes": [
    {
      "id": "TN-01",
      "locationId": null,
      "state": "ERROR"
    }
  ],
  "problems": [
    {
      "code": "TIMING_DATA_RECOVERY_FAILED",
      "severity": "ERROR",
      "nodeId": "TN-01",
      "message": "TimingData recovery failed for TN-01"
    }
  ]
}
```

The message is diagnostic text; clients use `state`, `code` and `nodeId` for
machine behaviour.

## IF03-OP-004 — Capabilities

HTTP mapping:

```text
GET /api/v1/capabilities
```

Current response shape:

```json
{
  "capabilities": [
    {
      "id": "DIRECT_REGISTRATION_SIMULATION",
      "supported": true,
      "enabled": true
    }
  ]
}
```

Unknown capability IDs are compatible additions.

## IF03-OP-005 — Open at a location

HTTP mapping:

```text
POST /api/v1/node/{id}/open
```

Request:

```json
{
  "locationId": 24
}
```

The request body is required. The server decodes `locationId` as the shared positive
LocationId value and invokes one application-level OPEN operation carrying that value.

Successful response:

```json
{
  "result": "OPENED"
}
```

An idempotent request may return:

```json
{
  "result": "ALREADY_OPEN"
}
```

The ISD intentionally leaves the exact result rule for `ALREADY_OPEN` with a different
requested LocationId open for review. This IDD shall not invent a second rule.

There is no separate v1 Set Location resource. The location body of the OPEN
request is the concrete mapping of the single `open(LocationId)` semantic operation;
assigning the requested LocationId and changing CLOSED to OPEN are processed as one
ordered node operation.

## IF03-OP-006 — Close

HTTP mapping:

```text
POST /api/v1/node/{id}/close
```

The request has no semantic body.

Successful result strings are:

- `CLOSED`;
- `ALREADY_CLOSED`.

## IF03-OP-007 — Direct accepted-registration simulation

HTTP mapping:

```text
POST /api/v1/dev/node/{id}/auto-reg
```

Request:

```json
{
  "id": "N0001",
  "time": "2026-10-01T12:00:00.000000000Z"
}
```

The body `id` is the resolved public RegistrationId. It is not a tag value.

Successful response:

```json
{
  "seq": 1
}
```

The operation is available only when
`DIRECT_REGISTRATION_SIMULATION` is supported and enabled.

This development operation represents the automatic-registration `ADD` action.
The presentation-facing application boundary receives that action together with
`registrationId` and `time`. Additional actions such as REV require an explicit
IF-03/IF-05 contract extension; they are not inferred from this ADD-only request.

## IF03-OP-008 — LogBook query

Metadata:

```text
GET /api/v1/node/{id}/logbook
```

Response:

```json
{
  "count": 12457,
  "first": 1,
  "last": 12457
}
```

For an empty LogBook, `count` is `0` and `first`/`last` are `null`.

Bounded source range:

```text
GET /api/v1/node/{id}/logbook?from=101&limit=100
```

Newest bounded range:

```text
GET /api/v1/node/{id}/logbook?last=100
```

Record-bearing response:

```json
{
  "count": 12457,
  "next": 201,
  "records": []
}
```

`from` is inclusive. The development-v1 bound for `limit` and `last` is 1..1000.
`last` cannot be combined with `from` or `limit`.

Each record in `records` uses the public IF-05 reference representation defined by
`33-05-IDD-timingdata-interchange.md`.

## IF03-OP-009 — Current application configuration

HTTP mapping:

```text
GET /api/v1/configuration
```

The response is a non-secret view produced through the Application-layer
`ConfigurationControl` boundary. Presentation does not receive or mutate the
Runtime `ApplicationConfiguration` tree directly.

Development-v1 response shape:

```json
{
  "timingNodes": [
    {
      "id": "TN-01",
      "tagProcessing": {
        "startup": {
          "quietTimeoutMillis": 250,
          "maxBurstDurationMillis": 1000,
          "duplicateWindowMillis": 15000,
          "sweepCadenceMillis": 50,
          "observationQueueCapacity": 256
        },
        "current": {
          "quietTimeoutMillis": 250,
          "maxBurstDurationMillis": 1000,
          "duplicateWindowMillis": 15000,
          "sweepCadenceMillis": 50,
          "observationQueueCapacity": 256
        },
        "overridden": false,
        "runtimeMutable": {
          "quietTimeoutMillis": true,
          "maxBurstDurationMillis": true,
          "duplicateWindowMillis": true,
          "sweepCadenceMillis": true,
          "observationQueueCapacity": false
        }
      }
    }
  ]
}
```

`startup` is the effective startup value after compiled defaults and IF-11
startup overrides have been resolved. `current` is the value currently used by
the running process. When no runtime override is active the two values are equal.

The field-level `runtimeMutable` map is descriptive API metadata. It does not
grant mutation permission by itself; normal IF-03 listener/security rules still
apply.

## IF03-OP-010 — Runtime TagProcessor configuration override

HTTP mapping:

```text
POST /api/v1/node/{id}/configuration/tag-processing
```

The path `{id}` identifies the TimingNode whose Runtime configuration branch is
targeted. The HTTP adapter maps the request to Application
`ConfigurationControl`; it does not call TagProcessor or the Runtime tree
directly.

Set/replace request:

```json
{
  "action": "SET",
  "value": {
    "quietTimeoutMillis": 300,
    "sweepCadenceMillis": 75
  }
}
```

The `value` object is a **partial** TagProcessingPolicy representation. Omitted
members retain their current value when the server constructs one complete typed
candidate policy. The candidate is then validated/applied atomically. There is no
partial success: if one supplied value makes the complete candidate invalid or
restart-only, none of the supplied changes become active.

Clear request:

```json
{
  "action": "CLEAR"
}
```

`CLEAR` removes the complete runtime override for this TagProcessing policy and
restores its effective startup value. It does not rewrite IF-11 deployment
configuration.

The semantic response envelope is:

```json
{
  "result": "APPLIED",
  "tagProcessing": {
    "startup": {},
    "current": {},
    "overridden": true,
    "runtimeMutable": {}
  }
}
```

Stable result strings and HTTP mapping are:

| Result | HTTP | Meaning |
| --- | ---: | --- |
| `APPLIED` | `200` | authoritative current value changed |
| `NO_CHANGE` | `200` | request is valid but current value is unchanged |
| `INVALID` | `400` | candidate TagProcessingPolicy is invalid |
| `RESTART_REQUIRED` | `409` | candidate changes a startup-only field |

For `INVALID` and `RESTART_REQUIRED`, the returned `tagProcessing.current`
remains the authoritative pre-request value. This semantic result envelope is used
for a syntactically valid configuration-update request. Malformed JSON, unknown
members, unknown nodes and unsupported actions continue to use the common error
envelope.

Development-v1 live mutation supports the four timing/cadence fields. A changed
`observationQueueCapacity` yields `RESTART_REQUIRED` because it sizes the
already-composed bounded observation queue.

## IF03-OP-003 — Live events

WebSocket path:

```text
/api/v1/events
```

The current realization may use a dedicated configured WebSocket listener/port.

Event envelope:

```json
{
  "eventType": "STATUS_SNAPSHOT",
  "occurredAt": "2026-10-03T12:00:00Z",
  "payload": {}
}
```

Current event type strings:

```text
STATUS_SNAPSHOT
STATUS_CHANGED
TIMING_DATA_COMMITTED
CONFIGURATION_CHANGED
```

For `STATUS_SNAPSHOT` and `STATUS_CHANGED`, `payload` is the complete current status
shape from `GET /api/v1/status`.

For `TIMING_DATA_COMMITTED`, `payload` is one committed public IF-05 TimingData record.

For `CONFIGURATION_CHANGED`, `payload` identifies the changed runtime
configuration branch and contains its resulting current view:

```json
{
  "nodeId": "TN-01",
  "section": "tagProcessing",
  "configuration": {
    "startup": {},
    "current": {},
    "overridden": true,
    "runtimeMutable": {}
  }
}
```

The event is post-fact and is emitted only for an `APPLIED` configuration
change. `NO_CHANGE`, `INVALID` and `RESTART_REQUIRED` do not emit it.

After connection SI-01 sends `STATUS_SNAPSHOT` before the client relies on subsequent
change events.

## Reconnect realization

The current client-side sequence is:

1. connect/reconnect to `/api/v1/events`;
2. receive `STATUS_SNAPSHOT`;
3. start buffering later live events during baseline recovery;
4. replace cached status from the snapshot;
5. query `GET /api/v1/configuration` for the current configuration baseline;
6. query `GET /api/v1/node/{id}/logbook` for metadata;
7. fetch required bounded LogBook ranges;
8. merge buffered `STATUS_CHANGED` and `CONFIGURATION_CHANGED` events in delivery order;
9. deduplicate buffered `TIMING_DATA_COMMITTED` records by stable TimingData record key;
10. mark the presentation view live.

No durable WebSocket replay is required across disconnected sessions.

## Error envelope

HTTP failures use:

```json
{
  "error": {
    "code": "<stable-machine-code>",
    "message": "<human-readable-summary>"
  }
}
```

Current status mapping:

| HTTP status | Stable code examples / meaning |
| --- | --- |
| `400` | `MALFORMED_REQUEST`, `INVALID_VALUE` |
| `403` | `CAPABILITY_NOT_ENABLED` |
| `404` | `NOT_FOUND`, `NODE_NOT_FOUND` |
| `405` | `METHOD_NOT_ALLOWED` |
| `409` | domain conflict such as `NODE_NOT_OPEN`, or semantic `RESTART_REQUIRED` for a valid configuration update |
| `503` | `BUSY`, `UNAVAILABLE`, `INTERRUPTED`, expected operation failure |
| `504` | `OUTCOME_UNKNOWN` |
| `500` | unexpected internal interface failure |

`OUTCOME_UNKNOWN` explicitly means that already accepted work may still complete.

## Request validation

Current v1 request parsing rules include:

- one JSON object where a JSON body is required;
- required members occur exactly once;
- unsupported request members are rejected rather than silently interpreted;
- node IDs are path-addressed;
- LocationId is a positive integer according to the shared LocationId contract;
- request bodies are bounded by the implementation;
- configuration SET bodies accept only the documented TagProcessingPolicy members;
- configuration CLEAR bodies do not accept a `value` object;
- durations are represented as integral milliseconds and queue capacity as a positive integer;
- methods other than the mapping defined above return an explicit failure.

## Listener and exposure design

Development configuration may assign HTTP and WebSocket different ports. This does not
create separate semantic interfaces.

The default listener scope is loopback/local. A non-loopback bind is an explicit
deployment choice.

Authentication, role authorization and browser CORS/origin policy are not part of this
development-v1 design yet.

## ISD mapping

| ISD operation/requirement | Development-v1 design |
| --- | --- |
| IF03-OP-001 / IF03-REQ-003 | `GET /api/v1/version` |
| IF03-OP-002 / IF03-REQ-004 | `GET /api/v1/status` |
| IF03-OP-003 / IF03-REQ-005/006/015/016 | WebSocket `/api/v1/events` + LogBook recovery |
| IF03-OP-004 / IF03-REQ-012 | `GET /api/v1/capabilities` |
| IF03-OP-005 / IF03-REQ-011 | `POST /api/v1/node/{id}/open` with `locationId` |
| IF03-OP-006 | `POST /api/v1/node/{id}/close` |
| IF03-OP-007 / IF03-REQ-013 | `POST /api/v1/dev/node/{id}/auto-reg` |
| IF03-OP-008 / IF03-REQ-014 | bounded `/api/v1/node/{id}/logbook` resources |
| IF03-OP-009 / IF03-REQ-018 | `GET /api/v1/configuration` |
| IF03-OP-010 / IF03-REQ-019 | `POST /api/v1/node/{id}/configuration/tag-processing` |
| IF03-OP-003 / IF03-REQ-020 | `CONFIGURATION_CHANGED` on WebSocket `/api/v1/events` |

## Open design points

- exact `ALREADY_OPEN` behavior when the request carries a different LocationId;
- production authentication/authorization;
- browser-origin/CORS policy if browser software later consumes IF-03 directly;
- whether high-volume diagnostics belong on the normal event stream or a separate
  diagnostics subscription.

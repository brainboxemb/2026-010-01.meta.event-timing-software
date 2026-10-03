# API HTTP/WebSocket Interface Design Description (IDD)

Status: draft / development-v1 realization

System interface: **IF-03 — API**

Specification: `32-03-ISD-application-control-status.md`


## Document guide

- **Role:** define the concrete HTTP/JSON + WebSocket realization of **IF-03 — API**.
- **Inputs:** `32-03-ISD-application-control-status.md`.
- **Owns:** HTTP methods/paths, JSON shapes, WebSocket envelopes, concrete result/error encoding and transport-level compatibility details.
- **Downstream:** SI-01 implementation/design, API clients and interface-level tests.
- **Key terms:** `IDD` — Interface Design Description; `ISD` — Interface Specification Document; `IF` — system interface; `OP` — semantic Operation defined by the ISD; `HTTP` — Hypertext Transfer Protocol.

## Purpose

This Interface Design Description maps the semantic IF-03 operations to the current
HTTP/JSON + WebSocket development-v1 realization.

The ISD owns operation and state semantics. This document owns concrete wire design:
resource paths, HTTP methods, JSON member names, event envelopes, concrete result/error
strings and status-code mapping.

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

PUT  /api/v1/node/{id}/location
POST /api/v1/node/{id}/open
POST /api/v1/node/{id}/close

GET  /api/v1/node/{id}/logbook
GET  /api/v1/node/{id}/logbook?from=...&limit=...
GET  /api/v1/node/{id}/logbook?last=...

POST /api/v1/dev/node/{id}/auto-reg

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
`CLOSED` or `OPEN`.

Problem entries use:

```json
{
  "code": "<stable-machine-code>",
  "severity": "WARNING|ERROR",
  "message": "<human-readable-summary>"
}
```

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

## IF03-OP-005 — Set operational location

HTTP mapping:

```text
PUT /api/v1/node/{id}/location
```

Request:

```json
{
  "locationId": 24
}
```

Successful response:

```json
{
  "result": "UPDATED"
}
```

A request for an unknown TimingNode returns `NODE_NOT_FOUND`. A location change while
the node is OPEN is a domain conflict.

## IF03-OP-006 — Open at a location

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

A client shall not implement normal OPEN as:

```text
PUT  .../location
POST .../open
```

The location body of the OPEN request is the concrete v1 mapping of the single
`open(LocationId)` semantic operation.

## IF03-OP-007 — Close

HTTP mapping:

```text
POST /api/v1/node/{id}/close
```

The request has no semantic body.

Successful result strings are:

- `CLOSED`;
- `ALREADY_CLOSED`.

## IF03-OP-008 — Direct accepted-registration simulation

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

## IF03-OP-009 — LogBook query

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
```

For `STATUS_SNAPSHOT` and `STATUS_CHANGED`, `payload` is the complete current status
shape from `GET /api/v1/status`.

For `TIMING_DATA_COMMITTED`, `payload` is one committed public IF-05 TimingData record.

After connection SI-01 sends `STATUS_SNAPSHOT` before the client relies on subsequent
change events.

## Reconnect realization

The current client-side sequence is:

1. connect/reconnect to `/api/v1/events`;
2. receive `STATUS_SNAPSHOT`;
3. start buffering later live events during baseline recovery;
4. replace cached status from the snapshot;
5. query `GET /api/v1/node/{id}/logbook` for metadata;
6. fetch required bounded LogBook ranges;
7. merge buffered `STATUS_CHANGED` events in delivery order;
8. deduplicate buffered `TIMING_DATA_COMMITTED` records by stable TimingData record key;
9. mark the presentation view live.

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
| `409` | domain conflict such as `NODE_NOT_CLOSED` or `NODE_NOT_OPEN` |
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
| IF03-OP-005 | `PUT /api/v1/node/{id}/location` |
| IF03-OP-006 / IF03-REQ-011 | `POST /api/v1/node/{id}/open` with `locationId` |
| IF03-OP-007 | `POST /api/v1/node/{id}/close` |
| IF03-OP-008 / IF03-REQ-013 | `POST /api/v1/dev/node/{id}/auto-reg` |
| IF03-OP-009 / IF03-REQ-014 | bounded `/api/v1/node/{id}/logbook` resources |

## Open design points

- exact `ALREADY_OPEN` behavior when the request carries a different LocationId;
- production authentication/authorization;
- browser-origin/CORS policy if browser software later consumes IF-03 directly;
- whether future high-volume diagnostics use the normal event stream or a separate
  diagnostics subscription.

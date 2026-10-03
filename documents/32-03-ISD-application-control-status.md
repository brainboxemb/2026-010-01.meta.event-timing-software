<!-- Generated review/output copy. Edit the source document, not this copy. -->

# API Interface Specification (ISD)

Status: review candidate / AP-1 first-executable slice

System interface: **IF-03 — API**

## Purpose

This Interface Specification Document owns the general programmable remote contract between SI-01 and the planned SI-02 GUI, engineering/service tools and automated ST-1 black-box/integration tooling.

For AP-1 it defines only the first-executable subset needed to expose build/version identity, current status and status-change events. The interface is intentionally broader than "status": later supported remote control, test and diagnostic operations may extend IF-03 when their SIP increments require them.

A simple browser-based test client may consume IF-03 later, just like the current JavaFX engineering client. It is not currently a separate product interface.

## Inputs

IF-03 is a system-owned interface allocated by
`31-SSSD-software-system-specification-document.md`. Its detailed contract is
therefore downstream of that allocation and upstream of both participating software-item
specifications. Applicable system use cases supply operational intent.

The SI-01/GUI SSDs and the SVP may trace to this ISD; they are not inputs to it.

## Parties

```text
client side
  planned SI-02 GUI / engineering client
  headless ST-1 / integration test driver
  other supported remote tooling
        |
        | IF-03 API
        v
SI-01 Timing Point Application
```

SI-01 keeps the TimingNode/status state. Clients observe/query it and later submit permitted commands; cached responses do not move that state into the client.

## Transport baseline

The first-executable transport contract is:

- HTTP with JSON for request/response queries;
- WebSocket for live status/event delivery;
- API major version represented in the resource path as `/api/v1`;
- network boundary usable when SI-01 and the client run on different hosts;
- the same semantic application model may also be represented through local console/remote-shell adapters, but those transports are not owned by this ISD.

The contract must remain compatible with the current Java 8 SI-01 baseline and the selected runtime on the Raspberry Pi target. HTTP and WebSocket may use separate configured listeners/ports in the first executable; the resource paths and semantics remain one IF-03 contract.

## First-executable resources

```text
GET /api/v1/version
GET /api/v1/status
WS  /api/v1/events
```

Only `GET` is required for the two HTTP resources in this slice. Later application commands may add other methods/resources without changing the ownership principle.

## Common compatibility rules

- JSON member names defined by this first slice are stable within API major version `v1`.
- Clients shall tolerate additional/unknown JSON members so the status model can grow compatibly.
- A breaking representation/semantic change requires a new API major path such as `/api/v2` or an explicitly documented compatible migration mechanism.
- Unknown event types shall not corrupt client state; a client may ignore/log an event type it does not understand and can always re-query `/status`.
- UTF-8 is used for JSON text.
- timestamps in the public contract use ISO-8601 UTC text form;
- the API major version is carried by the `/api/v1` resource namespace and is not repeated in every JSON object; `/version` still reports `apiVersion` as build/interface identity.

## Build/version identity

The stable first-executable build identity is:

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

Field semantics:

- `application` — stable application identity for SI-01;
- `version` — project/application version from the produced build;
- `revision` — exact source revision used to produce the running artifact, normally the Git commit SHA;
- `sourceRef` — source branch, tag or CI ref associated with the build;
- `buildOrigin` — stable build-environment class such as `local` or `github-actions`;
- `dirty` — whether uncommitted source changes were present when the artifact was built;
- `apiVersion` — IF-03 major API version represented by this contract.

The embedded identity deliberately excludes wall-clock build time, CI run/build number,
actor/user and other per-run metadata. Those values would make otherwise identical build
inputs produce different artifacts merely because a build was repeated. `revision` remains the
exact source authority; `sourceRef` and `buildOrigin` provide the human diagnostic context
needed when testing an artifact. A `dirty=true` local build is explicitly not fully described
by its commit SHA alone.

## Current status response

The status resource is intentionally compact. Build identity is queried through
`/version`; status carries only current operational state.

> This is an external interface shape. It does not prescribe a Java class with
> the same structure or a class named `ApplicationStatusSnapshot`. The
> implementation may assemble this response from the application objects that
> exist when the HTTP/status adapter is implemented.

```json
{
  "nodes": [
    {
      "id": "<configured-timing-node-id>",
      "locationId": null,
      "state": "CLOSED"
    }
  ],
  "problems": []
}
```

The first executable does not expose a separate application lifecycle state in
`/status`. A successful query already establishes that the IF-03 service is
running; startup/shutdown process lifecycle remains an internal/runtime concern
for this slice.

Internally SI-01 may host 1..N `TimingSystem` aggregates, each with its own
`SystemStatus`, but `TimingSystemId` is deliberately not part of this external
IF-03 shape. The `nodes` array aggregates the configured TimingNodes.
`TimingNodeId` is application-wide unique and is represented as `id` in the
compact IF-03 node object, so node-specific resources can use
`/api/v1/node/{id}/...` without exposing an internal TimingSystem identifier.

In the Step-4 first-registration slice, `locationId` is either `null` while
no operational location is assigned or the positive current IF-05 `LocationId`
value. `state` is `CLOSED` or `OPEN`. A closed node may retain its last
selected location during the same runtime session; startup/recovery does not
invent a current operational location from historical TimingData.

Problem entries use:

```json
{
  "code": "<stable-machine-code>",
  "severity": "WARNING|ERROR",
  "message": "<human-readable-summary>"
}
```

Clients must not make business decisions by parsing the human-readable `message`; `code` and structured status fields are the machine-readable contract.

## First-executable semantic operations

### IF03-OP-001 — Get build/version identity

HTTP mapping:

```text
GET /api/v1/version
```

Successful response:

- HTTP `200`;
- `application/json`;
- body is the build/version identity defined above.

Semantics:

- returns the authoritative application build/version identity;
- does not derive a separate client-specific version value;
- remains stable for the lifetime of one running application build;
- is equivalent in meaning to version identity shown by first-executable console/remote-shell views.

### IF03-OP-002 — Get current status

HTTP mapping:

```text
GET /api/v1/status
```

Successful response:

- HTTP `200`;
- `application/json`;
- body contains the current TimingNode status using the schema above.

Later subsystem/device/backoffice fields may extend the model without changing the ownership principle.

### IF03-OP-004 — Get public/engineering capabilities

HTTP mapping:

```text
GET /api/v1/capabilities
```

Successful response:

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

Unknown capability IDs added within API v1 are ignored by clients that do not
understand them. The direct-registration engineering command below is available
only when `DIRECT_REGISTRATION_SIMULATION` is both supported and enabled.

### IF03-OP-005 — Set current operational location

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

The value uses the shared IF-05 `LocationId` representation. Concrete allowed
values remain event/profile/deployment policy outside IF-03.

Successful response is HTTP `200`:

```json
{
  "result": "UPDATED"
}
```

The operation is accepted only while the TimingNode is CLOSED. A successful
change is reflected by subsequent status queries and a `STATUS_CHANGED` event.

### IF03-OP-006 — Open registration

HTTP mapping:

```text
POST /api/v1/node/{id}/open
```

The request has no semantic body. Successful HTTP `200` results are
`OPENED` or `ALREADY_OPEN`. OPEN without a configured current LocationId is
a domain conflict and does not change state.

### IF03-OP-007 — Close registration

HTTP mapping:

```text
POST /api/v1/node/{id}/close
```

The request has no semantic body. Successful HTTP `200` results are
`CLOSED` or `ALREADY_CLOSED`. A successful state change is followed by a
`STATUS_CHANGED` event.

### IF03-OP-008 — Simulate an automatic registration

This is an engineering capability, not a replacement RFID or manual-entry
interface. The short `auto-reg` resource name is a Step-4 review label; the
semantic injection boundary is the important contract decision.

HTTP mapping:

```text
POST /api/v1/dev/node/{id}/auto-reg
```

Request:

```json
{
  "id": "N001",
  "time": "2026-10-01T12:00:00.000000000Z"
}
```

The path `{id}` addresses the TimingNode. The request-body `id` is the
already-resolved shared `RegistrationId`; `N001` is only a short deterministic
example and does not define a required prefix or format. `time` is the accepted observation
time. SI-01 supplies source identity, current LocationId, next committed sequence
and recordedAt and executes the same accepted-registration operation used after
normal RFID interpretation/filtering.

Successful HTTP `200` response:

```json
{
  "seq": 1
}
```

The returned sequence identifies the newly committed record within the addressed
TimingNode. The committed record becomes visible through IF03-OP-009 and a
`TIMING_DATA_COMMITTED` event.

### IF03-OP-009 — Query committed LogBook

The LogBook resource is node-addressed and bounded. A client does not need to
download the complete history merely to learn its size.

HTTP mappings:

```text
GET /api/v1/node/{id}/logbook
GET /api/v1/node/{id}/logbook?from=101&limit=100
GET /api/v1/node/{id}/logbook?last=100
```

Without query parameters the response is metadata only:

```json
{
  "count": 12457,
  "first": 1,
  "last": 12457
}
```

For an empty LogBook, `count` is `0` and `first`/`last` are `null`.

`from` is an inclusive committed source sequence. `limit` is the maximum
number of records returned. `last` requests the newest records while preserving
source-sequence order. `last` cannot be combined with `from` or `limit`.
The Step-4 v1 baseline limits `limit` and `last` to 1..1000.

A record-bearing response is:

```json
{
  "count": 12457,
  "next": 201,
  "records": []
}
```

`count` is the total committed record count at response time. `next` is the
next source sequence to request when more records are available, otherwise
`null`. Each `records` element uses the public IF-05 TimingData JSON field
semantics. Records are returned in committed source-sequence order; queued or
uncommitted work is never exposed as LogBook content.

### IF03-OP-003 — Subscribe to status/event updates

WebSocket mapping:

```text
/api/v1/events
```

The first executable may expose this path on a dedicated configured WebSocket listener rather than the A06 HTTP listener. Clients therefore configure the WebSocket endpoint independently while the path and payload semantics remain stable.

After the WebSocket connection is established SI-01 shall immediately send a complete `STATUS_SNAPSHOT` event before normal change events are relied upon.

Event envelope:

```json
{
  "eventType": "STATUS_SNAPSHOT",
  "occurredAt": "<ISO-8601 UTC>",
  "payload": {}
}
```

Step-4 event types:

```text
STATUS_SNAPSHOT
STATUS_CHANGED
TIMING_DATA_COMMITTED
```

For `STATUS_SNAPSHOT`, `payload` contains the complete current status representation.

For `STATUS_CHANGED`, `payload` also contains a complete current status
representation. SI-01 emits this event only after an actual authoritative
location/lifecycle/status change; it shall not manufacture periodic or duplicate
changes merely to exercise the transport.

For `TIMING_DATA_COMMITTED`, `payload` is the committed public IF-05 TimingData
record. It is emitted only after durable local append and LogBook visibility.
Recovery does not replay old records as new live events.

WebSocket delivery order is sufficient within one connected session. The stable
TimingData record key, rather than a separate transient WebSocket sequence,
provides deduplication when history and live delivery overlap.

## Reconnect and resynchronisation

Reconnect semantics rebuild authoritative current state/LogBook gaps before the
client declares its view live:

1. client reconnects to `/api/v1/events`;
2. SI-01 sends a complete `STATUS_SNAPSHOT`; the client begins buffering later
   WebSocket events;
3. the client replaces its cached status from the snapshot;
4. for each selected/cached node, the client queries
   `GET /api/v1/node/{id}/logbook` and fetches only required bounded ranges,
   normally continuing from the last cached sequence;
5. the client applies buffered `STATUS_CHANGED` events in WebSocket order;
6. buffered `TIMING_DATA_COMMITTED` records already present in the rebuilt
   LogBook view are discarded by stable TimingData record key; later records are
   appended in source-sequence order;
7. only after this merge is complete does the client mark the view live.

No durable WebSocket replay across disconnected sessions is required. The
authoritative LogBook is the recovery source for committed TimingData missed
while disconnected.

## Error responses

HTTP failures use a JSON envelope:

```json
{
  "error": {
    "code": "<stable-machine-code>",
    "message": "<human-readable-summary>"
  }
}
```

Step-4 mapping:

| HTTP status | Stable example codes / meaning |
| --- | --- |
| `400` | `MALFORMED_REQUEST`, `INVALID_VALUE` |
| `403` | `CAPABILITY_NOT_ENABLED` |
| `404` | `NOT_FOUND`, `NODE_NOT_FOUND` |
| `405` | `METHOD_NOT_ALLOWED` |
| `409` | domain-state conflict such as `NO_LOCATION`, `NODE_NOT_CLOSED`, `NODE_NOT_OPEN` |
| `503` | `BUSY`, `UNAVAILABLE`, or expected commit dependency failure |
| `504` | `OUTCOME_UNKNOWN` after the caller-side operation guard timeout |
| `500` | unexpected internal interface failure |

A timeout response explicitly means that the accepted operation may still execute;
the transport shall not cancel already accepted TimingNode work. Before retrying a
state-changing command whose outcome is unknown, the client resynchronises current
status/history.

A normal reported problem represented by `/status` is not converted into HTTP
`500` merely because a problem entry is present.

## Network access and first-executable security policy

Authentication/authorisation is explicitly **deferred** for the first executable development baseline. This is a deliberate scope decision, not an assumption that the final product is unauthenticated.

Until a later security/interface increment defines authentication:

- the default IF-03 listen address shall be loopback/local-only;
- non-loopback binding must require explicit configuration;
- remote first-executable demonstrations shall run only on a trusted development/test network;
- deployment/prod exposure outside that controlled environment is out of scope;
- CORS/browser-origin policy is deferred until a browser-based client is actually needed.

This allows ST-1, engineering-client and later SI-02 development without prematurely inventing production security while preventing accidental default exposure.

## First-executable contract rules

<a id="IF03-REQ-001"></a>

**IF03-REQ-001 — Shared semantics**

HTTP/JSON and WebSocket representations shall map to the
shared SI-01 application/status semantics rather than
implement independent business/status state in the transport
adapter.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-022`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-022), [`SI01-REQ-030`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-030)
- **Satisfied by:** [`Api`](41-01-SSD-timing-application-specification-document.md#Api), [`CommandHandler`](41-01-SSD-timing-application-specification-document.md#CommandHandler)

---


<a id="IF03-REQ-002"></a>

**IF03-REQ-002 — Remote-host operation**

The interface shall support operation across a normal IP
network boundary when non-loopback access is explicitly
configured, so a client can run on a workstation while SI-01
runs on another host such as a Raspberry Pi.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-031`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-031)
- **Satisfied by:** [`Api`](41-01-SSD-timing-application-specification-document.md#Api)

---


<a id="IF03-REQ-003"></a>

**IF03-REQ-003 — Version query**

The interface shall provide `GET /api/v1/version` representing `IF03-OP-001`.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-010`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-010), [`SI01-REQ-011`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-011)
- **Verified by:** [`VC-ST1-001`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-001)

---


<a id="IF03-REQ-004"></a>

**IF03-REQ-004 — Status query**

The interface shall provide `GET /api/v1/status`
representing `IF03-OP-002`.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-020`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-020), [`SI01-REQ-021`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-021), [`SI01-REQ-022`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-022)
- **Satisfied by:** [`Api`](41-01-SSD-timing-application-specification-document.md#Api), [`CommandHandler`](41-01-SSD-timing-application-specification-document.md#CommandHandler)
- **Verified by:** [`VC-ST1-001`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-001)

---


<a id="IF03-REQ-005"></a>

**IF03-REQ-005 — Live status/event delivery**

The interface shall provide WebSocket `/api/v1/events` representing `IF03-OP-003` for the first executable.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-023`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-023)
- **Verified by:** [`VC-ST1-001`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-001)

---


<a id="IF03-REQ-006"></a>

**IF03-REQ-006 — Reconnect to current state**

A client that connects/reconnects shall receive a complete current status snapshot before relying on subsequent live events.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-023`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-023)
- **Verified by:** [`VC-ST1-001`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-001)

---


<a id="IF03-REQ-007"></a>

**IF03-REQ-007 — Machine-readable representation**

The HTTP query representation shall be machine-readable JSON suitable for SI-02, engineering clients and automated ST-1 verification.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-031`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-031)

---


<a id="IF03-REQ-008"></a>

**IF03-REQ-008 — Explicit failure response**

Unsupported or invalid HTTP requests shall produce the explicit JSON failure outcome defined in this ISD rather than a successful response containing silently invalid data.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-031`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-031)

---


<a id="IF03-REQ-009"></a>

**IF03-REQ-009 — Safe default listen scope**

Without explicit configuration the first-executable IF-03 service shall bind only to a local/loopback interface.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-032`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-032)

---


<a id="IF03-REQ-010"></a>

**IF03-REQ-010 — Compatible extension**

Clients shall be able to ignore unknown response members/event types within API major version `v1`; breaking contract changes shall not silently redefine existing `v1` semantics.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-033`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-033)

---


<a id="IF03-REQ-011"></a>

**IF03-REQ-011 — Step-4 location and lifecycle control**

IF-03 shall expose 1..N application-wide-unique TimingNode identities with current
optional LocationId and OPEN/CLOSED state and shall provide node-addressed
IF03-OP-005/006/007 location/open/close control using the shared SI-01
application/domain semantics.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-040`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-040)
- **Verified by:** [`VC-ST1-002`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-002)

---


<a id="IF03-REQ-012"></a>

**IF03-REQ-012 — Engineering capability discovery**

IF-03 shall provide IF03-OP-004 so the Engineering Client can determine whether
direct registration simulation is supported and enabled before presenting or
using that control.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-043`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-043)
- **Verified by:** [`VC-ST1-002`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-002)

---


<a id="IF03-REQ-013"></a>

**IF03-REQ-013 — Dev auto-reg control**

When the advertised capability is supported and enabled, IF-03 shall provide
IF03-OP-008 and pass only `id` plus `time` to the normal SI-01
accepted-registration operation.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-041`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-041), [`SI01-REQ-043`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-043)
- **Verified by:** [`VC-ST1-002`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-002)

---


<a id="IF03-REQ-014"></a>

**IF03-REQ-014 — Committed LogBook query**

IF-03 shall provide IF03-OP-009 as a node-addressed LogBook metadata and bounded
range query in source-sequence order using public IF-05 field semantics.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-042`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-042)
- **Verified by:** [`VC-ST1-002`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-002)

---


<a id="IF03-REQ-015"></a>

**IF03-REQ-015 — Live committed TimingData delivery**

The IF-03 WebSocket event stream shall emit `TIMING_DATA_COMMITTED` only after
the corresponding TimingData record is committed and visible in the authoritative
LogBook.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-042`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-042)
- **Verified by:** [`VC-ST1-002`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-002)

---


<a id="IF03-REQ-016"></a>

**IF03-REQ-016 — Rebuild LogBook before live presentation**

A reconnecting client shall be able to combine the current status snapshot,
bounded authoritative LogBook ranges and buffered live events using stable
TimingData record keys before declaring its view live.

— — —

- **Type:** Interface Requirement
- **Status:** Review
- **Derived from:** [`SI01-REQ-044`](41-01-SSD-timing-application-specification-document.md#SI01-REQ-044)
- **Verified by:** [`VC-ST1-003`](61-01-VTS-timing-application-verification-test-specification.md#VC-ST1-003)

---


## Relationship to SI-01 SSD

Each IF-03 requirement owns its upstream SI-01 traceability through its
`derived_from` relation. That relation is authored once with the requirement and
the generated engineering reader/graph provides the inverse context back to IF-03.

The SI-01 SSD references this contract instead of duplicating transport-level
requirements.

## Verification references

IF-03 owns the transport contract and acceptance semantics above. Concrete
verification procedures are downstream and are specified in
`61-01-VTS-timing-application-verification-test-specification.md`.

Current ST-1 cases using IF-03 include:

- `VC-ST1-001` — query version/status, connect/reconnect the event stream and
  verify a complete current status snapshot through the running executable;
- `VC-ST1-002` — exercise the first-registration control/history/live flow
  through the running executable.

The VTS maps each case to the applicable SSD/ISD requirements. Execution status,
PASS/FAIL, logs and persisted test artifacts belong to generated verification
evidence rather than this ISD.

## Remote shell scope

The first executable may expose equivalent version/status semantics through a remote-shell adapter as required by the SIP, but AP-1 does **not** introduce a separate system ISD for that transport.

Reason:

- the public programmable contract needed by the planned SI-02 GUI, engineering tooling and ST-1 is IF-03;
- remote-shell technology is an implementation/support adapter concern at this stage;
- it must reuse the shared version/status application queries and must not own a separate status model.

If the remote shell later becomes a stable externally consumed system interface, it should receive an appropriate ISD then.

## Deferred interface scope

The following IF-03 capabilities are visible in later use cases/architecture but intentionally outside this AP-1 baseline:

- start procedure;
- RFID power/reinitialisation commands;
- ready-team add/remove;
- manual registration/penalty/revocation beyond the dev auto-reg path;
- reference-data administration;
- backoffice controls;
- detailed diagnostics/support export;
- production authentication/role-based authorisation;
- browser CORS/origin policy if a browser-based test/client tool is later added.

They should be added when their corresponding SIP capability approaches implementation.

## Remaining AP-1 implementation choices

The following are implementation/toolchain selections rather than unresolved interface semantics and may be chosen in the implementation repository/toolchain step:

- concrete Java HTTP/WebSocket library;
- concrete remote-shell library/technology;
- concrete JSON library;
- concrete configuration library;
- exact JDK/Maven/toolchain provisioning.

Changing one of these libraries must not silently change the contract defined above.

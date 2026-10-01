# API Interface (IDD)

Status: review candidate / AP-1 first-executable slice

System interface: **IF-03 — API**

## Purpose

This Interface Design/Description Document owns the general programmable remote contract between SI-01 and the planned SI-02 GUI, engineering/service tools and automated ST-1 black-box/integration tooling.

For AP-1 it defines only the first-executable subset needed to expose build/version identity, current status and status-change events. The interface is intentionally broader than "status": later supported remote control, test and diagnostic operations may extend IF-03 when their SIP increments require them.

A simple browser-based test client may consume IF-03 later, just like the current JavaFX engineering client. It is not currently a separate product interface.

## Inputs

IF-03 is a system-owned interface allocated by
`31-SSSD-software-system-specification-document.md`. Its detailed contract is
therefore downstream of that allocation and upstream of both participating software-item
specifications. Applicable system use cases supply operational intent.

The SI-01/GUI SSDs and the SVP may trace to this IDD; they are not inputs to it.

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
- the same semantic application model may also be represented through local console/remote-shell adapters, but those transports are not owned by this IDD.

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
- timestamps in the public contract use ISO-8601 UTC text form.

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

The first-executable status representation is:

> This is an external interface shape. It does not prescribe a Java class with
> the same structure or a class named `ApplicationStatusSnapshot`. The
> implementation may assemble this response from the application objects that
> exist when the HTTP/status adapter is implemented.

```json
{
  "apiVersion": "1",
  "build": {
    "application": "timing-application",
    "version": "<project-version>",
    "revision": "<source-revision>",
    "sourceRef": "<branch-tag-or-ref>",
    "buildOrigin": "local|github-actions",
    "dirty": false,
    "apiVersion": "1"
  },
  "timingNodes": [
    {
      "timingNodeId": "<configured-timing-node-id>",
      "locationId": null,
      "lifecycle": "CLOSED"
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
`SystemStatus`, but `TimingSystemId` is deliberately not part of this first
external IF-03 shape. The `timingNodes` array is an application-facing
aggregation of the configured TimingNodes; the current configuration baseline
keeps `TimingNodeId` application-wide unique so that this flattened view is
unambiguous. Structured problem entries carry additional observable operational
problems.

In the Step-4 first-registration slice, `locationId` is either `null` while
no operational location is assigned or the positive current IF-05 `LocationId`
value. `lifecycle` is `CLOSED` or `OPEN`. A closed node may retain its last
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
  "apiVersion": "1",
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
PUT /api/v1/timing-node/location
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
  "apiVersion": "1",
  "result": "UPDATED"
}
```

The operation is accepted only while the TimingNode is CLOSED. A successful
change is reflected by subsequent status queries and a `STATUS_CHANGED` event.

### IF03-OP-006 — Open registration

HTTP mapping:

```text
POST /api/v1/timing-node/open
```

The request has no semantic body. Successful HTTP `200` results are
`OPENED` or `ALREADY_OPEN`. OPEN without a configured current LocationId is
a domain conflict and does not change state.

### IF03-OP-007 — Close registration

HTTP mapping:

```text
POST /api/v1/timing-node/close
```

The request has no semantic body. Successful HTTP `200` results are
`CLOSED` or `ALREADY_CLOSED`. A successful state change is followed by a
`STATUS_CHANGED` event.

### IF03-OP-008 — Inject an already-accepted registration

This is an engineering capability, not a replacement RFID or manual-entry
interface.

HTTP mapping:

```text
POST /api/v1/engineering/accepted-registration
```

Request:

```json
{
  "registrationId": "<resolved-registration-id>",
  "observationTime": "2026-10-01T12:00:00.000000000Z"
}
```

The caller supplies only the already-resolved shared `RegistrationId` and the
accepted observation time. SI-01 supplies its configured source identity,
current LocationId, next committed sequence and recordedAt value and executes the
same accepted-registration operation used after normal RFID interpretation and
filtering.

Successful HTTP `200` response:

```json
{
  "apiVersion": "1",
  "result": "COMMITTED",
  "recordKey": {
    "timingNodeId": "<configured-timing-node-id>",
    "sequenceNumber": 1
  }
}
```

Command outcome is intentionally separate from the history/live TimingData
representation. The committed record becomes visible through IF03-OP-009 and a
`TIMING_DATA_COMMITTED` event.

### IF03-OP-009 — Get committed TimingData history

HTTP mapping:

```text
GET /api/v1/timing-data
```

Successful response:

```json
{
  "apiVersion": "1",
  "timingNodeId": "<configured-timing-node-id>",
  "records": []
}
```

Each `records` element uses the public IF-05 TimingData JSON field semantics.
Records are returned in committed source-sequence order. This resource exposes
committed history only; it does not expose queued/uncommitted operations.

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
  "apiVersion": "1",
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

Reconnect semantics rebuild authoritative current state/history before the client
declares its view live:

1. client reconnects to `/api/v1/events`;
2. SI-01 sends a complete `STATUS_SNAPSHOT`; the client begins buffering later
   WebSocket events;
3. the client replaces its cached status from the snapshot and calls
   `GET /api/v1/timing-data` to rebuild committed history;
4. the client applies buffered `STATUS_CHANGED` events in WebSocket order;
5. buffered `TIMING_DATA_COMMITTED` records already present in rebuilt history
   are discarded by stable TimingData record key; later records are appended in
   source-sequence order;
6. only after this merge is complete does the client mark the view live.

No durable WebSocket replay across disconnected sessions is required. Committed
history is the recovery source for TimingData missed while disconnected.

## Error responses

HTTP failures use a JSON envelope:

```json
{
  "apiVersion": "1",
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
| `404` | `NOT_FOUND` |
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

```{ifreq} Shared semantics
:id: IF03-REQ-001
:derived_from: SI01-REQ-022, SI01-REQ-030

HTTP/JSON and WebSocket representations shall map to the
shared SI-01 application/status semantics rather than
implement independent business/status state in the transport
adapter.
```

```{ifreq} Remote-host operation
:id: IF03-REQ-002
:derived_from: SI01-REQ-031

The interface shall support operation across a normal IP
network boundary when non-loopback access is explicitly
configured, so a client can run on a workstation while SI-01
runs on another host such as a Raspberry Pi.
```

```{ifreq} Version query
:id: IF03-REQ-003
:derived_from: SI01-REQ-010, SI01-REQ-011

The interface shall provide `GET /api/v1/version` representing `IF03-OP-001`.
```

```{ifreq} Status query
:id: IF03-REQ-004
:derived_from: SI01-REQ-020, SI01-REQ-021, SI01-REQ-022

The interface shall provide `GET /api/v1/status`
representing `IF03-OP-002`.
```

```{ifreq} Live status/event delivery
:id: IF03-REQ-005
:derived_from: SI01-REQ-023

The interface shall provide WebSocket `/api/v1/events` representing `IF03-OP-003` for the first executable.
```

```{ifreq} Reconnect to current state
:id: IF03-REQ-006
:derived_from: SI01-REQ-023

A client that connects/reconnects shall receive a complete current status snapshot before relying on subsequent live events.
```

```{ifreq} Machine-readable representation
:id: IF03-REQ-007
:derived_from: SI01-REQ-031

The HTTP query representation shall be machine-readable JSON suitable for SI-02, engineering clients and automated ST-1 verification.
```

```{ifreq} Explicit failure response
:id: IF03-REQ-008
:derived_from: SI01-REQ-031

Unsupported or invalid HTTP requests shall produce the explicit JSON failure outcome defined in this IDD rather than a successful response containing silently invalid data.
```

```{ifreq} Safe default listen scope
:id: IF03-REQ-009
:derived_from: SI01-REQ-032

Without explicit configuration the first-executable IF-03 service shall bind only to a local/loopback interface.
```

```{ifreq} Compatible extension
:id: IF03-REQ-010
:derived_from: SI01-REQ-033

Clients shall be able to ignore unknown response members/event types within API major version `v1`; breaking contract changes shall not silently redefine existing `v1` semantics.
```

```{ifreq} Step-4 location and lifecycle control
:id: IF03-REQ-011
:derived_from: SI01-REQ-040

IF-03 shall expose the current optional LocationId and OPEN/CLOSED state and shall
provide IF03-OP-005/006/007 for location, open and close control using the shared
SI-01 application/domain semantics.
```

```{ifreq} Engineering capability discovery
:id: IF03-REQ-012
:derived_from: SI01-REQ-043

IF-03 shall provide IF03-OP-004 so the Engineering Client can determine whether
direct registration simulation is supported and enabled before presenting or
using that control.
```

```{ifreq} Direct accepted-registration engineering control
:id: IF03-REQ-013
:derived_from: SI01-REQ-041, SI01-REQ-043

When the advertised capability is supported and enabled, IF-03 shall provide
IF03-OP-008 and pass only resolved RegistrationId plus accepted observation time
to the normal SI-01 accepted-registration operation.
```

```{ifreq} Committed TimingData history query
:id: IF03-REQ-014
:derived_from: SI01-REQ-042

IF-03 shall provide IF03-OP-009 for committed TimingData history in source-sequence
order using public IF-05 field semantics.
```

```{ifreq} Live committed TimingData delivery
:id: IF03-REQ-015
:derived_from: SI01-REQ-042

The IF-03 WebSocket event stream shall emit `TIMING_DATA_COMMITTED` only after
the corresponding TimingData record is committed and visible in authoritative
local history.
```

```{ifreq} Rebuild history before live presentation
:id: IF03-REQ-016
:derived_from: SI01-REQ-044

A reconnecting client shall be able to combine the current status snapshot,
committed TimingData history and buffered live events using stable TimingData
record keys before declaring its view live.
```

## Relationship to SI-01 SSD

Each IF-03 requirement owns its upstream SI-01 traceability through its
`derived_from` relation. That relation is authored once with the requirement and
the generated engineering reader/graph provides the inverse context back to IF-03.

The SI-01 SSD references this contract instead of duplicating transport-level
requirements.

## First AP-1 verification case

Verification-case identifiers use `VC-<profile>-<number>` for this baseline.

```{vc} Query and resynchronise first-executable status
---
id: VC-ST1-001
verifies: >-
  SI01-REQ-003, SI01-REQ-020, SI01-REQ-021, SI01-REQ-022,
  SI01-REQ-030, SI01-REQ-031, IF03-REQ-001, IF03-REQ-002,
  IF03-REQ-004
---

Trace target:

~~~text
UC-001 / UC-008
  -> SI01-REQ-010/011/020/021/022/023/031/032/033
  -> IF03-REQ-001..010 as applicable
  -> SI-01 status/application boundary from SSD/SDD
  -> VC-ST1-001
~~~
```

Procedure:

1. start SI-01 as a separate process with a synthetic configuration containing at least one configured `TimingNode`;
2. wait for the configured local IF-03 endpoint to become available;
3. call `GET /api/v1/version` and verify the required identity fields are present;
4. call `GET /api/v1/status` and verify the same build identity and configured TimingNode `TimingNodeId` is represented;
5. connect to `/api/v1/events` and verify the first application message is a complete `STATUS_SNAPSHOT`;
6. disconnect the WebSocket client;
7. reconnect and verify a new complete `STATUS_SNAPSHOT` is received before further change events are relied upon;
8. call `/status` once more and verify it is semantically consistent with the latest snapshot;
9. shut the SI-01 process down through the supported controlled shutdown path.

A07 separately verifies the `STATUS_CHANGED` broadcast path at adapter level. End-to-end black-box verification of a real `STATUS_CHANGED` event is added when a supported public capability can actually change the status. The test driver shall not fabricate or directly mutate status solely to satisfy that event case.

The test driver shall not mutate internal Java objects or inspect private implementation state to obtain the pass/fail result.

## Step-4 first-registration verification case

```{vc} Control and observe first committed registration
---
id: VC-ST1-002
verifies: >-
  SI01-REQ-040, SI01-REQ-041, SI01-REQ-042, SI01-REQ-043, SI01-REQ-044,
  IF03-REQ-011, IF03-REQ-012, IF03-REQ-013, IF03-REQ-014, IF03-REQ-015,
  IF03-REQ-016
---

Deterministic procedure:

1. start SI-01 with direct registration simulation supported and enabled;
2. query status and verify CLOSED with no current LocationId;
3. set a known synthetic LocationId and verify CLOSED status reflects it;
4. request OPEN and verify OPEN with the same LocationId;
5. attempt another location change and verify explicit NODE_NOT_CLOSED conflict;
6. submit one accepted registration with a deterministic RegistrationId and
   observation time;
7. verify the command result is COMMITTED and does not supply client-owned source
   sequence/location/recordedAt fields;
8. verify committed history contains exactly the resulting TimingData with source
   sequence 1, the active LocationId and the supplied observation time;
9. verify a TIMING_DATA_COMMITTED live event represents that same stable record key;
10. request CLOSE and verify CLOSED;
11. reconnect the event client, rebuild history, deduplicate any buffered overlap
    by record key and only then mark the view live.
```

## Remote shell scope

The first executable may expose equivalent version/status semantics through a remote-shell adapter as required by the SIP, but AP-1 does **not** introduce a separate system IDD for that transport.

Reason:

- the public programmable contract needed by the planned SI-02 GUI, engineering tooling and ST-1 is IF-03;
- remote-shell technology is an implementation/support adapter concern at this stage;
- it must reuse the shared version/status application queries and must not own a separate status model.

If the remote shell later becomes a stable externally consumed system interface, it should receive an appropriate IDD then.

## Deferred interface scope

The following IF-03 capabilities are visible in later use cases/architecture but intentionally outside this AP-1 baseline:

- start procedure;
- RFID power/reinitialisation commands;
- ready-team add/remove;
- manual registration/penalty/revocation beyond the direct accepted-registration engineering path;
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
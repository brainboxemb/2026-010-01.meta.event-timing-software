# Application Control and Status Interface (IDD)

Status: review candidate / AP-1 first-executable slice

System interface: **IF-03 — Application Control & Status**

## Purpose

This Interface Design/Description Document owns the system-level software-to-software contract between SI-01 and network clients such as SI-02, SI-03 and automated ST-1 test tooling.

For AP-1 it defines only the first-executable subset needed to expose build/version identity, current status and status-change events. Later operator commands and domain data are deliberately deferred until their SIP increments require them.

## Parties

```text
client side
  SI-02 Desktop GUI
  SI-03 Web Operator Application
  ST-1 / integration test driver
        |
        | IF-03
        v
SI-01 Headless Timing Application
```

SI-01 owns the authoritative TimingNode/status state. Clients observe/query that state and later submit permitted commands; they do not become authoritative merely by caching a response.

## Transport baseline

The first-executable transport contract is:

- HTTP with JSON for request/response queries;
- WebSocket for live status/event delivery;
- API major version represented in the resource path as `/api/v1`;
- network boundary usable when SI-01 and the client run on different hosts;
- the same semantic application model may also be represented through local console/remote-shell adapters, but those transports are not owned by this IDD.

The contract must remain compatible with Java 8 and the mandatory Raspberry Pi Zero target. HTTP and WebSocket may use separate configured listeners/ports in the first executable; the resource paths and semantics remain one IF-03 contract.

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
      "lifecycle": "CLOSED"
    }
  ],
  "problems": []
}
```

The first executable does not expose a separate application lifecycle state in
`/status`. A successful query already establishes that the IF-03 service is
running; startup/shutdown process lifecycle remains an internal/runtime concern
for this slice. Observable operational status is owned by the configured
`TimingNode` objects and by structured problem entries.

The first executable does not yet implement operational open/close commands. A
configured minimal `TimingNode` therefore reports `CLOSED`; later SIP
increments may add additional lifecycle values while preserving the
field/ownership model.

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

First-executable event types:

```text
STATUS_SNAPSHOT
STATUS_CHANGED
```

For `STATUS_SNAPSHOT`, `payload` contains the complete current status representation.

For `STATUS_CHANGED`, `payload` also contains a complete current status representation in the first executable. SI-01 emits this event only after an actual authoritative status change; it shall not manufacture periodic or duplicate changes merely to exercise the transport. This deliberately avoids introducing partial-patch/replay semantics before they are needed. Later compatible optimisation may add more event types while `/status` remains the authoritative resynchronisation operation.

WebSocket transport ordering is sufficient for first-executable events; no durable cross-connection event sequence is introduced in AP-1.

## Reconnect and resynchronisation

Reconnect semantics are intentionally simple:

1. client reconnects to `/api/v1/events`;
2. SI-01 sends a new complete `STATUS_SNAPSHOT` event;
3. the client replaces its cached status with that snapshot;
4. subsequent `STATUS_CHANGED` events are applied in WebSocket delivery order;
5. the client may call `GET /api/v1/status` at any time to explicitly recover current authoritative state.

No event replay across disconnected sessions is required by the first executable.

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

Initial status mapping:

| HTTP status | Meaning in first executable |
| --- | --- |
| `400` | malformed request where applicable |
| `404` | unknown resource |
| `405` | unsupported HTTP method on a known resource |
| `500` | unexpected internal interface failure |

A normal reported problem represented by `/status` is not converted into HTTP `500` merely because a problem entry is present.

## Network access and first-executable security policy

Authentication/authorisation is explicitly **deferred** for the first executable development baseline. This is a deliberate scope decision, not an assumption that the final product is unauthenticated.

Until a later security/interface increment defines authentication:

- the default IF-03 listen address shall be loopback/local-only;
- non-loopback binding must require explicit configuration;
- remote first-executable demonstrations shall run only on a trusted development/test network;
- deployment/prod exposure outside that controlled environment is out of scope;
- CORS/browser-origin policy is deferred until SI-03/browser work requires it.

This allows ST-1 and SI-02 development without prematurely inventing production security while preventing accidental default exposure.

## First-executable contract rules

**IF03-REQ-001 — Shared semantics**  
HTTP/JSON and WebSocket representations shall map to the shared SI-01 application/status semantics rather than implement independent business/status state in the transport adapter.

**IF03-REQ-002 — Remote-host operation**  
The interface shall support operation across a normal IP network boundary when non-loopback access is explicitly configured, so a client can run on a workstation while SI-01 runs on another host such as a Raspberry Pi.

**IF03-REQ-003 — Version query**  
The interface shall provide `GET /api/v1/version` representing `IF03-OP-001`.

**IF03-REQ-004 — Status query**  
The interface shall provide `GET /api/v1/status` representing `IF03-OP-002`.

**IF03-REQ-005 — Live status/event delivery**  
The interface shall provide WebSocket `/api/v1/events` representing `IF03-OP-003` for the first executable.

**IF03-REQ-006 — Reconnect to authoritative state**  
A client that connects/reconnects shall receive a complete current status snapshot before relying on subsequent live events.

**IF03-REQ-007 — Machine-readable representation**  
The HTTP query representation shall be machine-readable JSON suitable for SI-02/SI-03 and automated ST-1 verification.

**IF03-REQ-008 — Explicit failure response**  
Unsupported or invalid HTTP requests shall produce the explicit JSON failure outcome defined in this IDD rather than a successful response containing silently invalid data.

**IF03-REQ-009 — Safe default listen scope**  
Without explicit configuration the first-executable IF-03 service shall bind only to a local/loopback interface.

**IF03-REQ-010 — Compatible extension**  
Clients shall be able to ignore unknown response members/event types within API major version `v1`; breaking contract changes shall not silently redefine existing `v1` semantics.

## Relationship to SI-01 SRD

| IDD obligation | SI-01 requirement(s) |
| --- | --- |
| IF03-REQ-001 | SI01-REQ-022, SI01-REQ-030 |
| IF03-REQ-002 | SI01-REQ-031 |
| IF03-REQ-003 | SI01-REQ-010, SI01-REQ-011 |
| IF03-REQ-004 | SI01-REQ-020, SI01-REQ-021, SI01-REQ-022 |
| IF03-REQ-005/006 | SI01-REQ-023 |
| IF03-REQ-007/008 | SI01-REQ-031 |
| IF03-REQ-009 | SI01-REQ-032 |
| IF03-REQ-010 | SI01-REQ-033 |

The SRD references this contract instead of duplicating transport schema details.

## First AP-1 verification case

Verification-case identifiers use `VC-<profile>-<number>` for this baseline.

### VC-ST1-001 — Query and resynchronise first-executable status

Trace target:

```text
UC-001 / UC-008
  -> SI01-REQ-010/011/020/021/022/023/031/032/033
  -> IF03-REQ-001..010 as applicable
  -> SI-01 status/application boundary from SAD/SDD
  -> VC-ST1-001
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

A07 separately verifies the `STATUS_CHANGED` broadcast path at adapter level. End-to-end black-box verification of a real `STATUS_CHANGED` event is added when a supported public capability can actually change the authoritative status. The test driver shall not fabricate or directly mutate status solely to satisfy that event case.

The test driver shall not mutate internal Java objects or inspect private implementation state to obtain the pass/fail result.

## Remote shell scope

The first executable may expose equivalent version/status semantics through a remote-shell adapter as required by the SIP, but AP-1 does **not** introduce a separate system IDD for that transport.

Reason:

- the public software-to-software contract needed by SI-02/SI-03/ST-1 is IF-03;
- remote-shell technology is an implementation/support adapter concern at this stage;
- it must reuse the shared version/status application queries and must not own a separate authoritative model.

If the remote shell later becomes a stable externally consumed system interface, it should receive an appropriate IDD then.

## Deferred interface scope

The following IF-03 capabilities are visible in later use cases/architecture but intentionally outside this AP-1 baseline:

- open/close TimingNode commands;
- start procedure;
- RFID power/reinitialisation commands;
- ready-team add/remove;
- manual registration/penalty/revocation;
- registration/history queries;
- reference-data administration;
- backoffice controls;
- detailed diagnostics/support export;
- production authentication/role-based authorisation;
- browser CORS/origin policy beyond later SI-03 needs.

They should be added when their corresponding SIP capability approaches implementation.

## Remaining AP-1 implementation choices

The following are implementation/toolchain selections rather than unresolved interface semantics and may be chosen in the implementation repository/toolchain step:

- concrete Java HTTP/WebSocket library;
- concrete remote-shell library/technology;
- concrete JSON library;
- concrete configuration library;
- exact JDK/Maven/toolchain provisioning.

Changing one of these libraries must not silently change the contract defined above.
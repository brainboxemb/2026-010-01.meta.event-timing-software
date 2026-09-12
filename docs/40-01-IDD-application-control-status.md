# Application Control and Status Interface (IDD)

Status: working draft / AP-1 first-executable slice

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

SI-01 owns the authoritative application/status state. Clients observe/query that state and later submit permitted commands; they do not become authoritative merely by caching a response.

## Transport baseline

Current architectural direction:

- HTTP with JSON representation for request/response queries and later commands;
- WebSocket for live status/event delivery;
- network boundary usable when SI-01 and the client run on different hosts;
- the same semantic application model is also represented through local console/remote-shell adapters, but those transports are not owned by this IDD.

The first-executable contract must remain compatible with Java 8 and the mandatory Raspberry Pi Zero target, but this IDD does not select a concrete Java HTTP/WebSocket library.

## First-executable semantic operations

### IF03-OP-001 — Get build/version identity

Purpose: allow a client to identify the exact SI-01 application build it is communicating with.

Semantics:

- returns the authoritative application build/version identity;
- does not derive a separate client-specific version value;
- remains stable for the lifetime of one running application build;
- is equivalent in meaning to version identity shown by first-executable console/remote-shell views.

The exact field set is an AP-1 open decision.

### IF03-OP-002 — Get current status snapshot

Purpose: obtain a coherent current application status snapshot.

For the first executable, the snapshot must be able to represent at least:

- application/build identity or a stable reference to it;
- process/application availability state;
- configured timing-system instance identity/identities;
- minimal lifecycle state for those instances;
- observable first-executable startup/configuration degradation or errors.

Later subsystem/device/backoffice fields may extend the model without changing the ownership principle.

### IF03-OP-003 — Subscribe to status/event updates

Purpose: allow a connected client to observe live status changes without polling as the only mechanism.

Semantics:

- uses the same authoritative status model as `IF03-OP-002`;
- does not make WebSocket delivery authoritative over queryable application state;
- reconnect/resynchronisation must ultimately permit the client to recover a complete current state rather than relying forever on a missed event history.

The first-executable event envelope and resynchronisation handshake remain to be finalised in AP-1.

## First-executable contract rules

**IF03-REQ-001 — Shared semantics**  
HTTP/JSON and WebSocket representations shall map to the shared SI-01 application/status semantics rather than implement independent business/status state in the transport adapter.

**IF03-REQ-002 — Remote-host operation**  
The interface shall work across a normal IP network boundary so a client can run on a workstation while SI-01 runs on another host such as a Raspberry Pi.

**IF03-REQ-003 — Version query**  
The interface shall provide an operation representing `IF03-OP-001`.

**IF03-REQ-004 — Status query**  
The interface shall provide an operation representing `IF03-OP-002`.

**IF03-REQ-005 — Live status/event delivery**  
The interface shall provide WebSocket-based live delivery representing `IF03-OP-003` for the first executable.

**IF03-REQ-006 — Reconnect to authoritative state**  
A client that reconnects after missing live updates shall be able to obtain a complete current status snapshot before relying on subsequent live events.

**IF03-REQ-007 — Machine-readable representation**  
The HTTP query representation shall be machine-readable JSON suitable for SI-02/SI-03 and automated ST-1 verification.

**IF03-REQ-008 — Explicit failure response**  
Unsupported or invalid requests shall produce an explicit interface-level failure outcome rather than a successful response containing silently invalid data.

The concrete HTTP status/error-body mapping remains an AP-1 open decision.

## Relationship to SI-01 SRD

The following allocation is the current first-slice view:

| IDD obligation | SI-01 requirement(s) |
| --- | --- |
| IF03-REQ-001 | SI01-REQ-022, SI01-REQ-030 |
| IF03-REQ-002 | first-executable network boundary; SI01-REQ-031 |
| IF03-REQ-003 | SI01-REQ-010, SI01-REQ-011 |
| IF03-REQ-004 | SI01-REQ-020, SI01-REQ-021, SI01-REQ-022 |
| IF03-REQ-005/006 | SI01-REQ-023 |
| IF03-REQ-007 | SI01-REQ-031 |

The SRD references the IDD contract instead of duplicating transport schema details.

## ST-1 verification intent

The first executable should permit a system-test driver to run against SI-01 as a separate process and demonstrate at least:

1. establish network connectivity to IF-03;
2. obtain build/version identity;
3. obtain current status;
4. verify at least one configured `TimingSystemInstance` is represented;
5. observe a status/event update over WebSocket;
6. disconnect/reconnect;
7. obtain a fresh complete status snapshot and continue receiving live updates.

No direct Java object access or filesystem inspection should be required for the client to validate these externally observable semantics.

## Deferred interface scope

The following IF-03 capabilities are visible in later use cases/architecture but intentionally outside this AP-1 baseline:

- open/close timing-system commands;
- start procedure;
- RFID power/reinitialisation commands;
- ready-team add/remove;
- manual registration/penalty/revocation;
- registration/history queries;
- reference-data administration;
- backoffice controls;
- detailed diagnostics/support export;
- authentication/role-based authorisation policy unless AP-1 determines a minimal first-executable rule is required.

They should be added when their corresponding SIP capability approaches implementation.

## AP-1 open decisions

The following decisions must become concrete enough before this IDD is review-ready for SIP Step 3 implementation:

- HTTP base path and operation/resource paths;
- stable JSON field names/types for build identity and first status snapshot;
- WebSocket path;
- event envelope/type/versioning strategy;
- initial connection behaviour: explicit snapshot request, automatic snapshot event, or both;
- reconnect/resynchronisation sequence;
- error response structure and HTTP status mapping;
- compatibility/version negotiation strategy for future client/server evolution;
- whether a minimal authentication policy is needed in the first executable or explicitly deferred;
- CORS/origin/network-access policy needed for later browser use versus the first SI-02/ST-1 clients.

These are interface-design questions for AP-1, not implementation-library choices.
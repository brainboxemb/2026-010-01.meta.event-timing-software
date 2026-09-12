# Timing Application Requirements (SRD)

Status: working draft / AP-1 first-executable slice

Software item: **SI-01 — Headless Timing Application**

## Purpose

This Software Requirements Document captures only the SI-01 requirements needed for the **first executable slice** covered by SIP Steps 2–3.

It is intentionally incomplete for the future product. RFID, CAN, displays, registration-domain behaviour, ready-team behaviour and production backoffice integration remain outside this requirement baseline until their SIP increments approach implementation.

The goal is to make the first executable implementable without forcing the implementation repository to invent externally visible behaviour.

## Inputs

This first slice is derived from:

- `04-UC-system-use-cases.md`, especially the status/control aspects of UC-001, UC-008 and UC-009;
- `11-SIP-software-implementation-planning.md`, Steps 2–3;
- `30-SSAD-software-system-architecture.md`;
- `31-01-SAD-timing-application-architecture.md`;
- `50-SVP-software-verification-plan.md`, especially ST-1.

Interface semantics for IF-03 are owned by `40-01-IDD-application-control-status.md`. This SRD references that interface rather than duplicating its protocol contract.

## Requirement identifier convention

Requirements in this working slice use:

```text
SI01-REQ-<number>
```

The identifier convention is provisional until AP-1 closes, but identifiers should remain stable once the slice becomes a review baseline.

## First-executable requirements

### Process lifecycle and configuration

**SI01-REQ-001 — Start from external configuration**  
SI-01 shall start using externally supplied configuration rather than requiring production/deployment values to be compiled into application code.

**SI01-REQ-002 — Clean process shutdown**  
SI-01 shall support a controlled shutdown path that terminates the first-executable runtime without requiring forced process termination during normal operation/testing.

**SI01-REQ-003 — Minimal timing-system composition**  
The first executable shall support configuration of at least one `TimingSystemInstance` with a stable instance identifier that can be represented in application status.

Detailed registration assets/sources/devices are not required by this first slice.

### Build and version identity

**SI01-REQ-010 — Single application build identity**  
A running SI-01 process shall expose one authoritative application build/version identity derived from the produced application artifact/build.

**SI01-REQ-011 — Consistent identity across interfaces**  
The build/version identity exposed through supported first-executable operator/application interfaces shall represent the same underlying build identity rather than interface-specific copies.

The transport representation is defined by the applicable IDD/interface design.

### Status

**SI01-REQ-020 — Authoritative current status snapshot**  
SI-01 shall maintain an authoritative current application status model that is separate from log output.

**SI01-REQ-021 — Minimum first-executable status content**  
The first-executable status shall expose enough information to determine at least:

- application/build identity;
- whether the process is running and able to answer application queries;
- configured `TimingSystemInstance` identity/identities;
- the current lifecycle state represented by the minimal first-executable instance model;
- explicit degraded/error information for first-executable configuration/startup failures that remain observable while the process can continue serving status.

The exact schema and field names belong to IF-03 and implementation design.

**SI01-REQ-022 — Equivalent status semantics across first interfaces**  
Local console, remote-shell and IF-03 application-control/status representations shall be derived from the same application status semantics. A transport adapter shall not maintain a separate authoritative status model.

**SI01-REQ-023 — Status-change publication**  
Where IF-03 WebSocket/event delivery is enabled by the first executable, SI-01 shall publish status-change information from the same authoritative status model used for status queries.

The exact event envelope and resynchronisation rules remain to be defined by IF-03 before AP-1 closes.

### Application boundary and testability

**SI01-REQ-030 — Shared application behaviour**  
Transport-specific adapters shall invoke shared SI-01 application commands/queries rather than implementing independent copies of version/status behaviour.

**SI01-REQ-031 — Externally testable executable**  
The produced SI-01 application shall support ST-1 verification as a separate running process through its public application interface without direct test mutation of internal application/domain state.

## Explicitly deferred requirements

The following areas are intentionally not made concrete by this SRD slice:

- RFID power/read/filter/decryption behaviour;
- registration and source-sequence behaviour beyond any minimal topology placeholder needed for configuration;
- ready-team/start/penalty behaviour;
- CAN/keypad/Display V1;
- smart Display V2;
- persistence/backup of operational timing data;
- backoffice semantic/protocol behaviour;
- RabbitMQ-specific behaviour;
- target-image/update/rollback requirements beyond what the later Pi deployment increment needs;
- final authentication/authorisation and production security policy.

These areas remain governed by the working architecture/use cases until a later SIP/document-maturity gate requires formalisation.

## Initial traceability view

| Requirement | Current source | Interface/design allocation | Planned verification |
| --- | --- | --- | --- |
| SI01-REQ-001/002 | SIP Step 2–3 | SI-01 composition/runtime | build/start/stop + ST-1 process control |
| SI01-REQ-003 | SIP Step 3; SSAD runtime topology | SI-01 runtime registry/configuration | ST-1 status inspection |
| SI01-REQ-010/011 | SIP Step 2–3 | IF-01/02/03; shared query boundary | V2/V3 + ST-1 version query |
| SI01-REQ-020/021/022 | SSAD/SAD status model; SIP Step 3 | Status service/model + IF-01/02/03 | V1/V2 + ST-1 status query |
| SI01-REQ-023 | SIP Step 3; IF-03 direction | IF-03 WebSocket/event adapter | V2/V3 + ST-1 event observation |
| SI01-REQ-030/031 | SAD testability; SVP ST-1 | shared application boundary | architecture/component checks + ST-1 |

This table is a starting point. AP-1 should tighten traceability rather than expanding requirement count for its own sake.

## Open AP-1 decisions

The following need resolution before this first-executable baseline can be considered review-ready:

- exact build/version identity fields that form the stable public contract;
- exact minimal lifecycle/status representation for the placeholder `TimingSystemInstance`;
- IF-03 HTTP resource/path and JSON schema mapping;
- IF-03 WebSocket endpoint/event envelope and initial-state/resynchronisation behaviour;
- remote-shell technology and the degree to which IF-02 needs a separate formal IDD now versus later;
- error response semantics for malformed/unsupported application queries;
- whether authentication is explicitly out of scope for the first executable or whether a minimal policy is required from the start;
- exact verification-case identifier convention.

Questions that do not block SIP Steps 2–3 should remain deferred.
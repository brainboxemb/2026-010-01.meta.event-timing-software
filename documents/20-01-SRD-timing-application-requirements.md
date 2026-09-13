<!-- Generated review/output copy. Edit the source document on the source branch. -->

# Timing Application Requirements (SRD)

Status: review candidate / AP-1 first-executable slice

Software item: **SI-01 — Headless Timing Application**

## Purpose

This Software Requirements Document captures only the SI-01 requirements needed for the **first executable slice** covered by the current framework-skeleton and minimal version/status SIP increments.

It is intentionally incomplete for the future product. RFID, CAN, displays, registration-domain behaviour, ready-team behaviour and production backoffice integration remain outside this requirement baseline until their SIP increments approach implementation.

The goal is to make the first executable implementable without forcing the implementation repository to invent externally visible behaviour.

## Inputs

This first slice is derived from:

- `04-UC-system-use-cases.md`, especially the status/control aspects of UC-001, UC-008 and UC-009;
- `11-SIP-software-implementation-planning.md`, the framework-skeleton and minimal version/status increments;
- `30-SSAD-software-system-architecture.md`;
- `31-01-SAD-timing-application-architecture.md`;
- `50-SVP-software-verification-plan.md`, especially ST-1.

Interface semantics for IF-03 are owned by `40-01-IDD-application-control-status.md`. This SRD references that interface rather than duplicating its protocol contract.

## Requirement identifier convention

Requirements in this slice use:

```text
SI01-REQ-<number>
```

Identifiers in this review candidate are intended to remain stable. A later capability should add requirements without renumbering these merely for document neatness.

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

The public representation and required fields are defined by IF-03.

### Status

**SI01-REQ-020 — Authoritative current status snapshot**  
SI-01 shall maintain an authoritative current application status model that is separate from log output.

**SI01-REQ-021 — Minimum first-executable status content**  
The first-executable status shall expose enough information to determine at least:

- application/build identity;
- application state;
- configured `TimingSystemInstance` identity/identities;
- the current minimal lifecycle state represented for those instances;
- explicit degraded/error information for first-executable configuration/startup failures that remain observable while the process can continue serving status.

The concrete IF-03 schema is defined by `40-01-IDD-application-control-status.md`.

**SI01-REQ-022 — Equivalent status semantics across first interfaces**  
Local console, remote-shell and IF-03 application-control/status representations shall be derived from the same application status semantics. A transport adapter shall not maintain a separate authoritative status model.

**SI01-REQ-023 — Status-change publication**  
SI-01 shall publish first-executable status-change information through IF-03 WebSocket/event delivery from the same authoritative status model used for status queries.

On connection/reconnection the client shall be able to recover a complete authoritative snapshot according to the IF-03 contract.

### Application boundary and testability

**SI01-REQ-030 — Shared application behaviour**  
Transport-specific adapters shall invoke shared SI-01 application commands/queries rather than implementing independent copies of version/status behaviour.

**SI01-REQ-031 — Externally testable executable**  
The produced SI-01 application shall support ST-1 verification as a separate running process through its public application interface without direct test mutation of internal application/domain state.

**SI01-REQ-032 — Safe default network exposure**  
The first-executable IF-03 service shall default to local/loopback-only access. Non-loopback listening shall require explicit configuration until a later security/interface baseline defines production exposure and authentication policy.

**SI01-REQ-033 — Compatible first API evolution**  
SI-01 shall implement IF-03 `v1` such that compatible additions can be made without requiring clients to understand every newly added JSON member or event type; breaking interface semantics shall not silently redefine the existing `v1` contract.

## First-executable lifecycle interpretation

The first executable is not yet an operational timing implementation.

Therefore:

- application state may move through `STARTING`, `RUNNING`, `DEGRADED` and `STOPPING` according to IF-03;
- at least one configured minimal `TimingSystemInstance` is represented;
- that instance reports lifecycle `CLOSED` in this slice;
- operational open/close commands and resulting registration-stream events remain deferred to the later domain increment.

This prevents the first version/status executable from inventing partial operational semantics merely to make a demo look more complete.

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
- production authentication/authorisation and final security policy;
- browser-specific CORS/origin policy.

These areas remain governed by the working architecture/use cases until a later SIP/document-maturity gate requires formalisation.

## Traceability view

| Requirement | Current source | Interface/design allocation | Planned verification |
| --- | --- | --- | --- |
| SI01-REQ-001/002 | SIP framework/version-status increments | SI-01 composition/runtime | build/start/stop + ST-1 process control |
| SI01-REQ-003 | UC-001; SSAD runtime topology | SI-01 runtime registry/configuration | `VC-ST1-001` status inspection |
| SI01-REQ-010/011 | UC-008/009; SIP first executable | IF-01/02/03; shared query boundary | V2/V3 + `VC-ST1-001` |
| SI01-REQ-020/021/022 | UC-001/008/009; SSAD/SAD status model | Status service/model + IF-01/02/03 | V1/V2 + `VC-ST1-001` |
| SI01-REQ-023 | first executable live status need | IF-03 WebSocket/event adapter | V2/V3 + `VC-ST1-001` |
| SI01-REQ-030/031 | SAD testability; SVP ST-1 | shared application boundary | architecture/component checks + `VC-ST1-001` |
| SI01-REQ-032 | AP-1 controlled development exposure | IF03-REQ-002/009 | configuration/interface verification |
| SI01-REQ-033 | AP-1 interface evolution policy | IF03-REQ-010 | contract/component verification |

## AP-1 decisions resolved by this baseline

The following are now fixed for the first-executable contract:

- build/version identity fields are owned by IF-03: `application`, `version`, `revision`, `buildTime`, `apiVersion`;
- minimal application status/lifecycle semantics are defined in IF-03 and the lifecycle interpretation above;
- IF-03 HTTP resources are `/api/v1/version` and `/api/v1/status`;
- IF-03 WebSocket endpoint is `/api/v1/events`;
- WebSocket connect/reconnect starts with a complete status snapshot;
- first-executable change events carry complete current status rather than a patch/replay protocol;
- explicit JSON error responses and initial HTTP status mapping are defined in the IDD;
- authentication/authorisation is explicitly deferred for the first executable while default network binding remains loopback-only;
- verification-case identifiers use `VC-<profile>-<number>` for the first baseline;
- no separate remote-shell IDD is required by AP-1 because that adapter reuses shared version/status semantics and is not yet a stable software-to-software contract.

## Remaining implementation/toolchain choices

The following do **not** block this requirement baseline and belong in the implementation/toolchain increments:

- concrete Java HTTP/WebSocket library;
- concrete remote-shell implementation;
- JSON/configuration/logging libraries;
- Maven/JDK provisioning details;
- concrete code/package classes implementing the shared status model;
- exact mechanism used to cause the first deterministic status transition in `VC-ST1-001`.

A chosen implementation technology must satisfy this SRD and IF-03 rather than redefining them.

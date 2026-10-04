# Timing Application Verification Test Specification (VTS)

Status: working / review baseline

Software item: **SI-01 — Timing Point Application**


## Purpose

This document specifies the concrete verification cases used to test SI-01.
It is downstream from product requirements, interface contracts and detailed
design. It does not create product behaviour.

The document roles are deliberately separate:

- `60-SVP-software-verification-plan.md` defines verification strategy, levels,
  ST profiles, environments and evidence rules;
- this VTS defines stable `VC-...` cases: purpose, setup, procedure and expected
  result;
- executable tests implement these cases in the implementation repository;
- generated/retained verification evidence records what revision was executed,
  PASS/FAIL and the produced logs/artifacts.

Current execution status is therefore **not** maintained in this document.

## Terms and abbreviations

- **VTS** — Verification Test Specification
- **VC** — Verification Case
- **SVP** — Software Verification Plan
- **SI** — Software Item
- **ST** — System Test profile


## Relationship to other documents

The cases below verify accepted behaviour from:

- `41-01-SSD-timing-application-specification-document.md`;
- applicable system-owned ISDs, especially
  `32-03-ISD-application-control-status.md`;
- `60-SVP-software-verification-plan.md` for the ST profile and evidence model.

The VTS may reference SDDs to understand test setup, but an SDD or VTS does not
become upstream product authority by being referenced here.

## Case identifier convention

Verification cases use:

```text
VC-<profile>-<number>
```

For example `VC-ST1-002` is case 002 in the ST-1 application-behaviour
profile.

Executable Java system-test classes use the same case identity in a
Java-identifier-safe form:

```text
VC-ST1-001  ->  VcSt1_001Test
VC-ST1-002  ->  VcSt1_002Test
VC-ST1-004  ->  VcSt1_004Test
```

The case ID is authoritative. The Java class name preserves that ID so the
mapping remains obvious in source trees and Surefire reports; descriptive
behaviour belongs in the VTS case title and test method name rather than in a
long generic class name.

## ST-1 — Application behaviour

ST-1 runs the packaged SI-01 application as a separate process and drives it
through public interfaces. The test driver must not mutate internal product Java
objects or depend on product implementation classes to obtain the pass/fail
result.

### VC-ST1-001 — Query and resynchronise first-executable status

```{vc} Query and resynchronise first-executable status
---
id: VC-ST1-001
verifies: >-
  SI01-REQ-001, SI01-REQ-002, SI01-REQ-003, SI01-REQ-010,
  SI01-REQ-020, SI01-REQ-021, SI01-REQ-031,
  IF03-REQ-003, IF03-REQ-004, IF03-REQ-005, IF03-REQ-006
---
```

**Executable test**

`system-test/.../VcSt1_001Test.java`

**Purpose**

Verify that the packaged application can start from external configuration,
expose its build/status state through IF-03, resynchronise a WebSocket client
after reconnect and shut down through the supported controlled path.

**Setup**

- packaged SI-01 application JAR;
- synthetic configuration with at least one TimingNode;
- loopback HTTP, WebSocket and controlled-shutdown endpoints;
- independent black-box test driver.

**Procedure**

1. Start SI-01 as a separate process with the synthetic configuration.
2. Wait for the configured IF-03 HTTP endpoint to become available.
3. Call `GET /api/v1/version` and verify the required build/version identity.
4. Call `GET /api/v1/status` and verify the configured TimingNode is present
   with its current state.
5. Connect to `/api/v1/events` and verify the first application message is a
   complete `STATUS_SNAPSHOT`.
6. Disconnect the WebSocket client.
7. Reconnect and verify a new complete `STATUS_SNAPSHOT` is received before
   later live events are relied upon.
8. Query status again and verify it is semantically consistent with the latest
   snapshot.
9. Shut SI-01 down through the supported controlled-shutdown path.

**Expected result**

- version and status are available through the running packaged application;
- connect/reconnect starts from a complete current status snapshot;
- the latest status query and reconnect snapshot describe the same current
  TimingNode state;
- the process exits cleanly without forced termination.

Adapter/component tests may cover additional event-path details that are not yet
observable through a supported black-box state-changing operation.

### VC-ST1-002 — Control and observe first committed registration

```{vc} Control and observe first committed registration
---
id: VC-ST1-002
verifies: >-
  SI01-REQ-040, SI01-REQ-041, SI01-REQ-042, SI01-REQ-043, SI01-REQ-047,
  IF03-REQ-011, IF03-REQ-012, IF03-REQ-013, IF03-REQ-014, IF03-REQ-015
---
```

**Executable test**

`system-test/.../VcSt1_002Test.java`

**Purpose**

Verify the first public registration slice through a real SI-01 process:
operational LocationId/lifecycle control, capability-gated engineering
registration input, committed LogBook/history and live post-commit observation.

The second process run verifies the restart-recovery requirement
`SI01-REQ-047`. Invalid/corrupt/incomplete recovery cases from
`SI01-REQ-048` remain component-level persistence/codec verification rather
than being forced into this happy-path black-box case.

**Setup**

- packaged SI-01 application JAR;
- deterministic synthetic TimingNode configuration;
- direct registration simulation supported and enabled;
- persistent TimingData file shared by the two process runs;
- independent IF-03 black-box test driver.

**Procedure — run 1**

1. Start SI-01 and verify the TimingNode is `CLOSED` with no current LocationId.
2. Request `OPEN` with synthetic LocationId `24` and verify the node becomes
   `OPEN` with LocationId `24` as one processed operation.
3. Submit one node-addressed dev auto-reg request with deterministic `id` and
   `time`.
4. Verify the response returns sequence 1 and that the request did not supply
   source identity or active location.
5. Query LogBook metadata and verify one committed record with first/last
   sequence 1.
6. Fetch a bounded LogBook range and verify the sequence-1 record contains the
   active LocationId and supplied time.
7. Verify one `TIMING_DATA_COMMITTED` live event represents the same Node ID +
   sequence number.
8. Request `CLOSE` and verify `CLOSED`.
9. Disconnect and reconnect the WebSocket client.
10. Verify the new session starts with a current `STATUS_SNAPSHOT`, the
    committed LogBook record remains queryable and the old record is not emitted
    again as a new `TIMING_DATA_COMMITTED` event.
11. Shut the first SI-01 process down through the controlled path.

**Procedure — run 2 restart recovery**

1. Start a second SI-01 process with the same TimingData persistence file.
2. Verify the TimingNode starts `CLOSED` with no current operational LocationId.
3. Verify the LogBook still contains the original sequence-1 record with the
   same Node ID + sequence number.
4. Verify the WebSocket session starts with `STATUS_SNAPSHOT` and the recovered
   record is not emitted as a new `TIMING_DATA_COMMITTED` event.
5. Shut the second process down through the controlled path.

**Expected result**

- lifecycle rules gate registration correctly;
- SI-01, not the client, supplies the committed source/location/sequence context;
- one accepted registration becomes one committed history record and one live
  post-commit event;
- reconnect exposes current state/history without re-emitting the historical
  record as a new commit;
- the second process run rebuilds the committed record while operational state
  starts CLOSED/no-location.

### VC-ST1-003 — Development Client reconnect/resynchronisation integration

```{vc} Development Client reconnect/resynchronisation integration
---
id: VC-ST1-003
verifies: >-
  SI01-REQ-044, IF03-REQ-016
---
```

**Purpose**

Verify through the real JavaFX Development Client that the accepted API-first client can
drive and observe the Step-4 public flow without private SI-01 state, and can rebuild
current status plus bounded TimingData history after reconnect/restart before presenting
that history as LIVE.

This manual case does not re-prove the server-side lifecycle, registration, LogBook
persistence or restart recovery already covered by `VC-ST1-002`.

**Setup**

- packaged SI-01 application started with the dedicated Step-4 demo
  configuration/storage;
- JavaFX Development Client started independently on Java 17;
- public IF-03, Remote Shell and LoggingServer boundaries only;
- one deterministic registration `N0001` committed during the first run.

**Procedure**

1. Start SI-01 with empty Step-4 demo storage and start the Development Client.
2. Verify the target host/IP is editable, **Apply target** selects the active host and the
   stateless API **CHECK** reports the IF-03 HTTP boundary as READY.
3. Verify the main client tabs are **API**, **Events**, **Device Log**, **Terminal** and
   **Client Log**, with Device Log and Client Log independent.
4. Verify the prominent **Timing view** state above Version/Status initially shows
   **NOT SYNCED — connect Events**. Connect **Events** and verify it changes to
   **SYNCING**, keeps mutating controls disabled and becomes **LIVE** only after the
   status/capabilities/LogBook baseline plus buffered live events are reconciled.
5. Enter Location ID 24 and OPEN the TimingNode. Verify OPEN applies LocationId 24 in the
   same request; no separate Set Location operation is used.
6. Enter date `2026-10-01` and time `12:00:00`, then commit deterministic auto-reg
   `N0001`. Verify the Development Client shows the interpreted time zone beside the
   field and that the public record contains the correct canonical UTC equivalent. For
   `Europe/Amsterdam` on this date, `12:00:00` maps to
   `2026-10-01T10:00:00Z`.
7. Verify the interpreted **Registrations** view shows one row with normal local clock
   time, Type `AUTO`, TeamID unresolved (`-`) while no reference-data mapping is
   available, an empty Code cell, and an icon-only disabled trash action with no text column
   heading.
8. Verify sequence 1 appears separately in the technical LogBook with RegistrationId
   `N0001`, Type `AUTO_REG` and Code `ADD` shown separately, and inspect the
   complete selected public record/raw response.
9. Verify one matching `TIMING_DATA_COMMITTED` live event is visible.
10. Verify Client Log remains usable independently of the SI-01 Device Log connection and
   that Events, Terminal and Device Log can be connected/disconnected independently.
11. CLOSE the TimingNode and stop SI-01 through the supported Terminal control.
12. Keep the demo TimingData file, restart SI-01 and reconnect Events.
13. Verify the client resynchronises to current CLOSED/no-location status, restores
    sequence 1 / `N0001` in both the interpreted registration view and bounded technical
    history, does not present recovered history as a new live commit and merges any
    history/live overlap by stable record key.
14. Verify the history view reaches LIVE only after baseline plus buffered live events are
    reconciled, then shut SI-01 down cleanly.

**Expected result**

- the current API-first Development Client reaches all required public Step-4 boundaries;
- Open carries LocationId and SI-01 remains authoritative for command acceptance;
- committed TimingData is visible both as an interpreted registration and as immutable
  technical LogBook history, plus live delivery;
- Device Log and Client Log remain independent;
- reconnect/restart is visible as synchronisation rather than immediately LIVE;
- history is resynchronised before LIVE presentation;
- duplicate history/live observations collapse to one record;
- recovered historical data is not presented as a new committed event;
- the running-system flow uses no private SI-01 state.

**Execution**

This remains a manual verification case. The executable checklist is maintained in the
Java repository at `test-client/STEP4-DEMO.md`; run-specific PASS/FAIL, revisions and
supporting artifacts are retained with Java issue #127 rather than in this VTS.

## Evidence

A VTS case defines what must be exercised and observed; it does not say that a
particular revision has passed.

Retained evidence should identify at least:

- verification-case ID;
- tested source/build revision;
- PASS/FAIL;
- executable test report;
- captured process output where useful;
- produced persistence/log artifacts required to support the result.

The implementation repository and CI publication own those run-specific
artifacts.

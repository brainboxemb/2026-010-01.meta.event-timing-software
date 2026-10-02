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

## Inputs and references

The cases below verify accepted behaviour from:

- `41-01-SSD-timing-application-specification-document.md`;
- applicable system-owned IDDs, especially
  `32-03-IDD-application-control-status.md`;
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
  SI01-REQ-040, SI01-REQ-041, SI01-REQ-042, SI01-REQ-043,
  IF03-REQ-011, IF03-REQ-012, IF03-REQ-013, IF03-REQ-014, IF03-REQ-015
---
```

**Executable test**

`system-test/.../VcSt1_002Test.java`

**Purpose**

Verify the first public registration slice through a real SI-01 process:
operational LocationId/lifecycle control, capability-gated engineering
registration input, committed LogBook/history and live post-commit observation.

The case also retains a second-process restart/recovery check as robustness
evidence for the current implementation. That extra check does not create a new
product requirement.

**Setup**

- packaged SI-01 application JAR;
- deterministic synthetic TimingNode configuration;
- direct registration simulation supported and enabled;
- persistent TimingData file shared by the two process runs;
- independent IF-03 black-box test driver.

**Procedure — run 1**

1. Start SI-01 and verify the TimingNode is `CLOSED` with no current LocationId.
2. Set synthetic LocationId `24` and verify the node remains `CLOSED`.
3. Request `OPEN` and verify the same LocationId remains active.
4. Attempt another location change and verify explicit `NODE_NOT_CLOSED`
   rejection.
5. Submit one node-addressed dev auto-reg request with deterministic `id` and
   observation `time`.
6. Verify the response returns sequence 1 and that the request did not supply
   source identity, active location or recorded time.
7. Query LogBook metadata and verify one committed record with first/last
   sequence 1.
8. Fetch a bounded LogBook range and verify the sequence-1 record contains the
   active LocationId and supplied observation time.
9. Verify one `TIMING_DATA_COMMITTED` live event represents the same stable
   record key.
10. Request `CLOSE` and verify `CLOSED`.
11. Disconnect and reconnect the WebSocket client.
12. Verify the new session starts with a current `STATUS_SNAPSHOT`, the
    committed LogBook record remains queryable and the old record is not emitted
    again as a new `TIMING_DATA_COMMITTED` event.
13. Shut the first SI-01 process down through the controlled path.

**Procedure — run 2 robustness evidence**

1. Start a second SI-01 process with the same TimingData persistence file.
2. Verify the TimingNode starts `CLOSED` with no current operational LocationId.
3. Verify the LogBook still contains the original sequence-1 record with the same
   stable key.
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
- the retained second-run robustness check recovers the committed record while
  operational state starts CLOSED/no-location.

## Engineering Client verification

The Engineering Client reconnect algorithm is not proven by VC-ST1-002 merely
because the server supports history and live events.

The Step-4 Engineering Client verification separately checks the behaviour
described by `SI01-REQ-044` / `IF03-REQ-016`: rebuild current status and
bounded history, buffer later live events, merge/deduplicate by stable TimingData
record key, then declare the view live.

The current manual running-system procedure is maintained with the Engineering
Client implementation until a dedicated automated client verification case is
introduced.

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

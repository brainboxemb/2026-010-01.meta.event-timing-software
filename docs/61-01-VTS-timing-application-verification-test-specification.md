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
VC-ST1-005  ->  VcSt1_005Test
VC-ST1-006  ->  VcSt1_006Test
```

The case ID is authoritative. The Java class name preserves that ID so the
mapping remains obvious in source trees and Surefire reports; descriptive
behaviour belongs in the VTS case title and test method name rather than in a
long generic class name.

Within a profile, each verification case is represented directly by its `{vc}`
object. The need owns the stable VC ID, descriptive title and traceability identity;
do not add a second Markdown heading for the same case.

## ST-1 — Application behaviour

ST-1 runs the packaged SI-01 application as a separate process and drives it
through public interfaces. The test driver must not mutate internal product Java
objects or depend on product implementation classes to obtain the pass/fail
result.

:::{vc} Query and resynchronise first-executable status  
:id: VC-ST1-001  
:verifies: SI01-REQ-001, SI01-REQ-002, SI01-REQ-003, SI01-REQ-010, SI01-REQ-020, SI01-REQ-021, SI01-REQ-031, IF03-REQ-003, IF03-REQ-004, IF03-REQ-005, IF03-REQ-006  

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

:::

:::{vc} Control and observe first committed registration  
:id: VC-ST1-002  
:verifies: SI01-REQ-040, SI01-REQ-041, SI01-REQ-042, SI01-REQ-043, SI01-REQ-047, IF03-REQ-011, IF03-REQ-012, IF03-REQ-013, IF03-REQ-014, IF03-REQ-015, IF05-REQ-003, IF05-REQ-008, IF05-REQ-009  

**Executable test**

`system-test/.../VcSt1_002Test.java`

**Purpose**

Verify the first public registration slice of a real SI-01 process through
**IF-03 — Application control and status**. The independent test driver uses
IF-03 commands and queries (HTTP) and observes IF-03 live events (WebSocket)
to verify lifecycle OPEN/CLOSE records, one automatic registration, committed
LogBook/history and live post-commit observation.

The test also checks the relevant **IF-05 TimingData record semantics** through
the records exposed by IF-03 and their persistence across restart. It does not
exercise the operator's IF-04 Web interface.

The second process run verifies restart recovery. Invalid/corrupt/incomplete
storage recovery remains component-level persistence/codec verification.

**Setup**

- packaged SI-01 application JAR;
- deterministic synthetic TimingNode configuration;
- direct registration simulation supported and enabled;
- persistent TimingData file shared by the two process runs;
- independent IF-03 black-box test driver.

**Procedure — run 1**

1. Start SI-01 and verify the TimingNode is `CLOSED` with no current LocationId.
2. Request `OPEN` with LocationId `24`.
3. Verify `TIMING_DATA_COMMITTED` first exposes sequence 1 as
   `NODE_INFO`, LocationId 24, code `OPEN`; then verify the successful
   `STATUS_CHANGED` reports `OPEN` at LocationId 24.
4. Submit one node-addressed dev auto-reg request with deterministic
   RegistrationId and time. Verify the response returns sequence 2.
5. Verify one `TIMING_DATA_COMMITTED` event exposes sequence 2 as
   `AUTO_REG` with code `ADD`, the supplied RegistrationId/time and
   LocationId 24.
6. Query LogBook metadata/range and verify source order is sequence 1 OPEN,
   sequence 2 registration.
7. Request `CLOSE`. Verify sequence 3 is committed first as
   `NODE_INFO` / `CLOSE` with LocationId 24, followed by successful
   `STATUS_CHANGED` to `CLOSED`.
8. Reconnect the WebSocket client. Verify the new session starts from current
   `STATUS_SNAPSHOT`, LogBook sequences 1..3 remain queryable and recovered
   history is not emitted again as new `TIMING_DATA_COMMITTED` events.
9. Shut the first process down through the controlled path.

**Procedure — run 2 restart recovery**

1. Start a second SI-01 process with the same TimingData persistence file.
2. Verify operational state starts `CLOSED` with no current LocationId.
3. Verify LogBook contains the original three committed records, in sequence:
   OPEN, registration ADD, CLOSE.
4. Verify a new WebSocket session begins with `STATUS_SNAPSHOT` and does not
   replay those records as new commit events.
5. Shut the second process down.

**Expected result**

- lifecycle and registration records share one contiguous NodeId-scoped sequence;
- OPEN/CLOSE records reach the committed-data visibility point before the
  corresponding successful status change;
- the registration remains committed between its surrounding lifecycle records;
- reconnect/restart exposes committed history without replaying it as new live
  commits;
- operational OPEN/CLOSED state is not restored merely from historical records.

:::

:::{vc} Engineering Client reconnect/resynchronisation integration  
:id: VC-ST1-003  
:verifies: SI01-REQ-044, IF03-REQ-016, IF03-REQ-022, IF05-REQ-006, IF05-REQ-007, IF05-REQ-008  

**Purpose**

Verify through the real JavaFX Engineering Desktop Client that it can drive
and interpret the public TimingNode lifecycle/registration stream, append a
registration REV through the trash action and rebuild current status plus
bounded TimingData history after reconnect/restart without private SI-01
state. This manual case is now a Step-6 V01 acceptance scenario; it was not
executed for the Step-5 V06 server-side closeout.

**Setup**

- packaged SI-01 application with deterministic verification storage;
- SI-02 Engineering Desktop Client on Java 21/JavaFX 21, independently of SI-01;
- public IF-03, Remote Shell and LoggingServer boundaries only;
- one deterministic automatic registration.

**Procedure**

1. Start SI-01 with empty verification storage and start the Engineering Client.
2. Apply/check the target, connect Events and verify the Timing view reaches
   LIVE only after status/capabilities/LogBook baseline synchronisation.
3. OPEN LocationId 24. Verify technical LogBook sequence 1 is
   `NODE_INFO / OPEN`.
4. Commit deterministic auto-reg `RT-A-0001`. Verify the interpreted
   Registrations view shows one non-deleted AUTO row and technical LogBook
   sequence 2 is `AUTO_REG / ADD`.
5. Verify the trash action is enabled for that interpreted row. Activate it.
6. Verify sequence 3 is appended as `AUTO_REG / REV` with the same
   RegistrationId, original registration time and LocationId; sequence 2 remains
   unchanged in the technical LogBook.
7. Verify the interpreted row remains present and is displayed as `DELETED`
   instead of disappearing.
8. CLOSE the TimingNode and verify sequence 4 is `NODE_INFO / CLOSE`.
9. Stop SI-01, preserve the verification TimingData file, restart and reconnect
   Events.
10. Verify status starts CLOSED/no-location, technical history restores
    sequences 1..4, the interpreted registration is still DELETED and recovered
    records are not presented as new live commits.
11. Verify Device Log and Client Log remain independent and shut down cleanly.

**Expected result**

- the Engineering Client interprets lifecycle records separately from
  registration rows;
- trash invokes append-only public revoke rather than destructive deletion;
- ADD and REV remain independently visible in technical history;
- the interpreted row folds ADD/REV to DELETED in the client/business view;
- reconnect/restart rebuilds the same interpretation from committed history.

**Execution**

This is a Step-6 V01 manual running-system verification case executed with the packaged
SI-02 Engineering Desktop Client. Headless verification does not substitute for this GUI
evidence. Repository-local checklists may mirror it but shall not redefine it.

:::

:::{vc} Contain TimingData recovery failure and keep diagnostics available  
:id: VC-ST1-004  
:verifies: SI01-REQ-048, IF03-REQ-004, IF03-REQ-006, IF03-REQ-008, IF03-REQ-017  

**Executable test**

`system-test/.../VcSt1_004Test.java`

**Purpose**

Verify that a TimingData recovery failure is contained to the affected
TimingNode while application-level diagnostic interfaces remain available.

**Procedure**

1. Prepare a syntactically valid persisted TimingData record owned by a
   different NodeId than the configured TimingNode.
2. Start SI-01 and verify the process remains running.
3. Query IF-03 status and verify the affected node is `ERROR` with
   `TIMING_DATA_RECOVERY_FAILED`.
4. Query the Remote Shell status and verify the same contained problem.
5. Attempt OPEN and verify an explicit failure response rather than normal
   acceptance.
6. Connect/reconnect IF-03 events and verify each session starts with an ERROR
   status snapshot that retains the problem.
7. Shut down through the supported control path.

**Expected result**

- invalid recovered ownership does not terminate SI-01;
- the affected TimingNode remains contained in ERROR;
- HTTP, WebSocket and Remote Shell diagnostics remain usable;
- normal state-changing work is rejected explicitly.

:::

:::{vc} Verify lifecycle TimingData source ordering and recovery  
:id: VC-ST1-005  
:verifies: IF03-REQ-011, IF03-REQ-014, IF03-REQ-015, IF05-REQ-002, IF05-REQ-003, IF05-REQ-008, IF05-REQ-009, IF05-REQ-010  

**Executable test**

`system-test/.../VcSt1_005Test.java`

**Purpose**

Verify V05 through public interfaces: lifecycle records use the normal source
sequence with registrations, idempotent lifecycle requests create no record,
restart recovers history and the next successful transition continues the
sequence.

**Procedure**

1. Start with empty TimingData storage and connect IF-03 events.
2. OPEN LocationId 24 and verify sequence 1 is `NODE_INFO / OPEN`.
3. Repeat OPEN while already OPEN. Verify `ALREADY_OPEN`, no new committed
   lifecycle event and LogBook count remains 1.
4. Commit one deterministic auto registration and verify sequence 2.
5. CLOSE and verify sequence 3 is `NODE_INFO / CLOSE`.
6. Repeat CLOSE. Verify `ALREADY_CLOSED`, no new commit and count remains 3.
7. Shut down and restart against the same persistence file.
8. Verify sequences 1..3 recover in exact source order and are not replayed live.
9. OPEN LocationId 25 and verify the newly committed OPEN record is sequence 4,
   proving sequence continuity after recovery.
10. Shut down cleanly.

**Expected result**

- actual CLOSED->OPEN and OPEN->CLOSED transitions each create exactly one
  lifecycle TimingData record;
- no-op/already-in-state lifecycle calls create none;
- registrations and lifecycle records share one contiguous sequence;
- restart preserves committed order and the next record continues it.

:::

:::{vc} Verify append-only registration revoke bookkeeping  
:id: VC-ST1-006  
:verifies: IF03-REQ-008, IF03-REQ-014, IF03-REQ-015, IF03-REQ-022, IF05-REQ-002, IF05-REQ-003, IF05-REQ-005, IF05-REQ-006, IF05-REQ-007  

**Executable test**

`system-test/.../VcSt1_006Test.java`

**Purpose**

Verify V06 server-side revoke semantics through public IF-03 while preserving
the bookkeeping/business boundary: REV appends history and never rewrites ADD;
TimingNode/LogBook do not infer an already-deleted business state.

**Procedure**

1. Start with empty TimingData storage and OPEN LocationId 24, producing
   lifecycle sequence 1.
2. Commit automatic registration `RT-A-0006` at a deterministic time; verify
   `AUTO_REG / ADD` sequence 2.
3. POST IF03-OP-011 using the original record family, LocationId,
   RegistrationId and time.
4. Verify response sequence 3 and one committed `AUTO_REG / REV` record with
   the same LocationId, RegistrationId and original time.
5. Query LogBook and verify the original sequence-2 ADD is unchanged and both
   records are present.
6. Deliberately submit the same well-formed revoke again. Verify bookkeeping
   does not silently fold/deduplicate business state: another REV is appended as
   sequence 4.
7. Submit a structurally invalid MAN_REG revoke without required AUTO/MAN
   time-source classification. Verify an explicit 400-class failure and no new
   TimingData record.
8. Restart SI-01 using the same persistence file. Verify sequences 1..4 recover
   unchanged and are not replayed as new live events.
9. Shut down cleanly.

**Expected result**

- each accepted revoke is a new immutable REV record;
- ADD remains untouched;
- REV repeats the original registration identity values;
- raw bookkeeping does not decide whether a registration is already deleted;
- malformed interface input is rejected before commit;
- restart preserves the append-only history.

**Scope note**

The black-box flow uses AUTO_REG because the current public engineering add
stimulus is automatic-registration only. MAN_REG `REV,AUTO` / `REV,MAN`
mapping is verified at codec/domain level until a public manual-add stimulus is
part of this test profile.

:::

:::{vc} Verify two TimingNodes in one TimingSystem with separate LogBooks  
:id: VC-ST1-007  
:verifies: SI01-REQ-003, SI01-REQ-041, SI01-REQ-042, SI01-REQ-046, SI01-REQ-047, IF03-REQ-011, IF03-REQ-013, IF03-REQ-014, IF03-REQ-015, IF05-REQ-003, IF05-REQ-008, IF05-REQ-009  

**Executable test**

`system-test/.../VcSt1_007Test.java`

**Purpose**

Verify through **IF-03 HTTP** that one packaged SI-01 process with one
TimingSystem (`SID-9`) can independently operate two TimingNodes (`A`
and `B`) and persist their committed TimingData in **two different physical
LogBook files**, resolved from the `{NodeId}` path template.

**Setup**

- one TimingSystem `SID-9` containing TimingNodes `A` and `B`;
- `io.storage.timingData.path: node-{NodeId}-logbook.jsonl`;
- empty separate test/evidence directory, independent black-box test driver.

**Procedure**

1. Start the packaged application and query IF-03 status: both nodes exist,
   initially `CLOSED`.
2. Open node A at LocationId 24, add `RT-A-0001` **without API time**
   and close A.
   Query A's LogBook: ordered OPEN, ADD, CLOSE at sequences 1..3.
3. Before operating node B, query its LogBook: it remains empty.
4. Open node B at LocationId 25, add `RT-A-0002` **without API time**
   and close B. Query B's LogBook: its own sequences independently start at 1..3.
5. Stop SI-01 cleanly. Check that exactly the expected two distinct nonempty
   files exist, named for nodes A and B. Each file contains only its own
   NodeId, location and registration, with no records from the other node.
6. Restart SI-01 using the same configuration and files. Query both LogBooks
   through IF-03 and verify the separate three-record histories are recovered.

**Expected result**

- two independently addressed TimingNodes operate inside one TimingSystem;
- each node maintains its own sequence beginning at 1, without cross-node
  registrations or lifecycle records;
- two physically different LogBooks exist and survive restart, with no
  duplicated or lost records;
- simulated ADD records use the node's TimeSource and retain
  `tagSrc=API` / `timeSrc=NODE` after recovery.

:::

:::{vc} Verify two TimingSystems with one TimingNode each and separate LogBooks  
:id: VC-ST1-008  
:verifies: SI01-REQ-003, SI01-REQ-041, SI01-REQ-042, SI01-REQ-046, SI01-REQ-047, IF03-REQ-011, IF03-REQ-013, IF03-REQ-014, IF03-REQ-015, IF05-REQ-003, IF05-REQ-008, IF05-REQ-009  

**Executable test**

`system-test/.../VcSt1_008Test.java`

**Purpose**

Verify through **IF-03 HTTP** that one packaged SI-01 process can compose
two independent TimingSystems (`SID-A` and `SID-B`), each containing one
TimingNode (A and B respectively), and persist committed TimingData in
**two different physical LogBook files**. The storage path resolves both
`{SystemId}` and `{NodeId}` in this configuration.

**Setup**

- TimingSystem `SID-A` with TimingNode `A`;
- TimingSystem `SID-B` with TimingNode `B`;
- `io.storage.timingData.path: system-{SystemId}-node-{NodeId}-logbook.jsonl`;
- empty separate test/evidence directory, independent black-box test driver.

**Procedure**

1. Start the packaged application and query IF-03 status: nodes A and B
   exist and are initially `CLOSED`.
2. Open A at LocationId 24, add `RT-A-0001` **without API time**
   and close A.
   Verify B's LogBook remains empty.
3. Open B at LocationId 25, add `RT-A-0002` **without API time**
   and close B.
   Independently query each LogBook; each has OPEN, ADD, CLOSE at sequences 1..3.
4. Stop SI-01 cleanly and check both physical files. Their paths include the
   correct TimingSystemId/TimingNodeId pair and each file contains only records
   belonging to its own node.
5. Restart the same two-system configuration and verify both separate
   LogBook histories recover unchanged through IF-03.

**Expected result**

- both TimingSystems run in one SI-01 process with correct node addressing;
- each TimingNode retains an independent ordered TimingData stream;
- two physical LogBook files are created, isolated and recover independently;
- neither system's records appear in the other system's LogBook;
- simulated ADD records use each owning system's composed TimeSource and
  retain `tagSrc=API` / `timeSrc=NODE` after recovery.

:::

**Test-data scope for VC-ST1-007/008**

Here `RT-A-0001` and `RT-A-0002` are **normal RegistrationIds**;
the `A` in `RT-A` is not the TimingNode identifier. These cases inject the
RegistrationIds directly through IF-03. They do not verify the separate RFID
tag-pair mapping (`TT-A-NNNN-1/-2`) or TeamId lookup.

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

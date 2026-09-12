# Software Verification Plan (SVP)

Status: working draft / non-authoritative

This Software Verification Plan defines the initial verification strategy for the software system. It is intentionally introduced early because testability, fault handling, interface boundaries, and Raspberry Pi Zero resource constraints are architectural concerns rather than end-of-project activities.

The SVP applies across software items unless a software-item-specific verification document later adds more detail.

## Verification objectives

Verification should provide evidence that:

- requirements and interface contracts are implemented correctly;
- software-item boundaries remain usable independently;
- domain behaviour is deterministic and unit-testable;
- real and stub/proprietary adapters conform to the same public contracts;
- faults and reconnect/recovery paths behave deliberately;
- local operation remains available where required during backoffice/network outages;
- the mandatory original Raspberry Pi Zero target remains viable;
- public framework code can be consumed by external reference and private integration projects;
- generated documentation and build artifacts are reproducible and reviewable.

## Traceability direction

The intended traceability chain is:

```text
system requirement
      |
      +--> system-level IDD requirement/section where applicable
      |
      v
software-item requirement (SRD)
      |
      v
SAD / SDD design element
      |
      v
implementation
      |
      v
verification case + evidence
```

An IDD remains software-system-owned. A software-item requirement references the relevant IDD obligation rather than duplicating the interface definition.

Verification identifiers and exact requirement-reference syntax are still to be defined.

## Verification levels

### V1 — Unit verification

Purpose: verify deterministic application/domain behaviour without external processes or real hardware.

Typical techniques:

- direct/synchronous execution instead of production thread scheduling;
- `FakeClock` rather than wall-clock waiting;
- in-memory repositories;
- fake/stub RFID, CAN, display and backoffice ports;
- deterministic state-machine and filtering tests;
- sequence/traceability tests;
- restore/replay tests for local state.

Examples:

- first RFID observation does not automatically create a registration;
- `OPEN` / `CLOSED` transition rules;
- ready-team add/remove projection;
- registration and ready-team sequence allocation;
- penalty revocation references the original record;
- full Display V1 state is rebuilt from current ready-team state;
- Display V2 reconnect receives a complete current snapshot;
- status snapshots reflect subsystem state changes.

### V2 — Component/module verification

Purpose: verify one concrete adapter or component against its contract while controlling the surrounding system.

Examples:

- file backup/restore adapter;
- HTTP/JSON adapter;
- WebSocket status/event stream;
- remote shell adapter;
- CAN scanner with simulated CAN traffic;
- public stub devices;
- proprietary RFID implementation in its private repository.

### V3 — Interface verification

Purpose: verify system-level interface contracts/IDDs between software items or external systems.

Expected examples:

- local console returns the same application version/status model as other clients;
- remote shell returns the same version/status semantics;
- Desktop GUI (SI-02) connects to Timing Application (SI-01) across a real network boundary;
- Web Operator Application (SI-03) loads over HTTP and communicates through HTTP/WebSocket;
- RabbitMQ/backoffice message exchange;
- Display V2 mDNS discovery and subsequent data/session protocol;
- CAN keypad/display interactions.

These tests should verify externally observable behaviour rather than internal class structure.

### V4 — Integration/system verification

Purpose: verify multiple real components together with realistic process/network boundaries.

Candidate scenarios:

- SI-01 + SI-02 over localhost;
- SI-01 on Raspberry Pi + SI-02 on another computer;
- SI-01 + browser/iPad client;
- stub RFID + real domain pipeline + local persistence;
- CAN scanner + keypad + Display V1 stub/real hardware;
- backoffice disconnect/reconnect with local outbox;
- restart/restore followed by synchronisation;
- multiple logical `TimingSystem` instances in one runtime.

### V5 — Hardware-in-the-loop verification

Purpose: verify behaviour that cannot be adequately represented by normal automated test doubles.

Likely scope:

- original Raspberry Pi Zero runtime behaviour;
- RFID reader power/boot/reinitialisation;
- real RFID read/filter behaviour;
- real CAN bus/device discovery;
- Display V1 physical behaviour;
- Display V2 network discovery/session behaviour;
- power-cycle/restart recovery where practical.

Hardware tests should be separated from the fast normal pull-request path when they are slow, scarce, or environment-specific.

### V6 — Operational/resource verification

Purpose: verify that the implementation remains viable on the weakest mandatory target and under representative failure/load conditions.

Measure at least:

- process startup time;
- resident memory / RSS;
- configured/max heap and observed heap behaviour;
- idle CPU usage;
- representative active CPU usage;
- application/thread count;
- queue backlog/latency under representative input;
- HTTP/status response latency;
- backup/write behaviour and SD-card write rate where relevant;
- reconnect/recovery timings;
- long-running stability.

Initial tests establish a baseline. Numeric acceptance budgets should be introduced only when evidence is sufficient; this document deliberately does not invent values before measurement.

## Raspberry Pi Zero baseline evidence

The original Raspberry Pi Zero / Zero W is a mandatory target for software item 01.

The first representative executable should therefore capture a repeatable baseline on real hardware using the selected Java 8 runtime.

Minimum baseline record:

```text
hardware model / RAM
OS image/version
Java runtime vendor/version
application commit/version
configuration profile
startup time
RSS after startup
RSS after representative workload
heap settings / observed heap use
thread count
idle CPU
representative workload CPU
version/status request latency
notes / anomalies
```

A later Java 11 evaluation must compare against the same or equivalent workload and hardware rather than only desktop benchmarks.

## Fault-injection verification

Failures should be verified deliberately rather than waiting for accidental occurrence.

Candidate injected conditions include:

- RFID power unavailable / boot failure / unresponsive reader;
- CAN device disappears;
- non-discoverable keypad remains silent;
- Display V1 reconnect/reset;
- Display V2 network disconnect/reconnect;
- local network loss;
- internet loss with local LAN still available;
- RabbitMQ/backoffice loss;
- delayed or rejected reference-data update;
- file backup write failure;
- corrupt/missing restore data;
- application restart after traceable events;
- queue pressure/overload;
- GUI/client disconnect and stale status.

Stubs/test-control interfaces should inject faults through normal adapter boundaries rather than mutating domain state directly.

## CI execution classes

A likely CI split is:

```text
PR fast checks
  compile
  unit tests
  architecture/dependency checks
  fast component/interface smoke tests

PR/merge integration
  process-level API/WebSocket tests
  reference-project consumer tests
  selected fault scenarios

scheduled/on-demand
  long-running integration
  performance/resource regression where a suitable target exists

hardware pipeline
  Pi Zero / RFID / CAN / display hardware-in-loop
```

Exact workflow names and triggers belong in implementation repositories and the SDE.

## Public/private verification model

The public framework must be verifiable without proprietary source.

The public reference/test project should prove that published Maven artifacts and public contracts work outside the framework reactor.

Private repositories should reuse the same contract tests/scenario concepts where possible. A private implementation is successful when it can replace a public stub/default adapter through the supported API/SPI without requiring changes to public framework source.

## Generated evidence

Useful evidence may include:

- JUnit/Maven test reports;
- GitHub Actions run links;
- integration logs;
- resource-measurement summaries;
- generated architecture/documentation review output;
- hardware-test notes or captured device logs;
- protocol/interface test reports where appropriate.

The active implementation PR should contain or link the detailed evidence for its scope. Long-term plans should only retain durable conclusions/baselines.

## Verification status model

Documents and requirements should eventually support states such as:

```text
not verified
verification planned
verification implemented
verified
failed / evidence not sufficient
verification impacted by change
```

The exact traceability tooling is still open; initially this can remain Markdown + tests + PR evidence.

## Open verification topics

- requirement and verification-case identifier conventions;
- when numeric Pi Zero budgets become acceptance criteria rather than measured baselines;
- standard test framework/version compatible with Java 8;
- architecture-test tooling compatible with the Java baseline;
- hardware-runner setup and how hardware tests are triggered;
- coverage expectations and whether line coverage is useful for this project;
- long-running/soak-test duration and acceptance criteria;
- timestamp precision/clock-synchronisation verification method;
- RFID filtering verification data sets;
- how proprietary interface/protocol verification evidence is referenced without exposing private details in public repositories;
- release-level regression criteria.

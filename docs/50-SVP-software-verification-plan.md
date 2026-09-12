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
- multiple registration assets/sources remain isolated and correctly routed;
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
- source-routing and sequence/traceability tests;
- restore/replay tests for local state.

Examples:

- first RFID observation does not automatically create a registration;
- `OPEN` / `CLOSED` transition rules;
- ready-team add/remove projection;
- registration-source sequence allocation;
- registration asset/source routing does not use hard-coded production IDs;
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
- RabbitMQ adapter against a controlled broker fixture;
- proprietary RFID implementation in its private repository.

### V3 — Interface verification

Purpose: verify system-level interface contracts/IDDs between software items or external systems.

Expected examples:

- local console returns the same application version/status model as other clients;
- remote shell returns the same version/status semantics;
- Desktop GUI (SI-02) connects to Timing Application (SI-01) across a real network boundary;
- Web Operator Application (SI-03) loads over HTTP and communicates through HTTP/WebSocket;
- RabbitMQ/backoffice message exchange with correct registration-source identity/routing;
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
- RabbitMQ test broker with multiple configured source consumers/publishers;
- backoffice disconnect/reconnect with local outbox;
- restart/restore followed by synchronisation;
- multiple `TimingSystemInstance` objects, assets and source streams in one runtime;
- full-field simulation using synthetic identities against the same normal backoffice path.

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
- timing-system queue backlog/latency under representative input;
- registration-source count and source-scaling overhead;
- RabbitMQ connection/channel/consumer count and their resource cost;
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
configured TimingSystemInstance / asset / source counts
RabbitMQ connection/channel/consumer counts when enabled
version/status request latency
notes / anomalies
```

A later Java 11 evaluation must compare against the same or equivalent workload and hardware rather than only desktop benchmarks.

## RabbitMQ container integration environment

RabbitMQ integration verification should use a disposable real broker, preferably through Docker Compose in the implementation/reference repository.

The broker fixture must use only synthetic/public test topology and credentials.

A normal test sequence should be automatable as:

```text
start RabbitMQ container
      |
      v
wait for broker health/readiness
      |
      v
start SI-01/reference application with synthetic multi-source configuration
      |
      v
exercise inbound + outbound messaging
      |
      v
stop/restart RabbitMQ
      |
      v
verify connection recovery + source consumer restoration + outbox resume
      |
      v
collect evidence and remove test environment
```

The same basic Compose definition should be usable locally and in GitHub Actions where practical.

RabbitMQ scenarios should include at least:

- one registration source using one inbound queue and one outbound routing endpoint;
- two or more registration sources sharing one broker connection;
- independent inbound consumers for each source;
- source-01 messages never appearing as source-02 data;
- source-specific outbound routing;
- broker outage while local registrations continue;
- pending outbound data retained while broker is unavailable;
- reconnect restoring every configured source consumer;
- broker restart without reuse of committed registration sequence numbers;
- malformed/unknown input;
- unavailable/misconfigured source queue;
- authentication/configuration failure;
- full-field simulation with many synthetic source streams;
- comparison of one-connection versus optional split consumer/publisher connection strategies when resource/recovery evidence is needed.

Actual production queue names, source IDs, schemas and credentials are not public test data.

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
- RabbitMQ/backoffice connection loss;
- individual registration-source consumer failure while broker remains connected;
- RabbitMQ broker restart;
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
  RabbitMQ Docker/Compose integration tests
  selected fault/reconnect scenarios

scheduled/on-demand
  long-running integration
  high-source-count/full-field simulations
  performance/resource regression where a suitable target exists

hardware pipeline
  Pi Zero / RFID / CAN / display hardware-in-loop
```

Exact workflow names and triggers belong in implementation repositories and the SDE.

## Public/private verification model

The public framework must be verifiable without proprietary source or deployment identities.

The public reference/test project should prove that published Maven artifacts and public contracts work outside the framework reactor, including the RabbitMQ adapter with synthetic source/broker topology.

Private repositories should reuse the same contract tests/scenario concepts where possible. A private implementation is successful when it can replace a public stub/default adapter through the supported API/SPI without requiring changes to public framework source.

Production asset names, source IDs, broker mappings, proprietary message schemas and credentials must not be copied into public verification fixtures.

## Generated evidence

Useful evidence may include:

- JUnit/Maven test reports;
- GitHub Actions run links;
- integration logs;
- Docker/Compose service logs for integration failures;
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
- Docker/Compose version/image-pinning conventions for integration services;
- hardware-runner setup and how hardware tests are triggered;
- coverage expectations and whether line coverage is useful for this project;
- long-running/soak-test duration and acceptance criteria;
- timestamp precision/clock-synchronisation verification method;
- RFID filtering verification data sets;
- RabbitMQ production acknowledgement/reconciliation verification approach;
- how proprietary interface/protocol verification evidence is referenced without exposing private details in public repositories;
- release-level regression criteria.

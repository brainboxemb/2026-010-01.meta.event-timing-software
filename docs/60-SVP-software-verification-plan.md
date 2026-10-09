# Software Verification Plan (SVP)

Status: working draft / non-authoritative


## Purpose

This Software Verification Plan defines the initial verification strategy for the software system. It is introduced early so public interfaces, testability, fault handling and target execution can be checked as the software grows.

The SVP applies across software items unless a software-item-specific verification document later adds more detail.

## Terms and abbreviations

- **SVP** — Software Verification Plan
- **VTS** — Verification Test Specification
- **VC** — Verification Case
- **ST** — System Test profile family


## Relationship to other documents

The intended traceability chain follows the product-authority direction established in
the SDP:

```text
system use case / external interface obligation
             |
             v
            SSSD
             |
      +------+------+
      |             |
      v             v
system ISD        SSD requirement
      |             |
      +------> SSD architecture
                    |
                    v
               focused SDD
                    |
                    v
              implementation
                    |
                    v
          verification case + evidence
```

An ISD remains software-system-owned. A software-item requirement references the
applicable ISD obligation rather than duplicating its interface definition. An optional
IDD may describe concrete interface design but does not replace the ISD requirement source. The SVP and
verification cases are downstream coverage/evidence artifacts; they are deliberately not
normative inputs to the requirements they verify.

Verification identifiers and exact requirement-reference syntax are still to be refined.


## Verification objectives

Verification should provide evidence that:

- requirements and interface contracts are implemented correctly;
- software-item boundaries remain usable independently;
- domain behaviour is deterministic and unit-testable;
- application behaviour can be tested automatically through its public interface;
- real and stub/proprietary adapters conform to the same public contracts;
- backoffice semantics remain correct across stub, socket and RabbitMQ transports;
- faults and reconnect/recovery paths behave deliberately;
- local operation remains available where required during backoffice/network outages;
- multiple registration assets/sources remain isolated and correctly routed;
- SI-01 runs correctly on the selected target platform after that platform is chosen;
- public core/reference implementation code can be consumed by external reference and private integration projects;
- generated documentation and build artifacts are reproducible and reviewable.


## Verification levels

The `V*` levels describe **what scope is being verified**. Separate `ST-*` profiles below describe concrete automated system-test compositions.

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
- simple socket backoffice adapter and framing;
- CAN scanner with simulated CAN traffic;
- public stub devices;
- RabbitMQ adapter against a controlled broker fixture;
- proprietary RFID implementation in its private repository.

### V3 — Interface verification

Purpose: verify system-level interface contracts/IDDs between software items or external systems.

Expected examples:

- local console returns the same application version/status model as other clients;
- remote shell returns the same version/status semantics;
- the Engineering Desktop Client consumes IF-03 across a real network boundary;
- an optional simple web test client may consume IF-03 if it becomes useful;
- backoffice semantic exchange through both socket-test and RabbitMQ adapters;
- Display V2 mDNS discovery and subsequent data/session protocol;
- CAN keypad/display interactions.

These tests should verify externally observable behaviour rather than internal class structure.

### V4 — Integration/system verification

Purpose: verify multiple real components together with realistic process/network boundaries.

Candidate scenarios:

- SI-01 + test driver through the public application-control interface;
- SI-01 + simple socket backoffice simulator;
- SI-01 + RabbitMQ test broker with multiple configured source consumers/publishers;
- SI-01 + Engineering Desktop Client over localhost;
- SI-01 on the selected target + an external IF-03 client;
- stub RFID + real domain pipeline + local persistence;
- CAN scanner + keypad + Display V1 stub/real hardware;
- backoffice disconnect/reconnect with local outbox;
- restart/restore followed by synchronisation;
- multiple `TimingNode` objects, assets and source streams in one runtime;
- full-field simulation using synthetic identities against the same normal backoffice path.

### V5 — Hardware-in-the-loop verification

Purpose: verify behaviour that cannot be adequately represented by normal automated test doubles.

Likely scope:

- selected target runtime/power/restart behaviour;
- RFID reader power/boot/reinitialisation;
- real RFID read/filter behaviour;
- real CAN bus/device discovery;
- Display V1 physical behaviour;
- Display V2 network discovery/session behaviour;
- power-cycle/restart recovery where practical.

Hardware tests should be separated from the fast normal pull-request path when they are slow, scarce, or environment-specific.

### V6 — Target/runtime observations

Purpose: record enough real target behaviour to detect an actual problem rather than
assuming one in advance.

For the first selected-target proof, simple observations are sufficient:

- startup time;
- memory use;
- idle and representative CPU use;
- thread count;
- basic API responsiveness.

Add more detailed measurements only when a feature or observed problem justifies them.
There are no numeric target resource budgets at this stage.

## Development-host runtime characterization

Development-host runtime characterization is engineering verification, not a
product performance requirement. A SIP step may invoke this method when it needs
measurement evidence before selecting a runtime optimization.

The characterized composition is deliberately small:

```text
deterministic SimulatedAntenna input
        |
        v
tag interpretation / filtering
        |
        v
one TimingNode bounded serial lane
        |
        +--> TimingData persistence / LogBook
        |
        +--> post-commit presentation events
```

Characterization cases use deterministic synthetic tag/reference fixtures and
growing committed history. The workload definition and random/sequence seed,
where one is used, are retained with the evidence so a later run can reproduce
the same input. The engineering harness/environment is defined by
`50-SDE-04-runtime-characterization.md`.

Retain enough evidence to compare runs without high-volume event logging:

- source/build revision, JVM, OS and relevant runtime configuration;
- workload shape, duration/count and preloaded committed-record volume;
- observation, filter/resolve, queue-admission and commit counts;
- queue depth/high-water and full/not-running admission counts;
- queue-wait, serial-processing, persistence/commit and useful end-to-end
  duration summaries;
- bounded history/query cost for the exercised query shape;
- GC count/time deltas and heap observations;
- project-owned thread CPU/state observations where the JVM supports them.

A baseline keeps ordinary JVM scheduling and the reviewed bounded TimingNode
execution design unless the characterization question is specifically about
one of those choices. The first characterization establishes ordinary/bursty
behaviour; a later fairness/backpressure case asks whether sustained ingress or
slow downstream delivery prevents required work from making forward progress. A stalled/slow IF-03 event client is included
where needed to prove that post-commit delivery does not block the TimingNode
lane indefinitely or create unbounded application-owned delivery state.

Do not preselect a fix. Batching, admission/fairness guards, thread-priority
changes, object pooling, copied read snapshots, caches/indexes or asynchronous
persistence are introduced only when the retained evidence identifies the
specific problem they solve. Re-run the affected scenario after a change and
compare it with the same baseline.

A single-TimingNode characterization does not establish multi-TimingNode scheduler
behaviour. When later integration introduces multiple active nodes, that composition
requires its own evidence. Important scheduling/CPU/GC/latency cases are repeated on
the selected target because development-host results do not define target behaviour.

No numeric pass/fail performance threshold is invented by this plan. A later
requirement may establish one if product evidence needs it. Until then the
acceptance question is repeatability, bounded resource behaviour, forward
progress and an evidence-backed implementation choice.

## Automated system-test profiles

The `ST-*` profiles provide a progressive set of reusable system-test compositions. A test case can exist at one or more profiles depending on the behaviour being verified.

### ST-1 — Application behaviour profile


Purpose: fast automated verification of **application behaviour through the public application interface**.

Composition:

```text
System-test driver
      |
      | public application control/status interface
      v
SI-01 real application process
      |
      +-- stub RFID/CAN/display adapters
      +-- in-memory/stub backoffice adapter
      +-- test configuration
```

Characteristics:

- real SI-01 process and composition;
- no direct mutation of domain state from the test;
- test actions enter through the same public application interface intended for GUI/automation clients;
- external devices/backoffice can be deterministic stubs;
- no Docker required;
- suitable for frequent PR execution.

Typical cases:

- start application and query version/status;
- open/close a `TimingNode` through the public interface;
- inject stub RFID observations and verify registrations/status;
- add/remove ready-team values and verify display model/state;
- start procedure commands;
- verify several configured TimingNodes/sources behave independently;
- verify backup/restore and application restart at the observable interface level.

This is intended to become the **primary fast system-level regression layer**.

The Development Client may consume the same public interface for human inspection, but
it does not replace automated ST-1 evidence. Automated tests continue to own formal
pass/fail verification unless a VTS case explicitly requires manual client interaction.

#### ST-1 test specifications

Concrete ST-1 cases are specified in
`61-01-VTS-timing-application-verification-test-specification.md`.

The VTS owns each `VC-ST1-...` case purpose, setup, deterministic procedure and
expected result. The executable `system-test` module implements those cases against
the packaged SI-01 process through public interfaces only.

This SVP deliberately does not carry the current case procedure or current PASS/FAIL
state. Run identity, PASS/FAIL, process output, logs and other retained artifacts belong
to generated verification evidence.
### ST-2 — Socket loop/network profile

Purpose: add a real process/network communication boundary for the backoffice while remaining lightweight.

Composition:

```text
Application test driver ----> SI-01 public application interface
                               |
                               +-- SocketBackofficeAdapter
                                         ^
                                         |
                                    simple TCP socket
                                         |
                               Backoffice test simulator
```

Characteristics:

- no RabbitMQ/Docker required;
- same source-aware semantic backoffice messages as other transports;
- simple public/synthetic test framing;
- one socket can multiplex several registration sources;
- suitable for reconnect/session/source-routing tests;
- still fast enough for normal automated integration testing.

Typical cases:

- several registration sources over one socket session;
- source identity preserved in both directions;
- socket loss reflected in status while local operation continues;
- reconnect and resume;
- outbound registrations observed by the simulator;
- inbound reference/control data delivered to the correct source/application path;
- full-field multi-TimingNode simulation without broker infrastructure.

### ST-3 — RabbitMQ integration profile

Purpose: verify the production-shaped broker transport against a real RabbitMQ service.

Composition:

```text
Application test driver ----> SI-01 public application interface
                               |
                               +-- RabbitMqBackofficeAdapter
                                         |
                                         v
                                  RabbitMQ test broker
                                  (Docker Compose)
                                         ^
                                         |
                               broker-side test driver
```

Characteristics:

- disposable real RabbitMQ broker;
- synthetic/public queue/exchange/source topology;
- verifies connection/channel/consumer/publisher behaviour;
- verifies multiple source consumers on shared connection(s);
- exercises broker restart and outbox recovery;
- slower than ST-1/ST-2 and may run as integration CI.

Typical cases:

- one registration source inbound/outbound happy path;
- two or more sources sharing one broker connection;
- independent inbound consumers per source;
- source-specific outbound routing;
- broker outage while local registrations continue;
- pending outbound data retained during outage;
- reconnect restores all source consumers;
- broker restart does not alter committed registration sequence identity;
- malformed/unavailable/misconfigured broker resource handling.

### ST-4 — Target/full-system profile

Purpose: run representative system tests on target hardware and/or with real external hardware/services.

Possible compositions include:

- SI-01 on the selected target with the ST-1 application driver;
- selected target + socket simulator to isolate target runtime/network behaviour;
- selected target + RabbitMQ broker on another host;
- selected target + real RFID/CAN/display hardware;
- Engineering Desktop Client against the real target application.

ST-4 is generally slower/on-demand and can reuse test scenarios first proven at ST-1/ST-3.
It starts only after the SIP target-platform decision and bring-up work have established a
reproducible target image/provisioning and runtime baseline.

## Selected-target baseline evidence

Step 9 owns the first real-target baseline after Step 8 has selected the platform. Candidate
Raspberry Pi models remain valid study inputs, but this SVP does not make Pi Zero/Zero W a
precondition for earlier development-host verification. The first representative executable
should be run on the selected real hardware using the documented OS/Java/deployment
baseline so target behaviour is known rather than guessed.

Useful first baseline:

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
configured TimingNode / asset / source counts
socket/RabbitMQ connection counts when enabled
RabbitMQ channel/consumer counts when enabled
version/status request latency
notes / anomalies
```

Any later Java-runtime comparison must use the same or equivalent workload and selected
hardware rather than only desktop benchmarks. The evidence should also identify how the
target was provisioned (base image/image recipe and provisioning revision) so runtime
comparisons are not confounded by an unknown machine setup.

## RabbitMQ container integration environment

ST-3 uses a disposable real RabbitMQ broker, preferably through Docker Compose in the implementation/reference repository.

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
- simple socket backoffice disconnect/reconnect;
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
  ST-1 application behaviour tests
  selected fast component/interface tests

PR integration
  ST-2 socket loop/network tests
  reference-project consumer tests
  selected fault/reconnect scenarios

merge / selected PR / scheduled integration
  ST-3 RabbitMQ Docker/Compose integration tests
  high-source-count/full-field simulations

scheduled/on-demand
  long-running integration
  performance/resource regression where a suitable target exists

hardware pipeline
  ST-4 selected target / RFID / CAN / display hardware-in-loop
```

The exact boundary between normal PR and merge-time ST-3 execution can be adjusted once runtime is known. Exact workflow names and triggers belong in implementation repositories and the SDE.

## Public/private verification model

The public application core must be verifiable without proprietary source or deployment identities.

Private implementations should use the same public contracts where applicable; detailed private-repository verification is added when such an implementation actually exists.

The public baseline should verify the Java-8 provider mechanism without requiring
private source. Verification should cover at least:

- built-in-provider discovery and selection;
- `SimulatedAntenna` availability with no external extension JARs;
- loading a synthetic external test provider through the same startup path intended for production extensions;
- typed conformance for TimingData, UpstreamProtocol, Antenna, CAN-protocol and display-protocol provider contracts as those contracts are implemented;
- deterministic failure for duplicate provider IDs, unknown configured provider IDs and incompatible provider configuration;
- proof that domain/application behaviour receives normal typed contracts and does not depend on extension-loader classes.

Production asset names, source IDs, broker mappings, proprietary message schemas, private provider names and credentials must not be copied into public verification fixtures.

## Generated evidence

Useful evidence may include:

- JUnit/Maven test reports;
- GitHub Actions run links;
- ST-1/ST-2/ST-3 scenario reports;
- integration logs;
- Docker/Compose service logs for integration failures;
- target/runtime measurement notes where useful;
- generated architecture/documentation review output;
- hardware-test notes or captured device logs;
- protocol/interface test reports where appropriate.

The active implementation PR should contain or link the detailed evidence for its scope. Long-term plans should only retain durable conclusions/baselines.

## Traceability status vocabulary

This is a vocabulary for future traceability tooling, not a current test-run status table.
Current execution state belongs to retained verification evidence. Requirements/cases may
eventually be summarised with states such as:

```text
not verified
verification planned
verification implemented
verified
failed / evidence not sufficient
verification impacted by change
```

The exact traceability tooling is still open. The VTS owns stable case definitions; executable tests and retained CI/PR evidence own actual execution results.

## Open verification topics

- requirement and verification-case identifier conventions;
- scenario identifier convention across ST-1/ST-4 profiles;
- whether any measured Pi behaviour warrants a numeric acceptance limit;
- standard test framework/version compatible with Java 8;
- architecture-test tooling compatible with the Java baseline;
- public test-driver API beyond the first `VC-ST1-001` HTTP/WebSocket/remote-terminal slice;
- exact simple socket framing for ST-2;
- Docker/Compose version/image-pinning conventions for ST-3;
- hardware-runner setup and how ST-4 is triggered;
- coverage expectations and whether line coverage is useful for this project;
- long-running/soak-test duration and acceptance criteria;
- timestamp precision/clock-synchronisation verification method;
- RFID filtering verification data sets;
- RabbitMQ production acknowledgement/reconciliation verification approach;
- how proprietary interface/protocol verification evidence is referenced without exposing private details in public repositories;
- release-level regression criteria.

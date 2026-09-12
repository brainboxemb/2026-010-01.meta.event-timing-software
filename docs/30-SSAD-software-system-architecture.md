# Software System Architecture Document (SSAD)

Status: working draft / non-authoritative

This document defines the current software-system architecture working model for the event timing/time-registration software. It establishes software-item boundaries, system-owned interfaces, cross-cutting architectural rules, and the relationship to software-item SAD/SDD documents.

The SSAD is deliberately more stable and less implementation-specific than the software-item detailed designs.

## Document role

The intended document hierarchy is:

```text
system requirements
        |
        +--> system-level IDDs
        |
        v
software-item SRDs
        |
        v
30-SSAD software-system architecture
        |
        +--> 31-01 SAD/SDDs — software item 01
        +--> 31-02 SAD/SDDs — software item 02
        +--> 31-03 SAD/SDDs — software item 03
        |
        v
implementation + verification
```

The exact formal requirements/IDD set has not yet been promoted. Current candidate requirements remain working material until that step occurs.

## Architecture decisions

A decision can be `proposed`, `accepted`, `superseded`, or `rejected`.

| ID | Status | Decision | Rationale / notes |
| --- | --- | --- | --- |
| ADR-001 | accepted | Use **Maven** as the Java build and dependency-management tool. | Maven is the preferred baseline because there is more existing project experience with it. |
| ADR-002 | accepted | Use **Java SE 8** as the initial language/API/runtime baseline for software item 01. | The original Raspberry Pi Zero / Zero W (ARMv6) is mandatory and the legacy application already uses Java 8. Start conservatively and gather evidence before increasing the baseline. |
| ADR-003 | proposed | Keep application code vendor-neutral at the Java SE level and pin an explicit ARMv6-capable reference runtime for Zero 1 deployment. | Deployment must be reproducible, but application code should not depend on vendor-specific JDK APIs. |
| ADR-004 | proposed | Evaluate **Java 11** as a later baseline upgrade after sufficient Zero 1 evidence exists. | Migration is desirable only when compatibility, footprint, performance, dependency support, maintenance, and deployment are proven on the mandatory target. |
| ADR-005 | proposed | Use **serialized application/domain execution** so mutable timing-system state has one logical writer while adapters own external I/O concurrency. | This avoids pervasive locking, makes ordering explicit, and keeps domain code straightforward to unit test. |
| ADR-006 | proposed | Generate architecture diagrams from Python into both **SVG** and **draw.io** and publish generated documentation on PR/prod documentation branches. | SVG keeps GitHub documentation directly readable; draw.io remains editable. One source model reduces drift. |
| ADR-007 | proposed | Treat status as a first-class shared model, separate from logs. | Console, GUI, browser and diagnostics should observe one coherent current-state representation. |
| ADR-008 | proposed | Treat software-item boundaries and system interfaces as explicit versioned contracts; proprietary implementations plug in through public contracts/composition. | Public framework/test code must not depend on private implementation source. |

## Software-item register

The second-level number used in SRD/SAD/SDD filenames identifies the software item.

| Software item | Name | Current status | Primary responsibility | Expected deployment |
| --- | --- | --- | --- | --- |
| **SI-01** | Headless Timing Application | working architecture | Authoritative local timing/registration runtime, device integration, local state, status, synchronisation and public control interfaces | Raspberry Pi Zero/Zero W, Linux, Windows development/runtime |
| **SI-02** | Desktop GUI Application | working architecture | Desktop operator client for status/control through the system interface | Operator workstation/laptop |
| **SI-03** | Web Operator Application | working architecture | React/browser/iPad operator client served by SI-01 and communicating over HTTP/WebSocket | Browser/iPad on local network |

Supporting framework modules, adapters, testkit/reference projects and private implementation repositories are important development/deployment components but are not automatically separate product software items. Their status should remain explicit rather than overloading the software-item numbering.

### SI-01 — Headless Timing Application

System authority for local operation. It may host `1..X` independently addressed logical `TimingSystem` instances and remains capable of local operation when GUI/browser/backoffice connectivity is unavailable where required data is available locally.

Architecture: `31-01-SAD-timing-application-architecture.md`.

### SI-02 — Desktop GUI Application

Separate client software item. It must communicate through a system-defined network interface and therefore must be able to control/observe SI-01 when SI-01 runs on another machine, including a Raspberry Pi.

Architecture: `31-02-SAD-gui-application-architecture.md`.

### SI-03 — Web Operator Application

Separate browser software item. Its compiled React assets may be hosted by SI-01, but its executable code runs in the browser and uses the same system authority rather than owning timing-domain state.

Architecture: `31-03-SAD-web-operator-application-architecture.md`.

## System context

```text
                    Operator
                  /          \
                 v            v
        SI-02 Desktop GUI   SI-03 Web/iPad
                 \            /
                  \          /
                   v        v
                 SI-01 Timing Application
                  /   |    |       \
                 /    |    |        \
              RFID   CAN  local     Backoffice
                    devices state     / RabbitMQ
                    /  \
                 keypad Display V1

SI-01 also advertises/serves data to smart Display V2 over the local network.
```

The desktop GUI and browser clients are not required for SI-01 to continue local registration/device operation.

## System interface catalogue

This catalogue identifies system-owned boundaries before individual IDDs are created. IDs are working identifiers but should remain stable once IDDs are promoted.

| Interface | Parties | Current transport/direction | Purpose | Planned documentation |
| --- | --- | --- | --- | --- |
| **IF-01 Local Operator Console** | Operator ↔ SI-01 | local process console/shell | Version/status and operator commands | possible system HMI/command IDD section |
| **IF-02 Remote Shell** | Operator/service tool ↔ SI-01 | remote terminal/shell, technology TBD | Remote version/status/commands using shared command semantics | IDD/command interface section |
| **IF-03 Application Control & Status** | SI-02/SI-03 ↔ SI-01 | HTTP/JSON + WebSocket direction | Network command/query/status/event boundary | candidate `40-01-IDD-application-control-status.md` |
| **IF-04 Desktop Operator HMI** | Operator ↔ SI-02 | desktop GUI | Required screens, information, controls and operator feedback | candidate `40-02-IDD-desktop-operator-hmi.md` |
| **IF-05 Web Operator HMI** | Operator ↔ SI-03 | browser/iPad UI | Required screens, information, controls and operator feedback | candidate `40-03-IDD-web-operator-hmi.md` |
| **IF-06 Backoffice Integration** | SI-01 ↔ Backoffice | RabbitMQ intended | Reference-data sync, registration delivery, reconciliation/status | candidate system IDD; proprietary details may require private material |
| **IF-07 RFID Integration** | SI-01 ↔ RFID subsystem | public port + production hardware/protocol adapter | Power/lifecycle, raw reads, health/status | public semantic contract; production protocol remains private where required |
| **IF-08 CAN Device Integration** | SI-01 ↔ CAN bus/devices | CAN | Discovery, Display V1, keypad input | system/device IDD candidate |
| **IF-09 Smart Display V2** | SI-01 ↔ Display V2 | LAN/Wi-Fi; SI-01 advertises mDNS service; display connects | Synchronised display/domain data | system IDD candidate |
| **IF-10 Test Control** | test/reference tooling ↔ stubs | development-only interface, technology TBD | Inject device/network/fault behaviour through normal adapter paths | SDE/SVP/test design, not production operator interface |

System-level IDDs own interface semantics. Software-item SRDs reference applicable IDD obligations rather than duplicating them.

## Visual overview

Generated diagrams are published on `dev/pr-<N>/docs` for active PR review and `prod/docs` after merge.

![Software system overview](../../../raw/prod/docs/architecture/system-overview.svg)

![Threading and unit-testability model](../../../raw/prod/docs/architecture/threading-model.svg)

The source models live in `tools/` and generate both GitHub-readable SVG and editable draw.io output.

## Shared command/query/event semantics

Local console, remote shell, API, desktop GUI and browser should not each implement business behaviour independently.

Transport adapters translate to/from shared application commands, queries and events such as:

```text
version query
status query
open timing system
close timing system
start participant/team
manual registration
penalty registration
penalty revocation
RFID power/reinitialise
ready-team add/remove
```

The exact type/API names are software-item design details. The system-level principle is that presentation/transport differences do not create independent domain implementations.

## TimingSystem boundary

Inside SI-01 a `TimingSystem` is the primary logical state/ordering boundary. One running SI-01 process may host `1..X` timing systems.

A timing-system lifecycle state such as `OPEN`/`CLOSED` must remain distinct from subsystem health. For example, a system may be operationally `OPEN` while RFID is starting or failed; status then shows degraded capability rather than silently changing lifecycle state.

Detailed design: `31-01-SDD-01-timing-system-design.md`.

## Status architecture

Status is a system concept, not a logging side effect.

One coherent model should cover at least:

### Application/runtime status

- software version;
- startup time/uptime;
- configured/running timing-system count;
- overall health/degraded state;
- configuration/restore state.

### Timing-system status

- identifier;
- lifecycle (`OPEN` / `CLOSED` and later formally defined states);
- current operational/degraded health;
- start-procedure state;
- last meaningful activity/state transition.

### Subsystem status

- RFID power/startup/protocol/heartbeat;
- CAN bus/scanner/discovered devices;
- keypad activity where observable;
- Display V1 state;
- Display V2 session/synchronisation state;
- local persistence/backup/restore;
- reference-data freshness;
- local-network reachability;
- internet reachability;
- RabbitMQ/backoffice connection;
- public interface endpoints.

Status snapshots should be immutable from consumer perspective and suitable for console, HTTP, WebSocket, desktop GUI, browser UI and diagnostics.

## Threading and concurrency model

The architectural goal is to keep threading out of domain behaviour as much as practical.

External libraries may have their own threads/callbacks for HTTP/WebSocket, remote shell, RFID, CAN, RabbitMQ, timers and network sessions. Those threads must not directly mutate timing-system domain state.

At the adapter/runtime boundary they should:

1. capture externally meaningful timestamps immediately when timing matters;
2. convert the input to an immutable command/event/message;
3. route/enqueue it to the addressed `TimingSystem`;
4. serialize state-changing handling for that timing system.

A logical serialized executor does not imply a dedicated OS thread per timing system. Several logical serial executors may use a small shared backing executor suitable for the Pi Zero.

Blocking/slow network, file or hardware work should not hold the serialized state path indefinitely. Completion/failure can re-enter as messages where it changes state.

## Testability architecture

Testability is an architectural requirement direction, not only a testing task.

Application/domain code should where practical:

- not create uncontrolled threads itself;
- not use `Thread.sleep()` to express domain timing;
- not depend on global/static mutable state;
- receive time through an injected clock abstraction;
- depend on storage/device/network ports rather than concrete libraries;
- use immutable commands/events/value objects where practical;
- keep parsing/protocol details in adapters;
- expose handlers usable synchronously in unit tests.

The public testkit/reference project should support fake clock, direct executor, in-memory repositories and controllable stub devices.

Verification strategy: `50-SVP-software-verification-plan.md`.

## Data ownership and persistence direction

The current initial direction is **typed in-memory authoritative state/repositories with simple persistent backup/restore**, not a conventional database engine as the normal domain API.

Important concepts remain distinct:

1. ingress/event queue — ordering and thread ownership;
2. registration ledger — traceable registration records;
3. ready-team journal/state — traceable keypad/operator prepare/remove actions plus current ready list;
4. reference data — start times, reserve-tag mappings and later required metadata;
5. local backup/restore — restart/power-loss recovery;
6. backoffice outbox/synchronisation — pending external delivery/reconciliation.

Detailed design: `31-01-SDD-02-data-and-display-design.md`.

## Device and network architecture

### RFID

The RFID reader/antenna is not continuously powered. It requires an explicit lifecycle with boot/initialisation and operator-controllable reinitialisation/recovery.

Raw tags are encrypted and must pass decrypt/validation, filtering/accumulation and normal/reserve-tag identity resolution before they become registration candidates.

### CAN

CAN carries both discoverable and non-discoverable devices.

Known directions:

- Display V1 is discoverable and relatively passive; SI-01 actively drives current display state;
- keypad is configured/non-discoverable and can add/remove teams from ready-team state;
- a periodic scanner discovers supported CAN devices.

### Display V2

Display V2 is a smart network client. SI-01 advertises a service via mDNS; the display discovers it and connects. SI-01 supplies current/revisioned data, while the display owns its presentation.

### Connectivity levels

Connectivity must not collapse into one boolean. At minimum distinguish:

```text
local LAN/router
internet reachability
RabbitMQ/backoffice session
```

Loss of the latter two should not automatically prevent local timing/device operation when required local state/reference data is available.

## Failure and recovery model

Fault handling should preserve **local authority, traceability and explicit status**. No component should silently appear healthy merely because the process remains running.

| Failure/condition | Intended architectural response | Local timing impact |
| --- | --- | --- |
| RFID powered off | explicit RFID `OFF` status; operator may power on | RFID registration unavailable; other local functions may continue |
| RFID boot/init failure | degraded/error status; explicit reinitialise/recovery path | local system may remain `OPEN` but degraded |
| RFID heartbeat/protocol loss | mark unresponsive/disconnected; controlled recovery policy | preserve already committed data; no fabricated reads |
| CAN Display V1 disappears/resets | mark display unavailable; current display model remains in SI-01; full refresh on return | timing/registration continues |
| keypad silent | absence of input is not automatically a failure because device is non-discoverable | no effect unless separate health evidence exists |
| Display V2 disconnects | retain authoritative data; full current snapshot on reconnect before normal updates | timing/registration continues |
| local LAN/router loss | remote GUI/web/display sessions unavailable; status distinguishes local link failure | SI-01 local hardware/registration should continue where possible |
| internet loss | expose internet-down while LAN may remain up; retain local operation/data | backoffice sync deferred |
| RabbitMQ loss | queue/reconcile pending information through outbox; explicit broker status | local operation continues where reference data is sufficient |
| backup write failure | explicit persistence/backup fault; keep in-memory state; commitment policy still needs requirement | severity/blocking policy TBD for traceable events |
| corrupt/missing restore data | startup/restore status must expose failure; do not silently create apparently healthy empty state | recovery/operator policy TBD |
| process restart | restore persisted state/reference data/sequence metadata before normal operation | avoid reuse of committed sequence numbers |
| queue overload | explicit bounded/backpressure policy required; never silently discard accepted timing information | policy to be formally defined/tested |
| desktop/browser disconnect | client shows stale/disconnected state; SI-01 continues independently | none to local authority |

This table is architectural direction, not yet final failure requirements. Timing thresholds, retry counts and blocking/commit policies belong in later requirements/IDD/SDD work.

## State-model direction

State machines should be used where lifecycle/recovery behaviour is more understandable as transitions than as scattered booleans.

At minimum model explicitly:

- TimingSystem lifecycle (initially `CLOSED` ↔ `OPEN`, independent from subsystem health);
- RFID device lifecycle (`OFF`, power/boot/init, ready, degraded/error, recovery);
- connection/session lifecycle for remote clients/backoffice/Display V2;
- backup/restore state where failure affects operation;
- start procedure once its detailed behaviour is formalised.

Generated state-model diagrams are part of the architecture output.

## Platform and Java runtime

SI-01 must run on the original Raspberry Pi Zero / Zero W (ARMv6) as a mandatory target.

Initial baseline:

- Maven;
- Java SE 8;
- explicit ARMv6-capable deployment runtime to be pinned/validated;
- vendor-neutral application code at Java-SE/API level.

Java 11 remains an evidence-driven future upgrade candidate, not a prerequisite for implementation.

## Resource-budget strategy

The Pi Zero requirement means resource use must be measured from the first executable rather than treated as late optimisation.

The first executable establishes measured baselines for:

| Resource/behaviour | Initial action |
| --- | --- |
| startup time | measure on real Zero 1 |
| process RSS | measure idle + representative workload |
| heap | record configuration and observed behaviour |
| CPU | measure idle + representative registration/API workload |
| threads | record count and major thread owners |
| timing-system queue | measure backlog/latency under representative bursts |
| API/status responsiveness | measure local/LAN response latency |
| file writes | observe backup frequency/volume and SD-card implications |
| reconnect/recovery | measure representative RFID/network/backoffice cases |
| long-running stability | add later soak verification |

Numeric budgets should be promoted only once there is evidence. The architecture nevertheless requires designs to remain compatible with the low-resource target and to avoid gratuitous thread/library/runtime overhead.

## Configuration, credentials and proprietary boundaries

Credentials, encryption keys and environment-specific secrets must not be hard-coded.

Settings need to support application, timing-system, interface, device and backoffice configuration through external mechanisms.

Private/proprietary implementation candidates include production RFID antenna control, encrypted RFID/protocol implementation and other product-specific protocols. Public framework code defines only the required contracts/semantics and must compile/test without private source.

Detailed component design: `31-01-SDD-03-java-component-design.md`.

## Traceability model

The intended engineering chain is:

```text
SYS requirement
   |
   +--> IF/IDD requirement or section (where interface-related)
   |
   v
SI-01 / SI-02 / SI-03 SRD requirement
   |
   v
SAD architectural element
   |
   v
SDD detailed design
   |
   v
source/configuration
   |
   v
verification case / evidence
```

The exact identifier syntax is still open. The important architectural rule is that requirements/interfaces are not duplicated into several documents with divergent wording.

## Document lifecycle

Working documents currently use `working draft / non-authoritative` while the project is still consolidating source/domain knowledge.

A simple future lifecycle is preferred:

```text
working draft
review candidate
accepted / authoritative
superseded
```

`rejected` applies to architecture decisions rather than normal document lifecycle.

Promotion must be explicit. Generated documents are review/publication copies; numbered source documents remain authoritative once a document is promoted.

## Development and verification environment

Development process/tooling: `12-SDE-software-development-environment.md`.

Verification strategy: `50-SVP-software-verification-plan.md`.

Generated PR documentation is published to `dev/pr-<N>/docs`; merged output is published to `prod/docs`.

## First architecture-validation increment

The first executable increment should validate lasting boundaries rather than implement the complete timing domain:

1. Maven-based headless Java 8 application;
2. central version model/service;
3. central status model/service;
4. local console;
5. remote terminal/shell;
6. HTTP/JSON control/status interface;
7. minimal WebSocket status/event path;
8. external settings structure;
9. logging framework;
10. deterministic unit-testable command/query handlers;
11. GitHub Actions build/test;
12. execution and resource baseline on original Raspberry Pi Zero/Zero W;
13. a first external GUI/client connection proving the network boundary.

## Open architecture questions

- exact ARMv6 Java 8 runtime/vendor/version baseline;
- evidence threshold and timing for a possible Java 11 migration;
- exact serialized-executor/backing-pool topology for `1..X` TimingSystems;
- bounded queue/backpressure/overload policy;
- HTTP/JSON/WebSocket technology compatible with Java 8 and Zero 1;
- remote-shell technology;
- desktop GUI technology;
- React/browser build/toolchain baseline;
- authentication/authorisation and secure transport for remote clients;
- formal status/health vocabulary;
- exact persistence commit/durability semantics;
- backup format/recovery policy;
- RFID filter acceptance/timestamp rules;
- CAN protocol/device identities;
- Display V2 session/data protocol;
- backoffice message contracts, retry/buffering/reconciliation;
- configuration/secret-loading hierarchy;
- requirement/IDD/verification identifier conventions;
- resource-budget values after first measurement evidence.

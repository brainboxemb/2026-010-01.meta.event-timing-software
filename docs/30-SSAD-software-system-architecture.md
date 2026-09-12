# Software System Architecture Document (SSAD)

Status: working draft / non-authoritative

This document defines the current software-system architecture working model for the event timing/time-registration software. It establishes software-item boundaries, system-owned interfaces, cross-cutting architectural rules, runtime topology, and the relationship to software-item SAD/SDD documents.

Stable working domain facts and terminology are consolidated in `03-domain-baseline.md` and should not be silently reinterpreted here.

## Document role

The intended document hierarchy is:

```text
system/domain source knowledge
        |
        v
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

Formal system requirements, SRDs and IDDs have not yet been promoted. Candidate requirements in the working designs remain staging material until that step occurs.

## Architecture decisions

A decision can be `proposed`, `accepted`, `superseded`, or `rejected`.

| ID | Status | Decision | Rationale / notes |
| --- | --- | --- | --- |
| ADR-001 | accepted | Use **Maven** as the Java build and dependency-management tool. | Existing project experience and a mature Java ecosystem make Maven the preferred baseline. |
| ADR-002 | accepted | Use **Java SE 8** as the initial language/API/runtime baseline for SI-01. | The original Raspberry Pi Zero / Zero W (ARMv6) is mandatory and the legacy application already uses Java 8. |
| ADR-003 | proposed | Keep application code vendor-neutral at the Java SE level and pin an explicit ARMv6-capable reference runtime for Zero 1 deployment. | Deployment must be reproducible without coupling source to one JDK vendor API. |
| ADR-004 | proposed | Evaluate **Java 11** as a later baseline upgrade after sufficient Zero 1 evidence exists. | Upgrade only when compatibility, footprint, performance, dependencies and deployment are proven. |
| ADR-005 | proposed | Use **serialized application/domain execution per `TimingSystemInstance`** while adapters own external I/O concurrency. | This keeps mutable total-system state single-writer without requiring one OS thread per system/source/device. |
| ADR-006 | proposed | Generate architecture diagrams from Python into SVG + draw.io and publish generated documentation on PR/prod documentation branches. | GitHub remains readable while diagrams remain editable/reproducible. |
| ADR-007 | proposed | Treat status as a first-class shared model, separate from logs. | Console, GUI, browser and diagnostics should observe one coherent current-state representation. |
| ADR-008 | proposed | Treat software-item boundaries and system interfaces as explicit versioned contracts; proprietary implementations plug in through public contracts/composition. | Public framework/test code must not depend on private implementation source. |
| ADR-009 | proposed | Make runtime topology externally configurable: one SI-01 process hosts `1..X` `TimingSystemInstance` objects, each with `1..X` registration sources and each source with `1..X` antenna bindings. | This supports real deployment, variable hardware composition and complete-field backoffice simulation with the same domain model. |

## Software-item register

The second-level number used in SRD/SAD/SDD filenames identifies the software item.

| Software item | Name | Current status | Primary responsibility | Expected deployment |
| --- | --- | --- | --- | --- |
| **SI-01** | Headless Timing Application | working architecture | Authoritative local timing/registration runtime, device integration, local state, status, persistence and synchronisation | Raspberry Pi Zero/Zero W; Linux/Windows development/test/runtime |
| **SI-02** | Desktop GUI Application | working architecture | Desktop operator client for status/control through the system interface | Operator workstation/laptop |
| **SI-03** | Web Operator Application | working architecture | React/browser/iPad operator client served by SI-01 and communicating over HTTP/WebSocket | Browser/iPad on local network |

Supporting framework modules, adapters, testkits/reference projects and private implementation repositories are important engineering components but are not automatically separate product software items.

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

![Software items and principal system interfaces](../../../raw/prod/docs/assets/architecture/software-item-system-overview.svg)

## Runtime/domain topology

The important domain hierarchy is now explicit:

```text
SI-01 TimingApplicationRuntime
  |
  +-- 1..X TimingSystemInstance
          |
          +-- 1..X RegistrationSystem
                  |
                  +-- 1..X RFID antenna/device binding
```

These concepts are intentionally different.

### `TimingSystemInstance`

A `TimingSystemInstance` is one complete logical timing system. It owns/coordinates:

- operational lifecycle such as `OPEN` / `CLOSED`;
- one logical serialized state-change boundary;
- ready-team state;
- start-procedure state;
- display state;
- local/reference-data calculations;
- one or more registration-system source streams;
- instance-level status and operator commands.

### `RegistrationSystem`

A `RegistrationSystem` represents one ordered source stream identified by `RegistrationSystemId`.

It owns source-scoped concepts such as:

- registration source identity;
- monotonic sequence;
- source-specific registration repository/ledger;
- source-specific persistent registration file;
- one or more configured antenna bindings;
- source persistence/registration status.

Registration identity remains conceptually:

```text
(RegistrationSystemId, SequenceNumber)
```

The location is a record/context field, not part of the source-sequence scope.

### Antenna identity

A configured `AntennaId` maps an RFID device/antenna to one registration source and total-system instance.

Preferred working label convention:

```text
RS-<registration-system-name>-ANT<n>
```

Examples include `RS-A-ANT1`, `RS-FINISH-ANT1` and `RS-FINISH-ANT2`.

The readable registration-system name and authoritative registration-source ID remain distinct concepts until domain naming is fully confirmed.

![Configurable runtime topology](../../../raw/prod/docs/assets/architecture/runtime-registration-topology.svg)

Detailed design: `31-01-SDD-04-runtime-topology-and-configuration.md`.

## Full-field simulation

One SI-01 process must be able to host multiple complete `TimingSystemInstance` objects so a development/integration environment can emulate complete field behaviour towards the backoffice.

The simulation uses the same architecture as production:

- same instance/source hierarchy;
- same source sequences;
- same registration persistence model;
- same outbox/backoffice path;
- same command/event queues;
- real adapters replaced with public controllable stubs where needed.

It must not depend on a second fake implementation of business behaviour.

Scale can differ between deployments: a Pi Zero may run a small production topology while a desktop/server test process may host the complete field.

## System interface catalogue

This catalogue identifies system-owned boundaries before individual IDDs are created. IDs are working identifiers but should remain stable once IDDs are promoted.

| Interface | Parties | Current transport/direction | Purpose | Planned documentation |
| --- | --- | --- | --- | --- |
| **IF-01 Local Operator Console** | Operator ↔ SI-01 | local console/shell | Version/status and operator commands | command/HMI IDD section candidate |
| **IF-02 Remote Shell** | Operator/service tool ↔ SI-01 | remote terminal/shell, technology TBD | Remote version/status/commands using shared command semantics | IDD candidate |
| **IF-03 Application Control & Status** | SI-02/SI-03 ↔ SI-01 | HTTP/JSON + WebSocket | Network command/query/status/event boundary | `40-01-IDD-application-control-status.md` candidate |
| **IF-04 Desktop Operator HMI** | Operator ↔ SI-02 | desktop GUI | Required screens, controls and operator feedback | GUI/HMI IDD candidate |
| **IF-05 Web Operator HMI** | Operator ↔ SI-03 | browser/iPad | Required browser screens, controls and feedback | Web HMI IDD candidate |
| **IF-06 Backoffice Integration** | SI-01 ↔ Backoffice | RabbitMQ intended | Reference-data sync, registrations, reconciliation/status | system IDD; proprietary wire details may remain private |
| **IF-07 RFID Integration** | SI-01 ↔ RFID subsystem | public port + production hardware/protocol adapter | Power/lifecycle, raw reads, health/status | public semantic contract; production protocol may remain private |
| **IF-08 CAN Device Integration** | SI-01 ↔ CAN bus/devices | CAN | Discovery, Display V1, keypad input | system/device IDD candidate |
| **IF-09 Smart Display V2** | SI-01 ↔ Display V2 | LAN/Wi-Fi; SI-01 advertises mDNS; display connects | Synchronised display/domain data | system IDD candidate |
| **IF-10 Test Control** | test/reference tooling ↔ stubs | development-only, technology TBD | Inject device/network/fault behaviour through normal adapter paths | SDE/SVP/test design |

System-level IDDs own interface semantics. Software-item SRDs reference applicable IDD obligations instead of duplicating them.

## Shared command/query/event semantics

Local console, remote shell, HTTP API, desktop GUI and browser should not implement business behaviour independently.

Transport adapters translate to/from shared commands, queries and events such as:

```text
version query
status query
open system instance
close system instance
start participant/team
manual registration
penalty registration/revocation
RFID power/reinitialise
ready-team add/remove
```

Commands/queries that address one total system must carry a `TimingSystemInstanceId`. Registration/device events additionally retain source/device context where needed.

## Threading and concurrency model

External libraries may have threads/callbacks for HTTP/WebSocket, remote shell, RFID, CAN, RabbitMQ, timers and network sessions. Those threads must not directly mutate total-system domain state.

At the boundary they should:

1. capture externally meaningful timestamps immediately where timing matters;
2. attach stable device/source context;
3. convert input to immutable messages;
4. route the message to the addressed `TimingSystemInstance`;
5. serialize state-changing handling for that instance.

Conceptually:

```text
many adapter callbacks
        |
        v
route by instance / antenna binding
        |
        v
TimingSystemInstance ingress queue
        |
        v
logical SerialExecutor
        |
        +-- source A sequence/state
        +-- source B sequence/state
        +-- lifecycle/ready-team/display state
```

A logical serial executor does not imply a dedicated OS thread. Multiple instances can share a small backing executor suitable for the Pi Zero.

Blocking file/network/hardware work should not hold the serialized state path indefinitely. Completion/failure can return as immutable messages where it changes state.

## Status architecture

Status is a current-state model, not a logging side effect.

The status hierarchy should follow the runtime topology sufficiently for diagnosis:

```text
ApplicationStatus
  runtime/network/backoffice

  TimingSystemInstanceStatus[instance]
    lifecycle
    location/context
    ready-team/start/display

    RegistrationSystemStatus[source]
      lastSequence
      persistence/file health
      registration statistics

      AntennaStatus[id]
        power
        startup/protocol
        heartbeat
        last activity
```

Status snapshots should be immutable from the consumer perspective and consumable by console, HTTP, WebSocket, GUI, browser and diagnostics.

## Lifecycle and subsystem health

A `TimingSystemInstance` lifecycle such as `OPEN` / `CLOSED` is distinct from subsystem health. For example, the instance can be `OPEN` while one RFID antenna is starting or failed; status then reports degraded capability rather than silently changing lifecycle state.

![TimingSystemInstance lifecycle and health separation](../../../raw/prod/docs/assets/architecture/timing-system-lifecycle.svg)

RFID itself has its own power/startup/recovery state model.

![RFID reader lifecycle and recovery](../../../raw/prod/docs/assets/architecture/rfid-lifecycle.svg)

## Testability architecture

Testability is an architecture property.

Application/domain code should where practical:

- not create uncontrolled threads itself;
- not use `Thread.sleep()` to express domain timing;
- not depend on global/static mutable state;
- receive time through an injected clock abstraction;
- depend on storage/device/network ports rather than concrete libraries;
- use immutable commands/events/value objects where practical;
- keep parsing/protocol details in adapters;
- expose handlers usable synchronously in unit tests.

The public testkit/reference project should support fake clocks, direct executors, in-memory repositories, configurable topology builders and controllable stub devices.

Verification strategy: `50-SVP-software-verification-plan.md`.

## Data ownership and persistence direction

The initial direction is **typed in-memory authoritative state/repositories with simple persistent files for backup/recovery**, not a conventional database engine as the domain API.

Important concepts remain distinct:

1. instance ingress queue — ordering/thread ownership;
2. per-registration-source ledger/file — traceable registration stream;
3. ready-team journal/state — operational prepare/remove history + current projection;
4. reference data — start times, reserve-tag mappings and required metadata;
5. local backup/restore — restart/power-loss recovery;
6. backoffice outbox/synchronisation — pending external delivery/reconciliation.

Each registration source has its own monotonic sequence and registration file. See `03-domain-baseline.md`, `31-01-SDD-02-data-and-display-design.md` and `31-01-SDD-04-runtime-topology-and-configuration.md`.

## RFID processing

The RFID antenna/reader is not continuously powered. It requires explicit startup/initialisation and operator-controllable recovery/reinitialisation.

Raw tags are encrypted and must pass decrypt/validation, observation accumulation/filtering, reserve-tag resolution and identity mapping before becoming registration candidates.

The antenna binding determines which registration source owns an accepted observation.

## CAN, keypad and displays

Known directions:

- Display V1 is CAN-based, discoverable and relatively passive; SI-01 actively pushes current display state;
- the keypad is CAN-based, configured/non-discoverable and can add/remove team numbers from ready-team state;
- a periodic scanner discovers device types that support discovery;
- Display V2 is a smart network client: SI-01 advertises an mDNS service and the display connects/synchronises data.

## Connectivity layers

Connectivity must not collapse into one boolean. At minimum distinguish:

```text
local LAN/router
internet reachability
RabbitMQ/backoffice session
```

Loss of internet/backoffice should not automatically prevent local timing/device operation when required configuration/reference data is available locally.

![Layered connectivity status](../../../raw/prod/docs/assets/architecture/connectivity-layers.svg)

## Failure and recovery model

Fault handling should preserve **local authority, traceability and explicit status**.

| Failure/condition | Intended architecture response |
| --- | --- |
| RFID powered off | explicit antenna/device `OFF` status; operator may power on |
| RFID boot/init failure | source/antenna degraded status; explicit recovery path |
| RFID heartbeat/protocol loss | mark unresponsive/disconnected; preserve committed data; no fabricated reads |
| one antenna fails | other configured antennas/sources continue where possible; status identifies exact antenna/source |
| source persistence file write fails | explicit source persistence fault; commit/blocking policy TBD |
| Display V1 disappears | retain current display model; full refresh on return |
| Display V2 disconnects | retain authority in SI-01; full snapshot on reconnect |
| LAN/internet/RabbitMQ loss | distinguish layer of failure; defer backoffice sync where possible |
| corrupt/missing restore data | expose startup/restore fault; do not silently present empty healthy state |
| process restart | restore source sequence/file state before normal registrations |
| queue overload | explicit bounded/backpressure policy; never silently discard accepted timing information |
| desktop/browser disconnect | client reports stale/disconnected; SI-01 local authority continues |

Thresholds, retries and persistence-commit rules remain requirement/SDD work.

## Platform and Java runtime

SI-01 must run on the original Raspberry Pi Zero / Zero W (ARMv6) as a mandatory target.

Initial baseline:

- Maven;
- Java SE 8;
- explicit ARMv6-capable deployment runtime to be pinned/validated;
- vendor-neutral Java-SE application code.

Java 11 remains an evidence-driven future upgrade candidate.

## Resource-budget strategy

Resource use must be measured from the first executable.

Initial evidence should include:

| Resource/behaviour | Initial action |
| --- | --- |
| startup time | measure on real Zero 1 |
| process RSS/heap | measure idle + representative workload |
| CPU | idle + representative registration/API workload |
| threads | record count and thread owners |
| instance queues | backlog/latency under representative bursts |
| topology scale | compare one production-sized instance versus larger desktop/full-field simulation |
| API/status responsiveness | local/LAN latency |
| file writes | frequency/volume and SD-card implications |
| reconnect/recovery | RFID/network/backoffice scenarios |
| long-running stability | later soak verification |

Numeric limits should be promoted after measurement evidence rather than guessed now.

## Configuration, credentials and proprietary boundaries

Configuration must describe:

```text
application
  system instances
    location/context
    registration systems
      source identity/name
      source registration file
      antenna bindings + adapter settings
```

The exact file syntax remains open.

Credentials, encryption keys and environment-specific secrets must not be hard-coded.

Private/proprietary implementation candidates include production RFID antenna control/decryption/protocol implementations and product-specific protocol details. Public framework code defines required contracts and must compile/test without private source.

Component/package design: `31-01-SDD-03-java-component-design.md`.

Runtime topology/configuration design: `31-01-SDD-04-runtime-topology-and-configuration.md`.

## Traceability model

The intended engineering chain is:

```text
system/domain source
   -> SYS requirement
   -> IDD requirement/section where interface-related
   -> software-item SRD requirement
   -> SAD architectural element
   -> SDD detailed design
   -> source/configuration
   -> verification case/evidence
```

Requirements/interfaces should not be duplicated into several documents with divergent wording.

## Document lifecycle

Working documents currently use `working draft / non-authoritative` while domain knowledge and architecture are still consolidating.

Preferred lifecycle:

```text
working draft
review candidate
accepted / authoritative
superseded
```

Promotion must be explicit. Generated documents are review/publication copies; numbered source documents remain authoritative once promoted.

## First architecture-validation increment

The first executable increment should validate lasting boundaries rather than the complete timing domain:

1. Maven-based headless Java 8 application;
2. external settings loader with at least a minimal instance/source topology;
3. central version/status model;
4. local console;
5. remote shell;
6. HTTP/JSON control/status interface;
7. minimal WebSocket status/event path;
8. logging framework;
9. deterministic/unit-testable command/query handling;
10. GitHub Actions build/test;
11. execution/resource baseline on original Pi Zero/Zero W;
12. first external GUI connection proving the network boundary;
13. early topology test proving multiple `TimingSystemInstance` objects can coexist without state leakage.

## Open architecture questions

- exact ARMv6 Java 8 runtime/vendor/version baseline;
- evidence threshold/timing for Java 11 migration;
- exact backing-executor topology for multiple instances;
- bounded queue/backpressure policy;
- HTTP/JSON/WebSocket technology compatible with Java 8/Zero 1;
- remote-shell and desktop GUI technology;
- React/browser build/toolchain baseline;
- authentication/authorisation and secure transport;
- formal status/health vocabulary;
- exact source persistence commit/durability semantics and file format;
- settings file syntax/include/override/live-reload rules;
- whether one `TimingSystemInstance` always maps to exactly one `LocationId`;
- whether one physical antenna can ever feed multiple registration sources;
- whether names such as `FINISH` are source IDs, human roles/names, or both;
- RFID filter acceptance/timestamp rules;
- CAN protocol/device identities;
- Display V2 session/data protocol;
- backoffice message contracts/retry/buffering/reconciliation;
- requirement/IDD/verification identifier conventions;
- resource-budget values after first measurement evidence.

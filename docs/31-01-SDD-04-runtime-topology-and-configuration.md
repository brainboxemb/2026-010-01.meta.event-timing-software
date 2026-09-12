# Runtime topology and configuration detailed design

Status: working draft / non-authoritative

Software item: **SI-01 — Headless Timing Application**

This SDD defines the working runtime hierarchy for multiple complete system instances, registration-system sources, RFID antennas, source-specific registration persistence, and configurable real/stub compositions.

It refines `03-domain-baseline.md` without fixing the final configuration file syntax.

## Runtime hierarchy

One SI-01 process can host multiple complete logical system instances:

```text
TimingApplicationRuntime
  |
  +-- TimingSystemInstance 1
  |     |
  |     +-- RegistrationSystem A
  |     |     +-- Antenna RS-A-ANT1
  |     |     +-- Antenna RS-A-ANT2
  |     |
  |     +-- RegistrationSystem B
  |           +-- Antenna RS-B-ANT1
  |
  +-- TimingSystemInstance 2
        |
        +-- RegistrationSystem ...
```

The three levels have different responsibilities and identifiers.

### Application runtime

The runtime owns process-wide concerns such as:

- loading and validating settings;
- constructing `1..X` `TimingSystemInstance` objects;
- shared executor/thread-pool infrastructure;
- public interfaces;
- logging and application status;
- backoffice connection infrastructure where appropriate;
- routing commands and device observations to the correct instance.

### `TimingSystemInstance`

A `TimingSystemInstance` represents one complete logical timing system inside the application.

It owns or coordinates instance-level behaviour such as:

- lifecycle (`OPEN` / `CLOSED` and later states);
- one logical serialized state-change boundary;
- `1..X` registration systems;
- ready-team state;
- start procedure;
- display state;
- instance status;
- local calculations/reference-data use;
- instance-level operator commands.

A single instance may register for one source or for multiple `RegistrationSystemId` sources.

### `RegistrationSystem`

A `RegistrationSystem` represents one ordered registration source stream.

It owns source-specific concerns such as:

- `RegistrationSystemId`;
- optional human/configuration name or role;
- monotonic source sequence;
- registration ledger/repository;
- source-specific registration file;
- `1..X` configured RFID antennas;
- source-specific registration/persistence status.

Its stable registration stream identity remains:

```text
(RegistrationSystemId, SequenceNumber)
```

### RFID antenna

An antenna/device endpoint has a configured `AntennaId` and is bound to one registration system in the initial model.

A registration system may own multiple antennas.

The software therefore needs the mapping:

```text
AntennaId
   -> RegistrationSystemId
   -> TimingSystemInstanceId
```

This mapping is settings-driven and must be unambiguous.

## Antenna identifier convention

The current hardware is not necessarily physically labelled. `AntennaId` is therefore first of all a **stable software/configuration identity**. A physical label can later use the same value.

Preferred convention:

```text
RS-<registration-system-name>-ANT<n>
```

Examples:

```text
RS-A-ANT1
RS-B-ANT1
RS-FINISH-ANT1
RS-FINISH-ANT2
```

Use an explicit numeric suffix even when only one antenna is currently present. This avoids renaming an existing antenna when a second antenna is later added.

`RegistrationSystemId` and the human/configuration name used in the antenna label are deliberately separate concepts. For example, a source can retain its protocol/domain ID while having a descriptive name such as `FINISH` for configuration, status and physical labelling.

The exact character/length constraints for identifiers remain to be specified.

## Threading and ordering

The working model is one **logical serialized state-change boundary per `TimingSystemInstance`**, not one OS thread per source or antenna.

```text
RFID callbacks from several antennas
operator/API commands
CAN/keypad events
reference-data events
        |
        v
route to TimingSystemInstance
        |
        v
instance ingress queue
        |
        v
logical SerialExecutor
        |
        +--> RegistrationSystem A sequence/state
        +--> RegistrationSystem B sequence/state
        +--> ready-team/display/lifecycle state
```

This preserves deterministic ordering for one complete system while each registration source still owns its independent sequence and registration file.

Multiple instance-level serial executors can share a small backing executor, especially on Raspberry Pi Zero.

## RFID observation routing

A raw RFID observation should capture antenna identity and observation time before entering domain processing.

Illustrative value object:

```java
final class RawRfidObservation {
    private final AntennaId antennaId;
    private final Instant observedAt;
    private final byte[] rawPayload;
    private final RfidSignalData signalData;
}
```

The configured topology resolves antenna ownership:

```java
final class AntennaBinding {
    private final TimingSystemInstanceId timingSystemInstanceId;
    private final RegistrationSystemId registrationSystemId;
    private final AntennaId antennaId;
}
```

Adapter callback pseudocode:

```java
void onRawRfidObservation(RawRfidObservation observation) {
    AntennaBinding binding = topology.requireBinding(observation.antennaId());

    runtime.submit(
        binding.timingSystemInstanceId(),
        new RfidRawReadObserved(
            binding.registrationSystemId(),
            binding.antennaId(),
            observation));
}
```

The RFID decrypt/filter pipeline therefore receives explicit source and antenna context instead of inferring it later.

## Source-specific registration processing

After tag acceptance/resolution, the registration source remains explicit:

```java
void acceptRegistration(
        RegistrationSystemId sourceId,
        RegistrationCandidate candidate) {

    RegistrationSystem source = registrationSystems.require(sourceId);
    long sequence = source.sequence().next();

    RegistrationRecord record = registrationFactory.create(
        sourceId,
        sequence,
        currentLocationId(),
        candidate);

    source.repository().append(record);
    source.persistence().append(record);
    registrationState.apply(record);
    outbox.enqueue(RegistrationCommitted.from(record));
}
```

The exact durability/acknowledgement policy remains open.

## Per-registration-system files

Each registration system/source has its own persistent registration file.

Conceptually:

```text
data/
  registrations-A.<format>
  registrations-B.<format>
  registrations-C.<format>
```

The file name/format are illustrative.

Each source-specific persistence set must retain enough information to recover at least:

- the source registration records;
- last/next committed source sequence;
- schema/version/integrity metadata required by the final persistence design.

The normal application API remains the in-memory repository; files are persistence/recovery mechanisms.

## Settings-driven topology

The complete topology is externally configurable rather than hard-coded.

The following is **pseudo-configuration only**; YAML is not yet a technology decision:

```yaml
application:
  systemInstances:
    - id: system-01
      locationId: 7

      registrationSystems:
        - id: A
          name: A
          registrationFile: data/registrations-A.dat
          antennas:
            - id: RS-A-ANT1
              adapter: production-rfid-1

        - id: B
          name: FINISH
          registrationFile: data/registrations-B.dat
          antennas:
            - id: RS-FINISH-ANT1
              adapter: production-rfid-2
            - id: RS-FINISH-ANT2
              adapter: production-rfid-3

    - id: system-02
      locationId: 8
      registrationSystems:
        - id: C
          name: C
          registrationFile: data/registrations-C.dat
          antennas:
            - id: RS-C-ANT1
              adapter: stub-rfid-c1
```

The final configuration may use nested objects, references or multiple files. The important architecture is the topology and validation semantics.

## Configuration validation

Candidate startup validation rules:

- `TimingSystemInstanceId` values are unique in one process;
- every configured registration source has a valid `RegistrationSystemId`;
- source IDs are unique in one running application unless a later simulation namespace requirement explicitly permits reuse;
- each registration system has its own persistence file/path;
- `AntennaId` values are unique;
- one antenna belongs to one registration source in the initial model;
- all antenna adapter references can be resolved;
- persistence paths needed for operation are usable;
- configuration failures are explicit in log/status and do not silently produce partial topology.

## Real and stub compositions

Real and simulated devices use the same topology and public contracts.

Production example:

```text
TimingSystemInstance system-01
  RegistrationSystem A
    RS-A-ANT1 -> ProductionRfidAdapter
```

Integration/full-field example:

```text
TimingApplicationRuntime
  system-01
    source A -> StubRfidAdapter
    source B -> StubRfidAdapter

  system-02
    source C -> StubRfidAdapter

  ... additional configured system instances ...
```

Stub inputs must use the normal adapter/event/queue/decrypt-filter/registration/persistence/outbox path where those behaviours are under test.

## Full-field backoffice simulation

Running multiple complete system instances in one SI-01 process is an explicit requirement direction.

A test deployment must be able to configure enough instances and sources to model complete field behaviour towards the backoffice.

This allows one development machine/application to exercise:

- multiple independently addressed total systems;
- multiple registration-source streams;
- independent source sequences;
- per-source persistence;
- realistic registration delivery/reconciliation;
- connection loss/recovery;
- reference-data distribution;
- device/stub behaviour.

The same business model is used for production and simulation; scale and adapter selection differ through configuration.

## Status hierarchy

Status should mirror the topology sufficiently for diagnosis:

```text
ApplicationStatus
  TimingSystemInstanceStatus[system-01]
    lifecycle
    location
    ready-team/display/start-procedure

    RegistrationSystemStatus[A]
      lastSequence
      registrationPersistence
      acceptedRegistrationCount

      AntennaStatus[RS-A-ANT1]
        power
        startup/protocol
        heartbeat
        lastRead

    RegistrationSystemStatus[B]
      ...
      AntennaStatus[RS-FINISH-ANT1]
      AntennaStatus[RS-FINISH-ANT2]

  TimingSystemInstanceStatus[system-02]
    ...
```

## Java component impact

The Java package model should distinguish the total-system aggregate from the registration-source capability.

Suggested direction inside `timing-core`:

```text
...timing.core.timingsystem
    TimingSystemInstance
    TimingSystemInstanceState
    TimingSystemHandler

...timing.core.registrationsystem
    RegistrationSystem
    RegistrationSystemId
    RegistrationSystemRegistry
    RegistrationSequence
    AntennaBinding

...timing.core.registration
    RegistrationService
    RegistrationRecord
    RegistrationLedger
    RegistrationRepository
```

`registrationsystem` owns source identity/topology/sequence; `registration` owns registration record behaviour.

## Candidate requirements

Temporary identifiers only.

- **CAND-TOPO-001** — SI-01 shall support multiple complete logical timing-system instances within one application process.
- **CAND-TOPO-002** — One timing-system instance shall support one or more registration-system sources.
- **CAND-TOPO-003** — One registration system shall support one or more configured RFID antennas.
- **CAND-TOPO-004** — The mapping between timing-system instances, registration systems and antennas shall be externally configurable.
- **CAND-TOPO-005** — Each registration-system source shall maintain its own monotonic sequence and registration persistence file.
- **CAND-TOPO-006** — RFID observations shall retain antenna identity and be routed to the configured registration-system source.
- **CAND-TOPO-007** — The same topology shall support real and stub/simulated adapters through public contracts.
- **CAND-TOPO-008** — One application shall be able to host a full-field simulation suitable for backoffice integration testing.
- **CAND-TOPO-009** — Configured antenna identities shall be stable and unique within one running application.

## Open questions

- Does each `TimingSystemInstance` always have exactly one `LocationId`?
- Can a registration source ever intentionally occur in more than one simultaneously running instance, particularly in simulation?
- Can one physical antenna ever intentionally feed multiple registration systems?
- Is `FINISH` a domain/source identifier, a human-readable role/name, or both?
- What final syntax/file format should settings use?
- Should registration-system settings and application topology live in one file or use includes/separate files?
- Which configuration changes may be applied live versus requiring restart?

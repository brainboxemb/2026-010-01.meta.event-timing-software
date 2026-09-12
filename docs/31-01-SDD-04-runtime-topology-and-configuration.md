# Runtime topology and configuration detailed design

Status: working draft / non-authoritative

Software item: **SI-01 — Headless Timing Application**

This SDD defines the working runtime hierarchy for multiple complete system instances, registration assets, registration-source streams, RFID antennas, source-specific registration persistence, and configurable real/stub compositions.

It refines `03-domain-baseline.md` without fixing the final configuration file syntax.

Concrete production asset names, external registration-system IDs and real deployment mappings are intentionally excluded from this public document. Generic placeholder identities are used throughout.

## Runtime hierarchy

One SI-01 process can host multiple complete logical system instances:

```text
TimingApplicationRuntime
  |
  +-- TimingSystemInstance system-01
  |     |
  |     +-- RegistrationAsset asset-01
  |     |     +-- Antenna RS-<asset-key>-ANT1
  |     |     +-- Antenna RS-<asset-key>-ANT2
  |     |     +-- RegistrationSource source-01
  |     |     +-- RegistrationSource source-02  # may be virtual
  |     |
  |     +-- RegistrationAsset asset-02
  |           +-- Antenna ...
  |           +-- RegistrationSource ...
  |
  +-- TimingSystemInstance system-02
        +-- ...
```

The levels have different responsibilities and identifiers.

### Application runtime

The runtime owns process-wide concerns such as:

- loading and validating settings;
- constructing `1..X` `TimingSystemInstance` objects;
- shared executor/thread-pool infrastructure;
- public interfaces;
- logging and application status;
- backoffice connection infrastructure where appropriate;
- routing commands and device observations to the correct instance/asset.

### `TimingSystemInstance`

A `TimingSystemInstance` represents one complete logical timing system inside the application.

It owns or coordinates instance-level behaviour such as:

- lifecycle (`OPEN` / `CLOSED` and later states);
- one logical serialized state-change boundary;
- `1..X` registration assets;
- ready-team state;
- start procedure;
- display state;
- instance status;
- local calculations/reference-data use;
- instance-level operator commands.

### `RegistrationAsset`

A `RegistrationAsset` represents the real/configured registration box or logical equipment asset.

It owns/configures asset-level concerns such as:

- stable internal/configuration `RegistrationAssetId`;
- optional human-facing label/role used only in the deployment configuration;
- `1..X` RFID antenna bindings;
- `1..X` registration sources;
- device lifecycle/status that belongs to the asset rather than an individual source;
- routing policy that determines which source stream(s) receive an accepted observation.

The public framework must not require the human-readable asset label to equal any external registration-system ID.

### `RegistrationSource`

A `RegistrationSource` represents one ordered registration stream.

It owns source-specific concerns such as:

- external/domain `RegistrationSystemId`;
- monotonic source sequence;
- registration ledger/repository;
- source-specific registration file;
- source-specific registration/persistence/synchronisation status.

A source may be physical/logical or virtual. One registration asset can expose several sources.

Its stable registration stream identity remains:

```text
(RegistrationSystemId, SequenceNumber)
```

## RFID antenna ownership

An antenna/device endpoint has a configured `AntennaId` and belongs to one `RegistrationAsset` in the initial model.

An asset may own multiple antennas and multiple registration sources.

The software therefore needs an unambiguous mapping:

```text
AntennaId
   -> RegistrationAssetId
   -> TimingSystemInstanceId
```

Source routing happens **after** asset/antenna resolution and is not hard-coded as `AntennaId -> RegistrationSystemId`, because an asset can represent more than one source stream.

## Antenna identifier convention

The current hardware is not necessarily physically labelled. `AntennaId` is therefore first of all a stable software/configuration identity. A physical label can later use the same value.

Preferred public naming template:

```text
RS-<asset-key>-ANT<n>
```

Use an explicit numeric suffix even when only one antenna is currently present. This avoids renaming an existing antenna when a second antenna is later added.

The actual `<asset-key>` values used by production installations are deployment/proprietary data and are not included in public examples.

## Threading and ordering

The working model is one **logical serialized state-change boundary per `TimingSystemInstance`**, not one OS thread per asset, source or antenna.

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
        +--> RegistrationAsset state/routing
        |       +--> RegistrationSource 1 sequence/state
        |       +--> RegistrationSource 2 sequence/state
        |
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

The configured topology resolves asset ownership:

```java
final class AntennaBinding {
    private final TimingSystemInstanceId timingSystemInstanceId;
    private final RegistrationAssetId registrationAssetId;
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
            binding.registrationAssetId(),
            binding.antennaId(),
            observation));
}
```

The RFID decrypt/filter pipeline receives explicit asset and antenna context. Only after a tag observation has been accepted does source-routing policy determine the target registration source stream or streams.

## Source-routing policy

Because one registration asset can expose multiple sources, the mapping from an accepted domain observation to a source cannot be assumed to be one-to-one with the antenna.

Conceptually:

```java
interface RegistrationSourceRouter {
    List<RegistrationSystemId> route(
        RegistrationAsset asset,
        AcceptedObservation observation,
        TimingSystemState state);
}
```

The concrete routing rule may be simple configuration or domain-specific logic. Production mappings/policies may be provided by the private integration repository.

Important architectural properties:

- antenna ownership remains stable even when source mappings change;
- every resulting source registration gets that source's own sequence number;
- one accepted observation may only generate registrations according to an explicit routing rule;
- tests can inject a deterministic public/stub routing policy;
- public framework code does not embed real deployment IDs.

## Source-specific registration processing

After source routing, every target source is processed explicitly:

```java
void acceptRegistration(
        RegistrationSystemId sourceId,
        RegistrationCandidate candidate) {

    RegistrationSource source = registrationSources.require(sourceId);
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

## Per-source files

Each registration source has its own persistent registration file.

Public example:

```text
data/
  registrations-source-01.<format>
  registrations-source-02.<format>
  registrations-source-03.<format>
```

Actual production file naming may include private/deployment identities and is outside the public framework specification.

Each source-specific persistence set must retain enough information to recover at least:

- source registration records;
- last/next committed source sequence;
- schema/version/integrity metadata required by the final persistence design.

The normal application API remains the in-memory repository; files are persistence/recovery mechanisms.

## Settings-driven topology

The complete topology is externally configurable rather than hard-coded.

The following is **pseudo-configuration only**; YAML is not yet a technology decision and all identities are placeholders:

```yaml
application:
  systemInstances:
    - id: system-01
      locationId: 7

      registrationAssets:
        - id: asset-01
          antennas:
            - id: RS-asset-01-ANT1
              adapter: production-rfid-1
            - id: RS-asset-01-ANT2
              adapter: production-rfid-2

          sources:
            - key: source-01
              externalId: ${PRIVATE_SOURCE_ID_01}
              registrationFile: data/registrations-source-01.dat
            - key: source-02
              externalId: ${PRIVATE_SOURCE_ID_02}
              virtual: true
              registrationFile: data/registrations-source-02.dat

    - id: system-02
      locationId: 8
      registrationAssets:
        - id: asset-02
          antennas:
            - id: RS-asset-02-ANT1
              adapter: stub-rfid-1
          sources:
            - key: source-03
              externalId: ${PRIVATE_SOURCE_ID_03}
              registrationFile: data/registrations-source-03.dat
```

The production configuration containing the actual asset inventory and external IDs can be private or supplied outside source control. The public framework only requires the topology/schema semantics.

The final configuration may use nested objects, references or multiple files. The important architecture is the topology and validation semantics.

## Configuration validation

Candidate startup validation rules:

- `TimingSystemInstanceId` values are unique in one process;
- `RegistrationAssetId` values are unique in their configured scope;
- every registration asset has at least one valid registration source;
- each source has a valid external `RegistrationSystemId` supplied by deployment configuration;
- source IDs are unique in one running application unless a later simulation namespace requirement explicitly permits reuse;
- each source has its own persistence file/path;
- `AntennaId` values are unique;
- each antenna belongs to one registration asset in the initial model;
- all antenna adapter references can be resolved;
- source-routing policy/configuration is complete and unambiguous;
- persistence paths needed for operation are usable;
- configuration failures are explicit in log/status and do not silently produce partial topology.

## Real and stub compositions

Real and simulated devices use the same topology and public contracts.

Public production-shape example:

```text
TimingSystemInstance system-01
  RegistrationAsset asset-01
    antenna-01 -> ProductionRfidAdapter
    source-01  -> source-specific ledger/file
```

Integration/full-field example:

```text
TimingApplicationRuntime
  system-01
    asset-01
      antennas -> StubRfidAdapter
      sources  -> placeholder source identities

  system-02
    asset-02
      antennas -> StubRfidAdapter
      sources  -> placeholder source identities

  ... additional configured system instances ...
```

Stub inputs must use the normal adapter/event/queue/decrypt-filter/source-routing/registration/persistence/outbox path where those behaviours are under test.

## Full-field backoffice simulation

Running multiple complete system instances in one SI-01 process is an explicit requirement direction.

A test deployment must be able to configure enough instances, assets and sources to model complete field behaviour towards the backoffice.

This allows one development machine/application to exercise:

- multiple independently addressed total systems;
- multiple configured assets per system;
- multiple registration-source streams per asset;
- independent source sequences;
- per-source persistence;
- virtual source mappings;
- realistic registration delivery/reconciliation;
- connection loss/recovery;
- reference-data distribution;
- device/stub behaviour.

The public reference project uses placeholder identities. A private integration project/configuration can provide the real deployment mapping without changing framework code.

## Status hierarchy

Status should mirror the topology sufficiently for diagnosis:

```text
ApplicationStatus
  TimingSystemInstanceStatus[system-01]
    lifecycle
    location
    ready-team/display/start-procedure

    RegistrationAssetStatus[asset-01]
      device/reader state
      AntennaStatus[antenna-01]
      AntennaStatus[antenna-02]

      RegistrationSourceStatus[source-01]
        lastSequence
        registrationPersistence
        acceptedRegistrationCount

      RegistrationSourceStatus[source-02]
        lastSequence
        registrationPersistence
        acceptedRegistrationCount

  TimingSystemInstanceStatus[system-02]
    ...
```

## Java component impact

The Java package model should distinguish the total-system aggregate, registration asset and registration-source stream.

Suggested direction inside `timing-core`:

```text
...timing.core.timingsystem
    TimingSystemInstance
    TimingSystemInstanceState
    TimingSystemHandler

...timing.core.registrationasset
    RegistrationAsset
    RegistrationAssetId
    AntennaBinding
    RegistrationSourceRouter

...timing.core.registrationsource
    RegistrationSource
    RegistrationSystemId
    RegistrationSourceRegistry
    RegistrationSequence

...timing.core.registration
    RegistrationService
    RegistrationRecord
    RegistrationLedger
    RegistrationRepository
```

`registrationasset` owns device/topology/routing context; `registrationsource` owns external source identity/sequence/persistence boundary; `registration` owns registration record behaviour.

## Candidate requirements

Temporary identifiers only.

- **CAND-TOPO-001** — SI-01 shall support multiple complete logical timing-system instances within one application process.
- **CAND-TOPO-002** — One timing-system instance shall support one or more registration assets.
- **CAND-TOPO-003** — One registration asset shall support one or more RFID antennas.
- **CAND-TOPO-004** — One registration asset shall support one or more registration sources, including virtual sources where configured.
- **CAND-TOPO-005** — The mapping between timing-system instances, assets, antennas and registration sources shall be externally configurable.
- **CAND-TOPO-006** — Each registration source shall maintain its own monotonic sequence and registration persistence file.
- **CAND-TOPO-007** — RFID observations shall retain antenna/asset identity and shall be routed to registration sources using explicit configured/domain routing rules.
- **CAND-TOPO-008** — The same topology shall support real and stub/simulated adapters through public contracts.
- **CAND-TOPO-009** — One application shall be able to host a full-field simulation suitable for backoffice integration testing.
- **CAND-TOPO-010** — Configured antenna identities shall be stable and unique within one running application.
- **CAND-TOPO-011** — Public source/design documentation shall not require or expose the actual production asset inventory or external source-ID mapping.

## Open questions

- Does each `TimingSystemInstance` always have exactly one `LocationId`?
- What is the exact routing rule when one registration asset exposes multiple sources?
- Can an accepted observation intentionally create records in multiple registration-source streams?
- What final syntax/file format should settings use?
- Should production registration-asset/source settings live entirely in private configuration, or is a public generic topology file plus private mapping file preferable?
- Which configuration changes may be applied live versus requiring restart?

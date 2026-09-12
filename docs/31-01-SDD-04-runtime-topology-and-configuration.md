# Runtime topology and configuration detailed design

Status: working draft / non-authoritative

Software item: **SI-01 — Headless Timing Application**

This SDD defines the working runtime hierarchy for complete timing-system instances, registration assets, registration-source streams, RFID antennas, source-specific persistence, and configurable real/stub compositions.

It refines `03-domain-baseline.md` without fixing the final configuration-file syntax.

Concrete production asset names, external registration-system IDs and real deployment mappings are intentionally excluded from this public document. Generic placeholder identities are used throughout.

The runtime concepts in this document are **logical/runtime responsibilities**, not a requirement for a separate Maven `runtime` artifact. Artifact/package boundaries are defined in `31-01-SDD-03-java-component-design.md`.

## Runtime hierarchy

The reusable model supports one or more complete logical timing-system instances:

```text
Application composition
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

The same framework can be consumed by different executable applications:

```text
single-system application
  exactly 1 TimingSystemInstance

multi-system / simulation application
  1..X TimingSystemInstance objects
```

The framework therefore models the reusable instance/asset/source concepts without requiring every executable to host multiple systems.

## Application composition versus reusable core

Process-wide concerns include:

- loading and validating settings;
- creating the selected number of `TimingSystemInstance` objects;
- selecting concrete platform/communication implementations;
- shared executor/thread-pool infrastructure where useful;
- public application interfaces;
- logging/application status;
- routing external input to the correct instance where multiple instances are hosted.

Not all of these concerns automatically belong in the reusable `core` package.

Working rule:

- reusable mechanics needed by several applications belong in framework `core`;
- executable-specific topology/composition remains in the application;
- multi-instance registry/routing moves into reusable `core` only when more than one real application needs the same behaviour.

This prevents a simple single-system application from carrying unnecessary multi-system orchestration while keeping extraction possible later.

## `TimingSystemInstance`

A `TimingSystemInstance` represents one complete logical timing system.

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

## `RegistrationAsset`

A `RegistrationAsset` represents a configured physical/logical registration equipment unit.

It owns/configures concerns such as:

- stable internal/configuration `RegistrationAssetId`;
- optional human-facing label/role supplied by deployment configuration;
- `1..X` RFID antenna bindings;
- `1..X` registration sources;
- device lifecycle/status that belongs to the asset rather than one source;
- routing policy determining which source stream(s) receive an accepted observation.

The public framework must not require the human-readable asset label to equal any external registration-system ID.

## `RegistrationSource`

A `RegistrationSource` represents one ordered registration stream.

It owns source-specific concerns such as:

- external/domain `RegistrationSystemId`;
- monotonic source sequence;
- registration ledger/repository;
- source-specific registration persistence;
- source-specific synchronisation/status.

A source may be physical/logical or virtual. One registration asset can expose several sources.

Its stable registration stream identity remains:

```text
(RegistrationSystemId, SequenceNumber)
```

## RFID antenna ownership

An antenna/device endpoint has a configured `AntennaId` and belongs to one `RegistrationAsset` in the initial model.

The software needs an unambiguous mapping:

```text
AntennaId
   -> RegistrationAssetId
   -> TimingSystemInstanceId
```

Source routing happens **after** asset/antenna resolution and is not hard-coded as `AntennaId -> RegistrationSystemId`, because an asset can expose more than one source stream.

## Antenna identifier convention

`AntennaId` is first of all a stable software/configuration identity. A physical label can later use the same value.

Preferred public naming template:

```text
RS-<asset-key>-ANT<n>
```

Use an explicit numeric suffix even when only one antenna is currently present so adding a later antenna does not force identity renaming.

Actual production `<asset-key>` values remain deployment/private data.

## Threading and ordering

The working model is one **logical serialized state-change boundary per `TimingSystemInstance`**, not one OS thread per asset, source or antenna.

```text
RFID callbacks
operator/API commands
CAN/keypad events
reference-data events
        |
        v
resolve target TimingSystemInstance
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

This preserves deterministic ordering for one complete system while each registration source keeps its independent sequence and persistence.

Several instance-level serial executors may share a small backing executor, especially on Raspberry Pi Zero-class hardware.

A single-system application still uses the same per-instance serialization; it simply has no application-level need to route between multiple instances.

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

Configured topology resolves asset ownership:

```java
final class AntennaBinding {
    private final TimingSystemInstanceId timingSystemInstanceId;
    private final RegistrationAssetId registrationAssetId;
    private final AntennaId antennaId;
}
```

Illustrative ingress pseudocode for a multi-system composition:

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

A single-system composition may omit the cross-instance lookup while still passing explicit asset/antenna context into the same instance processing path.

Only after a tag observation is accepted does source-routing policy determine the target registration source stream or streams.

## Source-routing policy

Because one registration asset can expose multiple sources, accepted observations cannot be assumed to map one-to-one from antenna to registration source.

Conceptually:

```java
interface RegistrationSourceRouter {
    List<RegistrationSystemId> route(
        RegistrationAsset asset,
        AcceptedObservation observation,
        TimingSystemState state);
}
```

The concrete routing rule may be simple configuration or domain-specific logic. Production mappings/policies may be provided by private/application-specific composition.

Important properties:

- antenna ownership remains stable when source mappings change;
- every resulting registration gets the target source's own sequence number;
- one accepted observation produces registrations only according to an explicit routing rule;
- tests can inject deterministic public/stub routing;
- public framework code does not embed real deployment IDs.

## Source-specific registration processing

Illustrative processing after source routing:

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

## Per-source persistence

Each registration source has its own persistent registration set/file.

Public example:

```text
data/
  registrations-source-01.<format>
  registrations-source-02.<format>
  registrations-source-03.<format>
```

Actual production file naming may include private deployment identities and is outside the public framework specification.

Each source-specific persistence set must retain enough information to recover at least:

- source registration records;
- last/next committed source sequence;
- schema/version/integrity metadata required by the final persistence design.

The normal application API remains an in-memory/domain abstraction; files are persistence/recovery mechanisms.

## Settings-driven topology

Topology is externally configurable rather than hard-coded.

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
              implementation: production-rfid-1
            - id: RS-asset-01-ANT2
              implementation: production-rfid-2
          sources:
            - key: source-01
              externalId: ${PRIVATE_SOURCE_ID_01}
              registrationFile: data/registrations-source-01.dat
            - key: source-02
              externalId: ${PRIVATE_SOURCE_ID_02}
              virtual: true
              registrationFile: data/registrations-source-02.dat
```

A single-system application may validate `systemInstances` as exactly one. A multi-system/simulation application may accept `1..X` entries.

The production configuration containing actual asset inventory and external IDs can be private or supplied outside source control. The public framework only requires reusable topology semantics.

## Configuration validation

Candidate validation rules include:

- `TimingSystemInstanceId` values are unique in one process;
- application-specific cardinality is enforced (`exactly 1` or `1..X` as applicable);
- `RegistrationAssetId` values are unique in their configured scope;
- every registration asset has at least one valid registration source;
- each source has a valid external `RegistrationSystemId` supplied by deployment configuration;
- source IDs are unique within the required application namespace;
- each source has its own persistence path/set;
- `AntennaId` values are unique;
- each antenna belongs to one registration asset in the initial model;
- all selected communication/platform implementations can be resolved;
- source-routing policy/configuration is complete and unambiguous;
- required persistence paths are usable;
- failures are explicit in log/status and do not silently create partial topology.

## Real and stub compositions

Real and simulated implementations use the same framework contracts/topology semantics.

Single-system production-shaped example:

```text
application
  TimingSystemInstance system-01
    RegistrationAsset asset-01
      antenna-01 -> concrete RFID communication implementation
      source-01  -> source-specific ledger/persistence
```

Multi-system simulation example:

```text
simulation application
  system-01
    asset-01
      antennas -> StubRfid
      sources  -> placeholder source identities

  system-02
    asset-02
      antennas -> StubRfid
      sources  -> placeholder source identities

  ...
```

Stub input must traverse the normal event/queue/domain/source-routing/registration/persistence/outbox path for behaviours under test.

## Full-field backoffice simulation

The framework should permit a multi-system application to model complete field behaviour towards the backoffice.

That application can exercise:

- multiple independently addressed total systems;
- multiple assets per system;
- multiple registration-source streams per asset;
- independent source sequences;
- per-source persistence;
- virtual source mappings;
- delivery/reconciliation;
- connection loss/recovery;
- reference-data distribution;
- device/stub behaviour.

This does not require the normal single-system executable to host every system. A dedicated multi-system/simulation application can consume the same framework library.

Public examples use placeholder identities; private integration configuration can provide real mappings without changing framework code.

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
```

A multi-system application aggregates several `TimingSystemInstanceStatus` objects. A single-system application can expose the same instance status without pretending that unused multi-system routing exists.

## Java package impact

The reusable framework JAR contains package responsibilities rather than separate layer artifacts.

Suggested direction:

```text
io.github.brainboxemb.eventtiming.domain.timingsystem
    TimingSystemInstance
    TimingSystemInstanceState

io.github.brainboxemb.eventtiming.domain.registrationasset
    RegistrationAsset
    RegistrationAssetId
    AntennaBinding
    RegistrationSourceRouter

io.github.brainboxemb.eventtiming.domain.registrationsource
    RegistrationSource
    RegistrationSystemId
    RegistrationSequence

io.github.brainboxemb.eventtiming.domain.registration
    RegistrationService
    RegistrationRecord
    RegistrationLedger
    RegistrationRepository

io.github.brainboxemb.eventtiming.core.execution
    SerialExecutor / reusable instance execution mechanics

io.github.brainboxemb.eventtiming.core.lifecycle
    reusable instance/runtime lifecycle mechanics

io.github.brainboxemb.eventtiming.comm...
    RFID/CAN/HTTP/WebSocket/backoffice communication contracts and implementations as justified

io.github.brainboxemb.eventtiming.platform...
    clock/executor/filesystem/process/device abstractions
```

The executable application's package owns composition and application-specific registry/routing. If multi-instance registry/routing later proves useful to several applications, it can be promoted into reusable framework `core` without requiring a new Maven artifact.

## Candidate requirements

Temporary identifiers only.

- **CAND-TOPO-001** — The reusable framework shall support composition of one or more complete logical timing-system instances; an executable application may constrain the supported cardinality for its product role.
- **CAND-TOPO-002** — One timing-system instance shall support one or more registration assets.
- **CAND-TOPO-003** — One registration asset shall support one or more RFID antennas.
- **CAND-TOPO-004** — One registration asset shall support one or more registration sources, including virtual sources where configured.
- **CAND-TOPO-005** — The mapping between timing-system instances, assets, antennas and registration sources shall be externally configurable where the application topology requires it.
- **CAND-TOPO-006** — Each registration source shall maintain its own monotonic sequence and registration persistence.
- **CAND-TOPO-007** — RFID observations shall retain antenna/asset identity and shall be routed to registration sources using explicit configured/domain routing rules.
- **CAND-TOPO-008** — The same framework contracts shall support real and stub/simulated implementations.
- **CAND-TOPO-009** — A multi-system/simulation application shall be able to host enough framework instances/assets/sources for complete-field backoffice integration testing.
- **CAND-TOPO-010** — Configured antenna identities shall be stable and unique within the applicable running application namespace.
- **CAND-TOPO-011** — Public source/design documentation shall not require or expose actual production asset inventory or external source-ID mapping.

## Open questions

- Does each `TimingSystemInstance` always have exactly one `LocationId`?
- Which executable is the first intended single-system composition and when is a separate multi-system/simulation executable required?
- Which multi-instance mechanics are truly reusable framework `core` versus application-level orchestration?
- What is the exact routing rule when one registration asset exposes multiple sources?
- Can an accepted observation intentionally create records in multiple registration-source streams?
- What final syntax/file format should settings use?
- Should production registration-asset/source settings live entirely in private configuration, or use a public generic topology plus private mapping?
- Which configuration changes may be applied live versus requiring restart?

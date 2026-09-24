# Domain baseline

Status: working domain knowledge / non-authoritative requirements

This document captures stable domain facts and terminology supplied during the initial architecture work. It is intentionally separate from formal requirements: it records what the system domain looks like so later requirements, IDDs, architecture and code use the same concepts consistently.

Concrete production asset names, external registration-system IDs, source mappings and deployment inventories are intentionally **not** recorded in this public repository. They are deployment/proprietary information. Public documents describe the structure and semantics using generic identifiers only.

## Waypoint systems, stages and locations

One running headless timing application must be able to host **multiple logical waypoint systems** at the same time.

The working software/domain term is `WaypointSystem` for one such independently addressed waypoint system. A waypoint is the registration/timing point at the **end of a stage**. A `WaypointSystem` is deployed or configured for a physical event `LocationId`; the software identity of the waypoint and the physical location where it is used are separate concepts.

Conceptually:

```text
TimingApplication
  +-- WaypointSystem waypoint-01 -> LocationId X
  +-- WaypointSystem waypoint-02 -> LocationId Y
  +-- ...
```

Operational state such as `OPEN` / `CLOSED` belongs to the waypoint-system software/domain concept. It is not the lifecycle of a physical registration box merely because that box is used by the waypoint.

A `Stage` and a `WaypointSystem` are related but distinct concepts: a stage ends at a waypoint. Stage-specific reference data such as start-time data may therefore be consumed by the waypoint software without making the stage itself a hardware or runtime container.

The previous working name `TimingSystemInstance` mixed runtime isolation with the domain meaning of a waypoint system. New architecture/design work should use `WaypointSystem`; existing implementation/API names may require a controlled follow-up when the working architecture is accepted.

## Registration hardware and data-source identity

Hardware/deployment identity and logical data identity are separate namespaces.

### Registration asset

A `RegistrationAsset` represents the physical/configured registration hardware unit for inventory, configuration, diagnostics and optional physical labelling.

For example, a physical unit may have an asset identity such as:

```text
RegistrationAssetId = asset-01
```

Concrete production asset names remain deployment/proprietary information and stay outside this public repository.

### Data-source identity

`DataSourceId` is the logical/software identity assigned to an ordered registration/data stream produced by a configured registration system. It is an identity and sequence/persistence scope; this baseline does **not** require a separate first-class `DataSource` software component.

A physical registration system can be configured with a logical data-source identity, for example:

```text
RegistrationAssetId = asset-01
DataSourceId        = source-01
```

Deployments may deliberately choose visually related hardware and data-source labels for convenience, but that is **not** an identity rule. Another producer may use an unrelated logical identity such as `source-02`.

The number of RFID antennas attached to a physical registration system does not by itself create additional data-source identities. A unit with one or two antennas may still produce the same configured `DataSourceId`; antenna identity remains additional origin/diagnostic context.

Known structural rules:

- `RegistrationAssetId` identifies hardware/inventory;
- `DataSourceId` identifies the logical ordered data stream;
- every `DataSourceId`-scoped stream owns its own monotonic registration sequence and source-specific persistence/synchronisation state;
- reserve and virtual data-source identities/streams exist, but their exact relationship to physical producers remains a separate mapping question;
- concrete production asset names, data-source IDs and mappings are deployment/proprietary information.

## Registration hardware and antenna topology

A physical registration asset can have **one or more RFID antennas**.

Conceptually:

```text
RegistrationAsset asset-01
  +-- Antenna ANT1
  +-- Antenna ANT2
  +-- configured DataSourceId source-01
```

The antennas are hardware/device inputs of that registration system. They are not child software components of a `WaypointSystem` and they are not separate data sources merely because there are multiple antennas.

An RFID observation must retain enough hardware context for diagnostics and processing, including the antenna identity where relevant. The resulting committed registration/data record uses the configured `DataSourceId` for stream identity and ordering.

The exact hardware distinction between reader, antenna, power controller and protocol endpoint remains implementation-specific and still needs to be documented for the selected production hardware.

### Antenna identifiers

The current antennas are not necessarily physically labelled. The software nevertheless needs a stable configuration identity for each antenna.

Preferred public naming template:

```text
RS-<asset-key>-ANT<n>
```

Use an explicit numeric suffix even when an asset currently has only one antenna, so adding a second antenna does not require renaming the first.

A future physical label may use the same `AntennaId`. The real `<asset-key>` values used in production remain deployment data and should not be copied into this public repository.

## Separate software, hardware and configuration views

Do not express the complete system as one parent/child tree. The software/domain decomposition, hardware/deployment decomposition and configuration/identity mapping answer different questions.

### Software/domain view

```text
TimingApplication
  1..X WaypointSystem
        waypoint identity
        configured LocationId
        lifecycle/state
        tag/RFID processing
        stage start-time reference data
        registration/journal behaviour
        status
```

The exact component/class boundaries remain design work, but the waypoint system is the software/domain aggregate being operated.

### Hardware/deployment view

```text
RegistrationAsset asset-01
  +-- Antenna 1
  +-- Antenna 2
  +-- ...
```

This view describes physical/configured equipment. It must not be used as the software component hierarchy.

### Configuration/identity mapping

Configuration connects those views and assigns logical stream identities, for example:

```text
WaypointSystem waypoint-A -> LocationId X
RegistrationAsset asset-01     -> DataSourceId source-01
Another producer            -> DataSourceId source-02
```

The concrete configuration file format is not yet selected. Production configuration may contain proprietary asset names/data-source IDs and therefore can live in a private deployment/integration repository or external deployment configuration. Public examples use placeholders.

The same mapping mechanism should support real hardware adapters and stub/simulated adapters without changing the waypoint-domain model.

## Location and record context

Each physical event location has a unique numeric identifier:

```text
LocationId = 1..25
```

A `WaypointSystem` is configured/deployed at a location, while its software identity remains separate from that location identity.

A registration record is associated with both:

```text
DataSourceId
LocationId
```

This lets a logical data source preserve one ordered stream while records still state where the registration occurred. Moving or reconfiguring a producing system must not silently redefine either namespace.

## Registration sequence

Every registration stream has a monotonically increasing sequence number scoped by **`DataSourceId`**.

Conceptually:

```text
RegistrationRecordKey = (DataSourceId, SequenceNumber)
```

The `LocationId`, `RegistrationAssetId` and `AntennaId` may provide useful context, but none of them changes the sequence scope.

Generic example:

```text
source-01:  1041, 1042, 1043, 1044, ...
source-02:   551,  552,  553, ...
```

This allows receiving/upstream systems to reason about stream consistency independently for every source. For example, receiving `1041`, `1042`, `1044` from one source makes a missing `1043` detectable.

Important intended properties:

- the number is monotonic per `DataSourceId`-scoped stream;
- a committed number must not be reused after restart/recovery;
- higher-level synchronisation can use it for ordering and gap/consistency detection;
- moving/changing location must not implicitly reset the source sequence;
- multiple sources inside one asset or total system keep independent sequence streams;
- the exact rules for allowed gaps, wraparound and sequence persistence still need formal requirements.

## Per-source persistence

Each `DataSourceId`-scoped registration stream has its **own registration file**.

The active application model may remain in memory, but registration persistence/recovery must preserve the source boundary so one `DataSourceId`-scoped stream and its sequence state can be recovered and synchronised independently.

Conceptually:

```text
DataSourceId source-01
  in-memory ledger/state
  source-specific sequence
  source-specific registration file

DataSourceId source-02
  in-memory ledger/state
  source-specific sequence
  source-specific registration file
```

The exact file names, external IDs and deployment mappings are configuration/private data. The file format, append/snapshot policy, atomicity and durability rules still need detailed design and formal requirements.

## Registration entries

A registration entry is not limited to participant RFID passage data. Operational events can also be persisted as registration entries when they must participate in the traceable/synchronised stream.

Known example:

- opening a location/waypoint is itself a registration entry.

A working minimal envelope is therefore conceptually:

```text
RegistrationRecord
  dataSourceId
  locationId
  sequenceNumber
  recordType
  observed/event time
  created time
  record-specific payload
```

Asset and antenna context may additionally be retained where useful for diagnostics/audit, but the exact storage/wire schema is not yet fixed.

## Time semantics

Recorded event time and start-time data need one unambiguous absolute-time meaning independent of how a local clock is displayed.

The working dedicated software value name is `TimingTimestamp`. At domain boundaries it represents an absolute point on the time line rather than a local date/time with an implicit time zone. Local time-zone and daylight-saving conversion are presentation/configuration concerns unless a future business rule explicitly depends on a local civil time.

A timestamp is **not** the source-ordering mechanism. Registration source sequence numbers remain the stable ordering/consistency mechanism even if an operating-system wall clock is corrected forwards or backwards.

The SI-01 SAD owns the implementation architecture for `TimingTimestamp`, injectable clock/time sources, monotonic duration measurement and the risk created by wall-clock corrections.

## Team number

The decoded participant/team identity contains a team number in the range:

```text
TeamNumber = 0..999
```

## Race data

`RaceData` is the locally available participant/team/tag reference data used by one `WaypointSystem`.

It may include participant/team reference data, normal tag references and reserve-tag conversion/mapping data. It is waypoint-scoped application/domain state; obtaining or synchronising that data from the backoffice is an integration/application responsibility rather than behaviour owned by a `RaceDataService`.

Stage start-time data remains a separate concern owned by `StageStartTimeRegistry`.

## RFID tag identity structure

The tag ultimately represents a structured identity containing:

```text
prefix + team number + postfix
```

Known semantics:

- `team number` is `0..999`;
- prefix semantics distinguish at least normal, reserve and test tag classes;
- a dedicated prefix indicates that a tag is a reserve tag;
- a dedicated prefix indicates that a tag is a test tag;
- there are two physical tags for a team/identity;
- a postfix distinguishes the two tag copies.

The exact encoded prefix/postfix values, encryption details and protocol representation are proprietary and are not defined here.

A working public semantic representation should preserve the tag class after decoding rather than immediately flattening every tag into one normal participant identity. The exact class/type API remains an implementation/design decision.

## Reserve tags

Reserve tags require conversion/mapping data supplied by the backoffice.

The local timing application therefore needs to be able to resolve a decoded reserve-tag identity through locally synchronised reference data before treating it as the intended team identity.

The mapping must remain available locally when live backoffice connectivity is temporarily unavailable, subject to later freshness/validity requirements.

## Test tags

Test tags are a separate RFID tag class identified by their prefix. They are **not** the same concept as software test doubles, stub adapters or synthetic test tooling.

After decoding, SI-01 must be able to distinguish a test tag from both a normal tag and a reserve tag so test-specific behaviour can be applied deliberately. A test tag must not be silently treated as a normal participant tag merely because its decoded payload also contains a team-like number.

The exact behaviour is intentionally not fixed in this domain baseline. It belongs in operational use cases and later requirements, including whether a test tag creates a registration record, affects calculations, is synchronised to backoffice, is allowed in all lifecycle states, and how it is made visible to an operator.

## Start-time reference data

Start times are supplied/synchronised from the backoffice and retained locally.

They support local calculations such as elapsed time and ranking without requiring every calculation to make a live backoffice request.

## Full-field simulation

A single SI-01 application must be capable of running enough configured `WaypointSystem` objects to represent the complete field behaviour required for backoffice integration testing.

For this use case:

- each total system instance remains separately addressable;
- each configured producer uses its configured data-source identity/identities according to the deployment mapping;
- each `DataSourceId` retains its configured logical identity and independent sequence stream;
- antennas/devices may be stubbed or simulated through the normal adapter contracts;
- registrations still follow the same normal queue, source-sequence, persistence and backoffice paths as production data;
- simulation must not require a special bypass around the application/domain model;
- public test scenarios use generic identities, while a private integration configuration may map to the actual production inventory/protocol IDs.

Resource limits for the original Raspberry Pi Zero and larger desktop/integration-test deployments are different concerns. The architecture should permit the same logical model to run with different configured scale and adapter sets.

## Public/private domain-data boundary

This repository can document structural facts and generic ranges required for reusable framework design, but it must not become an inventory of the live/real deployment.

Keep the following outside the public repository unless deliberately approved for publication:

- actual registration-box/asset names;
- concrete external registration-system/source IDs and their real mappings;
- exact virtual/reserve-source assignments;
- exact production topology/inventory;
- proprietary protocol field values;
- encryption keys or secrets.

Public examples should use names such as `asset-01`, `source-01`, `system-01`, and `RS-<asset-key>-ANT1`.

## Traceability implications

The combination of source identity and monotonically increasing sequence is a domain-level consistency mechanism, not merely an implementation convenience.

Later requirements/design must therefore preserve at least:

```text
source identity
sequence order
registration-asset context where useful
containing total-system context
location association
antenna context where relevant
record type/payload
record time
source-specific persistence/recovery without sequence reuse
synchronisation/gap detection
```

Corrections/revocations should remain traceable rather than silently rewriting earlier records; the exact record model remains under design.

## Open domain questions

- Can a `WaypointSystem` change `LocationId` during one operational session, or is location fixed until the waypoint system is closed/reconfigured?
- Is a physical producing registration system always configured with exactly one `DataSourceId`, and how are reserve/virtual data sources associated with physical or software producers?
- Does sequence numbering start at a defined value for a new data source?
- Are sequence-number gaps allowed after failed/aborted persistence, provided numbers are never reused?
- What happens if the numeric sequence reaches its maximum representation?
- Which operational events besides `OPEN` must be part of a registration stream (for example close/reinitialisation/configuration changes)?
- What exact data must an `OPEN` registration entry contain?
- Are normal, reserve and virtual data sources treated identically by backoffice synchronisation once their source identity is known?
- What exact operational behaviour is required for test tags, and which parts deliberately differ from normal and reserve tags?

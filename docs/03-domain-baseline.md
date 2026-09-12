# Domain baseline

Status: working domain knowledge / non-authoritative requirements

This document captures stable domain facts and terminology supplied during the initial architecture work. It is intentionally separate from formal requirements: it records what the system domain looks like so later requirements, IDDs, architecture and code use the same concepts consistently.

Concrete production asset names, external registration-system IDs, source mappings and deployment inventories are intentionally **not** recorded in this public repository. They are deployment/proprietary information. Public documents describe the structure and semantics using generic identifiers only.

## Runtime and total system instances

One running headless timing application must be able to host **multiple complete logical system instances** at the same time.

The working software term is `TimingSystemInstance` for one such complete logical system.

This is required for both normal composition flexibility and test/simulation use. In particular, one application should be able to simulate the behaviour of a complete field of multiple system instances towards the backoffice.

Conceptually:

```text
TimingApplication
  +-- TimingSystemInstance 1
  +-- TimingSystemInstance 2
  +-- TimingSystemInstance 3
  +-- ...
```

A `TimingSystemInstance` is not the same thing as a physical registration asset or a registration source.

## Registration assets and registration sources

The domain contains two separate identities that must not be conflated.

### Registration asset

A `RegistrationAsset` represents the real/configured registration box or logical equipment asset.

An asset has a stable configured identity/name for inventory, status, configuration and optional physical labelling. The concrete production asset names are deployment/proprietary information and stay outside this public repository.

A `TimingSystemInstance` can contain one or more registration assets.

### Registration source

A `RegistrationSource` represents one ordered registration stream towards storage/backoffice semantics.

Each source has an external/domain system identifier. `RegistrationSystemId` remains the working name for that external/source identifier where it appears in records and protocol contracts.

Important structural rules:

- one registration asset can expose one or more registration sources;
- some sources can be virtual rather than corresponding one-to-one with a physical box;
- reserve and normal source classes exist;
- the exact production names, IDs, ranges and mappings are proprietary/deployment data and are not documented here;
- every source owns its own monotonic registration sequence and source-specific registration persistence.

Conceptually:

```text
TimingSystemInstance
  +-- RegistrationAsset asset-01
  |     +-- RegistrationSource source-01
  |     +-- RegistrationSource source-02   # may be virtual
  |
  +-- RegistrationAsset asset-02
        +-- RegistrationSource source-03
```

This separation allows a real asset name to remain useful for operations without forcing that name to equal the external registration-system identifier.

## RFID antenna ownership and routing

A registration asset can have **one or more RFID antennas**.

Conceptually:

```text
TimingSystemInstance
  +-- RegistrationAsset asset-01
        +-- Antenna RS-<asset-key>-ANT1
        +-- Antenna RS-<asset-key>-ANT2
        +-- RegistrationSource source-01
        +-- RegistrationSource source-02
```

An RFID observation must retain enough antenna/asset context for the software to route an accepted observation to the correct registration-source stream or streams.

The antenna therefore belongs primarily to the **asset**, not inherently to one source. Source selection/routing is a configurable/domain policy because one asset can expose multiple registration sources.

The exact hardware distinction between reader, antenna, power controller and protocol endpoint remains implementation-specific and still needs to be documented for the selected production hardware.

### Antenna identifiers

The current antennas are not necessarily physically labelled. The software nevertheless needs a stable configuration identity for each antenna.

Preferred public naming template:

```text
RS-<asset-key>-ANT<n>
```

Use an explicit numeric suffix even when an asset currently has only one antenna, so adding a second antenna does not require renaming the first.

A future physical label may use the same `AntennaId`. The real `<asset-key>` values used in production remain deployment data and should not be copied into this public repository.

## Configurable topology

The relationship between application instances, registration assets, registration sources and antennas should be externally configurable through settings rather than hard-coded in application source.

The configuration needs to be able to describe at least:

```text
TimingApplication
  1..X TimingSystemInstance
    1..X RegistrationAsset
      1..X Antenna
      1..X RegistrationSource
        external RegistrationSystemId mapping
        source-specific sequence/persistence
```

The concrete configuration file format is not yet selected.

Production configuration may contain proprietary asset names/source IDs and therefore can live in a private deployment/integration repository or external deployment configuration. Public examples must use placeholder identities.

The same topology mechanism should support both real hardware adapters and stub/simulated adapters so a single application can model multiple total systems for integration/backoffice testing.

## Locations

Each physical event location has a unique numeric identifier:

```text
LocationId = 1..25
```

A registration record is associated with both:

```text
RegistrationSystemId
LocationId
```

The exact configuration ownership of `LocationId` still needs to be made explicit. A likely model is that the containing `TimingSystemInstance` provides the normal location context, while every persisted registration still carries the location explicitly for traceability and synchronisation.

## Registration sequence

Every registration stream has a monotonically increasing sequence number **per registration source**.

Conceptually:

```text
RegistrationRecordKey = (RegistrationSystemId, SequenceNumber)
```

The `LocationId`, `RegistrationAssetId` and `AntennaId` may provide useful context, but none of them changes the sequence scope.

Generic example:

```text
source-01:  1041, 1042, 1043, 1044, ...
source-02:   551,  552,  553, ...
```

This allows receiving/upstream systems to reason about stream consistency independently for every source. For example, receiving `1041`, `1042`, `1044` from one source makes a missing `1043` detectable.

Important intended properties:

- the number is monotonic per registration source;
- a committed number must not be reused after restart/recovery;
- higher-level synchronisation can use it for ordering and gap/consistency detection;
- moving/changing location must not implicitly reset the source sequence;
- multiple sources inside one asset or total system keep independent sequence streams;
- the exact rules for allowed gaps, wraparound and sequence persistence still need formal requirements.

## Per-source persistence

Each registration source has its **own registration file**.

The active application model may remain in memory, but registration persistence/recovery must preserve the source boundary so one source stream and its sequence state can be recovered and synchronised independently.

Conceptually:

```text
RegistrationSource source-01
  in-memory ledger/state
  source-specific sequence
  source-specific registration file

RegistrationSource source-02
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
  registrationSystemId
  locationId
  sequenceNumber
  recordType
  observed/event time
  created time
  record-specific payload
```

Asset and antenna context may additionally be retained where useful for diagnostics/audit, but the exact storage/wire schema is not yet fixed.

## Team number

The decoded participant/team identity contains a team number in the range:

```text
TeamNumber = 0..999
```

## RFID tag identity structure

The tag ultimately represents a structured identity containing:

```text
prefix + team number + postfix
```

Known semantics:

- `team number` is `0..999`;
- a dedicated prefix indicates that a tag is a reserve tag;
- there are two physical tags for a team/identity;
- a postfix distinguishes the two tag copies.

The exact encoded prefix/postfix values, encryption details and protocol representation are proprietary and are not defined here.

## Reserve tags

Reserve tags require conversion/mapping data supplied by the backoffice.

The local timing application therefore needs to be able to resolve a decoded reserve-tag identity through locally synchronised reference data before treating it as the intended team identity.

The mapping must remain available locally when live backoffice connectivity is temporarily unavailable, subject to later freshness/validity requirements.

## Start-time reference data

Start times are supplied/synchronised from the backoffice and retained locally.

They support local calculations such as elapsed time and ranking without requiring every calculation to make a live backoffice request.

## Full-field simulation

A single SI-01 application must be capable of running enough configured `TimingSystemInstance` objects to represent the complete field behaviour required for backoffice integration testing.

For this use case:

- each total system instance remains separately addressable;
- each configured registration asset can expose one or more source streams;
- each source retains its configured external/source-like identity and independent sequence stream;
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

- Does each `TimingSystemInstance` always correspond to exactly one `LocationId`, or are there valid cases where one instance contains multiple location contexts?
- How is an accepted RFID observation routed when one registration asset exposes multiple registration sources: one selected source, several streams, or a policy determined by operation/configuration?
- Does sequence numbering start at a defined value for a new registration source?
- Are sequence-number gaps allowed after failed/aborted persistence, provided numbers are never reused?
- What happens if the numeric sequence reaches its maximum representation?
- Which operational events besides `OPEN` must be part of a registration stream (for example close/reinitialisation/configuration changes)?
- What exact data must an `OPEN` registration entry contain?
- Are normal, reserve and virtual registration sources treated identically by backoffice synchronisation once their source identity is known?

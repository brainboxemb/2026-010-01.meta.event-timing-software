# Domain baseline

Status: working domain knowledge / non-authoritative requirements

This document captures stable domain facts and terminology supplied during the initial architecture work. It is intentionally separate from formal requirements: it records what the system domain looks like so later requirements, IDDs, architecture and code use the same concepts consistently.

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

A `TimingSystemInstance` is **not** the same thing as a `RegistrationSystemId` source.

## Registration systems

Every registration system/source has its own identifier.

Known identifier classes are:

- normal registration systems: `A` through `I`;
- reserve registration systems: reserve systems `1` through `4`;
- virtual registration systems also exist; their exact identifier representation still needs to be documented.

The term `RegistrationSystemId` is used as the working software name for this identity.

A registration system is a **source of an ordered registration stream**. Its sequence numbering is independent from the location number and from the containing `TimingSystemInstance`.

One `TimingSystemInstance` can contain **one or more registration systems**.

Conceptually:

```text
TimingSystemInstance
  +-- RegistrationSystem A
  +-- RegistrationSystem B
  +-- ...
```

A total system can therefore register for one source or for multiple sources.

## RFID antenna mapping

One registration system can be coupled to **one or more RFID antennas**.

Conceptually:

```text
TimingSystemInstance
  +-- RegistrationSystem A
  |     +-- Antenna RS-A-ANT1
  |     +-- Antenna RS-A-ANT2
  |
  +-- RegistrationSystem B
        +-- Antenna RS-B-ANT1
```

An RFID observation must retain enough antenna/source context for the software to route it to the correct registration-system processing path.

The exact hardware distinction between reader, antenna, power controller and protocol endpoint remains implementation-specific and still needs to be documented for the selected production hardware.

Whether one physical antenna may ever be intentionally shared by more than one registration system remains an open domain/configuration question. The initial architecture should prefer an unambiguous configured ownership relationship.

### Antenna identifiers

The current antennas are not necessarily physically labelled. The software nevertheless needs a stable configuration identity for each antenna.

The preferred working naming convention is:

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

The numeric antenna suffix should be present even when a registration system currently has only one antenna, so adding a second antenna does not require renaming the first.

A future physical label may use the same `AntennaId`.

`RegistrationSystemId` and a readable/configuration name such as `FINISH` are kept conceptually separate until the exact domain naming is confirmed. This avoids accidentally changing the source identity merely to obtain useful device labels.

## Configurable topology

The relationship between application instances, registration systems and antennas should be externally configurable through a settings/configuration file rather than hard-coded in application source.

The configuration needs to be able to describe at least:

```text
TimingApplication
  1..X TimingSystemInstance
    1..X RegistrationSystemId
      1..X antenna/device binding
```

The concrete configuration file format is not yet selected.

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

The exact configuration ownership of `LocationId` still needs to be made explicit. A likely model is that the containing total system instance provides the normal location context, while every persisted registration still carries the location explicitly for traceability and synchronisation.

## Registration sequence

Every registration stream has a monotonically increasing sequence number **per registration system/source**.

Conceptually:

```text
RegistrationRecordKey = (RegistrationSystemId, SequenceNumber)
```

The `LocationId` remains data on the record but is **not** part of the sequence scope.

Example:

```text
source A:  1041, 1042, 1043, 1044, ...
source B:   551,  552,  553, ...
```

This allows receiving/upstream systems to reason about stream consistency independently for every source. For example, receiving `1041`, `1042`, `1044` from source `A` makes a missing `1043` detectable.

Important intended properties:

- the number is monotonic per registration source;
- a committed number must not be reused after restart/recovery;
- higher-level synchronisation can use it for ordering and gap/consistency detection;
- moving/changing location must not implicitly reset the source sequence;
- multiple registration systems inside one total system keep independent sequence streams;
- the exact rules for allowed gaps, wraparound and sequence persistence still need formal requirements.

## Per-registration-system persistence

Each registration system/source has its **own registration file**.

The active application model may remain in memory, but registration persistence/recovery must preserve the source boundary so one source stream and its sequence state can be recovered and synchronised independently.

Conceptually:

```text
RegistrationSystem A
  in-memory ledger/state
  sequence A
  source-specific registration file

RegistrationSystem B
  in-memory ledger/state
  sequence B
  source-specific registration file
```

The exact file format, append/snapshot policy, atomicity and durability rules still need detailed design and formal requirements.

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

This is not yet the final storage or wire schema.

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
- a dedicated prefix indicates that a tag is a **reserve tag**;
- there are two physical tags for a team/identity;
- a postfix distinguishes the two tag copies.

The exact encoded prefix/postfix values and encryption/protocol representation are proprietary/detail information and are not defined here.

## Reserve tags

Reserve tags require conversion/mapping data supplied by the backoffice.

The local timing application therefore needs to be able to resolve a decoded reserve-tag identity through locally synchronised reference data before treating it as the intended team identity.

The mapping must remain available locally when live backoffice connectivity is temporarily unavailable, subject to later freshness/validity requirements.

## Start-time reference data

Start times are also supplied/synchronised from the backoffice and retained locally.

They support local calculations such as elapsed time and ranking without requiring every calculation to make a live backoffice request.

## Full-field simulation

A single SI-01 application must be capable of running enough configured `TimingSystemInstance` objects to represent the complete field behaviour required for backoffice integration testing.

For this use case:

- each total system instance remains separately addressable;
- each registration source retains its real/source-like identity and independent sequence stream;
- antennas/devices may be stubbed or simulated through the normal adapter contracts;
- registrations still follow the same normal queue, source-sequence, persistence and backoffice paths as production data;
- simulation must not require a special bypass around the application/domain model.

Resource limits for the original Raspberry Pi Zero and larger desktop/integration-test deployments are different concerns. The architecture should permit the same logical model to run with different configured scale and adapter sets.

## Traceability implications

The combination of source identity and monotonically increasing sequence is a domain-level consistency mechanism, not merely an implementation convenience.

Later requirements/design must therefore preserve at least:

```text
source identity
sequence order
containing total-system context
location association
antenna/source routing context where relevant
record type/payload
record time
source-specific persistence/recovery without sequence reuse
synchronisation/gap detection
```

Corrections/revocations should remain traceable rather than silently rewriting earlier records; the exact record model remains under design.

## Open domain questions

- What is the exact identifier format/name for reserve registration systems 1..4?
- What identifiers are used for virtual registration systems?
- Does each `TimingSystemInstance` always correspond to exactly one `LocationId`, or are there valid cases where one instance contains multiple location contexts?
- Can the same physical antenna ever intentionally feed more than one registration system, or is ownership always exactly one registration system?
- Is `FINISH` a registration-source identifier, a human-readable registration-system name/role, or both?
- Does sequence numbering start at a defined value for a new registration system?
- Are sequence-number gaps allowed after failed/aborted persistence, provided numbers are never reused?
- What happens if the numeric sequence reaches its maximum representation?
- Which operational events besides `OPEN` must be part of the registration stream (for example close/reinitialisation/configuration changes)?
- What exact data must an `OPEN` registration entry contain?
- Are normal/reserve/virtual registration systems treated identically by backoffice synchronisation once their source identity is known?

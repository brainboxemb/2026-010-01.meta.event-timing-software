# Domain baseline

Status: working domain knowledge / non-authoritative requirements

This document captures stable domain facts and terminology supplied during the initial architecture work. It is intentionally separate from formal requirements: it records what the system domain looks like so later requirements, IDDs, architecture and code use the same concepts consistently.

## Registration systems

Every registration system/source has its own identifier.

Known identifier classes are:

- normal registration systems: `A` through `I`;
- reserve registration systems: reserve systems `1` through `4`;
- virtual registration systems also exist; their exact identifier representation still needs to be documented.

The term `RegistrationSystemId` is used as the working software name for this identity.

A registration system is a **source of an ordered registration stream**. Its sequence numbering is independent from the location number.

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

The relationship between the current architecture term `TimingSystem` and the domain term `registration system` still needs to be made explicit. Do not silently assume they are identical until that mapping is confirmed.

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
- the exact rules for allowed gaps, wraparound and sequence persistence still need formal requirements.

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

## Traceability implications

The combination of source identity and monotonically increasing sequence is a domain-level consistency mechanism, not merely an implementation convenience.

Later requirements/design must therefore preserve at least:

```text
source identity
sequence order
location association
record type/payload
record time
recovery without sequence reuse
synchronisation/gap detection
```

Corrections/revocations should remain traceable rather than silently rewriting earlier records; the exact record model remains under design.

## Open domain questions

- What is the exact identifier format/name for reserve registration systems 1..4?
- What identifiers are used for virtual registration systems?
- Is a `TimingSystem` exactly one `RegistrationSystemId`, or does the architecture need a separate mapping between those concepts?
- Does sequence numbering start at a defined value for a new registration system?
- Are sequence-number gaps allowed after failed/aborted persistence, provided numbers are never reused?
- What happens if the numeric sequence reaches its maximum representation?
- Which operational events besides `OPEN` must be part of the registration stream (for example close/reinitialisation/configuration changes)?
- What exact data must an `OPEN` registration entry contain?
- Are normal/reserve/virtual registration systems treated identically by backoffice synchronisation once their source identity is known?

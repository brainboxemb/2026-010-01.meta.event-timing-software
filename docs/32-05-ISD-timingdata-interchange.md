# TimingData Interchange Interface Specification (ISD)

Status: review candidate / Step 4 D03 first TimingData slice

System interface: **IF-05 — TimingData Interchange**

## Purpose

This Interface Specification Document defines the normative TimingData
interchange contract.

It defines **what** every conforming TimingData representation must preserve:

- record identity and source ordering;
- Node ID, Location ID and Registration ID semantics;
- automatic and manual registration semantics;
- effective-time and recorded-time meaning;
- compatibility rules for the default/reference representation and alternative
  product/event-specific representations.

Concrete encoding choices for the current default/reference representation are
defined in `33-05-IDD-timingdata-interchange.md`.

IF-05 does not define Java classes, provider/factory APIs, worker threads,
storage classes or UI behaviour. Those are software-item design concerns.

The current slice does not define TimingNode OPEN/CLOSE as TimingData records and
does not enable registration revocation at runtime. A future design may add
revoke records without changing the identity/order principles defined here.

## Inputs

IF-05 is a system-owned interface allocated by
`31-SSSD-software-system-specification-document.md`.

Applicable system use cases provide the operational intent. Software-item
specifications and detailed designs consume this ISD and shall not redefine the
interface semantics independently.

## Interface scope

IF-05 owns:

- the semantic values carried by TimingData records;
- stable record identity;
- source ordering;
- registration identity and registration-family semantics;
- timestamp semantics;
- compatibility obligations across concrete representations;
- requirements on the public/default reference representation.

IF-05 does **not** own:

- RFID/tag decoding or source-resolution algorithms;
- TimingNode lifecycle implementation;
- sequence-allocation implementation;
- persistence classes or filesystem APIs;
- application queues/threads;
- query/read-model implementation;
- UI rendering;
- upstream transport/session mechanics;
- Java provider/factory/codec design.

## Common TimingData semantics

Every committed TimingData record has these common semantic values:

| Semantic value | Meaning |
| --- | --- |
| Node ID | identifies the TimingNode that owns the source stream |
| sequence number | monotonically increasing record order within that Node ID stream |
| Location ID | location captured for the represented timing fact |
| record family | identifies the kind of timing fact |
| effective time | absolute time at which the represented timing fact applies |
| recorded time | absolute time captured when the definitive record is materialized for commit |
| family-specific values | values required by the selected TimingData family |

A committed record captures its Location ID. Later TimingNode reconfiguration
does not change historical records.

The default/reference development-v1 design maps these values to concrete JSON
members in `33-05-IDD-timingdata-interchange.md`.

## Stable record key and sequence

The stable record key is:

```text
(Node ID, sequence number)
```

Sequence rules:

- numbering is scoped per Node ID;
- the authoritative local source stream advances by exactly one for each
  successfully committed record;
- failed/uncommitted commit attempts do not consume a sequence number;
- a new source stream starts at **1**;
- sequence number **0 is reserved**;
- changing Location ID does not reset the sequence;
- sequence is an ordering/traceability value, not a timestamp;
- a committed record key is never reused;
- the sequence does not wrap;
- an authoritative complete local stream is contiguous;
- partial/imported/exported subsets may contain visible gaps, but records are not
  renumbered and such a subset shall not be presented as a complete contiguous
  authoritative stream.

How software allocates and durably commits the next sequence is outside IF-05.

## Registration semantics

The first TimingData slice defines two registration families:

- **automatic registration** — created after an automatic observation has been
  accepted;
- **manual registration** — explicitly initiated by an operator/tool.

A registration record carries one canonical **Registration ID**. Source-specific
identities such as RFID/tag identifiers or team/reference-data identifiers are
not part of the current common registration record.

For a manual registration the record also preserves how its effective time was
obtained:

- system-assigned time; or
- operator-entered time.

The current slice defines registration **add** behaviour. Registration revoke is
reserved for later behaviour; it is not currently executable.

When revoke behaviour is promoted, a revoke record shall be a new immutable
record with its own record key. It shall not rewrite or delete the original
record.

The duplicate/ambiguity policy needed to identify the registration being revoked
is deferred until that behaviour is promoted.

## Registration ID boundary

Registration ID is a provider-neutral semantic value at IF-05.

The common semantic form is a non-empty string. Event/profile-specific allowed
values, number ranges, tag mappings and participant/reference-data rules remain
outside IF-05.

Registration ID is separate from the TimingData record key.

## Time semantics

TimingData effective time and recorded time represent absolute UTC instants.

The interface semantics require:

- the represented instant is preserved;
- comparison of timestamps is by absolute instant;
- source sequence remains authoritative for record ordering;
- recorded time is metadata captured when the definitive record is materialized
  for the commit attempt;
- recorded time is not itself a durable-commit marker.

The default/reference textual timestamp representation is defined in the IDD.

## Default/reference representation

IF-05 requires one public default/reference representation so development,
engineering/test tooling and compatible consumers can exchange TimingData
without depending on a product-specific representation.

The current design is documented by
`33-05-IDD-timingdata-interchange.md`.

The reference representation shall:

- carry all common and record-family-specific values needed to interpret one
  record;
- identify record identity and source order unambiguously;
- allow one complete record to be decoded without requiring preceding or
  following TimingData records;
- define an unambiguous record-completion boundary;
- identify the representation version used by each record;
- allow compatible additions without changing the meaning of existing values;
- prevent unsupported versions from being silently interpreted using another
  version's semantics.

## Alternative representations

A product/event-specific implementation may use another concrete representation,
including a different text, fixed-field, binary or proprietary format.

Such a representation does not need to use the default filename extension,
record framing or member names. It must preserve the IF-05 semantic contract
when data is translated to/from the common boundary.

## IF-05 requirements

The requirements below define observable interface behaviour and semantic
constraints. Concrete JSON member names, line framing, numeric encoding and
version-number conventions belong to the IDD and are not software
implementation requirements.

```{ifreq} Required TimingData values
:id: IF05-REQ-001
:status: draft

Every committed TimingData record shall carry exactly one Node ID, sequence
number, Location ID, record family, effective time and recorded time, plus every
value required by that record family.
```

```{ifreq} Stable TimingData record key
:id: IF05-REQ-002
:status: draft

The pair (Node ID, sequence number) shall uniquely identify one committed
TimingData record. Two distinct committed records shall not use the same pair.
```

```{ifreq} Authoritative sequence progression
:id: IF05-REQ-003
:status: draft

For each Node ID, the first committed record in an authoritative source stream
shall have sequence number 1. Each later committed record shall have the previous
committed sequence number plus 1. Sequence number 0 shall not identify a
committed record.
```

```{ifreq} Registration family
:id: IF05-REQ-004
:status: draft

Each registration record in the current IF-05 slice shall identify exactly one
registration family: automatic registration or manually initiated registration.
```

```{ifreq} Canonical registration identity
:id: IF05-REQ-005
:status: draft

Each registration record shall carry exactly one Registration ID as its
canonical registration identity.
```

```{ifreq} Registration ID value
:id: IF05-REQ-006
:status: draft

Registration ID at the common IF-05 boundary shall be a non-empty string.
Event/profile-specific allowed values, ranges and mappings shall remain outside
IF-05.
```

```{ifreq} Source-specific identity exclusion
:id: IF05-REQ-007
:status: draft

The current common registration record shall not use source-specific tag,
transponder or reference-data identifiers in place of Registration ID.
```

```{ifreq} Registration action and manual-time source
:id: IF05-REQ-008
:status: draft

The current registration slice shall represent registration add operations.
A manually initiated registration shall also identify whether its effective time
was system-assigned or operator-entered.
```

```{ifreq} Independently decodable reference record
:id: IF05-REQ-009
:status: draft

The default/reference representation shall carry all values needed to interpret
one complete TimingData record without requiring preceding or following
TimingData records.
```

```{ifreq} Unambiguous record completion
:id: IF05-REQ-010
:status: draft

The default/reference representation shall define an unambiguous completion
boundary for each record. Data after the last completed boundary shall not be
interpreted as a complete TimingData record.
```

```{ifreq} Alternative representation compatibility
:id: IF05-REQ-011
:status: draft

Translation between a conforming alternative representation and the common
IF-05 boundary shall preserve the stable record key, source order, Location ID,
record family, Registration ID where applicable, effective time and recorded
time.
```

```{ifreq} Committed-record immutability
:id: IF05-REQ-012
:status: draft

Once a TimingData record is committed, the semantic values associated with its
stable record key shall not change. A later correction or revocation, when
supported, shall be represented by another record rather than by rewriting the
committed record.
```

```{ifreq} Absolute timestamp semantics
:id: IF05-REQ-013
:status: draft

Effective time and recorded time shall each represent one absolute UTC instant.
Translation between conforming IF-05 representations shall preserve that
instant.
```

```{ifreq} Sequence defines source order
:id: IF05-REQ-014
:status: draft

Within one Node ID stream, sequence number shall define authoritative record
order. Effective time and recorded time shall not change that source order.
```

```{ifreq} Compatible reference additions
:id: IF05-REQ-015
:status: draft

A reader for a supported default/reference representation version shall accept
a record that contains additional unknown representation fields when all
required known values remain valid and the meaning of known values is unchanged.
```

```{ifreq} Explicit representation version
:id: IF05-REQ-016
:status: draft

Each default/reference record shall identify the representation version used to
encode it. A reader shall not decode an unsupported version using the semantics
of a supported version.
```

## Deferred from this first slice

- TimingNode OPEN/CLOSE TimingData representation;
- executable registration revocation/correction behaviour and ambiguity policy;
- start-procedure record family and payload;
- penalty/correction record families and payloads;
- unknown-registration semantics;
- source/tag provenance fields;
- filename/directory policy, retention, rotation and filesystem-specific
  durability primitives;
- upstream transport/session/reconciliation semantics owned by IF-06;
- further IF-03 resources that create or inspect future record types.

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
- the common/reference range is `1..9007199254740991` (`2^53 - 1`);
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
resolved before the definitive registration record is committed.

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

- preserve all common IF-05 semantics;
- keep record identity and source ordering unambiguous;
- support append-oriented persistent/interchange use;
- distinguish complete committed records from an incomplete trailing record;
- provide explicit representation versioning;
- allow compatible readers to tolerate additions that do not change existing
  semantics;
- report malformed/incompatible records explicitly rather than silently
  reinterpreting them.

## Alternative representations

A product/event-specific implementation may use another concrete representation,
including a different text, fixed-field, binary or proprietary format.

Such a representation does not need to use the default filename extension,
record framing or member names. It must preserve the IF-05 semantic contract
when data is translated to/from the common boundary.

## IF-05 requirements

```{ifreq} Common TimingData semantics
:id: IF05-REQ-001

Every committed TimingData record shall expose the common semantic values
defined by this ISD.
```

```{ifreq} Stable TimingData record key
:id: IF05-REQ-002

The stable record key shall be Node ID plus sequence number.
```

```{ifreq} Sequence start and non-reuse
:id: IF05-REQ-003

Sequence numbering shall start at 1 per Node ID stream; 0 is reserved and
committed record keys shall not be reused.
```

```{ifreq} Registration families
:id: IF05-REQ-004

The first TimingData registration slice shall support automatic and manually
initiated registration records.
```

```{ifreq} Canonical registration identity
:id: IF05-REQ-005

Registration records shall carry Registration ID rather than a source-specific
identity.
```

```{ifreq} Registration ID semantics
:id: IF05-REQ-006

Registration ID shall be a non-empty provider-neutral string at the common
IF-05 boundary. Concrete event/profile meanings, allowed values and deployment
mappings shall remain outside IF-05.
```

```{ifreq} Registration source boundary
:id: IF05-REQ-007

Source-specific tag/reference identities shall be resolved to Registration ID
before a registration is committed.
```

```{ifreq} Registration action and manual-time semantics
:id: IF05-REQ-008

The current registration slice shall represent add operations. Manual
registrations shall preserve whether effective time was system-assigned or
operator-entered. A concrete reference representation shall encode those
semantics unambiguously.
```

```{ifreq} Public reference representation
:id: IF05-REQ-009

IF-05 shall provide a public default/reference representation suitable for
append-oriented TimingData persistence/interchange and independent record
decoding.
```

```{ifreq} Incomplete trailing record
:id: IF05-REQ-010

The default/reference representation shall distinguish a complete committed
record from an incomplete trailing record after an interrupted append.
```

```{ifreq} Alternative representation compatibility
:id: IF05-REQ-011

Alternative representations shall preserve IF-05 record identity, ordering,
registration semantics and represented timestamps when translating to/from the
common semantic contract.
```

```{ifreq} Representation-independent semantics
:id: IF05-REQ-012

The common IF-05 semantics shall not depend on the default/reference
representation or one software implementation of that representation.
```

```{ifreq} Absolute timestamp semantics
:id: IF05-REQ-013

TimingData effective and recorded timestamps shall represent absolute UTC
instants. A concrete representation shall preserve the represented instant.
```

```{ifreq} Sequence range and no-wrap rule
:id: IF05-REQ-014

The common/reference sequence range shall be `1..2^53-1`; sequence shall not
wrap and committed values shall not be reused.
```

```{ifreq} Compatible reader behaviour
:id: IF05-REQ-015

The default/reference representation shall support compatible additions while
treating malformed records, invalid known semantics, sequence violations and
unsupported representation versions as explicit compatibility/validation
conditions.
```

```{ifreq} Explicit reference-version maturity
:id: IF05-REQ-016

The default/reference representation shall explicitly distinguish
development/unstable versions from released/stable versions.
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

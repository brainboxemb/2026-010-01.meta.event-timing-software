# TimingData Interchange Interface (IDD)

Status: review candidate / Step 4 D03 first TimingData slice

System interface: **IF-05 — TimingData Interchange**

## Purpose

This Interface Design/Description Document owns the system-level persistent and
interchange contract for TimingData records.

It defines the canonical public record semantics and reference file encoding used
when timing facts cross a durable-file or compatible interchange boundary. It is
deliberately independent from SI-01 internal classes, threads, queues and storage
implementation details.

The first slice covers:

- TimingNode lifecycle facts;
- participant registrations;
- participant-registration revocations;
- record identity and ordering;
- registration identity;
- canonical public/reference file encoding;
- public/private codec/provider compatibility.

Later TimingData record families, including start-procedure and penalty/correction
facts, extend this interface when their domain requirements are promoted.

## Inputs

IF-05 is a system-owned interface allocated by
`31-SSSD-software-system-specification-document.md`.

Applicable system use cases and the stable domain baseline supply operational
meaning. SI-01 software-item design, Java packaging and implementation planning
are downstream consumers of this IDD and shall not redefine the file/interchange
contract independently.

## Parties and consumers

IF-05 is a data/interface boundary rather than a live network connection.

Representative consumers are:

```text
SI-01 Timing Point Application
        |
        +-- writes / reads canonical TimingData file
        |
        +-- converts TimingData for supported upstream/external formats

Engineering/Test Client
        |
        +-- reads / writes/inspects TimingData through the shared codec/provider contract

External/proprietary TimingData provider
        |
        +-- translates external representation <-> canonical TimingData semantics
```

A consumer may use TimingData in memory after decoding, but this IDD does not
prescribe its in-memory object model or presentation.

## Interface ownership

The public TimingData contract owns:

- record kinds and their field meanings;
- stable record identity;
- source ordering semantics;
- registration identity semantics;
- timestamp semantics at the interchange boundary;
- protocol/file versioning;
- canonical public/reference encoding;
- compatibility rules for external/provider translations.

It does **not** own:

- RFID callback handling;
- `TagProcessor` internals;
- record queues or worker threads;
- sequence-allocation implementation classes;
- read-model/projection implementation;
- query execution;
- UI visibility/rendering;
- upstream transport/session mechanics.

Those are software-item design concerns.

<a id="fig-if05-01"></a>
![TimingData v1 interchange model](../../../raw/prod/docs/assets/architecture/timingdata-interchange-model.svg)

*Figure IF05-01 — Canonical TimingData envelope, first record families, identity and representation/provider boundaries.*

The figure deliberately stops at the IF-05 contract boundary. It does not show
which SI-01 component produced a record or which thread persists it; those
relationships belong in SI-01 detailed design.

## TimingData v1 common record envelope

Every committed TimingData v1 record has the following semantic envelope:

```text
TimingDataRecord
  version
  timingNodeId
  sequenceNumber
  locationId
  recordType
  effectiveTime
  recordedAt
  type-specific data
```

First-slice field semantics:

- `version` — TimingData interchange major version; first slice is `1`;
- `timingNodeId` — stable functional identity of the TimingNode that owns the
  record stream;
- `sequenceNumber` — monotonically increasing record sequence scoped to that
  `TimingNodeId`;
- `locationId` — location active for the fact represented by the record;
- `recordType` — semantic record family;
- `effectiveTime` — time at which the represented timing fact applies;
- `recordedAt` — absolute time captured when SI-01 materializes the definitive
  record for the commit attempt; durable commit itself is established only by a
  successful complete append, not by this timestamp;
- type-specific data — semantic payload required by the selected `recordType`.

A record captures its `locationId`; later TimingNode reconfiguration does not
change historical records.

## Stable record key and sequence

The stable record key is:

```text
TimingDataRecordKey = (TimingNodeId, SequenceNumber)
```

Sequence rules:

- numbering is scoped per `TimingNodeId`;
- the authoritative local source stream advances by exactly one for each
  successfully committed record; failed/uncommitted append attempts do not
  consume a sequence number;
- a new source stream starts at **1**;
- sequence number **0 is reserved** and shall not identify a normal committed
  TimingData record;
- canonical v1 `SequenceNumber` values are positive JSON-safe integers in the
  range `1..9007199254740991` (`2^53 - 1`);
- the canonical JSON writer emits the value as a plain decimal integer, without a
  fractional part or exponent notation;
- changing `LocationID` does not reset the sequence;
- sequence is an ordering/traceability value, not a timestamp;
- a committed record key shall not be reused;
- the sequence does not wrap. Exhaustion of the defined range is an explicit
  source failure and shall not restart or reuse earlier values;
- partial/imported/exported subsets may contain visible sequence gaps, but those
  records are not renumbered and the gap shall not be presented as a contiguous
  authoritative source stream.

The internal mechanism that tentatively allocates and durably commits the next
sequence belongs to SI-01 design. IF-05 only defines the externally observable
ordered stream and stable key.

## TimingData v1 record types

### TIMING_NODE_STATE

Represents a traceable TimingNode lifecycle **transition**.

```text
recordType = TIMING_NODE_STATE
state = OPEN | CLOSED
```

For this record family:

- `effectiveTime` is the time at which the represented transition becomes effective;
- `recordedAt` is captured when the definitive transition record is
  materialized for its commit attempt;
- `locationId` is the location associated with the transition;
- an initial process/runtime state of CLOSED with no assigned LocationID does not
  by itself require a synthetic TimingData record.

The public semantic states are `OPEN` and `CLOSED`. Legacy/proprietary status
characters are not IF-05 values.

### REGISTRATION

Represents one participant registration.

```text
recordType = REGISTRATION
registrationIdentity
origin
timeSource
effectiveTime
```

`origin`:

```text
AUTOMATIC
MANUAL
```

`timeSource`:

```text
OBSERVED
SYSTEM_ASSIGNED
OPERATOR_ENTERED
```

Meaning:

- `AUTOMATIC + OBSERVED` represents the normal accepted electronic/tag path;
- a manual registration may use `SYSTEM_ASSIGNED` time;
- a manual registration may instead use `OPERATOR_ENTERED` time.

Provider-specific one-character registration/action codes are not part of the
public IF-05 contract.

### REGISTRATION_REVOKED

Represents an append-only fact that refers to an earlier registration.

```text
recordType = REGISTRATION_REVOKED
reference = TimingDataRecordKey of the concerned REGISTRATION
registrationIdentity
origin
timeSource
effectiveTime
```

Rules:

- the referenced registration remains present and unchanged;
- the revocation is a new record with its own record key and `recordedAt`;
- the referenced record key belongs to the same `TimingNodeId` stream;
- in an authoritative complete source stream, `reference.sequenceNumber` is
  lower than the revocation's own sequence and identifies a
  `REGISTRATION` record;
- a partial/imported subset may omit that earlier record; the reference remains
  representable but is then explicitly unresolved rather than silently treated
  as valid business state;
- `effectiveTime` equals the effective registration/race time of the referenced
  registration, not the later operator/command time;
- `locationId` equals the location captured by the referenced registration,
  even if the TimingNode has subsequently been reconfigured while CLOSED;
- registration identity, origin and time-source semantics remain those of the
  registration being referred to.

TimingData records the facts only. Domain/application business logic may derive an
effective registration state for ranking, classification and other race-result
calculations. Presentation clients independently decide whether a revoked
registration is hidden, struck through, marked revoked or otherwise displayed.

IF-05 does not impose a "maximum one revocation" rule. Behaviour of a command that
would produce redundant or conflicting business facts belongs to the applicable
application/use-case contract.

## TimingData v1 record matrix

| Record type | Common envelope | Type-specific required data |
| --- | --- | --- |
| `TIMING_NODE_STATE` | version, TimingNodeId, sequence, LocationID, effectiveTime, recordedAt | `state = OPEN | CLOSED` |
| `REGISTRATION` | version, TimingNodeId, sequence, LocationID, effectiveTime, recordedAt | `registrationIdentity`, `origin`, `timeSource` |
| `REGISTRATION_REVOKED` | version, TimingNodeId, sequence, original LocationID, original effectiveTime, recordedAt | `registrationIdentity`, `origin`, `timeSource`, `reference` |

The matrix is a compact view of the same normative field semantics above; it does
not define an alternative record shape.

## Canonical JSON field contract

Known v1 members use the following JSON types and validation rules:

| Member | JSON type | Required | v1 rule |
| --- | --- | --- | --- |
| `version` | integer | every record | exactly `1` |
| `timingNodeId` | string | every record | non-empty stable TimingNode identity; carried unchanged from the configured/application identity |
| `sequenceNumber` | integer | every record | `1..9007199254740991`; plain decimal; source-stream ordering rules apply |
| `locationId` | integer | every committed v1 record | positive configured LocationID; concrete deployment/event ranges are outside IF-05 |
| `recordType` | string | every record | `TIMING_NODE_STATE`, `REGISTRATION` or `REGISTRATION_REVOKED` |
| `effectiveTime` | string | every record | canonical IF-05 TimingTimestamp text |
| `recordedAt` | string | every record | canonical IF-05 TimingTimestamp text |
| `state` | string | `TIMING_NODE_STATE` only | `OPEN` or `CLOSED` |
| `registrationIdentity` | string | registration/revocation | non-empty provider-neutral canonical participant identity |
| `origin` | string | registration/revocation | `AUTOMATIC` or `MANUAL` |
| `timeSource` | string | registration/revocation | `OBSERVED`, `SYSTEM_ASSIGNED` or `OPERATOR_ENTERED` |
| `reference` | object | `REGISTRATION_REVOKED` only | `TimingDataRecordKey` of the concerned registration |

Nested objects:

```text
reference
  timingNodeId    non-empty string
  sequenceNumber  integer: 1..9007199254740991
```

`registrationIdentity` is deliberately opaque at the IF-05 boundary. Its
concrete categories, number ranges, source encodings and source-to-participant
mapping rules are not part of this public interchange contract.

Validation rules:

- every required known member is present and non-null;
- a canonical writer omits non-applicable type-specific members rather than
  emitting `null` placeholders;
- a known type-specific member that contradicts the selected `recordType`
  (for example `state` on a `REGISTRATION`) is invalid rather than treated
  as an unknown compatible extension;
- additional genuinely unknown object members are handled by the v1
  compatibility rules below, including inside the defined `reference` object;
- `timingNodeId` values are not normalized, case-folded or derived by IF-05;
  they represent the same stable identity used by the surrounding application
  contracts;
- `AUTOMATIC` registrations use `timeSource = OBSERVED`;
- `MANUAL` registrations use `SYSTEM_ASSIGNED` or `OPERATOR_ENTERED`;
- a revocation repeats the original registration's `registrationIdentity`,
  `origin`, `timeSource`, `locationId` and `effectiveTime`;
- for a revocation, `reference.timingNodeId` equals the record's own
  `timingNodeId`.

The repeated registration fields on `REGISTRATION_REVOKED` are deliberate:
each complete line remains independently decodable for identity/effective-time
inspection, while `reference` preserves the historical relationship to the
original registration.

No chronological ordering invariant is inferred from `effectiveTime` or
`recordedAt`. Operator-entered effective times and wall-clock corrections can
make timestamp ordering differ from record ordering; `sequenceNumber` remains
the authoritative source order.

## Registration identities

`RegistrationIdentity` is the canonical participant identity carried by a
TimingData registration record.

The IF-05 v1 public contract treats it as a non-empty provider-neutral string.
It intentionally does **not** define event categories, participant number ranges,
source/tag encoding, location-to-participant rules or production mapping tables.

Conceptually:

```text
source-specific identity --------\
                                 +--> RegistrationIdentity --> TimingData REGISTRATION
operator/reference identity -----/
```

Resolution to `RegistrationIdentity` happens before the definitive TimingData
record is committed. That resolution may use application/reference data, but the
concrete mapping remains outside IF-05.

A provider may translate an external representation to/from the canonical
identity value. Provider-specific codes and deployment mappings remain outside
this public contract.

## Time semantics

TimingData event/registration timestamps are absolute `TimingTimestamp` values.

The canonical IF-05 v1 text representation is:

```text
YYYY-MM-DDTHH:mm:ss.nnnnnnnnnZ
```

Rules:

- the value is an absolute UTC instant and always uses the literal `Z`;
- fractional seconds contain exactly **9 digits**;
- offsets such as `+02:00`, implicit local time and time-zone names are not
  canonical IF-05 values;
- the nine-digit representation defines interchange resolution/capacity, not the
  accuracy of the underlying hardware or operating-system clock;
- chronological comparison is by represented absolute instant, not by source
  sequence;
- provider-specific/external formats may use another timestamp representation
  but must translate without silently changing the represented instant.

Example:

```text
2026-09-30T20:01:39.123000000Z
```

The `recordedAt` value is metadata captured immediately before the definitive
record is encoded/appended by the ordered commit handler. It is not a durable
commit marker and need not equal the exact physical completion time of the file
write. In particular, source sequence remains authoritative for record ordering
when the wall clock is corrected.

Race/stage start reference data may separately be defined as time-of-day only.
That reference-data concept is not forced into an absolute TimingData timestamp by
inventing a date.

When time-only start data is used for elapsed-time business calculations, the
application resolves it according to the event/race timezone and applicable
race-day rules. That calculation is not part of the TimingData file encoding.

## Canonical public/reference file encoding

The canonical v1 reference file is append-only UTF-8 JSON Lines and represents
records from exactly one `TimingNodeId` source stream.

Rules:

- encoding is UTF-8 without a byte-order mark (BOM);
- there is no file header, footer or comment syntax; version is carried by each
  record;
- one complete TimingData record is encoded on one physical line;
- all records in one canonical file use the same `timingNodeId`;
- canonical writer line ending is **LF** (`0x0A`);
- a reader may accept **CRLF** (`0x0D 0x0A`) for interoperability;
- the line terminator is part of the complete-record boundary: valid JSON bytes
  at EOF without the terminating LF/CRLF are an incomplete trailing record and
  are not committed;
- empty/blank lines are not canonical records and are reported as invalid input
  rather than silently inventing sequence positions;
- every complete record line is independently JSON-decodable;
- the canonical writer emits compact single-line JSON; insignificant whitespace
  and JSON object member ordering are not semantic to readers;
- the canonical writer emits common envelope members in the order shown by this
  IDD, followed by the applicable type-specific members; nested
  `reference` uses `timingNodeId` then `sequenceNumber`;
- the file is append-only; existing records are not rewritten for revocation or
  correction;
- an incomplete trailing line after interrupted/power-loss write is not a
  committed record;
- valid complete records before an incomplete tail remain readable;
- a complete authoritative local file/stream keeps contiguous committed sequence
  order; recovery/import validates ordering and reports gaps, duplicates or
  regressions explicitly;
- canonical JSON member names and enum text are the names shown by this IDD.

The exact file naming, rotation/retention and filesystem durability primitive are
deployment/software-item concerns and are not defined by IF-05.

## Reference JSON shape

The following examples illustrate the canonical v1 semantic shape and timestamp
representation.

Lifecycle example:

```json
{
  "version": 1,
  "timingNodeId": "timing-node-01",
  "sequenceNumber": 1,
  "locationId": 7,
  "recordType": "TIMING_NODE_STATE",
  "effectiveTime": "2026-09-30T20:01:39.123000000Z",
  "recordedAt": "2026-09-30T20:01:39.123000000Z",
  "state": "OPEN"
}
```

Registration example:

```json
{
  "version": 1,
  "timingNodeId": "timing-node-01",
  "sequenceNumber": 2,
  "locationId": 7,
  "recordType": "REGISTRATION",
  "effectiveTime": "2026-09-30T20:01:39.123000000Z",
  "recordedAt": "2026-09-30T20:01:39.123000000Z",
  "registrationIdentity": "participant-0042",
  "origin": "AUTOMATIC",
  "timeSource": "OBSERVED"
}
```

Revocation example:

```json
{
  "version": 1,
  "timingNodeId": "timing-node-01",
  "sequenceNumber": 3,
  "locationId": 7,
  "recordType": "REGISTRATION_REVOKED",
  "effectiveTime": "2026-09-30T20:01:39.123000000Z",
  "recordedAt": "2026-09-30T20:02:05.456000000Z",
  "registrationIdentity": "participant-0042",
  "origin": "AUTOMATIC",
  "timeSource": "OBSERVED",
  "reference": {
    "timingNodeId": "timing-node-01",
    "sequenceNumber": 2
  }
}
```

## Canonical codec and external providers

The framework-owned public/reference codec implements the IF-05 canonical
representation.

A `TimingDataProvider`/translator may support an external/proprietary format:

```text
external/proprietary representation
        |
        v
TimingDataProvider / translator
        |
        v
IF-05 TimingDataRecord semantics
```

Rules:

- the provider translates representation; it does not redefine IF-05 semantics;
- proprietary fixed-field values/codes remain outside this public IDD;
- an external format may use different line endings or physical layout;
- an external fixed-field codec may therefore use CRLF while the canonical
  public/reference writer uses LF;
- SI-01 and the Engineering/Test Client shall be able to use the same compatible
  provider implementation rather than maintaining separate proprietary decoders;
- a provider may internally delegate to a native/proprietary DLL without exposing
  that implementation detail in IF-05.

## Compatibility and versioning

TimingData v1 is identified by `version = 1`.

Compatibility rules:

- a canonical writer emits only members defined by the IF-05 version it
  implements;
- a v1 reader shall tolerate and ignore additional JSON object members on a
  record whose required v1 fields and known semantics remain valid;
- a reader encountering an unknown `recordType` within a supported major
  version shall retain/report the common envelope and sequence position as an
  unsupported record rather than silently reinterpreting it as a known type;
- business projections may skip an unsupported record type only with explicit
  unsupported-data status/diagnostics; they shall not pretend the stream is fully
  understood;
- malformed JSON, a missing required field, an invalid field type/value or a
  sequence violation is an invalid-record condition and shall be reported
  explicitly during authoritative recovery/import;
- an unsupported major `version` is an explicit compatibility failure for
  semantic decoding. The raw line may be retained/exported, but shall not be
  interpreted using v1 semantics;
- compatible additions must not change the meaning of already-defined v1 fields
  or enum values.

Breaking semantic changes shall not silently redefine v1.

## IF-05 requirements

```{ifreq} Common TimingData v1 envelope
:id: IF05-REQ-001

Every committed TimingData record shall contain the v1 common record envelope
defined by this IDD.
```

```{ifreq} Stable TimingData record key
:id: IF05-REQ-002

The stable record key shall be `TimingNodeId + SequenceNumber`.
```

```{ifreq} Sequence start and non-reuse
:id: IF05-REQ-003

Sequence numbering shall start at 1 per TimingNode stream; 0 is reserved and
committed record keys shall not be reused.
```

```{ifreq} TimingData v1 record families
:id: IF05-REQ-004

TimingData v1 shall support `TIMING_NODE_STATE`, `REGISTRATION` and
`REGISTRATION_REVOKED` records as defined by this IDD.
```

```{ifreq} Canonical registration identity
:id: IF05-REQ-005

Registration records shall use canonical `RegistrationIdentity` rather than a
source-specific or provider-specific identity representation.
```

```{ifreq} RegistrationIdentity v1 semantics
:id: IF05-REQ-006

v1 `RegistrationIdentity` shall be a non-empty provider-neutral canonical
participant identity. Concrete event categories, ranges and deployment mappings
shall remain outside IF-05.
```

```{ifreq} Source identity resolution
:id: IF05-REQ-007

Source-specific participant identities shall resolve to canonical
`RegistrationIdentity` before a registration is committed. Concrete source
encoding and mapping rules shall remain outside IF-05.
```

```{ifreq} Append-only registration revocation
:id: IF05-REQ-008

Revocation shall be represented by a new append-only record referring to the
concerned registration; it shall not rewrite the registration.
```

```{ifreq} Canonical reference file encoding
:id: IF05-REQ-009

The canonical public/reference file encoding shall be UTF-8 JSON Lines with LF
writer output and one independently decodable record per complete line.
```

```{ifreq} Incomplete trailing line
:id: IF05-REQ-010

A record shall be considered complete in the canonical file only when its JSON
record bytes are followed by an accepted line terminator. An unterminated
trailing record shall not be interpreted as committed.
```

```{ifreq} External codec semantic compatibility
:id: IF05-REQ-011

External/proprietary codecs shall translate to/from the IF-05 semantic model
rather than redefining its record semantics.
```

```{ifreq} Shared provider contract
:id: IF05-REQ-012

The same provider contract shall be reusable by SI-01 and engineering/test
tooling where that tooling inspects or converts external TimingData
representations.
```

```{ifreq} Canonical TimingTimestamp text
:id: IF05-REQ-013

Canonical IF-05 TimingTimestamp text shall use UTC `Z` form with exactly nine
fractional-second digits as defined by this IDD.
```

```{ifreq} SequenceNumber range and no-wrap rule
:id: IF05-REQ-014

Canonical v1 SequenceNumber shall be a positive JSON-safe integer in the range
`1..2^53-1`, shall not wrap and shall not reuse committed values.
```

```{ifreq} Compatible v1 reader behavior
:id: IF05-REQ-015

v1 readers shall tolerate additional JSON members while treating malformed
records, sequence violations and unsupported major versions as explicit
compatibility/validation conditions according to this IDD.
```

## Deferred from this first slice

- start-procedure record family and payload;
- penalty/correction record families and payloads;
- unknown-team registration semantics;
- source `TagIdentity` provenance exposure;
- file naming, retention, rotation and filesystem-specific durability primitives;
- upstream transport/session/reconciliation semantics owned by IF-06;
- IF-03 control/query resources that create or inspect these records.

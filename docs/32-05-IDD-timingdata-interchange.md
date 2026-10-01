# TimingData Interchange Interface (IDD)

Status: review candidate / Step 4 D03 first TimingData slice

System interface: **IF-05 — TimingData Interchange**

## Purpose

This Interface Design/Description Document owns the system-level persistent and
interchange contract for TimingData.

It defines the common public TimingData semantics plus the default/reference
representation used when timing facts cross a durable-file or compatible
interchange boundary. A configured TimingData profile may use another concrete
Java implementation and representation while preserving the common semantic
contracts. The IDD is deliberately independent from SI-01 internal classes,
threads, queues and storage implementation details.

The first slice covers:

- participant registrations;
- record identity and ordering;
- registration identity;
- canonical public/reference file encoding;
- public/private codec/provider compatibility.

Other TimingData families are added only when a promoted use case or requirement
needs them. In particular, UC-002 currently leaves OPEN/CLOSE-as-TimingData as a
later decision, and the current use-case baseline does not require registration
revocation.

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
        +-- constructs TimingData through configured factory
        +-- reads / writes through matching codec

Engineering/Test Client
        |
        +-- reads / writes / inspects through the same common API

TimingDataProvider
        |
        +-- stateless TimingDataFactory
        +-- matching TimingDataCodec
        +-- default, test or product-specific concrete implementation
```

A consumer may use TimingData in memory after decoding, but this IDD does not
prescribe its in-memory object model or presentation.

## Interface ownership

The public TimingData contract owns:

- the common semantic TimingData families and their field meanings;
- stable TimingData identity;
- source ordering semantics;
- registration identity semantics;
- timestamp semantics at the interchange boundary;
- compatibility rules that every configured profile must preserve.

The default/reference profile additionally owns its concrete versioning and
canonical public/reference encoding. Other profiles may use a different concrete
representation without changing the common semantics.

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

*Figure IF05-01 — Common TimingData registration contract, identity and representation/provider boundaries.*

The figure deliberately stops at the IF-05 contract boundary. It does not show
which SI-01 component produced a record or which thread persists it; those
relationships belong in SI-01 detailed design.

## Common TimingData envelope

Every committed TimingData value exposes the following common semantic envelope.
The default/reference v1 representation serializes these values directly:

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
- changing `LocationId` does not reset the sequence;
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

### REGISTRATION

Represents one committed participant registration.

```text
recordType = REGISTRATION
registrationId
origin
timeSource
effectiveTime
```

The v1 representation distinguishes two semantic registration variants:

```text
AUTOMATIC
  origin = AUTOMATIC
  timeSource = OBSERVED

MANUAL
  origin = MANUAL
  timeSource = SYSTEM_ASSIGNED | OPERATOR_ENTERED
```

An automatic registration uses the accepted observed time. A manual
registration may use the system-assigned time or an explicitly operator-entered
effective time.

These discriminators describe the canonical representation. They do not require
one universal Java record class: the common Java API may expose
`TimingData.AutomaticRegistration` and `TimingData.ManualRegistration` directly
for type safety.

Provider-specific one-character registration/action codes are not part of the
public IF-05 contract.

## TimingData v1 record matrix

| Record type | Common envelope | Type-specific required data |
| --- | --- | --- |
| `REGISTRATION` | version, TimingNodeId, sequence, LocationId, effectiveTime, recordedAt | `registrationId`, `origin`, `timeSource` |

## Canonical JSON field contract

Known v1 members use the following JSON types and validation rules:

| Member | JSON type | Required | v1 rule |
| --- | --- | --- | --- |
| `version` | integer | every record | exactly `1` |
| `timingNodeId` | string | every record | non-empty stable TimingNode identity; carried unchanged from the configured/application identity |
| `sequenceNumber` | integer | every record | `1..9007199254740991`; plain decimal; source-stream ordering rules apply |
| `locationId` | integer | every record | positive LocationId representation; concrete event/profile allowed sets and meanings are outside IF-05 |
| `recordType` | string | every record | exactly `REGISTRATION` in v1 |
| `effectiveTime` | string | every record | canonical IF-05 TimingTimestamp text |
| `recordedAt` | string | every record | canonical IF-05 TimingTimestamp text |
| `registrationId` | string | every record | non-empty RegistrationId representation; concrete event/profile allowed values and meanings are outside IF-05 |
| `origin` | string | every record | `AUTOMATIC` or `MANUAL` |
| `timeSource` | string | every record | `OBSERVED`, `SYSTEM_ASSIGNED` or `OPERATOR_ENTERED` |

`LocationId` and `RegistrationId` are shared value representations at the
IF-05 boundary, not universal event policy. IF-05 owns their serialized shape
and common structural validity. The active event/profile/reference model owns
their concrete meaning, allowed values/ranges and source mappings.

Validation rules:

- every required member is present and non-null;
- `timingNodeId` values are not normalized, case-folded or derived by IF-05;
- `AUTOMATIC` registrations use `timeSource = OBSERVED`;
- `MANUAL` registrations use `SYSTEM_ASSIGNED` or `OPERATOR_ENTERED`;
- no chronological ordering invariant is inferred from `effectiveTime` or
  `recordedAt`; `sequenceNumber` remains the authoritative source order.

## Registration identities

`RegistrationId` is the canonical registration identity carried by a
TimingData registration record.

The IF-05 v1 public contract treats it as a non-empty provider-neutral string
representation. The actual identity domain may be event/profile-specific. IF-05
therefore does **not** define event categories, participant number ranges,
source/tag encoding, location-to-participant rules or production mapping tables.

Conceptually:

```text
TagId  -----> RaceData/reference resolution ----\
                                                  +--> RegistrationId --> TimingData REGISTRATION
TeamId -----> RaceData/reference resolution ----/
```

`TagId` is the RFID/tag source identity and `TeamId` is the
team/reference-data identity used by manual/domain input. Resolution to
`RegistrationId` happens before the definitive TimingData record is created.
Only `RegistrationId` crosses the committed IF-05 TimingData boundary in this
slice. `RegistrationId` is separate from the record key
`(TimingNodeId, SequenceNumber)`.

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
  IDD, followed by the registration-specific members;
- the file is append-only; existing committed records are not rewritten;
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

Automatic registration example:

```json
{
  "version": 1,
  "timingNodeId": "timing-node-01",
  "sequenceNumber": 1,
  "locationId": 7,
  "recordType": "REGISTRATION",
  "effectiveTime": "2026-09-30T20:01:39.123000000Z",
  "recordedAt": "2026-09-30T20:01:39.123000000Z",
  "registrationId": "registration-0042",
  "origin": "AUTOMATIC",
  "timeSource": "OBSERVED"
}
```

Manual registration example:

```json
{
  "version": 1,
  "timingNodeId": "timing-node-01",
  "sequenceNumber": 2,
  "locationId": 7,
  "recordType": "REGISTRATION",
  "effectiveTime": "2026-09-30T20:01:42.000000000Z",
  "recordedAt": "2026-09-30T20:01:45.456000000Z",
  "registrationId": "registration-0042",
  "origin": "MANUAL",
  "timeSource": "OPERATOR_ENTERED"
}
```

## TimingData profiles, factory and codec

A `TimingDataProvider` supplies one coherent concrete profile:

```text
TimingDataProvider
  |
  +-- TimingDataFactory     stateless object construction
  |
  +-- TimingDataCodec       encode/decode the same concrete profile
```

The factory receives already selected construction values and returns the typed
semantic registration variant. It does not allocate sequence numbers, inspect
mutable TimingNode state, persist data or publish events.

The common construction values are grouped once:

```text
TimingDataFactory.Context
  timingNodeId
  sequenceNumber
  locationId
  effectiveTime
  recordedAt
```

The factory then adds only variant-specific values:

```java
TimingData.AutomaticRegistration createAutomaticRegistration(
        TimingDataFactory.Context context,
        RegistrationId registrationId);

TimingData.ManualRegistration createManualRegistration(
        TimingDataFactory.Context context,
        RegistrationId registrationId,
        TimingData.ManualTimeSource timeSource);
```

There is no separate `RegistrationData`, `AutomaticRegistrationContext` or
`ManualRegistrationContext` hierarchy. A concrete profile may return different
immutable implementing classes while callers retain the typed common semantic
contract.

The default/reference profile implements the canonical JSON Lines representation
defined below. A product-specific provider may use another representation,
including a proprietary fixed-field format or native library, provided that its
common TimingData values preserve the IF-05 semantic contracts.

The selected provider/profile is an application/configuration concern. A
`profileId` is therefore not repeated in every common TimingData value. A tool
opening profile-specific data outside that configured context must be told which
provider to use. File-level self-description may be added later if a concrete
standalone-import requirement justifies it.

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

TimingData v1 shall support `REGISTRATION` records as defined by this IDD.
```

```{ifreq} Canonical registration identity
:id: IF05-REQ-005

Registration records shall use canonical `RegistrationId` rather than a
source-specific or provider-specific identity representation.
```

```{ifreq} RegistrationId v1 semantics
:id: IF05-REQ-006

v1 `RegistrationId` shall be a non-empty provider-neutral representation at
the IF-05 boundary. Concrete event/profile meanings, allowed values/ranges and
deployment mappings shall remain outside IF-05.
```

```{ifreq} Source identity resolution
:id: IF05-REQ-007

Source-specific `TagId` / `TeamId` values shall resolve to canonical
`RegistrationId` before a registration is committed. Concrete source
encoding and mapping rules shall remain outside IF-05.
```

```{ifreq} Registration variant semantics
:id: IF05-REQ-008

Automatic registrations shall use observed effective time. Manual registrations
shall distinguish system-assigned and operator-entered effective time as defined
by this IDD.
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

- TimingNode OPEN/CLOSE TimingData representation; UC-002 leaves this as a later decision;
- registration revocation/correction semantics and record family;
- start-procedure record family and payload;
- penalty/correction record families and payloads;
- unknown-team registration semantics;
- source `TagId` provenance exposure;
- file naming, retention, rotation and filesystem-specific durability primitives;
- upstream transport/session/reconciliation semantics owned by IF-06;
- IF-03 control/query resources that create or inspect these records.

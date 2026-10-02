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
later decision, and the current use-case baseline does not require runtime
registration revocation. The development representation does reserve the
registration `REV` action shape so a later promoted revoke flow does not require
another representation redesign.

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

Every committed TimingData value exposes the following common semantic values:

```text
TimingData
  timingNodeId
  sequenceNumber
  locationId
  effectiveTime
  recordedAt
  type-specific semantics
```

Semantic field meanings:

- `timingNodeId` — stable functional identity of the TimingNode that owns the
  record stream;
- `sequenceNumber` — monotonically increasing record sequence scoped to that
  TimingNodeId;
- `locationId` — location captured for the represented timing fact;
- `effectiveTime` — time at which the represented timing fact applies;
- `recordedAt` — absolute time captured when SI-01 materializes the definitive
  record for the commit attempt; durable commit itself is established only by a
  successful complete append, not by this timestamp;
- type-specific semantics — values required by the selected TimingData family.

The compact default/reference JSON representation maps these semantic values to
`nodeId`, `seqNr`, `locId`, `time` and `recTime`. Representation fields
`v`, `recType` and `code` identify the concrete development format and the
registration variant/action.

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

## TimingData v1 registration record types

The development v1 reference representation uses a separate record type for an
automatic registration and a manually initiated registration.

### AUTO_REG

Represents an automatic registration, for example a registration derived from an
accepted automatic observation.

Current Step-4 add shape:

```text
recType = AUTO_REG
code = [ADD]
regId
time
```

The record type already carries the automatic-registration meaning, so `AUTO`
is not repeated in `code`.

The reserved future revoke mirror is:

```text
recType = AUTO_REG
code = [REV]
same regId
same time
```

Runtime creation/processing of `REV` is not part of the current Step-4 slice.

### MAN_REG

Represents a manually initiated registration. Its second code states how the
effective time was obtained:

```text
system-assigned time:
  recType = MAN_REG
  code = [ADD, AUTO]

operator-entered time:
  recType = MAN_REG
  code = [ADD, MAN]
```

The future revoke form mirrors the original time-source code:

```text
[ADD, AUTO]  -> [REV, AUTO]
[ADD, MAN]   -> [REV, MAN]
```

For canonical writer output, the action code (`ADD` or future `REV`) comes
first and the MAN_REG time-source code comes second. Code-array ordering itself
is not semantic to a reader; the combination is semantic. Duplicate,
contradictory or unknown codes for a known record type are invalid.

The common Java API may continue to expose
`TimingData.AutomaticRegistration` and `TimingData.ManualRegistration` for
type safety. The default codec maps those semantic types to the compact
`recType` + `code[]` representation.

Product/event-specific providers may map these semantics to their native record
or action codes. Native provider codes are not imposed on the common Java API.

### Reserved revoke matching semantics

When registration revocation is promoted into an executable use case, a revoke
record repeats the original registration's `regId` and effective/race `time`.
Within the TimingNode stream those values identify the registration to revoke.
The revoke record receives its own new `seqNr` and its own `recTime`; it does
not point to the original LogBook sequence number.

For a manual registration, the revoke record also mirrors the original
`AUTO`/ `MAN` time-source code. The original committed record is never
rewritten or deleted.

The duplicate/ambiguity policy required to guarantee an unambiguous
`regId + time` lookup is part of the deferred runtime revoke design and must be
defined before `REV` is enabled.

## TimingData v1 record matrix

| Record type | Current Step-4 code | Required registration data | Reserved future revoke code |
| --- | --- | --- | --- |
| `AUTO_REG` | `["ADD"]` | `regId`, observed/effective `time` | `["REV"]` |
| `MAN_REG` | `["ADD","AUTO"]` or `["ADD","MAN"]` | `regId`, effective `time` | `["REV","AUTO"]` or `["REV","MAN"]` |

## Canonical JSON field contract

Known development-v1 members use the following JSON types and validation rules.
The canonical writer emits them in the order shown.

| Member | JSON type | Required | v1 rule |
| --- | --- | --- | --- |
| `v` | integer | every record | exactly `1`; odd values denote development/unstable formats |
| `nodeId` | string | every record | non-empty stable TimingNode identity; maps to semantic `TimingNodeId` |
| `seqNr` | integer | every record | `1..9007199254740991`; plain decimal; maps to semantic `SequenceNumber` |
| `locId` | integer | every record | positive LocationId representation; concrete event/profile allowed sets and meanings are outside IF-05 |
| `recType` | string | every record | `AUTO_REG` or `MAN_REG` in the current v1 registration slice |
| `time` | string | every record | canonical effective/race `TimingTimestamp` text |
| `regId` | string | registration records | non-empty RegistrationId representation; concrete event/profile allowed values and meanings are outside IF-05 |
| `code` | array of strings | registration records | exact valid code combination for the selected `recType`; no duplicates |
| `recTime` | string | every record | canonical recorded-at `TimingTimestamp` text |

Canonical member order is therefore:

```text
v
nodeId
seqNr
locId
recType
time
regId
code
recTime
```

`LocationId` and `RegistrationId` are shared value representations at the
IF-05 boundary, not universal event policy. IF-05 owns their serialized shape
and common structural validity. The active event/profile/reference model owns
their concrete meaning, allowed values/ranges and source mappings.

Validation rules:

- every required member is present and non-null;
- `nodeId` values are not normalized, case-folded or derived by IF-05;
- `AUTO_REG` currently accepts exactly `["ADD"]`;
- `MAN_REG` currently accepts `ADD` plus exactly one of `AUTO` or `MAN`;
- readers may accept a valid `code` combination in another array order, but the
  canonical writer always emits action first;
- no chronological ordering invariant is inferred from `time` or `recTime`;
  `seqNr` remains the authoritative source order.

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
                                                  +--> RegistrationId --> TimingData registration
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

The canonical IF-05 development-v1 text representation is:

```text
YYYY-MM-DDTHH:mm:ss[.fraction]Z
```

Rules:

- the value is an absolute UTC instant and always uses the literal `Z`;
- fractional seconds are optional and, when present, contain **1 to 9 digits**;
- the canonical writer omits a fractional part for a whole second and removes
  unnecessary trailing fractional zeroes;
- the representation preserves the absolute instant at up to nanosecond
  resolution; trailing zeroes do not carry independent semantic meaning;
- offsets such as `+02:00`, implicit local time and time-zone names are not
  canonical IF-05 values;
- chronological comparison is by represented absolute instant, not by source
  sequence;
- provider-specific/external formats may use another timestamp representation
  but must translate without silently changing the represented instant.

Examples:

```text
2026-10-01T12:00:00Z
2026-10-02T10:57:43.444Z
2026-10-02T10:57:43.444123789Z
```

The semantic `recordedAt` value is serialized as `recTime`. It is metadata
captured immediately before the definitive record is encoded/appended by the
ordered commit handler. It is not a durable commit marker and need not equal the
exact physical completion time of the file write. In particular, source sequence
remains authoritative for record ordering when the wall clock is corrected.

Race/stage start reference data may separately be defined as time-of-day only.
That reference-data concept is not forced into an absolute TimingData timestamp by
inventing a date.

When time-only start data is used for elapsed-time business calculations, the
application resolves it according to the event/race timezone and applicable
race-day rules. That calculation is not part of the TimingData file encoding.

## Canonical public/reference file encoding

The canonical development-v1 reference file is append-only UTF-8 JSON Lines and
represents records from exactly one `nodeId` source stream.

Rules:

- encoding is UTF-8 without a byte-order mark (BOM);
- there is no file header, footer or comment syntax; `v` is carried by each
  record;
- one complete TimingData record is encoded on one physical line;
- all records in one canonical file use the same `nodeId`;
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
- the canonical writer emits members in this fixed order:
  `v,nodeId,seqNr,locId,recType,time,regId,code,recTime`;
- the file is append-only; existing committed records are not rewritten;
- an incomplete trailing line after interrupted/power-loss write is not a
  committed record;
- valid complete records before an incomplete tail remain readable;
- a complete authoritative local file/stream keeps contiguous committed sequence
  order; recovery/import validates ordering and reports gaps, duplicates or
  regressions explicitly.

The exact file naming, rotation/retention and filesystem durability primitive are
deployment/software-item concerns and are not defined by IF-05.

## Reference JSON shape

The following examples use the canonical compact member order.

Automatic registration:

```json
{"v":1,"nodeId":"Test","seqNr":1,"locId":24,"recType":"AUTO_REG","time":"2026-10-01T12:00:00Z","regId":"N001","code":["ADD"],"recTime":"2026-10-02T10:57:43.444Z"}
```

Manually initiated registration using system-assigned time:

```json
{"v":1,"nodeId":"Test","seqNr":2,"locId":24,"recType":"MAN_REG","time":"2026-10-01T12:00:05Z","regId":"N002","code":["ADD","AUTO"],"recTime":"2026-10-02T10:57:45.1Z"}
```

Manually initiated registration using operator-entered time:

```json
{"v":1,"nodeId":"Test","seqNr":3,"locId":24,"recType":"MAN_REG","time":"2026-10-01T11:59:58.25Z","regId":"N003","code":["ADD","MAN"],"recTime":"2026-10-02T10:57:46Z"}
```

Reserved future revoke examples (not yet executable Step-4 behavior):

```json
{"v":1,"nodeId":"Test","seqNr":4,"locId":24,"recType":"AUTO_REG","time":"2026-10-01T12:00:00Z","regId":"N001","code":["REV"],"recTime":"2026-10-02T11:05:12.123Z"}
{"v":1,"nodeId":"Test","seqNr":5,"locId":24,"recType":"MAN_REG","time":"2026-10-01T11:59:58.25Z","regId":"N003","code":["REV","MAN"],"recTime":"2026-10-02T11:05:14Z"}
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

The default/reference representation uses **integer format versions only**.

Version parity is intentional:

- **odd** values are development/unstable formats;
- **even** values are released/stable formats;
- the current working format is development `v = 1`;
- once the first contract is frozen for release it becomes stable `v = 2`;
- a later incompatible development cycle uses `v = 3`, which may later be
  frozen as stable `v = 4`, and so on;
- decimal/minor values such as `1.1` are not used.

Because v1 is explicitly a development format, its shape may still change while
the Step-4 review candidate is being finalized. A v1 reader and writer are
therefore expected to come from the same agreed development baseline.

Within one supported baseline:

- a canonical writer emits only members defined by the IF-05 version it
  implements;
- a reader shall tolerate and ignore additional JSON object members when the
  required known fields and semantics remain valid;
- a reader encountering an unknown `recType` within a supported version shall
  retain/report the common semantic envelope and sequence position as an
  unsupported record rather than silently reinterpreting it as a known type;
- malformed JSON, a missing required field, an invalid field type/value, an
  invalid `code` combination or a sequence violation is an invalid-record
  condition and shall be reported explicitly during authoritative recovery/import;
- an unsupported integer `v` is an explicit compatibility failure for semantic
  decoding. The raw line may be retained/exported, but shall not be interpreted
  using another version's semantics;
- compatible additions must not silently change the meaning of already-defined
  fields or code values.

A stable even-numbered format is not silently redefined. Breaking work starts in
the next odd-numbered development format.

## IF-05 requirements

```{ifreq} Common TimingData v1 envelope
:id: IF05-REQ-001

Every committed TimingData record shall expose the common semantic values
defined by this IDD. The default/reference representation shall map them to the
compact v1 fields defined here.
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

```{ifreq} TimingData v1 registration families
:id: IF05-REQ-004

Development v1 shall support `AUTO_REG` and `MAN_REG` records as defined by
this IDD.
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

```{ifreq} Registration code semantics
:id: IF05-REQ-008

`AUTO_REG` add records shall use `code=["ADD"]`. `MAN_REG` add records shall
use `code=["ADD","AUTO"]` for system-assigned time or
`code=["ADD","MAN"]` for operator-entered time. The canonical writer shall
emit action first.
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

Canonical IF-05 TimingTimestamp text shall use UTC `Z` form with zero through
nine fractional-second digits. Canonical writer output shall omit unnecessary
trailing fractional zeroes while preserving the represented instant.
```

```{ifreq} SequenceNumber range and no-wrap rule
:id: IF05-REQ-014

Canonical v1 SequenceNumber shall be a positive JSON-safe integer in the range
`1..2^53-1`, shall not wrap and shall not reuse committed values.
```

```{ifreq} Compatible v1 reader behavior
:id: IF05-REQ-015

A v1 reader shall tolerate additional JSON members while treating malformed
records, invalid known-code combinations, sequence violations and unsupported
format versions as explicit compatibility/validation conditions according to
this IDD.
```

```{ifreq} Integer version parity
:id: IF05-REQ-016

The default/reference representation shall use integer format versions only.
Odd versions shall identify development/unstable formats and even versions shall
identify released/stable formats.
```

## Deferred from this first slice

- TimingNode OPEN/CLOSE TimingData representation; UC-002 leaves this as a later decision;
- executable registration revocation/correction behavior, ambiguity/duplicate
  policy and the IF-03/UI operations that invoke it; v1 only reserves the
  `REV` representation shape described above;
- start-procedure record family and payload;
- penalty/correction record families and payloads;
- unknown-team registration semantics;
- source `TagId` provenance exposure;
- file naming, retention, rotation and filesystem-specific durability primitives;
- upstream transport/session/reconciliation semantics owned by IF-06;
- further IF-03 control/query resources that create or inspect future record types.



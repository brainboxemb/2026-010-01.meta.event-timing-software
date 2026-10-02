# TimingData Interchange Interface (IDD)

Status: review candidate / Step 4 D03 first TimingData slice

System interface: **IF-05 — TimingData Interchange**

## Purpose

IF-05 defines the persistent/interchange contract for TimingData.

For the current registration slice it defines:

- record identity and source ordering;
- Node ID, Location ID and Registration ID semantics at the interface;
- automatic and manual registration record types;
- timestamp representation;
- the default/reference JSON record format;
- JSON Lines framing and recovery rules;
- compatibility and versioning rules.

IF-05 defines what a TimingData record means and how the default/reference
representation is encoded. It does not define Java classes, factories, provider
discovery, threads, queues, storage classes or UI behaviour. Those are
software-item design concerns.

A product/event-specific implementation may use another concrete representation,
but it must preserve the common IF-05 semantics defined here.

The current slice does not define TimingNode OPEN/CLOSE as TimingData records and
does not enable registration revocation at runtime. Development v1 reserves the
`REV` record shape so the representation does not need to be redesigned when a
revoke use case is promoted later.

## Inputs

IF-05 is a system-owned interface allocated by
`31-SSSD-software-system-specification-document.md`.

Applicable system use cases define the operational meaning that reaches this
boundary. SI-01 detailed design and implementation are downstream consumers and
shall not redefine the interchange contract independently.

## Interface boundary

IF-05 owns:

- the semantic values carried by TimingData records;
- the stable record key and source ordering rules;
- registration record semantics;
- the default/reference v1 JSON members and validation rules;
- canonical timestamp text;
- JSON Lines record framing;
- compatibility/versioning behaviour.

IF-05 does **not** own:

- RFID/tag decoding or source-resolution algorithms;
- TimingNode lifecycle implementation;
- sequence-allocation implementation;
- persistence classes or filesystem APIs;
- application queues/threads;
- query/read-model implementation;
- UI rendering;
- upstream transport/session mechanics;
- provider/factory/codec Java API design.

Those implementation concerns are described in the applicable SDDs.

<a id="fig-if05-01"></a>
![TimingData v1 interchange model](../../../raw/prod/docs/assets/architecture/timingdata-interchange-model.svg)

*Figure IF05-01 — TimingData semantics, development-v1 JSON representation and JSON Lines stream.*

## TimingData record semantics

Every committed TimingData record has a Node ID and sequence number. Together
they form its stable record key.

For the current registration slice the common values are:

| Semantic value | Development-v1 member | Meaning |
| --- | --- | --- |
| Node ID | `nodeId` | identifies the TimingNode that owns the source stream |
| sequence number | `seqNr` | monotonically increasing record order within that Node ID stream |
| Location ID | `locId` | location captured for the represented timing fact |
| record type | `recType` | identifies the TimingData record family/variant |
| effective time | `time` | absolute time at which the represented timing fact applies |
| Registration ID | `regId` | registration identity carried by registration records |
| record code(s) | `code` | action and, where required, additional record semantics |
| recorded time | `recTime` | absolute time captured when the definitive record is materialized for commit |

The `v` member identifies the concrete representation version and is not part
of the business identity of a record.

A record captures its Location ID. Later TimingNode reconfiguration does not
change an already committed record.

## Stable record key and sequence

The stable record key is:

```text
(Node ID, sequence number)
```

In development-v1 JSON this is:

```text
(nodeId, seqNr)
```

Sequence rules:

- numbering is scoped per Node ID;
- the authoritative local source stream advances by exactly one for each
  successfully committed record;
- failed/uncommitted append attempts do not consume a sequence number;
- a new source stream starts at **1**;
- sequence number **0 is reserved**;
- development-v1 `seqNr` is a positive JSON-safe integer in the range
  `1..9007199254740991` (`2^53 - 1`);
- canonical writer output uses a plain decimal integer without fraction or
  exponent notation;
- changing Location ID does not reset the sequence;
- sequence is an ordering/traceability value, not a timestamp;
- a committed record key is never reused;
- the sequence does not wrap;
- an authoritative complete local stream is contiguous;
- imported/exported subsets may contain visible gaps, but records are not
  renumbered and such a subset shall not be presented as a complete contiguous
  source stream.

How software allocates and commits the next sequence is outside IF-05. IF-05
defines only the observable ordered stream and stable key.

## Registration record types

Development v1 currently defines two registration record types.

### AUTO_REG

`AUTO_REG` represents an automatic registration, for example one produced
after an automatic observation has already been accepted by the application.

Current add form:

```text
recType = AUTO_REG
code    = [ADD]
regId
time
```

The record type itself carries the automatic-registration meaning, so `AUTO`
is not repeated in `code`.

Reserved future revoke form:

```text
recType = AUTO_REG
code    = [REV]
same regId
same time
```

Runtime creation/processing of `REV` is not part of the current Step-4 slice.

### MAN_REG

`MAN_REG` represents a manually initiated registration. Its second code states
how the effective time was obtained.

System-assigned time:

```text
recType = MAN_REG
code    = [ADD, AUTO]
```

Operator-entered time:

```text
recType = MAN_REG
code    = [ADD, MAN]
```

Reserved future revoke forms mirror the original time-source code:

```text
[ADD, AUTO] -> [REV, AUTO]
[ADD, MAN]  -> [REV, MAN]
```

Canonical writer output places the action (`ADD` or future `REV`) first.
Array order is not semantic to a reader; the valid code combination is.
Duplicate, contradictory or unknown codes for a known record type are invalid.

### Reserved revoke matching semantics

When registration revocation is promoted into executable behaviour, the revoke
record repeats the original registration's `regId` and `time`. Within one
Node ID stream those values identify the registration to revoke.

The revoke record receives its own new `seqNr` and `recTime`; it does not
point to the original sequence number. A manual revoke also mirrors the original
`AUTO`/`MAN` time-source code. The original committed record is never
rewritten or deleted.

The duplicate/ambiguity policy required to guarantee an unambiguous
`regId + time` lookup is deferred until runtime revoke behaviour is promoted.

## Development-v1 record matrix

| Record type | Current add code | Required registration data | Reserved future revoke code |
| --- | --- | --- | --- |
| `AUTO_REG` | `["ADD"]` | `regId`, effective `time` | `["REV"]` |
| `MAN_REG` | `["ADD","AUTO"]` or `["ADD","MAN"]` | `regId`, effective `time` | `["REV","AUTO"]` or `["REV","MAN"]` |

## Development-v1 JSON contract

Known members use the following JSON types and validation rules. The canonical
writer emits them in the order shown.

| Member | JSON type | Required | v1 rule |
| --- | --- | --- | --- |
| `v` | integer | every record | exactly `1`; odd values denote development/unstable formats |
| `nodeId` | string | every record | non-empty Node ID; identifies the TimingNode that owns the stream |
| `seqNr` | integer | every record | `1..9007199254740991`; plain decimal |
| `locId` | integer | every record | positive Location ID representation; event/profile allowed sets are outside IF-05 |
| `recType` | string | every record | `AUTO_REG` or `MAN_REG` in the current registration slice |
| `time` | string | every record | canonical absolute effective-time text |
| `regId` | string | registration records | non-empty Registration ID representation |
| `code` | array of strings | registration records | exact valid code combination for the selected `recType`; no duplicates |
| `recTime` | string | every record | canonical absolute recorded-time text |

Canonical member order:

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

General validation rules:

- every required member is present and non-null;
- `nodeId` is not normalized, case-folded or derived by IF-05;
- `AUTO_REG` currently accepts exactly `["ADD"]`;
- `MAN_REG` currently accepts `ADD` plus exactly one of `AUTO` or `MAN`;
- readers may accept a valid `code` combination in another array order, but the
  canonical writer emits action first;
- no chronological ordering invariant is inferred from `time` or `recTime`;
  `seqNr` remains the authoritative source order.

Location ID and Registration ID are interface representations, not universal
event policy. IF-05 defines their serialized shape and common structural
validity. Event/profile/reference-data configuration defines their concrete
allowed values and business meaning.

## Registration ID boundary

A registration TimingData record carries one canonical Registration ID in
`regId`.

The current IF-05 contract treats it as a non-empty provider-neutral string.
Source-specific identities such as RFID/tag identifiers or team/reference-data
identifiers are resolved **before** the registration is committed. They are not
additional fields in the current IF-05 registration record.

IF-05 does not define participant categories, number ranges, tag encoding,
reference-data mappings or other event-specific Registration ID policy.

Registration ID is separate from the record key `(nodeId, seqNr)`.

## Time representation

The canonical development-v1 timestamp representation is:

```text
YYYY-MM-DDTHH:mm:ss[.fraction]Z
```

Rules:

- the value is an absolute UTC instant and always uses literal `Z`;
- fractional seconds are optional and, when present, contain **1 to 9 digits**;
- canonical writer output omits the fractional part for a whole second;
- unnecessary trailing fractional zeroes are removed;
- the represented instant is preserved at up to nanosecond resolution;
- offsets such as `+02:00`, implicit local time and timezone names are not
  canonical IF-05 values;
- chronological comparison is by represented absolute instant, not by source
  sequence;
- another concrete representation may encode time differently but must preserve
  the same absolute instant.

Examples:

```text
2026-10-01T12:00:00Z
2026-10-02T10:57:43.444Z
2026-10-02T10:57:43.444123789Z
```

`recTime` is metadata captured when the definitive record is materialized for
the commit attempt. It is not itself a durable-commit marker and need not equal
the exact physical completion time of a storage write. Source sequence remains
authoritative for record order when wall-clock time is corrected.

## JSON Lines file encoding

The default/reference development-v1 file is append-only UTF-8 JSON Lines
(`.jsonl`) and contains records from exactly one `nodeId` source stream.

Rules:

- encoding is UTF-8 without a byte-order mark (BOM);
- there is no file header, footer or comment syntax;
- `v` is carried by every record;
- one complete TimingData JSON record is written per physical line;
- all records in one canonical file use the same `nodeId`;
- canonical writer line ending is **LF** (`0x0A`);
- a reader may accept **CRLF** (`0x0D 0x0A`);
- a line terminator completes the record boundary;
- valid JSON bytes at EOF without LF/CRLF form an incomplete trailing record and
  are not committed;
- blank lines are invalid input, not implicit sequence positions;
- every complete line is independently JSON-decodable;
- canonical writer output is compact single-line JSON;
- insignificant JSON whitespace and member ordering are not semantic to readers;
- canonical writer member order is
  `v,nodeId,seqNr,locId,recType,time,regId,code,recTime`;
- committed records are append-only and are not rewritten;
- valid complete records before an incomplete trailing line remain readable;
- recovery/import validates Node ID and sequence ordering and reports gaps,
  duplicates or regressions explicitly.

The exact filename, directory mapping, rotation/retention policy and filesystem
durability primitive are deployment/software-item concerns. IF-05 does not
require every TimingData representation to use a `.jsonl` file.

## Reference JSON examples

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

Reserved future revoke examples (not current executable behaviour):

```json
{"v":1,"nodeId":"Test","seqNr":4,"locId":24,"recType":"AUTO_REG","time":"2026-10-01T12:00:00Z","regId":"N001","code":["REV"],"recTime":"2026-10-02T11:05:12.123Z"}
{"v":1,"nodeId":"Test","seqNr":5,"locId":24,"recType":"MAN_REG","time":"2026-10-01T11:59:58.25Z","regId":"N003","code":["REV","MAN"],"recTime":"2026-10-02T11:05:14Z"}
```

## Alternative representations

The JSON/JSONL format above is the default/reference representation.

A product/event-specific implementation may use another concrete representation,
for example an existing text, fixed-field or proprietary format. That
representation does not need to use the same filename extension or physical
record framing.

When such data crosses IF-05, it must preserve the common semantics needed to
translate records without silently changing their identity, ordering,
registration meaning or represented instants.

Java provider/factory/codec APIs used to implement this boundary are defined by
SI-01 detailed design, not by IF-05.

## Compatibility and versioning

The default/reference representation uses **integer format versions only**.

Version parity is intentional:

- **odd** values are development/unstable formats;
- **even** values are released/stable formats;
- the current working format is development `v = 1`;
- the first frozen/released contract is expected to become stable `v = 2`;
- a later incompatible development cycle uses `v = 3`, which may later become
  stable `v = 4`;
- decimal/minor values such as `1.1` are not used.

Because v1 is explicitly a development format, its shape may change while the
Step-4 review candidate is being finalized. A v1 reader and writer are expected
to come from the same agreed development baseline.

Within one supported baseline:

- a canonical writer emits only members defined by the IF-05 version it
  implements;
- a reader tolerates additional JSON object members when all required known
  fields remain valid;
- an unknown `recType` in an otherwise supported version is retained/reported
  as unsupported rather than silently reinterpreted as a known type;
- malformed JSON, missing required fields, invalid field types/values, invalid
  `code` combinations and sequence violations are explicit invalid-record
  conditions;
- an unsupported integer `v` is an explicit compatibility failure for semantic
  decoding;
- raw unsupported lines may be retained/exported but are not interpreted using a
  different version's semantics;
- compatible additions do not silently change the meaning of existing members or
  code values.

A stable even-numbered format is not silently redefined. Breaking work starts in
the next odd-numbered development format.

## IF-05 requirements

```{ifreq} Common TimingData v1 record semantics
:id: IF05-REQ-001

Every committed TimingData record shall expose the common semantic values
defined by this IDD. The default/reference representation shall map them to the
development-v1 members defined here.
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

```{ifreq} TimingData v1 registration families
:id: IF05-REQ-004

Development v1 shall support `AUTO_REG` and `MAN_REG` records as defined by
this IDD.
```

```{ifreq} Canonical registration identity
:id: IF05-REQ-005

Registration records shall carry Registration ID rather than a source-specific
identity.
```

```{ifreq} Registration ID v1 semantics
:id: IF05-REQ-006

Development-v1 `regId` shall be a non-empty provider-neutral representation.
Concrete event/profile meanings, allowed values and deployment mappings shall
remain outside IF-05.
```

```{ifreq} Registration source boundary
:id: IF05-REQ-007

Source-specific tag/reference identities shall be resolved to Registration ID
before a registration is committed and shall not replace `regId` in the
current registration record.
```

```{ifreq} Registration code semantics
:id: IF05-REQ-008

`AUTO_REG` add records shall use `code=["ADD"]`. `MAN_REG` add records
shall use `code=["ADD","AUTO"]` for system-assigned time or
`code=["ADD","MAN"]` for operator-entered time. Canonical writer output shall
emit action first.
```

```{ifreq} Canonical reference file encoding
:id: IF05-REQ-009

The default/reference file encoding shall be UTF-8 JSON Lines with LF writer
output and one independently decodable record per complete line.
```

```{ifreq} Incomplete trailing line
:id: IF05-REQ-010

A default/reference file record shall be complete only when its JSON bytes are
followed by an accepted line terminator. An unterminated trailing record shall
not be interpreted as committed.
```

```{ifreq} Alternative representation compatibility
:id: IF05-REQ-011

Alternative representations shall preserve IF-05 record identity, ordering,
registration semantics and represented timestamps when translating to/from the
common semantic contract.
```

```{ifreq} Representation-independent semantics
:id: IF05-REQ-012

The common IF-05 semantics shall not depend on the default/reference JSON/JSONL
representation or on one software implementation of that representation.
```

```{ifreq} Canonical timestamp text
:id: IF05-REQ-013

Canonical development-v1 timestamp text shall use UTC `Z` form with zero
through nine fractional-second digits. Canonical writer output shall omit
unnecessary trailing fractional zeroes while preserving the represented instant.
```

```{ifreq} Sequence range and no-wrap rule
:id: IF05-REQ-014

Development-v1 `seqNr` shall be a positive JSON-safe integer in the range
`1..2^53-1`, shall not wrap and shall not reuse committed values.
```

```{ifreq} Compatible v1 reader behaviour
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

- TimingNode OPEN/CLOSE TimingData representation;
- executable registration revocation/correction behaviour and ambiguity policy;
  v1 only reserves the `REV` representation described above;
- start-procedure record family and payload;
- penalty/correction record families and payloads;
- unknown-registration semantics;
- source/tag provenance fields;
- filename/directory policy, retention, rotation and filesystem-specific
  durability primitives;
- upstream transport/session/reconciliation semantics owned by IF-06;
- further IF-03 resources that create or inspect future record types.

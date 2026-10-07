# TimingData Interchange Interface Design Description (IDD)

Status: draft / development-v1 reference representation

System interface: **IF-05 — TimingData Interchange**



## Purpose

This Interface Design Description defines the current **default/reference
development-v1 representation** of IF-05 TimingData.

The ISD owns the normative TimingData semantics and requirements. This IDD
describes how that contract is represented as compact JSON records in an
append-only JSON Lines file.

This document deliberately does not define Java classes, factories, providers,
threads, queues or storage implementation classes.

## Terms and abbreviations

- **IDD** — Interface Design Description
- **ISD** — Interface Specification Document
- **IF** — system interface
- **JSONL** — JSON Lines
- **TimingData** — committed interchange record model


## Relationship to other documents

This IDD implements the default/reference representation of
`32-05-ISD-timingdata-interchange.md`. The ISD remains the semantic IF-05 contract;
this document defines its current JSON/JSON Lines representation. Software-item design,
reference codecs/stores and compatible consumers use this design without redefining the
IF-05 semantics.

## Design overview

The reference design uses:

- one compact JSON object per TimingData record;
- one complete JSON object per JSON Lines record;
- one Node ID source stream per file;
- monotonically increasing `seqNr`;
- explicit record type in `recType`;
- compact semantic codes in `code`;
- absolute UTC timestamp text;
- per-record integer representation version `v`.

<a id="fig-if05-01"></a>
![TimingData v1 interchange model](../../../raw/prod/docs/assets/architecture/timingdata-interchange-model.svg)

*Figure IF05-01 — IF-05 semantics mapped to development-v1 JSON and JSON Lines.*

## Semantic-to-JSON mapping

| Semantic value | Presence | v1 JSON member |
| --- | --- | --- |
| representation version | Always | `v` |
| Node ID | Always | `nodeId` |
| sequence number | Always | `seqNr` |
| Location ID | Always | `locId` |
| record type | Always | `recType` |
| time | By record type | `time` |
| Registration ID | By record type | `regId` |
| code | By record type | `code` |
| record creation time metadata | Optional | `recTime` |

The stable IF-05 record key `(Node ID, sequence number)` is represented by
`(nodeId, seqNr)`.

## Registration record mapping

### AUTO_REG

Automatic registration add:

```text
recType = AUTO_REG
code    = [ADD]
```

The record type already carries the automatic-registration meaning, so `AUTO`
is not repeated in `code`.

Reserved revoke mapping:

```text
recType = AUTO_REG
code    = [REV]
same regId
same time
```

### MAN_REG

Manual registration using system-assigned time:

```text
recType = MAN_REG
code    = [ADD, AUTO]
```

Manual registration using operator-entered time:

```text
recType = MAN_REG
code    = [ADD, MAN]
```

Reserved revoke mappings:

```text
[ADD, AUTO] -> [REV, AUTO]
[ADD, MAN]  -> [REV, MAN]
```

Canonical writer output places the action (`ADD`, or `REV` when the reserved mapping is enabled) first.
Array order is not semantic to a reader; the valid code combination is.
Duplicate, contradictory or unknown codes for a known record type are invalid.

A revoke record using the reserved mapping repeats the original `regId` and `time`,
receives a new `seqNr` and `recTime`, and never rewrites the original record.

## TimingNode lifecycle record mapping

The development-v1 reference representation maps lifecycle transitions to
dedicated record types:

```text
CLOSED -> OPEN
recType = NODE_OPEN
time    = effective transition instant
locId   = location becoming active
```

```text
OPEN -> CLOSED
recType = NODE_CLOSE
time    = effective transition instant
locId   = location active immediately before close
```

`NODE_OPEN` and `NODE_CLOSE` do not carry `regId` or `code`. The
record type itself contains the lifecycle meaning. `recTime`, when emitted,
remains optional record-creation metadata and does not replace lifecycle
`time`.

An idempotent/already-in-state lifecycle command or a command that fails before
commit produces no lifecycle JSON record.

## Development-v1 record matrix

| Record type | Meaning | Required type-specific data | `code` |
| --- | --- | --- | --- |
| `AUTO_REG` | automatic registration | `regId`, `time` | `["ADD"]`; `["REV"]` reserved |
| `MAN_REG` | manual registration | `regId`, `time` | `["ADD","AUTO"]` or `["ADD","MAN"]`; corresponding REV mapping reserved |
| `NODE_OPEN` | CLOSED -> OPEN lifecycle transition | `time` | absent |
| `NODE_CLOSE` | OPEN -> CLOSED lifecycle transition | `time` | absent |

## Development-v1 JSON contract

Known members use the following JSON types and validation rules.

| Member | JSON type | Presence | v1 design rule |
| --- | --- | --- | --- |
| `v` | integer | Always | exactly `1` for the current development format |
| `nodeId` | string | Always | non-empty Node ID |
| `seqNr` | integer | Always | `1..9007199254740991`; plain decimal; v1 reference-design limit |
| `locId` | integer | Always | positive Location ID representation |
| `recType` | string | Always | identifies the concrete v1 record type |
| `time` | string | By record type | required for `AUTO_REG`, `MAN_REG`, `NODE_OPEN` and `NODE_CLOSE`; canonical time text |
| `regId` | string | By record type | required for `AUTO_REG` and `MAN_REG`; absent for lifecycle records |
| `code` | array of strings | By record type | required for registration records; absent for `NODE_OPEN` and `NODE_CLOSE` |
| `recTime` | string | Optional | canonical record-creation time metadata when emitted |

Canonical writer member order:

```text
v
nodeId
seqNr
locId
recType
time
regId
code
recTime   # when present
```

Validation rules:

- every `Always` member is present and non-null;
- every `By record type` member required by the selected `recType` is present and non-null;
- `Optional` members such as `recTime` may be omitted;
- `nodeId` is not normalized, case-folded or derived by the reference reader/writer;
- the development-v1 `AUTO_REG` mapping accepts exactly `["ADD"]` while REV remains reserved;
- the development-v1 `MAN_REG` mapping accepts `ADD` plus exactly one of `AUTO` or `MAN` while REV remains reserved;
- `NODE_OPEN` and `NODE_CLOSE` require `time` and shall not contain `regId` or `code`;
- readers may accept a valid registration `code` combination in another array order;
- canonical writer output always emits action first;
- `seqNr` remains authoritative source order; no chronological ordering is
  inferred from `time` or `recTime`.

## Timestamp encoding

Canonical development-v1 timestamp text for registration/lifecycle `time`,
and for optional `recTime` when present, is:

```text
YYYY-MM-DDTHH:mm:ss[.fraction]Z
```

Rules:

- literal `Z` represents UTC;
- fractional seconds are optional and contain **1 to 9 digits** when present;
- canonical writer output omits the fractional part for a whole second;
- unnecessary trailing fractional zeroes are removed;
- offsets such as `+02:00`, implicit local time and timezone names are not
  canonical v1 values.

This absolute UTC syntax is a property of the default/reference development-v1
representation. It does not require every conforming TimingData profile to
serialize an absolute timestamp literally. An alternative profile may use a
local event-time representation when its configured codec owns the reversible
translation context required by IF-05.

Examples:

```text
2026-10-01T12:00:00Z
2026-10-02T10:57:43.444Z
2026-10-02T10:57:43.444123789Z
```

`recTime`, when present, is optional record-creation metadata. It is not a
durable-commit marker and is not part of the common IF-05 record envelope.

## JSON Lines file design

The default/reference development-v1 file uses UTF-8 JSON Lines (`.jsonl`) and
contains records from exactly one `nodeId` source stream.

Rules:

- encoding is UTF-8 without BOM;
- there is no file header, footer or comment syntax;
- `v` is carried by every record;
- one complete TimingData JSON object is written per physical line;
- all records in one file use the same `nodeId`;
- canonical writer line ending is **LF** (`0x0A`);
- a reader may accept **CRLF** (`0x0D 0x0A`);
- a line terminator completes the record boundary;
- valid JSON bytes at EOF without LF/CRLF are an incomplete trailing record and
  are not committed;
- blank lines are invalid input;
- every complete line is independently JSON-decodable;
- canonical writer output is compact single-line JSON;
- insignificant JSON whitespace and member ordering are not semantic to readers;
- committed records are append-only and are not rewritten;
- valid complete records before an incomplete trailing line remain readable;
- recovery/import validates Node ID and sequence ordering and reports gaps,
  duplicates or regressions explicitly.

The exact filename, directory mapping, rotation/retention policy and filesystem
durability primitive are outside IF-05. A different TimingData representation
does not have to use `.jsonl`.

## Reference JSON examples

Automatic registration:

```json
{"v":1,"nodeId":"Test","seqNr":1,"locId":24,"recType":"AUTO_REG","time":"2026-10-01T12:00:00Z","regId":"N0001","code":["ADD"],"recTime":"2026-10-02T10:57:43.444Z"}
```

Manual registration using system-assigned time:

```json
{"v":1,"nodeId":"Test","seqNr":2,"locId":24,"recType":"MAN_REG","time":"2026-10-01T12:00:05Z","regId":"N0002","code":["ADD","AUTO"],"recTime":"2026-10-02T10:57:45.1Z"}
```

Manual registration using operator-entered time:

```json
{"v":1,"nodeId":"Test","seqNr":3,"locId":24,"recType":"MAN_REG","time":"2026-10-01T11:59:58.25Z","regId":"N0003","code":["ADD","MAN"],"recTime":"2026-10-02T10:57:46Z"}
```

Reserved revoke examples:

```json
{"v":1,"nodeId":"Test","seqNr":4,"locId":24,"recType":"AUTO_REG","time":"2026-10-01T12:00:00Z","regId":"N0001","code":["REV"],"recTime":"2026-10-02T11:05:12.123Z"}
{"v":1,"nodeId":"Test","seqNr":5,"locId":24,"recType":"MAN_REG","time":"2026-10-01T11:59:58.25Z","regId":"N0003","code":["REV","MAN"],"recTime":"2026-10-02T11:05:14Z"}
```

The Registration IDs above are synthetic test/example data. Four numeric digits
are used so examples remain convenient for later test sets containing up to
2000 teams; IF-05 does not impose that display convention on Registration ID.


TimingNode lifecycle examples:

```json
{"v":1,"nodeId":"A","seqNr":6,"locId":24,"recType":"NODE_OPEN","time":"2026-10-02T11:10:00Z","recTime":"2026-10-02T11:10:00.001Z"}
{"v":1,"nodeId":"A","seqNr":7,"locId":24,"recType":"NODE_CLOSE","time":"2026-10-02T12:05:30.25Z","recTime":"2026-10-02T12:05:30.251Z"}
```

The examples show only successful state transitions. `ALREADY_OPEN`,
`ALREADY_CLOSED`, rejected and failed lifecycle commands do not produce a
reference record.

## Compatibility and versioning design

Development v1 includes explicit per-record representation versioning through
an integer `v` member and uses the odd/even maturity convention below. Both are
design choices of this reference representation, not additional IF-05
requirements.

The default/reference representation uses integer format versions:

- **odd** values are development/unstable formats;
- **even** values are released/stable formats;
- current working format: `v = 1`;
- first frozen/released contract: expected `v = 2`;
- later incompatible development work starts at `v = 3`, then may freeze as
  `v = 4`;
- decimal/minor versions such as `1.1` are not used.

Within one supported baseline:

- a canonical writer emits only members defined by the version it implements;
- a reader tolerates additional JSON members when all required known fields
  remain valid;
- an unknown `recType` in an otherwise supported version is retained/reported
  as unsupported rather than reinterpreted as a known type;
- malformed JSON, missing required fields, invalid field types/values, invalid
  `code` combinations and sequence violations are explicit invalid-record
  conditions;
- an unsupported integer `v` is an explicit semantic-decoding compatibility
  failure;
- raw unsupported lines may be retained/exported but are not interpreted using
  another version's semantics;
- compatible additions do not silently change existing member/code meaning.

A stable even-numbered format is not silently redefined. Breaking work starts in
the next odd-numbered development format.

## ISD requirement realization

| ISD requirement | development-v1 design realization |
| --- | --- |
| IF05-REQ-001 | `nodeId`, `seqNr`, `locId` and `recType` form the common JSON envelope |
| IF05-REQ-002 | Node ID + `seqNr` identify a record when streams are combined |
| IF05-REQ-003 | `seqNr` starts at 1 and advances contiguously per Node ID source stream |
| IF05-REQ-004 | `recType` distinguishes `AUTO_REG` and `MAN_REG` |
| IF05-REQ-005 | registration records carry `regId` and `time` |
| IF05-REQ-006 | `code[]` represents ADD/REV while revoke repeats `regId` + `time` in a new record |
| IF05-REQ-007 | JSON Lines persistence is append-only; an existing committed record is not rewritten |
| IF05-REQ-008 | `NODE_OPEN` and `NODE_CLOSE` represent successful lifecycle transitions in the normal source stream |
| IF05-REQ-009 | lifecycle records carry the transition `locId` and `time` and omit registration-only values |
| IF05-REQ-010 | no lifecycle JSON record is written for no-op/already/rejected/failed transitions |

JSON Lines completion rules, unknown-member handling, integer `v`, the v1
`seqNr` limit, odd/even version-number convention and optional `recTime`
are concrete reference-design choices. They are intentionally not additional
IF-05 requirements.

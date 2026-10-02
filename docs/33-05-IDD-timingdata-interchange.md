# TimingData Interchange Interface Design Description (IDD)

Status: review candidate / development-v1 reference representation

System interface: **IF-05 — TimingData Interchange**

Implements: `32-05-ISD-timingdata-interchange.md`

## Purpose

This Interface Design Description defines the current **default/reference
development-v1 representation** of IF-05 TimingData.

The ISD owns the normative TimingData semantics and requirements. This IDD
describes how that contract is represented as compact JSON records in an
append-only JSON Lines file.

This document deliberately does not define Java classes, factories, providers,
threads, queues or storage implementation classes.

## Design overview

The reference design uses:

- one compact JSON object per TimingData record;
- one complete JSON object per JSON Lines record;
- one Node ID source stream per file;
- monotonically increasing `seqNr`;
- explicit record family in `recType`;
- compact semantic codes in `code`;
- absolute UTC timestamp text;
- per-record integer representation version `v`.

<a id="fig-if05-01"></a>
![TimingData v1 interchange model](../../../raw/prod/docs/assets/architecture/timingdata-interchange-model.svg)

*Figure IF05-01 — IF-05 semantics mapped to development-v1 JSON and JSON Lines.*

## Semantic-to-JSON mapping

| ISD semantic value | v1 JSON member |
| --- | --- |
| Node ID | `nodeId` |
| sequence number | `seqNr` |
| Location ID | `locId` |
| record family | `recType` |
| effective time | `time` |
| Registration ID | `regId` |
| record/action semantics | `code` |
| recorded time | `recTime` |
| representation version | `v` |

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

Reserved future revoke mapping:

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

Reserved future revoke mappings:

```text
[ADD, AUTO] -> [REV, AUTO]
[ADD, MAN]  -> [REV, MAN]
```

Canonical writer output places the action (`ADD` or future `REV`) first.
Array order is not semantic to a reader; the valid code combination is.
Duplicate, contradictory or unknown codes for a known record type are invalid.

A future revoke record repeats the original `regId` and `time`, receives a
new `seqNr` and `recTime`, and never rewrites the original record.

## Development-v1 record matrix

| Record type | Current add code | Required registration data | Reserved future revoke code |
| --- | --- | --- | --- |
| `AUTO_REG` | `["ADD"]` | `regId`, `time` | `["REV"]` |
| `MAN_REG` | `["ADD","AUTO"]` or `["ADD","MAN"]` | `regId`, `time` | `["REV","AUTO"]` or `["REV","MAN"]` |

## Development-v1 JSON contract

Known members use the following JSON types and validation rules.

| Member | JSON type | Required | v1 design rule |
| --- | --- | --- | --- |
| `v` | integer | every record | exactly `1` for the current development format |
| `nodeId` | string | every record | non-empty Node ID |
| `seqNr` | integer | every record | `1..9007199254740991`; plain decimal; v1 reference-design limit |
| `locId` | integer | every record | positive Location ID representation |
| `recType` | string | every record | `AUTO_REG` or `MAN_REG` in the current slice |
| `time` | string | every record | canonical effective-time text |
| `regId` | string | registration records | non-empty Registration ID |
| `code` | array of strings | registration records | exact valid combination for the selected `recType`; no duplicates |
| `recTime` | string | every record | canonical recorded-time text |

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
recTime
```

Validation rules:

- every required member is present and non-null;
- `nodeId` is not normalized, case-folded or derived by the reference reader/writer;
- `AUTO_REG` currently accepts exactly `["ADD"]`;
- `MAN_REG` currently accepts `ADD` plus exactly one of `AUTO` or `MAN`;
- readers may accept a valid `code` combination in another array order;
- canonical writer output always emits action first;
- `seqNr` remains authoritative source order; no chronological ordering is
  inferred from `time` or `recTime`.

## Timestamp encoding

Canonical development-v1 timestamp text is:

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

Examples:

```text
2026-10-01T12:00:00Z
2026-10-02T10:57:43.444Z
2026-10-02T10:57:43.444123789Z
```

`recTime` is not a durable-commit marker. It records the absolute instant
captured when the definitive record is materialized for the commit attempt.

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

Reserved future revoke examples:

```json
{"v":1,"nodeId":"Test","seqNr":4,"locId":24,"recType":"AUTO_REG","time":"2026-10-01T12:00:00Z","regId":"N0001","code":["REV"],"recTime":"2026-10-02T11:05:12.123Z"}
{"v":1,"nodeId":"Test","seqNr":5,"locId":24,"recType":"MAN_REG","time":"2026-10-01T11:59:58.25Z","regId":"N0003","code":["REV","MAN"],"recTime":"2026-10-02T11:05:14Z"}
```

The Registration IDs above are synthetic test/example data. Four numeric digits
are used so examples remain convenient for later test sets containing up to
2000 teams; IF-05 does not impose that display convention on Registration ID.

## Compatibility and versioning design

The ISD requires explicit per-record representation versioning. Development v1
chooses an integer `v` member and the odd/even maturity convention below. The
odd/even convention is a design choice of this reference representation, not an
additional ISD requirement.

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

| ISD requirement | v1 design realization |
| --- | --- |
| IF05-REQ-001 | required JSON members carry common and family-specific values |
| IF05-REQ-002 | stable key is represented by `(nodeId, seqNr)` |
| IF05-REQ-003 | `seqNr` starts at 1 and advances contiguously in the authoritative file |
| IF05-REQ-004 | `recType` distinguishes `AUTO_REG` and `MAN_REG` |
| IF05-REQ-005..007 | `regId` carries the one canonical registration identity; source-specific identities are not v1 registration members |
| IF05-REQ-008 | `code[]` maps add plus the manual time-source distinction |
| IF05-REQ-009 | every physical JSON line contains one complete self-contained record, including `v` |
| IF05-REQ-010 | LF/accepted CRLF terminates a complete record; unterminated EOF data is incomplete |
| IF05-REQ-011 | semantic-to-JSON mapping provides the reference translation target for alternative representations |
| IF05-REQ-012 | committed JSON Lines are append-only and existing records are not rewritten |
| IF05-REQ-013 | `time` and `recTime` use canonical UTC `Z` text |
| IF05-REQ-014 | `seqNr` is source order; timestamps do not reorder the stream |
| IF05-REQ-015 | readers tolerate additional unknown JSON object members when required known members remain valid |
| IF05-REQ-016 | every record carries integer `v`; unsupported values are not decoded as another version |

The v1 `seqNr` limit of `2^53-1` and the odd/even version-number convention
are concrete reference-design choices. They are intentionally not additional
ISD requirements.

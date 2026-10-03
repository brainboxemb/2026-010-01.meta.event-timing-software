# Web Interface Specification (ISD)

Status: initial working baseline

System interface: **IF-04 — Web Interface**


## Document guide

- **Role:** define the semantic protocol of **IF-04 — Web Interface** for one Web binding/TimingNode.
- **Inputs:** SSSD interface allocation and applicable system use cases.
- **Owns:** Web-interface operations, state/result/failure semantics, ordering and compatibility obligations; not GUI layout or concrete wire names.
- **Downstream:** an optional IF-04 IDD, SI-01 design and conforming Web realizations.
- **Key terms:** `IF` — system interface; `ISD` — Interface Specification Document; `IDD` — Interface Design Description; `OP` — Operation; `SI` — Software Item.

## Purpose

This Interface Specification Document defines the semantic protocol between a
browser-based Web client and one configured **TimingNode** of the
**Timing Point Application** (SI-01).

The interface defines the state, commands, results and ordering that a conforming
Web client can use. It does not define page layout, widgets, styling or other GUI
design.

Concrete URL paths, HTTP/WebSocket methods, payload member names and browser
transport details belong in an optional IF-04 Interface Design Description when
that realization is designed.

## Inputs

IF-04 is allocated by
`31-SSSD-software-system-specification-document.md`.

The first baseline is driven mainly by:

- UC-001 — connect to a registration system;
- UC-002 — configure, open and close a registration point.

## Parties

```text
Browser-based Web client
          |
          | IF-04
          v
Timing Point Application (SI-01)
          |
          v
one configured TimingNode
```

SI-01 owns TimingNode state and command acceptance. The Web client does not own
or duplicate lifecycle business rules.

## Binding and addressing

Each configured TimingNode has one configured Web binding.

The Web binding therefore identifies the TimingNode to which IF-04 commands and
queries apply. A normal IF-04 command does not need to carry a separate
TimingNodeId merely to select the node already identified by that binding.

The binding address/port is presentation configuration and is not part of the
TimingNode domain identity.

A process containing multiple TimingNodes may expose multiple IF-04 bindings.

## Operation identifiers

Operations use the identifier form `IF04-OP-<number>`, where **OP** means
**Operation**. The identifier names a stable semantic interface operation; it is
independent of a concrete HTTP route, message name or other wire representation.

## IF04-OP-001 — Get current TimingNode state

Returns the current state of the TimingNode associated with the Web binding.

The semantic state contains at least:

- TimingNodeId;
- current operational LocationId, or no assigned location;
- lifecycle state `CLOSED` or `OPEN`;
- explicit problem/error state where relevant to operation.

Returned state represents SI-01 application/domain state, not browser-local
presentation state.

## IF04-OP-002 — Open at a location

Input:

- requested `LocationId`.

For a CLOSED TimingNode, applying the requested LocationId and changing lifecycle
to OPEN are **one ordered application/domain operation**.

A conforming IF-04 client shall not implement normal OPEN as two independently
ordered protocol operations:

```text
set LocationId
open
```

Instead, OPEN carries the requested LocationId as part of the same command.

This ensures that another concurrently active presentation client cannot insert a
different location change between selecting the location and opening the
TimingNode.

Successful semantic outcomes include:

- `OPENED`;
- `ALREADY_OPEN`.

The exact result when an OPEN request supplies a different LocationId while the
TimingNode is already OPEN remains an open point.

## IF04-OP-003 — Close

Requests the TimingNode associated with the Web binding to change to CLOSED.

When the TimingNode is OPEN and CLOSE is accepted, the resulting state is `CLOSED`.

A CLOSE request while the TimingNode is already CLOSED is rejected. The semantic
reason may remain available inside SI-01, while a concrete compatibility mapping
may expose only a general failed-request outcome.

A successful state change is visible through subsequent IF-04 state observation.

## Command ordering

Commands received through IF-04 may race with commands received through other
presentation paths.

State-changing work for one TimingNode shall therefore have one
application-owned order. IF-04 shall not expose a partially applied compound
operation.

In particular, IF04-OP-002 has one externally observable ordering point for the
requested LocationId plus the CLOSED-to-OPEN transition.

This specifies external behaviour. It does not prescribe a mutex, worker class or
thread implementation.

## Failure semantics

IF-04 distinguishes at least:

- invalid request value;
- command rejected by current domain state;
- unavailable or busy processing;
- failed processing;
- operation timeout with outcome unknown;
- unexpected internal failure.

A timeout does not mean already accepted work was cancelled. A client can query
current state before deciding whether to retry a state-changing command.

IF-04 requires success and rejection to be distinguishable. A concrete
compatibility mapping may expose less detailed failure information than SI-01
keeps internally. Human-readable text is diagnostic.

## Compatibility

The IF-04 semantic operations, state values and results form the stable contract.

A concrete Web realization may use a compatibility mapping for representation
details such as endpoint names, field names or field encodings/types. Such a
mapping shall preserve the IF-04 semantic meaning and command ordering defined by
this ISD.

Compatible extensions shall not silently change the meaning of existing IF-04
operations, state values or results. A breaking semantic change requires a new
interface version or an explicitly defined compatible migration.

Concrete endpoint names, payload fields, representation types and version
encoding belong to the IF-04 design/configuration layer rather than this ISD.

## IF-04 requirements

```{ifreq} Per-TimingNode Web binding
:id: IF04-REQ-001
:status: D
:derived_from: UC-001, UC-002

IF-04 shall support one configured Web binding per TimingNode. The binding shall
identify the TimingNode to which IF-04 operations apply without making the Web
endpoint part of TimingNode domain identity.
```

```{ifreq} Current TimingNode state
:id: IF04-REQ-002
:status: D
:derived_from: UC-001, UC-002

IF-04 shall expose the bound TimingNode identity, current operational LocationId
when assigned, OPEN/CLOSED lifecycle state and relevant explicit problem state.
```

```{ifreq} Open with LocationId
:id: IF04-REQ-003
:status: D
:derived_from: UC-002

IF-04 OPEN shall carry the requested LocationId and shall represent LocationId
selection plus the CLOSED-to-OPEN transition as one ordered TimingNode operation.
```

```{ifreq} Close operation
:id: IF04-REQ-004
:status: D
:derived_from: UC-002

IF-04 shall provide an explicit CLOSE operation for the bound TimingNode.
```

```{ifreq} Shared TimingNode semantics
:id: IF04-REQ-005
:status: D
:derived_from: UC-002

IF-04 shall use SI-01 TimingNode application/domain semantics rather than own a
separate lifecycle or LocationId state model.
```

```{ifreq} Explicit failure outcome
:id: IF04-REQ-006
:status: D
:derived_from: UC-001, UC-002

Invalid, rejected, unavailable and outcome-unknown operations shall be
distinguishable from successful operations. A concrete compatibility mapping may
reduce the available failure detail.
```

```{ifreq} Compatible Web realizations
:id: IF04-REQ-007
:status: D
:derived_from: UC-001, UC-002

IF-04 shall allow concrete Web realizations to map endpoint names, field names
and representation types while preserving the semantic operations, values,
results and ordering defined by this ISD.
```

## Interface design

An optional `33-04-IDD` may later define the concrete Web realization,
including:

- URL/resource structure;
- HTTP/WebSocket methods;
- request and response payload fields;
- event/update mechanism;
- version encoding;
- browser connection/reconnect behaviour.

Those design choices shall preserve the semantics defined by this ISD.

## Open points

- OPEN with a different LocationId while already OPEN;
- concrete default Web transport and payload design;
- compatibility-mapping mechanism for deployment-specific representation details.

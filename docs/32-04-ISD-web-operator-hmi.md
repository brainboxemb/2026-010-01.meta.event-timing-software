# Web Operator HMI Interface Specification (ISD)

Status: initial working baseline

System interface: **IF-04 — Web Operator HMI**

## Purpose

This Interface Specification Document defines the browser-facing operator interface
provided directly by the **Timing Point Application** (SI-01).

IF-04 is intended for a normal browser or tablet-class browser used near the timing
point. It is distinct from:

- **IF-03 — API**, used by independent software clients such as SI-02 and the Engineering Client;
- the planned **Desktop GUI Application** (SI-02), which is a separate software item and
  communicates with SI-01 through IF-03;
- a possible browser-based engineering/test client that consumes IF-03.

IF-04 defines operator-visible behaviour and interaction semantics. Concrete HTML, CSS,
JavaScript, URL routing, browser transport and rendering design are outside this first ISD
baseline and may be described by a later IF-04 IDD when needed.

## Inputs

IF-04 is allocated by
`31-SSSD-software-system-specification-document.md`.

Its first baseline is driven mainly by:

- UC-001 — connect to a registration system;
- UC-002 — configure/open/close a registration point.

The SI-01 SSD consumes this interface contract and owns the internal implementation.

## Parties

```text
Operator
   |
   v
Browser / tablet browser
   |
   | IF-04 Web Operator HMI
   v
SI-01 Timing Point Application
```

The browser presents SI-01 state and sends operator intent. It does not own or duplicate
TimingNode lifecycle/business rules.

## Binding model

The current SI-01 architecture allocates one Web binding per configured TimingNode.

A deployment with multiple TimingNodes can therefore expose multiple Web bindings/ports.
The browser-facing binding identifies the TimingNode it controls; the operator does not
need to navigate internal TimingSystem structure.

This binding model is a presentation/deployment concern. It does not make a Web port part
of the TimingNode domain identity.

## First operator view

The first useful IF-04 view shows at least:

- TimingNode identity or other clear source identification;
- current operational LocationId, or no assigned location;
- lifecycle state `CLOSED` or `OPEN`;
- connection/current-data state where loss of current state would affect operator action;
- explicit result/error feedback for operator commands.

The interface should stay compact enough for tablet use. Detailed visual layout is an IDD/UI
design concern.

## IF04-OP-001 — View current timing-point state

The operator can view the current state of the addressed TimingNode.

The displayed state comes from SI-01 application/domain state. Browser-local cached values
shall not be presented as current after the interface knows that the connection or state is
stale.

## IF04-OP-002 — Open at a selected location

The operator selects the intended LocationId and requests OPEN as **one operator action**.

The Web interface passes that intent to the same application-level
`open(LocationId)` semantic operation used by other supported presentation adapters.

For a CLOSED TimingNode, location selection and the CLOSED-to-OPEN transition are one
application operation. The Web interface shall not implement normal OPEN as two independent
steps such as:

1. send a location-change command;
2. send a separate OPEN command.

This prevents another presentation client from changing the location in between those two
parts of one operator intent.

After a successful operation the interface shows the TimingNode as OPEN with the accepted
LocationId.

If the command is rejected or its final outcome is unknown, that state is shown explicitly.

The exact behavior of an OPEN request with a different LocationId while the TimingNode is
already OPEN remains aligned with the corresponding unresolved IF-03/application semantic
decision; IF-04 does not invent a separate rule.

## IF04-OP-003 — Close

The operator can request CLOSE for the addressed TimingNode.

After a successful transition the interface shows the node as CLOSED. The last selected
LocationId may remain visible, but later OPEN still carries the LocationId selected for that
new OPEN action.

## Shared application semantics

IF-04 and IF-03 are different interfaces, but they shall not implement different TimingNode
business rules.

Examples:

- OPEN/CLOSE acceptance is decided by SI-01;
- LocationId validity is decided by the shared application/domain logic;
- a browser cannot force a state transition by locally changing displayed state;
- concurrent commands from IF-03, IF-04, Console or RemoteShell are ordered by the same
  SI-01 TimingNode operation semantics.

## Connection and stale-state behaviour

If the Web interface cannot establish current state, or loses its live connection/state
feed, it shall make that condition visible to the operator.

A stale browser view shall not silently present old state as current.

The concrete refresh/reconnect mechanism is a later design concern.

## Error and feedback semantics

Operator feedback distinguishes at least:

- invalid operator input;
- command rejected by current domain state;
- TimingNode unavailable/busy;
- connection unavailable;
- operation result unknown;
- unexpected internal failure.

The interface may present human-readable text, but application acceptance/rejection remains
owned by SI-01 rather than by browser-only rules.

## IF-04 requirements

```{ifreq} Browser-facing operator boundary
:id: IF04-REQ-001
:status: D
:derived_from: UC-001, UC-002

SI-01 shall provide IF-04 as a browser-facing operator interface distinct from IF-03 and
from the separate SI-02 Desktop GUI Application.
```

```{ifreq} Current TimingNode state
:id: IF04-REQ-002
:status: D
:derived_from: UC-001, UC-002

IF-04 shall show the addressed TimingNode's current identification, operational LocationId
when assigned, and OPEN/CLOSED lifecycle state.
```

```{ifreq} Open with selected LocationId
:id: IF04-REQ-003
:status: D
:derived_from: UC-002

IF-04 shall let the operator select a LocationId and request OPEN as one operator action
mapped to one SI-01 `open(LocationId)` application operation.
```

```{ifreq} No two-command OPEN workflow
:id: IF04-REQ-004
:status: D
:derived_from: UC-002

IF-04 shall not require normal operator OPEN to be implemented as a separate LocationId
update followed by an independently ordered OPEN command.
```

```{ifreq} Close operation
:id: IF04-REQ-005
:status: D
:derived_from: UC-002

IF-04 shall let the operator request CLOSE and shall show the resulting CLOSED state when
the transition succeeds.
```

```{ifreq} Explicit stale/error feedback
:id: IF04-REQ-006
:status: D
:derived_from: UC-001, UC-002

IF-04 shall make unavailable, stale, rejected and outcome-unknown conditions explicit rather
than presenting them as successful/current operator state.
```

```{ifreq} Shared SI-01 command semantics
:id: IF04-REQ-007
:status: D
:derived_from: UC-002

IF-04 shall use the same SI-01 TimingNode command semantics as other supported presentation
interfaces and shall not own independent lifecycle/location business rules.
```

```{ifreq} Per-TimingNode Web binding
:id: IF04-REQ-008
:status: D
:derived_from: UC-001, UC-002

The current Web presentation model shall support one configured IF-04 binding per TimingNode
without making the Web endpoint part of TimingNode domain identity.
```

## Relationship to SI-02

The **Desktop GUI Application** (SI-02) is not IF-04.

SI-02 is an independent software item that uses IF-03. Its screen structure and internal
presentation design belong to its own specification/design documents.

IF-04 is the direct browser/tablet HMI exposed by SI-01.

## Open points

- define the exact result/feedback when OPEN is requested with a different LocationId
  while the TimingNode is already OPEN;
- define the concrete browser realization and interaction layout in an IF-04 IDD when
  implementation approaches.

# Desktop GUI Application Specification Document (SSD)

Status: working draft / non-authoritative

Software item: **SI-02 — Desktop GUI Application**


## Purpose

This combined SSD contains the working SI-02 architecture direction and the first
Draft software-item requirement slice. Requirements mature in this same document; a
separate SRD/SAD pair is not required unless that split later has a clear engineering
benefit.

## Terms and abbreviations

- **SSD** — Software Specification Document
- **SI** — Software Item
- **SSSD** — Software System Specification Document
- **ISD** — Interface Specification Document
- **IDD** — Interface Design Description


## Relationship to other documents

The SI-02 specification consumes:

- `31-SSSD-software-system-specification-document.md` for SI-02 allocation and software-system constraints;
- `32-03-ISD-application-control-status.md` for the SI-01/SI-02 API contract;
- applicable parent/external-system inputs registered by `20-EXT-external-system-inputs.md` where an obligation is allocated directly to SI-02;
- `33-03-IDD-api-http-websocket.md` for the current IF-03 HTTP/JSON + WebSocket realization.

`30-UC-system-use-cases.md` provides system-level operational traceability. A separate software-item use-case document is optional and should be introduced only if decomposing GUI-specific actor/goal behaviour makes the SSD clearer. Its document range is assigned when such documents are actually introduced.

The SIP may schedule SI-02 work but is not requirement/design authority.

## Software-item requirements status

The first SI-02 software-item requirements are **Draft**. They establish the
technology-independent public-interface and connection/recovery baseline needed before
selecting a GUI toolkit, runtime or packaging model.

:::{req} Use only the public SI-01 interface boundary  
:id: SI02-REQ-001  
:status: D  
:derived_from: UC-008, IF03-REQ-001, IF03-REQ-007  

For normal monitoring and operator control, SI-02 shall communicate with SI-01
through the system-defined IF-03 boundary. SI-02 shall not require direct access
to SI-01 process memory, internal Java classes/objects or private runtime files.
:::

:::{req} Select endpoint and expose connection state  
:id: SI02-REQ-002  
:status: D  
:derived_from: UC-001, UC-008, IF03-REQ-002, IF03-REQ-009  

SI-02 shall allow an operator to select or configure the SI-01 endpoint it uses
and shall visibly distinguish at least disconnected, connection/synchronisation
in progress and usable live state. A view that has not completed synchronisation
shall not be presented as live.
:::

:::{req} Show connected application identity  
:id: SI02-REQ-003  
:status: D  
:derived_from: UC-001, UC-008, IF03-REQ-003  

After connecting to SI-01, SI-02 shall obtain and display the connected
application/version identity provided through IF-03 so the operator can identify
the system instance being operated.
:::

:::{req} Present current TimingNode operational status  
:id: SI02-REQ-004  
:status: D  
:derived_from: UC-001, UC-008, IF03-REQ-004, IF03-REQ-005, IF03-REQ-011, IF03-REQ-017  

For each TimingNode exposed through IF-03, SI-02 shall present its current
identity, optional operational LocationId, lifecycle state and explicit problem
state when present. The displayed state shall come from SI-01 rather than from a
GUI-owned lifecycle model.
:::

:::{req} Mark disconnected cached state as stale  
:id: SI02-REQ-005  
:status: D  
:derived_from: UC-001, UC-008, IF03-REQ-006, IF03-REQ-021  

When the live IF-03 connection is lost, SI-02 shall make clear that previously
displayed status/history is stale or disconnected and shall not continue to
present cached information as current live state.
:::

:::{req} Rebuild baseline before declaring the view live  
:id: SI02-REQ-006  
:status: D  
:derived_from: UC-008, IF03-REQ-006, IF03-REQ-014, IF03-REQ-016  

After initial connection or reconnect, SI-02 shall rebuild the current status and
the committed LogBook history required for its view before declaring that view
live. Where history and later live delivery overlap, SI-02 shall use the stable
TimingData source identity (Node ID plus sequence number) to avoid presenting the
same committed record twice.
:::

:::{req} Present committed registration history and live updates  
:id: SI02-REQ-007  
:status: D  
:derived_from: UC-008, IF03-REQ-014, IF03-REQ-015  

SI-02 shall be able to present committed registration history and later
committed registration updates delivered through IF-03. It shall not present an
uncommitted command/request result as if it were committed TimingData.
:::

:::{req} Execute lifecycle control with explicit outcome  
:id: SI02-REQ-008  
:status: D  
:derived_from: UC-002, UC-008, IF03-REQ-008, IF03-REQ-011  

SI-02 shall support the IF-03 OPEN-at-location and CLOSE operations made
available for normal operator control and shall present the operation outcome
separately from the resulting observed state. If connectivity is lost after a
request was submitted but before its outcome can be confirmed, SI-02 shall keep
that outcome visibly unknown until resynchronisation establishes the current
state.
:::

## Software-item architecture

Software item: **Desktop GUI Application** (SI-02)

This SSD describes the working architecture direction for the Desktop GUI Application. The GUI is a separate software item from the **Timing Point Application** (SI-01) and communicates with it through system-defined network interfaces.

The GUI provides an operator-facing desktop application for monitoring and controlling the timing application.

The GUI must be able to connect to a timing application running:

- locally during development;
- in a public reference/test application;
- remotely on a Raspberry Pi target;
- remotely on another Windows/Linux host where applicable.

It must not depend on in-process Java calls, internal runtime classes or direct access to timing-application files.

## Software-item relationship

```text
Software item 02
Desktop GUI Application
        |
        | system-defined application-control/status interface
        | current IF-03 HTTP/JSON + WebSocket realization
        v
Software item 01
Timing Point Application
        |
        +-- local development host
        +-- Raspberry Pi Zero target
        +-- Windows/Linux target
```

The transport and message contracts ultimately belong in a system-level ISD rather than being owned by either software item.

## Relationship to the current JavaFX test client

The current JavaFX test client is an engineering/manual-integration tool for IF-03. It is
**not SI-02** and does not select the GUI toolkit, runtime or packaging for SI-02.

## Minimum capability baseline

The minimum SI-02 capability baseline is deliberately small and validates the
software-item/interface boundary:

- configure/select a timing-application endpoint;
- connect/disconnect;
- query/display application version;
- show connection state;
- show the connected application identity;
- show current TimingNode status;
- show stale/disconnected state explicitly;
- reconnect and rebuild current status/history before treating the view as live.

This baseline is sufficient to verify that the GUI can operate against a Timing Point
Application across the supported network boundary without requiring operational timing
controls to be present in the same capability set.

## Additional operator capabilities

As allocated system requirements and interface contracts mature, SI-02 may include:

- open/close a timing system;
- RFID power and reinitialisation controls;
- start procedure control;
- registration overview;
- manual registration;
- penalty registration/revocation;
- ready-team overview/control;
- device/network/backoffice status and diagnostics.

These operations are handled by the **Timing Point Application** (SI-01). The GUI sends commands and presents state; it does not duplicate timing-domain business rules.

## Operator interface ownership

The **Desktop GUI Application** (SI-02) owns its desktop screen structure, navigation,
presentation models and interaction design within this SSD and any focused detailed design.
It is not IF-04.

**IF-04 — Web Interface** is the separate browser/tablet interface exposed directly by
SI-01.

## Software-to-software interface

SI-02 communicates with SI-01 through **IF-03 — API**.

The semantic contract is defined by
`32-03-ISD-application-control-status.md`. The current HTTP/JSON + WebSocket realization
is defined by `33-03-IDD-api-http-websocket.md`.

The same IF-03 interface is also used by engineering/test tools. A browser-based test
client may consume IF-03 without becoming SI-02 or IF-04.

## Internal GUI layering

A possible GUI structure is:

```text
GUI bootstrap
    |
    +-- presentation / views
    |
    +-- presentation models / view models
    |
    +-- GUI application services
    |      connection state
    |      status subscriptions
    |      command execution
    |
    +-- timing-application client port
           |
           +-- HTTP/WebSocket implementation
           +-- fake/stub implementation for GUI tests
```

Views should depend on presentation/application models rather than directly on HTTP/WebSocket libraries. This allows most GUI behaviour to be unit tested without a live timing application.

## Testability

The GUI should support at least three test levels:

1. **unit tests** using a fake timing-application client;
2. **integration tests** against the public reference/test application;
3. **system tests** against a real timing application, including one running on a Raspberry Pi.

The fake client should be able to produce version/status changes, disconnects, stale state and command results deterministically.

## Technology choices still open

- desktop GUI toolkit/framework;
- packaging/distribution model;
- HTTP/WebSocket client library compatible with the selected GUI runtime;
- whether the GUI uses the same Java baseline as the **Timing Point Application** (SI-01) or can use a newer runtime;
- configuration storage for known endpoints;
- authentication/credential storage;
- update mechanism.

The Raspberry Pi Java-8 constraint applies to the headless timing application. It does **not automatically require** the desktop GUI to use Java 8; that should be a separate software-item decision.

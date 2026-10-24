# Engineering Desktop Client Specification Document (SSD)

Status: working draft / non-authoritative

Software item: **SI-02 — Engineering Desktop Client**

## Purpose

This SSD defines the current requirements and architecture direction for the
**Engineering Desktop Client (SI-02)**.

SI-02 is a reusable desktop software item for development, integration,
commissioning, diagnostics and system testing. It is intended to be packaged and
used by multiple people rather than serving as a disposable local test utility.

Normal field/operator interaction remains the SI-01-owned **IF-04 Web Interface**.
SI-02 is therefore not the normal operator GUI.

## Relationship to other documents

SI-02 consumes:

- `31-SSSD-software-system-specification-document.md` for software-item allocation;
- `30-UC-system-use-cases.md`, especially UC-009;
- `32-03-ISD-application-control-status.md` for IF-03 semantics;
- `33-03-IDD-api-http-websocket.md` for the current HTTP/JSON + WebSocket realization;
- applicable external inputs registered by `20-EXT-external-system-inputs.md`.

`50-SDE-03-development-client.md` records the selected desktop technology,
workbench and development/client-service baseline. `70-02-SUM-engineering-client.md`
provides downstream user instructions for the Engineering Client. The SIP schedules
the work. None of these documents replaces this software-item specification.

## Software-item role

SI-02 has its own requirements, architecture baseline, build/runtime/package,
version identity and verification activities.

It may be used:

- by developers while building SI-01 and its integrations;
- by engineers during commissioning and diagnostics;
- by system testers as the real desktop client in running-system verification;
- by repeatable scripted engineering workflows through the same client/application services.

SI-02 does not own TimingNode or TimingData domain state. SI-01 remains
authoritative and SI-02 uses supported external interfaces.

## Software-item requirements

The initial SI-02 requirements are Draft and trace to UC-009.

:::{req} Use only supported public SI-01 boundaries
:id: SI02-REQ-001
:status: D
:specifies: UC-009
:depends_on: IF03-REQ-001, IF03-REQ-007

For live engineering, integration, commissioning and system-test operation,
SI-02 shall communicate with SI-01 through supported public interfaces. SI-02
shall not require direct access to SI-01 process memory, internal Java
classes/objects or private runtime files.
:::

:::{req} Select target and expose connection state
:id: SI02-REQ-002
:status: D
:specifies: UC-009
:depends_on: IF03-REQ-002, IF03-REQ-009

SI-02 shall allow the user or test setup to select or configure the SI-01
target and shall visibly distinguish disconnected, synchronising and usable
live state. A view that has not completed synchronisation shall not be
presented as live.
:::

:::{req} Show connected application identity
:id: SI02-REQ-003
:status: D
:specifies: UC-009
:depends_on: IF03-REQ-003

After connecting to SI-01, SI-02 shall obtain and display the connected
application/version identity provided through IF-03.
:::

:::{req} Present current TimingNode operational status
:id: SI02-REQ-004
:status: D
:specifies: UC-009, UC-022
:refines: SI01-REQ-024
:depends_on: IF03-REQ-004, IF03-REQ-005, IF03-REQ-011, IF03-REQ-017

For each TimingNode exposed through IF-03, SI-02 shall present its identity,
optional operational LocationId, lifecycle state and explicit problem state
when present. The displayed state shall come from SI-01 rather than from an
SI-02-owned lifecycle model.
:::

:::{req} Mark disconnected cached state as stale
:id: SI02-REQ-005
:status: D
:specifies: UC-009, UC-022
:refines: SI01-REQ-025
:depends_on: IF03-REQ-006, IF03-REQ-021

When the live IF-03 connection is lost, SI-02 shall make clear that previously
displayed status/history is stale or disconnected and shall not present cached
information as current live state.
:::

:::{req} Rebuild baseline before declaring the view live
:id: SI02-REQ-006
:status: D
:specifies: UC-009, UC-022
:refines: SI01-REQ-025
:depends_on: IF03-REQ-006, IF03-REQ-014, IF03-REQ-016

After initial connection or reconnect, SI-02 shall rebuild current status and
the committed history required for its view before declaring that view live.
Where baseline history and later live delivery overlap, SI-02 shall use stable
source identity to avoid presenting the same committed record twice.
:::

:::{req} Present committed registration history and live updates
:id: SI02-REQ-007
:status: D
:specifies: UC-009, UC-022
:refines: SI01-REQ-042
:depends_on: IF03-REQ-014, IF03-REQ-015

SI-02 shall present committed registration history and later committed updates
delivered through IF-03. It shall not present an uncommitted command/request
result as committed TimingData.
:::

:::{req} Execute engineering controls with explicit outcome
:id: SI02-REQ-008
:status: D
:specifies: UC-009, UC-023
:refines: SI01-REQ-040, SI01-REQ-026
:depends_on: IF03-REQ-008, IF03-REQ-011

SI-02 shall support the IF-03 lifecycle and engineering operations made
available to the client and shall present operation outcome separately from
resulting observed state. If connectivity is lost after submission but before
the outcome can be confirmed, SI-02 shall keep that outcome visibly unknown
until resynchronisation establishes current state.
:::

:::{req} Display connected IF-03 engineering capabilities
:id: SI02-REQ-009
:status: D
:specifies: UC-009
:depends_on: IF03-REQ-012

After the IF-03 baseline synchronises, SI-02 shall present the capability
identities and their authoritative `supported` and `enabled` values from the
connected SI-01, including unrecognised IDs. Before retrieval or after connection
loss, the display shall distinguish unknown/stale capability state from an
explicitly disabled capability. UI controls may depend on capabilities but shall
not replace the diagnostic list.
:::

:::{req} Support explicit client-side Lua engineering scripts
:id: SI02-REQ-010
:status: D
:specifies: UC-009
:depends_on: IF03-REQ-012, IF03-REQ-024

SI-02 shall execute explicitly started local Lua scripts through a documented,
limited client-facing engineering API. Client-local operations shall not depend
on SI-01's optional simulation capability; simulated-tag requests shall only
execute when SI-01 advertises their enabled IF-03 capability. Stopping a script
shall prevent future submissions but cannot reverse accepted server requests.
:::

:::{req} Simulate the Central System upstream peer through supported transports
:id: SI02-REQ-011
:status: D
:specifies: UC-009

SI-02 shall provide an engineering-only Central System Simulator for IF-06
UpstreamData semantics. The simulator shall own Central-side RaceData source
sequence state per NodeId, inspect and react to ACK/REQ/SYNC, request retained
TimingData and answer PING requests. It shall communicate through supported
external transports and shall not call SI-01 domain objects directly.

For deterministic ST-2 operation the simulator shall use the existing IF-03
event WebSocket in `role=upstream` mode as one full-duplex connection. A later
RabbitMQ transport may be selected for ST-3 without changing the simulator's
semantic UpstreamData state model.
:::

## Software-item architecture

The principal boundary is:

```text
JavaFX / BentoFX views ----+
                           |
Lua scripting -------------+--> SI-02 client/application services --> IF-03 --> SI-01
                           |
tests / fakes -------------+

Backend pane / tests
        |
        v
CentralSystemSimulator
        |
        +--> IF-03 Central transport --> ApiEventClient role=upstream --> SI-01
        |
        +--> RabbitMQ Central transport (ST-3, later) --> broker --> SI-01
```

Connection/session lifecycle, baseline synchronisation, live-event buffering
and reconciliation, command execution, raw-message context and target/system
state belong below JavaFX controls and docking objects.

The `CentralSystemSimulator` is a client/application service, not UI-owned
protocol state. It owns the semantic Central-side UpstreamData model and delegates
wire/session mechanics to a selected transport. For ST-2 the normal
`ApiEventClient` connection is opened at `/api/v1/events?role=upstream`; that
single WebSocket still receives the normal STATUS_SNAPSHOT/event flow and also
carries UpstreamData in both directions.

A connected timing system is represented as an **instance-scoped client
context**, not global UI state. The first workbench may still present one
primary system.

## Selected desktop baseline

| Concern | Selected baseline |
| --- | --- |
| Runtime | Java 21 |
| UI | JavaFX 21 |
| Workbench | BentoFX 0.16.0 |
| Styling | application-owned JavaFX CSS |
| Optional theme layer | Transit where useful; not architecture-critical |
| HTTP/JSON | JDK `java.net.http.HttpClient` |
| WebSocket | JDK `java.net.http.WebSocket` |
| JSON | Jackson |
| Build | Maven |
| First Windows distribution | self-contained `jpackage` application image |
| Module model | classpath/non-JPMS initially |

Installer/update machinery and JPMS are later decisions driven by actual need.

## Deployment and repository boundary

SI-02 runs on engineering, commissioning and system-test workstations. It may
connect to SI-01 on the same host, a development machine or a field target.

The implementation may remain co-located with SI-01 in the current Java
repository while the two evolve together. Repository co-location does not
remove the SI-02 software-item boundary.

## Relationship to IF-04 Web

**IF-04 Web Interface** remains the normal browser/tablet operator interface
exposed by SI-01.

SI-02 may expose richer engineering-only capabilities such as raw protocol
inspection, negative-path controls, simulation, Remote Shell, device logs and
client logs.

## Verification and system-test role

SI-02 shall support:

1. unit tests of client/application services using fakes;
2. deterministic presentation/view-model tests;
3. integration tests against public SI-01 interfaces;
4. running-system tests using the real packaged SI-02 where GUI behaviour is
   part of the evidence.

Step 6 V01 uses the real SI-02 for the revoke/DELETED/restart/reconnect GUI
scenario. Headless verification does not replace that UI evidence.

## Client-side Lua scripting

SI-02 provides an embedded, explicitly invoked Lua engineering interface through
the same client/application service layer used by the GUI. The current documented
facade provides client-local output/waits and capability-gated IF-03 simulated-tag
requests. Script execution shall not depend on JavaFX control automation and shall
not add Lua or internal Java access to SI-01.

The supported facade contract, execution design, preconditions, cancellation and
security limitations are defined in `43-02-SDD-01-lua-scripting-design.md`.
Practical use, examples and troubleshooting are documented in
`70-02-SUM-engineering-client.md`. Extended multi-system control and state assertions
are future extensions, not current functions.

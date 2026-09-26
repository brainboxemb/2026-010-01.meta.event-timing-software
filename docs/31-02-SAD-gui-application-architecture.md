# GUI Application Architecture (SAD)

Status: working draft / non-authoritative

Software item: **Desktop GUI Application** (SI-02)

This Software Architecture Document describes the initial architecture direction for the planned desktop GUI. The GUI is a separate software item from the **Headless Timing Application** (SI-01) and communicates with it through system-defined network interfaces.

## Purpose

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
        | HTTP/JSON + WebSocket are current architecture candidates
        v
Software item 01
Headless Timing Application
        |
        +-- local development host
        +-- Raspberry Pi Zero target
        +-- Windows/Linux target
```

The transport and message contracts ultimately belong in a system-level IDD rather than being owned by either software item.

## Relationship to the current JavaFX test client

The current JavaFX test client is an engineering/manual-integration tool for IF-03. It is
**not** the first implementation of SI-02 and does not select the GUI toolkit, runtime or
packaging for SI-02.

## First increment

The first GUI increment should remain deliberately small and validate the software-item/interface boundary:

- configure/select a timing-application endpoint;
- connect/disconnect;
- query/display application version;
- show connection state;
- show central application status;
- show available `TimingSystem` status;
- show stale/disconnected state explicitly;
- reconnect cleanly after temporary network loss.

This is enough to verify that the GUI can operate against a timing application running on a Raspberry Pi before adding operational timing controls.

## Later operator capabilities

As system requirements and IDDs mature, the GUI may add:

- open/close a timing system;
- RFID power and reinitialisation controls;
- start procedure control;
- registration overview;
- manual registration;
- penalty registration/revocation;
- ready-team overview/control;
- device/network/backoffice status and diagnostics.

These operations are handled by the **Headless Timing Application** (SI-01). The GUI sends commands and presents state; it does not duplicate timing-domain business rules.

## GUI IDD as system input

The graphical user interface should be treated as a **system-level interface** rather than allowing the implementation to invent screens ad hoc.

A system-level GUI IDD can define items such as:

- screen/navigation structure;
- information that must be visible;
- operator actions and control availability;
- status/state representations;
- warnings/errors/confirmation behaviour;
- update/staleness behaviour;
- terminology and identifiers;
- interaction flows for open/close/start/RFID recovery and later registration operations.

The future SRD for the **Desktop GUI Application** (SI-02) can reference the applicable GUI-IDD clauses as requirements instead of copying the interface definition into the software-item requirements.

## Software-to-software interface IDD

A separate system-level IDD should define the communication interface between the **Desktop GUI Application** (SI-02) and **Headless Timing Application** (SI-01).

Current direction:

- HTTP/JSON for commands, queries and initial snapshots;
- WebSocket for live status/data events;
- explicit versioning/compatibility of the interface;
- connection/reconnection semantics;
- authentication/authorisation when defined;
- stale-data behaviour;
- errors/result semantics.

The same interface is also used by engineering/test tools. A small browser-based test client may consume it later without becoming another software item.

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
- whether the GUI uses the same Java baseline as the **Headless Timing Application** (SI-01) or can use a newer runtime;
- configuration storage for known endpoints;
- authentication/credential storage;
- update mechanism.

The Raspberry Pi Java-8 constraint applies to the headless timing application. It does **not automatically require** the desktop GUI to use Java 8; that should be a separate software-item decision.

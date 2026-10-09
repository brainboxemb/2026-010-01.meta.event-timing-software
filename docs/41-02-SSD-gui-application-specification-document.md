# Withdrawn Desktop GUI Application specification record

Status: **withdrawn — former SI-02 operator-desktop allocation is no longer active**

Former software item: **SI-02 — Desktop GUI Application**

## Decision

The earlier architecture allocated a separate operator-facing Desktop GUI Application
in addition to the browser/operator path through IF-04.

That allocation is withdrawn.

Normal field/operator interaction is owned by the SI-01 **IF-04 Web Interface**.
The desktop application direction is the **Engineering Client**: development,
integration and diagnostic tooling that exercises supported public boundaries such as
IF-03. It is not promoted to another product software item merely because it has a
substantial desktop UI.

The software-item identity **SI-02** and use-case identity **UC-008** are retained as
historical identifiers and shall not be reused for unrelated future items.

## Former Draft requirements

The former Draft requirements `SI02-REQ-001` through `SI02-REQ-008` were created
while the separate operator-desktop allocation was still assumed.

They were never promoted beyond Draft and are now withdrawn with that allocation.
They are not active product requirements and must not be used as authority for
implementation or verification.

Several underlying behaviours remain useful for the Engineering Client and are already
owned by public-interface contracts and engineering-tool design, including:

- use of public IF-03 rather than SI-01 internals;
- endpoint selection and explicit connection/synchronisation state;
- application/version identity;
- TimingNode status;
- stale/disconnected presentation;
- reconnect/history rebuild;
- committed registration/history presentation;
- explicit command outcomes.

Those behaviours belong in the applicable IF-03 requirements plus
`50-SDE-03-development-client.md` and UC-009. They do not require a separate
operator-desktop software item.

## Current authority

Use:

- `30-UC-system-use-cases.md` — UC-001/UC-002 for normal operator behaviour and
  UC-009 for Engineering Client behaviour;
- `31-SSSD-software-system-specification-document.md` — current software-item and
  system-interface allocation;
- `32-03-ISD-application-control-status.md` and
  `33-03-IDD-api-http-websocket.md` — IF-03 contract/design;
- `32-04-ISD-web-interface.md` — normal browser/operator interface;
- `50-SDE-03-development-client.md` — Engineering Client architecture and UI baseline;
- `11-SIP-software-implementation-plan.md` — current implementation sequencing.

This file remains only to make the withdrawn allocation explicit and to preserve
review history. It is not an active software-item specification.

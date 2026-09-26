# Web Operator Application Architecture (SAD)

Status: working draft / non-authoritative

Software item: **Web Operator Application** (SI-03)

This Software Architecture Document describes the React-based browser/iPad **Web Operator Application** (SI-03) as a separate software item. The application is delivered by the **Headless Timing Application** (SI-01) over HTTP but executes in the browser and communicates with the timing system only through system-defined interfaces.

## Responsibility

The **Web Operator Application** (SI-03) provides a browser-based operational user interface for a timing system.

Expected responsibilities include:

- load and run in a modern browser/iPad Safari environment;
- connect to the **Headless Timing Application** (SI-01) over HTTP/WebSocket;
- show application/timing-system/subsystem status;
- show registration data and relevant local timing information;
- open and close a logical timing system when authorised;
- initiate the local start procedure when authorised;
- show/manage ready-team state where applicable;
- later support manual registration and penalty operations where authorised;
- make disconnected/stale state visible to the operator.

Registration and timing-domain state remain in the **Headless Timing Application** (SI-01).

## Deployment model

The compiled React application is intended to be served as static content by the **Headless Timing Application** (SI-01):

```text
Timing Application (SI-01)
   |
   | HTTP: HTML/JS/CSS bundle
   v
browser / iPad
Web Operator Application (SI-03)
   |
   | HTTP commands/queries
   | WebSocket status/events
   v
Timing Application (SI-01)
```

Serving the bundle from the **Headless Timing Application** (SI-01) simplifies local deployment and ensures the browser can reach the same endpoint even when the wider internet/backoffice is unavailable.

The exact JavaScript/React build toolchain and browser-support baseline remain open.

## Interface boundary

The web application consumes the same system-level application command/query/event semantics as other external clients where practical.

HTTP is the current direction for:

- loading the application;
- initial state/query retrieval;
- operator commands;
- explicit request/response operations.

WebSocket is the current direction for:

- live status updates;
- registration/event updates;
- ready-team/data updates;
- connection/staleness indication.

The browser must not bypass the **Headless Timing Application** (SI-01) by accessing its files or internal Java classes directly.

## State ownership

The web application may maintain presentation/cache state, but the current timing state remains in the **Headless Timing Application** (SI-01).

On connect/reconnect the web application should be able to obtain a complete current state/snapshot before applying subsequent live updates.

This is especially important after:

- browser refresh;
- Wi-Fi interruption;
- iPad sleep/wake;
- WebSocket reconnect;
- SI-01 restart.

## Offline and degraded behaviour

The browser client itself is not required to become a second autonomous timing system.

When its connection to the Headless Timing Application is lost it should:

- clearly show disconnected/stale state;
- stop presenting cached operational data as current without indication;
- avoid pretending commands succeeded when acknowledgement was not received;
- reconnect/resynchronise when the timing application becomes reachable again.

The timing application may continue local RFID/CAN/registration operation while the browser is disconnected.

## Security boundary

Authentication, authorisation and transport security need system-level requirements/IDD definition.

The web application should not contain long-lived secrets that are inappropriate for browser delivery. Operator permissions should be enforced by the **Headless Timing Application** (SI-01) rather than trusted only to disabled/hidden UI controls.

## Relationship to system IDDs and SRD

A future software-item requirements document is expected under the software-item-03 requirement family, for example:

```text
20-03-SRD-web-operator-application-requirements.md
```

Likely system-level interface inputs include:

- application interface IDD between the **Web Operator Application** (SI-03) and **Headless Timing Application** (SI-01);
- WebSocket/live-event portions of that interface;
- operator/HMI IDD describing required information and operator actions.

The SRD should reference those system-owned interface obligations rather than duplicate them.

## Verification direction

Early verification should prove at least:

- bundle can be served by the **Headless Timing Application** (SI-01);
- application can load on a normal desktop browser and representative iPad/Safari environment;
- version/status can be displayed from the Headless Timing Application;
- disconnect/stale state is visible;
- reconnect obtains a complete fresh state before normal live updates resume;
- commands use the system interface and receive explicit success/failure responses;
- browser operation does not require live backoffice/internet connectivity while the Headless Timing Application remains locally reachable.

## Open architecture questions

- React/build-tool/version baseline;
- supported browser/iPad versions;
- authentication/session model;
- HTTP/API technology and resource model;
- WebSocket event envelope and revision/sequence semantics;
- whether desktop and browser clients share generated client models or only the system IDD;
- how static assets are versioned/cached across Headless Timing Application upgrades;
- whether the web application is built in the framework/reference repository or a dedicated repository;
- detailed operator screen/navigation design.

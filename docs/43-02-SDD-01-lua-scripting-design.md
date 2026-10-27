# SI-02 Lua Scripting Design (SDD)

Status: working design baseline

Software item: **SI-02 — Engineering Desktop Client**

## Purpose

This SDD explains how the client-side Lua scripting capability of SI-02 is
designed internally. It covers the script execution boundary, Lua-visible
engineering facade, capability gating, cancellation and implementation mapping.

The SI-02 SSD remains the authority for the required behaviour. IF-03 documents
remain authoritative for the external SI-01 protocol and semantics.

## Terms and abbreviations

- **SDD** — Software Design Description.
- **SI-02** — Engineering Desktop Client.
- **IF-03** — Engineering API between SI-02 and SI-01.
- **LuaJ** — embedded Java implementation used to execute the supported Lua subset.

## Relationship to other documents

This SDD elaborates the scripting part of
[41-02 SSD](41-02-SSD-gui-application-specification-document.md), in particular
`SI02-REQ-009` and `SI02-REQ-010`.

The external request/capability semantics remain owned by
[32-03 ISD](32-03-ISD-application-control-status.md) and the concrete HTTP /
WebSocket representation by [33-03 IDD](33-03-IDD-api-http-websocket.md).
[44-02 GPD](44-02-GPD-engineering-client-design-rules.md) defines reusable
SI-02 design/review rules and [50-SDE-03](50-SDE-03-development-client.md)
defines the development/runtime baseline.

[70-02 SUM](70-02-SUM-engineering-client.md) is the user-facing manual. It owns
the practical workflows, examples and troubleshooting for running Lua scripts.
This SDD owns the internal design and the stable Lua-visible facade contract; it
does not duplicate step-by-step user instructions.

## Design scope and ownership

Lua is an **SI-02-local programming interface**. Scripts execute inside SI-02
and reach SI-01 only through the same SI-02 client/application services and
IF-03 boundary used by the GUI.

This design does not create another system IF-xx, does not add Lua to SI-01 and
does not permit scripts to bypass the public client/service boundary and call
SI-01 internals, AntennaManager internals or JavaFX controls directly.

## Detailed design

### Lua-visible facade contract

| Signature | Arguments and result | Design behaviour |
| --- | --- | --- |
| `timing.log(text)` | String-representable value; no result. | Writes to SI-02 Scripts output only. |
| `print(...)` | Lua values; no result. | Joins arguments with tabs and writes to Scripts output. |
| `timing.now([offsetSeconds])` | Optional integral seconds; canonical UTC timestamp text. | Uses the Engineering Client clock; e.g. -600 means ten minutes before now. |
| `timing.sleep(ms)` | Integral 0..60000 ms; no result. | Interruptible client-local delay. |
| `timing.simulate(regId, profile)` | Non-empty RegistrationId; profile defaults to `normal`; true after accepted request. | Requires enabled `TAG_SCENARIO_SIMULATION`; submits one IF-03 simulation request for the captured node. |
| `timing.batch{...}` | Repeatable batch parameters; returns submitted request count. | Client-side loop over the same `timing.simulate` request path. |
| `central.team_set/del` | RegistrationId/team values. | Mutates global Central-owned Team Mapping state; no selected node required. |
| `central.stage_start_set/del` | StageId, RegistrationId and timestamp. | Mutates Central-owned StageStartTimes for that StageId. |
| `central.stage_start_range{...}` | StageId, prefix/range, start, interval. | Uses the same bulk Central state semantics as the GUI. |
| `central.timing_data_req(fromSeq)` | Source sequence; packet result. | Node-specific IF-06 request using the TimingNode captured at Run start. |
| `client.reset()` | No args. | Disconnects SI-02 stateful boundaries and clears Central simulator state while retaining target configuration. |
| `client.events_connect/disconnect()` | No args. | Controls ordinary IF-03 Events. |
| `client.central_connect/disconnect()` | No args. | Promotes/demotes the same IF-03 event session to/from upstream role. |
| `client.api_available()` | Boolean. | Performs HTTP reachability check; IF-03 HTTP has no persistent connection. |
| `client.status()` / connection predicates | Current booleans. | Inspects API availability and Events/Central connection state. |
| `client.wait(boundary, expected[, timeoutMs])` | api/events/central, boolean, bounded timeout. | Polls current state without automating JavaFX controls. |

`timing.batch` supports:

- `count`: required, 1..10000;
- `from=1`, `to=2000`;
- `order='linear'` or reproducibly seeded `random`;
- `seed=1`;
- `intervalMs=500`, range 0..60000;
- `profile='normal'`, with `simple`, `normal` and `edge` supported.

Generated registration identifiers use `RT-A-%04d`.

The user-facing examples and operational procedure for these calls are maintained in
[70-02 SUM](70-02-SUM-engineering-client.md).

### Internal execution model

- Interpreter: embedded LuaJ 3.0.1, using its Lua 5.2-style language support.
- Script source is UTF-8 text with a maximum size of 128 KiB.
- A file may be opened/dropped or source edited; **Run** is always explicit.
  Dropping a file never starts it automatically.
- Script execution uses one dedicated SI-02 worker and never runs on the JavaFX
  application thread or on SI-01 execution lanes.
- A run may start without a selected TimingNode or active Events session; generic client/Central calls remain available.
- Node-specific calls use the TimingNode captured at Run start.
- A GUI simulation batch and a Lua simulation batch may not run concurrently.
- **Stop** or client shutdown stops further script execution. Intentional Events/Central disconnects do not cancel a script because reconnect testing is a supported use case. A request already accepted by SI-01 cannot be undone by
  cancelling the local script.

### Capability handling

The SI-02 capability view remains source-driven from IF-03 and keeps
`supported` and `enabled` distinct. Unknown or stale capability state is not
treated as `enabled=false`.

Local Lua operations such as `print`, `timing.log` and `timing.sleep` do
not depend on simulated-antenna support. `timing.simulate` and
`timing.batch` require the currently connected SI-01 to advertise
`TAG_SCENARIO_SIMULATION` as enabled.

`DIRECT_REGISTRATION_SIMULATION` is a separate capability and is never used
as a substitute for tag-scenario simulation.

### Visibility and isolation

The interpreter does not expose `io`, `os`, `package`, `require`,
`luajava`, `loadfile`, `dofile`, Java reflection or arbitrary
process/file/network access.

These restrictions reduce accidental misuse but are not a security sandbox.
The supported operational model is trusted, explicitly selected engineering
scripts.

Not exposed by the current facade are multi-system orchestration, node OPEN/CLOSE,
arbitrary IF-03 dispatch or JavaFX-control automation. Connection-state assertions are
implemented through `client.status()` / `client.wait(...)` instead of GUI inspection.

## Failure and recovery behaviour

- Syntax/runtime errors are reported in Scripts output/status.
- A locally unavailable simulation capability is rejected before IF-03
  submission and is not reported as a server rejection.
- An actual IF-03 rejection remains distinguishable as a remote request failure.
- **Stop** or SI-02 shutdown cancels further local execution; connection transitions initiated by the script do not.
- Cancellation never rewrites or rolls back requests already accepted by SI-01.
- An accepted simulation request is not treated as proof of a committed LogBook
  registration.

## Threading and ordering

The script worker is separate from the JavaFX thread. Public-interface I/O uses
the normal SI-02 service/request lanes and results are marshalled back to the UI
through the existing client presentation path.

Within one script run, facade calls are executed in script order. Batch order is
therefore deterministic for `linear` and reproducible for `random` when the
same seed and bounds are used.

## Implementation mapping

The implementation is owned by the SI-02 `test-client` module in the Java
repository.

Key implementation elements include:

- `EngineeringLuaEngine` — LuaJ interpreter setup, facade binding and error handling;
- `EngineeringScriptsPane` — source editor, Run/Stop state and script output;
- `SimulationBatchPlan` — deterministic client-side batch generation;
- SI-02 request/client services — public IF-03 submission boundary.

No Lua dependency is permitted in SI-01.

## Verification considerations

Verification covers:

- local Lua execution without simulation capability;
- successful simulated passages with a composed simulated antenna;
- disabled-capability refusal before request submission;
- distinction between local gating and remote IF-03 rejection;
- cancellation, disconnect and selected-node changes;
- repeatable seeded batch ordering;
- Windows file open/drop and explicit Run/Stop behaviour.

# SI-02 — Lua scripting interface design (SID)

Status: development baseline. Owner: **SI-02 Engineering Client**.

## Purpose and boundary

The Lua API is an **SI-02-local programming interface**, not a new system IF-xx. Scripts execute on an SI-02 worker and interact with SI-01 only through SI-02 client/application services and **IF-03**. Normative IF-03 semantics belong to `32-03-ISD`; HTTP and WebSocket encodings belong to `33-03-IDD`. This document specifies the **Lua-visible client facade**, not server internals, JavaFX controls or a second remote API.

## Execution model

- Interpreter: embedded LuaJ 3.0.1 (Lua 5.2-style language).
- Source is UTF-8 text, up to 128 KiB. A file may be opened/dropped or source edited. **Run is explicit**; file drop is not autorun.
- Execution uses one dedicated client worker; scripts do not run on JavaFX or SI-01 lanes.
- For this initial facade, **Run** requires a LIVE IF-03 baseline and a selected TimingNode. The selected node/target is captured at start. A GUI batch and a script batch may not run concurrently.
- **Stop**, disconnect or changing the selected node cancels further script execution/requests. Already accepted IF-03 commands cannot be undone by cancellation.
- Runtime errors are reported in Scripts Output/status. Server-side rejection is not silently interpreted as successful registration.

## Supported functions

| Signature | Arguments and result | Preconditions/effects |
| --- | --- | --- |
| `timing.log(text)` | Appends a string-representable value; returns no value. | Client-local only. |
| `print(...)` | Joins Lua arguments with tabs and writes to Output. | Client-local only. |
| `timing.sleep(ms)` | Integral milliseconds 0..60000; returns no value. | Interruptible client-local delay. |
| `timing.simulate(regId, profile)` | Nonempty registration ID; optional `profile` defaults `normal`; returns true on accepted IF-03 request. | Requires `TAG_SCENARIO_SIMULATION` enabled; sends one `IF03-OP-013` request for captured TimingNode. |
| `timing.batch{count, from, to, order, seed, intervalMs, profile}` | `count` required, 1..10000; `from=1`, `to=2000`, `order='linear'`, `seed=1`, `intervalMs=500`, `profile='normal'` are defaults; returns number of submitted requests. | Requires `TAG_SCENARIO_SIMULATION`. Generates `RT-A-%04d` IDs; issues repeated `IF03-OP-013` calls via the same client path. |

Supported profiles: `simple`, `normal`, `edge`. `order` is `linear` or reproducibly seeded `random`. The maximum batch length is 10000, and delay per step 0..60000 ms. Accepted simulation requests do **not** prove LogBook commits; scripts must inspect committed data separately when that API becomes available.

```lua
print("Local Lua works")
timing.log("Starting test")
timing.batch{count=10, from=1, to=100, order="random",
             seed=42, intervalMs=500, profile="normal"}
```

## Capability contract

The API's `GET /api/v1/capabilities` returns independent `supported` and `enabled` values. The Engineering Client shall display those actual values, including IDs it does not recognise; absence or stale baseline is **unknown**, not `enabled=false`. A local Lua `print`/`log`/`sleep` operation does **not** need simulated antenna capability. Tag-simulation calls do and must report a clear failure when not enabled. `DIRECT_REGISTRATION_SIMULATION` is a distinct capability and must not be confused with antenna simulation.

## Visibility, safety and limits

No script-visible `io`, `os`, `package`, `require`, `luajava`, arbitrary Java reflection or direct disk/process/network access. These restrictions reduce accidental misuse but **are not a security sandbox**. Only trusted, explicitly selected local engineering scripts may run.

Not available in the current API: multi-system connection management, node open/close, awaiting LIVE from Lua, state assertions, arbitrary IF-03 dispatch or GUI automation. Extend the facade and tests before advertising these functions.

## Verification

Exercise local Lua without simulation capability; exercise successful simulated passages with a simulated antenna; verify disabled capability rejection, cancellation, node/target changes, repeated seeded batch order and Windows file-drop/run/stop behavior. The implementation is in `test-client` of SI-02; no Lua dependency is permitted in SI-01.

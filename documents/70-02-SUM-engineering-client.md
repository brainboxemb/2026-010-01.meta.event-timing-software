<!-- Generated review/output copy. Edit the source document, not this copy. -->

# 70-02 — Engineering Desktop Client Software User Manual

Status: working release-oriented user manual

Software item: **SI-02 — Engineering Desktop Client**

## Purpose

This is the technical software user manual for engineers, developers, integrators
and system testers who use the **Engineering Desktop Client (SI-02)** to connect to,
inspect and exercise a running **Timing Point Application (SI-01)**.

It explains how to start the client, select a target, establish a usable LIVE
baseline, use the engineering workbench and run supported client-side Lua scripts.

This manual does not define product requirements, architecture or detailed design.
Those remain in the SI-02 SSD, applicable interface documents and focused SDDs.

## Terms and abbreviations

- **SUM** — Software User Manual.
- **SI-01** — Timing Point Application.
- **SI-02** — Engineering Desktop Client.
- **IF-03** — engineering API used by SI-02 to communicate with SI-01.
- **LIVE** — SI-02 has rebuilt the required baseline and may present the connected
  TimingNode data as current.
- **LuaJ** — embedded Lua runtime used by the Scripts view.

## Relationship to other documents

This manual is downstream of the current implementation and engineering baseline.

- [41-02 SSD](41-02-SSD-gui-application-specification-document.md) defines SI-02
  requirements and software-item architecture.
- [43-02-SDD-01](43-02-SDD-01-lua-scripting-design.md) defines the detailed design
  of the client-side Lua scripting capability and its supported facade.
- [44-02 GPD](44-02-GPD-engineering-client-design-rules.md) defines reusable SI-02
  UI and interaction design rules.
- [50-SDE-03](50-SDE-03-development-client.md) defines the development environment,
  technology and engineering baseline.
- [32-03 ISD](32-03-ISD-application-control-status.md) and
  [33-03 IDD](33-03-IDD-api-http-websocket.md) remain authoritative for IF-03.

When this manual and an authoritative specification disagree, the specification
or interface document wins.

## Audience and applicability

Use this manual for the current SI-02 development/release baseline. SI-02 is intended
for engineering, commissioning, diagnostics and system-test use. It is **not** the
normal operator interface; normal browser/tablet operation belongs to IF-04 Web.

The current desktop client presents one primary SI-01 target context at a time while
keeping the internal client model suitable for later multi-system use.

## Compatibility matrix

| Concern | Current baseline |
| --- | --- |
| Normal desktop platform | Windows 10/11 |
| Packaged client | self-contained Windows `jpackage` app-image |
| Source/development runtime | JDK 21 |
| UI runtime | JavaFX 21 |
| SI-01 connection | public IF-03 plus Remote Shell and live diagnostics |
| Script runtime | embedded LuaJ 3.0.1 |
| Script files | UTF-8 `.lua`, maximum 128 KiB |

A packaged SI-02 app-image includes its runtime. A JDK 21 installation is needed when
running or building SI-02 from source, not when using the self-contained packaged image.

## Obtain the software

For normal engineering use, prefer the packaged Windows app-image produced from the
intended SI-02 revision.

When working from the Java repository, the Engineering Client implementation is in
`test-client/`. The local packaged image is produced under:

```text
test-client\target\jpackage\EventTimingEngineeringClient\
```

Development/build instructions belong to
[50-SDE-03](50-SDE-03-development-client.md); this manual focuses on using the client.

## Configure

SI-02 reads its normal target and presentation defaults from:

```text
config/engineering-client.properties
```

The default configuration includes the target host and the normal ports for:

- IF-03 HTTP API: `8081`;
- IF-03 Events WebSocket: `8082`;
- Remote Shell: `8023`;
- SI-01 live diagnostics / LoggingServer: `8030`.

The target host remains editable in the client. **Apply target** changes the active
host for the external boundaries without rewriting the configuration file.

Changing the target disconnects stateful connections so they cannot silently remain
connected to the previous host.

Use:

```text
--config=<path>
```

to start SI-02 with another Engineering Client configuration file.

## Start and stop

### Packaged Windows client

Start the packaged **Event Timing Engineering Client** executable from its app-image.

The client does **not** automatically connect to SI-01 at startup. Confirm the target
host before connecting.

Close SI-02 using the normal application/window close action. The client closes its
owned stateful connections as part of shutdown.

### Source/development launch

From the Java repository, with JDK 21 active:

```powershell
.\mvnw.cmd -f test-client\pom.xml clean javafx:run
```

NetBeans Run/Debug uses the checked-in SI-02 actions and starts the client in a
separate child JVM.

## Connect to SI-01

1. Start SI-01 separately.
2. Enter or confirm the SI-01 host in the SI-02 target bar.
3. Use **Connect** to establish the normal engineering connections.
4. Wait until the Timing view progresses through **NOT SYNCED / SYNCING** to
   **LIVE**.
5. Select the intended TimingNode in **Systems** when more than one node is available.

The main **Connect** action checks/opens the normal engineering boundaries. IF-03 HTTP
itself is stateless; its API control therefore reports reachability rather than
pretending to maintain a persistent HTTP connection.

Do not treat a visible TCP connection as proof that the Timing view is ready.
Node-scoped engineering actions and scripts rely on the rebuilt LIVE baseline.

### Re-synchronise

Use **Sync view** when Events is connected and you need to rebuild the current
TimingNode/capability/LogBook baseline.

After disconnect or connection loss, cached data is shown as stale rather than current.

## Workbench overview

The Engineering Client uses a dockable BentoFX workbench. The important views are:

| View | Primary use |
| --- | --- |
| **Systems** | target, TimingNodes, lifecycle/location state and selection |
| **TimingNode** | node lifecycle controls such as Open/Close |
| **API** | application/version diagnostics, capabilities and API checks |
| **Registration** | manual and direct engineering registration controls |
| **Simulation** | simulated-tag scenarios and GUI batches |
| **Scripts** | client-side Lua engineering scripts |
| **Registrations** | interpreted committed registration view |
| **LogBook** | technical committed TimingData history |
| **Raw Data** | raw selected source data |
| **Events** | raw IF-03 event stream |
| **Device Log** | live SI-01 diagnostics |
| **Terminal** | Remote Shell |
| **Client Log** | SI-02-local diagnostics |

All built-in panes are intended to remain available. Tabs may be docked, moved or
detached; **View → Reset layout** restores the default arrangement without changing
the SI-01 state.

## Registration and simulation use

### Manual registration

Use **Registration** for a normal manual ADD. The displayed local civil time is
converted by SI-02 to the canonical UTC timestamp sent through IF-03.

**Now** captures the client time and marks the time source as automatically captured.
Editing the date/time makes the source manual.

### Direct auto-reg

Direct auto-reg is an engineering injection at the TimingNode. It does **not** simulate
an antenna passage. Its availability is controlled by the separate
`DIRECT_REGISTRATION_SIMULATION` capability.

### Simulated tags

The **Simulation** view drives the simulated antenna path. It uses
`TAG_SCENARIO_SIMULATION` and the supported `simple`, `normal` and `edge`
profiles.

The capability must be reported by the connected SI-01. It is determined by the
actual SI-01 composition, including a suitable simulated antenna, not by the name of
the EventData provider.

An accepted simulation request means SI-01 accepted the request. Verify the actual
committed result in **Registrations** or **LogBook**.

## Client-side Lua scripting

### What scripting is for

The **Scripts** view automates repeatable engineering actions from SI-02. Lua runs
locally in SI-02 and uses the same client/application services and IF-03 boundary as
the GUI.

Lua is not executed inside SI-01 and does not provide direct access to SI-01 Java
objects or internal domain components.

### Run a script

1. Connect SI-02 and wait for **LIVE**.
2. Select the intended TimingNode.
3. Open **Scripts**.
4. Either:
   - edit the source directly;
   - choose **Open .lua**; or
   - drop a UTF-8 `.lua` file onto the Scripts pane.
5. Click **Run**.
6. Read script messages and errors in **Output**.
7. Use **Stop** to stop further local script execution.

Opening or dropping a script **never runs it automatically**.

The currently selected TimingNode/target is captured when Run starts. Disconnecting,
changing the selected node or pressing Stop prevents further submissions from that run.
Requests already accepted by SI-01 are not rolled back.

A GUI simulation batch and a Lua simulation batch cannot run concurrently.

### Local smoke test

The local functions do not require simulated-antenna capability:

```lua
print("Engineering Lua is ready")
timing.log("Selected TimingNode is LIVE")

for i = 1, 3 do
    timing.log("Step " .. i)
    timing.sleep(100)
end
```

### Supported Lua facade

#### `print(...)`

Writes its arguments to Scripts Output, separated by tabs.

```lua
print("node", "ready")
```

#### `timing.log(text)`

Writes one value to Scripts Output.

```lua
timing.log("Starting engineering scenario")
```

#### `timing.sleep(ms)`

Interruptible client-side delay. Supported range: `0..60000` milliseconds.

```lua
timing.sleep(500)
```

#### `timing.simulate(regId, profile)`

Submits one simulated tag passage for the captured TimingNode.

```lua
timing.simulate("RT-A-0100", "simple")
```

The profile is optional and defaults to `normal`. Supported profiles are:

- `simple`;
- `normal`;
- `edge`.

This function requires `TAG_SCENARIO_SIMULATION` to be enabled by SI-01.

#### `timing.batch{...}`

Submits a repeatable client-side series of simulated passages.

```lua
timing.batch{
    count=10,
    from=1,
    to=100,
    order="random",
    seed=42,
    intervalMs=500,
    profile="normal"
}
```

Parameters:

| Parameter | Meaning | Default / range |
| --- | --- | --- |
| `count` | number of requests | required, 1..10000 |
| `from` | first numeric RegistrationId value | 1 |
| `to` | last numeric RegistrationId value | 2000 |
| `order` | generated order | `linear` or `random`; default `linear` |
| `seed` | seed for reproducible random order | 1 |
| `intervalMs` | delay between starts | 500; range 0..60000 |
| `profile` | simulated antenna profile | `normal` |

Generated IDs use the form `RT-A-%04d`.

A seeded random batch is reproducible when the same bounds, count and seed are used.

### Check simulation capability

Before using `timing.simulate` or `timing.batch`:

1. wait until Events/baseline is **LIVE**;
2. open **API**;
3. inspect **Capabilities**;
4. verify `TAG_SCENARIO_SIMULATION` is both supported and enabled.

Before synchronisation, capability state is unknown. Do not interpret unknown/stale
as disabled.

Changing or updating SI-02 does not change the capability of an already running SI-01.
If SI-01 was started with another composition/configuration, restart SI-01 as required
and reconnect SI-02.

### Script errors

Typical classes of errors are:

- **local Lua syntax/runtime error** — the script itself failed;
- **simulation not submitted** — SI-02 rejected the call locally because the required
  capability is unavailable;
- **IF-03 simulation rejected** — the request reached SI-01 and SI-01 rejected it;
- **stopped/disconnected/node changed** — SI-02 stopped further execution because the
  captured execution context is no longer valid.

A locally unavailable capability is intentionally distinguished from a remote
SI-01 rejection.

## Diagnostics and logs

### API

Use **API** to inspect:

- connected SI-01 application identity;
- SI-01 version and API version;
- current capability IDs and their `supported` / `enabled` values.

Unknown capability IDs remain visible for diagnostics.

### Client Log

**Client Log** contains SI-02 startup, configuration, connection and request diagnostics.
It remains available when SI-01 is offline.

### Device Log

**Device Log** shows live diagnostics from the connected SI-01 LoggingServer.
It is independent from Client Log.

### Events and Raw Data

Use **Events** to inspect the raw WebSocket event stream and **Raw Data** to inspect
source JSON associated with selected technical data.

### Terminal

**Terminal** is the line-oriented Remote Shell client. It is not an SSH or Telnet
emulator.

## Common troubleshooting

### The client is connected but controls or Run are disabled

Check that the Timing view is actually **LIVE**, not merely connected. Then select a
TimingNode.

### Lua local code works but simulated passages fail

Open **API → Capabilities** and check `TAG_SCENARIO_SIMULATION`. Local
`print`, `timing.log` and `timing.sleep` do not require that capability;
simulation calls do.

### Capability is unknown

Ensure Events is connected and wait for baseline synchronisation. Use **Sync view** if
necessary.

### The wrong target still appears connected

Apply the intended host and reconnect. Stateful connections are deliberately not
silently redirected between targets.

### JavaFX runtime mismatch during source launch

Use the Maven/NetBeans configuration described by SDE-03. Do not add an independent
old JavaFX SDK/JAR set to the SI-02 launch classpath.

## Known limitations

- The current UI presents one primary SI-01 target context.
- The current Lua facade does not provide multi-system connect management, node
  Open/Close, `awaitLive`, state assertions, arbitrary IF-03 dispatch or GUI automation.
- Only one Lua script runs at a time.
- GUI and Lua simulation batches cannot run concurrently.
- Lua restrictions are **not a security sandbox**. Run trusted engineering scripts only.
- Stop/cancellation cannot undo an IF-03 request already accepted by SI-01.
- A successful simulation request is not proof of a committed TimingData record.
- The Windows distribution is currently an app-image rather than an installer with
  automatic update support.

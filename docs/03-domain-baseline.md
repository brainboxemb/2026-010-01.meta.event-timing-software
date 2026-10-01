# Domain baseline

Status: working domain knowledge / non-authoritative requirements

This document captures stable domain facts and terminology supplied during the initial architecture work. It is intentionally separate from formal requirements: it records what the system domain looks like so later requirements, IDDs, architecture and code use the same concepts consistently.

Concrete production asset names, external registration-system IDs, source mappings and deployment inventories are intentionally **not** recorded in this public repository. They are deployment/proprietary information. Public documents describe the structure and semantics using generic identifiers only.

## TimingNodes, stages and locations

One running headless timing application must be able to host **1..N logical `TimingSystem` instances** at the same time. Each `TimingSystem` owns **1..N `TimingNode` instances**. This supports normal single-system deployment as well as simulation/test compositions that run multiple independent timing systems in one process.

The working software/domain term is `TimingNode` for one independently addressed logical timing aggregate at the **end of a stage**. A `TimingNode` is deployed or configured for a physical event `LocationId`; the software identity of the timing node and the physical location where it is used are separate concepts.

Conceptually, one timing application owns one or more independently addressed timingNodes:

```text
TimingApplication
  +-- ApplicationId
  |
  +-- 1..N TimingSystem
        +-- TimingSystemId        internal composition/simulation identity
        +-- SystemStatus          complete current system overview
        +-- UpstreamMessagePort   system-level upstream messages
        +-- UpstreamProtocol
        |     +-- heartbeat / ping
        |     +-- synchronisation / reconciliation
        +-- TimeSource             absolute time / controllable test offset
        |
        +-- 1..N TimingNode
              +-- TimingNodeId
              +-- LocationId
              +-- lifecycle / status
              +-- UpstreamMessagePort
              +-- TagProcessor
              +-- StageStartTimes
              +-- LogBook
              |     +-- 0..N TimingData
              +-- NextUpTeams
              +-- RaceData
              +-- StageTiming
              +-- uses / produces TimingData

Shared Domain contract:
  +-- TimingData
```

`ApplicationId`, internal `TimingSystemId`, `TimingNodeId` and `LocationId` are distinct concepts. `ApplicationId` identifies the running process/runtime. `TimingSystemId` is an internal composition/simulation identity used to distinguish multiple TimingSystem instances in one process; it is not part of the upstream functional addressing contract. `TimingNodeId` is the functional identity exposed to timing-data/upstream semantics, and `LocationId` identifies the physical event location where that node is configured or deployed.

Operational state such as `OPEN` / `CLOSED` belongs to the TimingNode software/domain concept. It is not the lifecycle of a physical registration box merely because that box is used by the timing node.

A `Stage` and a `TimingNode` are related but distinct concepts: a stage ends at a timing node. Stage-specific reference data such as start-time data may therefore be consumed by the timing node software without making the stage itself a hardware or runtime container.

The previous working name `TimingSystemInstance` was rejected as a name for an individual timing node because it mixed node semantics with runtime isolation. `TimingSystem` now has a distinct broader meaning: one logical timing-system aggregate that owns 1..N `TimingNode` instances.

## Timing-system, antenna and TimingNode identity

`ApplicationId`, `TimingSystemId`, `TimingNodeId`, `AntennaId` and `LocationId` are separate namespaces.

`TimingSystemId` identifies one logical `TimingSystem` inside a `TimingApplication` for internal composition, diagnostics and simulation isolation. The upstream system need not know that this grouping exists. `TimingNodeId` remains the functional identity of a node and scopes that node's registration sequence and synchronisation semantics. `LocationId` separately identifies the event location where the TimingNode is configured or deployed.

The I/O boundary owns antenna configuration and mapping:

```text
Antenna (0..N)
  +-- AntennaId
  +-- driver / device configuration

each Antenna
        -> 1..N TimingNodeId
```

An `Antenna` is the configured registration input. Reader/protocol/device
details belong to the concrete antenna implementation/configuration and are not
separate software identities unless implementation evidence later requires that
distinction. `SimulatedAntenna` is the built-in baseline implementation and is
always available for development/simulation. Other concrete antenna
implementations may be selected through the application extension/provider
mechanism without changing `AntennaId` or TimingNode semantics.

One antenna may intentionally feed more than one TimingNode. Each target
TimingNode keeps its own `TimingNodeId`, sequence and state; `AntennaId`
remains source/diagnostic context.

Known structural rules:

- `TimingNodeId` identifies the logical TimingNode;
- `AntennaId` identifies a configured antenna within the application;
- the application may compose 0..N antennas; configuration maps each `AntennaId` to its TimingNode targets;
- every TimingNode owns its own monotonic registration sequence and
  TimingNode-specific persistence/synchronisation state;
- multiple TimingNodes may share a physical antenna through explicit routing;
- concrete production antenna/device settings remain deployment information.

### Antenna identifiers

The software needs a stable configuration identity for every antenna.

Public examples use simple synthetic names:

```text
ANT1
ANT2
ANT3
```

A future physical label may use the same `AntennaId`. Production antenna names
and device settings remain deployment data and should not be copied into this
public repository.

## Separate software, I/O and configuration views

The logical I/O layer is repeated as part of each `TimingSystem` runtime
composition. A process hosting 1..N TimingSystems therefore normally composes
1..N corresponding I/O sets (Storage, Devices, Messaging and DeviceNetworks).
A lower-level implementation may multiplex a shared physical resource when that
is explicitly designed, but that does not merge the TimingSystem ownership
contexts.


Do not express the complete system as one parent/child tree. The software/domain
decomposition and I/O/configuration routing answer different questions.

### Software/domain view

```text
TimingApplication
  +-- ApplicationId
  |
  +-- 1..N TimingSystem
        +-- TimingSystemId        internal composition/simulation identity
        +-- SystemStatus          complete current system overview
        +-- UpstreamMessagePort   system-level upstream messages
        +-- UpstreamProtocol
        |     +-- heartbeat / ping
        |     +-- synchronisation / reconciliation
        +-- TimeSource             absolute time / controllable test offset
        |
        +-- 1..N TimingNode
              +-- TimingNodeId
              +-- LocationId
              +-- lifecycle / status
              +-- UpstreamMessagePort
              +-- TagProcessor
              +-- StageStartTimes
              +-- LogBook
              |     +-- 0..N TimingData
              +-- NextUpTeams
              +-- RaceData
              +-- StageTiming
              +-- uses / produces TimingData

Shared Domain contract:
  +-- TimingData
```

The exact component/class boundaries remain design work. `TimingSystem` is the parent domain aggregate hosted 1..N times by the `TimingApplication`; each TimingSystem owns 1..N `TimingNode` aggregates.

Each `TimingSystem` contains its own dedicated Domain `SystemStatus` component, system-level
`UpstreamMessagePort`, `TimeSource` and heartbeat/ping semantics. `SystemStatus` is the
complete current operational overview of that TimingSystem, not a single health
flag. It may include its TimingNode states, antenna/device availability, whether
a display is connected, keypad/beeper availability, device-network health,
storage state, upstream connectivity and synchronisation state. Concrete I/O
implementations report semantic status into this overview without becoming part
of the Domain model. Those semantics remain isolated per simulated/hosted system
rather than being application-global.

`TimeSource` is also per TimingSystem. In production it can delegate to the
platform wall clock. In simulation/test it may be controlled independently,
including a programmable offset or stepped time, so several TimingSystems hosted
in one process can intentionally observe different absolute times. Duration and
timeout semantics remain separate and use a monotonic source where appropriate.

Each TimingNode contains one passive `LogBook`. The LogBook keeps the node's
committed timing history as 0..N immutable `TimingData` values. The same
semantic value that is persisted is also what runtime consumers read from the
LogBook; the current design does not add a second logbook-specific data type.

The system-owned IF-05 interface defines the common TimingData semantics and
the default/reference interchange profile. SI-01 consumes the common `TimingData`
interfaces while a configured provider supplies the concrete immutable classes,
stateless factory and matching codec. Storage, Web and upstream communication may
consume the common API without becoming alternative owners of IF-05 semantics.

A TimingNode is the active serialization boundary for its mutable per-node
state. Its contained `LogBook`, `NextUpTeams`, `StageStartTimes` and
`RaceData` objects remain passive state holders. Concrete queue/thread choices
belong to detailed design.

`UpstreamProtocol` is a Domain protocol owned in the context of one
`TimingSystem`. It covers transfer of TimingData plus
synchronization/reconciliation and protocol-level handling such as ping/pong.
System-level semantic operations enter/leave through
`TimingSystem.UpstreamMessagePort`; node-level operations use the addressed
`TimingNode.UpstreamMessagePort`. The upstream peer can remain functionally
TimingNode-oriented; a ping does not require exposing `TimingSystemId`.
Transport/session mechanics remain I/O concerns.

### I/O routing view

```text
Antenna (0..N)
  +-- each Antenna -> 1..N TimingNode

BackofficeConnector (0..N)
  +-- bindings <-> 1..N TimingNode
```

The same routing model supports real and simulated I/O without changing the
TimingNode domain model.

## Location and record context

Each physical event location has a unique numeric identifier:

```text
LocationId = configured physical event-location identity
```

A `TimingNode` is configured/deployed at a location, while its software identity remains separate from that location identity.

A `TimingData` value is associated with the functional timing-node identity and physical location:

```text
TimingNodeId
LocationId
```

The containing `TimingSystem` is local runtime/composition context and is not required to be serialized into TimingData.

This lets a logical timing node preserve one ordered stream while records still state where the registration occurred. Moving or reconfiguring a producing system must not silently redefine either namespace.

## Registration sequence

Every timing node registration stream has a monotonically increasing sequence number scoped by **`TimingNodeId`** in the TimingData/upstream contract.

Conceptually:

```text
TimingData key = (TimingNodeId, SequenceNumber)
```

The `LocationId` and `AntennaId` may provide useful context, but neither changes the sequence scope. When one process hosts multiple TimingSystems, local storage/composition keeps their runtime contexts separated without changing the functional TimingData key.

Generic example:

```text
timing-node-01:  1041, 1042, 1043, 1044, ...
timing-node-02:   551,  552,  553, ...
```

This allows receiving/upstream systems to reason about stream consistency independently for every source. For example, receiving `1041`, `1042`, `1044` from one source makes a missing `1043` detectable.

Important intended properties:

- committed sequence numbering starts at **1** for a new `TimingNodeId` stream;
- sequence number **0 is reserved** and shall never identify a normal committed TimingData value;
- the number is monotonic per `TimingNodeId`-scoped stream;
- a committed number must not be reused after restart/recovery;
- higher-level synchronisation can use it for ordering and gap/consistency detection;
- moving/changing location must not implicitly reset the timing node sequence;
- multiple `TimingNode` streams in one application keep independent sequence streams;
- the exact rules for allowed gaps, wraparound and sequence persistence still need formal requirements.

## Per-source persistence

Each `TimingNodeId`-scoped timing node registration stream has its **own registration file**.

The active application model may remain in memory, but registration persistence/recovery must preserve the timing node boundary so one `TimingNodeId`-scoped stream and its sequence state can be recovered and synchronised independently.

Conceptually:

```text
TimingNodeId timing-node-01
  in-memory ledger/state
  TimingNode-specific sequence
  TimingNode-specific registration file

TimingNodeId timing-node-02
  in-memory ledger/state
  TimingNode-specific sequence
  TimingNode-specific registration file
```

The exact file names, external IDs and deployment mappings are configuration/private data. The file format, append/snapshot policy, atomicity and durability rules still need detailed design and formal requirements.

## TimingData values

A `TimingData` value represents a committed fact in one `TimingNodeId`-scoped
ordered stream. The common envelope carries source identity, sequence, location
and time. Type-specific semantics are represented by the concrete TimingData
variant rather than by nullable fields in one universal in-memory record.

The currently promoted/required v1 fact is participant registration. UC-002
explicitly leaves OPEN/CLOSE-as-TimingData as a later interface/protocol
decision, and the current use-case baseline does not yet promote registration
revocation. Those may become TimingData variants later when a use case or
requirement actually owns them.

A working minimal envelope is therefore conceptually:

```text
TimingData
  timingNodeId
  locationId
  sequenceNumber
  effective time
  recorded time
  semantic variant data
```

Asset and antenna context may additionally be retained where useful for
diagnostics/audit, but the exact storage/wire schema is not yet fixed.

### Participant registration semantics

The public TimingData model distinguishes **automatic** and **manual**
registrations as typed semantic variants. Both use the same common TimingData
envelope and sequence/key rules.

Three IDs have different meanings:

- `TagId` is the RFID/tag source identity;
- `TeamId` is the team/reference-data identity used by manual/domain input;
- `RegistrationId` is the canonical registration identity stored in committed
  TimingData.

The source IDs are resolved before TimingData construction:

```text
TagId  -----> RaceData/reference resolution ----+
                                                 +--> RegistrationId --> TimingData
TeamId -----> RaceData/reference resolution ----+
```

An automatic registration therefore starts from `TagId`; a manual registration
starts from `TeamId`. The configured/reference data resolves either path to the
same canonical `RegistrationId` concept before the definitive TimingData value
is created.

`RegistrationId` is not the TimingData record key. Record identity/order remains
`(TimingNodeId, SequenceNumber)`.

For manual registrations the semantic model may additionally record whether the
effective time was assigned by SI-01 or explicitly entered by the operator.
Automatic registration uses the accepted observed time by definition. A concrete
wire/profile representation may encode these facts with discriminators or compact
codes; those representation details do not require a universal Java record with
nullable fields.

## Time semantics

Recorded **event time** needs one unambiguous absolute-time meaning independent of how a local clock is displayed. Race/stage start reference data is different: an external definition may contain only a local time-of-day and no date.

The working dedicated absolute-event value name is `TimingTimestamp`. At domain boundaries it represents an absolute point on the time line rather than a local date/time with an implicit time zone. A time-only race/start definition remains a separate value and is resolved using the configured event/race time zone when an absolute registration is compared with it.

For a time-only start definition, SI-01 chooses the most recent valid occurrence of that local clock time that is not after the registration timestamp. This supports the normal midnight rollover without requiring the external definition to invent a date. Example: `23:59:50` start and `00:00:10` registration yields 20 seconds elapsed. If a start date is supplied, it is authoritative. Durations of 24 hours or more cannot be inferred uniquely from a time-only start and therefore require additional date/day context.

A timestamp is **not** the source-ordering mechanism. Registration timing node sequence numbers remain the stable ordering/consistency mechanism even if an operating-system wall clock is corrected forwards or backwards.

The SI-01 SAD owns the implementation architecture for `TimingTimestamp`, injectable clock/time sources, monotonic duration measurement and the risk created by wall-clock corrections.

## Registration identity and source resolution

`RegistrationId` is the canonical registration identity stored on committed
TimingData. It is deliberately separate from the concrete source/reference IDs
used to reach that registration:

```text
TagId  -----> RaceData/reference resolution ----+
                                                 +--> RegistrationId
TeamId -----> RaceData/reference resolution ----+
```

`TagId` and `TeamId` remain source/reference-domain identities. Their concrete
formats, categories, ranges and mappings are outside the public baseline.
Resolution occurs before TimingData construction and may use locally available
`RaceData`.

`RegistrationId` also remains separate from the TimingData record key
`(TimingNodeId, SequenceNumber)`.

## Race data

`RaceData` is the locally available participant/reference data used by one
`TimingNode`.

It may contain the data needed to resolve source identities to canonical
`RegistrationId` values. Obtaining or synchronising that data from an
external system is an integration/application responsibility rather than
behaviour owned by `RaceData`.

Concrete source formats, production mappings and private compatibility rules are
outside this public baseline. Stage start-time data remains a separate concern
owned by `StageStartTimes`.

## Start-time reference data

Start times are supplied/synchronised from the backoffice and retained locally.

A start-time definition shall support at least a local time-of-day without a date. A source may additionally provide an explicit date/race-day context; SI-01 may retain that richer information. A date is therefore optional in the semantic input, not a prerequisite for elapsed-time calculation.

They support local calculations such as elapsed time and ranking without requiring every calculation to make a live backoffice request. When only time-of-day is known, elapsed-time calculation uses the midnight-rollover rule defined in the time model above.

## Full-field simulation

A single SI-01 application must be capable of running enough configured `TimingNode` objects to represent the complete field behaviour required for backoffice integration testing.

For this use case:

- each configured `TimingNode` remains separately addressable by its `TimingNodeId`;
- each configured producer uses its configured timing node identity/identities according to the deployment mapping;
- each `TimingNodeId` retains its configured logical identity and independent sequence stream;
- antennas/devices may be stubbed or simulated through the normal adapter contracts;
- registrations still follow the same normal queue, source-sequence, persistence and backoffice paths as production data;
- simulation must not require a special bypass around the application/domain model;
- public test scenarios use generic identities, while a private integration configuration may map to the actual production inventory/protocol IDs.

The Raspberry Pi Zero target and desktop/integration-test hosts may show different runtime behaviour. Measure that difference when representative software exists; do not invent target resource limits in the domain model.

## Public/private domain-data boundary

This repository can document structural facts and generic ranges required for reusable implementation design, but it must not become an inventory of the live/real deployment.

Keep the following outside the public repository unless deliberately approved for publication:

- concrete antenna/device IDs and their real mappings;
- exact production source-to-node assignments;
- exact production antenna/device topology;
- proprietary protocol field values;
- encryption keys or secrets.

Public examples should use names such as `timing-node-01`, `ANT1`, and `connector-01`.

## Traceability implications

The combination of timing node identity and monotonically increasing sequence is a domain-level consistency mechanism, not merely an implementation convenience.

Later requirements/design must therefore preserve at least:

```text
timing node identity
sequence order
registration-asset context where useful
containing total-system context
location association
antenna context where relevant
record type/payload
effective event time plus recordedAt metadata
TimingNode-specific persistence/recovery without sequence reuse
synchronisation/gap detection
```

Corrections/revocations remain traceable rather than silently rewriting earlier
records. The first public record/file model is now defined by IF-05; later record
families extend that contract only when their domain requirements are promoted.

## Open domain questions

- Can a `TimingNode` change `LocationId` during one operational session, or is location fixed until the timing node is closed/reconfigured?
- How are multiple TimingNodes represented in registration-routing rules when they share a physical producer?
- Sequence numbering starts at 1; 0 is reserved.
- Are sequence-number gaps allowed after failed/aborted persistence, provided numbers are never reused?
- What happens if the numeric sequence reaches its maximum representation?
- Which operational events besides `OPEN` must be part of a timing node registration stream (for example close/reinitialisation/configuration changes)?
- What exact data must an `OPEN` registration entry contain?
- Which TimingNode-specific synchronisation rules, if any, are required once the node identity is known?
- Which source-specific behaviours, if any, require public operational requirements rather than provider-private handling?

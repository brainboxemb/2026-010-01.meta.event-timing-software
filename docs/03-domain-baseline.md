# Domain baseline

Status: working domain knowledge / non-authoritative requirements

This document captures stable domain facts and terminology supplied during the initial architecture work. It is intentionally separate from formal requirements: it records what the system domain looks like so later requirements, IDDs, architecture and code use the same concepts consistently.

Concrete production asset names, external registration-system IDs, source mappings and deployment inventories are intentionally **not** recorded in this public repository. They are deployment/proprietary information. Public documents describe the structure and semantics using generic identifiers only.

## TimingNodes, stages and locations

One running headless timing application must be able to host **multiple logical timingNodes** at the same time.

The working software/domain term is `TimingNode` for one independently addressed logical timing aggregate at the **end of a stage**. A `TimingNode` is deployed or configured for a physical event `LocationID`; the software identity of the timing node and the physical location where it is used are separate concepts.

Conceptually, one timing application owns one or more independently addressed timingNodes:

```text
TimingApplication
  |
  +-- SystemStatus
  |
  +-- 1..N TimingNode
        +-- TimingNodeId
        +-- LocationID
        +-- lifecycle / status
        +-- TagProcessor
        +-- StageStartTimes
        +-- TimingNodeJournal
        +-- NextUpTeams
        +-- RaceData
        +-- StageTiming
```

`TimingNodeId` is the stable identity of the `TimingNode`; `LocationID` identifies the physical event location where that timing node is configured or deployed.

Operational state such as `OPEN` / `CLOSED` belongs to the TimingNode software/domain concept. It is not the lifecycle of a physical registration box merely because that box is used by the timing node.

A `Stage` and a `TimingNode` are related but distinct concepts: a stage ends at a timing node. Stage-specific reference data such as start-time data may therefore be consumed by the timing node software without making the stage itself a hardware or runtime container.

The previous working name `TimingSystemInstance` mixed runtime isolation with the domain meaning of a timing node. New architecture/design work should use `TimingNode`; existing implementation names may be migrated later to match this documentation-led model.

## Antenna and TimingNode identity

`TimingNodeId`, `AntennaId` and `LocationID` are separate namespaces.

`TimingNodeId` is the stable software identity of a `TimingNode`. It scopes
that TimingNode's registration sequence, persistence and synchronisation
semantics. `LocationID` separately identifies the event location where the
TimingNode is configured or deployed.

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
distinction.

One antenna may intentionally feed more than one TimingNode. Each target
TimingNode keeps its own `TimingNodeId`, sequence and state; `AntennaId`
remains source/diagnostic context.

Known structural rules:

- `TimingNodeId` identifies the logical TimingNode;
- `AntennaId` identifies a configured antenna within the application;
- the application may compose 0..N antennas; configuration maps each `AntennaId` to its TimingNode targets;
- every TimingNode owns its own monotonic registration sequence and
  TimingNode-specific persistence/synchronisation state;
- reserve and virtual TimingNodes may share a physical antenna through routing;
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

Do not express the complete system as one parent/child tree. The software/domain
decomposition and I/O/configuration routing answer different questions.

### Software/domain view

```text
TimingApplication
  |
  +-- SystemStatus
  |
  +-- 1..N TimingNode
        +-- TimingNodeId
        +-- LocationID
        +-- lifecycle / status
        +-- TagProcessor
        +-- StageStartTimes
        +-- TimingNodeJournal
        +-- NextUpTeams
        +-- RaceData
        +-- StageTiming
```

The exact component/class boundaries remain design work, but the TimingNode is
the software/domain aggregate being operated.

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
LocationID = 1..25
```

A `TimingNode` is configured/deployed at a location, while its software identity remains separate from that location identity.

A registration record is associated with both:

```text
TimingNodeId
LocationID
```

This lets a logical timing node preserve one ordered stream while records still state where the registration occurred. Moving or reconfiguring a producing system must not silently redefine either namespace.

## Registration sequence

Every timing node registration stream has a monotonically increasing sequence number scoped by **`TimingNodeId`**.

Conceptually:

```text
RegistrationRecordKey = (TimingNodeId, SequenceNumber)
```

The `LocationID` and `AntennaId` may provide useful context, but neither changes the sequence scope.

Generic example:

```text
timing-node-01:  1041, 1042, 1043, 1044, ...
timing-node-02:   551,  552,  553, ...
```

This allows receiving/upstream systems to reason about stream consistency independently for every source. For example, receiving `1041`, `1042`, `1044` from one source makes a missing `1043` detectable.

Important intended properties:

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

## Registration entries

A registration entry is not limited to participant RFID passage data. Operational events can also be persisted as registration entries when they must participate in the traceable/synchronised stream.

Known example:

- opening a location/timing node is itself a registration entry.

A working minimal envelope is therefore conceptually:

```text
RegistrationRecord
  timingNodeId
  locationId
  sequenceNumber
  recordType
  observed/event time
  created time
  record-specific payload
```

Asset and antenna context may additionally be retained where useful for diagnostics/audit, but the exact storage/wire schema is not yet fixed.

## Time semantics

Recorded event time and start-time data need one unambiguous absolute-time meaning independent of how a local clock is displayed.

The working dedicated software value name is `TimingTimestamp`. At domain boundaries it represents an absolute point on the time line rather than a local date/time with an implicit time zone. Local time-zone and daylight-saving conversion are presentation/configuration concerns unless a future business rule explicitly depends on a local civil time.

A timestamp is **not** the source-ordering mechanism. Registration timing node sequence numbers remain the stable ordering/consistency mechanism even if an operating-system wall clock is corrected forwards or backwards.

The SI-01 SAD owns the implementation architecture for `TimingTimestamp`, injectable clock/time sources, monotonic duration measurement and the risk created by wall-clock corrections.

## Team number

The decoded participant/team identity contains a team number in the range:

```text
TeamNumber = 0..999
```

## Race data

`RaceData` is the locally available participant/team/tag reference data used by one `TimingNode`.

It may include participant/team reference data, normal tag references and reserve-tag conversion/mapping data. It is TimingNode-scoped application/domain state; obtaining or synchronising that data from the backoffice is an integration/application responsibility rather than behaviour owned by a `RaceData`.

Stage start-time data remains a separate concern owned by `StageStartTimes`.

## RFID tag identity structure

The tag ultimately represents a structured identity containing:

```text
prefix + team number + postfix
```

Known semantics:

- `team number` is `0..999`;
- prefix semantics distinguish at least normal, reserve and test tag classes;
- a dedicated prefix indicates that a tag is a reserve tag;
- a dedicated prefix indicates that a tag is a test tag;
- there are two physical tags for a team/identity;
- a postfix distinguishes the two tag copies.

The exact encoded prefix/postfix values, encryption details and protocol representation are proprietary and are not defined here.

A working public semantic representation should preserve the tag class after decoding rather than immediately flattening every tag into one normal participant identity. The exact class/type API remains an implementation/design decision.

## Reserve tags

Reserve tags require conversion/mapping data supplied by the backoffice.

The local timing application therefore needs to be able to resolve a decoded reserve-tag identity through locally synchronised reference data before treating it as the intended team identity.

The mapping must remain available locally when live backoffice connectivity is temporarily unavailable, subject to later freshness/validity requirements.

## Test tags

Test tags are a separate RFID tag class identified by their prefix. They are **not** the same concept as software test doubles, stub adapters or synthetic test tooling.

After decoding, SI-01 must be able to distinguish a test tag from both a normal tag and a reserve tag so test-specific behaviour can be applied deliberately. A test tag must not be silently treated as a normal participant tag merely because its decoded payload also contains a team-like number.

The exact behaviour is intentionally not fixed in this domain baseline. It belongs in operational use cases and later requirements, including whether a test tag creates a registration record, affects calculations, is synchronised to backoffice, is allowed in all lifecycle states, and how it is made visible to an operator.

## Start-time reference data

Start times are supplied/synchronised from the backoffice and retained locally.

They support local calculations such as elapsed time and ranking without requiring every calculation to make a live backoffice request.

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

Resource limits for the original Raspberry Pi Zero and larger desktop/integration-test deployments are different concerns. The architecture should permit the same logical model to run with different configured scale and adapter sets.

## Public/private domain-data boundary

This repository can document structural facts and generic ranges required for reusable framework design, but it must not become an inventory of the live/real deployment.

Keep the following outside the public repository unless deliberately approved for publication:

- concrete antenna/device IDs and their real mappings;
- exact virtual/reserve-source assignments;
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
record time
TimingNode-specific persistence/recovery without sequence reuse
synchronisation/gap detection
```

Corrections/revocations should remain traceable rather than silently rewriting earlier records; the exact record model remains under design.

## Open domain questions

- Can a `TimingNode` change `LocationID` during one operational session, or is location fixed until the timing node is closed/reconfigured?
- How are reserve/virtual TimingNodes represented in registration-routing rules when they share a physical producer with normal TimingNodes?
- Does sequence numbering start at a defined value for a new timing node?
- Are sequence-number gaps allowed after failed/aborted persistence, provided numbers are never reused?
- What happens if the numeric sequence reaches its maximum representation?
- Which operational events besides `OPEN` must be part of a timing node registration stream (for example close/reinitialisation/configuration changes)?
- What exact data must an `OPEN` registration entry contain?
- Are normal, reserve and virtual timingNodes treated identically by backoffice synchronisation once their timing node identity is known?
- What exact operational behaviour is required for test tags, and which parts deliberately differ from normal and reserve tags?

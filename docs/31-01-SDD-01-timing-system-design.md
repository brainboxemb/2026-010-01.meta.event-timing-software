# Timing system architecture detail

Status: working draft / non-authoritative

This document expands the system-level architecture sketch for one logical `TimingSystem`. It is intentionally more detailed than `software-architecture-sketch.md`, but it is still a design working document. Candidate requirements below are staging material for later promotion into formal requirements documents.

## Purpose

One headless Java runtime can host `1..X` logical timing systems. A `TimingSystem` is the main isolation boundary for waypoint-specific state and behaviour.

A timing system owns or coordinates:

- lifecycle such as `OPEN` / `CLOSED`;
- ordered processing of operator commands and device observations;
- participant registrations;
- local start procedure;
- manual registrations;
- penalty registrations and revocations;
- RFID reader lifecycle and tag-processing state;
- display/keypad interaction;
- timing-system status;
- local calculations based on reference data received from the backoffice.

Runtime-wide infrastructure may be shared where this does not leak timing-system state, for example logging, HTTP server infrastructure, RabbitMQ connection infrastructure, thread pools, configuration loading, and network monitoring.

## Generated detail diagrams

The PR documentation branch contains generated SVG and editable draw.io versions:

- [Timing-system internals](../../../blob/dev/pr-1/docs/architecture/timing-system-internals.svg)
- [Device and network topology](../../../blob/dev/pr-1/docs/architecture/device-network-topology.svg)
- [RFID processing pipeline](../../../blob/dev/pr-1/docs/architecture/rfid-pipeline.svg)

After merge, the equivalent outputs are published under `prod/docs`.

## TimingSystem as an architectural boundary

A possible composition is:

```text
TimingSystem
  TimingSystemState
  TimingSystemExecutor
  RegistrationService
  RegistrationStore
  StatusService
  RfidService
  CanDeviceService
  DisplayService
  StartProcedureService
  ReferenceDataService
  TimingCalculationService
```

Names are illustrative. The important part is ownership and dependency direction rather than the final class names.

The runtime should address a timing system explicitly:

```text
runtime
  +-- timing-system A
  +-- timing-system B
  +-- timing-system C
```

Operator APIs and device adapters should include enough context to route an incoming command or observation to the correct timing system.

## Ordered ingress and persistence

There are three different concepts that should not be conflated:

1. **Ingress/event queue** — orders commands and observations entering a timing system.
2. **Registration store** — durable local record of accepted registrations and corrections.
3. **Backoffice outbox/synchronisation queue** — tracks locally committed information that still needs to be delivered/reconciled with the backoffice.

The proposed execution model is one *logical* serialized executor per timing system. A logical serial executor does not require a dedicated OS thread; multiple timing systems may be multiplexed over a small shared executor appropriate for Raspberry Pi Zero constraints.

```text
many I/O callbacks/threads
        |
        v
immutable TimingSystemMessage
        |
        v
TimingSystem ingress queue
        |
        v
logical SerialExecutor
        |
        v
single-writer timing-system state
```

### Pseudocode — timing-system execution

```java
final class TimingSystemRuntime {
    private final TimingSystemId id;
    private final SerialExecutor executor;
    private final TimingSystemHandler handler;

    void submit(TimingSystemMessage message) {
        executor.execute(new Runnable() {
            @Override
            public void run() {
                handler.handle(message);
            }
        });
    }
}
```

`SerialExecutor` guarantees ordering for one timing system. Its backing executor can be shared by several timing systems.

Unit tests can replace it with a direct/synchronous executor:

```java
class DirectExecutor implements Executor {
    public void execute(Runnable command) {
        command.run();
    }
}
```

This keeps the same application handlers usable in production and deterministic unit tests.

## Registration flow

A registration should become an explicit domain record rather than an incidental side effect of an RFID callback.

Possible record types include:

```text
PASSAGE
START
MANUAL
PENALTY
PENALTY_REVOKED
```

A record will likely need at least:

```text
registration id
logical timing-system id
record type
participant/team identity where applicable
observation/event timestamp
creation timestamp
source (RFID, keypad/operator, API, ...)
source/device identity
quality/filter metadata where useful
correlation/reference id for corrections or revocations
```

The exact schema remains open.

### Pseudocode — accepting a registration

```java
void handleAcceptedObservation(AcceptedObservation observation) {
    Registration registration = registrationFactory.create(observation);

    registrationStore.append(registration);
    state.apply(registration);
    outbox.enqueue(RegistrationCommitted.from(registration));
    statusService.recordRegistration(registration);
    eventPublisher.publish(registration);
}
```

Whether persistence must complete synchronously before the registration is considered committed is a requirements/design decision still to be made.

## RFID device lifecycle

The RFID antenna/reader is not continuously powered. Its power is independently controlled and it requires boot/initialisation time.

The UI therefore needs explicit RFID device control separate from timing-system `OPEN` / `CLOSED` state.

Suggested device states:

```text
OFF
POWERING_ON
INITIALISING
READY
DEGRADED
ERROR
POWERING_OFF
```

`REINITIALISE` is an operator command/action, not necessarily a persistent state. Depending on hardware behaviour it may mean a software reconnect, reader reset, controlled power cycle, or a staged recovery strategy.

### Pseudocode — RFID power control

```java
void handle(SetRfidPower command) {
    if (command.isOn()) {
        if (rfidState == OFF || rfidState == ERROR) {
            rfidState = POWERING_ON;
            statusChanged();
            rfidPowerPort.powerOn();
        }
    } else {
        rfidState = POWERING_OFF;
        statusChanged();
        rfidPowerPort.powerOff();
    }
}

void handle(RfidPowerAvailable event) {
    rfidState = INITIALISING;
    rfidPort.initialise();
}

void handle(RfidInitialised event) {
    rfidState = READY;
    statusChanged();
}

void handle(ReinitialiseRfid command) {
    // Policy remains configurable/designable:
    // reconnect -> reset -> power cycle.
    recoveryService.reinitialise();
}
```

The timing system can therefore be `OPEN` while RFID is not yet `READY`; status must make that degraded condition visible rather than silently pretending the system is healthy.

## RFID heartbeat and health

A heartbeat/health mechanism is useful because a powered device is not necessarily responsive.

Possible inputs to RFID health include:

- last successful protocol exchange;
- explicit reader heartbeat/ping when supported;
- last received reader status message;
- expected versus actual connection state;
- time since last successful health observation.

The status service should derive states such as:

```text
READY
DEGRADED
UNRESPONSIVE
DISCONNECTED
ERROR
```

The exact heartbeat interval, timeout and recovery policy remain requirements/design choices.

## RFID tag-processing pipeline

RFID tag data is encrypted and a raw tag read is **not** immediately a participant registration.

Proposed pipeline:

```text
RFID hardware read
      |
      | capture source timestamp immediately
      v
RawTagRead
      |
      v
Decrypt / authenticate
      |
      v
TagObservation
      |
      v
Observation accumulator / filter
      |
      | accept only when filter policy is satisfied
      v
AcceptedTag
      |
      v
Reserve-tag conversion / normal identity lookup
      |
      v
ParticipantIdentity
      |
      v
Registration candidate
      |
      v
TimingSystem ingress/registration processing
```

The exact filtering algorithm is deliberately open. It may use multiple reads, observation duration, signal information, antenna identity, time windows, or other reader data. The architecture should allow the filter to accumulate observations rather than treating the first read as authoritative.

### Pseudocode — RFID observation

```java
void onRawTag(RawReaderFrame frame) {
    Instant observedAt = clock.instant();

    RawTagRead read = new RawTagRead(
        readerId,
        frame.getPayload(),
        frame.getSignalData(),
        observedAt);

    timingSystem.submit(new RfidRawReadObserved(read));
}
```

### Pseudocode — decrypt and filter

```java
void handle(RfidRawReadObserved event) {
    DecryptedTag tag = tagDecryptor.decrypt(event.getRead());

    if (!tag.isValid()) {
        statusService.recordInvalidTag();
        return;
    }

    FilterDecision decision = tagFilter.observe(tag);

    if (!decision.isAccepted()) {
        return;
    }

    ParticipantIdentity participant =
        participantResolver.resolve(decision.getAcceptedTag(), referenceData);

    if (participant == null) {
        statusService.recordUnknownTag(decision.getAcceptedTag());
        return;
    }

    handleAcceptedObservation(
        AcceptedObservation.rfidParticipant(
            participant,
            decision.getObservationTime(),
            decision.getEvidence()));
}
```

Encryption keys/credentials must come through the settings/secret mechanism and must not be hard-coded.

## Backoffice reference data

The backoffice supplies reference data needed for autonomous local operation.

Identified data sets include:

- reserve-tag conversion table;
- participant/team start times;
- potentially further participant/team metadata needed for local display or validation.

This data should be treated separately from live registrations.

A `ReferenceDataService` can own the latest accepted local snapshot/version and persist it so loss of RabbitMQ/internet connectivity does not immediately remove local functionality.

### Reserve-tag resolution

A reserve RFID tag maps to the participant/team identity that it temporarily represents.

```java
ParticipantIdentity resolve(TagId tag) {
    ParticipantIdentity direct = normalTagIndex.get(tag);
    if (direct != null) {
        return direct;
    }

    return reserveTagConversion.get(tag);
}
```

The update/versioning and validity rules for conversion tables still need requirements.

## Local elapsed time and ranking

When start-time reference data is locally available, the timing system should be able to calculate local information without waiting for the backoffice.

Possible calculation:

```text
elapsed time = accepted passage time - participant/team start time
```

A local ranking can then be derived from the locally known accepted passages and reference data.

Important: local ranking is a locally calculated operational view. Whether it is authoritative, provisional, or merely informational must be defined in requirements.

### Pseudocode

```java
Optional<LocalResult> calculate(Registration passage) {
    StartTime start = referenceData.startTimeFor(passage.participantId());
    if (start == null) {
        return Optional.empty();
    }

    Duration elapsed = Duration.between(start.instant(), passage.observedAt());
    return Optional.of(new LocalResult(passage.participantId(), elapsed));
}
```

## CAN subsystem

The CAN bus has both discoverable and non-discoverable devices.

Current known devices:

- version 1 LED display — CAN-based and discoverable;
- keypad — CAN-based but not discoverable.

The architecture should therefore not equate "present on CAN" with "discoverable by scan".

### Periodic CAN device scanner

A `CanDeviceScanner` periodically scans/probes for device types that support discovery and updates a `CanDeviceRegistry`.

```java
void scan() {
    for (CanDiscoveryProbe probe : configuredProbes) {
        probe.send(canPort);
    }
}

void handle(CanDiscoveryResponse response) {
    deviceRegistry.markSeen(
        response.deviceId(),
        response.deviceType(),
        clock.instant());
}
```

The scanner interval, timeout and disappearance policy remain open.

### Keypad

The keypad is configured as an expected non-discoverable CAN device/input endpoint.

It provides team numbers to the timing system.

```text
CAN frame
  -> KeypadAdapter
  -> TeamNumberEntered
  -> TimingSystem queue
  -> DisplayService
  -> active DisplayPort
```

The keypad adapter should report its own activity/health where possible even though it cannot participate in discovery.

## Display abstraction

The timing system should depend on a transport-independent display contract.

```java
interface DisplayPort {
    void showTeamNumber(TeamNumber teamNumber);
    void showStatus(DisplayStatusModel status);
    DisplayHealth health();
}
```

The exact contract will evolve, but application code should not need to know whether the display is CAN or Wi-Fi based.

### Display V1 — CAN

- connected through CAN;
- discoverable by the CAN device scanner;
- represented by a CAN display adapter implementing `DisplayPort`.

### Display V2 — IP/Wi-Fi

- connected through the local network/Wi-Fi router;
- the headless timing application publishes an mDNS service;
- the display discovers that service and connects to the application;
- represented by a network display adapter/session implementing the same logical `DisplayPort` contract.

This is deliberately *service advertisement from the application*, not application-side discovery of the display.

Possible topology:

```text
Timing application
   |
   | advertises _<service>._tcp via mDNS
   v
local LAN / Wi-Fi router
   ^
   |
Display V2 discovers service and connects
```

The mDNS service name/type, connection protocol, reconnect behaviour and authentication remain open.

## Network connectivity model

"Network connected" is not one boolean. The system needs status at several levels.

Suggested levels:

1. **Local link/router** — application can reach/use the local router/LAN.
2. **Internet** — a suitable external connectivity check succeeds.
3. **Backoffice transport** — RabbitMQ endpoint/session is connected and usable.

The router provides a 4G uplink, but the application should report what it can actually observe rather than infer mobile-network health that it cannot measure directly.

Example status:

```text
network.local        = UP
network.internet     = UP
backoffice.rabbitmq  = DISCONNECTED
```

This distinction lets operators see whether a RabbitMQ failure is local-network, internet, DNS/server, authentication, or broker-specific.

The probe strategy must avoid excessive traffic and false positives.

## Status model extension

The status service should aggregate immutable status snapshots without becoming the owner of device behaviour.

Potential tree:

```text
ApplicationStatus
  runtime
  network
    local-network
    internet
    rabbitmq
  TimingSystemStatus[A]
    lifecycle
    registration
    reference-data
    rfid
      power
      protocol
      heartbeat
      last-tag-activity
    can
      bus
      scanner
      discovered-devices
      keypad-activity
    display
      active-adapter
      connection/health
```

Status can be pushed to HTTP/WebSocket clients and queried through console/remote shell/API.

## Stub and simulated devices

Real hardware must be replaceable with stub/simulated adapters implementing the same ports.

Examples:

```text
RfidPort
  RealRfidAdapter
  StubRfidAdapter

CanPort
  LinuxCanAdapter
  StubCanAdapter

DisplayPort
  CanDisplayAdapter
  NetworkDisplayAdapter
  StubDisplayAdapter
```

A **test control interface** may be enabled in development/integration-test profiles so an operator/test can control stub behaviour, for example:

```text
inject RFID raw tag
change RFID health
simulate device disconnect/reconnect
inject keypad team number
add/remove discoverable CAN display
simulate internet down/up
simulate RabbitMQ down/up
```

The test-control interface must control adapters/stubs, not bypass the application/domain path. An injected stub RFID read should therefore flow through the same decrypt/filter/resolve/registration pipeline as a real read whenever the test is intended to exercise that pipeline.

### Pseudocode — controlled stub

```java
final class StubRfidAdapter implements RfidPort {
    private RfidListener listener;

    void testInject(RawReaderFrame frame) {
        listener.onFrame(frame); // same callback path as real hardware
    }

    void testSetConnectionState(ConnectionState state) {
        listener.onConnectionStateChanged(state);
    }
}
```

This provides realistic integration tests while preserving unit-testable pure services beneath the adapter boundary.

## Threading implications

Likely producers of concurrent events include:

- console/remote/API requests;
- WebSocket sessions;
- RFID callbacks;
- CAN receive/scanner callbacks;
- network display sessions;
- RabbitMQ consumer callbacks;
- timers for heartbeat, CAN scanning and connectivity checks.

Rules:

- callbacks capture source information/timestamps and enqueue immutable messages;
- callbacks do not mutate timing-system domain state directly;
- timers create messages just like hardware/operator inputs;
- state changes for one timing system are serialized;
- slow/blocking I/O is performed outside the serialized state executor;
- completion/failure is reported back as another message when it affects state.

### Example timer event

```java
scheduler.scheduleAtFixedRate(new Runnable() {
    @Override
    public void run() {
        timingSystem.submit(new CanScanDue(clock.instant()));
    }
}, initialDelay, scanInterval, TimeUnit.MILLISECONDS);
```

The handler decides what to do; the scheduler itself contains no domain rule.

## Unit-test examples

### RFID filter test

```java
@Test
public void firstRawReadDoesNotImmediatelyRegisterParticipant() {
    FakeClock clock = new FakeClock();
    InMemoryRegistrationStore store = new InMemoryRegistrationStore();
    FakeTagDecryptor decryptor = new FakeTagDecryptor();
    AccumulatingTagFilter filter = configuredFilter();

    TimingSystemHandler handler = fixture(clock, store, decryptor, filter);

    handler.handle(rawRead("encrypted-tag", clock.instant()));

    assertEquals(0, store.size());
}
```

### RFID lifecycle test

```java
@Test
public void powerOnReportsStartingUntilReaderInitialised() {
    handler.handle(new SetRfidPower(true));
    assertEquals(POWERING_ON, status.rfid().state());

    handler.handle(new RfidPowerAvailable());
    assertEquals(INITIALISING, status.rfid().state());

    handler.handle(new RfidInitialised());
    assertEquals(READY, status.rfid().state());
}
```

### CAN discovery test

```java
@Test
public void staleDiscoverableDisplayIsRemovedButConfiguredKeypadIsNot() {
    scanner.handle(discoveredDisplay("display-1"));
    clock.advance(discoveryTimeout.plusSeconds(1));
    scanner.handle(new DiscoverySweepDue(clock.instant()));

    assertFalse(registry.contains("display-1"));
    assertTrue(configuredDevices.containsKeypad());
}
```

## Candidate requirements emerging from this design

These identifiers are temporary working identifiers, not formal requirement IDs.

### Timing-system/runtime

- **CAND-TS-001** — The runtime shall support one or more independently addressed logical timing systems within one running application.
- **CAND-TS-002** — State-changing inputs for one timing system shall be processed in a defined order through a controlled serialized execution boundary.
- **CAND-TS-003** — The system shall persist accepted registrations locally independently of backoffice connectivity.
- **CAND-TS-004** — The system shall retain sufficient status to distinguish timing-system lifecycle from subsystem/device health.

### RFID

- **CAND-RFID-001** — The RFID antenna/reader shall be unpowered by default until explicitly enabled by an authorised operator/system action.
- **CAND-RFID-002** — The software shall represent RFID power/startup/initialisation/readiness state and expose it through system status.
- **CAND-RFID-003** — An authorised interface shall support RFID power control and reinitialisation/recovery actions.
- **CAND-RFID-004** — The software shall monitor RFID responsiveness/health using a heartbeat or equivalent health-observation mechanism.
- **CAND-RFID-005** — RFID tag payloads shall be decrypted/validated before participant identity resolution.
- **CAND-RFID-006** — A single first raw RFID read shall not by itself be required to create a participant registration; a configurable filtering/acceptance stage shall precede registration.
- **CAND-RFID-007** — RFID encryption/decryption credentials shall not be hard-coded in application source.

### Reference data and timing calculations

- **CAND-REF-001** — The system shall receive and locally retain reserve-tag conversion data from the backoffice.
- **CAND-REF-002** — The system shall receive and locally retain participant/team start-time data from the backoffice.
- **CAND-REF-003** — When required reference data is available, the system shall be able to calculate local elapsed times without a live backoffice request.
- **CAND-REF-004** — The system shall be able to derive a local ranking/ordering from locally available registrations and reference data; authority/provisional semantics remain to be defined.

### CAN and operator devices

- **CAND-CAN-001** — The system shall periodically scan/probe the CAN bus for device types that support discovery.
- **CAND-CAN-002** — The system shall support configured CAN devices that cannot participate in discovery.
- **CAND-CAN-003** — The system shall accept team-number input from the CAN-connected keypad.
- **CAND-DISP-001** — The system shall present display functionality through a transport-independent display interface.
- **CAND-DISP-002** — The system shall support the discoverable CAN-based version 1 display.
- **CAND-DISP-003** — The system shall support a network/Wi-Fi-based version 2 display that discovers the timing application through an advertised mDNS service and connects to it.

### Network/backoffice

- **CAND-NET-001** — Status shall distinguish local-network/router connectivity, internet connectivity and RabbitMQ/backoffice connectivity.
- **CAND-NET-002** — Loss of internet/backoffice connectivity shall not by itself prevent local registration processing when required local configuration/reference data is available.

### Simulation/testing

- **CAND-SIM-001** — Real hardware ports shall have stub/simulated implementations suitable for development and automated integration testing.
- **CAND-SIM-002** — A development/test control interface shall be able to manipulate supported stub-device states and inject simulated input.
- **CAND-SIM-003** — Stub input shall use the normal production application/device-adapter path where the purpose of the test is to exercise that behaviour.

## Important open questions

- What exact RFID hardware controls antenna power, and what feedback confirms that power is actually present?
- What does "reinitialise" mean for the selected RFID reader: protocol reconnect, hardware reset, power cycle, or staged recovery?
- What RFID encryption/authentication algorithm and key lifecycle are used?
- Which raw-reader properties are available for tag filtering (read count, RSSI, antenna, phase, dwell time, etc.)?
- What constitutes an accepted RFID observation and which timestamp is authoritative when several raw reads contribute?
- How are reserve-tag table versions activated and invalidated?
- Are start times corrected after initial publication, and how are corrections versioned/audited?
- What exact definition and authority does a locally calculated ranking have?
- What CAN discovery protocol/device identifiers are available?
- How can keypad health be inferred if the keypad is non-discoverable and silent when unused?
- Can multiple displays be present, and how is an active display selected?
- What protocol does Display V2 use after mDNS discovery?
- What mDNS service type/name and authentication model should be used?
- How should internet connectivity be tested without depending on one fragile external host?
- Are reference data, registrations and outbox data stored in one file/database or separate stores?
- What queue/backpressure behaviour is required if a device produces input faster than the Zero 1 can process it?

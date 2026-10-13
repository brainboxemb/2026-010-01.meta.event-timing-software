# Backoffice transport detailed design

Status: working draft / focused detailed design

Software item: **SI-01 — Timing Point Application**

## Purpose

This SDD explains **how the upstream connection is implemented**. The SSD still
defines SI-01's integration responsibilities, `32-06-ISD-backend-integration.md`
defines the UpstreamData semantics and `33-06-IDD-upstreamdata-json.md` defines the
public/default JSON representation. This document does not create another protocol
definition.

## Terms and abbreviations

- **SDD** — Software Design Description
- **SSD** — Software Specification Document
- **SI** — Software Item
- **RabbitMQ** — messaging-broker technology used by one transport realization


## Relationship to other documents

This SDD refines the SI-01 SSD for the transport implementation below the upstream
semantic boundary. The applicable system interface contract defines externally visible
semantics; this document defines connector/transport realisation without redefining that
contract.

Two SI-01 connector implementations are planned for the current integration path:

- an **Engineering API backoffice connector** for deterministic ST-2 testing through
  existing IF-03 HTTP/WebSocket transport;
- a **RabbitMQ backoffice connector** for production-shaped integration and deployment.

The Engineering Client (SI-02) owns one Backend Simulator model/pane. It can drive the
same semantic test data through either IF-03 or RabbitMQ. In RabbitMQ mode SI-02 is the
controllable external backend peer; it is not part of SI-01.

The application/domain model must not depend on RabbitMQ classes, socket classes, broker names, or the proprietary production message format.

Concrete production broker endpoint names, credentials, queue/exchange names, routing keys, external source IDs and message schemas are deployment/proprietary information and are intentionally excluded from this public repository.

Package/artifact placement follows `43-01-SDD-02-java-component-design.md`: a transport implementation can initially live under the application core's `io.messaging` capability and becomes a separate Maven library only when independent reuse, dependencies, lifecycle, ownership or release boundaries justify that split.

## Architectural goal

Backoffice target routing and transport are separate responsibilities:

```text
SystemStatus / TimingNode.UpstreamMessagePort
               ^
               |
      UpstreamMessageRouter
      upstream targets only
               |
               v
         Messaging (I/O)
          UpstreamGateway
               |
       +-------+-------+
       |               |
       v               v
Engineering API   RabbitMQ
BackofficeConnector BackofficeConnector
       |               |
       v               v
     IF-03         RabbitMQ broker
```

`UpstreamMessageRouter` is application behaviour scoped only to messages
exchanged with the external upstream system. **Upstream** identifies that
relationship and remains bidirectional; it is not a per-message direction.
`UpstreamGateway` and its connectors are I/O. Both transport
implementations preserve the same semantic addressing and feed the same
application router; neither connector owns application/TimingNode target
resolution. `TimingNode.UpstreamMessagePort` is bidirectional.

## Semantic upstream/backoffice boundary

The reusable application-core/domain side should work with semantic source-aware messages, not transport destinations.

Illustrative contracts:

```java
interface UpstreamPublisherPort {
    void publish(UpstreamData message);
}

interface UpstreamInboundListener {
    void onMessage(UpstreamData message);
}
```

`UpstreamData` is the reusable/public semantic message contract defined by IF-06.
In the default implementation, both inbound and outbound exchanges use the same
UpstreamData JSON envelope. A message variant that carries TimingData embeds one
or more committed IF-05 records as child values of a `TIMING_DATA` message; it
does not send standalone legacy log lines or redefine TimingData identity/order
semantics. PING request/answer and other message families share that envelope, with their
own payloads. Deployment-specific adapters may translate asymmetric external
wire protocols at the connector boundary without exposing them to application
or domain code.

These semantic contracts form the boundary between application `UpstreamMessageRouter` and I/O `Messaging`. Transport/session/wire types stay with `io.messaging`; domain objects do not depend on them.

The system-level IF-06 ISD defines the semantic obligations that both sides must fulfil.
The public/default JSON representation is defined by the IF-06 IDD; a deployment may
supply another UpstreamData codec/provider behind the same semantic boundary.

## Registration-source separation

Every configured `RegistrationSource` has its own logical inbound and outbound backoffice path.

Conceptually:

```text
source-01
  inbound semantic stream
  outbound semantic stream

source-02
  inbound semantic stream
  outbound semantic stream
```

This logical separation remains the same regardless of whether the selected transport is an in-memory stub, the Engineering API connector, or RabbitMQ.

## Transport selection and composition

Backoffice transport is selected through settings/application composition rather than compiled into domain code.

Pseudo-configuration:

```yaml
backoffice:
  transport: engineering-api   # or rabbitmq
```

The executable application resolves this selection to a concrete communication implementation.
A public reference/test application can use `engineering-api` or a stub. A
private/product application can select RabbitMQ plus private mappings/codecs where
required.

This selection does not imply a separate Maven artifact for every transport. Initial implementations may coexist in the core library while their boundaries are being tested.

## Engineering API test transport

### Purpose

The Engineering API connector provides a deterministic local backoffice transport without
adding another SI-01 listener port or another SI-02 connection lifecycle.

It is composed as a normal SI-01 backoffice connector, but uses the already-established
engineering interface:

- **IF-03 HTTP/JSON** for SI-02 to submit synthetic inbound semantic backoffice messages;
- **IF-03 WebSocket events** for SI-01 to expose outbound semantic messages and connector
  status back to SI-02.

This transport is for engineering and verification. It does not redefine IF-06 and does
not make IF-03 the production backoffice interface.

### Engineering topology

```text
SI-02 Backend Simulator / pane
      |                    ^
      | IF-03 HTTP         | IF-03 WebSocket
      v                    |
EngineeringApiBackofficeConnector
             |
             v
semantic UpstreamData boundary
             |
             v
UpstreamMessageRouter / normal SI-01 path
```

The payload at the engineering connector boundary is structured `UpstreamData` using
the public/default JSON representation plus only the IF-03 wrapper metadata needed for
that engineering operation/event.
Do not tunnel a pre-serialized RabbitMQ frame or proprietary production message as an
opaque string through IF-03.

The same SI-02 Backend Simulator can therefore edit/send synthetic RaceData and
StageStartTimes, inspect outbound TimingData/synchronisation state, and exercise
acknowledgement/synchronization behaviour without direct access to SI-01 Java objects.

### ST-2 scenarios

Candidate scenarios include:

- submit source/node-specific reference data from SI-02 through IF-03;
- verify it reaches the correct semantic source path;
- trigger normal TimingNode/application behaviour;
- observe outbound semantic backoffice events in SI-02;
- reconnect IF-03 Events and rebuild the relevant engineering view;
- exercise acknowledgement, pending-work and synchronization behaviour;
- repeat against one or multiple TimingNode/source combinations.

This profile verifies backoffice semantics and application routing. It deliberately does
not prove RabbitMQ connection/channel/consumer behaviour.

## RabbitMQ transport

RabbitMQ is a concrete communication implementation beneath the same semantic boundary.
For ST-3 the Engineering Client uses the same Backend Simulator model/pane as ST-2, but
switches to a RabbitMQ backend-peer transport. SI-01 and SI-02 then both connect to the
same broker; SI-02 plays the external backend side of the exchange.

![RabbitMQ shared connection with per-source consumers and controlled publishing](../../../raw/prod/docs/assets/architecture/rabbitmq-source-topology.svg)

### RabbitMQ terminology

Receiving and sending are intentionally modelled differently:

- a consumer reads/delivers messages from a RabbitMQ **queue**;
- a publisher normally publishes to an **exchange** with a **routing key**;
- RabbitMQ routes that publication to one or more queues according to broker bindings.

The working source configuration is therefore:

```text
RabbitMqSourceMessagingConfig
  inboundQueue
  outboundExchange
  outboundRoutingKey
```

If production uses the default exchange or a direct-to-queue convention, the implementation can represent that through the same outbound-endpoint abstraction.

### RabbitMQ connector topology

The application may compose 0..N `BackofficeConnector` instances. RabbitMQ is one concrete connector implementation:

```text
application
  +-- BackofficeConnector connector-01
  |     -> RabbitMqBackofficeConnector
  |     -> 1..N TimingNode/source bindings
  |
  +-- BackofficeConnector connector-02
        -> RabbitMqBackofficeConnector
        -> 1..N TimingNode/source bindings
```

A `RabbitMqBackofficeConnector` owns its broker connection/channel/consumer/publisher resources internally. Those mechanics are implementation detail, not a separate architectural manager component.

The ST-3 engineering peer is separate from that SI-01 connector:

```text
SI-02 Backend Simulator
        |
RabbitMqBackendTransport
        |
        v
    RabbitMQ broker
        ^
        |
RabbitMqBackofficeConnector
        |
SI-01 semantic backoffice boundary
```

The SI-02 transport uses backend-side queue/exchange/routing configuration complementary
to SI-01. It reuses the same semantic simulator data as the IF-03 transport so that ST-2
and ST-3 differ primarily in transport, not test intent.

One connector may multiplex several source-specific queues/channels over one physical broker connection. Separate connectors may use different brokers, credentials or routing domains. A TimingNode may intentionally participate in more than one connector.

Within one connector, separate consumer and publisher connections remain an implementation option when fault isolation, channel/thread ownership, broker-client behaviour or measured Pi Zero evidence justifies it. That refinement must not change the semantic connector boundary.

### RabbitMQ threading

RabbitMQ callbacks are external I/O callbacks and must not directly mutate timing-domain state.

```text
RabbitMQ consumer callback
      |
      v
RabbitMqConnector / UpstreamGateway
      |
      v
transport-neutral upstream message
      |
      v
UpstreamMessageRouter resolves ApplicationId / TimingNodeId
      |
      v
application target or TimingNode.UpstreamMessagePort
```

Each consumer must have controlled channel ownership. Arbitrary domain threads must not publish directly on shared RabbitMQ channels.

### RabbitMQ source-specific settings

Pseudo-configuration only:

```yaml
backoffice:
  connectors:
    - id: connector-01
      type: rabbitmq
      host: ${BROKER_HOST}
      port: ${BROKER_PORT}
      virtualHost: ${BROKER_VHOST}
      credentials: external-secret-reference
      bindings:
        - timingNode: timing-node-01
          externalName: ${PRIVATE_TIMING_NODE_NAME}

      sources:
        - key: source-01
          externalId: ${PRIVATE_SOURCE_ID_01}
          timingNode: timing-node-01
          inboundQueue: ${PRIVATE_SOURCE_01_IN_QUEUE}
          outboundExchange: ${PRIVATE_SOURCE_01_OUT_EXCHANGE}
          outboundRoutingKey: ${PRIVATE_SOURCE_01_OUT_KEY}
        - key: source-02
          externalId: ${PRIVATE_SOURCE_ID_02}
          timingNode: timing-node-02
          inboundQueue: ${PRIVATE_SOURCE_02_IN_QUEUE}
          outboundExchange: ${PRIVATE_SOURCE_02_OUT_EXCHANGE}
          outboundRoutingKey: ${PRIVATE_SOURCE_02_OUT_KEY}
```

For two configured sources, two inbound consumers exist even if they share one physical RabbitMQ connection.

## PING scheduling and connector lifecycle

PING scheduling belongs to the lifecycle of each configured upstream connector, not to a
TimingNode and not to TimingData persistence.

When a connector reports that it has reached its operational connected state, the owning
connector/gateway lifecycle starts one periodic PING task with:

```text
initial delay: 0
period:        30 seconds
```

The first execution therefore publishes `PING(op=REQ, mode=HB)`
immediately. Later executions publish heartbeat PING REQUEST messages at the
30-second period while that connector remains operationally connected. The
reference implementation may assign a connector-scoped opaque `pingId` to
individual requests and track whether a PING ANSWER echoing that identifier has
been observed. This is an implementation choice rather than an IF-06 interface
obligation. A manual PING request omits `mode`; the answer does too.
A manual request/answer exchange does not reset the heartbeat scheduler.

When the connector disconnects, deactivates or is replaced, its scheduled PING task is
cancelled. Reconnect creates a new task/cycle and again begins with an immediate PING.
Only one active PING task may exist per active connector.

The Java implementation should use the application's existing scheduled-executor
infrastructure rather than introduce a separate `java.util.Timer` thread solely for
heartbeat work. PING submission goes through the normal UpstreamData publisher/connector
path. It bypasses TimingData sequence allocation and LogBook persistence because PING is
not a TimingData record.

Inbound PING REQUEST is handled at the same upstream semantic boundary:
SI-01 creates one PING ANSWER retaining the request's optional `mode`
(`HB` when present; absent for manual) and publishes it through
the connector without entering the TimingData/LogBook path. Incoming PING ANSWER messages are processed as
responses and must never trigger another answer. The reference codec echoes
an optional incoming `pingId` when present.

No missing-answer timeout or disconnect threshold is fixed yet. Connector status may
expose the last sent PING REQUEST, last received PING ANSWER and whether exchanges
remain unconfirmed, but policy for changing connection health remains a later decision.

Transport-level keepalive mechanisms (for example broker/TCP heartbeat features) may
coexist with this application-level PING request/answer exchange but do not replace
IF06-REQ-011/012/013.

## Outbox and delivery

Local commitment and external transport are deliberately separated. For the public
v1 TimingData path, the **LogBook is the durable outbound payload history**; SI-01
does not persist a second copy of each record merely to implement an outbox.

```text
TimingNode LogBook (authoritative committed TimingData)
       |
       +--> local committed head sequence
       |
       v
per logical upstream target + NodeId sync cursor/state
       |
       +--> backend highest contiguous accepted sequence
       +--> pending = LogBook records after backend sequence
       |
       v
BackofficePublisherPort
       |
       +--> EngineeringApiBackofficeConnector
       |
       +--> RabbitMqBackofficeConnector
```

Working direction:

1. commit TimingData locally and make it durable in the LogBook;
2. publish/replay records in original source order;
3. transport delivery/confirm may show that bytes reached the selected transport,
   but does not clear semantic pending state;
4. backend sends SYNC state with its highest contiguous accepted sequence;
5. SI-01 derives pending records as committed sequence values after that point;
6. on reconnect or backend rollback, replay retained records from the backend's
   current contiguous sequence + 1;
7. identical duplicate record delivery is idempotent; same record key with changed
   content is a conflict.

Each configured logical upstream target keeps independent progress for each bound
NodeId. A connector reconnect creates a new transport session but not a new TimingData
identity or synchronization namespace.

No exact millisecond retry/backoff policy is fixed by D03. Connectors may use suitable
transport retry/backoff, while the semantic guarantee is that uncertain delivery can
be repeated and pending TimingData remains derivable until backend progress confirms it.

Reference-data synchronization uses the same SYNC exchange only for revision state.
Actual RaceData/StageStartTimes content is still transferred as REFERENCE_DATA snapshots.

## Status model

Transport status and source status remain separately observable.

```text
BackofficeStatus
  selectedTransport
  connection/session state
  lastPing
  lastPong
  pingPending

  source-01
    inbound
      configured
      active
      lastMessage
    outbound
      localTimingSeq
      backendTimingSeq
      pendingCount
      syncState
      lastPublish
      lastFailure

  source-02
    ...
```

For RabbitMQ, connection status can additionally expose broker/authentication/recovery
information. For the Engineering API connector, status can expose whether the connector is
enabled plus its last inbound/outbound engineering interaction; IF-03 connection state
itself remains owned by the existing API/Event interfaces.

## Java package and artifact boundaries

Working package/artifact direction:

```text
shared/upstream-data
    UpstreamData
    UpstreamDataCodec
    UpstreamDataProvider
    default/reference JSON implementation

application/domain
    semantic routing, reference-state application, outbox/sync state

existing IF-03 presentation/application adapter
    EngineeringApiBackofficeConnector

io.messaging.rabbitmq
    RabbitMqBackofficeConnector
    broker connection/channel/consumer/publisher implementation
```

This does **not** require three Maven libraries.

Extract an `event-timing-comm-rabbitmq` (or similarly named) artifact only when
one or more of these boundaries become real:

- several applications need RabbitMQ independently;
- the RabbitMQ client dependency should be optional and excluded from non-RabbitMQ applications;
- lifecycle/release ownership needs an independent boundary;
- public/private implementation ownership requires extraction.

Without such evidence, clean package boundaries are sufficient and keep extraction straightforward.

## Public/private boundary

Public core/test code may define:

- transport-independent semantic ports;
- generic source/node binding identities where connector routing requires them;
- shared public `UpstreamData` + provider/codec contracts;
- built-in public/reference JSON UpstreamData representation;
- Engineering API backoffice adapter using structured public UpstreamData;
- RabbitMQ connection/consumer infrastructure if proprietary production codec details remain separate;
- SI-02 RabbitMQ backend-peer test transport using synthetic/public topology;
- synthetic RabbitMQ topology for integration tests.

Private components/configuration may provide:

- actual external source-ID mappings;
- actual broker topology names;
- proprietary message schemas/codecs;
- authentication details;
- production-specific retry/synchronization protocol details where sensitive.

## Automated system-test profiles

The transport abstraction supports progressively more realistic automated system tests.

### ST-1 — Application behaviour

Goal: validate application behaviour through its public control/status interface while external dependencies are controlled stubs.

```text
System-test driver
      |
      | public application control/status interface
      v
real application process
      |
      +-- stub RFID/CAN/display
      +-- in-memory/stub backoffice port
```

This is the fastest system-level feedback loop and does not require a network backoffice service.

### ST-2 — Engineering API backoffice loop

Goal: verify the semantic backoffice path through the existing Engineering Client and
IF-03 transport before broker-specific behaviour is introduced.

```text
SI-02 Backend Simulator
      | IF-03 HTTP / WebSocket
      v
EngineeringApiBackofficeConnector
      |
      v
real SI-01 semantic backoffice path
```

This profile verifies source/node routing, inbound/outbound semantics,
acknowledgement/synchronization and recovery of the engineering view without RabbitMQ.

### ST-3 — RabbitMQ integration

Goal: verify the production-shaped broker transport end-to-end with SI-02 as the
controllable backend peer.

```text
SI-02 Backend Simulator
      |
RabbitMqBackendTransport
      |
      v
hosted RabbitMQ
      ^
      |
RabbitMqBackofficeConnector
      |
      v
real SI-01
```

A hosted broker such as CloudAMQP is a suitable initial environment. This verifies
broker connection/channel/consumer behaviour, source-specific queues/routing,
acknowledgement, outbox recovery and reconnect/recovery scenarios. Hosted-broker
availability is integration evidence and must not become a prerequisite for every fast CI
run.

These profiles complement unit/component tests and Pi Zero/hardware-in-the-loop verification; they do not replace them.

## RabbitMQ test environment

The first production-shaped ST-3 environment may use a hosted RabbitMQ service such as
CloudAMQP. Broker URI, credentials, vhost and test topology are provided through external
configuration/secrets and are never committed to the public repository.

A local disposable RabbitMQ container remains a useful optional fallback for repeatable
offline regression tests, but it is not required for ST-2 and does not replace the hosted
end-to-end verification.

The intended ST-3 operator flow is:

```text
configure test broker
start SI-01 with RabbitMqBackofficeConnector
connect SI-02 Backend Simulator using RabbitMqBackendTransport
exercise inbound/outbound source flows
force/recover broker or client connection where practical
verify pending delivery / synchronization
clean up test topology
```

## Candidate requirements

Temporary identifiers only.

- **CAND-BO-001** — SI-01 backoffice semantics shall be independent from the concrete communication transport.
- **CAND-BO-002** — The backoffice transport shall be selectable through external configuration/composition.
- **CAND-BO-003** — An Engineering API backoffice connector shall be available for deterministic ST-2 testing without requiring RabbitMQ.
- **CAND-BO-004** — The Engineering API connector shall carry structured public/reference UpstreamData through existing IF-03 HTTP/WebSocket transport.
- **CAND-BO-005** — RabbitMQ shall support a source-specific inbound queue configuration for each configured registration source.
- **CAND-BO-006** — RabbitMQ shall support source-specific outbound routing configuration for each configured registration source.
- **CAND-BO-007** — Multiple RabbitMQ source consumers shall be able to share one physical broker connection.
- **CAND-BO-008** — External transport callbacks shall not directly mutate timing-domain state.
- **CAND-BO-009** — Transport connection status and per-source inbound/outbound status shall be observable independently.
- **CAND-BO-010** — Loss of external backoffice transport shall not discard locally committed registration data; LogBook remains the authoritative replay payload history.
- **CAND-BO-011** — Reconnection shall restore configured source communication, exchange semantic SYNC state and replay records after the backend's highest contiguous accepted sequence.
- **CAND-BO-012** — Production broker/source topology, protocol details and credentials shall remain external/private configuration or implementation.
- **CAND-BO-013** — ST-3 shall support an external RabbitMQ test broker and an SI-02 backend-peer transport so the Engineering Client can exercise the broker-side backend role end-to-end.
- **CAND-BO-014** — SI-01 shall support zero or more configured backoffice connectors within one application composition.
- **CAND-BO-018** — Each operationally connected upstream connector shall publish one immediate PING REQUEST with `mode = HB` and then another every 30 seconds until disconnect/deactivation; every valid PING REQUEST shall receive one PING ANSWER preserving optional HEARTBEAT mode (manual requests omit mode; correlation remains optional).
- **CAND-BO-015** — A backoffice connector shall support bindings for one or more TimingNodes, and one TimingNode may be bound to more than one connector.
- **CAND-BO-016** — Connector-specific external names/routing identities shall not redefine the internal `TimingNodeId`.
- **CAND-BO-017** — Backoffice routing/fan-out shall remain separate from concrete connector transport/resource handling.

## Open questions

- What exact IF-03 HTTP operation and WebSocket event schema should carry the engineering backoffice envelope?
- Which acknowledgement/synchronization controls need to be exposed in the SI-02 Backend Simulator?
- Within one RabbitMqBackofficeConnector, is one physical connection sufficient, or should consumer and publisher traffic use separate connections?
- Are RabbitMQ queues/exchanges pre-provisioned or should the application declare/bind any topology?
- At what point does RabbitMQ deserve its own Maven library rather than a `comm` package inside the core artifact?
- What connector-specific retry/backoff timing is appropriate for the Engineering API
  and RabbitMQ implementations?
- Should cached per-target synchronization progress be persisted for faster status
  restoration, even though it is never authoritative and is re-established by SYNC?
- What broker/client settings are appropriate on the Raspberry Pi Zero memory/CPU budget?

# Upstream transport detailed design

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

- an **Engineering API upstream connector** for deterministic ST-2 testing through
  existing IF-03 HTTP/WebSocket transport;
- a **RabbitMQ upstream connector** for production-shaped integration and deployment.

The Engineering Client (SI-02) owns one Central System Simulator model/pane. It can drive the
same semantic test data through either IF-03 or RabbitMQ. In RabbitMQ mode SI-02 is the
controllable external Central System peer; it is not part of SI-01.

The application/domain model must not depend on RabbitMQ classes, socket classes, broker names, or the proprietary production message format.

Concrete production broker endpoint names, credentials, queue/exchange names, routing keys, external source IDs and message schemas are deployment/proprietary information and are intentionally excluded from this public repository.

Package/artifact placement follows `43-01-SDD-02-java-component-design.md`: a transport implementation can initially live under the application core's `io.messaging` capability and becomes a separate Maven library only when independent reuse, dependencies, lifecycle, ownership or release boundaries justify that split.

## Architectural goal

Node-scoped semantic protocol handling and external transport are separate responsibilities:

```text
TimingSystem
  Upstream
    NodeUpstream A <----> UpstreamStream A
    NodeUpstream B <----> UpstreamStream B
                              |
                              v
                        UpstreamGateway
                              |
                    +---------+---------+
                    |                   |
             Engineering API         RabbitMQ
                Connector            Connector
```

`NodeUpstream` owns node-scoped UpstreamData semantics, packet delivery state,
`UpstreamDataCodec` ownership and heartbeat cadence/state. `UpstreamData` is represented
as one node-scoped `UP_PACKET` or `DN_PACKET` carrying packetNr and one semantic
message. Current semantic messages include TimingData, TimingDataReq, Seq,
RaceData, Recv and Ping; there is no hidden implementation hierarchy behind subtype
interfaces. `DefaultUpstreamData` remains only the reference-profile
factory/convenience layer.
One concrete `UpstreamStream` is composed for each NodeUpstream.

Runtime composition first constructs the fixed node-scoped UpstreamStreams from
NodeId + connector bindings, then constructs one complete UpstreamGateway from that
connector and the complete NodeId-to-stream routing map. Runtime operation does not add,
replace or create application ports.

Transport ingress supplies `NodeId + encodedMessage` through the connector's fixed
Messaging-internal gateway input. `UpstreamGateway` uses the NodeId exactly there to
select the already composed node-scoped UpstreamStream application port. The internal
input is not a public ConnectorPort contract, and Generic Messaging has no separate
`UpstreamMessage(NodeId, payload)` value.

Once selected, UpstreamStream is the fixed application port: `read()`, `send(...)`
and availability checks operate through its captured connector/queue binding without
another NodeId lookup in UpstreamGateway. Stream CONNECTED and DATA_AVAILABLE events
carry the producing UpstreamStream object itself. The owning TimingSystem installs those
fixed stream subscriptions before activation and targets ordinary NodeUpstream input
methods; NodeUpstream does not expose composition-only EventInput ports. Connector
CONNECTED/DISCONNECTED events likewise carry the producing connector object. `UpstreamConnector` is the
abstract base that owns those public event ports and the one-time internal gateway input
binding; concrete transports only implement their transport-specific state and delivery.
Queue admission is not modeled as an event because it returns
ACCEPTED/UNKNOWN_NODE/INPUT_FULL.

Engineering-specific protocol adaptation is below `io.messaging.engineering`.
`UpstreamApiMessage` extracts the IF-06 NodeId needed for inbound routing and retains
the complete encoded IF-06 message unchanged. `EngineerApiConnector` owns only
Engineering WebSocket session/delivery mechanics; it does not own PING/heartbeat
protocol scheduling.

The generic architecture deliberately does not model RabbitMQ's physical queue shape.
A full-duplex WebSocket can carry both directions on one connection; RabbitMQ may use
1..N inbound consumers/queues plus controlled outbound publishing. Both realise the
same connector boundary and the same node-scoped streams.

## Semantic upstream boundary

The reusable application-core/domain side should work with semantic source-aware messages, not transport destinations.

Conceptually, Domain sees one concrete bidirectional application port per
`NodeUpstream`:

```java
final class UpstreamStream {
    EventSource<UpstreamStream> CONNECTED;
    EventSource<UpstreamStream> DATA_AVAILABLE;

    boolean isAvailable();
    boolean hasMessage();
    String read();
    void send(String encodedMessage);
}
```

Transport-side ingress is separate and result-bearing:

```java
interface ConnectorPort {
    ReceiveResult receive(NodeId nodeId, String encodedMessage);
}
```

NodeUpstream decodes immediately after `read()` and encodes immediately before
`send(...)`. NodeId is used once to select the application port on inbound transport
routing and is otherwise implicit in the composed stream. No generic Messaging type
wraps each payload in a second NodeId-bearing message object.

`UpstreamData` is the reusable/public semantic packet contract defined by IF-06. The
default implementation uses one JSON packet shape with explicit `UP_PACKET` and
`DN_PACKET` direction, a packetNr for delivery/debug identity, and one semantic message.
RECV confirms a downstream packetNr. The JSON `v` member is the representation version
owned by the IF-06 IDD and follows the project-wide odd/even maturity convention; it is
not runtime packet state and does not replace the IF-05 TimingData sequence. Deployment-specific adapters may translate
asymmetric external wire protocols at the connector boundary without exposing them to
application or domain code.

These semantic contracts form the boundary between application `UpstreamGateway` and I/O `Messaging`. Transport/session/wire types stay with `io.messaging`; domain objects do not depend on them.

The system-level IF-06 ISD defines the semantic obligations that both sides must fulfil.
The public/default JSON representation is defined by the IF-06 IDD; a deployment may
supply another UpstreamData codec/provider behind the same semantic boundary.

## Registration-source separation

Every configured `RegistrationSource` has its own logical inbound and outbound upstream path.

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
upstream:
  transport: engineering-api   # or rabbitmq
```

The executable application resolves this selection to a concrete communication implementation.
A public reference/test application can use `engineering-api` or a stub. A
private/product application can select RabbitMQ plus private mappings/codecs where
required.

This selection does not imply a separate Maven artifact for every transport. Initial implementations may coexist in the core library while their boundaries are being tested.

## Engineering API test transport

### Purpose

The Engineering API connector provides a deterministic local upstream transport without
adding another SI-01 listener port or a second Central System Simulator connection.

It is composed as a normal SI-01 upstream connector and uses the existing IF-03
WebSocket endpoint at `/api/v1/events?role=upstream`. That WebSocket is full-duplex:
both SI-02-to-SI-01 and SI-01-to-SI-02 UpstreamData travel over the same connection.
The normal STATUS_SNAPSHOT remains the first event; after that baseline the connection
becomes the active engineering upstream session.

This transport is for engineering and verification. It does not redefine IF-06 and does
not make IF-03 the production backoffice interface.

### Engineering topology

```text
SI-02 Central System Simulator
            ^
            | bidirectional IF-03 WebSocket
            v
EngineerApiConnector
            ^
            | UpstreamApiMessage / NodeId + encoded message
            v
      UpstreamGateway
            ^
            | fixed node-scoped UpstreamStream application port
            v
        NodeUpstream
```

UpstreamData is carried as structured semantic data; do not tunnel a serialized
RabbitMQ frame or proprietary production message as an opaque string through IF-03.
Only one upstream-role peer is active at a time. Generic IF-03 event clients remain
independent and do not receive UPSTREAM_DATA.

### Engineering connector lifecycle and wiring

`EngineerApiConnector` is one normal Connector implementation and lives with
`UpstreamApiMessage` under `io.messaging.engineering`. Presentation/IF-03 owns the
WebSocket mechanics. The Engineering boundary parses only enough IF-06 JSON to extract
NodeId into `UpstreamApiMessage`; it does not construct semantic `UpstreamData`.

Inbound Engineering data calls the gateway ConnectorPort with NodeId and the complete
encoded IF-06 payload. UpstreamGateway resolves that NodeId to one already composed
UpstreamStream application port. From that point forward the application side no longer
routes by NodeId. Outbound traffic uses the stream's fixed connector binding and passes
routing context separately to the transport adapter when required.

Connector connection/disconnection are typed post-fact events. Heartbeat/PING cadence
is scheduled by NodeUpstream because it is IF-06 protocol behavior rather than
Engineering WebSocket session behavior.

The SI-02 Central System Simulator owns peer behavior. It can allocate packet ids, keep
one normal DN_PACKET outstanding, inspect RECV/SEQ/TIMING_DATA,
answer PING, issue TIMING_DATA_REQ and deliberately disconnect/reconnect for recovery
tests.

### ST-2 scenarios

ST-2 scenarios include:

- connect the upstream-role WebSocket and observe STATUS_SNAPSHOT followed by immediate
  PING plus the packet/sequence exchange;
- inspect packetNr in both directions and verify the current IF-06 JSON representation
  version independently from packet delivery;
- send RACE_DATA in a normal DN_PACKET, verify semantic apply followed by RECV, and
  verify that a lost RECV causes the exact same downstream packet to be resent without
  applying its changes twice;
- observe outbound TIMING_DATA and bidirectional SEQ REQ/ANS/NTF;
- issue TIMING_DATA_REQ and verify bounded LogBook replay plus the replay-to-live handoff;
- request full current downstream-state resend through RECV position 0;
- disconnect/reconnect and verify fresh TIMING_DATA sequence reconciliation without a
  RACE_DATA source-history replay;
- repeat against configured bindings for one or multiple TimingNodes.

This profile verifies semantic routing and recovery without proving RabbitMQ
connection/channel/consumer behavior.

## RabbitMQ transport

RabbitMQ is a concrete communication implementation beneath the same semantic boundary.
For ST-3 the Engineering Client uses the same Central System Simulator model/pane as ST-2, but
switches to a RabbitMQ backend-peer transport. SI-01 and SI-02 then both connect to the
same broker; SI-02 plays the external Central System side of the exchange.

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

The application may compose 0..N `UpstreamConnector` instances. RabbitMQ is one concrete connector implementation:

```text
application
  +-- UpstreamConnector connector-01
  |     -> RabbitMqUpstreamConnector
  |     -> 1..N TimingNode/source bindings
  |
  +-- UpstreamConnector connector-02
        -> RabbitMqUpstreamConnector
        -> 1..N TimingNode/source bindings
```

A `RabbitMqUpstreamConnector` owns its broker connection/channel/consumer/publisher resources internally. Those mechanics are implementation detail, not a separate architectural manager component.

The ST-3 engineering peer is separate from that SI-01 connector:

```text
SI-02 Central System Simulator
        |
RabbitMqCentralSystemTransport
        |
        v
    RabbitMQ broker
        ^
        |
RabbitMqUpstreamConnector
        |
SI-01 semantic upstream boundary
```

The SI-02 transport uses Central-System-side queue/exchange/routing configuration complementary
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
RabbitMqConnector
      |
      v
UpstreamMessage
      |
      v
UpstreamGateway resolves NodeId only
      |
      v
node-scoped UpstreamStream
      |
      v
NodeUpstream
```

Each consumer must have controlled channel ownership. Arbitrary domain threads must not publish directly on shared RabbitMQ channels.

### RabbitMQ source-specific settings

Pseudo-configuration only:

```yaml
upstream:
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

PING scheduling belongs to the lifecycle of each configured upstream connector/session,
while node-scoped PING protocol state belongs to NodeUpstream and not to TimingData
persistence.

When a connector reaches its operational connected state, the owning lifecycle schedules
PING with:

```text
initial delay: 0
period:        30 seconds
```

The first execution publishes `PING(op=REQ, mode=HB)` immediately. Later executions
publish heartbeat PING REQUEST messages at the 30-second period while that connector
remains connected. A manual PING request omits `mode`; the answer does too. Manual
request/answer does not reset the heartbeat scheduler.

PING uses packetNr 0 in both directions. It therefore bypasses normal positive-ID
DN_PACKET stop-and-wait state and is never followed by RECV. A PING packet contains no
other semantic message. The receiver answers a PING REQUEST immediately, even when a
normal downstream packet is still awaiting confirmation.

When the connector disconnects, deactivates or is replaced, its scheduled PING task is
cancelled. Reconnect begins a new cycle with another immediate PING. Only one active PING
task may exist per active connector.

The Java implementation uses the application's existing scheduled-executor
infrastructure rather than introducing a separate timer thread solely for heartbeat
work. PING bypasses TimingData sequence allocation and LogBook persistence.

No missing-answer timeout or disconnect threshold is fixed yet. Transport-level
keepalive mechanisms may coexist with this application-level PING exchange but do not
replace IF06-REQ-011/012/013.

## Packet delivery and TimingData replay

Local TimingData commitment, packet delivery and external synchronization remain separate.

```text
TimingNode -> Central System
  LogBook seqNr 1..N
       |
       +--> UP_PACKET / TIMING_DATA
       +--> UP_PACKET / SEQ NTF
       +--> answer SEQ REQ
       +--> serve TIMING_DATA_REQ fromSeq=M
              by replaying retained LogBook records M..N

Central System -> TimingNode
  current Central state
       |
       +--> one normal DN_PACKET outstanding
               packetNr = delivery identity
               message  = RACE_DATA / SEQ / TIMING_DATA_REQ / ...
                    |
                    +--> SI-01 processes message
                    +--> UP_PACKET / RECV(receivedPacketNr)
```

### Downstream delivery

For one TimingNode, Central has at most one normal positive-ID DN_PACKET outstanding.
Central does not send the next normal positive-ID packet until the current one is
confirmed through RECV. If confirmation does not arrive, Central resends the exact same
packet with the same packetNr and semantic content.

SI-01 keeps enough receive state to recognize a resend of the already processed
downstream packet. It must not apply RACE_DATA or another state-changing message twice;
it repeats RECV for the packet already processed.

Central does not retain a historical RACE_DATA sequence. Once a downstream packet is
confirmed, its old wire packet is not required for future source replay. Central keeps
its current race/reference state and the one exact outstanding packet needed for retry.

RECV position 0 requests a complete resend of the applicable current Central-owned
downstream state. It is not a request for a retained RACE_DATA history.

### TimingData synchronization

TIMING_DATA is the only current application-data domain with durable sequence replay.
Its source identity remains the IF-05/LogBook sequence.

SEQ has REQ/ANS/NTF operations. Central may ask SI-01 for its current LogBook head; SI-01
may ask Central for the highest contiguous TimingData sequence Central processed; either
side may answer, and SI-01 may proactively notify a new source head.

Central requests actual records with TIMING_DATA_REQ from an inclusive IF-05 sequence.
When SI-01 handles that request it captures the current LogBook head and replays through
that captured position in bounded TIMING_DATA messages. Later commits are not
interleaved into the captured replay range. This request remains the replay-to-live
handoff barrier, including the empty-range case when Central is already caught up.

The LogBook is the durable replay payload history; SI-01 does not persist a duplicate
TimingData outbox solely for upstream recovery.

A reconnect creates a new transport session but does not create a new TimingData source
sequence. The peers refresh their TimingData positions through SEQ and use
TIMING_DATA_REQ where required. RACE_DATA recovery remains packet/state based rather than
source-history based.

No exact millisecond retry/backoff policy is fixed by this SDD.

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
    packet
      lastUpPacketNr
      lastDnPacketNr
      outstandingDnPacketNr
    timingData
      localHead
      remoteProcessedHead
      replayState
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
    semantic packet handling, downstream RECV/resend state, SEQ/TIMING_DATA_REQ replay state

io.messaging
    UpstreamGateway
    UpstreamStream
    Connector
    engineering/EngineeringApiConnector

io.messaging.rabbitmq
    RabbitMqUpstreamConnector
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
- Engineering API upstream adapter using structured public UpstreamData;
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

This is the fastest system-level feedback loop and does not require a network upstream service.

### ST-2 — Engineering API backoffice loop

Goal: verify the semantic upstream path through the existing Engineering Client and
IF-03 transport before broker-specific behaviour is introduced.

```text
SI-02 Central System Simulator
      | bidirectional IF-03 WebSocket
      v
EngineeringApiConnector
      |
      v
real SI-01 semantic upstream path
```

This profile verifies source/node routing, inbound/outbound semantics,
acknowledgement/synchronization and recovery of the engineering view without RabbitMQ.

### ST-3 — RabbitMQ integration

Goal: verify the production-shaped broker transport end-to-end with SI-02 as the
controllable Central System peer.

```text
SI-02 Central System Simulator
      |
RabbitMqCentralSystemTransport
      |
      v
hosted RabbitMQ
      ^
      |
RabbitMqUpstreamConnector
      |
      v
real SI-01
```

A hosted broker such as CloudAMQP is a suitable initial environment. This verifies
broker connection/channel/consumer behaviour, source-specific queues/routing,
packet acknowledgement/resend and reconnect/recovery scenarios. Hosted-broker
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
start SI-01 with RabbitMqUpstreamConnector
connect SI-02 Central System Simulator using RabbitMqCentralSystemTransport
exercise inbound/outbound source flows
force/recover broker or client connection where practical
verify packetNr handling, RECV/resend and TIMING_DATA SEQ/replay
clean up test topology
```

## Candidate requirements

Temporary identifiers only.

- **CAND-BO-001** — SI-01 upstream semantics shall be independent from the concrete communication transport.
- **CAND-BO-002** — The upstream transport shall be selectable through external configuration/composition.
- **CAND-BO-003** — An Engineering API upstream connector shall be available for deterministic ST-2 testing without requiring RabbitMQ.
- **CAND-BO-004** — The Engineering API connector shall carry structured public/reference UpstreamData through existing IF-03 HTTP/WebSocket transport.
- **CAND-BO-005** — RabbitMQ shall support a source-specific inbound queue configuration for each configured registration source.
- **CAND-BO-006** — RabbitMQ shall support source-specific outbound routing configuration for each configured registration source.
- **CAND-BO-007** — Multiple RabbitMQ source consumers shall be able to share one physical broker connection.
- **CAND-BO-008** — External transport callbacks shall not directly mutate timing-domain state.
- **CAND-BO-009** — Transport connection status and per-source inbound/outbound status shall be observable independently.
- **CAND-BO-010** — Loss of external upstream transport shall not discard locally committed registration data; LogBook remains the authoritative replay payload history.
- **CAND-BO-011** — Reconnection shall refresh TIMING_DATA positions through SEQ and use TIMING_DATA_REQ for missing LogBook records; downstream current-state recovery shall use DN_PACKET/RECV rather than a retained RACE_DATA source sequence.
- **CAND-BO-012** — Production broker/source topology, protocol details and credentials shall remain external/private configuration or implementation.
- **CAND-BO-013** — ST-3 shall support an external RabbitMQ test broker and an SI-02 Central System transport so the Engineering Client can exercise the upstream Central System role end-to-end.
- **CAND-BO-014** — SI-01 shall support zero or more configured upstream connectors within one application composition.
- **CAND-BO-018** — Each operationally connected upstream connector shall publish one immediate PING REQUEST with `mode = HB` and then another every 30 seconds until disconnect/deactivation; every valid PING REQUEST shall receive one PING ANSWER preserving optional HEARTBEAT mode (manual requests omit mode; correlation remains optional).
- **CAND-BO-015** — A upstream connector shall support bindings for one or more TimingNodes, and one TimingNode may be bound to more than one connector.
- **CAND-BO-016** — Connector-specific external names/routing identities shall not redefine the internal `TimingNodeId`.
- **CAND-BO-017** — Upstream routing/fan-out shall remain separate from concrete connector transport/resource handling.

## Open questions

- Within one RabbitMqUpstreamConnector, is one physical connection sufficient, or should consumer and publisher traffic use separate connections?
- Are RabbitMQ queues/exchanges pre-provisioned or should the application declare/bind any topology?
- At what point does RabbitMQ deserve its own Maven library rather than a `comm` package inside the core artifact?
- What connector-specific retry/backoff timing is appropriate for the Engineering API
  and RabbitMQ implementations?
- Should cached per-target TIMING_DATA processed progress be persisted for faster status
  restoration, even though the LogBook sequence remains authoritative and progress is
  refreshed through SEQ?
- What broker/client settings are appropriate on the Raspberry Pi Zero memory/CPU budget?

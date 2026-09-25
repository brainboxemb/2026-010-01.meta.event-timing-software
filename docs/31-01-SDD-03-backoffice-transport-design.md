# Backoffice transport detailed design

Status: working draft / non-authoritative

Software item: **SI-01 — Headless Timing Application**

This SDD defines the transport-independent backoffice boundary and two intended communication implementations:

- a lightweight **socket implementation** for automated loop/network system tests;
- a **RabbitMQ implementation** for production-shaped integration and deployment.

The application/domain model must not depend on RabbitMQ classes, socket classes, broker names, or the proprietary production message format.

Concrete production broker endpoint names, credentials, queue/exchange names, routing keys, external source IDs and message schemas are deployment/proprietary information and are intentionally excluded from this public repository.

Package/artifact placement follows `31-01-SDD-02-java-component-design.md`: a transport implementation can initially live under the framework `comm` packages and becomes a separate Maven library only when independent reuse, dependencies, lifecycle, ownership or release boundaries justify that split.

## Architectural goal

Backoffice semantics and transport are separate responsibilities:

```text
Timing/domain behaviour
       |
       v
Backoffice semantic boundary
  source-aware messages
  status
  outbox
       |
       +-----------------------+
       |                       |
       v                       v
SocketBackoffice           RabbitMqBackoffice
system-test transport      production-shaped transport
       |                       |
       v                       v
socket test peer           RabbitMQ broker
```

Both implementations must preserve the same logical `RegistrationSource` identity and feed the same serialized application/domain path.

## Semantic backoffice boundary

The reusable framework/domain side should work with semantic source-aware messages, not transport destinations.

Illustrative contracts:

```java
interface BackofficePublisherPort {
    void publish(RegistrationSourceKey source, BackofficeEnvelope message);
}

interface BackofficeInboundListener {
    void onMessage(RegistrationSourceKey source, BackofficeEnvelope message);
}
```

`BackofficeEnvelope` is a reusable/public semantic envelope or test representation. It must not force proprietary production serialization into the public framework.

These semantic contracts belong with the domain/backoffice responsibility that owns their meaning. Transport/session/wire types belong under `comm`.

The final system-level backoffice IDD can define the semantic obligations that both sides must fulfil while transport-specific/private specifications define their actual encoding where required.

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

This logical separation remains the same regardless of whether the selected transport is an in-memory stub, socket connection, or RabbitMQ.

## Transport selection and composition

Backoffice transport is selected through settings/application composition rather than compiled into domain code.

Pseudo-configuration:

```yaml
backoffice:
  transport: socket-test   # or rabbitmq
```

The executable application resolves this selection to a concrete communication implementation. A public reference/test application can use `socket-test` or a stub. A private/product application can select RabbitMQ plus private mappings/codecs where required.

This selection does not imply a separate Maven artifact for every transport. Initial implementations may coexist in the framework library while their boundaries are being tested.

## Socket test transport

### Purpose

The socket implementation provides a lightweight real communication boundary without requiring RabbitMQ or Docker.

It is intended for automated system tests that need to prove:

- SI-01 runs as a real process;
- source-aware messages cross a real TCP/socket boundary;
- inbound and outbound routing works for several sources;
- connect/disconnect/reconnect behaviour is observable;
- tests can run quickly and locally without production infrastructure.

It is not intended to define or expose the production backoffice protocol.

### Test topology

```text
System test driver / backoffice simulator
             |
             | simple TCP socket
             v
SocketBackoffice
             |
             v
Backoffice semantic boundary
             |
             v
framework domain/core
```

One connection can multiplex several logical registration sources because every test message includes a generic source key.

### Test framing

The exact framing remains an implementation choice. A simple public test protocol could use a length-prefixed or line-delimited synthetic envelope such as:

```text
sourceKey
messageType
payload
```

The socket test protocol must use only synthetic/public fields and must not copy proprietary production serialization.

The important contract is deterministic framing, source identity, reconnect behaviour and unambiguous message boundaries.

### Socket-loop scenarios

Candidate scenarios include:

- connect a backoffice simulator to a real application process;
- inject source-01 and source-02 messages over one connection;
- verify they reach the correct source path;
- trigger application behaviour through the normal application interface;
- observe outbound source messages at the simulator;
- drop the socket and verify status/reconnect behaviour;
- reconnect and continue without changing committed registration-sequence identity;
- exercise one or multiple `TimingNode`/asset/source combinations according to the selected executable topology.

## RabbitMQ transport

RabbitMQ is a concrete communication implementation beneath the same semantic boundary.

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
  BackofficeRouter
        |
        +-- BackofficeConnector connector-01
        |     -> RabbitMqBackofficeConnector
        |     -> 1..N TimingNode/source bindings
        |
        +-- BackofficeConnector connector-02
              -> RabbitMqBackofficeConnector
              -> 1..N TimingNode/source bindings
```

A `RabbitMqBackofficeConnector` owns its broker connection/channel/consumer/publisher resources internally. Those mechanics are implementation detail, not a separate architectural manager component.

One connector may multiplex several source-specific queues/channels over one physical broker connection. Separate connectors may use different brokers, credentials or routing domains. A TimingNode may intentionally participate in more than one connector.

Within one connector, separate consumer and publisher connections remain an implementation option when fault isolation, channel/thread ownership, broker-client behaviour or measured Pi Zero evidence justifies it. That refinement must not change the semantic connector boundary.

### RabbitMQ threading

RabbitMQ callbacks are external I/O callbacks and must not directly mutate timing-domain state.

```text
RabbitMQ consumer callback
      |
      v
source-aware BackofficeInboundMessage
      |
      v
BackofficeRouter resolves TimingNodeId / RegistrationSource
      |
      v
serialized framework/domain boundary
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

## Outbox and delivery

Local commitment and external transport are deliberately separated.

```text
RegistrationSource
  committed record
       |
       v
local outbox / sync state
       |
       v
BackofficePublisherPort
       |
       +--> SocketBackoffice
       |
       +--> RabbitMqBackoffice
```

A locally committed registration must not disappear because a transport is unavailable.

Working direction:

1. commit registration locally according to the final persistence rule;
2. represent it as pending in local outbox/synchronisation state;
3. selected transport attempts delivery;
4. transport acknowledgement/reconciliation advances pending state;
5. failure remains pending and visible through status.

The exact acknowledgement, retry, duplicate/idempotency and reconciliation rules belong to later requirements/IDD/detail design.

## Status model

Transport status and source status remain separately observable.

```text
BackofficeStatus
  selectedTransport
  connection/session state

  source-01
    inbound
      configured
      active
      lastMessage
    outbound
      pendingCount
      lastPublish
      lastFailure

  source-02
    ...
```

For RabbitMQ, connection status can additionally expose broker/authentication/recovery information. For socket testing, it can expose connected/disconnected peer state.

## Java package and future artifact placement

Working package direction inside the reusable framework:

```text
io.github.brainboxemb.eventtiming.domain.backoffice
    semantic backoffice contracts/state/outbox concepts

io.github.brainboxemb.eventtiming.comm.socket
    socket session/framing/test transport

io.github.brainboxemb.eventtiming.comm.rabbitmq
    RabbitMQ connection/channel/consumer/publisher implementation
```

This does **not** require three Maven libraries.

A future `event-timing-comm-rabbitmq` (or similarly named) artifact becomes useful when, for example:

- several applications need RabbitMQ independently;
- the RabbitMQ client dependency should be optional and excluded from non-RabbitMQ applications;
- lifecycle/release ownership needs an independent boundary;
- public/private implementation ownership requires extraction.

Until such evidence exists, clean package boundaries are sufficient and make later extraction straightforward.

## Public/private boundary

Public framework/test code may define:

- transport-independent semantic ports;
- generic `RegistrationSourceKey`;
- generic/test `BackofficeEnvelope`;
- socket-test communication implementation/protocol;
- RabbitMQ connection/consumer infrastructure if proprietary production codec details remain separate;
- synthetic RabbitMQ topology for integration tests.

Private components/configuration may provide:

- actual external source-ID mappings;
- actual broker topology names;
- proprietary message schemas/codecs;
- authentication details;
- production-specific retry/reconciliation protocol details where sensitive.

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

### ST-2 — Socket loop/network

Goal: add a real communication/process boundary with minimal infrastructure.

```text
application test driver --> real application process
backoffice simulator <----> simple socket implementation
```

This profile verifies source multiplexing/routing, network session state, disconnect/reconnect and outbound/inbound semantics without RabbitMQ.

### ST-3 — RabbitMQ integration

Goal: verify the production-shaped broker transport with a real disposable broker.

```text
system-test driver
      |
      +--> application interface
      |
      +--> RabbitMQ test broker (Docker Compose)
```

This verifies broker connection/channel/consumer behaviour, source-specific queues/routing, outbox recovery and broker restart scenarios.

These profiles complement unit/component tests and Pi Zero/hardware-in-the-loop verification; they do not replace them.

## Docker-based RabbitMQ test environment

RabbitMQ is a good candidate for a containerised integration dependency because it is a real external service with meaningful connection and recovery behaviour.

A future implementation/reference application can provide a small Compose environment:

```text
compose.yaml
  rabbitmq-test
```

The broker must use synthetic/public queue names and credentials.

Typical lifecycle:

```text
start RabbitMQ container
wait for health
start application
exercise several source consumers + publisher
stop/restart broker
verify consumer restoration + pending delivery
clean up
```

Docker remains optional for ST-1 and ST-2 so most behaviour can be tested without container startup cost.

## Candidate requirements

Temporary identifiers only.

- **CAND-BO-001** — SI-01 backoffice semantics shall be independent from the concrete communication transport.
- **CAND-BO-002** — The backoffice transport shall be selectable through external configuration/composition.
- **CAND-BO-003** — A lightweight socket transport shall be available for automated system/integration testing without requiring RabbitMQ.
- **CAND-BO-004** — The socket test protocol shall support multiple logical registration sources over a real communication boundary.
- **CAND-BO-005** — RabbitMQ shall support a source-specific inbound queue configuration for each configured registration source.
- **CAND-BO-006** — RabbitMQ shall support source-specific outbound routing configuration for each configured registration source.
- **CAND-BO-007** — Multiple RabbitMQ source consumers shall be able to share one physical broker connection.
- **CAND-BO-008** — External transport callbacks shall not directly mutate timing-domain state.
- **CAND-BO-009** — Transport connection status and per-source inbound/outbound status shall be observable independently.
- **CAND-BO-010** — Loss of external backoffice transport shall not discard locally committed registration data.
- **CAND-BO-011** — Reconnection shall restore configured source communication and resume pending outbound synchronisation.
- **CAND-BO-012** — Production broker/source topology, protocol details and credentials shall remain external/private configuration or implementation.
- **CAND-BO-013** — A disposable RabbitMQ broker shall be available for automated ST-3 integration tests.
- **CAND-BO-014** — SI-01 shall support zero or more configured backoffice connectors within one application composition.
- **CAND-BO-015** — A backoffice connector shall support bindings for one or more TimingNodes, and one TimingNode may be bound to more than one connector.
- **CAND-BO-016** — Connector-specific external names/routing identities shall not redefine the internal `TimingNodeId`.
- **CAND-BO-017** — Backoffice routing/fan-out shall remain separate from concrete connector transport/resource handling.

## Open questions

- What exact semantic messages belong in the public backoffice IDD?
- What minimal public socket-test framing should be used: length-prefixed binary, line-delimited JSON, or another simple representation?
- Should the socket implementation use one bidirectional connection or separate inbound/outbound sockets?
- Within one RabbitMqBackofficeConnector, is one physical connection sufficient, or should consumer and publisher traffic use separate connections?
- Are RabbitMQ queues/exchanges pre-provisioned or should the application declare/bind any topology?
- At what point does RabbitMQ deserve its own Maven library rather than a `comm` package inside the framework artifact?
- What is the production acknowledgement/reconciliation protocol?
- Which outbound items require durable local outbox persistence versus rebuildable state?
- What publisher-confirm/retry policy is required?
- How are duplicates/redeliveries detected and handled?
- What broker/client settings are appropriate on the Raspberry Pi Zero memory/CPU budget?

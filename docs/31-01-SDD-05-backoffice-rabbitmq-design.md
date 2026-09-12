# Backoffice and RabbitMQ detailed design

Status: working draft / non-authoritative

Software item: **SI-01 — Headless Timing Application**

This SDD describes the working RabbitMQ/backoffice architecture for multiple registration sources. It defines reusable connection, channel, configuration, status and test boundaries without exposing the actual production queue names, routing keys, source IDs or message protocol.

Concrete broker endpoint names, credentials, virtual hosts, queue/exchange names, routing keys and production message schemas are deployment/proprietary information and are intentionally excluded from this public repository.

## Architectural goal

Every configured `RegistrationSource` has its own logical inbound and outbound backoffice path.

Conceptually:

```text
RegistrationSource source-01
  inbound  <- broker queue dedicated/configured for source-01
  outbound -> broker routing endpoint for source-01

RegistrationSource source-02
  inbound  <- broker queue dedicated/configured for source-02
  outbound -> broker routing endpoint for source-02
```

The source separation is logical. It does **not** imply one TCP connection per source.

## RabbitMQ terminology

For clarity, receiving and sending are intentionally modelled differently:

- a consumer reads/delivers messages from a RabbitMQ **queue**;
- a publisher normally publishes to an **exchange** with a **routing key**;
- RabbitMQ routes that publication to one or more queues according to broker bindings.

Therefore the working configuration model uses:

```text
SourceMessagingConfig
  inboundQueue
  outboundExchange
  outboundRoutingKey
```

If the production system uses the default exchange or another direct-to-queue convention, the adapter can represent that through the same outbound endpoint abstraction without forcing the public domain model to call a publisher destination a queue.

## Connection topology

The preferred initial architecture is one RabbitMQ connection manager per SI-01 process.

```text
SI-01
  RabbitMqConnectionManager
        |
        +-- inbound consumer channel source-01
        +-- inbound consumer channel source-02
        +-- ...
        |
        +-- outbound publisher component
```

This allows many source-specific queues to be consumed over one broker connection while preserving independent source handling.

The application must not assume that one `RegistrationSource` equals one TCP connection.

### Possible two-connection refinement

A later implementation may use two physical connections:

```text
consumer connection
  +-- source-01 consumer channel
  +-- source-02 consumer channel

publisher connection
  +-- publisher channel(s)
```

Potential reasons include fault isolation, simpler channel/thread ownership, recovery behaviour or broker/client-library recommendations observed during implementation.

This is an implementation refinement, not a change to the per-source messaging contract. Evidence should decide whether the additional connection is worthwhile on the Raspberry Pi Zero target.

## Channel ownership and threading

RabbitMQ callbacks are external I/O callbacks and must not directly mutate timing-domain state.

For inbound traffic:

```text
RabbitMQ consumer callback
      |
      | capture source/config/message context
      v
BackofficeInboundMessage
      |
      v
route to TimingSystemInstance / RegistrationSource
      |
      v
serialized application/domain boundary
```

Each source-specific consumer should have clear channel ownership. The implementation should avoid uncontrolled concurrent use of one mutable channel from unrelated threads.

Outbound publishing should similarly be owned by a dedicated publisher component or controlled channel pool rather than allowing arbitrary domain threads to publish directly.

The exact Java RabbitMQ client/channel strategy belongs to implementation evidence, but the domain/application layer must only depend on a backoffice port.

## Source-specific configuration

RabbitMQ mappings belong in external settings.

Pseudo-configuration only:

```yaml
backoffice:
  host: ${BROKER_HOST}
  port: ${BROKER_PORT}
  virtualHost: ${BROKER_VHOST}
  credentials: external-secret-reference

systemInstances:
  - id: system-01
    registrationAssets:
      - id: asset-01
        sources:
          - key: source-01
            externalId: ${PRIVATE_SOURCE_ID_01}
            messaging:
              inboundQueue: ${PRIVATE_SOURCE_01_IN_QUEUE}
              outboundExchange: ${PRIVATE_SOURCE_01_OUT_EXCHANGE}
              outboundRoutingKey: ${PRIVATE_SOURCE_01_OUT_KEY}

          - key: source-02
            externalId: ${PRIVATE_SOURCE_ID_02}
            messaging:
              inboundQueue: ${PRIVATE_SOURCE_02_IN_QUEUE}
              outboundExchange: ${PRIVATE_SOURCE_02_OUT_EXCHANGE}
              outboundRoutingKey: ${PRIVATE_SOURCE_02_OUT_KEY}
```

The public framework defines the shape and validation rules. Actual broker/source mappings belong in private deployment configuration.

## Inbound source consumers

At application startup/reconnect, each configured source requiring inbound backoffice data causes an inbound consumer to be established.

Conceptually:

```java
for (RegistrationSource source : topology.registrationSources()) {
    SourceMessagingConfig messaging = source.messaging();

    consumerManager.startConsumer(
        source.key(),
        messaging.inboundQueue());
}
```

For two configured sources, two queue consumers therefore exist even though they can share the same RabbitMQ connection.

Inbound message semantics are intentionally not fixed here. Candidate categories include source/reference/configuration/control information, but the actual production protocol belongs in the future backoffice IDD/private protocol implementation.

## Outbound source publisher

Committed source records are offered to a transport-independent outbox/backoffice port first.

```text
RegistrationSource
  committed record
       |
       v
local outbox
       |
       v
BackofficePublisherPort
       |
       v
RabbitMQ adapter
       |
       v
configured exchange + routing key for that source
```

The domain must not construct RabbitMQ exchange names or routing keys.

Illustrative API:

```java
interface BackofficePublisherPort {
    void publish(RegistrationSourceKey source, BackofficeEnvelope message);
}
```

The RabbitMQ adapter resolves `RegistrationSourceKey` through `SourceMessagingConfig`.

## Delivery, acknowledgement and local outbox

A local committed registration must not disappear merely because RabbitMQ is unavailable.

The working direction remains:

1. registration becomes locally committed according to the final persistence rule;
2. an outbound item is represented in a local outbox/synchronisation state;
3. the RabbitMQ publisher attempts delivery;
4. successful broker acknowledgement advances/removes the pending outbox item according to the chosen persistence design;
5. failed/unavailable delivery remains pending and visible through status.

The exact publisher-confirm, retry, duplicate/idempotency and reconciliation rules remain future requirements/IDD/detail work.

The source `(RegistrationSystemId, SequenceNumber)` identity provides an important basis for upstream ordering/gap detection but does not by itself define the complete delivery acknowledgement protocol.

## Connection and source status

Status should distinguish process/broker connection health from individual source consumers/publishers.

```text
BackofficeStatus
  connection
    DNS/transport
    authenticated
    connected

  source-01
    inboundConsumer
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

One failed source consumer should therefore be visible separately from a total broker connection failure.

## Recovery direction

On RabbitMQ disconnect:

- local timing/registration continues where required local state/reference data is available;
- outbound data remains pending locally;
- source consumer status becomes disconnected/stale;
- reconnect is handled by the RabbitMQ adapter/connection manager;
- after reconnect, all configured source consumers are re-established;
- pending outbound items are resumed/reconciled;
- recovery must not invent new registration sequence numbers for already committed records.

Whether the RabbitMQ client performs automatic recovery or the application adapter owns explicit recovery is an implementation decision that must be tested rather than assumed.

## Public/private protocol boundary

The public framework may define generic semantic ports such as:

```text
BackofficePublisherPort
BackofficeInboundListener
SourceMessagingConfig
BackofficeStatus
```

The production implementation may remain private where it contains:

- actual broker topology names;
- actual source mappings;
- proprietary message schemas;
- proprietary serialization/deserialization;
- authentication details;
- production retry/reconciliation protocol details where sensitive.

A public stub/test adapter must be able to exercise the same public semantic contracts.

## Docker-based integration test environment

RabbitMQ is a good candidate for a containerised development/integration-test dependency because it is a real external service with meaningful protocol, connection and recovery behaviour.

A future implementation/reference repository should therefore provide a small Docker Compose test environment such as:

```text
docker compose
  rabbitmq-test
  optional test-support services later
```

The test broker should be disposable and use only synthetic/public queue names and credentials.

Example test lifecycle:

```text
start RabbitMQ container
      |
      v
start SI-01/reference app with test configuration
      |
      +-- create/connect source-01 consumer
      +-- create/connect source-02 consumer
      +-- publisher path
      |
      v
inject broker messages / registrations
      |
      v
assert source routing + outbox + status
      |
      v
stop/restart broker
      |
      v
assert reconnect + consumer restoration + pending delivery
```

Docker is appropriate here because it gives local development and GitHub Actions the same reproducible broker dependency. It is intentionally different from the documentation generator, where Docker would add complexity without meaningful benefit.

## Integration-test scenarios

The RabbitMQ integration suite should eventually cover at least:

- one source: inbound + outbound happy path;
- two or more sources sharing one broker connection;
- messages from source-01 never being routed as source-02;
- independent inbound queue consumers for each configured source;
- correct outbound exchange/routing configuration per source;
- connection loss while local registrations continue;
- queued/pending outbound delivery after broker recovery;
- broker restart and recreation/recovery of all source consumers;
- malformed/unknown inbound message handling;
- wrong/unavailable queue/configuration status;
- authentication/configuration failure;
- duplicate/redelivery behaviour once protocol semantics are defined;
- full-field simulation with many source consumers in one application process.

Pi Zero resource verification should separately measure the cost of the selected RabbitMQ client, connection count, channel count and source scale.

## Candidate requirements

Temporary identifiers only.

- **CAND-MQ-001** — Each configured registration source shall support a source-specific inbound backoffice queue configuration.
- **CAND-MQ-002** — Each configured registration source shall support a source-specific outbound backoffice routing configuration.
- **CAND-MQ-003** — Multiple registration-source consumers shall be able to share one RabbitMQ connection.
- **CAND-MQ-004** — RabbitMQ I/O callbacks shall not directly mutate timing-domain state.
- **CAND-MQ-005** — RabbitMQ connection status and per-source consumer/publisher status shall be observable independently.
- **CAND-MQ-006** — Loss of RabbitMQ connectivity shall not discard locally committed registration data.
- **CAND-MQ-007** — Reconnection shall restore the configured source consumers and resume pending outbound synchronisation.
- **CAND-MQ-008** — Actual production broker/source topology names and credentials shall be external configuration and shall not be required in the public framework repository.
- **CAND-MQ-009** — The integration-test environment shall support a disposable RabbitMQ broker suitable for automated multi-source and reconnect tests.

## Open questions

- Is one broker connection sufficient in production, or should consumer and publisher traffic use separate connections?
- Are queues/exchanges pre-provisioned by the backoffice environment or should SI-01 declare/bind any topology itself?
- What inbound message categories are source-specific?
- What is the production acknowledgement/reconciliation protocol?
- Which messages require durable local outbox persistence versus rebuildable state?
- What publisher-confirm and retry policy is required?
- How are duplicates/redeliveries detected and handled?
- Should source consumer channels be one-per-source for simplicity, or can a safely managed smaller channel strategy be used at high simulated scale?
- What broker/client settings are appropriate on the Raspberry Pi Zero memory/CPU budget?

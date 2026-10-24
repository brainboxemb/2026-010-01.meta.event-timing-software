# SI-01 Java Design Rules (GPD)

Status: working project guidance

## Purpose

This document contains practical Java design rules for
**SI-01 — Timing Point Application**.

The purpose is simple: when we add or review Java code, equivalent problems should be
solved in the same way. The rules mainly cover component responsibility, lifecycle,
events, queues, asynchronous work, logging, comments and tests.

This document is **not** a product specification. Requirements and the 43-01-SDD design
documents remain authoritative for product behaviour and detailed design.

## Who should read this

This document is written **first for a human developer or reviewer**.

A coding agent may also use it as a checklist, but the text must remain understandable
without knowing hidden project history. If a rule cannot be explained clearly to a human
reviewer, the rule is not written well enough.

Each rule therefore uses the same structure:

- **Rule** — what we normally do;
- **Why** — why the rule exists;
- **Example** — how it applies in this application;
- **Avoid** — a typical implementation that should trigger review.

## Useful terms

A few words occur repeatedly in the Java design:

- **owner** — the component that is responsible for a piece of behaviour or state;
- **desired state** — what the application currently wants to be true;
- **actual state** — what is currently true in the component or device;
- **reconcile** — read the current state, compare it with the requested state and
  perform the missing work;
- **event-triggered reconciliation** — let a state-change event wake a task. The
  task reads current state instead of replaying old event values;
- **serial lane** — a `SerialLane<T>` that owns one bounded typed FIFO and processes
  accepted items serially on an externally owned executor. A lane is not its own Java thread;
- **serial task runner** — a `SerialTaskRunner` that independently bounds eligible
  cooperative task steps and submits them directly to a Runtime-supplied single-thread
  `ScheduledExecutorService`; it does not introduce another `SerialLane`.

Example:

```text
TimingNode operation state is OPEN
        |
        v
Conductor requests:
AntennaManager.setInventoryRequired(...)
        |
        v
AntennaManager reconciles:
power -> initialize -> inventory
```

The Conductor owns the application decision and publishes desired state. The
AntennaManager owns the device sequence.

## Design rules

### DR-01 — Put a decision with the component that owns it

**Rule**

A component should decide only the behaviour it owns.

A caller says **what it needs**. The component that owns the mechanism decides
**how to achieve it**.

**Why**

Otherwise high-level classes slowly acquire knowledge about power switching, retries,
device protocols, persistence details and other implementation mechanics. That makes both
classes harder to change.

**Example**

Good:

```java
antennaManager.setInventoryRequired(true);
```

The Conductor tells AntennaManager whether inventory is required. AntennaManager may then
power the antenna, wait for stabilization, initialize it and start inventory. When all
TimingNodes are CLOSED, the Conductor calls `setInventoryRequired(false)`. Repeating the
same desired value is idempotent and is not an implicit retry.

**Avoid**

```java
antennaManager.powerOn();
antennaManager.initialize();
antennaManager.startInventory();
```

from Conductor. This makes Conductor responsible for AntennaManager internals.

Calling `setInventoryRequired(...)` is different: it states the outcome the system needs,
not the physical sequence. AntennaManager still owns recovery needed to restore the requested
state without requiring the Conductor to micromanage hardware.

The same ownership rule also guides package placement. A reusable technical mechanism
that knows nothing about SI-01 concepts belongs under `infra`; domain-specific
registration and behaviour stay with the owning Domain component.

Example:

```text
domain.system.TimingSystemConductor
        reads current TimingNode status and calculates desired inventory

io.devices.antenna.manager.AntennaManager
        accepts desired inventory intent and owns physical transitions and recovery

infra.setting.Setting<T>
        optional manager-private requested/applied/retry bookkeeping
```

A Setting is state, not a scheduler. It must not own a SerialLane, Future,
queue admission, retry loop, coalescing controller or component lifecycle merely
because its value can change asynchronously.

Do not introduce a shared settings object merely to avoid a direct semantic method call
between two components that already belong to the same composition owner. A settings
abstraction needs its own concrete reason, such as genuinely shared configuration or an
atomic multi-value contract.

---

### DR-02 — Construction should not secretly start behaviour

**Rule**

A constructor creates and validates an object. Construction must not start runtime
behaviour.

Internal software-component lifecycle is infrastructure, not functional component API.
Components that participate in generic lifecycle extend `LifecycleComponent` and implement
protected `onActivate()` / `onDeactivate()` hooks. `LifecycleComponent` owns the generic
active/inactive fact and the reusable inactive guard; concrete components do not duplicate
either with another `active` field or private `failIfInactive()` implementation.
The package-private lifecycle driver is owned by `infra.lifecycle`; callers do not invoke
public `activate()/deactivate()` methods on TimingNode, LogBook, NodeService, TagProcessor,
AntennaManager or TimingSystem.

A real process/runtime boundary may still expose an explicit public start/stop operation.
Functional operations such as `requestEnableInventory()` remain normal component API.

For an active component, `onActivate()` primarily establishes lifecycle/execution context.
If the component owns a serial lane and startup requires potentially blocking persisted-data
loading or state reconstruction, start the lane, admit that work to the owning lane and return
rather than performing or awaiting the work on the caller thread. Readiness is a separate fact
from lifecycle activation.

A data dependency is not automatically a lifecycle dependency. If one sibling component
later consumes facts produced by another, each component may still establish its own
execution context independently. Represent data-dependent operations as unavailable until
the required data arrives. Do not add cross-component activation preflights that inspect a
sibling's private lane or lifecycle state merely because data will flow between them.

Lifecycle order should express a real execution/ingress dependency. For example, start a
consumer lane before enabling a producer that may immediately emit work to it. The shared
`ComponentLifecycleManager` owns that order, rollback and reverse deactivation; sibling
components do not coordinate each other's internal lifecycle state.

Use the shared `LifecycleComponent` base and register the component itself:

```java
lifecycle.register(nodeService);
lifecycle.register(logBook);
lifecycle.register(tagProcessor);
```

Do not repeat lifecycle method references at every composition site and do not discover
lifecycle methods with reflection. The base class gives `ComponentLifecycleManager` one
compile-time lifecycle contract while keeping lifecycle driver methods out of the public
functional API.

**Why**

Object composition remains predictable. Creating an object should not unexpectedly start a
thread, connect to hardware, power a device or publish events.

**Example**

Good:

```java
AntennaManager manager = new AntennaManager(...);
lifecycle.register(manager);
```

The owning lifecycle coordinator later activates the registered graph. The AntennaManager
public API therefore contains antenna/control operations, not infrastructure lifecycle.

**Avoid**

A constructor that immediately self-tests all antennas or starts inventory.

If construction has an unavoidable side effect, that must be an explicit design decision,
not a convenience hidden in the constructor.

---

### DR-03 — One lifecycle word should mean one thing

**Rule**

Keep different lifecycle levels separate.

For SI-01 we use, for example:

```text
software component         LifecycleComponent onActivate / onDeactivate
TimingNode operation state  OPEN / CLOSED
LogBook failure diagnostics logging / failure events
antenna provider            initialize / startInventory / stopInventory / shutdown
```

**Why**

Using the same word for unrelated states makes call order and failure handling difficult
to understand.

**Example**

`Antenna.shutdown()` is clearer than `Antenna.close()` when there is no corresponding
`Antenna.open()`.

**Avoid**

Making AntennaManager lifecycle activation mean both:

1. establish the software component execution context; and
2. synchronously self-test all physical antennas before returning.

Those are different actions and may be requested by different owners.

When one owner coordinates the lifecycle of several child components, use the shared
`ComponentLifecycleManager` for ordered activation, rollback and reverse-order
deactivation. Register `LifecycleComponent` instances directly. Do not duplicate that
generic lifecycle algorithm or expose public activate/deactivate methods in each component.

---

### DR-04 — A synchronous event callback must be short

**Rule**

A callback from local `Event<T>` must stay short. When the event arrives from outside
the component's own serial lane, the callback may validate the event, hand work to that
lane and then return.

When the event is guaranteed to be emitted on the consumer's own serial lane, do **not**
mechanically re-admit it to that same lane. A short handler may update owned state and
admit the next task directly.

Do not perform blocking I/O, waits, retries or cross-component control directly in the
synchronous callback.

**Why**

Local event delivery is synchronous. Heavy work in a listener delays the component that
published the event and can accidentally propagate downstream problems back into it.

**Example**

For `TimingSystemConductor`, a TimingNode functional-state change only wakes its control task:

```java
node.PROPERTIES.CHANGED.subscribe(
        update -> update.contains(TimingNode.FUNCTIONAL_STATE),
        ignored -> wakeMainTask());
```

The handler may validate source identity and wake the existing control task, then returns.
The later control run reads TimingNode status with CURRENT consistency and calls
`AntennaManager.setInventoryRequired(...)`. That call only records desired state and wakes
the manager's own work when needed; physical reconciliation does not run in the synchronous
TimingNode event callback.

**Event and handler naming**

Use `Event<T>` / `EventSource<T>` for observable post-fact notifications. Do not add a
second registration style such as `onChange(Consumer<T>)`, `addListener(...)` or
`setCallback(...)` when the project event abstraction already fits.

Use these naming roles consistently:

```text
statusChangedEvent           private Event<Status> backing object
STATUS_CHANGED               public EventSource<Status> (illustrative)
onTimingNodeStatusChanged()  listener/handler method; TimingNode uses PROPERTIES.CHANGED
```

Private mutable `Event<T>` backing fields use lowerCamelCase and end in
`Event`. The exposed `EventSource<T>` keeps the semantic source name; do not
append `Event` merely because its backing object is an `Event<T>`.

An `onXxx(...)` method is a handler name, not a subscription API.

When a consumer only needs a subset of an event's values, use the normal
`EventSource.subscribe(filter, listener)` composition path. The Event evaluates the predicate
before listener delivery. Do not create a second Event merely to express the subset, and do not
put consumer-specific routing policy into the event owner.

`EventSource<T>` always has 0..N notification semantics. Do not introduce public
`SingleEvent` / `MultiEvent` variants or cardinality configuration merely because a
particular composition currently has one subscriber. When a relationship is semantically
a direct action to one owned component, use a normal method call instead of an event.

Event wiring is fixed before activation at the **smallest component owner
that owns both endpoints**. `subscribe(...)` is therefore a composition-time
operation; runtime operation is emit-only and the baseline `EventSource<T>`
exposes no `unsubscribe(...)`.

Apply the same ownership rule at every level:
- a top-level component wires relationships between its own child components;
- a parent component wires relationships that cross child-component boundaries;
- Runtime constructs objects and resolves configuration/routing data, but should
  not retain ownership of a relationship once a real component owns both ends;
- lifecycle methods never add or remove subscriptions.

Current examples:
- `TimingNode` owns node-internal links among LogBook, NodeService and
  TagProcessor;
- `TimingSystemConductor` subscribes to the TimingNodes it owns;
- `TimingSystem` binds AntennaManager observations to TimingNode ingress;
- `ApplicationConductor` orchestrates application lifecycle across complete
  TimingSystems but does not implement their internal event graph.

**Make externally wired relationships discoverable in both places:**
- The receiving component's class Javadoc states which owner installs the link.
- The owning component comments non-obvious event links, including whether a
  payload is consumed or merely wakes work that rereads CURRENT state.
- Similar ownership relationships use the same wiring pattern unless an explicit
  design decision records why they differ.

A developer inspecting either endpoint should be able to identify the component
that owns the relationship without searching for hidden Runtime rewiring.

A component's `activate()`, `deactivate()`, `start()` or `close()` changes component
or transport behaviour, not the application event graph. Do not hide
cross-component subscribe/unsubscribe wiring inside those lifecycle methods.

The `Event<T>` implementation may optimize the common 0/1-subscriber case internally.
That optimization remains invisible to callers: zero listeners need no listener container,
one listener may be stored directly, and only two or more listeners require an immutable
array representation. Subscription order remains stable. Concurrent runtime
`emit(...)` calls are allowed, but runtime rewiring is not part of the event contract.

`Event.emit(...)` isolates ordinary listener `RuntimeException` failures and
makes them available through `Event.DeliveryReport`. The emitter owns publication
of its domain fact, not the downstream work performed by arbitrary subscribers.
Do not require an emitter to inspect subscriber outcomes, infer whether a consumer
committed work, or implement a consumer-specific recovery policy.

A receiving component or its composition boundary owns its expected operational
failures (for example, a rejected enqueue to the LogBook Data Lane). It should
handle those failures locally, with relevant identity and diagnostics, without
putting subscriber-specific knowledge in the source component. Where repeated
`RejectedExecutionException` handling would obscure a named handoff, a small
execution guard may separate the queued operation from the caller-owned rejection
handler; it must not invent an alternative queue-admission protocol. Other
unexpected subscriber `RuntimeException` failures remain isolated by `Event`;
system-wide reporting of those failures belongs to event infrastructure/diagnostics,
not to domain event producers.

Initialization is also separate from events. TimingSystemConductor activation wakes its first
normal reconciliation run; that run reads CURRENT TimingNode status and sets the desired
AntennaManager inventory state. No synthetic status-change event is required.

**Avoid**

```java
property.onChange(this::onTimingNodeStateChanged);
```

This invents another event-registration mechanism next to `EventSource.subscribe(...)`.

Also avoid doing downstream device control directly in the synchronous source-event
callback.

For an event emitted by a task already running on the same owner lane, prefer:

```java
selfTestCompletedEvent.subscribe(this::onSelfTestCompleted);

private void onSelfTestCompleted(SelfTestResult result) {
    selfTestPassed = result.passed();
    startInventoryTaskIfNeeded();
}
```

when both operations are short and `startInventoryTaskIfNeeded()` only admits later work.
Do not wrap the callback in another one-step `YieldingTask` merely to bounce it through
the same `SerialTaskRunner` again.

---

### DR-05 — Let the queue operation decide whether work was queued

**Rule**

Attempt admission once and handle the result returned by the queue owner. Do not first
inspect lane/executor state and then try to queue the item.

At the generic typed-lane boundary:

- `SerialLane.offer(T)` performs one non-blocking admission attempt;
- `ACCEPTED` means the item is now owned by the lane;
- `FULL` means the bounded FIFO has no waiting capacity;
- `NOT_RUNNING` means the lane is not accepting items;
- a backing-executor `RejectedExecutionException` is different: the lane could not
  schedule its fixed queue worker and can no longer guarantee execution;
- direct `ArrayBlockingQueue`, `poll()` and queue-worker scheduling stay inside
  `SerialLane`.

Do not add a preflight `isRunning()` check before `offer(...)`; that creates a race
without adding information. The admission operation already decides whether the item was
accepted.

The generic lane does not own Runnable/Callable command semantics or result futures.
Result-bearing Domain adapters put the completion alongside the typed queued item. For
example, a LogBook query item carries its `CompletableFuture<R>`, while
`SerialLane<LogBookOperationItem<?>>` remains unaware of query semantics.

Domain boundaries may translate `FULL` / `NOT_RUNNING` when they own a different
policy. TagProcessor, for example, records ingress counters and drops/reports an observation
according to its bounded callback contract. A synchronous result-bearing LogBook boundary
may fail the caller instead.

**Why**

This pattern is redundant and race-prone:

```java
if (lane.isRunning()) {
    lane.offer(item);
}
```

The lane can stop between the two calls. The `offer(...)` result is the only admission
fact that matters.

**Examples**

A typed lane user should make the admission outcome explicit:

```java
switch (lane.offer(item)) {
    case ACCEPTED:
        break;
    case FULL:
        metrics.recordQueueFull();
        break;
    case NOT_RUNNING:
        metrics.recordNotRunning();
        break;
    default:
        throw new IllegalStateException("Unsupported offer result");
}
```

The bounded container remains an implementation detail inside `SerialLane`:

```java
if (!queue.offer(new QueuedItem<T>(item))) {
    return OfferResult.FULL;
}
```

**Avoid**

- a separate state check immediately before admission;
- silently ignoring `FULL` or `NOT_RUNNING`;
- recreating another queue around `SerialLane<T>`;
- adding Runnable/Callable wrappers when the queued value already has a meaningful type.

See DR-09 for observability.

---

### DR-06 — Use current state when only the latest state matters

**Rule**

When a component only needs to know **what is true now**, maintain or read one current
representation of that truth. Do not queue historical state snapshots and replay them later
as commands.

If the authoritative owner has several related current values, keep them as separate typed
properties and use one generic property container when consumers need change notification.
Each `Property<T>` owns one strongly typed value. The owner sets one or more properties
and then calls `PropertyContainer.update()`.

The container compares current values with its previous baseline and exposes one normal
project `EventSource<PropertyUpdate>`. One `PropertyUpdate` contains the complete list
of properties changed by that logical update. Do not invent a second callback/subscription
mechanism and do not create one bespoke Event field per property.

Use typed immutable `PropertyKey<T>` values when another component must identify a property.
Keep the mutable `Property<T>` handle private to its owner. A consumer that only reacts to
selected properties should filter the existing grouped change source, for example by testing
`update.contains(TimingNode.FUNCTIONAL_STATE)`; do not compare property-name strings.

For example, TimingNode sets LocationId + OPEN and then calls `properties.update()`; one
`PropertyUpdate` reports both properties. Lifecycle teardown may use
`PropertyContainer.sync()` to accept a silent baseline reset without emitting a normal
runtime change event.

A current-state controller may use the container change only to wake a reconciliation run.
The reconciliation then reads the owner's current values explicitly. This keeps event
history separate from current control state and makes initialization use the same path as
later updates.

Calculate intermediate decisions locally. If the result is already the desired state of
another owned component, pass it through that component's semantic API rather than copying
it into a DerivedProperty or introducing a shared-state bridge.

**Why**

A queue may contain old snapshots by the time they execute.

For example:

```text
OPEN -> CLOSED -> OPEN
```

If antenna behaviour only depends on current TimingNode state, replaying all three Status
objects creates unnecessary work and can briefly apply stale intent. Coalescing the wake
signals and letting the later Conductor run reread CURRENT state preserves the final truth
without an event queue or second property scheduler.

**Example**

Good startup flow:

```text
TimingNode construction
        |
        +--> functionalState = CLOSED
        +--> locationId = none

TimingNode.activate()
        |
        +--> start Task Lane
        +--> start Data Lane and admit persisted-data load as its first task
        +--> start TagProcessor ingress
        +--> return

Data Lane recovery
        |
        +--> read/validate persisted TimingData
        +--> rebuild committed LogBook TimingData
        +--> publish loaded-data fact to Task-owned derived views
        +--> report recovery failure separately when needed
        +--> does not define or reconstruct TimingNode functional state

TimingSystemConductor control run
        |
        +--> read TimingNode functionalState() directly
        |
        v
derive inventoryRequired = any TimingNode OPEN
```

Good runtime flow:

```text
TimingNode.PROPERTIES.CHANGED
        |
        v
AbstractTask.wake(SerialTaskRunner)
        |
        v
query current functionalState + derive inventoryRequired
        |
        v
AntennaManager.setInventoryRequired(inventoryRequired)
        |
        v
manager reconciles current inventory intent
```

The event callback only validates/wakes the consumer; it does not call AntennaManager,
wait on another lane or perform device control. Repeated wakes may be coalesced because the
later control run rereads CURRENT TimingNode status before deriving behaviour.

Current immutable snapshots and ordered mutable reads are different consistency choices on
the same typed query boundary. Use CURRENT when the query supports a safely published
completed snapshot; use ORDERED when the read must be sequenced after earlier queued node
work. Mutable LogBook traversal remains ORDERED. A result-bearing ORDERED call made
reentrantly from that same lane must fail immediately rather than queueing behind itself and
appearing later as a timeout.

**Avoid**

- queueing every `Status` object and later executing each one as if it were a command;
- hiding an initial authoritative read inside a property initializer or Future;
- forcing a CURRENT-capable immutable snapshot through the serial lane solely because other queries are ORDERED;
- allowing same-lane result-bearing reentrancy to wait until timeout;
- giving a property its own executor/coalescing loop when the owning component already has one.

Not every event should be coalesced. TimingData records, registrations and other records
that must be preserved are different: there the individual event itself matters.

---

### DR-07 — A downstream operational failure should stay downstream

**Rule**

A queue-full condition, stopped consumer or recoverable device failure should be handled by
the component that owns that condition. Do not throw it back through an unrelated
synchronous event producer.

**Why**

Otherwise a Conductor queue problem can become a TimingNode command failure simply because
the TimingNode happened to publish an event.

**Example**

For a Conductor callback:

```text
offer(reconcile) -> FULL
        |
        +--> record diagnostic/metric
        +--> keep failure inside Conductor
        +--> do not throw into TimingNode event delivery
```

**Avoid**

```java
if (admission == FULL) {
    throw new IllegalStateException(...);
}
```

inside a synchronous event listener.

Programming errors such as a required argument being `null` may still fail immediately.
This rule is about operational failures, not hiding programming mistakes.

---

### DR-08 — Keep asynchronous lifecycle work with its owner

**Rule**

The class that owns a lifecycle should also own the sequence of asynchronous steps needed
for that lifecycle.

Helpers should remain narrow.

**Why**

Otherwise a helper grows into a second manager and ownership becomes unclear.

**Example**

For antennas:

```text
AntennaManager
    owns:
      lifecycle/status boundary
      requested/applied inventory setting
      deciding when a task should start or cancel

task/
    owns:
      cooperative multi-step device sequences
      task-local state such as antenna index, phase and switch position
      its current execution handle/Future when one is needed
      its completion event

ManagedAntenna
    owns:
      direct one-antenna device actions + runtime state
```

There is deliberately no second inventory or switching controller. Switching is one
cooperative state machine (`AntennaSwitchTask`) owned by the manager's reusable task set.

**Avoid**

Adding an `InventoryController` or `AntennaSwitchController` merely to move parts of the
same manager decision into another object. Also avoid putting device sequencing back into
`AntennaManager`; the manager chooses when a task starts, while the task owns its steps
and any execution handle required to represent that run. Do not keep a
`CompletableFuture` field in the manager merely to observe a task's normal completion;
prefer the task's completion event.

If several components genuinely need the same low-level scheduling primitive, that
primitive may live in Platform. Component policy stays with the component.

---

### DR-09 — Status, metrics and logging have different jobs

**Rule**

Use the three mechanisms for different questions:

```text
status   -> What is true now?
metrics  -> How often or how much?
logging  -> What happened, in what order, and why?
```

**Why**

One mechanism cannot replace the others.

A queue-full counter tells us that overload occurred, but not which control decision was
being attempted at that moment. A log tells the story, but should not be used as the
authoritative current status.

**Level intent**

Use levels consistently across components:

| Level | Generic use |
| --- | --- |
| TRACE | high-rate/raw technical facts that are useful only for deep tracing |
| DEBUG | internal decisions, filtering, reconciliation and detailed diagnostic flow |
| INFO | meaningful operational facts, lifecycle transitions and completed business/commit boundaries |
| WARN | recoverable anomaly, rejected/degraded work or automatic repair that deserves attention |
| ERROR | failure that prevents a component from reliably fulfilling its role |

Do **not** promote every high-rate observation to INFO. Normal INFO output must remain
readable as an operational narrative.

Log at the component that owns the fact, and log the fact only after it is true. For
example, a successful write/commit message belongs after the complete commit boundary;
a request or attempt must not be phrased as if success already happened. When a separate
design defines a domain-specific logging matrix, follow that matrix instead of scattering
level choices through implementations.

Recurring operational boundaries should use **stable semantic prefixes and stable key
names** instead of ad-hoc prose. This makes a normal INFO log readable as a sequence and
lets operators filter the same fact across releases. For the registration/upstream path,
the normal vocabulary is:

```text
Registration accepted:
LogBook persisted:
Upstream queued:
Upstream sent:
Upstream connected:
Upstream disconnected:
```

The owner still determines the fields following that prefix. LogBook owns durable
persistence facts; the semantic upstream owner summarizes IF-06 messages; the transport
owner logs session connection/disconnection. INFO summaries stay compact. Exact encoded
payload belongs at DEBUG/TRACE when useful.

A transport log follows the **actual message boundary**, not every item contained in a
batch. For example, one TIMING_DATA message containing records 578 through 593 produces
one queued/sent batch summary such as `seq=578..593, records=16`; it must not produce
sixteen transport INFO lines merely because the message contains sixteen records.

Logging I/O must not become hidden application backpressure. When normal logging writes
to potentially blocking sinks such as console, files or network transports, Infrastructure
must isolate that I/O from Domain/Application execution with bounded non-blocking handoff.
Overload may lose diagnostic records, but must not stall a timing/control lane. The detailed
queue, writer and flush mechanics belong to the logging component design rather than to
individual business components.

A useful log line normally includes the relevant stable identity and the cause/reason
when something failed. Logging remains diagnostic history; it is not authoritative
current state, a metric store or a substitute for durable domain persistence.

---

### DR-10 — Comments should explain things the code cannot say clearly

**Rule**

Write comments and Javadoc for **ownership, lifecycle, threading, invariants and reasons**.
Do not use comments merely to translate Java syntax into English.

Every constructor and method should have a short Javadoc or immediately adjacent
comment that states its purpose. Private helpers are included. The comment may be one line
when the purpose is simple, but an undocumented method should be treated as a review issue.

Comments must still add meaning rather than translate syntax. A comment that starts with
`Returns...`, `Creates...`, `Verifies...` or `Publishes...` should trigger review when
it only turns the method name into an English sentence. Keep such wording only when it adds a
caller-visible contract, invariant or ownership rule that is not already obvious from the
name and signature.

For component boundaries, threading/lifecycle helpers or non-obvious code, explain:

1. what the component or method is responsible for;
2. what it is deliberately not responsible for when that matters;
3. important lifecycle/call-order rules;
4. important threading or serial-lane assumptions;
5. the reason for a non-obvious implementation choice.

At an execution boundary, the Javadoc must also make caller-visible execution behaviour
explicit when the method name alone does not already make it obvious. State whether the call:

- returns directly without waiting for queued work;
- blocks until an ordered operation/result completes;
- queues fire-and-forget work and returns after queue admission;
- invokes event/callback listeners synchronously on the emitting thread or lane.

Do not leave this to implementation archaeology. In particular, a method that returns
`void` must not force a reviewer to guess whether the requested work is already complete,
merely queued, or still being delivered synchronously.

Keep simple accessor comments simple. Do not add adjectives such as `immutable`,
`resolved`, `authoritative` or `logical` unless that distinction is relevant to the
caller's contract. For example, `Returns the antenna assigned to this node` is clearer
than `Returns the resolved antenna identity for this logical TimingNode` when there is
no unresolved or mutable alternative.

Names should carry ordinary control-flow meaning where possible. Do not make a reader
learn low-level queue/executor jargon to understand Domain code.

**Naming guideline**

Prefer names that tell a reader what the object or operation means in the current
architecture, without first knowing the implementation mechanism.

| Intent | Prefer | Avoid at Domain/Application level |
| --- | --- | --- |
| Process a LogBook command and return its domain result | `process(command)` | `invoke(command)`, public `executeAndWait(command)` |
| Execute a fire-and-forget LogBook command | `execute(command)` | `queue(command)`, `offer(...)`, `submit(...)` at the Domain boundary |
| Try to queue internal lane work without waiting | `tryQueueOnTaskLane(work)` | exposing queue-container operations outside the lane owner |
| Work is waiting to run | `QUEUED` | `ACCEPTED` |
| Queue cannot accept more work | `QUEUE_FULL` | bare `FULL` outside the queue primitive |
| Execute serially and return the result | `executeOnDataLaneAndWait(...)` | generic `run(...)` when waiting is important |
| Active component that owns LogBook behaviour | `LogBook` | `LogBookProcessor` when it is more than a processor |
| Passive committed TimingData | `LogBookData` | another active-sounding `LogBook` |
| Node Task Lane service | `NodeService` | `NodeTaskRunner` when it owns domain state as well |
| Actual input-processing component | `TagProcessor` | renaming merely for suffix consistency |
| Registration being matched for revoke | `activeRegistration` | `candidate` |
| Team ID read from static EventData | `configuredTeamId` | `fixed` |
| Contract assertion that throws `IllegalStateException` when false | `failIfIllegalState(state == NEW, ...)` | `checkState(...)`, inverted failure conditions |
| Contract assertion that throws `IllegalArgumentException` when false | `failIfInvalidArgument(value != null, ...)` | `checkArgument(...)`, inverted failure conditions |
| Guard that throws when a runtime condition holds | `failIfInactive()` | `requireActive()` when the throw behaviour is otherwise hidden |

Keep a simple contract guard visually simple. When the condition and message are short,
keep the complete `failIfInvalidArgument(...)` or `failIfIllegalState(...)` call on one
source line:

```java
failIfInvalidArgument(registrationId != null, "registrationId must not be null");
```

Do not spread the same trivial check over several lines merely because a formatter permits it:

```java
failIfInvalidArgument(
        registrationId != null,
        "registrationId must not be null");
```

If a contract condition is genuinely too complex to read on one line, name the condition
or extract a meaningful helper first. Do not make the guard call itself look structurally
complex when the contract is simple.

For LogBook data, name the concrete thing being handled. Prefer `TimingData record`,
`registration`, `committed TimingData` or `persisted TimingData` as appropriate. Avoid the
generic word `history` for LogBook data because it hides which records or registrations the
code actually owns.

Do not introduce a `Runner` merely because a component has a task. `SerialTaskRunner`
is an execution mechanism with a narrow responsibility: it runs cooperative
`YieldingTask` steps. Concrete tasks/components keep their own domain or device state and
retain responsibility names such as `NodeService`, `AntennaManager` or `MainTask`.

Use `Executor` for objects that implement or concretely represent Java
`Executor`/`ExecutorService` execution resources. Do not call a
`ThreadPoolExecutor` or `ScheduledThreadPoolExecutor` a `worker`: the executor
owns/schedules work while one or more Java threads perform that work.

Thread names should identify the **functional role**, not restate that they are threads.
Do not mechanically append `-worker` or `-thread`. The surrounding thread dump,
debugger or `Thread` API already supplies that context. Add a numeric suffix only when
one executor may create multiple threads. For example:

```java
ThreadPoolExecutor timingNodeExecutor = ...;
ScheduledThreadPoolExecutor tagProcessorScheduledExecutor = ...;

threadFactory("tp-dl-node");
threadFactory("tp-dl-tagproc");
```

For counts of actual Java threads, prefer names such as `SHARED_IO_THREADS` rather than
`SHARED_IO_WORKERS`.

When a logical `SerialLane` depends on such an executor, name the dependency
`backingExecutor` (or another explicit executor name), not `workerExecutor`.
Likewise, a field or accessor containing a `SerialLane` should say `Lane` when
that distinction would otherwise be ambiguous (for example `dataLane()` or
`observationLane`). A `SerialTaskRunner` should be named `taskRunner` or by the
cooperative responsibility, not disguised as a generic data lane.

Use `Processor` when processing input is the actual responsibility, as with
`TagProcessor`. Do not add `Processor`, `Manager`, `Controller` or `Service`
merely because a class is active. Prefer the responsibility itself when that produces
a clear noun.

Technical names may still exist inside the implementation that owns the technical
contract. The important rule is to translate them at the next architectural boundary.

**Why**

A reviewer should not have to reverse-engineer a 300-line class before understanding why
it exists or which thread is allowed to call it.

**Good comment**

```java
/*
 * Only one member of the multiplex group may inventory at a time.
 * The AntennaManager serial lane is the single writer of activeIndex,
 * so this helper needs no internal locking.
 */
private int activeIndex = -1;
```

This explains an invariant and why locking is absent.

**Poor comment**

```java
// Increment the index.
activeIndex++;
```

The code already says that.

Another warning sign is a very large comment needed to explain why one class performs many
unrelated jobs. In that case simplify or split the code first.

Comments are maintained code. When ownership or behaviour changes, update or remove the
old comment in the same pull request.

For lambdas and callbacks, prefer the form that is easiest to understand in context.
A lambda is fine when it is genuinely clearer or measurably useful in a hot path. Do not
avoid a lambda merely because it is a lambda. However, a callback must not hide its purpose
behind syntax alone.

Use the following rule:

1. **Trivial callback:** keep the lambda inline when the operation and callback role are
   immediately obvious from the receiving method.
2. **Meaningful callback:** declare a local variable with the explicit functional-interface
   type and a name that describes the callback's role before passing it to the boundary.
   This applies not only to `Runnable` and `Callable`, but also to types such as
   `Consumer<T>`, `BiConsumer<T,U>`, `Function<T,R>`, `Supplier<T>`,
   `Predicate<T>` and similar project/API callback contracts.
3. **Multi-step or lifecycle callback:** prefer a named method and method reference when
   the callback performs several operations, changes state, owns error/lifecycle handling,
   or is clearer as a reusable operation.

For example, this is fine when the named method already explains the callback:

```java
currentRunFuture.whenComplete(this::runCompleted);
```

When an execution call is easier to scan without the lambda body inside its argument list,
prefer:

```java
Callable<R> commandApplication = () -> applyCommand(command);
return submitAndWait(commandApplication, command.name());
```

over:

```java
return submitAndWait(() -> applyCommand(command), command.name());
```

The same rule applies to a real synchronous lock/transaction boundary. Name the deferred
work first when that makes the operation easier to read:

```java
Supplier<CommandResult> processRevocation =
        () -> CommandResult.committed(logBook.process(command));

return timingNode.processLocked(processRevocation);
```

A method such as `processLocked(...)` must document what the boundary actually does:
the Supplier runs synchronously on the caller thread while the lock is held; it is not
queued work and it must not imply commit/rollback semantics that do not exist.

Do not introduce a callback merely to express a direct semantic request. For example,
`antennaManager.setInventoryRequired(inventoryRequired)` is clearer than wrapping one
Boolean in a transaction/callback abstraction. Use an explicitly named callback variable
when the receiving API genuinely accepts deferred or transactional work.

The local name should describe the deferred/callback operation, not the lambda syntax.
This is especially useful at serial-lane, task-runner, asynchronous-execution,
configuration-update and event/callback boundaries where the distinction between invoking
the boundary and the work performed by the callback matters.

Do not add a comment merely to explain `() ->`, `->`, captured variables or the fact
that a functional interface is invoked later. A comment is appropriate only when it
explains ownership, threading, lifecycle, transaction semantics or another reason that
the code itself cannot express clearly.

---

### DR-11 — Use clear English and established project words

**Rule**

Java source uses English for:

- class/method/field names;
- comments and Javadoc;
- logs and exception messages;
- test names and test failure messages.

Use the terminology already established in the design instead of inventing a synonym in
each class.

**Why**

Consistent terms make code searchable and prevent two names from appearing to describe two
different concepts.

**Example**

Keep these distinctions:

```text
activate / deactivate       software component lifecycle
OPEN / CLOSED               TimingNode state
LogBook failure diagnostics  TimingData persistence/commit problem reporting
initialize                  prepare antenna provider
startInventory              start tag inventory
shutdown                    release antenna/provider resources
```

Prefer:

```java
requestEnableInventory()
requestDisableInventory()
currentInventoryIndex
```

over vague names such as:

```java
handle(...)
process(...)
doWork(...)
flag
data
obj
```

when the more precise meaning is known.

Logs and exceptions should also be normal, concise English. They should describe the
operational problem, not expose arbitrary implementation trivia.

---

### DR-12 — Test the design assumption, not only the happy path

**Rule**

If correctness depends on queue bounds, lifecycle ordering, cancellation, coalescing or
failure containment, write a focused test for that exact behaviour.

**Why**

A normal successful test says nothing about what happens when the queue is full or a
provider fails during a delayed transition.

**Examples**

For Conductor:

- `TimingNode.activate()` returns while persisted TimingData is still being loaded on the
  Data Lane;
- Task Lane activation is independent of LogBook state and does not require a preflight
  against the Data Lane;
- TimingNode Status is readable as CLOSED/no-location independently from LogBook recovery;
- a persistence command waits for ordered LogBook recovery before it can commit;
- a recovery failure is reported separately and does not redefine OPEN/CLOSED Status;
- a functional-state change only wakes the control task; no shared Settings object is used;
- every control run reads current TimingNode Status before deriving desired inventory;
- rapid state changes converge to the final desired inventory while control wakes coalesce;
- one OPEN node among several nodes keeps the AntennaManager inventory request enabled;
- CURRENT-state failure after readiness is explicit and is never interpreted as CLOSED;
- no downstream control failure throws back through TimingNode event delivery.

For AntennaManager:

- one self-test failure must not prevent another configured antenna from completing its self-test;
- a disable request arriving during power stabilization must prevent stale inventory start;
- only one multiplex-group member may inventory at a time.

A test should make the design rule visible. Avoid tests that merely duplicate the
implementation line by line.

### DR-13 — Keep normal control flow linear

**Rule**

Use an early `return` for a guard, precondition or invalid state at the beginning of a
method.

For two or more normal, equivalent business paths, prefer an explicit `if / else`
structure and let the method continue to its normal end. Avoid using a `return` in the
middle of one normal branch merely to avoid writing `else`.

**Why**

A reader should be able to distinguish immediately between:

- a condition that says "this method has nothing valid to do"; and
- a normal business decision between two valid paths.

Scattered returns inside the main flow make one normal path look exceptional and make the
control flow harder to scan, especially in orchestration code.

**Example**

Good guard:

```java
if (!ready
        || busy
        || !inventoryEnabledSetting.changePending()) {
    return;
}
```

Good normal choice:

```java
if (inventoryRequestedEnabled()) {
    startEnableOperation();
} else {
    stopSwitching();
    startDisableOperation();
}
```

**Avoid**

```java
if (inventoryRequestedEnabled()) {
    startEnableOperation();
    return;
}

stopSwitching();
startDisableOperation();
```

Both enable and disable are normal paths. The early `return` incorrectly makes the
enable path read like a special case.

This is a readability rule, not a prohibition on multiple returns. Additional early
returns are appropriate when they are true guards, fail-fast validation or other
conditions that terminate the method before its normal main flow starts.

---

### DR-14 — Reuse owned stateful helpers for recurring work

**Rule**

When a long-lived component repeatedly performs the same responsibility, prefer one
long-lived owned helper/task object whose execution state is explicitly reset for a new run.

Do not create a new mutable state-machine/helper object for every invocation merely because
construction happens to reset its fields.

This rule is about objects that represent a stable owned responsibility. It is **not** a
general requirement to pool short-lived immutable values, events, DTOs or other ordinary
temporary data.

**Why**

A recurring stateful task is part of the owning component's runtime structure. Recreating
it for every run hides the lifecycle in object allocation, creates unnecessary garbage and
makes it less obvious which state must be reset before reuse.

Explicit reuse makes the lifecycle visible:

```text
construct component
    |
    +--> construct task once
             |
             +--> start -> run steps -> DONE
             |
             +--> reset/start -> run steps -> DONE
             |
             +--> reset/start -> ...
```

The task's reset/start operation must restore all per-run state before the task is admitted
again. A task must never be restarted while a previous execution is still active.

**Example**

Prefer:

```java
final class InventoryDisableTask implements CooperativeTask {
    private int antennaIndex;
    private Phase phase;
    private RuntimeException failure;

    void reset() {
        antennaIndex = antennas.size() - 1;
        phase = Phase.STOP_INVENTORY;
        failure = null;
    }
}
```

with one `InventoryDisableTask` owned by the manager's reusable `AntennaTasks` set.

**Avoid**

```java
void disableInventory() {
    runner.runTask(
            new InventoryDisableTask(antennas));
}
```

when disable is a normal recurring operation and the new object exists only to obtain a
fresh index/phase/failure state.

Also avoid generic object pooling for stateless or cheap value objects. Reuse should follow
stable ownership and recurring responsibility, not become an optimization ritual.

---

### DR-15 — Device completion belongs to the device owner

**Rule**

When a device/provider operation can complete later, start the operation explicitly and
let the component that owns that operation publish its completion/result.

Do not make a caller infer operation completion from a configured delay. A delay is only
appropriate when the delay itself is the physical requirement, such as power stabilization.

**Why**

These are different facts:

```text
power switched on
    -> wait 200 ms because hardware requires stabilization

self-test started
    -> wait until the antenna reports that the self-test finished
```

The first is a time requirement and fits `TaskStep.after(...)`.
The second is an operation-completion relationship. When a `CompletionStage` already
represents that dependency, a cooperative task can return `TaskStep.await(completion)`;
otherwise use an event or equivalent owner-controlled completion signal and wake the task
from that completion.

This keeps provider timing and protocol details inside the device boundary and allows the
caller to remain event-driven.

**Example**

Prefer:

```text
AntennaManager
    -> antenna.startSelfTest()

ManagedAntenna
    -> performs self-test on its serial task runner
    -> emits selfTestCompletedEvent(result)

AntennaManager event listener
    -> admits the result to its own serial lane
    -> returns immediately
```

**Avoid**

```java
Duration delay = antenna.startSelfTest();
return TaskStep.after(delay);
```

when the returned duration is merely a guess for when the self-test will be complete.

A concrete provider may itself use cooperative tasks, callbacks, protocol events or bounded
polling internally. That implementation choice must not leak into the manager contract.

---

### DR-16 — Keep contract failures explicit and assertions positive

**Rule**

Use compact helpers for programming-contract failures such as required state or argument
validity.

The caller always supplies an **assertion of the valid contract**:

```text
true  = contract holds
false = fail now
```

Use:

```java
failIfIllegalState(assertion, message, ...);
failIfInvalidArgument(assertion, message, ...);
```

The helper name makes the runtime failure visible, while the Boolean expression reads like
a normal assertion. Do not invert every caller into an error condition merely because the
method name starts with `fail`.

These helpers are ordinary always-enabled Java methods. They are **not** the Java
`assert` keyword and must not disappear when assertions are disabled.

Keep normal business decisions as ordinary control flow. A contract-failure helper must
not hide a recoverable condition, device result or normal application branch.

When a recoverable runtime guard depends only on generic component lifecycle, keep the guard
with `LifecycleComponent` rather than reimplementing it in each concrete component. For
example, `LifecycleComponent.failIfInactive()` owns the active-state check. A concrete
component may configure the caller-visible failure factory so the lifecycle package remains
independent from domain/application exception types. Avoid a private `requireActive()` or
`failIfInactive()` wrapper that merely repeats the lifecycle check.

**Why**

Repeated exception boilerplate makes a simple contract dominate the visual structure of a
method. Positive assertions are also easier to review consistently than a mixture of
positive and inverted failure conditions.

**Example**

Prefer:

```java
synchronized (this) {
    failIfIllegalState(
            state == State.NEW,
            "AntennaManager must be NEW, was %s",
            state);
}
```

The expression states the required invariant. The helper throws
`IllegalStateException` when that assertion is false.

For arguments:

```java
failIfInvalidArgument(
        controlLane != null,
        "controlLane must not be null");
```

The helper throws `IllegalArgumentException` when the assertion is false.

The project may provide these small helpers directly rather than adding a broad utility
dependency solely for precondition syntax. Static imports are preferred at call sites when
they improve readability.

**Avoid**

Inverting the expression into the failure condition:

```java
failIfInvalidArgument(
        controlLane == null,
        "controlLane must not be null");
```

That contradicts the project convention: the argument must describe what is valid.

Also avoid using a contract helper as normal application flow:

```java
failIfIllegalState(
        inventoryRequestedEnabled(),
        "inventory must be enabled");
```

when disabled inventory is a valid runtime state. That belongs in ordinary task/state
logic, not in a programming-contract assertion.

---

### DR-17 — Name asynchronous boundaries

**Rule**

Do not hide event delivery, queueing or thread/lane transfer inside nested lambda
expressions.

At an asynchronous boundary, prefer a named method reference and move the queueing step
into that method. The call site should read as the architecture reads.

The boundary method must make wait semantics visible. A fire-and-forget method should
say that it queues work and returns immediately; a result-bearing method should say that
it waits for ordered execution. Avoid exposing generic `offer`, `admission`, `submit` or
`submission` vocabulary from Domain/Application APIs when ordinary queueing words are clearer.

A lambda that executes **synchronously** inside a genuine transaction API is different.
Keep a short lambda where it makes that transaction visible, and explain non-obvious
publication semantics at the API boundary. Do not introduce a transaction callback solely
to move one desired Boolean between components already owned by the same composition.

**Why**

Nested lambdas compress multiple execution contexts into punctuation. The code may be
shorter, but a reader can no longer see where the event callback ends and where serial
execution begins.

**Example**

Prefer:

```java
antenna.selfTestCompletedEvent()
        .subscribe(
                this::onSelfTestCompleted);

private void onSelfTestCompleted(
        AntennaSelfTestResult result) {
    taskRunner.execute(
            () -> selfTestCompleted(
                    result));
}
```

The names make the two boundaries explicit:

```text
device event callback
        |
        v
onSelfTestCompleted
        |
        v
manager serial lane
        |
        v
selfTestCompleted
```

**Avoid**

```java
antenna.selfTestCompletedEvent()
        .subscribe(
                result ->
                        taskRunner.execute(
                                () -> selfTestCompleted(
                                        result)));
```

Also avoid extracting meaningless methods such as `handle(...)` or `process(...)`.
The extracted method must name the execution/event boundary it represents.

Do not extract a private helper merely to shorten the caller or relocate `try/catch`,
branches or ordinary control flow. An extraction must expose a real mechanism,
architectural boundary or owned responsibility. If no such concept exists, keep the
control flow where the decision is made.

---

### DR-18 — Keep line wrapping readable

**Rule**

Use **120 characters as the maximum Java source line length**.

Do not wrap a statement merely because it has multiple arguments. When a complete,
readable statement fits within 120 characters, keep it on one line. This applies equally
to assignments, constructor/method calls, callback declarations and method references.

"One declaration per line" means do not combine unrelated variables such as
`int width, height;`; it does **not** mean moving a short initializer onto its own line.

Wrap only when the line would exceed 120 characters or when the expression has enough
logical structure that line breaks genuinely improve understanding. Explicitly naming a
meaningful `Runnable`, `Callable` or `Consumer` (DR-10/DR-17) does not require the
initializer itself to be split across lines.

**Why**

Over-wrapping turns simple Java into tall visual noise and hides the actual control flow.
Line breaks should expose structure, not mechanically put every argument on its own line.

**Example**

Prefer:

```java
failIfIllegalState(state == State.NEW, "AntennaManager must be NEW, was %s", state);
```

over:

```java
failIfIllegalState(
        state == State.NEW,
        "AntennaManager must be NEW, was %s",
        state);
```

Likewise, prefer:

```java
inventoryEnabledSetting.request(Boolean.valueOf(enabled));
```

when it fits comfortably within the limit.

For assignments and lifecycle wiring, prefer the compact form when it remains readable:

```java
this.timingNodeId = logBook.timingNodeId();

lifecycle.register(nodeService, NodeService::activate, NodeService::deactivate);
lifecycle.register(logBook, LogBook::activate, LogBook::deactivate);

Runnable queueRegistration = () -> logBook.execute(command);
```

Avoid mechanical wrapping such as:

```java
this.timingNodeId =
        logBook.timingNodeId();

lifecycle.register(
        nodeService,
        NodeService::activate,
        NodeService::deactivate);

Runnable queueRegistration =
        () -> logBook.execute(command);
```

A callback with a long body may still use a line break after `=` when that genuinely
improves readability; the rule is not to force either shape mechanically.

For a constructor or method with a **multi-line body**, leave one blank line immediately
after the opening brace. This visually separates the declaration/signature from the body,
especially when the body starts with contract checks or local setup. Do not add that blank
line to a genuinely one-line method body.

Prefer:

```java
public TimingNode(LogBook logBook, NodeService nodeService, TagProcessor tagProcessor) {

    failIfInvalidArgument(logBook != null, "logBook must not be null");
    failIfInvalidArgument(nodeService != null, "nodeService must not be null");
    failIfInvalidArgument(tagProcessor != null, "tagProcessor must not be null");

    this.logBook = logBook;
    this.nodeService = nodeService;
    this.tagProcessor = tagProcessor;
}
```

A compact one-line body remains compact:

```java
public long timingDataHead() { return logBookData.headSequence(); }
```

For a genuinely long or structured expression, break at logical boundaries and align the
continuation so the structure remains visible.

**Avoid**

- one argument per line as a blanket formatting rule;
- wrapping short method calls into three or four lines;
- shortening meaningful names merely to satisfy the line limit.

---

### DR-19 — Deactivation is not destruction

**Rule**

A software component that exposes `activate()` and `deactivate()` is normally reusable:

```text
NEW -> ACTIVE -> INACTIVE -> ACTIVE -> INACTIVE ...
```

`NEW` means only that the component has never been activated. It must not be used as a
synonym for "activation is allowed".

Use a separate terminal lifecycle operation such as `close()`, `shutdown()` or
`dispose()` only when the object really cannot be activated again afterwards.

**Why**

Component lifecycle and execution-resource lifecycle are different concerns. Treating every
deactivation as object destruction makes composition brittle and forces callers to rebuild
objects merely to restart behaviour.

**Example**

Prefer:

```java
failIfIllegalState(
        state == State.NEW || state == State.INACTIVE,
        "AntennaManager cannot activate from %s",
        state);
```

or an equivalent compact check that fits within the 120-character line limit.

The same principle applies to serial lanes: stopping a logical lane must not automatically
destroy the externally owned physical worker, and a cleanly stopped lane may be started
again. A failed lane remains a separate terminal/faulted case unless recovery is explicitly
designed.

**Avoid**

```java
failIfIllegalState(state == State.NEW, "...");
```

for an ordinary reusable component merely because its first implementation happened to be
activated only once by Runtime.

Also avoid calling a terminal provider `shutdown()` from ordinary component
`deactivate()` if that would make later activation impossible.

---

### DR-20 — Synchronize the whole state transition

**Rule**

When correctness depends on a lifecycle/state precondition and the following state change,
protect the **check and the transition together**.

Do not synchronize only the check and then modify the guarded state outside that
synchronization boundary.

**Why**

This is racy:

```java
synchronized (this) {
    failIfIllegalState(state == State.NEW || state == State.INACTIVE, "...");
}

taskRunner.start();
state = State.ACTIVE;
```

Another thread can change lifecycle state after the check but before `state = ACTIVE`.

Prefer one atomic lifecycle operation:

```java
public synchronized void activate() {
    failIfIllegalState(state == State.NEW || state == State.INACTIVE,
            "AntennaManager cannot activate from %s", state);

    taskRunner.start();
    state = State.ACTIVE;
}
```

If the protected operation would block for a long time, introduce an explicit transitional
state such as `ACTIVATING`/`DEACTIVATING` and release the monitor only after that
transition has been recorded. Do not create a check-then-act race merely to keep the
critical section short.

---

### DR-21 — Production API must serve production behaviour

**Rule**

Do not widen a production class API merely to make tests convenient.

A public method should exist because a production caller or an intentional production
boundary needs it. When tests need direct access to a composed child, prefer keeping that
child reference in the test composition or using a test fixture. If a production member
genuinely exists only as a test seam, keep it non-public where practical and mark it
explicitly as test-only in its name or Javadoc.

Repeated methods that only forward a child component's API are also a review smell. If
that child boundary is intentionally exposed, prefer one named narrow contract such as
`LogBookAccessor` over copying each child operation onto the parent facade.

A single forwarding method **is** justified when it is the semantic ingress of the parent
component and exists specifically to keep an owned child private. The method must describe
the parent-level fact/action, not expose the child's implementation mechanism. For example,
system-level antenna routing may call `TimingNode.onTagObserved(...)`; TimingNode then
delegates internally to its TagProcessor. The system owner therefore depends on the
TimingNode component boundary and does not need `tagProcessor()` access.

The same principle applies to state queries. When a production caller needs one stable
predicate, expose that semantic predicate on the owner instead of making every caller read
and interpret the owner's full state representation. For example:

```java
if (taskRunner.isRunning()) {
    wakeControlTask();
}
```

Do not expose or interpret a lifecycle enum merely so ordinary control flow can answer this
Boolean question. A richer state view is justified only when a real caller must distinguish
those states; the owner should otherwise expose the semantic predicate directly.

**Why**

Test-only convenience methods and pass-through getters slowly become accidental production
API. They hide the real owner of behaviour, make top-level components look responsible for
mechanisms they do not own, and make later refactoring harder because tests depend on the
wrong boundary.

**Example**

Prefer test composition that retains the owned child directly:

```java
NodeService nodeService = new NodeService(...);
TimingNode node = new TimingNode(logBook, nodeService, tags);

UpstreamHandler handler = nodeService.upstreamHandler();
```

When production callers intentionally need LogBook operations, expose one narrow boundary:

```java
LogBookAccessor logBook = timingNode.logBook();
Status status = logBook.process(LogBookQueries.status(), ReadConsistency.CURRENT);
```

**Avoid**

```java
public UpstreamHandler upstreamHandler() {
    return nodeService.upstreamHandler();
}
```

when no production caller uses that method and it exists only so a test can reach the child.

Also avoid growing a parent facade with repeated one-line `execute`, `queue`, `process`
and event pass-throughs that simply mirror the same child component. A justified semantic
ingress should normally be a small, deliberate exception rather than the start of a mirror
API for the child.

---

### DR-22 — Keep small immutable data carriers simple

**Rule**

Java 8 has no `record` or `struct` language construct. When a type is only a small,
fixed immutable bundle of data and its fields are intentionally the complete public
contract, prefer a `final class` with `public final` fields and a validating constructor.

Do not add private fields plus one-line getters merely to imitate encapsulation when there
is no hidden representation, behaviour or evolution boundary to protect.

**Example**

For TimingNode status:

```java
public final class Status {
    public final State state;
    public final LocationId locationId;

    public Status(State state, LocationId locationId) {
        failIfInvalidArgument(state != null, "state must not be null");
        this.state = state;
        this.locationId = locationId;
    }
}
```

Callers then read the data directly:

```java
if (node.status().state == State.OPEN) {
    use(node.status().locationId);
}
```

Keep the class immutable: fields remain `final`, no setters are added, and mutable
collections/objects are not exposed this way unless their mutability is itself part of the
contract.

Use private fields and methods when the type owns behaviour, hides a representation,
computes derived values, needs controlled mutation, or has an abstraction boundary that
must remain free to change independently of its storage layout.

**Avoid**

```java
private final State state;

public State state() {
    return state;
}
```

when the type is nothing more than a two-field immutable data carrier and the method adds
no semantic contract beyond returning that field.

---

### DR-23 — Keep normal results separate from technical failures

**Rule**

Public result types describe normal semantic outcomes. Do not turn queue state,
timeouts, interruption and internal execution failures into a second public state
machine merely because a caller needs to know that normal processing did not finish.

Prefer a small result owned by the actual boundary:

```java
public CommandResult addManualRegistration(...) {
    ...
}
```

For this example, `CommandResult` may contain `COMMITTED` and
`NODE_NOT_OPEN`. The LogBook command itself returns the committed
`TimingData`; `NODE_NOT_OPEN` is decided by Application before LogBook
processing starts.

Use an exception only to leave normal Java flow when the operation cannot return
its normal result. Prefer ordinary Java runtime failures when callers do not have
distinct recovery behaviour. Do not introduce a generic project reason enum
solely to mirror BUSY, unavailable, timeout, interruption and execution-failure
diagnostics already owned by the execution boundary.

Exceptions do not belong in a generic `*Types` grouping merely for convenience.
If a custom exception is genuinely required, place it with the component/boundary
that owns its meaning and keep it as specific as the caller's recovery need.

Do not wrap fire-and-forget submission failure into a caller-result model. That
path has no synchronous caller result; its owner records the operational
diagnostic and applies any local recovery policy.

**Why**

A compact API is easier to read when callers see the domain/application outcomes
they can actually act on. Repeating internal execution categories through Domain,
Application and Presentation creates mapping code without adding authoritative
state; retained logs are the right place for those technical diagnostics.

---

### DR-24 — Log operational failures at their owning boundary

**Rule**

When an execution boundary detects a technical failure, emit the operational log
record at that owning boundary.

The record must contain enough context to identify the failed operation without requiring
the caller to reconstruct it. For TimingNode/LogBook operations this means at least the
NodeId, stable operation name and failure category. A wait timeout must also report the
effective timeout duration. For an accepted state-changing command, the record must state
that the final outcome may still be unknown; an ORDERED-query timeout must not imply an
unknown state-change outcome.

Use severity consistently:

- `TIMEOUT` and execution/commit `FAILED`: ERROR;
- `BUSY`, `UNAVAILABLE` and `INTERRUPTED`: WARN or higher.

Do not catch and re-log the same technical failure in forwarding layers merely to
reclassify it for HTTP, terminal or another presentation adapter. The execution boundary
that knows the cause owns its operational log.

A lower-level owner may emit one additional root-cause record when it adds materially
different diagnostic context. For example, TimingData persistence may log sequence,
record type and location before the Data Lane reports the resulting command failure.
Do not duplicate the same message and stack trace at every layer.

**Why**

Returning an exception to one caller is not durable diagnostics. Field failures such as a
stalled commit, unavailable Data Lane or persistence error must remain visible after the
client disconnects.

Logging only at presentation boundaries also creates inconsistent diagnostics: HTTP may
record a failure while a terminal or internal caller does not. Logging at the operation
owner gives every caller the same retained evidence while avoiding repeated catch/log/rethrow
boilerplate.

---

### DR-25 — Bound collection-producing reads

**Rule**

Do not let a component query silently materialize a collection whose size grows with
runtime data.

When a caller may ask for many records or rows, make the bound part of the contract. If
the caller asks for one scalar property of one row, calculate that scalar directly instead
of first materializing the complete derived collection. Prefer one of these shapes:

- a scalar or maintained index when the caller needs only a count/current fact;
- a bounded range/page/batch with an explicit maximum size;
- a bounded visitor such as `visitXxx(limit, Consumer<T>)` when the caller only needs to
  process rows;
- an incremental maintained projection when recomputing the complete result on every query
  would be expensive.

A `List<T>` return is fine when the domain itself guarantees a small fixed maximum. It is
not fine merely because current test data is small.

If ordering requires temporary materialization, keep that storage within the same explicit
bound. If a caller needs only one scalar or one maintained fact, calculate/read that fact
directly instead of first constructing a complete derived collection.

When a derived result first needs to choose one representative record from an unbounded
record set, maintain that selection incrementally when the source mutates. Do not rescan
all records on every query merely to rediscover the same representative. Keep enough
ordered/indexed candidates to handle removal of the current selection without a full scan.

A visitor executed on a serial lane must document that fact. Its callback must stay short
and non-blocking. If an external caller cannot satisfy that rule, copy only the already
bounded result and invoke the external callback outside the owning lane.

Do not use `Integer.MAX_VALUE`, an omitted limit, or another sentinel as a disguised
unbounded query.

When a component is notified that authoritative data changed, the event does not need to
transport the complete data set. Prefer a small wake/change signal when the receiving
component can schedule its own task and read the authoritative source in bounded chunks.
The scheduled task owns its cursor/batch size and catches up until the source head is
reached. Repeated signals may coalesce while that task is already active.

This is especially useful when the event payload is already available for other consumers:
the receiving component may deliberately ignore that payload and use the event only to wake
its own catch-up task. Document that choice so a future maintainer does not accidentally
reintroduce duplicate state or large event payloads.

**Why**

Unbounded collection APIs hide both time and memory cost at an innocent-looking call site.
They also encourage repeated full rescans of state that could have been maintained
incrementally.

The caller normally knows how much data it can use. Making that limit explicit keeps
memory, queue turns and presentation work predictable.

**Example**

Prefer the maintained scalar or bounded visitor that matches the real consumer:

```java
int teamCount =
        nodeService.uniqueTeamRegistrationCount();

nodeService.visitRegistrations(
        64,
        this::onRegistrationRow);
```

Do not create a second complete collection merely because one presentation or test wants
to inspect the same source state in a different shape.

For LogBook-driven derived state, prefer a wake-and-catch-up flow:

```java
private void onTimingDataChanged(TimingData ignored) {
    mainTask.wake(taskRunner);
}
```

The task then reads the current source head and fetches only what it still misses:

```java
logBook.submit(LogBookQueries.timingDataRange(nextSequence, 64));
```

Yield between reads and continue until `nextSequence` has passed the current head.

**Avoid**

```java
public List<RegistrationView> registrationViews(LocationId locationId) {
    return buildCompletePresentationList(locationId);
}
```

when the maintained domain state already supports the real bounded/scalar consumer.

Also avoid adding a public production query or result type solely so a test can inspect
private state more conveniently. A test is evidence for behavior; it is not itself a
production consumer. Prefer testing the existing production boundary or, for true
implementation invariants, package-local tests that do not widen the public API.

Also avoid returning a complete persisted TimingData list from a recovery event merely so
each consumer can decide afterwards which subset it needed. Likewise, do not copy each
post-commit TimingData object into another queue when a coalescing wake signal plus the
consumer's own source cursor is sufficient.

---

### DR-26 — Keep retained state compact; materialize semantic values at boundaries

**Rule**

When a component retains many domain rows or keeps hot mutable working state, store only
the fields that the component owns and needs. If those fields have a stable scalar
representation, retain that scalar representation rather than retaining a larger boundary
object merely so its getters can be called later.

Prefer one small primitive-backed object for an ordered domain row:

```java
final class Registration {
    private final long sequenceNumber;
    private final long effectiveTimeMillis;
    private final int registrationId;
    private boolean valid;
}
```

Convert boundary values once when state enters the component. Keep the scalar representation
through internal read boundaries when the next owner can use it directly. Reconstruct semantic
values such as `RegistrationId`, `LocationId` or `TimingTimestamp` only at the first boundary
that actually needs that representation; do not materialize a wrapper merely because a getter is
public to another internal component.

```text
TimingData / protocol value
          |
          | copy owned fields once
          v
compact retained state
          |
          | scalar read when sufficient
          v
application / protocol / presentation boundary
          |
          | materialize only when needed
          v
semantic value / DTO / external representation
```

Do **not** retain `TimingData`, a protocol DTO or another aggregate solely because it
already contains the few fields needed by the component.

**Why**

A retained aggregate keeps its complete object graph alive and makes ownership unclear.
The component then appears to own the boundary model instead of its own state. Compact
state makes both memory cost and responsibility visible, while boundary getters keep
calling code readable.

This is not a rule to replace all Java objects with primitive arrays. Preserve the domain
shape:

- for an ordered list of registrations, prefer one compact `Registration` object per row;
- for a tiny temporary result, event or DTO, ordinary semantic value objects are fine;
- for a short-lived lookup set whose entries have no row identity or ordering meaning,
  primitive arrays may be appropriate when measurement/design already justifies them;
- do not replace a clear semantic `Map` with boxed primitive keys merely to claim a
  primitive representation; that normally changes no allocation advantage;
- do not duplicate both a primitive field and a retained wrapper of the same value.

**Project examples**

`DefaultTimingDataFactory` stores absolute times as epoch-millisecond `long` values and
RegistrationId as its packed `int`, then reconstructs the public TimingData value types.
The TagProcessor passage and duplicate-filter state use the same scalar-boundary pattern.

`ActiveRegistrations` follows this rule as well: LocationId scopes the complete active-WP
projection, so each retained row needs only sequence, effective time, packed RegistrationId and
validity. Committed `TimingRecord` is input to `apply(...)`, not retained state. Its internal
read exposes effective time as epoch milliseconds; `TimingNodeProxy` materializes
`TimingTimestamp` only when building the presentation-facing registration entry.
`StageStartTimes` likewise retains normalized UTC epoch milliseconds rather than a partial
`TimingTimestamp`.

When every row in a retained projection shares one scope value, retain that value once at the
projection owner instead of repeating it in every row. The current OPEN LocationId is such a
scope: registration rows do not each need another LocationId field.

---

### DR-27 — Normalize external civil time at ingress

**Rule**

Keep internal timing state absolute. A component that receives an external protocol value
containing local time, date+time, offset time or another partial civil representation must
resolve that value once at the semantic ingress boundary. Downstream domain calculations
must not receive a `ZoneId` or current-date parameter merely to finish interpreting an
older packet.

Use the runtime-composed `TimeSource` when the protocol requires current timing context.
Sample it once per accepted message or operation so every value in that transaction uses
the same absolute-time basis.

For example, IF-06 RACE_DATA stage starts are normalized before entering live race state:

```text
IF-06 stage-start value
        |
        | RACE_DATA ingress + shared TimeSource
        v
UTC epoch milliseconds
        |
        +--> StageStartTimes
        +--> future domain consumers
```

An absolute source value keeps its Instant. A source date+time is interpreted according to
the protocol's documented time basis. A source time-only value uses the protocol-defined
date rule and the shared TimeSource where current date is required.

**Why**

Deferring civil-time interpretation spreads protocol knowledge through otherwise simple
domain calculations and lets different callers resolve the same stored value differently.
Normalizing once makes retained state unambiguous, keeps later calculations deterministic
and prevents time-zone/date interpretation from leaking into downstream domain code.

Do not use `Clock.systemDefaultZone()`, `ZoneId.systemDefault()` or another ambient JVM
setting inside timing-domain calculations. The composition root owns the timing source and
the ingress contract owns external time interpretation.

---

### DR-28 — Name object creation explicitly

**Rule**

A factory method that creates and returns a new object or immutable value uses a
`create...` name.

Prefer:

```java
TimingRecord.createNodeClosed(...);
UpstreamApiMessage.createOutboundMessage(...);
```

over adjective/noun-only factory names such as:

```java
TimingRecord.closed(...);
UpstreamApiMessage.outbound(...);
```

Use a different verb only when the operation is genuinely different from creation:

- `parse...` converts an external representation and may validate syntax;
- `read...` / `load...` retrieves existing data;
- `find...` searches existing state;
- `copyOf...` makes a copy where copy semantics are the relevant distinction.

**Why**

At a call site, object creation should be visible without opening the implementation.
This is especially important for static factories whose names otherwise look like
properties or state predicates.

**Avoid**

Using a noun/adjective solely because the return type already reveals the created type.

---

### DR-29 — Complete fixed composition before runtime use

**Rule**

A runtime component should be fully composed before it becomes operational.

When a relationship is fixed by configuration/composition, construct the participating
objects and pass the complete fixed structure into the runtime owner. Do not create an
empty runtime object and then use public `create...`, `register...` or `add...` methods
to mutate its permanent object graph unless dynamic registration is itself a real runtime
requirement.

Prefer:

```java
Map<NodeId, UpstreamStream> streams = createStreams(...);
UpstreamGateway gateway = new UpstreamGateway(connector, streams);
```

over:

```java
UpstreamGateway gateway = new UpstreamGateway();
gateway.createApplicationPort(...);
gateway.createApplicationPort(...);
```

A constructor may validate and retain the completed graph; it must still obey DR-02 and
must not start runtime behaviour.

**Why**

Fixed composition and runtime behaviour are different responsibilities. A complete
constructor contract makes valid object state explicit and prevents component APIs from
being polluted with setup-only mutation operations.

**Avoid**

Keeping a setup/factory method on a runtime component only because composition code needs
a convenient place to create one of the component's children.

---

### DR-30 — Keep the primary class flow visible

**Rule**

Lay out a class so a reader sees its public meaning and normal call flow before private
implementation machinery.

A useful default order is:

1. constants and public semantic nested types that are part of the API;
2. fields;
3. constructors;
4. public methods;
5. protected/package-private methods where relevant;
6. private helpers;
7. private nested implementation classes.

A private nested helper such as `NodeBinding` should normally be placed after the
constructor/method flow, not between the class declaration and the primary constructor.
Move it earlier only when the nested type itself is essential to understanding the public
contract.

**Why**

Private implementation structure should not obscure the class's main API. Reviewers should
be able to scan construction and normal runtime behaviour without first reading helper
types that only support the implementation.

**Avoid**

Placing a private nested implementation class above the public constructor merely because
it is declared before the fields that reference it.

---

## Pull-request review check

For Java component changes, a reviewer can use this short check:

1. **Responsibility** — Is the decision made by the component that owns it?
2. **Lifecycle** — Are side effects explicit and are lifecycle words clear?
3. **Event callback** — Does a synchronous callback return quickly?
4. **Queueing** — Is work queued once, without a state-check race, and is `QUEUED` clearly distinguished from completed?
5. **Current state** — Are stale snapshots being replayed when only current state matters?
6. **Failure direction** — Can a downstream operational problem leak into its producer?
7. **Async ownership** — Does lifecycle sequencing remain with its real owner?
8. **Observability** — Can status, metrics and logs explain what happened afterwards?
9. **Comments** — Are non-obvious ownership, externally wired event subscriptions,
   transaction/lambda semantics and threading decisions discoverable at the relevant code?
10. **Language** — Are names and messages clear English using established terminology?
11. **Control flow** — Are early returns guards, while normal equivalent paths remain explicit?
12. **Object lifecycle** — Are recurring stateful helpers owned/reused with explicit reset semantics?
13. **Device completion** — Are real completion facts emitted by the operation owner rather than inferred from delays?
14. **Contract checks** — Are programming-contract failures expressed compactly without hiding normal control flow?
15. **Async readability** — Are event and lane boundaries named instead of hidden in nested lambdas?
16. **Wrapping** — Are lines kept compact up to the 120-character maximum instead of mechanically wrapped?
17. **Lifecycle reuse** — Can an ordinary component activate again after clean deactivation?
18. **State synchronization** — Are lifecycle checks and their state transitions protected by the same synchronization boundary?
19. **Production API** — Does each public member serve an actual production boundary? Never add a public query/result type only because a test wants to inspect state.
20. **Data carriers** — Is a small immutable Java-8 value kept simple instead of wrapped in getter boilerplate without a reason?
21. **Tests** — Is the risky behaviour tested, not only the happy path?
22. **Failure contract** — Do normal result types contain only semantic outcomes, with technical execution failures kept out of a duplicate public state model?
23. **Failure logging** — Is an operational failure logged once at its owning boundary with stable identity, operation and reason, without forwarding-layer duplicates?
24. **Bounded reads** — Can any query or derived view grow with runtime data, and if so is its batch/page/visitor limit explicit and enforced internally?
25. **Maintained selection** — If a view repeatedly chooses one representative from many source records, is that selection updated on mutation instead of rediscovered by full scans?
26. **Projection scope** — Is a current-WP/current-session projection activated and rebuilt by its owning lifecycle instead of silently retaining unrelated historical scopes?
27. **Creation naming** — Do factories that create new objects/values use an explicit `create...` name?
28. **Fixed composition** — Is the permanent object graph completed during composition instead of mutated later through setup-only runtime API?
29. **Class layout** — Is the primary constructor/API visible before private nested implementation machinery?

A review can cite a rule such as `DR-05`, but the rule text and example should remain
clear enough that the identifier is not required to understand the review comment.

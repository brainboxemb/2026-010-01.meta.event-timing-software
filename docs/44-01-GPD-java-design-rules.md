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
- **reconcile** — read the current authoritative state and do the work needed to make the
  owned state match what is required;
- **event-triggered reconciliation** — use a change event as a wake signal, then reread
  authoritative current state and derive/apply the required behaviour instead of replaying
  the event payload as control history;
- **serial lane** — a `SerialExecutor` or `SerialScheduledExecutor` ordering boundary.
  A lane is not automatically its own Java thread.

Example:

```text
TimingNode state is OPEN
        |
        v
Conductor publishes:
AntennaSettings.update(...)
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
antennaSettings.update(edit -> edit.inventoryEnabled(true));
```

The Conductor publishes desired inventory enable. AntennaManager may then power the
antenna, wait for stabilization, initialize it and start inventory. When all TimingNodes
are CLOSED or ERROR, the Conductor publishes `inventoryEnabled(false)` in the
same shared Settings object.

**Avoid**

```java
antennaManager.powerOn();
antennaManager.initialize();
antennaManager.startInventory();
```

from Conductor. This makes Conductor responsible for AntennaManager internals.

The same rule applies to recovery. After the Conductor publishes desired
inventory state, AntennaManager owns recovery needed to restore it without
requiring the Conductor to micromanage hardware.

The same ownership rule also guides package placement. A reusable technical mechanism
that knows nothing about SI-01 concepts belongs under `infra`; domain-specific
registration and behaviour stay with the owning Domain component.

Example:

```text
domain.system.SystemConductor
        reads current TimingNode status and calculates desired inventory

infra.setting.Setting<T>
        passive desired/applied tracking, reused across components

io.devices.antenna.manager.AntennaSettings
        antenna-specific shared desired-state transaction

io.devices.antenna.manager.AntennaManager
        owns applied state, physical transitions and recovery
```

A Setting is state, not a scheduler. It must not own a SerialExecutor, Future,
queue admission, retry loop, coalescing controller or component lifecycle merely
because its value can change asynchronously.

---

### DR-02 — Construction should not secretly start behaviour

**Rule**

A constructor creates and validates an object. Runtime behaviour starts through an
explicit operation such as `activate()`, `requestEnableInventory()` or `requestDisableInventory()`.

For an active component, `activate()` primarily establishes lifecycle/execution context.
If the component owns a serial lane and startup requires potentially blocking persisted-data
loading or state reconstruction, start the lane, admit that work to the owning lane and return rather
than performing or awaiting the work on the caller thread. Readiness is a separate fact
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

If components deliberately do not implement one shared lifecycle interface, do not recreate
that interface dynamically with reflection. Register lifecycle actions explicitly with
compile-time method references so renamed or missing lifecycle methods fail during compilation.
Deriving a diagnostic component name from the registered instance is fine; discovering
`activate()` or `deactivate()` by method-name lookup is not.

**Why**

Object composition remains predictable. Creating an object should not unexpectedly start a
thread, connect to hardware, power a device or publish events.

**Example**

Good:

```java
AntennaManager manager = new AntennaManager(...);
manager.activate();
```

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
software component      activate / deactivate
TimingNode state        OPEN / CLOSED / ERROR
antenna provider         initialize / startInventory / stopInventory / shutdown
```

**Why**

Using the same word for unrelated states makes call order and failure handling difficult
to understand.

**Example**

`Antenna.shutdown()` is clearer than `Antenna.close()` when there is no corresponding
`Antenna.open()`.

**Avoid**

Making `AntennaManager.activate()` mean both:

1. start the software component; and
2. synchronously self-test all physical antennas before returning.

Those are different actions and may be requested by different owners.

When one owner coordinates the lifecycle of several child components, use the shared
`ComponentLifecycleManager` for ordered activation, rollback and reverse-order
deactivation. Do not duplicate that generic lifecycle algorithm in each component.

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

For SystemConductor, a TimingNode status event is only a short wake signal:

```java
timingNode.statusChangedEvent()
        .subscribe(
                status -> systemConductor.onTimingNodeStatusChanged(timingNode, status));
```

The handler may validate source identity and wake the existing control task, then returns.
The later control run reads TimingNode status with CURRENT consistency and updates
shared AntennaSettings, which wakes the manager to reconcile asynchronously. It does not perform that
reconciliation in the synchronous event callback.

**Event and handler naming**

Use `Event<T>` / `EventSource<T>` for observable post-fact notifications. Do not add a
second registration style such as `onChange(Consumer<T>)`, `addListener(...)` or
`setCallback(...)` when the project event abstraction already fits.

Use these naming roles consistently:

```text
statusChangedEvent()          EventSource: first available Status + later effective changes
onTimingNodeStatusChanged()   listener/handler method that reacts to the fact
```

An `onXxx(...)` method is a handler name, not a subscription API.

`EventSource<T>` always has 0..N notification semantics. Do not introduce public
`SingleEvent` / `MultiEvent` variants or cardinality configuration merely because a
particular composition currently has one subscriber. When a relationship is semantically
a direct action to one owned component, use a normal method call instead of an event.

Cross-component event wiring is completed during Runtime composition before
activation. `subscribe(...)` is therefore a composition-time operation; runtime
operation is emit-only and the baseline `EventSource<T>` exposes no `unsubscribe(...)`.

**Make externally wired relationships discoverable in both places:**
- The receiving component's class Javadoc must state which externally supplied
  event(s) invoke its handler and name or link to the composition owner that
  installs the subscription.
- The composition code must comment the purpose of non-obvious event links,
  including whether the handler consumes the event payload or only wakes a
  task that rereads CURRENT state.
- Internal completion-event subscriptions between helpers owned by one component
  may stay inside that component; do not move every local listener to Runtime.

For example, `SystemConductor` documents that `TimingSystemComposer` connects
`TimingNode.statusChangedEvent()` to `onTimingNodeStatusChanged(...)`. The
Composer installs the subscription and explains that it is a wake signal, not
a queued command or a second copy of node state. A developer inspecting either
class can locate the other half of the relationship.

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

Initialization is also separate from events. SystemConductor activation wakes its first
normal reconciliation run; that run reads CURRENT TimingNode status and publishes
the desired AntennaSettings state. No synthetic status-change event is required.

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
Do not add `taskRunner.execute(...)` merely to bounce the callback through the same lane
again.

---

### DR-05 — Let the queue operation decide whether work was queued

**Rule**

Queue work once and handle the returned queue result. Do not first inspect executor
state and then try to queue the work.

Follow the established Java execution model at a serial-lane boundary:

- `SerialLane.execute(Runnable)` queues fire-and-forget work and returns without
  waiting for the later operation result;
- `SerialLane.submit(Callable<R>)` queues result-bearing work and returns a
  standard `Future<R>`;
- when the bounded lane cannot accept work, use the standard
  `RejectedExecutionException` contract;
- queue-container vocabulary such as `offer()`, `poll()` and direct
  `ArrayBlockingQueue` handling belongs **inside the SerialLane implementation**,
  not in LogBook, NodeService, TagProcessor or other lane users.

Do not create project-specific admission/result types merely to rename Java's existing
execute/submit/rejection model. A deviation needs a concrete semantic requirement that the
JDK contract cannot express. Extra vocabulary without such a requirement adds review noise.

Domain components may still use domain words where they add real meaning. For the LogBook
boundary, `process(command)` means execute in LogBook order and return the domain result,
while `execute(command)` is the fire-and-forget path. The latter may delegate to
`SerialLane.execute(...)`; lane rejection uses `RejectedExecutionException` rather than
a separate project-specific queue/admission result.

**Why**

This pattern is both redundant and race-prone:

```java
if (lane.state() == RUNNING) {
    lane.offer(work);
}
```

The lane can change state between the two calls. The queue operation already knows
whether it can accept the work.

**Examples**

A lane user should read like ordinary Java concurrency code:

```java
lane.execute(this::processNext);
Future<Result> future = lane.submit(this::calculateResult);
```

The bounded queue remains an implementation detail inside `SerialLane`:

```java
private boolean enqueueTaskLocked(TrackedTask task) {
    return queue.offer(task);
}

private TrackedTask nextQueuedTaskLocked() {
    return queue.poll();
}
```

A Domain boundary may translate a standard rejection only when that boundary owns a
different failure policy, for example a synchronous device callback that must log/drop a
fire-and-forget event instead of propagating the rejection.

**Avoid**

A separate `state()` check immediately before queueing.

Also do not silently ignore a full queue or a meaningful not-running result. See DR-09
for observability.

---

### DR-06 — Use current state when only the latest state matters

**Rule**

When a component only needs to know **what is true now**, maintain or read one current
representation of that truth. Do not queue historical state snapshots and replay them later
as commands.

If the authoritative owner emits a first-availability or post-change event, a current-state
controller may use that event only to wake a reconciliation run. The reconciliation then reads the owner's
authoritative current representation explicitly. This keeps event history separate from
current control state and makes initialization use the same path as later updates.

Calculate intermediate decisions locally. If the result is already the desired state of
another component, publish it directly to that component's shared settings rather than
copying it into a DerivedProperty first.

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
TimingNode.activate()
        |
        +--> start Task Lane
        +--> start Data Lane and admit persisted-data load as its first task
        +--> start TagProcessor ingress
        +--> return

Data Lane
        |
        +--> read/validate persisted TimingData
        +--> rebuild LogBook/current node state
        +--> publish initial loaded-data fact to Task-owned derived views
        +--> publish immutable currentStatus
        +--> statusChangedEvent() wake

SystemConductor control run
        |
        +--> CURRENT unavailable while persisted-data load is pending
        |       -> publish no partial decision; return
        |
        v
TimingNode.query(status, CURRENT)
        |
        v
derive inventoryRequired = any TimingNode OPEN
```

Good runtime flow:

```text
TimingNode.statusChangedEvent(Status)
        |
        v
CooperativeTaskController.wake()
        |
        v
query current Status + derive inventoryRequired
        |
        v
AntennaSettings.update(edit -> edit.inventoryEnabled(inventoryRequired))
        |
        v
apply current inventory intent
```

The event callback only validates/wakes the consumer; it does not modify Settings,
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

Not every event should be coalesced. TimingData records, registrations and other history
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

Comments must still add meaning rather than translate syntax. For component boundaries,
threading/lifecycle helpers or non-obvious code, explain:

1. what the component or method is responsible for;
2. what it is deliberately not responsible for when that matters;
3. important lifecycle/call-order rules;
4. important threading or serial-lane assumptions;
5. the reason for a non-obvious implementation choice.

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
| Passive committed history | `LogBookData` | another active-sounding `LogBook` |
| Node Task Lane service | `NodeService` | `NodeTaskRunner` when it owns domain state as well |
| Actual input-processing component | `TagProcessor` | renaming merely for suffix consistency |
| Registration being matched for revoke | `activeRegistration` | `candidate` |
| Team ID read from static EventData | `configuredTeamId` | `fixed` |

Use `Runner` for an execution mechanism that runs work, such as
`SerialTaskRunner` or `YieldingTaskRunner`. Do not use `Runner` for a component
that also owns domain state, protocol state or business decisions.

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
that distinction would otherwise be ambiguous (for example `tagProcessorLane()`).

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

The same rule applies to non-execution callbacks. When the explicit functional type makes
the contract clearer, prefer:

```java
final boolean inventoryRequired = required;
Consumer<AntennaSettings.Edit> settingsUpdate =
        edit -> edit.inventoryEnabled(inventoryRequired);

antennaSettings.update(settingsUpdate);
```

over:

```java
final boolean inventoryRequired = required;
antennaSettings.update(edit -> edit.inventoryEnabled(inventoryRequired));
```

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
OPEN / CLOSED / ERROR       TimingNode state
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
- the initial Data Lane load publishes CURRENT status only after LogBook/current
  state is complete;
- the first Conductor run may observe startup UNAVAILABLE and then publishes no
  partial Settings decision;
- the initial status event wakes a later reconciliation after persisted-data loading completes;
- a status event only wakes the control task and does not publish Settings itself;
- every ready-state control run reads CURRENT TimingNode status before deriving desired inventory;
- rapid state changes converge to the final desired inventory while control wakes coalesce;
- one OPEN node among several nodes keeps shared inventory desired state enabled;
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
The second is an operation-completion relationship and should be represented by an event
or equivalent owner-controlled completion signal.

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

### DR-16 — Keep contract checks compact

**Rule**

Use compact precondition helpers for programming-contract checks such as required state or
argument validity.

Prefer static `checkState(...)` and `checkArgument(...)` calls over repeated
`if (...) { throw new IllegalStateException/...; }` blocks when the only purpose of the
branch is to enforce a contract.

Keep normal business decisions as ordinary control flow. A precondition helper must not
hide a recoverable condition, device result or normal application branch.

**Why**

Repeated exception boilerplate makes a simple contract dominate the visual structure of a
method. The reader should see the operation first and the contract as one concise guard.

**Example**

Prefer:

```java
synchronized (this) {
    checkState(
            state == State.NEW,
            "AntennaManager must be NEW, was %s",
            state);
}
```

over:

```java
synchronized (this) {
    if (state != State.NEW) {
        throw new IllegalStateException(
                "AntennaManager can only activate from NEW; current state="
                        + state);
    }
}
```

For arguments:

```java
checkArgument(
        controlLane != null,
        "controlLane must not be null");
```

The project may provide these small helpers directly rather than adding a broad utility
dependency solely for precondition syntax. Static imports are preferred at call sites when
they improve readability.

**Avoid**

Using `checkState(...)` as a replacement for normal application flow:

```java
checkState(
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

A lambda that executes **synchronously**, such as an atomic
`AntennaSettings.update(edit -> edit.inventoryEnabled(enabled))`, is different.
Keep a short lambda where it makes the transaction visible, but explain the
non-obvious contract at the call site or in the immediately referenced API:
the edit is staged, `update()` commits desired state before returning, and
hardware application still happens asynchronously. Do not let the lambda
syntax hide when state becomes visible or which component performs the work.

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
checkState(state == State.NEW, "AntennaManager must be NEW, was %s", state);
```

over:

```java
checkState(
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

    checkArgument(logBook != null, "logBook must not be null");
    checkArgument(nodeService != null, "nodeService must not be null");
    checkArgument(tagProcessor != null, "tagProcessor must not be null");

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
checkState(
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
checkState(state == State.NEW, "...");
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
    checkState(state == State.NEW || state == State.INACTIVE, "...");
}

taskRunner.start();
state = State.ACTIVE;
```

Another thread can change lifecycle state after the check but before `state = ACTIVE`.

Prefer one atomic lifecycle operation:

```java
public synchronized void activate() {
    checkState(state == State.NEW || state == State.INACTIVE,
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
Status status = logBook.query(LogBookQueries.status(), ReadConsistency.CURRENT);
```

**Avoid**

```java
public UpstreamHandler upstreamHandler() {
    return nodeService.upstreamHandler();
}
```

when no production caller uses that method and it exists only so a test can reach the child.

Also avoid growing a parent facade with repeated one-line `execute`, `queue`, `query`
and event pass-throughs that simply mirror the same child component.

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
19. **Production API** — Does each public member serve a production boundary, and are intentional test-only seams explicit?
20. **Tests** — Is the risky behaviour tested, not only the happy path?

A review can cite a rule such as `DR-05`, but the rule text and example should remain
clear enough that the identifier is not required to understand the review comment.

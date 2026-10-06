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
- **serial lane** — a `SerialExecutor` or `SerialScheduledExecutor` ordering boundary.
  A lane is not automatically its own Java thread.

Example:

```text
TimingNode state is OPEN
        |
        v
Conductor calls:
requestEnableInventory()
        |
        v
AntennaManager decides how:
power -> initialize -> inventory
```

The Conductor owns the application decision. The AntennaManager owns the device sequence.

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
antennaManager.requestEnableInventory();
```

The Conductor explicitly requests inventory enable. AntennaManager may then power the
antenna, wait for stabilization, initialize it and start inventory. When the TimingNode
state becomes CLOSED or ERROR, Conductor explicitly calls
`requestDisableInventory()`.

**Avoid**

```java
antennaManager.powerOn();
antennaManager.initialize();
antennaManager.startInventory();
```

from Conductor. This makes Conductor responsible for AntennaManager internals.

The same rule applies to recovery. Conductor may have requested
`requestEnableInventory()`; AntennaManager owns any device recovery needed to restore
enabled inventory without requiring Conductor to micromanage the recovery sequence.

The same ownership rule also guides package placement. A reusable technical mechanism
that knows nothing about SI-01 application concepts belongs under `infra`; the concrete
binding that gives that mechanism application meaning belongs under `application`.

Example:

```text
infra.property.TrackedProperty<T>
        generic scheduling + change detection

application.property.TimingNodeStateProperty
        binds TrackedProperty to TimingNode state semantics
```

Avoid placing the generic scheduler/change-detection implementation in Conductor or in the
application package merely because the first consumer happens to be application code.

---

### DR-02 — Construction should not secretly start behaviour

**Rule**

A constructor creates and validates an object. Runtime behaviour starts through an
explicit operation such as `activate()`, `requestEnableInventory()` or `requestDisableInventory()`.

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

For a tracked application property, the source event only invalidates the cached value:

```java
timingNode.statusChangedEvent()
        .subscribe(
                ignored -> timingNodeStateProperty.signalChanged());
```

The property rereads the authoritative TimingNode state on its serial lane.

When the tracked value really changes, the property uses the same project event mechanism
as other components:

```java
timingNodeStateProperty.changedEvent()
        .subscribe(this::onTimingNodeStateChanged);
```

**Event and handler naming**

Use `Event<T>` / `EventSource<T>` for observable post-fact notifications. Do not add a
second registration style such as `onChange(Consumer<T>)`, `addListener(...)` or
`setCallback(...)` when the project event abstraction already fits.

Use these naming roles consistently:

```text
statusChangedEvent()        EventSource: observable notification
changedEvent()              generic tracked-property notification
signalChanged()             command/invalidation: reread the source
onTimingNodeStateChanged()  listener/handler method
```

An `onXxx(...)` method is a handler name, not a subscription API.

`EventSource<T>` always has 0..N notification semantics. Do not introduce public
`SingleEvent` / `MultiEvent` variants or cardinality configuration merely because a
particular composition currently has one subscriber. When a relationship is semantically
a direct action to one owned component, use a normal method call instead of an event.

Event wiring is completed during Runtime composition before activation. `subscribe(...)`
is therefore a composition-time operation; runtime operation is emit-only and the baseline
`EventSource<T>` exposes no `unsubscribe(...)`.

A component's `activate()`, `deactivate()`, `start()` or `close()` changes component
or transport behaviour, not the application event graph. Do not hide subscribe/unsubscribe
wiring inside those lifecycle methods.

The `Event<T>` implementation may optimize the common 0/1-subscriber case internally.
That optimization remains invisible to callers: zero listeners need no listener container,
one listener may be stored directly, and only two or more listeners require an immutable
array representation. Subscription order remains stable. Concurrent runtime
`emit(...)` calls are allowed, but runtime rewiring is not part of the event contract.

Initialization is also separate from events. A tracked property returns its first
authoritative value from `initialize()`; that first value is not emitted as a
`changedEvent`. Only a later real value change is an event.

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

### DR-05 — Let the admission operation decide whether work was accepted

**Rule**

Call `offer()`, `execute()` or `submit()` once and handle its result.

Do not first inspect executor state and then perform admission.

**Why**

This pattern is both redundant and race-prone:

```java
if (executor.state() == RUNNING) {
    executor.offer(work);
}
```

The executor can change state between the two calls. The admission operation already knows
whether it can accept the work.

**Example**

Good:

```java
AdmissionResult result = executor.offer(work);

switch (result) {
    case ACCEPTED:
        break;
    case FULL:
        LOG.warn("...");
        break;
    case NOT_RUNNING:
        LOG.debug("...");
        break;
    default:
        throw new IllegalStateException(
                "Unsupported admission result " + result);
}
```

**Avoid**

A separate `state()` check immediately before `offer()`.

Also do not silently ignore `FULL` or a meaningful `NOT_RUNNING`. See DR-09 for
observability.

---

### DR-06 — Use current state when only the latest state matters

**Rule**

When a component only needs to know **what is true now**, treat a state-change event as
"something changed" and read the current authoritative state during reconciliation.

Do not automatically treat the event snapshot as a command that must later be replayed.

**Why**

A queue may contain old snapshots by the time they execute.

For example:

```text
OPEN -> CLOSED -> OPEN
```

If antenna behaviour only depends on the current TimingNode state, replaying all three
snapshots creates unnecessary work and can briefly apply stale intent.

**Example**

Good:

```text
statusChangedEvent
        |
        v
TrackedProperty.signalChanged()
        |
        v
TimingNode.query(status).state()
        |
        +-- unchanged --> no event
        |
        v
changedEvent(newState)
```

If many source events arrive while one property refresh is already pending, they may be
coalesced into one later refresh, provided a change cannot be lost.

**Avoid**

Queueing every `Status` object and later executing each one as if it were a command.

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

**Example**

A useful diagnostic sequence could be:

```text
INFO  TimingNode TN-01 state changed CLOSED -> OPEN
INFO  TimingNode TN-01 state OPEN -> enable antenna inventory
INFO  Antenna ANT1 inventory started
WARN  Antenna ANT1 provider failed
INFO  Antenna ANT1 recovery started
INFO  Antenna ANT1 inventory restored
```

For a high-rate path such as tag observations, do **not** write an INFO log for every
observation. Use counters/metrics and log only meaningful transitions or failures.

Typical intent:

| Level | Use |
| --- | --- |
| DEBUG | detailed control/reconcile information useful during diagnosis |
| INFO | meaningful lifecycle and operational transitions |
| WARN | degraded operation, rejected work, recoverable failure |
| ERROR | component can no longer fulfil its role |

A useful log line normally includes the relevant stable identity, such as
`TimingNodeId` or `AntennaId`, and the cause/reason when something failed.

---

### DR-10 — Comments should explain things the code cannot say clearly

**Rule**

Write comments and Javadoc for **ownership, lifecycle, threading, invariants and reasons**.
Do not use comments merely to translate Java syntax into English.

Public component boundaries should normally explain:

1. what the component is responsible for;
2. what it is deliberately not responsible for;
3. important lifecycle/call-order rules;
4. important threading or serial-lane assumptions.

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

- many source status events while one property refresh is pending should not fill the queue;
- a stale `Status` snapshot must not override the authoritative current TimingNode state;
- unchanged property values must not emit `changedEvent`;
- property admission overload must not throw back into TimingNode event delivery.

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

Do not hide event delivery, queue admission or thread/lane transfer inside nested lambda
expressions.

At an asynchronous boundary, prefer a named method reference and move the admission step
into that method. The call site should read as the architecture reads.

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

---

### DR-18 — Keep line wrapping readable

**Rule**

Use **120 characters as the maximum Java source line length**.

Do not wrap a statement merely because it has multiple arguments. When a complete,
readable statement fits within 120 characters, keep it on one line.

Wrap only when the line would exceed 120 characters or when the expression has enough
logical structure that line breaks genuinely improve understanding.

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

## Pull-request review check

For Java component changes, a reviewer can use this short check:

1. **Responsibility** — Is the decision made by the component that owns it?
2. **Lifecycle** — Are side effects explicit and are lifecycle words clear?
3. **Event callback** — Does a synchronous callback return quickly?
4. **Queue admission** — Is admission handled once, without a state-check race?
5. **Current state** — Are stale snapshots being replayed when only current state matters?
6. **Failure direction** — Can a downstream operational problem leak into its producer?
7. **Async ownership** — Does lifecycle sequencing remain with its real owner?
8. **Observability** — Can status, metrics and logs explain what happened afterwards?
9. **Comments** — Are the non-obvious ownership/threading/reasoning points documented?
10. **Language** — Are names and messages clear English using established terminology?
11. **Control flow** — Are early returns guards, while normal equivalent paths remain explicit?
12. **Object lifecycle** — Are recurring stateful helpers owned/reused with explicit reset semantics?
13. **Device completion** — Are real completion facts emitted by the operation owner rather than inferred from delays?
14. **Contract checks** — Are programming-contract failures expressed compactly without hiding normal control flow?
15. **Async readability** — Are event and lane boundaries named instead of hidden in nested lambdas?
16. **Wrapping** — Are lines kept compact up to the 120-character maximum instead of mechanically wrapped?
17. **Lifecycle reuse** — Can an ordinary component activate again after clean deactivation?
18. **State synchronization** — Are lifecycle checks and their state transitions protected by the same synchronization boundary?
19. **Tests** — Is the risky behaviour tested, not only the happy path?

A review can cite a rule such as `DR-05`, but the rule text and example should remain
clear enough that the identifier is not required to understand the review comment.

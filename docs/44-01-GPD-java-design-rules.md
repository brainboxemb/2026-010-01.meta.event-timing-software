# SI-01 Java Design Rules (GPD)

Status: working project guidance

## Purpose

This General Purpose Document defines the shared Java design and implementation review
rules for **SI-01 — Timing Point Application**.

The rules exist to keep equivalent component behaviour consistent across the codebase.
They are especially intended for code review when implementation details such as event
callbacks, queue admission, lifecycle, failure handling, logging and asynchronous work
would otherwise be decided differently in each class.

This is supportive engineering guidance. It does not create product requirements or
override the SI-01 SSD, applicable interface documents or focused SDDs.

## Terms and abbreviations

- **GPD** — General Purpose Document
- **SI-01** — Timing Point Application
- **SDD** — Software Design Description
- **desired state** — application intent that a component is responsible for realizing
- **actual state** — currently observed component/device state
- **reconcile** — compare desired/current authoritative state and perform only the work
  needed to bring the owned state into agreement

## Relationship to other documents

The SI-01 SSD and applicable ISDs define required behaviour and architecture. The
43-01-SDD documents define focused detailed design. This GPD turns recurring
implementation lessons from those documents into one reusable Java review checklist.

When a rule here conflicts with an approved requirement or focused design decision, the
requirement/design is authoritative and this GPD must be corrected. A code change must not
use this GPD to invent product policy that has not been specified or designed.

The Java implementation repository should use these rules during implementation and pull
request review.

## Design rules

### DR-01 — Preserve semantic ownership

A component decides only policy that belongs to its responsibility.

Application coordination expresses **what is required**. A lower component that owns a
mechanism decides **how to realize that requirement**. Do not let callers micromanage
internal device/protocol steps merely because those steps are visible in the
implementation.

If a new retry, fallback, timeout, recovery or selection policy materially changes
behaviour, identify the requirement/design authority before implementing it.

### DR-02 — Keep construction passive

Constructors validate and capture dependencies/configuration. They must not start worker
threads, connect to external systems, power devices, start inventory, perform probes or
register hidden cross-component behaviour unless an explicit design decision requires
construction-time activity.

Runtime side effects start through explicit lifecycle or control operations.

### DR-03 — Give lifecycle operations one clear meaning

Lifecycle verbs must describe one level of lifecycle.

Examples:

- component `activate()/deactivate()` controls whether the software component accepts and
  performs its role;
- TimingNode `OPEN/CLOSED` describes domain operational state;
- device/provider initialization, inventory and shutdown are separate device operations.

Do not make `activate()` silently perform unrelated application actions merely because
startup currently needs those actions. Avoid ambiguous pairs such as `close()` when
there was no matching semantic `open()` at that level.

### DR-04 — Keep synchronous event callbacks bounded

Local `Event<T>` delivery is synchronous. A callback running on the producer thread may
validate the immutable event value and perform one bounded/non-blocking admission action.

It must not perform cross-component control, blocking I/O, waits, retries or substantial
mapping/processing on the producer thread.

### DR-05 — Treat admission as one atomic decision

Do not check executor/lane state immediately before calling `offer()`, `execute()` or an
equivalent admission operation. That creates a check-then-act race and duplicates the
admission API.

Use the admission operation as the authority and handle its returned result explicitly.

Example:

```java
AdmissionResult result = lane.offer(this::reconcile);

switch (result) {
    case ACCEPTED:
        return;
    case FULL:
        // record overload according to component policy
        return;
    case NOT_RUNNING:
        // record lifecycle/failure context according to component policy
        return;
    default:
        throw new IllegalStateException("unsupported admission result " + result);
}
```

### DR-06 — Do not leak downstream operational failures through event producers

A synchronous event producer must not unexpectedly fail because a downstream listener's
queue is full, component is stopping, diagnostic sink failed or another coordinated
component rejected work.

The listener owns its admission/failure policy. Record the failure locally and expose it
through the appropriate status/metrics/logging path.

Programming-contract violations such as a null argument may still fail immediately where
that is the intended API contract.

### DR-07 — Never make loss invisible

`FULL`, `NOT_RUNNING`, cancellation, timeout and failed asynchronous completion are not
"nothing happened" results.

When they can affect operation they must become observable through at least one appropriate
mechanism:

- current component/status state;
- a counter/metric;
- a log record with causal context.

Do not silently return unless the event is explicitly documented as safely ignorable and
another authoritative reconciliation path guarantees correctness.

### DR-08 — Reconcile current state when history is not the requirement

When a consumer needs the **latest authoritative state**, an event should normally mean
"state changed; reconcile" rather than "execute this historical snapshot as a command".

Prefer:

```text
change event
   -> request one reconcile
   -> read authoritative current state on owner lane
   -> derive desired state
   -> apply only necessary transition
```

over queueing every transient state snapshot.

Coalesce duplicate reconcile requests when bursts can otherwise create redundant work.
Coalescing must not lose a change that occurs while reconciliation is running; use a
small pending/dirty mechanism where necessary rather than a generic framework.

### DR-09 — Keep commands, facts and state-change signals distinct

An immutable event value is a fact that occurred. A command expresses an action/request.
A current-state query returns authoritative state.

Do not turn a state-change notification into a command merely because the event contains
a convenient snapshot. Do not add command semantics to diagnostic/logging events.

### DR-10 — Keep execution ownership visible

A component may own a logical serial lane without owning the physical worker behind it.
Classes that receive an externally owned executor/lane must not shut down shared physical
workers.

Do not create another executor, scheduler or thread merely to avoid understanding the
existing ownership boundary. Add physical parallelism only when design/measurement
justifies it.

### DR-11 — Keep asynchronous sequencing with the lifecycle owner

Multi-step asynchronous work belongs with the component that owns the lifecycle being
implemented. Small reusable execution primitives may supply admission, delayed
continuations, bounded waiting and cancellation mechanics.

Do not move lifecycle policy into a helper such as a switcher only because that helper can
call all the required methods. Do not create a component-local generic
`CompletableFuture` sequencing framework when the sequence is small and specific.

### DR-12 — Separate status, metrics and logging

These three mechanisms answer different operational questions:

```text
status   -> What is true now?
metrics  -> How often / how much / how full?
logging  -> What happened, in what order, and why?
```

Do not use only metrics when chronological diagnosis is required. Do not use logs as the
only source of current authoritative state. Do not add high-cardinality historical detail
to status objects merely to avoid proper logging.

### DR-13 — Log state transitions and abnormal control decisions

Logging must make meaningful control behaviour reconstructable after a run.

Normally log:

- component activation/deactivation failure;
- meaningful desired-state changes when they trigger control work;
- operational state transitions and degraded/recovered transitions;
- queue/admission rejection that can affect behaviour;
- timeout/cancellation/provider failure with the owning component context;
- recovery start, retry outcome and terminal failure when recovery exists;
- configuration changes that alter runtime control behaviour.

Do **not** log every high-rate observation, queue acceptance or periodic successful
rotation at INFO merely for traceability. Use DEBUG/TRACE-like detail only when the
project logging stack supports it and the volume is appropriate; use metrics for rates and
counts.

Typical level intent:

| Level | SI-01 intent |
| --- | --- |
| DEBUG | detailed accepted control/reconcile decisions useful during diagnosis |
| INFO | meaningful lifecycle/desired-state/operational transitions |
| WARN | degraded operation, rejected work, recoverable timeout/failure, skipped work |
| ERROR | component cannot fulfil its role or an unrecoverable control failure escaped normal containment |

### DR-14 — Put useful identity and cause in diagnostic records

A diagnostic record should carry enough context to answer which component/object and why,
without requiring the reader to correlate unrelated lines by guesswork.

Where applicable include stable identifiers such as TimingNodeId/AntennaId, the requested
or desired state, the previous/current state, admission/failure reason and exception.

Avoid dumping complete mutable objects or sensitive/provider-private payloads into logs.

### DR-15 — Keep failure and recovery boundaries local

The component that owns a recoverable mechanism owns its recovery state. Higher layers
retain application intent and should not repeatedly replay low-level repair commands.

A failure that is intentionally contained must still update visible health and diagnostic
state. Automatic retry/backoff/limit policy requires explicit design authority; do not
smuggle it into a catch block.

### DR-16 — Test the non-happy path that the design depends on

When a component relies on bounded admission, lifecycle ordering, reconciliation,
cancellation or contained failure, add focused tests for those semantics.

At minimum, as applicable, cover:

- not-running admission;
- full/rejected admission;
- activation/deactivation ordering;
- stale/coalesced state-change handling;
- timeout/cancellation;
- contained downstream/provider failure;
- desired-state change while asynchronous work is pending.

A happy-path unit test is not evidence for overload or lifecycle semantics.

### DR-17 — Document non-obvious intent, ownership and constraints

Code should be understandable from its public/component boundary before a reviewer must
reverse-engineer the implementation.

Use Javadoc or nearby comments when they explain information that is not obvious from the
Java syntax, especially:

- what a component owns and what it deliberately does **not** own;
- lifecycle meaning and valid call order;
- thread/lane ownership and whether a method is expected to run on a specific lane;
- asynchronous sequencing, cancellation and stale-work guards;
- invariants such as single-writer, at-most-one-active-member or bounded-queue behaviour;
- why a seemingly simpler implementation would violate a requirement/design decision;
- externally important side effects or failure-containment behaviour.

Public component boundaries and reusable abstractions need enough Javadoc to answer:
**what is this for, who owns it, how is it used, and what are the important lifecycle or
threading constraints?**

Comments should explain **intent, contract or rationale**, not narrate obvious syntax.
Avoid comments such as "increment index", "set flag" or "loop over antennas" when the code
already says exactly that.

A complex method is not made acceptable merely by adding many comments. If a comment is
needed to explain several unrelated responsibilities, first check whether the code should
be simplified or split.

Comments and Javadoc are part of the maintained design surface. When behaviour or
ownership changes, update or remove stale comments in the same change. A misleading
comment is worse than no comment.

### DR-18 — Use one implementation language and stable terminology

Java source uses **English** for:

- identifiers and type/member names;
- comments and Javadoc;
- log messages;
- exception messages;
- test names and test diagnostics.

Use terminology already established by the SSD/SDD/interface documents and domain model.
Do not introduce a new synonym simply because it sounds convenient in one class.

Examples of terminology that should stay distinct include:

- `activate/deactivate` for software-component lifecycle;
- `OPEN/CLOSED` for TimingNode operational lifecycle;
- `initialize`, `inventory` and `shutdown` for antenna/provider operations;
- `desired state`, `actual state` and `reconcile` where that model is used;
- `TimingNode`, `AntennaManager`, `TagProcessor` and other established component names.

Prefer specific names that reveal role and meaning over vague names such as `data`,
`handler`, `manager`, `process`, `doWork` or `obj` when a more precise domain or
technical term is available. Generic names remain acceptable when the abstraction itself
is genuinely generic and the surrounding type makes the role unambiguous.

Log and exception messages should be concise, grammatical English and include operational
context rather than implementation trivia. Avoid unexplained abbreviations, casual wording
and multiple spellings for the same concept.

## Review check

For Java changes touching component behaviour, review the following before merge:

1. **Owner** — Is policy located with the component/layer that owns its meaning?
2. **Authority** — Is any new retry/fallback/recovery behaviour supported by design?
3. **Lifecycle** — Are side effects explicit and are lifecycle verbs unambiguous?
4. **Thread boundary** — Can an event callback block or execute downstream behaviour?
5. **Admission** — Is there one atomic admission decision with all outcomes handled?
6. **Failure direction** — Can a downstream failure leak back into an unrelated producer?
7. **Freshness** — Does the consumer need every event, or only authoritative current state?
8. **Observability** — Can status, metrics and logs together explain a failure afterwards?
9. **Logging volume** — Are meaningful transitions logged without flooding high-rate paths?
10. **Comments/Javadoc** — Are non-obvious ownership, lifecycle, threading and rationale documented without narrating obvious syntax?
11. **Language** — Does the code use clear English and the established project/domain terminology consistently?
12. **Verification** — Is the important overload/lifecycle/failure behaviour tested?

A review may cite the stable rule identifier, for example `DR-06`, rather than restating
the entire rationale in each pull request.

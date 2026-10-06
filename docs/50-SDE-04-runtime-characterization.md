# Runtime Characterization Environment (SDE)

Status: draft engineering baseline

## Purpose

This Software Development Environment document defines the engineering environment used
to characterize Timing Point Application runtime behaviour on a development host.

It defines the measurement harness, JVM/OS observations, repeatable workload execution
and retained evidence. It does **not** define product performance requirements, TimingNode
domain behaviour or implementation-step scope.

## Terms and abbreviations

- **SDE** — Software Development Environment
- **JVM** — Java Virtual Machine
- **GC** — Garbage Collection
- **JMX** — Java Management Extensions

## Relationship to other documents

The SIP decides when runtime characterization is needed and which planning questions a
roadmap step must answer. The SVP defines verification/characterization method and evidence
rules. The VTS may later define stable concrete characterization cases.

Product-side observability needed by the harness is software design and belongs in the
SI-01 SSD/SDD. This SDE owns only the engineering environment and tooling used to drive
and observe that design.

The Java build/runtime baseline remains owned by
`50-SDE-02-java-build-test-toolchain.md`.

## Engineering objectives

The environment must make it possible to:

- drive one TimingNode through the same accepted simulated-input and commit path used by
  the application design;
- generate deterministic steady, burst and growing-history workloads without physical
  RFID hardware;
- observe enough execution, persistence and JVM behaviour to locate a bottleneck without
  turning measurement into a second product event model;
- compare an unchanged baseline with a candidate design under the same workload;
- retain machine-readable evidence with source/build/environment identity;
- repeat important cases later on the selected target without treating development-host
  results as target evidence.

## Scope and boundary

Runtime characterization uses a dedicated **engineering harness**, separate from the
formal black-box `system-test` module.

The separation is deliberate:

```text
system-test
  separate packaged SI-01 process
  supported public interfaces only
  no product Java imports
  formal externally observable verification

runtime-characterization harness
  engineering-only Maven profile/module
  may depend on timing-point-core
  composes deterministic runtime fixtures directly
  may read internal engineering diagnostics
  never ships as part of the product artifact
```

Do not add an IF-03 metrics/simulation endpoint merely to make characterization convenient.
A public interface is added only when product behaviour independently requires it.

The harness may use the real file-backed TimingData persistence path and may also use a
controlled engineering fixture when a specific question requires deterministic delay or
failure injection. Evidence must state which persistence mode was used.

## Required product-side observability

The harness needs a narrow pull-based engineering view of the runtime. The detailed Java
placement is owned by the SI-01 design, but the engineering requirement is:

- count antenna/tag observations and resolution/filter outcomes;
- observe bounded TimingNode admission, queue depth/high-water and rejected admission;
- measure monotonic queue wait and serial execution duration;
- measure TimingData persistence attempts/failures/duration and committed count;
- observe post-commit event-delivery duration/failure where it can affect the producer
  lane;
- measure the cost of the bounded LogBook/history query shape under characterization;
- capture process/JVM heap, live-thread and GC observations on demand;
- obtain project-owned thread CPU time where the selected JVM exposes it;
- record the configured/default JVM thread-stack size and total live thread count;
- observe thread/native-memory reserved versus committed memory where the target
  JVM/OS exposes reliable data for it;
- characterize whether an explicit lower `-Xss` is useful and safe on the target
  Raspberry Pi deployments rather than inheriting a workstation-oriented default
  without evidence.

These observations are diagnostic engineering state. They are not TimingData, domain
state, public IF-03 semantics or a second logging/event stream.

The default design direction is aggregate primitive counters and monotonic duration
summaries read on demand. Avoid per-observation metrics objects, continuous measurement
threads and high-volume measurement logging unless a later measured question explicitly
requires them.

The SI-01 design keeps those measurements outside the public TimingNode Domain contract.
The harness receives `runtime.measurement.RuntimeMeasurementReader` from its direct
`timing-point-core` composition and reads `TimingNodeRuntimeSnapshot`,
`TagProcessingCounters.Snapshot` and `JvmRuntimeSnapshot`. It does not use
`TimingNode.runtimeMetrics()`, `TimingNodeTypes.RuntimeMetrics` or an IF-03 endpoint.

## Environments and tools

### Baseline Java environment

Use the same canonical Java baseline as normal SI-01 development:

- repository Maven Wrapper;
- canonical Java 8 toolchain/pinned JDK from the Java build baseline;
- normal project artifact/core revision being characterized.

A characterization result always records the actual JVM vendor/version and OS.

### Measurement harness

Add an optional Maven profile/module named for runtime characterization. It is engineering
code and is not included in the normal application reactor/artifact unless the profile is
selected.

The harness owns:

- deterministic workload generation;
- synthetic tag/reference fixtures;
- selection of steady/burst/history workload parameters;
- preloading a defined committed-history volume;
- warm-up and measured phases;
- capture of product diagnostic snapshots before/after or at defined checkpoints;
- evidence output.

The harness must not contain alternative registration/commit semantics. It reaches the
same TimingNode-owned commit/persistence path as the design under test.

### JVM observations

The baseline requires only Java/JDK facilities that can be used with the supported Java
baseline:

- `ManagementFactory`;
- `ThreadMXBean` where per-thread CPU time is supported/enabled;
- `MemoryMXBean`;
- `GarbageCollectorMXBean`.

Thread-stack characterization is target-sensitive. A run records the JVM's effective
stack configuration (for example the default/effective `-Xss` or equivalent VM flag)
together with live thread count. Where the selected HotSpot build exposes Native Memory
Tracking or an equivalent reliable mechanism, retain reserved and committed thread-stack
memory as engineering evidence. When that facility is unavailable on the target JVM,
retain the exact alternative OS/JVM observation method used instead of inventing a
portable per-thread byte count.

Java stack-trace depth may be sampled to understand representative call depth, but it is
not interpreted as exact stack bytes because Java/native/JIT frame sizes are not fixed.

The first target comparison covers at least:

- the simple one-antenna Raspberry Pi Zero deployment;
- the Raspberry Pi 3 Model B deployment with the known two-antenna 500 ms multiplex
  configuration.

An explicit lower `-Xss` value is a candidate deployment tuning only after the same
representative workloads complete safely on the target, including persistence, event
publication, presentation and antenna lifecycle activity. Stack-size tuning must not be
used to compensate for accidental thread proliferation.

External profilers, JFR/JMC-style tooling or OS-specific samplers may be used to investigate
a specific finding, but they are not baseline evidence until their exact tool/version and
collection procedure are qualified. The basic characterization must not depend on a
workstation-only commercial/proprietary profiler.

## Workload model

A concrete characterization case defines at least:

- workload name/version;
- deterministic seed or exact ordered input set;
- observation count/rate or burst shape;
- known/unknown tag mix;
- configured TimingNode count;
- aggregate registration rate and its per-node distribution;
- initial TimingNode state and LocationId for each active node;
- preloaded committed-record count;
- TimingNode queue capacity;
- persistence mode;
- warm-up definition;
- measured interval/repetition count.

Do not encode product limits into these fixture values. They are engineering workloads.

The current reference stress workload uses **20 registrations per second aggregate across
the complete SI-01 application**. That is a characterization input, not 20/s per
TimingNode and not yet a product limit. Multi-node runs keep the same aggregate rate and
vary its distribution (for example one node at 20/s, or two nodes at 10/s each) so worker
fairness, queue growth and persistence delay can be compared without silently multiplying
the required Raspberry Pi capacity.

Use multiple measured repetitions for a comparison and retain ordinary variation; do not
keep only the best run. Candidate changes use the same workload definition as their
baseline unless the question explicitly concerns scaling.

## Workflow

```text
canonical source/build revision
        |
        v
prepare clean characterization work directory
        |
        +--> deterministic reference/input fixture
        +--> optional preloaded TimingData history
        |
        v
warm-up phase
        |
        v
capture JVM/runtime start observation
        |
        v
run measured workload through normal simulated-input path
        |
        v
capture runtime/JVM end observation
        |
        v
write retained evidence
        |
        v
repeat / compare baseline and candidate
```

A measurement run does not decide architecture by itself. Results feed the SIP A03
decision, which records whether the simple design remains adequate or whether a specific
optimization has evidence behind it.

## Reproducibility and evidence

Retain one machine-readable summary per run with at least:

- repository/source revision and application version;
- JVM vendor/version and OS;
- workload definition/parameters;
- relevant runtime configuration;
- initial history size and queue capacity;
- observation/resolution/admission/commit counts;
- queue depth/high-water and rejection counts;
- queue-wait, execution, persistence and relevant event-delivery summaries;
- history/query cost where exercised;
- heap/GC/thread observations that were available;
- effective thread-stack configuration, live thread count and, where supported,
  reserved/committed thread-stack or native-memory observations;
- run start/end and outcome;
- tool/harness revision.

A compact JSON summary is preferred for retained run metadata/results. Bulk/raw samples
are retained only when a concrete analysis requires them; aggregate evidence is the normal
case.

## Open engineering questions

- exact Maven module/profile name and evidence publication path (T01);
- whether a specific workload needs raw sample retention in addition to aggregate summaries;
- which development-host cases are important enough to repeat during later target bring-up.

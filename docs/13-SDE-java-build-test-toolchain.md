# Java Build and Test Toolchain (SDE)

Status: working baseline / AP-2

This document refines the system-level Software Development Environment for Java repositories. It defines the **engineering toolchain roles, build/test matrix, artifact flow and reusable-tool boundary** needed before the first SI-01 implementation repository is bootstrapped.

It does not define SI-01 product behaviour. Product requirements remain in the SRD/IDD/SAD/SDD documents, and verification intent remains owned by the SVP.

## Why this document exists

A Java repository alone is not yet a reproducible engineering environment. Before creating the first implementation repository the project needs a deliberate answer to:

- which environments build and test Java code;
- which operating systems are verified;
- how Maven itself is provisioned;
- which JDK/API baseline is authoritative;
- which job produces the canonical application artifact;
- how that same artifact is exercised on other platforms;
- which parts are generic enough to reuse across future Java repositories;
- when a dedicated/self-hosted machine is actually justified.

This document exists because those decisions are cross-repository SDE policy rather than SI-01 application design.

## Engineering roles are not physical machines

The toolchain defines **roles/environments** first. One physical computer or hosted runner can fulfil more than one role.

Initial roles:

```text
Windows developer workstation
  interactive development and demonstrations
  local Maven Wrapper build/test
  local application execution

GitHub-hosted Linux CI
  canonical CI build
  compile + unit/component verification
  package canonical Java artifact
  provenance/build metadata
  fast system-test jobs when available

GitHub-hosted Windows CI
  Windows compatibility build/test
  Windows execution/smoke verification
  later ST-1 compatibility execution

Raspberry Pi Zero target
  target execution only after the target/deployment SIP increment
  ARMv6-compatible Java 8 runtime
  resource/ST-4/HIL evidence

Optional integration/test controller
  not required initially
  later Docker/RabbitMQ services
  longer-running tests
  target/HIL orchestration when hosted CI is insufficient
```

A separate physical build server or Java test server is therefore **not an initial requirement**.

## Initial platform matrix

| Environment | Build source? | Unit/component tests | Runs canonical artifact | Main purpose |
| --- | --- | --- | --- | --- |
| Windows developer workstation | yes | yes | yes | interactive development and stakeholder demo |
| GitHub Ubuntu runner | **yes — canonical** | **yes** | yes | authoritative CI build/package path |
| GitHub Windows runner | yes, compatibility | yes | **yes** | detect Windows-specific build/runtime problems |
| Original Raspberry Pi Zero / Zero W | no normal source build required | selected target tests | **yes** | target viability/resource/HIL evidence |
| Optional Linux integration host | optional | integration/system | yes | external services and longer test orchestration |

The matrix can grow only when there is evidence that another environment materially improves verification or deployment.

## Java baseline

The first SI-01 baseline remains **Java SE 8** because the original Raspberry Pi Zero / Zero W is mandatory.

Toolchain implications:

- the canonical compile runs with a Java 8 JDK, not merely a newer JDK configured with `source=8`;
- Maven compiler/source/target settings must enforce Java 8 bytecode/source compatibility;
- the CI job records the actual JDK vendor/version used;
- source code remains vendor-neutral at the Java SE/API boundary;
- the Pi may use a different ARMv6-capable Java 8 runtime vendor from hosted CI without changing the application artifact;
- Java 11 remains a later evidence-driven compatibility/upgrade checkpoint, not part of the first canonical build.

The exact hosted-CI JDK distribution and patch version should be pinned/configured in the reusable workflow when that workflow is implemented. The exact Pi runtime is selected by the target-image SIP increment after ARMv6 evidence.

## Maven Wrapper policy

Every Java consumer/implementation repository should carry the Maven Wrapper:

```text
mvnw
mvnw.cmd
.mvn/wrapper/...
```

Normal commands are therefore repository-owned:

```text
Linux/macOS/CI:
  ./mvnw verify

Windows:
  mvnw.cmd verify
```

This avoids requiring every workstation or runner to install an independently managed Maven version.

Rules:

- the wrapper pins the Maven distribution used by the repository;
- CI invokes the wrapper rather than a runner-global `mvn` installation;
- wrapper files are source-controlled and reviewed;
- changing Maven version is a deliberate repository/toolchain change;
- the JDK remains an environment prerequisite and is provisioned explicitly by CI/developer setup.

## Canonical build and artifact model

The normal Java application artifact should be platform-neutral where the code/dependencies permit it.

Preferred flow:

```text
source commit
    |
    v
GitHub Linux canonical build
  pinned JDK 8 policy
  Maven Wrapper
  ./mvnw verify
    |
    +--> test reports
    +--> build/provenance manifest
    +--> canonical Java artifact(s)
                 |
                 +--> Linux execution/smoke
                 +--> Windows execution/smoke
                 +--> later Pi Zero execution
```

The project should **not** produce a separate Windows JAR, Linux JAR and Pi JAR merely because those operating systems are different.

A platform-specific artifact is justified only when a genuine native/platform dependency makes it necessary. Such a dependency must remain behind an appropriate adapter/module boundary rather than silently making core Java code platform-specific.

## Canonical versus compatibility builds

Two related questions need evidence:

1. can the source build/test correctly on an environment?
2. can the **same produced artifact** execute on another supported environment?

The toolchain should eventually verify both.

Initial CI direction:

```text
linux-canonical
  checkout
  set up JDK 8
  ./mvnw verify
  collect reports
  create/upload canonical artifact
  record build metadata

windows-compatibility
  checkout
  set up JDK 8
  mvnw.cmd verify

windows-artifact-smoke (when runnable app exists)
  download canonical artifact from linux-canonical
  java -jar ...
  execute first public smoke/ST-1 check
```

A Linux artifact-smoke job may use the same canonical artifact as an additional packaging sanity check.

## Build provenance

A produced artifact should be traceable without relying on a developer's workstation memory.

The build/release evidence should record at least:

```text
repository
source commit SHA
source ref/tag where applicable
project/application version
build timestamp or reproducible-build epoch policy
JDK vendor/version
Maven version from Wrapper
workflow/toolchain version
OS/runner class used for canonical build
```

Where practical, the application should embed enough non-secret build identity to answer its public version query without reading CI logs.

Reproducible-JAR settings such as a controlled Maven build output timestamp should be considered when the first Maven reactor is created.

## Test execution responsibility

The toolchain executes tests; the SVP defines what the tests mean.

Initial allocation:

### Linux canonical CI

- compile all modules;
- unit tests;
- deterministic component/module tests that need no platform-specific behaviour;
- architecture/dependency checks;
- package artifacts;
- later fast ST-1 tests where practical;
- publish reports/artifacts.

### Windows compatibility CI

- compile/test with the same Java source/API baseline;
- catch path, shell, filesystem and process-launch differences;
- run the canonical application artifact once it exists;
- later run a compact ST-1 compatibility subset.

### Raspberry Pi Zero

- do not use the Pi as the normal project build machine;
- run the already-produced canonical artifact;
- verify ARMv6 runtime compatibility;
- collect startup/RSS/CPU/thread/latency evidence;
- run selected target/ST-4 scenarios.

### Optional integration host

Introduce only when needed for capabilities that are awkward or inappropriate on hosted runners, for example:

- long-running RabbitMQ/recovery tests;
- hardware access;
- Pi image deployment/orchestration;
- CAN/RFID/display HIL;
- multi-target endurance testing.

## Docker policy

Docker is **not** part of the basic Java compile/unit-test toolchain.

Use Docker/Compose when a real external service materially improves verification, for example RabbitMQ in ST-3.

This keeps:

```text
normal Java verify
  JDK + Maven Wrapper
```

independent from:

```text
integration service fixture
  Docker/Compose + RabbitMQ/etc.
```

## Reusable `tool.java-project` boundary

Working repository name:

```text
tool.java-project
```

The name is provisional until that repository is created.

The reusable tool repository should own **generic Java-project engineering behaviour**, not product behaviour.

Good candidates:

```text
.github/workflows/
  reusable-java-verify.yml
  reusable-java-artifact.yml
  later reusable-integration entrypoints

templates/ or examples/
  minimal consumer workflow
  Maven Wrapper/bootstrap guidance

scripts/ (only when a script is genuinely reused)
  build/provenance collection
  project/toolchain validation

docs/
  supported inputs/outputs
  versioning/release policy
  consumer migration notes
```

Potential later candidates, only after repeated need is proven:

- a reusable Maven parent/convention artifact;
- a Maven plugin for project-specific convention checks;
- shared test-support tooling that is not timing-domain-specific.

Do **not** put the following in `tool.java-project`:

- SI-01 module layout as a hard-coded product assumption;
- timing-domain requirements;
- RFID/CAN/display behaviour;
- proprietary/private protocols or credentials;
- real deployment identities;
- Raspberry Pi image content that is specific to SI-01;
- RabbitMQ topology that belongs to a product/integration contract.

## Relationship to existing reusable tooling pattern

The existing SCAD tooling separates reusable project workflow from its runtime/toolchain and from consumer projects. The Java toolchain should preserve the same responsibility discipline without copying implementation mechanisms blindly.

In particular:

- Java consumers should normally use versioned/released reusable workflows rather than depend on an unversioned branch;
- Maven Wrapper remains local to each Java repository;
- a Git submodule is **not** assumed to be the Java reuse mechanism;
- reusable CI should be referenced by an immutable commit or a deliberately managed release tag/version;
- consumer projects must still be buildable/testable locally without requiring the reusable GitHub workflow repository at runtime.

## Toolchain release/use direction

A reusable toolchain change should be testable before consumers adopt it.

Target model:

```text
tool.java-project change
       |
       v
its own CI + reference consumer tests
       |
       v
versioned release/tag
       |
       v
consumer workflow pins/adopts that version
```

Consumer updates can then be reviewed as normal dependency/tooling changes rather than silently changing every project when `main` moves.

## First consumer expectation

The eventual SI-01 implementation repository becomes the first real consumer and validation project.

A clean checkout should require no globally managed Maven installation:

```text
Windows developer
  JDK 8 + Git
  mvnw.cmd verify

Linux CI
  provision JDK 8
  ./mvnw verify

Windows CI
  provision JDK 8
  mvnw.cmd verify
```

Once the application artifact exists, the exact artifact produced by the canonical Linux build should also be run by the Windows compatibility job and later by the Pi target step.

## Dedicated build/test hardware decision

Initial decision: **do not create a dedicated self-hosted build server yet**.

Rationale:

- GitHub-hosted Linux and Windows runners cover the first cross-platform build/test need;
- the developer workstation provides interactive Windows evidence;
- the Pi Zero provides target evidence;
- a self-hosted machine introduces patching, credentials, runner security and availability work before it solves a demonstrated problem.

Revisit this decision when external services, HIL, endurance or target orchestration need a stable local controller.

## Initial deliverable boundary

Before the SI-01 implementation repository is bootstrapped, the engineering baseline should be able to answer:

1. What command builds/tests a clean Java checkout on Windows and Linux?
2. Which environment is the canonical artifact producer?
3. What Java/Maven versions/policies are recorded and controlled?
4. How are test reports and artifacts retained?
5. How do we prove the canonical artifact is portable to Windows and later the Pi?
6. Which workflow/tooling logic is generic and belongs in a reusable tool repository?
7. Which configuration remains consumer/product-specific?

The next implementation increment may create the reusable tool repository and a minimal reference/fixture consumer before SI-01 adopts it.

## Open AP-2 decisions

- exact JDK 8 distribution/version used on GitHub Linux/Windows runners;
- exact Maven Wrapper/Maven version to pin initially;
- exact reusable-workflow inputs/outputs;
- whether canonical artifact publication initially uses workflow artifacts only or also a package/release channel;
- naming/version policy for `tool.java-project` releases;
- whether a minimal generic reference consumer lives inside the tool repository or as a separate template/test repository;
- when repeated Maven configuration justifies a reusable parent/convention artifact;
- exact checks used to prove the canonical JAR remains platform-neutral.

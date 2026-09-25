# 60-01-SUM — Headless Timing Application

Status: working release-oriented user manual  
Software item: **SI-01 — Headless Timing Application**

## 1. Purpose, audience and applicability

This is a **technical software user manual**, not an end-user/operator manual for the
timing system.

Its intended audience is developers, integrators, testers and operations/support
engineers who need to obtain, build, configure, start, stop or diagnose SI-01. It does
not describe timing-event workflows for an operator or other product end user.

This manual records how an identified SI-01 software release is obtained, built,
configured, started and stopped. It also records the compatible development/runtime
baseline needed to reproduce that release.

The detailed development-environment documents remain authoritative for how tooling is
managed. This manual answers the technical release/user question: **which combination
belongs with this software version, and how do I run or work with it?**

A released row in the compatibility matrix is immutable historical guidance. The
current development row may change until it is promoted to a normal software release.

## 2. Compatibility matrix

| Software baseline | Java | Maven | Maven Wrapper | tool.git-project | tool.java-project | Windows / IDE status | Runtime/configuration |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **v0.2.1** | Temurin 8.0.504+1 / Java SE 8 | 3.9.16 | 3.3.4 | v0.2.8 | v0.3.2 | Windows is the primary development host; NetBeans version is not pinned for this release | Short-lived executable baseline; no external application configuration required |
| **0.2.2-SNAPSHOT** — current development line, not a release | Temurin 8.0.504+1 / Java SE 8 | 3.9.16 | 3.3.4 | v0.2.8 | v0.3.2 | Windows/NetBeans A04 acceptance in progress; record the verified NetBeans version before the next release | External `application.yml`; configured TimingNode; long-running process with graceful Ctrl+C/OS shutdown |

Exact immutable tooling commits are recorded in the implementation repository's
`docs/tooling-baseline.md`.

A tool or IDE version only belongs in a released compatibility row after the release
has actually been built/verified with that combination.

## 3. Obtain the software

For a released version, prefer the artifacts attached to the corresponding GitHub
release. Building from source should use the exact release tag when reproducibility is
important.

For source development:

```text
brainboxemb/2026-010-02.java.event-timing-framework
```

Normal clone/bootstrap does not require recursive submodule checkout; repository
bootstrap restores the pinned tooling.

## 4. Open and build on Windows

### Command line

From the repository root:

```powershell
.\bootstrap.ps1
.\mvnw.cmd verify
```

Use the repository Maven Wrapper rather than a separately selected Maven installation
for the normal project build.

### NetBeans

Open the repository root as a Maven project and select a Java 8 JDK matching the
release compatibility row.

The repository contains a committed root `nbactions.xml` for the SI-01 development
workflow. **Run Project** prepares the current reactor and starts the configured
`app/` executable with `config/application.yml`; **Debug Project** uses the same
configured application path and adds the NetBeans JPDA debugger.

The exact NetBeans version is not yet a released compatibility requirement. A04 keeps a
user-facing Windows/NetBeans acceptance check; the version used for that accepted check
should be recorded in this manual before the next software release.

## 5. Application configuration

### v0.2.1

No external application configuration is required by the released v0.2.1 executable
baseline.

### Current 0.2.2-SNAPSHOT development line

The current development application uses one external YAML file. The implemented slice
contains one TimingNode identity:

```yaml
timingNodeId: timing-node-01
```

A synthetic development example is stored as:

```text
config/application.yml
```

Do not infer support for the complete future IF-11 configuration tree from this
development slice.

## 6. Start and stop

### v0.2.1

After building the release tag:

```powershell
java -jar app\target\event-timing-app-0.2.1.jar
```

This baseline performs the short lifecycle used by that release and exits.

### Current 0.2.2-SNAPSHOT development line

After building:

```powershell
java -jar app\target\event-timing-app-0.2.2-SNAPSHOT.jar config\application.yml
```

The configured application remains running. On a normal Windows/Linux foreground
terminal, **Ctrl+C** or the normal OS/JVM shutdown route closes the application through
its graceful lifecycle.

## 7. Build provenance

A built SI-01 artifact identifies itself without requiring a sidecar text/JSON file. The embedded
provenance includes application/version, exact Git revision, source ref, build origin and dirty-state.

Typical development output is expected to distinguish, for example:

```text
revision=c715455...
sourceRef=feature/pr-52-a04-local-console
buildOrigin=local
dirty=false
```

CI-built artifacts use a CI ref/origin instead. Wall-clock build time, CI run id and actor/user are
not embedded because they change per execution and are not required to identify the source context.

## 8. Local console

The local console is Step-3 A04 work. Its intended command set is:

```text
help
version
status
quit
exit
```

Do not list the local console as a released v0.2.1 capability. The command behaviour,
NetBeans run path and user-facing Windows acceptance must be completed before this
section is promoted into the next released compatibility row.

The later remote terminal/shell uses the same application command behaviour through a
different transport; console and remote shell are separate presentation interfaces.

## 9. Troubleshooting

### Build uses the wrong Java version

Check the selected JDK against the compatibility matrix. The current software baseline
targets Java SE 8.

### Tooling checkout does not match the software baseline

Run the repository bootstrap and compare the tooling revisions with
`docs/tooling-baseline.md` in the implementation repository/tag. Do not silently use a
newer tool release and assume it represents the original software baseline.

### Current development configuration is rejected

Start from the synthetic `config/application.yml` in the matching source revision.
The current implementation deliberately rejects configuration fields that do not yet
have an implemented consumer.

### NetBeans behaviour differs from command-line Maven

First verify the same revision with `.\mvnw.cmd verify`. Record the NetBeans/JDK
version used when the difference is investigated. A release compatibility claim should
only be added after that combination is verified.

## 10. Release maintenance

Before a normal SI-01 software release is accepted:

1. update this manual for the release candidate;
2. add or promote the release row in the compatibility matrix;
3. remove development-only wording that no longer applies;
4. verify the documented build/start/stop workflow against the release candidate;
5. record any required Java, Maven, tooling, IDE or configuration-format compatibility;
6. keep detailed engineering-tool policy in the SDE rather than duplicating it here.

This manual is part of the formal software-document set and should evolve with the
software release rather than as an unrelated after-the-fact note.

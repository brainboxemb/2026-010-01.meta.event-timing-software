# Brainstorm

This is the working area for ideas, questions, alternatives, observations, and early software thinking.

Content in this document is **not** an approved requirement or architecture decision unless it is explicitly promoted later.

## Working principles

- Capture first, decide later.
- Separate observations from assumptions.
- Keep alternatives visible until a decision is made.
- Link ideas back to source material where possible.
- Prefer questions over premature answers when evidence is missing.
- Keep generic framework concerns separate from event-specific application concerns.
- Do not use a concrete event name in project documentation; describe the intended domain generically.

## Initial product direction

The intended domain is a distributed timing/registration system for a large relay-style event with multiple waypoints.

Current direction:

- Java is the intended implementation language.
- The software at a waypoint records participant passages using RFID carried by the participant.
- A waypoint system therefore interacts with at least one RFID reader/antenna setup.
- The software should be designed as a reusable framework rather than only as one event-specific application.
- A complete product may later combine public/generic framework components with proprietary/private implementation components.

The exact Java version, framework boundaries, packaging model, and repository split still need to be decided.

## Runtime and application topology

Explore a headless core application as the normal runtime foundation.

Desired direction:

- run on Windows;
- run on Linux;
- run on Raspberry Pi Zero-class hardware;
- allow one running application/process to host one to multiple logical waypoint systems;
- allow one to multiple separate user-facing/control applications to connect to the headless application.

This suggests a distinction between the runtime/service and its user interfaces, but the exact process and module boundaries are not yet fixed.

Questions to resolve:

- Does `1..X waypoint systems` mean multiple fully isolated logical systems inside one JVM, or multiple configured waypoint instances sharing selected services?
- Which resources are shared across instances: logging, backoffice connections, persistence, metrics, hardware access, configuration?
- Should every logical system be independently startable/stoppable/reconfigurable?
- What are the practical CPU and memory limits on the target Raspberry Pi Zero generation?
- Is one Java distribution/package expected to run unchanged on every target platform?

## Waypoints, timing, and RFID observations

A waypoint is expected to observe participant passages through RFID.

Topics that need later requirements and design work:

- RFID reader/antenna abstraction;
- mapping an RFID identifier to a participant or registration known by the wider system;
- conversion of raw RFID reads into a single timing/registration observation;
- handling repeated reads while a participant remains in antenna range;
- handling simultaneous or near-simultaneous participants;
- timestamp source and required precision;
- clock synchronisation between distributed waypoint systems;
- late, duplicate, missing, or corrected observations;
- local persistence/recovery after restart or power loss;
- behaviour when backoffice connectivity is unavailable.

None of these points yet defines the final timing algorithm or RFID hardware contract.

## Waypoint software versus registration hardware terminology

Issue/PR #40 clarified a terminology problem in the earlier architecture sketches: software/domain decomposition, hardware/deployment decomposition and logical data-source identity had been drawn as though they were one ownership tree.

Working direction discussed and promoted in PR #40:

- `WaypointSystem` is the software/domain system operated for one waypoint;
- a waypoint is at the end of a `Stage`;
- a `WaypointSystem` is deployed/configured at a `LocationId`;
- `RegistrationAssetId` identifies a physical registration hardware asset such as `asset-01`;
- a physical registration system can have one or more antennas;
- `DataSourceId` is the logical ordered-stream identity configured for a producing system, for example `asset-01` using `source-01`; another producer may use an unrelated identity such as `source-02`;
- similar-looking hardware and data-source labels are a deployment convenience, not an identity rule;
- the current team-preparation capability is better expressed as one `PrepareTeamRegistry`: it owns both the current teams that must prepare at the waypoint/exchange point and the traceable keypad/operator add/remove history needed for audit/restore; that log is internal registry state rather than a separate architecture component;
- `RaceData` is the waypoint-scoped participant/team/tag reference data used by a `WaypointSystem`; synchronising/loading that data is an application/integration concern rather than a reason to call the data object `RaceDataService`;
- generic `*Service` names should be replaced by responsibility-specific names when the responsibility is actually data/state, a processor, registry, journal or coordinator.

The architecture should therefore maintain separate software/domain, hardware/deployment and configuration/identity-mapping views rather than nesting registration assets and antennas inside the waypoint software component tree.

This topic is being promoted into the working domain/SI-01 architecture in PR #40; implementation/API renames remain a controlled follow-up rather than being silently performed from brainstorm content.

## Headless control and management interfaces

The headless application should expose multiple ways to inspect and control the running system.

Initial interface ideas:

1. a local interactive console/shell;
2. a shell/terminal interface reachable through a remote terminal connection;
3. a machine-readable API, with JSON as an initial candidate representation.

Possible GUI or other operator applications should connect through a defined application interface rather than require the core to have a graphical desktop environment.

Questions to resolve:

- Can the local and remote shell use one shared command model?
- Can the API expose the same command/query model where appropriate?
- Which interfaces are always enabled and which are optional modules?
- How are authentication, authorization, and secure transport handled for remote access?
- Is the future GUI a separate software item/repository or one module in a larger product repository?

## Backoffice communication

The waypoint software communicates with a backoffice system.

RabbitMQ is one intended communication mechanism and should be investigated as a transport/integration option.

The architecture should avoid unnecessarily coupling the domain model to one transport so other communication methods can be supported when needed.

Topics to explore:

- connection lifecycle and reconnect behaviour;
- message contracts and versioning;
- acknowledgement and delivery semantics;
- retry and dead-letter behaviour;
- ordering expectations;
- offline queueing/local buffering;
- idempotency and duplicate delivery;
- configuration of one or multiple backoffice destinations;
- observability of communication health.

## Platform abstraction

A platform abstraction boundary is likely needed because not all facilities and hardware are present on every supported platform.

Examples:

- RFID hardware may only be attached on a production waypoint device;
- GPIO or other Raspberry Pi-specific facilities are unavailable on a normal development PC;
- development/test environments need simulated or fake implementations;
- deployment and service-management behaviour differs between Windows and Linux.

The abstraction should make normal development and automated tests possible without production hardware.

Questions to resolve:

- Which capabilities belong behind platform interfaces versus device-specific interfaces?
- Should hardware simulation be part of the generic framework?
- How should optional capabilities be discovered and reported at runtime?
- How much Raspberry Pi-specific code should exist in the generic repository?

## Architecture layering reference

The repository <https://github.com/SvenWesterhof/embedded-iot-platform> is a useful illustrative reference for the architectural style the project may want, even though that project targets embedded C/C++ systems rather than a Java application.

Relevant ideas to investigate rather than copy literally:

- a thin application/bootstrap layer that composes and starts the system;
- an explicit control/orchestration layer for state machines and higher-level coordination;
- service-style components for reusable/background infrastructure;
- user-facing or protocol-facing features kept separate from low-level platform/device access;
- platform/hardware access hidden behind explicit abstractions;
- a clear dependency direction where higher-level behaviour depends on contracts rather than directly on concrete hardware/platform implementations;
- event-driven or message-driven communication where this usefully reduces horizontal/upward coupling.

A possible Java-oriented interpretation to explore is therefore something conceptually like:

```text
Application / bootstrap
        |
        v
Control / orchestration
        |
        +---- Services / domain capabilities
        |
        +---- Features / external interfaces
        |
        v
Platform + device contracts
        |
        v
Concrete adapters
  - Windows/Linux
  - Raspberry Pi
  - RFID hardware
  - simulated/test implementations
```

This is deliberately only an architectural direction. The eventual Java architecture may fit ports-and-adapters, clean architecture, modular services, or another model better than the exact embedded layering of the reference project.

Questions to resolve:

- Which responsibilities are genuinely distinct enough to justify `control`, `service`, and `feature` concepts in this Java system?
- Should domain/application services know only interfaces/ports while platform and hardware implementations live entirely in adapter modules?
- Is an internal event bus useful for timing observations, device status, command handling, and lifecycle events, or would it add unnecessary indirection?
- How do multiple logical waypoint systems share framework services without accidentally sharing waypoint-specific state?
- Which abstractions are platform-level (clock, filesystem, process/service management, GPIO) and which are device-level (RFID reader, antenna/controller)?
- Can the same contracts support both real hardware adapters and deterministic simulated adapters used by unit/integration tests?

## Modularity and public/private boundaries

The project should remain usable as a generic framework while allowing parts of a later complete application to be developed privately/proprietarily.

Potential implications to explore:

- define stable module/service interfaces rather than allowing implementation details to spread through the codebase;
- keep generic contracts reusable;
- allow selected implementations to live in separate private repositories;
- ensure a complete application can compose public and private modules cleanly;
- avoid designing public components around assumptions that only exist in the private product.

Logging and backoffice communication were specifically identified as areas that may eventually have private/product-specific implementation work. The exact split is still open and should be designed deliberately rather than moved between repositories ad hoc.

Questions to resolve:

- Which modules are generic contracts and which are default implementations?
- Does the public project provide usable reference implementations for all important contracts?
- How are private modules integrated during build, test, and release?
- What dependency direction prevents the generic framework from depending on proprietary modules?

## Java artifact/package boundary exploration

The first framework bootstrap exposed a useful distinction that was not clear enough in the earlier modularity discussion.

Two successive structures were considered and then rejected as too eager:

```text
timing-api / timing-core / timing-runtime / timing-adapters / timing-testkit / timing-app
```

and later:

```text
domain / core / platform / comm / app
```

as one Maven artifact per architectural responsibility.

The improved working direction is:

```text
event-timing-framework.jar
  io.github.brainboxemb.eventtiming.domain
  io.github.brainboxemb.eventtiming.core
  io.github.brainboxemb.eventtiming.platform
  io.github.brainboxemb.eventtiming.comm

event-timing-app.jar
  io.github.brainboxemb.eventtiming.app
```

The reasoning is that an architecture layer/package and a Maven publication boundary answer different questions. A separate artifact should have a concrete consumer or lifecycle reason, for example independent reuse, an optional heavy dependency, deployment/release ownership, or a public/private boundary.

This leaves room for later extraction of infrastructure such as RabbitMQ/platform/device support without creating those libraries before their consumers exist.

The reusable framework should also permit several executable compositions. Examples include a deliberately single-system application and a multi-system/simulation application. Multi-instance registry/routing should remain application-level until it proves generically reusable across applications.

Likewise, reusable event-timing domain behaviour can belong in the framework while one product/application can add specific domain policy through its own composition or extension library.

This direction has been promoted as a **working/non-authoritative design** in PR #7 through `31-01-SDD-03`, `31-01-SDD-04`, and `31-01-SDD-05`. Future splits should be driven by implementation/consumer evidence rather than by keeping an architecture diagram visually symmetric.

## Logging and observability

Use a logging framework rather than direct ad-hoc console output.

Later design should determine:

- logging facade/framework choice;
- configuration model;
- console/file/system logging targets;
- per-waypoint/logical-system context;
- log rotation and retention;
- structured logging where useful;
- separation between normal logs, audit information, metrics, and timing observations;
- behaviour on storage-constrained Raspberry Pi systems.

The Java logging stack is not selected yet.

## Testing strategy

Automated testing is expected from the start.

Desired layers include:

- unit tests;
- integration tests;
- later, where useful, hardware or deployment-level tests.

GitHub Actions is intended for build and test automation.

The CI pipeline should account for the fact that integration tests may become significantly slower than normal unit tests.

Possible model to investigate:

- fast build + unit-test checks on every pull request;
- a separate integration-test job or workflow;
- selective integration tests on normal PRs where feasible;
- broader integration suites on merge, schedule, or explicit request;
- hardware-specific tests separated from tests that can run on hosted GitHub runners.

The exact pipeline is not yet decided.

## Build, versioning, and deployment

Java is selected as the language direction, but the Java release and build tooling still need evaluation.

Potential early development milestone:

- create the smallest runnable application;
- give it an explicit software version;
- make that version queryable through a simple interface;
- then incrementally introduce the architectural building blocks.

This could become the first step in a staged software plan rather than attempting the complete architecture in the first implementation.

Longer-term deployment direction:

- automate build/package creation;
- automate testing through GitHub;
- eventually support automated deployment of the application to a Raspberry Pi target.

Questions to resolve:

- Java version/LTS baseline;
- Maven versus Gradle or another build approach;
- packaging format and runtime distribution;
- whether to ship a bundled Java runtime;
- service installation/startup model on Linux/Raspberry Pi;
- safe update/rollback strategy;
- how deployment credentials and device identities are managed.

## Documentation model

A deliberate software documentation set is wanted rather than putting everything in one architecture document.

### Project-level software documentation

Potential documents:

- **Requirements** — system-level functional and non-functional requirements.
- **Software architecture** — system decomposition, architectural principles, boundaries, runtime topology, major interfaces, and cross-cutting concerns.
- **Software development** — development environment, tooling, repository conventions, Git/PR workflow, build tooling, testing approach, coding conventions, and local developer setup.
- **Software plan** — staged implementation approach and major development increments.
- **Software planning** — tracked roadmap/milestones derived from the plan; exact distinction from the software plan still needs refinement.

The software plan could act as the higher-level anchor for a deliberately staged implementation, for example beginning with a minimal versioned executable before adding complex capabilities.

### Interface documentation

A working documentation convention is that an **Interface Design/Description Document (IDD)** is a **software-system-level document**, not documentation owned by one software item.

The intended traceability model is:

- the IDD defines the interface contract at software-system level;
- a software-item requirement may reference an IDD, or a specific identified part of an IDD, as a requirement applicable to that software item;
- the software item therefore implements/conforms to the system-owned interface definition rather than duplicating that interface definition in its own requirements document;
- interface identifiers and requirement identifiers should support traceability between the system interface definition, the applicable software-item requirement, implementation, and verification.

The exact IDD template, identifier scheme, and reference syntax still need to be defined.

### Software-item documentation

In addition to system-level documentation, individual software items may need their own documentation.

Possible software items include:

- headless core application;
- GUI/operator application;
- RFID/device integration;
- backoffice communication components;
- platform-specific adapters;
- reusable framework modules.

Each relevant software item could have its own focused requirements/design documentation while remaining linked to the system-level architecture and system-level interface documents.

The exact document hierarchy and naming convention still need to be designed.

## Architecture documentation and diagrams

Architecture should be documented visually as well as textually.

Candidate approaches:

- Mermaid for diagrams that work naturally as text in Markdown;
- draw.io for diagrams that need richer manual layout;
- preferably generated or assisted diagrams where practical, potentially using Python, to avoid repetitive manual alignment/editing work.

A useful principle to investigate is keeping authoritative diagram information in a text-reviewable form where possible while using richer generated outputs for presentation when needed.

Questions to resolve:

- Which diagram types are required: system context, containers/components, deployment, data flow, sequence, state, interface/dependency views?
- Can Mermaid cover most architecture views acceptably?
- Can draw.io files be generated or updated predictably from Python when richer diagrams are needed?
- What belongs in source-controlled architecture documentation versus generated project-dashboard content?

## Agent-driven development workflow

Keep an agent plan separate from the software plan.

Current intended distinction:

- the **software plan** describes how the software itself is expected to evolve;
- the **agent plan** breaks the current work into executable coordination steps for coding agents/chat sessions;
- detailed work and evidence for the active step live primarily in its pull request rather than turning the long-term agent plan into a detailed activity log.

The repository's normal Git workflow should follow the PR-first approach established for the project: work is performed on a numbered feature branch attached to a draft pull request and merged only when the step is ready.

## Project dashboard and documentation

Explore a GitHub Pages dashboard for this meta repository.

Ideas:

- use the central `brainboxemb.dashboard` as a visual and structural reference rather than inventing an unrelated presentation style;
- show planning progress;
- provide document navigation;
- surface decisions and open topics;
- index collected reference material;
- link to related implementation repositories when those are created;
- potentially expose high-level software-plan/agent-plan progress without duplicating their authoritative Markdown content.

The exact information model, generation approach, and scope are still open questions; this is not yet an implementation decision.

## Reporting and exports

Still to be discussed.

Potential future topics include operational reports, diagnostic exports, backoffice reconciliation data, and support bundles, but no format or requirement is defined yet.

## Technology choices still open

Known direction:

- Java application;
- headless-first architecture;
- Windows, Linux, and Raspberry Pi Zero-class target environments;
- GitHub Actions for automated build/test;
- unit and integration testing;
- RabbitMQ as at least one backoffice communication option;
- a real logging framework;
- APIs/interfaces that permit multiple operator/control clients.

Still to select or validate:

- Java version;
- Maven/Gradle/build tooling;
- logging stack;
- API technology/protocol;
- remote shell technology;
- configuration format/library;
- dependency injection/module model, if any;
- persistence approach;
- RabbitMQ client and message conventions;
- GUI technology;
- packaging/deployment model;
- diagram tooling.

## Open questions

- Which source documents already exist and should be collected first?
- Which terminology in those documents should become project terminology, and which is specific to a source system?
- Which concerns belong in a reusable framework and which belong in a concrete application built on top of it?
- What exactly defines one logical `waypoint system` inside a multi-system runtime?
- What timing precision and clock-synchronisation guarantees are actually required?
- How should a waypoint continue operating when backoffice connectivity is lost?
- What is the expected RFID hardware and what abstraction can remain hardware-independent?
- Which functionality must remain usable on the lowest-spec Raspberry Pi target?
- Which modules need to be public/generic and which may eventually have private implementations?
- Which command/query capabilities should be common across console, remote shell, API, and future GUI clients?
- What information would be most useful on a project-specific meta dashboard, and which information should remain in Markdown only?
- What is the intended distinction between `software plan` and `software planning`, or should these ultimately be one document?
- What IDD template, identifier scheme, and software-item requirement reference syntax should be used?
- Which concepts from the embedded architecture reference should become actual Java architectural rules, and which should remain inspiration only?

## Decision candidates

Possible candidates for later formalisation, not yet approved decisions:

- Java as the primary implementation language.
- Headless core as the primary runtime model.
- Support for Windows, Linux, and Raspberry Pi Zero-class systems.
- Multiple logical waypoint systems per running core application.
- Multiple external control/operator clients per running core application.
- RFID as the participant observation mechanism at waypoints.
- RabbitMQ as one supported backoffice transport.
- A platform/device abstraction layer for unavailable or platform-specific capabilities.
- A service-oriented application structure with explicit dependency direction and platform/device adapters, inspired by the embedded architecture reference but adapted for Java.
- Unit and integration tests as first-class development practices.
- GitHub Actions as the initial CI platform.
- Separate system-level and software-item-level documentation.
- IDDs as software-system-level interface documents referenced by applicable software-item requirements.

When a brainstorm topic is mature enough to become authoritative, record the promotion explicitly and link to the resulting document or decision record rather than silently deleting its history here.
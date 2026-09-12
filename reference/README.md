# Reference material

This directory is the collection area for source documents and other reference material used by the meta project.

## Conventions

For each collected source, record enough context to understand:

- what the source is;
- where it came from;
- its date or version when known;
- whether it is authoritative, historical, illustrative, or uncertain;
- why it is relevant to the project;
- any important limitations or interpretation notes.

Prefer preserving original source material rather than rewriting it. Project interpretations, questions, and possible software consequences belong in `docs/00-brainstorm.md` until they are deliberately promoted.

Do not use filenames or notes that identify the specific real-world event that motivated this project.

## Sources

### 4+1 architectural view model

Source: Philippe Kruchten, *Architectural Blueprints — The “4+1” View Model of Software Architecture*, IEEE Software 12(6), November 1995, pp. 42–50.

Reference copy: <https://www.cs.ubc.ca/~gregor/teaching/papers/4+1view-architecture.pdf>

Type: software-architecture documentation/model reference.

Relevant aspects:

- architecture is described through multiple concurrent views rather than one diagram that mixes several meanings;
- logical, process, development and physical/deployment concerns are kept distinguishable;
- selected use cases/scenarios form the `+1` view and help discover and validate architectural elements;
- the model is intentionally generic and does not require one specific notation/tool;
- the development view is about source/module/subsystem organisation, while the process and physical views address runtime/concurrency and software-to-hardware deployment respectively.

For this project the model is a **review framework**, not a requirement to create five separate documents. Existing SSAD/SAD/SDD/UC documents should be organised so each section/diagram has one clear abstraction level and view purpose, and new SDDs should only be created where separate detailed design has a real engineering purpose.

### Embedded IoT Platform architecture reference

Source: <https://github.com/SvenWesterhof/embedded-iot-platform>

Type: illustrative architecture reference.

Relevant aspects:

- layered separation between application, control/services/features, OS/runtime facilities, and drivers/HAL;
- explicit hardware/platform abstraction;
- service-style infrastructure components;
- event-driven communication used to reduce direct coupling between layers;
- separation between target-specific implementation and shared/common functionality.

This is an embedded C/C++ architecture and is **not** a prescribed implementation model for the Java software. It is retained as a useful reference for the kind of service layering, dependency direction, and platform abstraction the project may want to achieve in a different runtime and domain.

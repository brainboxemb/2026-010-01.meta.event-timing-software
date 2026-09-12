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

Prefer preserving original source material rather than rewriting it. Project interpretations, questions, and possible software consequences belong in `docs/brainstorm.md` until they are deliberately promoted.

Do not use filenames or notes that identify the specific real-world event that motivated this project.

## Sources

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

# Event Timing Software

Engineering coordination repository for the public BrainboxEmb event-timing software
project. It owns project planning, software-system and software-item specifications,
interfaces, detailed design, development-environment guidance and verification
specifications for the Timing Point Application and related software.

Use this repository when you need to understand **what the software should do, how it is
designed, what work is active, or how that work is verified**. Java implementation lives
in the separate
[Timing Point Application repository](https://github.com/brainboxemb/2026-010-02.java.timing-point-application).

## Start here

- [Documentation overview](docs/README.md) — reading routes through the authored engineering documents.
- [Software Implementation Plan](docs/11-SIP-software-implementation-plan.md) — current implementation sequence and active work.
- [Engineering portal](https://brainboxemb.github.io/2026-010-01.meta.event-timing-software/) — generated searchable view with architecture and traceability.
- [Architecture/specification book](https://github.com/brainboxemb/2026-010-01.meta.event-timing-software/blob/prod/docs/documents/architecture-book.md) — generated review view from merged source.
- [AGENTS.md](AGENTS.md) — repository-specific working guidance for agents.
- [CHANGELOG.md](CHANGELOG.md) — chronological repository changes.

## Typical use

To understand one SI-01 behaviour, start in the
[system use cases](docs/30-UC-system-use-cases.md), follow the allocated requirement and
interface links into the
[SI-01 specification](docs/41-01-SSD-timing-application-specification-document.md) and
focused design, then use the
[verification test specification](docs/61-01-VTS-timing-application-verification-test-specification.md)
to see how that behaviour is checked.

For current planning rather than product semantics, use the SIP instead.

## Source and generated documentation

Authored Markdown on the normal source branch is authoritative. CI publishes review/output
documentation separately:

- merged/default branch: [prod/docs](https://github.com/brainboxemb/2026-010-01.meta.event-timing-software/tree/prod/docs);
- active pull requests: dev/pr-N/docs.

Generated output is for review and navigation and is not hand-edited.

## Public scope

This repository contains public engineering material only. Proprietary protocols,
production identities, credentials, secrets and private mappings stay outside the public
source tree and are referenced only through safe public boundaries where required.

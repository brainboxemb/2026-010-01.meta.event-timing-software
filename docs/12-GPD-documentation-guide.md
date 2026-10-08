# Documentation Guide (GPD)

Status: working project guidance

## Purpose

This guide defines how project documents are named, structured and related. It is
supporting engineering guidance, not a product specification and not part of the
software architecture baseline.

Use this guide when creating a new project document or when changing a document-family
convention. Do not invent a new introductory structure or new generic wording for an
existing family when a template already exists.

## Terms and abbreviations

| Abbreviation | Full name | Primary role |
| --- | --- | --- |
| GPD | General Purpose Document | project/support guidance that does not fit a more specific document family |
| SDP | Software Development Plan | project-wide development strategy |
| SIP | Software Implementation Plan | implementation steps, roadmap and exit evidence |
| EXT | External Inputs | register of parent/external sources that constrain this software system |
| UC | Use Case | externally meaningful behaviour and goals |
| SSSD | Software System Specification Document | software-system requirements and architecture |
| ISD | Interface Specification Document | system-owned interface requirements and semantics |
| IDD | Interface Design Description | optional concrete design/representation of an ISD |
| SRD | Software Requirements Document | software-item requirements when split from architecture |
| SSD | Software Specification Document | software-item requirements and architecture combined |
| SAD | Software Architecture Document | software-item architecture when split from requirements |
| SDD | Software Design Description | focused detailed software-item design |
| SDE | Software Development Environment | repositories, tooling, build and development environment |
| SVP | Software Verification Plan | verification strategy, levels, environments and evidence rules |
| VTS | Verification Test Specification | stable verification cases and expected results |
| SUM | Software User Manual | technical user/release guidance |

## Creating a new document

Reusable templates live in `docs/templates/`. A new document in an existing family
starts from the matching template rather than from an empty file.

The normal introductory order is:

```text
Purpose
Terms and abbreviations
Relationship to other documents
<document-family content>
```

The template contains reusable explanatory text that belongs to the document family.
Keep that text when it remains true. Replace the marked placeholders with the
document-specific names, identifiers and relationships.

A template is a starting point, not a requirement to keep empty sections. Omit a
section when it adds no reader value and add a document-specific section when the
subject needs it. Do not, however, rewrite generic family explanation differently in
each new document.

Do not repeat the same relationship in several places. If an ISD explains near the top
that an IDD owns the concrete representation, a later generic `Interface design`
section should not repeat the same statement.

Important abbreviations belong under **Terms and abbreviations**, directly after
**Purpose**. Include only terms that materially help a reader of that document.

Available templates are listed in `docs/templates/README.md`.

## Document categories and numbering

The numeric prefix groups documents by engineering role. It helps navigation but does
not by itself define dependency order.

```text
00–09  working / project context
10–19  project planning / guidance
20–29  external / parent-system inputs
30–39  software-system specification and design
40      software-item use cases
41      software-item requirements / combined specification
42      software-item architecture
43      software-item detailed design
44      software-item supportive design / implementation guidance
50–59  development environment / engineering
60–69  verification and validation
70–79  user / operational documentation
```

Current examples are:

```text
00-brainstorm
02-agent-plan
03-domain-baseline

10-SDP
11-SIP
12-GPD-documentation-guide

20-EXT-external-system-inputs

30-UC-system-use-cases
31-SSSD-software-system-specification-document
32-03-ISD-application-control-status
32-04-ISD-web-interface
32-05-ISD-timingdata-interchange
32-11-ISD-application-configuration
33-03-IDD-api-http-websocket
33-05-IDD-timingdata-interchange

40-01-UC                         reserved / optional for SI-01
41-01-SSD-timing-application-specification-document
41-02-SSD-gui-application-specification-document

43-01-SDD-01-data-and-display-design
43-01-SDD-02-java-component-design
43-01-SDD-03-backoffice-transport-design
44-01-GPD-java-design-rules

50-SDE-01-software-development-environment
50-SDE-02-java-build-test-toolchain
50-SDE-03-engineering-client
50-SDE-04-runtime-characterization

60-SVP
61-01-VTS-timing-application-verification-test-specification

70-01-SUM-headless-timing-application
```

Numbering rules:

- the leading number identifies the document category or reserved family;
- where a family has a natural stable scope identifier, that scope is the next segment;
- software-item families use the software-item ID, for example `41-01-SSD` and
  `43-01-SDD-02`;
- family `32` is reserved for system-owned ISDs and uses the stable interface ID,
  for example IF-03 becomes `32-03-ISD`;
- family `33` is reserved for optional IDDs and uses the same interface ID as its
  ISD, for example `33-05-IDD`;
- family `40` is reserved for optional software-item use cases;
- family `41` contains a combined SSD or an SRD when requirements are split from
  architecture;
- family `42` contains a separate SAD only when architecture is split from the SRD;
- family `43` contains focused SDDs; a final sequence distinguishes multiple SDDs
  for the same software item;
- family `44` contains software-item-scoped supportive design/implementation guidance
  that is intentionally non-normative, using the software-item ID such as `44-01-GPD`;
- repeatable generic families without a natural scope identifier put a sequence after
  the type, for example `50-SDE-01`;
- singular generic documents do not receive a synthetic sequence only for symmetry;
- family `61` contains software-item VTS documents and uses the software-item ID;
- range 70–79 uses the stable software-item segment where applicable;
- externally owned documents keep the identifier/version assigned by their owner and
  are registered through document 20 instead of being locally renumbered.

A new document should fit an existing specific family before a new family is invented. Use GPD only for genuine project/support guidance that does not fit a more specific established document type; do not use it to avoid choosing the correct engineering document family.

## Relationship between document families

The normal internal product-document direction is:

```text
domain baseline / system use cases / applicable external inputs
                         |
                         v
                        SSSD
                         |
              allocates items/interfaces
                         |
              +----------+----------+
              |                     |
              v                     v
        system-owned ISD      optional item UC
              |
        optional IDD
              |
              +----------+----------+
                         |
                         v
                   SRD/SSD + SAD
                         |
                         v
                    focused SDD
                         |
                         v
                  implementation
                         |
                         v
                    VTS / tests
                         |
                         v
              verification evidence
```

This is a normal decomposition path, not a rule that every input must pass through every
box. An externally imposed requirement, interface design, protocol or standard may
directly constrain the SSSD or an affected software-item specification when its
allocation is already explicit.

The families have these normal roles:

- **GPD** records project/support guidance when no more specific established document type fits. It is not part of the product-definition chain. A software-item-scoped GPD in family `44` may derive reusable implementation/review guidance from architecture and detailed design, but does not override those authorities.
- **SSSD** owns software-system requirements, software-item allocation, system-owned
  interface allocation and cross-item architecture.
- **ISD** owns the semantic contract of one system-owned interface.
- **IDD** optionally owns the concrete protocol, encoding or representation of an ISD;
  it does not replace the ISD semantics.
- **software-item UC** is optional and is used only when item-specific actor/goal
  behaviour makes the later specification clearer.
- **SSD** combines one software item's requirements and architecture.
- **SRD/SAD** are the split alternative to a combined SSD.
- **SDD** refines a focused part of the software-item design.
- **SVP** defines verification strategy.
- **VTS** defines stable verification cases and expected results.
- **SDE** defines the engineering environment and tooling, not product behaviour.
- **SIP** plans implementation sequence, not product behaviour.

### Current-state authority versus project history

Current-state specification and design books describe the engineering state that is
authoritative **now**. They are not implementation diaries.

Use these placement rules:

- SDP/SIP/agent planning may describe sequence, milestones, deferred work and closure
  history because planning is their purpose;
- UC/SSSD/SSD/ISD/IDD documents describe current externally meaningful behaviour,
  requirements, interface semantics and concrete representation;
- SDD documents describe the current detailed design and its rationale;
- SDE documents describe the current engineering environment/support tooling;
- SVP/VTS describe current verification strategy and stable cases, not run history;
- issues, pull requests, CHANGELOG entries and retained/generated evidence preserve
  implementation chronology and run-specific history.

A current-state book may mention a previous/released state only when that history itself
is part of the engineering contract, for example compatibility behaviour, an immutable
released-user matrix or an explicitly obsolete requirement whose identifier/history must
remain traceable.

Avoid headings and prose such as `first implementation`, `Step-4 implementation`,
`historical baseline` or `the next step will...` inside current-state books when the
same information is merely project history. Rewrite the passage as current design/
semantics, move planning to SIP, or rely on repository history instead of retaining a
parallel narrative.

Do not create a separate logbook only to rescue obsolete prose from a current-state book.
Create one only when a distinct reader/use case needs a curated chronological record.
- **SUM** provides user/release guidance for a software baseline.

## External and parent-system inputs

This software system can be constrained by requirements, interface contracts, protocols
or standards owned outside the current software-system scope.

`20-EXT-external-system-inputs.md` records those sources and the revision/baseline that
applies. The external source remains the authority. The register must not silently copy,
weaken or reinterpret an externally controlled contract.

Private or proprietary source material may remain outside this public repository while
its applicable identity and revision are recorded generically when that can be done
safely.

## Engineering traceability — model review

The engineering graph should explain how an operational goal is specified, designed,
implemented and verified. Each direct link is a meaningful engineering claim, not
just a navigation shortcut. The incoming and outgoing views show direction; the
link type explains the claim. Sphinx-Needs generates the reverse view from one
authored link.

**Status:** the vocabulary below is the proposed direction for review, not an
active migration. The current Sphinx-Needs configuration still uses
`derived_from`, `satisfies`, `detailed_by` and `verifies`. Do not use the proposed
new link names in authored Needs until they are configured and the existing
relationships have been reviewed.

### Reference review — useblocks/SPLed

[SPLed](https://github.com/useblocks/SPLed) is a small software-product-line
demonstrator that uses Sphinx-Needs across requirements, architecture, component
design, source code and tests. Reviewed revision:
[`e79a759d`](https://github.com/useblocks/SPLed/tree/e79a759d54a8d00f04e234af0f7b148de53dd222).

- Its [`ubproject.toml`](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/ubproject.toml)
  configures `realizes`, `fulfills`, `refines`, `implements`, `results`,
  `verifies` and `tests`, each with outgoing and incoming labels. It does not
  configure `derived_from` or `specifies`.
- The [software architecture](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/doc/software_architecture/index.md)
  uses `SWARCH_001 :realizes:` to connect architecture to 18 requirements.
  Component [detailed designs](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/components/light_controller/doc/index.md)
  contain `spec` Needs using `:refines: SWARCH_001`.
- [C source](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/components/light_controller/src/light_controller.c)
  contains `// @need` implementation annotations referring to design and
  requirement IDs. [C++ tests](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/components/light_controller/test/test_light_controller.cc)
  declare `:tests:` links to specific design Needs. Its
  [traceability table](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/doc/results/index.md)
  uses `needtable` to display requirement implementation/test backlinks.
- There is also a scaling problem: in six inspected component design files,
  **48** `spec` Needs all point to the same broad `SWARCH_001` node. Typed
  links alone do not prevent a hub or a spiderweb if the linked architecture
  objects are too broad.

**Lesson for this project:** retain meaningful relation types and the ability to
trace into actual code/tests, but use focused existing architecture/design objects
instead of linking every detailed element to one general architecture node.
Do not copy SPLed's link vocabulary or code-annotation mechanism without a
specific need and a working Java implementation path.

### Proposed relationship model

Prefer a small set of active verbs, consistently directed from the more concrete
object to the object whose obligation or design it addresses:

| Source object | Target object | Candidate link | Meaning |
| --- | --- | --- | --- |
| Requirement in SSSD, ISD or SSD | System/software-item use case | `specifies` | States a requirement for that use-case behaviour. |
| Architecture element | Requirement | `realizes` | Design responsibility meets the requirement. |
| Focused SDD/IDD design object | Architecture/interface design authority | `elaborates` | Adds implementation-level design detail. |
| Identified source implementation | Design or requirement it implements | `implements` | Concrete code is responsible for the specified behaviour. |
| Verification case | Requirement or behaviour actually checked | `verifies` | Verification coverage supported by a real case/evidence. |

These names are **candidates**, not approved new Sphinx-Needs link types.
SPLed's `refines` is a viable alternative to `elaborates` for design detail;
use `refines` for requirement-to-requirement refinement only if that separate
meaning is needed and unambiguous. `tests` may be valuable for source-level
unit tests, distinct from formal `verifies`, once the test objects are
represented in the graph. Do not introduce either merely for naming symmetry.

The document-family flow (UC, SSSD, ISD/IDD, SSD, SDD, implementation, VTS) is
**not** a mandatory one-object-per-level chain. An interface requirement can
directly constrain a software item, and one design can address several valid
requirements. Link the closest meaningful objects; add a cross-level direct
link when it states a separate, useful obligation, not just because both
objects belong to the same feature.

For example, a future `SI02-REQ-002 :specifies: UC-001` would mean that the
client endpoint/connection-state requirement specifies part of the connection
use case. It would appear outgoing from the requirement and incoming at UC-001.
A related design does not also need a direct UC-001 link if it is already
traceable through that requirement.

### How to avoid redundant links

1. For every direct edge, ask: what claim does this particular link make?
   If the answer is merely “related to the same feature”, use a Markdown
   reference or follow the existing graph path instead.
2. Keep direct links where the source really specifies, realizes, elaborates,
   implements or verifies the target. Do not add every transitive connection
   as another direct link.
3. Maintain enough granularity: a single broad architecture Need receiving
   links from many unrelated designs hides useful ownership. Conversely, do
   not create empty Needs or a Need per Java class just to increase coverage.
4. Do not infer that source code is implemented or a requirement is verified
   from a design description alone. Implementation anchors and test evidence
   must be real and separately inspectable.
5. In the Engineering Portal show readable, directional link labels, and
   allow navigation across multiple hops. Incoming/outgoing alone do not
   communicate the engineering meaning.

**Initial review case:** UC-001, “Connect to a registration system”, currently
has 18 incoming `derived_from` links. Audit these by actual meaning: direct
use-case specification, a narrower requirement refinement, a cross-cutting
constraint, an indirect dependency or an incorrect link. Review IF-03, IF-04,
SI-01 and SI-02 requirements together. Keep genuine direct links even when
there are many; remove or redirect redundant links only after confirming that
no valid trace path is lost. A link count is a diagnostic, not a limit.

The current [SSD-to-SDD design traceability](#ssd-to-sdd-design-traceability)
rule below remains in force until a separate link-model migration is agreed,
configured, validated in the graph and reviewed in generated documentation.

## SSD-to-SDD design traceability

Architecture elements defined in an SSD use the Sphinx-Needs `arch` type. When an
architecture element has substantive Java or implementation design elaboration in an
SDD, the SSD object may declare `detailed_by` to one or more focused SDD
`design` objects.

The relationship is directional:

```text
SSD architecture element
        |
        | detailed_by
        v
focused SDD detailed-design object
```

The SSD remains the architecture authority. The SDD `design` object elaborates how one
focused design responsibility is realised; it must not duplicate or silently redefine the
SSD architecture. One SDD design object may detail several related SSD architecture
objects where they are explained together. Do not create one design object per Java class
only to manufacture traceability.

Use ordinary Markdown links for incidental references. Use `detailed_by` when the
relationship belongs in the engineering graph and should therefore be visible in the
Object Explorer with its inverse relation.

A `design` Need owns the **substantive detailed-design content** for that object.
Do not use a two-line Need merely as a traceability anchor and then place the actual
design prose, examples or code immediately outside the directive. Keeping the detail
inside the Need makes the same authoritative content available to Sphinx-Needs, the
normalized engineering graph, generated reader Markdown and the Engineering Portal.

Keep one coherent design responsibility per Need. Cross-cutting document guidance may
remain ordinary Markdown, and unresolved/open design decisions stay outside accepted
design objects until they become real design authority.

## Requirement maturity

Software and interface requirements use the standard Sphinx-Needs `status` field:

| Status | Meaning |
| --- | --- |
| `D` | Draft — still being developed; wording, scope or existence may change |
| `R` | Review — proposed requirement is ready for focused review |
| `A` | Approved — accepted normative requirement for the current engineering baseline |
| `O` | Obsolete — no longer active; retained where its ID/history is needed |

A requirement written with `shall` is normative at its stated maturity. A draft
requirement is therefore not automatically accepted or frozen.

Move a requirement back to `D` when review causes a material change in meaning or
scope. Use `O` rather than reusing an approved requirement ID for a different meaning.

Every software and interface requirement carries an explicit status.

## Release references

When documents are released independently, a released document identifies the exact
revision/version of the documents and external sources that constrain it.

While this repository releases the local document set together, the repository
release/tag/commit may identify that coherent local baseline. The relationship between
documents should still remain clear enough that independent release remains possible
later.

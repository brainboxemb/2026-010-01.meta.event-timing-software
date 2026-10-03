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

50-SDE-01-software-development-environment
50-SDE-02-java-build-test-toolchain
50-SDE-03-engineering-client

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

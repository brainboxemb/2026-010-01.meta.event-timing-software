# Engineering Traceability (GPD)

## Purpose

This document explains the project's engineering traceability model, how
Sphinx-Needs stores its relationships, and how the generated Engineering Portal
uses them. It provides the technical reasoning behind the short authoring
instructions in [12-GPD — Documentation Guide](12-GPD-documentation-guide.md).

Traceability connects operational behaviour, requirements, architecture,
detailed design, implementation and verification. It does not replace the
specification, design or verification documents.

## Terms and abbreviations

- **Need** — a Sphinx-Needs object with a stable ID and a defined engineering role.
- **Relation** — a directed link from a source Need to a target Need.
- **Backlink** — the reverse view of the same directed relation.
- **UC** — Use Case; externally meaningful actor goal and behaviour.
- **SSSD / ISD / SSD** — system, interface and software-item specifications.
- **IDD / SDD** — concrete interface design and detailed software design.
- **VTS** — Verification Test Specification.

## Relationship to other documents

[12-GPD — Documentation Guide](12-GPD-documentation-guide.md) owns document
families, templates and the concise instructions for entering valid links in
Markdown. This document owns the technical traceability model and the meaning
of engineering links. Neither document replaces requirement or architecture
authority in the SSSD, ISDs, SSDs, IDDs, SDDs or VTS.

The external [reverse-engineered SPLed documentation guide](../reference/spled-traceability-analysis.md)
explains when each configured SPLed relation is used, with links to authored
source and generated test-result machinery. It is a reference, not an
authority over this project's design.

## Model and relationship direction

A link is a specific engineering claim, not a general indication that two
objects are related. In the Sphinx-Needs representation the source is the Need
containing the link option; the target is the referenced ID. Sphinx-Needs
generates an incoming backlink on the target automatically.

The model distinguishes these meanings:

| Source | Target | Semantic relation | Question answered |
| --- | --- | --- | --- |
| Requirement | Use case | `specifies` | Which requirements specify this use-case behaviour? |
| More specific requirement | Parent requirement | `refines` | Which requirement refines the parent obligation? |
| Architecture element | Requirement | `realizes` | Which architecture responsibility meets this requirement? |
| Detailed-design object | Architecture / interface design object | `elaborates` | Which detailed design explains this responsibility? |
| Identified implementation element | Design / requirement | `implements` | Which source code implements the design or contract? |
| Verification case | Requirement or behaviour checked | `verifies` | Which test case verifies the stated obligation? |

These verbs describe **semantic relationships**, not a list of configured
Sphinx-Needs option names. The configuration table below is the reference
for valid authoring syntax. In particular, the existing `detailed_by`
relationship points from architecture to design, whereas `elaborates` points
from design to architecture: changing that encoding requires an intentional
graph migration, not just a vocabulary substitution.

A document-family decomposition is not a mandatory chain of objects. An
interface requirement may constrain multiple software items; one design may
address multiple requirements. Use a cross-level direct link when it carries
an independent meaningful claim. Do not duplicate an indirect path merely to
make everything directly clickable from a use case.

## Sphinx-Needs representation

The [Sphinx-Needs configuration](_sphinx-needs/conf.py) defines the actual
Need types and `needs_links`. The configured relationship options are:

| Option in a Need | Outgoing meaning | Incoming meaning |
| --- | --- | --- |
| `:derived_from:` | derived from | is source for |
| `:satisfies:` | satisfies | satisfied by |
| `:detailed_by:` | detailed by | details |
| `:verifies:` | verifies | verified by |

An option value lists **target IDs**; the reader must not write a second,
reverse relation merely to obtain an incoming entry. The `incoming` and
`outgoing` strings configure the human-readable labels of each link type;
they do not change the stored direction.

The current Need types are `uc`, `req`, `ifreq`, `arch`, `design`
and `vc`. A `design` Need should contain the actual design prose, examples
and any supporting code that define its responsibility, rather than acting
as an empty link anchor. Keep each design Need focused on a coherent design
responsibility, not necessarily one Java class. A focused design may explain
several closely related architecture objects.

The authored Markdown remains the engineering source. The documentation
build exports Sphinx-Needs objects and relations into the normalized
engineering graph; the [Engineering Portal generator](../tools/generate_engineering_portal.py)
presents incoming/outgoing relations and linked object pages. The portal's
current relationship table renders stored relation keys. This is a
presentation choice; the directional labels are configured in Sphinx-Needs.

Graph coverage is validated against the stable IDs and authored objects
described in the [engineering graph coverage contract](_data/engineering-graph-coverage.md).
The graph cannot prove that Java code implements a design merely because
a design Need mentions a class, nor can an unexecuted test establish
verification evidence. Implementation and test links need identifiable
source/evidence anchors before they can be treated as proof.

## Link quality and graph granularity

The link's meaning must be understandable without reading its entire
surrounding document. Use an ordinary Markdown link for incidental references.
Prefer a trace through meaningful intermediate objects over adding
transitive shortcuts to the graph.

Architecture objects should represent focused responsibilities. A single
broad hub linked to unrelated requirements and detailed designs obscures
allocation and impact analysis, even when every edge has a meaningful label.
Do not counter this by creating a Need per Java class or artificial,
content-free Needs.

For example, a requirement such as `IF03-REQ-004` can refer to `UC-001`
as its direct source. A design that addresses the status interface is
traceable through its architecture/interface and requirement links; it does
not need an additional direct link to `UC-001` unless that link expresses
a distinct claim.

Use the [SPLed documentation guide](../reference/spled-traceability-analysis.md)
for a concrete example of both end-to-end source/test traceability and the
problems created by an overly broad central architecture object.

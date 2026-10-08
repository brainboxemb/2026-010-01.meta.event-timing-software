# Engineering Traceability (GPD)

## Purpose

This guide defines the traceability model for the Event Timing Software
project. Traceability records engineering claims between actual, identified
objects: user goals, normative requirements, architecture, detailed design,
implementation and verification. It is not a list of links added for
convenient navigation.

The [Documentation Guide](12-GPD-documentation-guide.md) explains how
to enter these links in Need headers and how the document families relate.

## Terms and abbreviations

- **Need** — an identified Sphinx-Needs object, such as `uc`,
  `req`, `ifreq`, `arch`, `design`, `impl` or `vc`.
- **UC** — Use Case: externally meaningful actor goal and behaviour.
- **SSSD / ISD / SSD** — system, interface and software-item specifications.
- **IDD / SDD** — interface and detailed software design.
- **VTS** — Verification Test Specification.
- **Backlink** — automatically computed incoming view of an outgoing link.

## Relationship to other documents

The SSSD, ISDs, SSDs, IDDs, SDDs and VTS own the actual requirements,
design and verification cases. This guide defines only their link semantics.
The external [SPLed traceability reference](../reference/spled-traceability-analysis.md)
is supporting research, not an authority over this project's conventions.

## Relations and motivation

A relation is directed from the **source Need declaring the header option**
to the **target Need identified by its value**.

| Source | Target | Relation | Engineering meaning |
| --- | --- | --- | --- |
| Requirement | Use case | `specifies` | States the observable obligations supporting an actor goal. |
| Specific requirement | Parent requirement | `refines` | Adds detail to an existing normative requirement. |
| Requirement | Related requirement | `depends_on` | Uses or is constrained by another requirement's interface or capability. |
| Architecture | Requirement | `realizes` | Allocates design responsibility for the requirement. |
| Detailed design | Architecture | `elaborates` | Explains an architectural responsibility in greater detail. |
| Identified implementation | Detailed design | `implements` | Maps real source code to the design it implements. |
| Identified implementation | Requirement | `fulfills` | Direct code-to-contract claim, useful only with an inspectable implementation anchor. |
| Verification case | Requirement | `verifies` | States what a defined verification procedure checks, not its run result. |

These names deliberately keep different claims separate:

- **`specifies`, not `refines`, for requirement → UC.**
  A use case expresses an operational goal, not a parent requirement.
  The requirement specifies behaviour needed to meet that goal.
- **`realizes`, not `fulfills`, for architecture → requirement.**
  Architecture identifies a solution responsibility; it does not
  establish that working, verified code satisfies the requirement.
- **`elaborates`, not `realizes`, for design → architecture.**
  A detailed design explains a portion of the architecture rather
  than replacing the authority of the SSD or IDD.
- **`implements` and `fulfills` have different targets.**
  A source-code object may implement a design and also fulfill a
  requirement, but neither a second direct link nor coverage is
  implied automatically.
- **`refines` and `depends_on` are different.**
  A consumer's requirement may depend on the defined IF-03 contract
  without being a more specific version of that interface requirement.
  Dependencies are not refinements.

A representative trace has the following authored directions:

```text
DD-TimingNodeExecution --elaborates--> TimingNode
TimingNode --realizes--> SI01-REQ-020
SI01-REQ-020 --specifies--> UC-001
```

The chain can be followed from either end using generated backlinks.
An interface requirement can also constrain a software item directly;
a design can elaborate several related architecture elements. There
is no mandatory Need at every document family level.

## Sphinx-Needs and Engineering Portal

The [Sphinx-Needs configuration](_sphinx-needs/conf.py) defines
Need types and relation labels. The labels below are the configured
readable descriptions of one stored relation:

| Link | Outgoing | Incoming |
| --- | --- | --- |
| `specifies` | specifies | specified by |
| `refines` | refines | refined by |
| `depends_on` | depends on | required by |
| `realizes` | realizes | realized by |
| `elaborates` | elaborates | elaborated by |
| `implements` | implements | implemented by |
| `fulfills` | fulfills | fulfilled by |
| `verifies` | verifies | verified by |

The generated Engineering Portal displays incoming relations by the **role of
the related object** (for example, *Requirements* for a use case and *Detailed
designs* for an architecture element). This avoids treating the automatically
generated reverse verb as a sentence that readers must interpret. Outgoing
relations retain their active verb. Long groups of six or more links use
collapsible sections labelled with the identity of each **authored source
document**; this is a presentation choice and neither restricts the number of
valid links nor alters the engineering graph.

The author declares only the outgoing `:relation: target-id` option;
Sphinx-Needs supplies `relation_back`. The
[Sphinx-Needs network schemas](_sphinx-needs/schemas.json) constrain
linked object types. The authored Markdown is exported as a normalized
engineering graph; the [reader renderer](../tools/render_needs_reader_markdown.py)
and [Engineering Portal](../tools/generate_engineering_portal.py) use
the same configured labels. Generated pages and reverse relations are
never hand-edited.

## Direct links, object scope and evidence

A direct link must make a specific, reviewable claim. Do not add an
A→C shortcut simply because A→B→C already expresses the trace.
Use ordinary Markdown links for incidental references. A high link
count invites a review of the *meaning* and granularity, not a
numerical cap.

An architecture Need should represent a meaningful responsibility,
not a single broad hub attached to otherwise unrelated designs.
An SDD `design` Need owns substantive design content: prose,
examples and relevant code should be **inside** its directive, not
outside an empty traceability anchor. One focused design Need may
elaborate several related SSD architecture Needs. Creating one Need
per Java class merely to raise coverage adds no value.

Code traceability requires stable, inspectable Java implementation
anchors; a class named in design prose is not proof of implementation.
A `vc` Need records the verification intent. Actual run results and
their evidence are separate and must not be inferred from a
`verifies` link. The
[engineering graph coverage contract](_data/engineering-graph-coverage.md)
defines which promoted engineering object IDs belong to the graph.

# SIP planning data

The files in this directory are the machine-readable source for generated SIP planning views.

The generated SVG, draw.io and PDF files are **outputs**. Do not edit planning content in generated drawings.

## Structure

```text
sip-roadmap.yaml
  programme/roadmap-level planning data

sip-steps/
  step-02.yaml
  step-03.yaml
  ...
  detailed activity-board data for individual SIP steps

schemas/
  sip-roadmap.schema.json
  sip-step-board.schema.json
  JSON Schemas used to validate the YAML planning source before rendering
```

## Source-format rule

Use **YAML for human-maintained semantic/planning data** and **JSON Schema for type/structure validation**.

The same convention is intended for later declarative architecture-diagram sources: content and relationships live in YAML, reusable types/styles are validated separately, and Python remains the renderer/layout engine.

## Separation of concerns

`docs/11-SIP-software-implementation-planning.md` remains the human-readable implementation plan and owns the meaning, deliverable and demonstration of each SIP step.

`sip-roadmap.yaml` owns working planning metadata such as estimates, cadence and compact named-document indicators used by the overview roadmap.

`sip-steps/step-NN.yaml` owns the concrete planning activities shown on an A4 portrait step board. Activities are typed by lane, kind and state; dependencies and optional effort are data rather than drawing geometry.

The Python generator parses YAML, validates it against JSON Schema, resolves layout and renders the generated outputs. Therefore changing a card position or page layout must not require changing the engineering activity itself.

## Activity model

A step-board activity has fields such as:

```yaml
- id: T05
  lane: tooling
  kind: implementation
  title: Linux canonical CI
  state: planned
  estimate_project_days: 0.5
  depends_on: [T03, T04]
```

Supported lanes, kinds, states and document-maturity values are defined by the JSON Schema rather than by ad-hoc generator code.

## Documentation indicators

Documentation indicators intentionally separate:

- `maturity` — how stable/authoritative the document is for the scope needed by this step;
- `completeness` — how much of the documentation needed by this step is currently covered.

Completeness is **not** a claim that the future product or entire document family is complete.

The overview roadmap shows named documents compactly. Concrete engineering activities belong on the per-step A4 board.

## Generated outputs

The overview generator creates the programme-level roadmap. Detailed step-board data creates matching browser and document outputs under:

```text
bld/docs/planning/steps/
  step-NN.svg
  step-NN.pdf
```

The SVG and PDF use the same step-board source, activity states, document indicators and A4 portrait layout. CI validates the YAML sources before publishing generated planning output.

## Future generic tooling

Once both the planning model and at least one declarative architecture-diagram proof have demonstrated value, the reusable schema/theme/rendering code is intended to move to a separate generic engineering-document tool repository, working name:

```text
tool.eng-docs
```

This project repository should continue to own project-specific planning and architecture content. The generic tool may understand concepts such as activities, lanes, documents, maturity, completeness, nodes, edges, themes and print/page layouts, but not timing-domain semantics.
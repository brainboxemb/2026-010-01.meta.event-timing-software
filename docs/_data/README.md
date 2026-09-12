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

`sip-roadmap.yaml` owns working planning metadata such as estimates, cadence and compact documentation indicators used by the overview roadmap.

`sip-steps/step-NN.yaml` owns the concrete planning activities shown on an A3 step board. Activities are typed by lane, kind and state; dependencies and optional effort are data rather than drawing geometry.

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

## Generated outputs

The overview generator creates the programme-level roadmap. Detailed step-board data creates outputs under:

```text
bld/docs/planning/steps/
```

CI validates the YAML sources before publishing generated planning output.
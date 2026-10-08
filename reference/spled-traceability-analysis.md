# SPLed documentation and traceability — reconstructed guide

## Purpose and source

This guide reconstructs **how the SPLed project actually authors and generates
engineering documentation**, and when each traceability link type is used. It is
a reading and authoring guide to the observed SPLed model, **not** an
instruction to adopt that model in Event Timing Software.

Sources: [useblocks/SPLed](https://github.com/useblocks/SPLed) at
[`e79a759d5`](https://github.com/useblocks/SPLed/tree/e79a759d54a8d00f04e234af0f7b148de53dd222) and
the [pinned spl-core](https://github.com/useblocks/spl-core/tree/ce62088e6d85116c1e93495971b687f5d03da77f)
used for report generation. These exact revisions distinguish what is present
in source from what is generated at build time.

The [Event Timing traceability model](../docs/13-GPD-engineering-traceability.md)
owns our project-specific conventions. SPLed is a worked external reference.

## 1. Where documentation comes from

| Source | Need/role | How it enters the documentation |
| --- | --- | --- |
| [Customer requirements](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/doc/customer_requirements/index.md) | `req` Needs for Disco, Sleep and Spa customers | Authored MyST Markdown, with variant-conditional sections. |
| [Software requirements](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/doc/sw_requirements/index.md) | Imported `spec` Needs such as `REQ_42` | `needimport` of external ReqIF and CSV-derived JSON. |
| [Software architecture](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/doc/software_architecture/index.md) | `arch` Need `SWARCH_001` | Authored MyST; links to imported requirements. |
| [Component detailed designs](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/components/light_controller/doc/index.md) | `spec` Needs such as `SWDD_LC-100` | Component-local Markdown; links to architecture. |
| [C implementation](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/components/light_controller/src/light_controller.c) | `impl` Needs such as `SWIMPL_LC-001` | Source comments parsed through `sphinx-codelinks`; exposed in `src-trace`. |
| [C++ tests](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/components/light_controller/test/test_light_controller.cc) | `test` Needs such as `TS_LC-001` | RST `.. test::` blocks in Doxygen-compatible comments; source documentation tooling exposes them. |
| [Build-generated JUnit results](https://github.com/useblocks/spl-core/blob/ce62088e6d85116c1e93495971b687f5d03da77f/src/spl_core/test_report/junit_to_needs.py) | `testfile`, `testsuite`, `testcase` Needs | Generated `needs.json` plus `needimport` and `needextend`; available for a reports build. |

SPLed has two documentation readers: Sphinx and ubCode/ubc. Both consume
the shared [`ubproject.toml`](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/ubproject.toml) Need model. Sphinx
loads it through `needs_from_toml` in [`conf.py`](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/conf.py).
The project keeps the shared [spl-core link definitions](https://github.com/useblocks/spl-core/blob/ce62088e6d85116c1e93495971b687f5d03da77f/src/spl_core/report_generation/ubproject.toml)
in its own TOML configuration and tests for drift.

The customer `req` Needs and imported `REQ_*` `spec` Needs are
**different sets**. A prefix beginning `REQ_` does not by itself imply
Need type `req`. The checked source does not establish a complete
customer-requirement-to-software-requirement trace for every customer goal.

## 2. The seven configured link types

**Direction rule:** `A :relation: B` defines a directed edge **A → B**.
The incoming label is the backlink visible on B. Both labels describe one
link, not two independently authored links.

| Link | Observed source → target | When / why SPLed uses it | Evidence |
| --- | --- | --- | --- |
| **`realizes`** | `arch` → software requirement (`spec`) | Assigns a requirement to an architecture element that realizes it. | `SWARCH_001 → REQ_42` in [software architecture](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/doc/software_architecture/index.md). |
| **`refines`** | Detailed-design `spec` → `arch` | Adds component-level detail to a higher-level architecture element. | `SWDD_LC-100 → SWARCH_001` in [Light Controller design](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/components/light_controller/doc/index.md). |
| **`implements`** | Source-code `impl` → detailed-design `spec` | Identifies code responsible for implementing one or more design objects. | `SWIMPL_LC-001 → SWDD_LC-100` in [source annotation](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/components/light_controller/src/light_controller.c). |
| **`fulfills`** | Source-code `impl` → software requirement (`spec`) | States which requirement a concrete implementation claims to fulfill, separately from the design it implements. | `SWIMPL_LC-001 → REQ_42` in the same [source annotation](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/components/light_controller/src/light_controller.c). |
| **`tests`** | Test specification `test` → detailed-design `spec` | Declares which design responsibilities a named test exercises. | `TS_LC-001 → SWDD_LC-100, SWDD_LC-102, SWDD_LC-300` in [Light Controller tests](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/components/light_controller/test/test_light_controller.cc). |
| **`results`** | Test specification `test` → generated `testcase` | Associates a declared test with the matching outcome of a JUnit run. The link is **generated**, not hand-authored in the test. | [Pinned spl-core converter](https://github.com/useblocks/spl-core/blob/ce62088e6d85116c1e93495971b687f5d03da77f/src/spl_core/test_report/junit_to_needs.py). |
| **`verifies`** | **No authored use identified** in inspected SPLed requirements, designs, implementation annotations or tests | The configured label suggests formal verification of an obligation, but this is not demonstrated by the checked project content. Do not infer its actual target type or enforce its use from the configuration alone. | [Declared in `ubproject.toml`](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/ubproject.toml); unlike `tests`, no worked `:verifies:` instance found. |

Exact human-readable labels, as declared in
[`ubproject.toml`](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/ubproject.toml):

| Link | Outgoing | Incoming |
| --- | --- | --- |
| `realizes` | realizes | is realized by |
| `fulfills` | fulfills | is fulfilled by |
| `refines` | refines | is refined by |
| `implements` | implements | is implemented by |
| `results` | results | results from |
| `verifies` | verifies | is verified by |
| `tests` | tests | is tested by |

**Configured does not mean used.** `verifies` is present as an available
field, but the inspected material uses `tests` for test-to-design
coverage. Conversely, `results` is an active workflow even though its
edges are produced during report generation.

## 3. A concrete trace — the Light Controller

The following IDs and link directions come from the checked sources.
Read each arrow literally as the option written in its source object.

```text
SWARCH_001 (arch)  ──realizes────> REQ_42 (spec)
     ▲                                   ▲
     │ refines                           │ fulfills
     │                                   │
SWDD_LC-100 (spec) <──implements── SWIMPL_LC-001 (impl)
     ▲
     │ tests
     │
TS_LC-001 (test) ────results────> generated JUnit testcase (reports build)
```

Here `REQ_42` is the imported
[“Light State Management” software requirement](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/doc/ubconnect/output/_0dd2794f-3901-4590-99d1-a554ded61130.json).
The [architecture Need](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/doc/software_architecture/index.md) lists it
in `:realizes:`; the [Light Controller design](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/components/light_controller/doc/index.md)
declares `:refines: SWARCH_001`.
The [implementation comment](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/components/light_controller/src/light_controller.c)
points both to the design (`implements`) and directly to that requirement
(`fulfills`). The [test](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/components/light_controller/test/test_light_controller.cc)
declares which design Needs it tests. The last `results` edge exists when
a matching JUnit testcase has been converted by the reports build.

This is **not** a claim that a passing testcase verifies every requirement
listed on the architecture Need. A link expresses intended coverage or
responsibility; evidence of a successful test run is a separate fact.

## 4. How to author each type of object in SPLed

### A. Architecture: `realizes`

[Source: `doc/software_architecture/index.md`](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/doc/software_architecture/index.md)

```markdown
```{arch} <Overall Software Component Architecture>
:id: SWARCH_001
:realizes: REQ_2, REQ_36, REQ_38, ...
...
```
```

This object owns an architectural view and a list of software requirements.
The real declaration contains **18** `:realizes:` targets. SPLed does
not use one Need per architectural component here.

### B. Detailed design: `refines`

[Source: `components/light_controller/doc/index.md`](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/components/light_controller/doc/index.md)

```text
```{spec} State Management
:id: SWDD_LC-100
:refines: SWARCH_001

The light can be in one of two states: ON or OFF.
```
```

This is a component-level specification that elaborates the broad architecture
Need. Other component documents use the same pattern, including design Needs
for runnables, inputs, outputs and state machines. `refines` is therefore
**design-to-architecture** in these examples, not requirement-to-requirement
refinement.

### C. Source implementation: `implements` and `fulfills`

[Source: `components/light_controller/src/light_controller.c`](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/components/light_controller/src/light_controller.c)

```c
// @need Light state, SWIMPL_LC-001, impl, [SWDD_LC-100], [REQ_42]
```

The positional syntax is documented in
[`AGENTS.md`](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/AGENTS.md):

```text
// @need <title>, <id>, impl, [<implements>], [<fulfills>]
```

The **fourth field** identifies detailed-design IDs; the **fifth**
identifies requirements fulfilled. Empty brackets mean no IDs in that
field. For example, `SWIMPL_LC-005` implements `SWDD_LC-204`
without a direct `fulfills` target.

SPLed enables `sphinx-codelinks` and uses:

```text
```{src-trace}
:project: components
:directory: light_controller
```
```

This exposes traced source objects on a component's documentation page.
The source must be represented by the build's actual compilation settings,
including relevant feature switches.

### D. Tests: `tests`

[Source: `components/light_controller/test/test_light_controller.cc`](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/components/light_controller/test/test_light_controller.cc)

```rst
.. test:: light_controller.test_light_on_and_off
   :id: TS_LC-001
   :tests: SWDD_LC-100, SWDD_LC-102, SWDD_LC-300
```

This declaration is embedded in a C++ documentation comment above the
GoogleTest implementation. It creates a **test specification** Need and
explicitly links that test to the design objects it covers. It does
not directly link to an implementation `impl` Need.

### E. Run evidence: `results`

The actual implementation is in the
[pinned `spl-core` JUnit converter](https://github.com/useblocks/spl-core/blob/ce62088e6d85116c1e93495971b687f5d03da77f/src/spl_core/test_report/junit_to_needs.py).
For a reports build, the converter:

1. Converts the JUnit XML into `testfile`, `testsuite` and `testcase`
   Needs in `unit_test_results.needs.json`.
2. Matches `.. test::` titles/IDs from generated source listings to JUnit
   testcase names.
3. Writes a generated `unit_test_results` page that imports the JSON
   and extends the matching test specification with `:+results:`.

The equivalent generated structure is:

```rst
.. needimport:: unit_test_results.needs.json

.. needextend:: TS_LC-001
   :+results: <matching generated testcase ID>
```

The `<...>` placeholder represents build-generated IDs and is
**not a verbatim committed file**. The concrete testcase identities
depend on the JUnit input. Result linking is thus available only when
a reports build supplies the generated data. A test specification can
still exist without a result.

### F. Formal verification: `verifies`

There is a `verifies` link definition, but no concrete authored
`:verifies:` example in the inspected source set. Unlike `tests`,
there is no established usage convention to reverse-engineer from
these files. Describing `verifies` as the implemented project
verification rule would overstate the evidence.

## 5. Imported needs and additional cases

The [ReqIF import](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/doc/ubconnect/input/import.toml) marks
its imported objects as `type = "spec"`, even when their IDs begin
with `REQ_`. The [CSV import](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/doc/ubconnect/csv/import.toml)
can populate an `implements` field as structured imported data.

The checked [CSV Needs JSON](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/doc/ubconnect/csv/needs.json)
contains `ARCH_CSV_1` of **type `spec`** with
`implements: [REQ_CSV_1, REQ_CSV_2, REQ_CSV_3]`. This is a
different source/target pairing from the primary C-code example.
It demonstrates that a link's **configured name does not enforce**
a source/target type constraint. Consumer modelling must provide
the semantic discipline.

The same CSV JSON also uses generic `links` for relationships
between CSV requirements. The CSV import setting
`links_column = "satisfies"` describes its input-column mapping;
it does **not** establish a custom Sphinx-Needs
`:satisfies:` type in SPLed.

The [traceability matrix](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/doc/results/index.md) filters
`type == 'req'` and shows `id`, `title`, `is tested by` and
`is implemented by`. Because much of the imported software
requirement set has type `spec`, the matrix's filter is **not**
a complete view of all software requirements. It should not be
interpreted as proof of full project coverage.

## 6. Why the trace graph changes by variant

[AGENTS.md](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/AGENTS.md) and
[`VARIANTS.md`](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/VARIANTS.md) describe the variant-aware
document selection. In brief:

- Component documents are included only if the selected variant
  contains the component.
- `{if} var.features.BLINKING` and related feature conditions
  gate the inclusion of blocks and their Need objects.
- A normal `docs` build does not import generated test-result
  pages; a `reports` build selects the matching generated source
  listings, test specifications, JUnit results and coverage.
- The selection is generated before rendering and shared between
  Sphinx and ubCode/ubc, so links that exist for one variant
  need not exist for another.

Therefore, absence of a link in one generated report may reflect
the variant or build target rather than a missing authored declaration.

## 7. Modelling observations

**Useful pattern.** SPLed distinguishes architecture allocation
(`realizes`), design decomposition (`refines`), a code-to-design
mapping (`implements`), a direct code-to-requirement claim
(`fulfills`), test-to-design coverage (`tests`) and
test-to-execution-result evidence (`results`).

**High-degree architecture node.** Six component design documents
contain **48** `:refines: SWARCH_001` relations in total:
Auto Off 13; Brightness Controller 7; Light Controller 10; Main
Control Knob 6; Power Button 7; Power Signal Processing 5.
All 48 target one broad architecture Need. A precise relation name
does not compensate for an excessively coarse target.

**Unproven complete coverage.** No complete chain from every
customer request to implementation and successful verification
is established by the inspected source. `verifies` is only
configured; `results` requires generated test-run data;
the imported `spec` type complicates the `req`-filtered matrix.

**Implication for Event Timing Software.** Prefer focused existing
architecture identities and meaningful direct relationships, not a
hub linked to all details. Decide our own link vocabulary and
authoring direction based on the roles of UC, SSSD, ISD, SSD,
IDD, SDD and VTS; code/test traceability needs actual Java-source
and verification anchors. See
[13-GPD — Engineering Traceability](../docs/13-GPD-engineering-traceability.md)
for the project's own model.

# SPLed — traceability reference analysis

## Source and scope

Repository: [useblocks/SPLed](https://github.com/useblocks/SPLed),
a software-product-line demonstrator for variants of an LED product.

Reviewed source revision: [`e79a759d5`](https://github.com/useblocks/SPLed/tree/e79a759d54a8d00f04e234af0f7b148de53dd222)
on the `develop` branch. The repository is illustrative external material,
not a dependency or an authority for the Event Timing Software project.
This analysis concerns its Sphinx-Needs model and examples, not its runtime
product architecture or quality as a whole.

## Relationship configuration

SPLed keeps its Needs types and relation configuration in
[`ubproject.toml`](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/ubproject.toml), which Sphinx-Needs
loads using `needs_from_toml` in
[`conf.py`](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/conf.py).

The configured custom link types are:

| Link type | Outgoing label | Incoming label |
| --- | --- | --- |
| `realizes` | realizes | is realized by |
| `fulfills` | fulfills | is fulfilled by |
| `refines` | refines | is refined by |
| `implements` | implements | is implemented by |
| `results` | results | results from |
| `verifies` | verifies | is verified by |
| `tests` | tests | is tested by |

It also declares `req`, `arch`, `spec`, `impl` and `test` Need
types. Neither `derived_from` nor `specifies` is configured.

## Observed traceability

**Architecture to requirements.** In
[software architecture](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/doc/software_architecture/index.md)
a single `SWARCH_001` `arch` Need declares `:realizes:`
to 18 requirement IDs.

**Detailed design to architecture.** Each component contains
`spec` Needs in its detailed-design document. For instance,
[`SWDD_LC-100`](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/components/light_controller/doc/index.md)
describes the Light Controller state and declares
`:refines: SWARCH_001`.

**Implementation in source code.** C source annotations are exposed through
Sphinx's `sphinx-codelinks` extension and a source-trace directive.
The [Light Controller code](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/components/light_controller/src/light_controller.c)
contains a line such as:

```c
// @need Light state, SWIMPL_LC-001, impl, [SWDD_LC-100], [REQ_42]
```

This identifies an implementation Need with design and requirement
references. It provides a concrete source-code anchor, although
a declared link alone does not prove functional correctness.

**Tests and traceability overview.** The
[Light Controller tests](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/components/light_controller/test/test_light_controller.cc)
declare `test` Needs with `:tests:` links to detailed-design IDs,
for example `TS_LC-001` tests `SWDD_LC-100`, `SWDD_LC-102` and
`SWDD_LC-300`. The
[requirements traceability matrix](https://github.com/useblocks/SPLed/blob/e79a759d54a8d00f04e234af0f7b148de53dd222/doc/results/index.md)
uses `needtable` with the columns `is tested by` and
`is implemented by`.

## Strengths and limitations for our use

Typed links express distinct engineering responsibilities. Including
implementation anchors and tests in the Needs graph permits navigation
beyond specification and design. The model is also compatible with
variant-aware documentation.

The biggest granularity limitation in the inspected example is that
six component designs collectively contain **48** `:refines: SWARCH_001`
links: 13 Auto Off, 7 Brightness Controller, 10 Light Controller,
6 Main Control Knob, 7 Power Button and 5 Power Signal Processing.
Every one points to the same top-level architecture Need. This
creates a high-degree hub even though the link type is meaningful.

The imported external/CSV requirements and build-specific test reports
also mean not every link in the example is authored directly beside
its related Need. The presence of a link should be distinguished from
evidence of implementation and test success.

## Relevance to Event Timing Software

Use SPLed as evidence that meaningful relations can span requirements,
architecture, detailed design, source code and test definitions. Do
not reuse a single broad architecture object as the target of every
SDD design. Retain our focused component identities and add links only
where the source and target have a direct, reviewable relationship.

The project-specific model and implementation are defined in
[13-GPD — Engineering Traceability](../docs/13-GPD-engineering-traceability.md).

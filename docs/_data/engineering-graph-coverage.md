# Engineering graph coverage contract

Migration 013 uses the engineering graph for **stable, explicitly identified engineering objects**. It does not turn every documentation section or paragraph into a Need.

The project coverage rule is source-driven rather than a fixed canary count. CI discovers the current expected object set from the authored repository and requires Sphinx-Needs and the normalized graph to contain exactly that set.

## In scope

CI treats these as graph-owned engineering objects:

- every native `uc`, `req`, `ifreq`, `arch` or `vc` Need with an explicit `:id:`;
- every still-unmigrated formal `UC-NNN — ...` heading, so a newly added legacy-style use case cannot silently escape the graph;
- every still-unmigrated formal `*-REQ-NNN — ...` requirement definition, for the same reason;
- every formal `VC-* — ...` verification-case definition;
- every diagram node carrying `object_id`; that identity must resolve to the same engineering object and the normalized graph must retain a diagram reference;
- every semantic diagram node using `notation: class`, `component` or `packaging-component` must carry an `object_id`. Explanatory/layout-only nodes without semantic notation may remain non-clickable.

This makes migration completeness an invariant: adding a new stable engineering ID without putting it in the production authoring model makes documentation CI fail.

## Narrative by design

Documents and sections without a promoted stable engineering ID remain ordinary Markdown/MyST narrative. In the current baseline that intentionally includes:

- the SSSD system-level requirement/architecture prose where no `SYS-REQ-*` set has yet been promoted;
- IF-11 configuration-contract prose, which currently allocates existing SI-01 requirements but has no promoted `IF11-REQ-*` set;
- the SI-02 SSD working architecture, which explicitly states that no stable SI-02 requirement set has yet been promoted;
- focused SDD design prose and candidate requirements such as `CAND-*`;
- SVP verification profiles `ST-1` through `ST-4`, which are reusable profiles rather than verification-case IDs;
- planning, SDE, SUM and ordinary explanatory material.

If one of those areas promotes a stable requirement, architecture or verification identifier later, it becomes graph-owned at that point rather than being kept outside the graph for document-family reasons.

## Current migration baseline

At the full-project Migration-013 cut-over the existing stable set consists of:

- 19 system use cases (`UC-001` through `UC-019`);
- 13 Headless Timing Application requirements (`SI01-REQ-*`);
- 10 IF-03 requirements (`IF03-REQ-*`);
- the existing formal verification case `VC-ST1-001`;
- all semantic class/component/packaging-component identities shown in Figure SI01-01. The current figure has 27 such top-level architecture nodes; annotation/layout-only nodes remain outside the engineering graph.

The exact total is deliberately **not** hard-coded here or in CI. The validator derives it from current source so later promoted engineering objects cannot leave the project in another bounded-canary state.

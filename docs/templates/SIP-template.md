# Software Implementation Plan (SIP)

Status: working draft / non-authoritative

## Purpose

This document explains how the software is expected to grow from the current baseline
into the intended system. It owns implementation sequence, step scope, activities,
estimates and exit criteria.

The SIP plans work. It does not define product requirements, interface semantics or
detailed design merely because those items appear in a roadmap step.

## Terms and abbreviations

- **SIP** — Software Implementation Plan
- **D..** — documentation/design activity
- **A..** — application/product implementation activity
- **V..** — verification activity
- **T..** — tooling/engineering-environment activity

## Relationship to other documents

The SDP defines the project-wide development direction. Product specifications and
design documents define the accepted behaviour and design baseline that implementation
work must realise.

SDE documents define the engineering environment. SVP/VTS documents define verification
strategy and stable verification cases. Issues, pull requests and retained/generated
evidence record execution of the plan.

## How to read a step

Each step should use the same small structure:

- **Purpose** — why the step exists here;
- **Goal** — capability added by the step;
- **Scope** — work that belongs in the step;
- **Not in this step** — useful boundary where scope could otherwise grow;
- **Needs** — real dependencies/resources that can block the step;
- **Activities** — stable step-local activity IDs and titles;
- **Result** — short outcome;
- **Demo** — practical end demonstration;
- **Done** — engineering exit criterion.

## Roadmap

### Step <N> — <name>

**Purpose**

<why this step exists>

**Goal**

<capability added>

**Scope**

<included work>

**Not in this step**

<explicit exclusions where useful>

**Needs**

<dependencies/resources>

**Activities**

| ID | Activity |
| --- | --- |
| D01 | <documentation/design activity> |
| A01 | <application activity> |
| V01 | <verification activity> |

**Result**

<short outcome>

**Demo**

<practical demonstration>

**Done**

<exit criteria>

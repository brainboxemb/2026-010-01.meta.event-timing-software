# <Software item name> Verification Test Specification (VTS)

Status: working / review baseline

Software item: **SI-<ID> — <Software item name>**

## Purpose

This document specifies the stable verification cases used to test **SI-<ID>**.

It is downstream from product requirements and interface contracts and does not create
product behaviour. Current PASS/FAIL execution status is not maintained in this
specification.

## Terms and abbreviations

- **VTS** — Verification Test Specification
- **VC** — Verification Case
- **SVP** — Software Verification Plan
- **SI** — Software Item
- **ST** — System Test profile

## Relationship to other documents

The SVP defines verification strategy, levels, profiles, environments and evidence
rules. This VTS defines stable verification cases: purpose, setup, procedure and expected
result.

Executable tests implement these cases in the implementation repository. Retained
verification evidence records the executed revision, actual result and produced
logs/artifacts.

The VTS may reference an SDD to understand test setup, but design or verification
documents do not become upstream product authority merely because they are referenced.

<!-- Add exact SSD/ISD/SVP references for this VTS. -->

## Case identifier convention

Verification cases use:

```text
VC-<profile>-<number>
```

The case ID is the stable traceability identity. Executable-test names should preserve
that identity where practical.

## <Profile> — <Profile name>

### VC-<profile>-<number> — <Case title>

**Verifies**

<!-- Requirement/interface IDs. -->

**Purpose**

<!-- What this case proves. -->

**Setup**

<!-- Required software/hardware/configuration. -->

**Procedure**

1. <step>
2. <step>

**Expected result**

<!-- Observable pass criteria. -->

## Open verification-case questions

<!-- Keep only unresolved case-definition questions. -->

# Software Verification Plan (SVP)

Status: working draft / non-authoritative

## Purpose

This Software Verification Plan defines the verification strategy for the software
system. It defines verification levels, environments, reusable profiles and evidence
rules.

The SVP does not define product behaviour and does not contain the stable step-by-step
procedure of each verification case.

## Terms and abbreviations

- **SVP** — Software Verification Plan
- **VTS** — Verification Test Specification
- **VC** — Verification Case
- **ST** — System Test profile family

## Relationship to other documents

Product requirements and interface contracts define what must be verified.

The SVP defines **how verification is organised**. A VTS defines stable verification
cases: purpose, setup, procedure and expected result. Executable tests implement those
cases. Retained evidence records what revision was executed and the actual result.

Verification documents are downstream of the product definition; they do not become
product requirements by referencing or testing them.

```text
requirements / interfaces
          |
          v
         SVP
          |
          v
         VTS
          |
          v
 executable verification
          |
          v
       evidence
```

## Verification objectives

<!-- State the main verification objectives. -->

## Verification levels

<!-- Define unit/component/system/HIL or other levels used by this project. -->

## Verification profiles

<!-- Define reusable execution compositions/profiles. -->

## Environments and tooling

<!-- Define environment classes without duplicating SDE provisioning detail. -->

## Evidence and traceability

<!-- Define required evidence and traceability rules. -->

## Open verification-strategy questions

<!-- Keep only unresolved strategy questions. -->

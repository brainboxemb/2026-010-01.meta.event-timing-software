# <Software item name> Specification Document (SSD)

Status: working draft / non-authoritative

Software item: **SI-<ID> — <Software item name>**

## Purpose

This document combines the requirements and architecture of **SI-<ID>** in one
software-item baseline.

Requirements keep stable identifiers. Focused SDDs refine this architecture instead of
repeating it.

## Terms and abbreviations

- **SSD** — Software Specification Document
- **SI** — Software Item
- **SSSD** — Software System Specification Document
- **ISD** — Interface Specification Document
- **SDD** — Software Design Description

## Relationship to other documents

This SSD consumes the software-system allocation from the SSSD plus each applicable
system-owned ISD and any directly allocated external obligation.

System use cases provide operational traceability. Focused SDDs are downstream and
define detailed internal design. Verification documents verify the accepted requirements
and interfaces; they do not define product behaviour.

<!-- Add the exact SSSD, ISD/external and SDD references for this software item. -->

## Design boundary

Use this SSD for the software item's **requirements and architecture**: what the main
parts are responsible for, how they relate and which constraints detailed design must
respect.

Keep concrete classes, queue/executor choices, package layout and implementation
algorithms in focused SDDs unless a choice is itself an architectural constraint.

## Software-item requirements

<!-- Add requirements with stable IDs and explicit maturity status. -->

## Software-item architecture

<!-- Define components/responsibilities, internal boundaries and major data/control flow. -->

## Interface realization responsibilities

<!-- State what this item must provide/consume without redefining the ISDs. -->

## Deployment and runtime constraints

<!-- Add item-level deployment/runtime constraints where they are architectural. -->

## Open software-item questions

<!-- Keep only unresolved item-level specification/architecture questions. -->

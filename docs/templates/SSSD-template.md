# <Software system name> Software System Specification Document (SSSD)

Status: working draft / non-authoritative

## Purpose

This Software System Specification Document combines the software-system requirements
baseline with the software-system architecture. It defines the software items, their
allocated responsibilities, system-owned interfaces, deployment relationships and
constraints that apply across software-item boundaries.

It does not define software-item implementation details. Those belong in the applicable
software-item specification and focused detailed-design documents.

## Terms and abbreviations

- **SSSD** — Software System Specification Document
- **SI** — Software Item
- **IF** — system interface
- **ISD** — Interface Specification Document
- **IDD** — Interface Design Description

## Relationship to other documents

The SSSD is shaped by the domain baseline, system use cases and applicable
parent-system/external inputs.

A system-owned ISD is created from an interface allocation made by the SSSD. Once
defined, that ISD constrains each software-item specification that implements or
consumes the interface. An optional IDD may then define the concrete representation of
that interface.

Software-item SSDs/SDDs and verification documents are downstream of the SSSD; they do
not redefine software-system allocation or architecture.

```text
domain / external inputs / system use cases
                    |
                    v
                   SSSD
                    |
          allocates items/interfaces
                    |
          +---------+---------+
          |                   |
          v                   v
   system-owned ISDs      item SSDs
          |                   |
   optional IDDs               v
          |                 item SDDs
          +---------+---------+
```

## Software-system requirements

<!-- Add system requirements with stable IDs and explicit maturity status. -->

## Software-item register

<!-- List software items and their allocated responsibilities. -->

## System context

<!-- Define external systems/devices and the software-system boundary. -->

## System interface catalogue

<!-- List stable system interfaces and their owning/affected software items. -->

## Software-system architecture

<!-- Add cross-item relationships, deployment and architectural constraints. -->

## Open system questions

<!-- Keep only unresolved system-level questions. -->

# <System name> use cases

Status: working draft / non-authoritative

## Purpose

This document captures system-level operational use cases that explain how actors use
the software system.

Use cases describe **desired externally meaningful behaviour and goals**, not
implementation details.

<!-- Add any document-specific scope/public-private statement here. -->

## Terms and abbreviations

- **UC** — Use Case
- **SSSD** — Software System Specification Document
- **ISD** — Interface Specification Document
- **SI** — Software Item

## Relationship to other documents

System use cases are part of the software-system specification/design family. They
express behaviour of the **software system as a whole** before that behaviour is
decomposed across software items.

Relevant parent-system/external inputs are registered in the external-input register.
Together with the domain baseline they can shape these system use cases and the SSSD.

```text
domain / parent-system inputs
          |
          v
     system use cases
          |
          v
         SSSD
          |
   allocates items/interfaces
          |
    +-----+-----+
    |           |
    v           v
system ISDs   optional software-item UC
    |           |
    +-----+-----+
          |
          v
         SSD
          |
          v
         SDD
```

A software-item use case is optional. It is appropriate when responsibility has been
allocated across software items and describing one item's actor/goal behaviour separately
makes the subsequent SSD clearer. It should reference the originating system use case and
must not merely copy it.

A use case is not a test case. One use case may be realised by several requirements and
verified by several verification cases.

## Use-case format

Each use case should contain enough of the following to make the behaviour unambiguous:

```text
ID
Name / goal
Primary actor(s)
Supporting actor(s)
Preconditions
Trigger
Main flow
Alternative / failure flows
Postconditions / observable result
Relevant interfaces
Derived requirements
Verification references
```

## Use-case catalogue

<!-- Add the document-specific catalogue and detailed use cases here. -->

## Open use-case questions

<!-- Keep only genuine unresolved behavioural questions. -->

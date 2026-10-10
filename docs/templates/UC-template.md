# <System name> use cases

Status: working draft / non-authoritative

## Purpose

This document captures system-level use cases describing how people, devices and
external systems use the complete system in its physical operating environment.

Use cases describe actor goals and observable behaviour. Physical equipment and
network conditions may be specified when essential to the scenario; software-item
allocations, IF numbers and internal design belong downstream.

<!-- Add any document-specific scope/public-private statement here. -->

## Terms and abbreviations

- **UC** — Use Case
- **SSSD** — Software System Specification Document
- **ISD** — Interface Specification Document
- **SI** — Software Item

## Relationship to other documents

System use cases are part of the software-system specification/design family. They
express behaviour of the **whole operational system** before the software
responsibilities are allocated in the SSSD.

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
Status (D — Draft, R — Review, A — Approved)
Name / goal
Primary actor(s)
Supporting actor(s)
Preconditions
Trigger
Main flow
Alternative / failure flows
Postconditions / observable result
Relevant physical equipment / operating environment, where important
```

Each use case is a Sphinx-Needs `uc` entry with an explicit `:status:`.
Use D while editing, R when ready for review, and A only after acceptance.
Keep numbered software interfaces and internal implementation details out of UCs.

Use two trailing spaces after the directive opening line, `:id:` and
`:status:` so the raw GitHub Markdown shows each on its own line.
See the source-formatting rule in the Documentation Guide.

```markdown
:::{uc} Example registration use case  
:id: UC-001  
:status: D  

**Goal:** Describe the operator goal.
:::
```

## Use-case catalogue

<!-- Add the document-specific catalogue and detailed use cases here. -->

## Open use-case questions

<!-- Keep only genuine unresolved behavioural questions. -->

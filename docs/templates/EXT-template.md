# External and Parent-System Inputs

Status: working input baseline / traceability register

## Purpose

This register records requirements, interface contracts, protocols, standards or other
controlled sources that are owned **outside the current software-system scope** but can
constrain this software system or an allocated software item.

The external source remains the authority. A local entry records its identity,
applicable revision and scope without silently rewriting, weakening or reinterpreting
the source contract.

## Terms and abbreviations

- **EXT** — External Inputs
- **SSSD** — Software System Specification Document
- **IDD** — Interface Design Description

## Relationship to other documents

Relevant external/parent-system inputs can shape system use cases and constrain the
SSSD. Where responsibility is already allocated explicitly, an external input may also
constrain an affected software-item specification directly.

System-owned ISDs/IDDs are different: they are created and maintained inside this
software-system document set.

```text
external / parent-system source
            |
            v
    external-input register
            |
       +----+----+
       |         |
       v         v
  system UCs    SSSD
                 |
                 v
          allocated item specs
```

## Scope and public/private boundary

Do not copy proprietary protocol values, production identities, credentials, private
topology or other restricted material merely to make this register self-contained.

Record the strongest safe source identity and revision that makes the dependency
reviewable.

## Registered inputs

| Local reference | External owner / scope | External document or contract | Revision / baseline | Applies to | Notes |
| --- | --- | --- | --- | --- | --- |
| <ID> | <owner/scope> | <source> | <revision> | <affected area> | <notes> |

## Entry discipline

A new source revision is reviewed deliberately. Do not silently move the baseline to a
new external revision.

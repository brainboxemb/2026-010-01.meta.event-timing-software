# External and Parent-System Inputs

Status: working input baseline / traceability register


## Document guide

- **Role:** register externally owned requirements, interface contracts, protocols and standards that constrain this software system.
- **Inputs:** controlled parent/external sources.
- **Owns:** only the local registration, revision/applicability and public/private handling of those inputs; it does not rewrite the external source.
- **Downstream:** system use cases, SSSD and directly constrained software-item specifications.
- **Key terms:** `EXT` — External Inputs; `SSSD` — Software System Specification Document; `IDD` — Interface Design Description.

The event-timing software system described by this repository is a subsystem of a larger operational system. Requirements, interface contracts, protocols or standards may therefore be owned **outside the current software-system scope** and still be normative inputs to the SSSD or to an allocated software item.

This document records those upstream inputs without taking ownership of them.

## Purpose

Use this register to record:

- parent-system requirements allocated to this software system;
- externally owned IDDs or interface contracts;
- externally controlled protocols or standards;
- the exact version/revision/baseline that applies;
- the software-system interface, SSSD area or software item constrained by that input;
- whether the source is public, private/proprietary or otherwise externally controlled.

The external source remains the authority. A local entry must not silently rewrite, weaken or reinterpret the source contract.

## Scope and public/private boundary

This public repository may record a safe identifier, owner/scope, revision and applicability while the actual source document remains outside the repository. Do not copy proprietary protocol values, production identities, credentials, private topology or other restricted material merely to make this register self-contained.

Where an external input can be published safely, link/reference its exact controlled revision. Where it cannot, keep enough non-sensitive baseline identity to make the dependency reviewable by authorised project participants.

## Registered inputs

| Local reference | External owner / scope | External document or contract | Revision / baseline | Applies to | Notes |
| --- | --- | --- | --- | --- | --- |
| LEGACY-WEB | Private legacy-system input | Private legacy web/interface design baseline | Controlled private baseline | Legacy client/interface compatibility review before Step-4 public-contract decisions | Private compatibility input only. Keep source identity, content and protocol detail outside the public repository. Record only abstract behavioural conclusions that are safe and necessary for the new-system design. It is not automatically normative for the new software system. |

## Relationship to local documents

```text
parent / surrounding system
        |
        +-- requirement allocation
        +-- externally owned IDD
        +-- protocol / standard
        |
        v
20-01 external-input register
        |
        +--> 30-UC system use cases where applicable
        +--> 31-SSSD
        +--> 40-<N>-SSD when an obligation is already allocated directly
```

System-owned interfaces are different: if the SSSD allocates and this project owns an interface contract, its ISD uses document family `32` with the stable interface ID as its second segment; current examples are `32-03-ISD` for IF-03 and `32-11-ISD` for IF-11. An optional concrete interface design may use family `33` as an IDD.

## Entry discipline

For publishable or unrestricted inputs, record the strongest stable identity
available: document identifier, title, owner, version/revision/date and immutable
reference where possible. If a newer external revision appears, review impact
deliberately rather than silently moving the baseline.

**Exception — `LEGACY-WEB`:** the public register intentionally holds only
the local generic identifier, a private-input category and a controlled-private
baseline designation. Do not add a source title, authors, institution, year,
source/repository location or other identifying metadata. Do not reproduce
private endpoints, message formats, structures or wire examples in public
documents, issues, PR text or normally reachable commit history. A separate
private review may yield only abstract functional compatibility conclusions;
the controlled source itself stays outside this repository.

# <Interface realization> Interface Design Description (IDD)

Status: <draft/review/approved state>

System interface: **IF-<ID> — <Interface name>**

## Purpose

This Interface Design Description maps the semantic **IF-<ID>** contract to the
selected concrete realization.

The ISD owns operation, value, state and failure semantics. This document owns the
concrete representation choices needed to realise those semantics, such as resource or
message names, field names, encoding, framing, transport mapping and representation
versioning.

## Terms and abbreviations

- **IDD** — Interface Design Description
- **ISD** — Interface Specification Document
- **IF** — system interface
- **OP** — Operation defined by the ISD
<!-- Add representation-specific terms such as HTTP, JSONL or CAN only when useful. -->

## Relationship to other documents

This IDD implements the concrete realization of **IF-<ID>** defined by
`<matching ISD document>`.

The ISD remains the semantic interface contract. Software-item design, implementation,
clients/adapters and interface tests consume this IDD where the concrete representation
matters.

The IDD shall not introduce product behaviour that is absent from the ISD.

## Design baseline

<!-- State the selected transport/encoding/representation baseline. -->

## Representation summary

<!-- Give the compact route/message/file/member summary that helps readers navigate. -->

## Semantic-to-representation mapping

<!-- Map each relevant ISD operation/value/requirement to its concrete representation. -->

## Validation and error representation

<!-- Define concrete validation and error mapping without changing ISD semantics. -->

## Compatibility and versioning design

<!-- Define compatible additions and representation-version handling. -->

## ISD mapping

<!-- Table from ISD operations/requirements to concrete design elements. -->

## Open design points

<!-- Keep only unresolved representation/design choices. -->

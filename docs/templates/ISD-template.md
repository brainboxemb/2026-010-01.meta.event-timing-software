# <Interface name> Interface Specification (ISD)

Status: <draft/review/approved state>

System interface: **IF-<ID> — <Interface name>**

## Purpose

This Interface Specification Document defines the **semantic contract** of
**IF-<ID> — <Interface name>**.

It defines what participating software can request, provide or observe and the meaning
of its states, values, results and failures. It deliberately does not define concrete
transport paths, payload member names, framing or other representation details unless
those details are themselves part of the semantic contract.

<!-- Add the interface-specific purpose and boundary here. -->

## Terms and abbreviations

- **IF** — system interface
- **ISD** — Interface Specification Document
- **IDD** — Interface Design Description
- **OP** — Operation
- **SI** — Software Item

## Relationship to other documents

This interface is allocated by the SSSD and supports the behaviour described by
applicable system use cases.

Affected software-item specifications consume this interface contract and shall not
independently redefine its semantics.

An optional IDD may define a concrete protocol, encoding or representation for this
interface. The IDD implements the ISD; it does not replace or change the semantic
contract defined here.

<!-- Add exact SSSD, UC, SSD and IDD references for this interface. -->

## Parties

<!-- Show the participating software items/external actors and interface direction. -->

## Interface model

<!-- Explain semantic interaction styles, addressing and state ownership. -->

## Operation identifiers

Operations use the identifier form `IF<ID>-OP-<number>`. The identifier names a stable
semantic operation and is independent of a concrete transport or wire representation.

## Semantic operations

<!-- Define the operations, inputs, outcomes and observable ordering. -->

## Failure semantics

<!-- Define stable semantic failure categories and outcome-unknown behaviour. -->

## Compatibility

Compatible extensions shall not silently change the meaning of existing operations or
values. Breaking semantic changes require a new interface version or an explicitly
defined migration.

## IF-<ID> requirements

<!-- Add interface requirements with stable IDs and explicit maturity status. -->

## Open points

<!-- Keep only unresolved semantic-interface questions. -->

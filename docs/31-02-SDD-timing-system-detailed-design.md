# Timing System Detailed Design (SDD)

Status: working draft / non-authoritative

This document is the detailed design for the logical `TimingSystem` inside the timing application. It belongs below `31-01-SAD-timing-application-architecture.md` and focuses on the internal state, execution, device interaction and detailed flows of one logical timing system.

The existing detailed timing-system design content is being reorganised into this software-item document family. See the generated document set on `dev/pr-<N>/docs` for the current review view.

## Scope

A `TimingSystem` is the main isolation boundary for waypoint-specific state and behaviour. It owns or coordinates:

- lifecycle such as `OPEN` / `CLOSED`;
- ordered processing of operator commands and device observations;
- participant registrations;
- local start procedure;
- manual registrations;
- penalty registrations and revocations;
- RFID reader lifecycle and tag-processing state;
- display/keypad interaction;
- timing-system status;
- local calculations based on reference data received from the backoffice.

The detailed pseudocode, candidate requirements and device/network flows from the earlier architecture draft remain part of this design and will continue to be refined here.

## Execution model

Each timing system uses a logical serialized execution boundary so mutable state has one ordered writer. Adapter callbacks submit immutable messages rather than mutating state directly. Multiple logical serial executors may share a small backing executor on Raspberry Pi Zero.

## Detailed design areas

This SDD covers or will cover:

- timing-system state model;
- ingress/message processing;
- registration acceptance flow;
- RFID power, boot, initialisation and heartbeat;
- RFID decrypt/filter/resolve pipeline;
- reserve-tag and start-time reference data use;
- local elapsed-time/ranking calculation;
- CAN bus scanning and device registry;
- keypad input processing;
- V1/V2 display interaction at the timing-system boundary;
- network/backoffice status inputs;
- stub/simulated devices and test-control paths;
- deterministic unit-test patterns.

More specialised data/display and Java component details are kept in `31-03-SDD-data-and-display-design.md` and `31-04-SDD-java-component-design.md` so this document does not become the only place for every implementation detail.

# Changelog

- Clarify TimingNode lifecycle ownership: OPEN/CLOSED runtime state now remains independent from lifecycle LogBook persistence, with lifecycle records treated as separately ordered historical TimingData and verification updated accordingly.

All notable changes to this repository are documented here.

The repository is currently in its planning and research phase.

## Unreleased

- Simplify TimingNode current state to strongly typed functional-state and LocationId properties only. Remove the premature INIT/OK/ERROR operational-health model from TimingNode and IF-03.

- Define the generic property pattern as `Property<T>` + `PropertyContainer` + `PropertyUpdate`: owners set typed properties, call `update()` once, and receive one grouped change message. Lifecycle teardown may `sync()` the baseline without emitting a runtime change event.


# IPI — Intermittent TinyML

This directory is part of the `baokhanh-TinyML` research project.

## Purpose

The `ipi/` directory is reserved for project-specific intermittent neural network inference and simulation components.

The research focuses on:

- Energy-harvesting, intermittently powered IoT devices.
- State preservation using non-volatile memory.
- Dynamic early-exit inference.
- Energy-aware Exit / Persist / Skip decisions.

## Current S01 Components

Existing S01 implementations remain in their original locations:

- Speech Commands loader: `../data/gsc.py`
- EnHANTs energy trace loader: `../data/traces.py`
- Unit and integration tests: `../tests/`
- GitHub Actions CI: `../.github/workflows/`

These components are not duplicated or moved into `ipi/`.

## Implementation Status

This directory has been initialized for future project-specific implementation.

Intermittent execution, capacitor dynamics, checkpoint cost models, and early-exit policies are not implemented in this directory yet.

Future modules will be added incrementally, with tests and documented assumptions.

## Scope

All development in this directory remains within the existing `baokhanh-TinyML` repository. No separate repository or hardware deployment is required for this initialization.

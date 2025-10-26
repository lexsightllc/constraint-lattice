# ADR 0001: Establish repository-wide architecture and tooling contract

## Status
Accepted

## Context
The Constraint Lattice repository has grown organically across multiple prototypes, resulting in a
mix of tooling standards, infrastructure layouts, and developer workflows. Inconsistent scripts and
CI behavior made onboarding difficult and created drift between local development and automation.

## Decision
We are adopting the Structure Steward canonical layout:

- Canonical top-level directories (`src/`, `tests/`, `docs/`, `scripts/`, `ci/`, `infra/`, `configs/`, `assets/`, `data/`).
- A standardized developer toolbelt exposed via `scripts/*` and mirrored through the Makefile.
- Uniform documentation (`README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `CHANGELOG.md`).
- Pre-commit hooks enforcing formatting, linting, type-checking, and security scanning.
- A metadata manifest (`project.yaml`) describing runtimes, entrypoints, and ownership.

## Consequences

- Developers have a predictable interface (`make check`) for validating contributions.
- Existing bespoke scripts have been preserved under `scripts/legacy/` for reference but are no longer the supported interface.
- CI workflows will converge on the standardized toolbelt, reducing maintenance overhead.
- Future architectural decisions will be documented under `docs/adr/` to maintain traceability.

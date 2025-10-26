# Contributing to Constraint Lattice

Thank you for investing your time in improving the Constraint Lattice project! This document captures
how to set up your environment, follow our engineering conventions, and propose changes.

## Development prerequisites

- Python 3.11 (managed via [mise](https://mise.jdx.dev/) or `pyenv` using `.tool-versions`)
- Node.js 18 for the web assets and automated tests
- Docker and Docker Compose for end-to-end workflows
- GNU Make for orchestrating developer tasks

Run `make bootstrap` after cloning to install tooling, configure pre-commit hooks, and prime caches.

## Workflow

1. Create a feature branch from `main`.
2. Make your changes with commits that follow the [Conventional Commits](https://www.conventionalcommits.org) style.
3. Run `make check` locally to ensure formatting, linting, typing, testing, security scanning, and coverage checks all pass.
4. Submit a pull request and request reviews from the CODEOWNERS listed in `.github/CODEOWNERS`.
5. Ensure CI passes; the repository only allows fast-forward merges on green builds.

## Coding standards

- Python code must pass `ruff`, `black`, `isort`, and `mypy --strict`.
- TypeScript/JavaScript code must pass `eslint` and `prettier` with `tsc --noEmit` for type analysis.
- Use structured logging, avoid printing secrets, and route sensitive configuration through environment variables.
- Tests live under `tests/` mirroring the `src/` tree, with deterministic seeds and explicit fixtures.

## Commit hygiene

- Run `make fmt` before committing to auto-format staged changes.
- Keep commits focused and include context in the body when necessary.
- Reference related issues with `Fixes #123` syntax in the pull request body when closing issues.

## Reporting security issues

Please do not file public GitHub issues for security vulnerabilities. Email
[security@constraintlattice.dev](mailto:security@constraintlattice.dev) with details so we can respond promptly.

We appreciate your contributions and are excited to collaborate!

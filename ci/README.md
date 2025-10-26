# Continuous Integration

The CI configuration is centralized around the `Structure Steward CI` workflow in `.github/workflows/structure-steward.yml`.

- `make bootstrap --ci` ensures deterministic tool installation.
- `make check` runs the consolidated quality gate locally and in CI.
- `make security-scan` and `make sbom` provide post-check security artifacts.

Reusable job templates and future pipeline experiments should live in this directory.

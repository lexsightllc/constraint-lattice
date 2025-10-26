# Infrastructure

This directory houses infrastructure-as-code assets for the Constraint Lattice platform.

- `docker/` contains development, testing, and production Dockerfiles plus compose definitions.
- `kubernetes/` contains manifests for managed clusters.

Legacy symlinks are preserved at the repository root to maintain backwards compatibility with
existing scripts. New infrastructure should live within this directory.

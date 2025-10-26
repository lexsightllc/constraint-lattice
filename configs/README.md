# Configuration Manifests

Configuration files that parameterize Constraint Lattice services live in this directory. Policies,
YAML pipelines, and environment-specific overrides should be tracked here.

Symlinks are maintained from historical paths (e.g., `constraints.yaml`) to avoid breaking older
integrations. New configuration files should follow kebab-case naming and include comments for
sensitive defaults.

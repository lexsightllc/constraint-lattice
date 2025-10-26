# License Provenance Audit - MPL Relicensing Blocked

## Summary
The requested relicensing to the Mozilla Public License 2.0 (MPL-2.0) cannot proceed at this time. The repository currently contains source files that carry the license notice "AGPL-3.0-only OR Commercial" without documented consent from all contributors to relicense under MPL-2.0. Until explicit approval is obtained from those contributors, relicensing would violate the inbound license terms.

## Blocking Components
The following components are blocked:

- `src/api/varkiel_agent-main/` — introduced in commit `26af91278f4a59cf74e6865badd79964b9b0bba3` by `Your Name <you@example.com>`. Files under this path embed the SPDX header `SPDX-License-Identifier: AGPL-3.0-only OR Commercial`.
- `varkiel_agent_main/` — introduced in commit `26af91278f4a59cf74e6865badd79964b9b0bba3` by `Your Name <you@example.com>`. Files under this path embed the same SPDX header `SPDX-License-Identifier: AGPL-3.0-only OR Commercial`.

These components are governed by the GNU Affero General Public License v3.0 (AGPL-3.0-only) unless separate commercial terms are agreed. AGPL-3.0-only is incompatible with relicensing to MPL-2.0 without explicit contributor consent.

## Required Actions
1. Obtain written consent from the contributor(s) associated with commit `26af91278f4a59cf74e6865badd79964b9b0bba3` to relicense the affected files under MPL-2.0, or replace the AGPL-covered code with code authored under MPL-2.0.
2. Once consent is received or the code is replaced, rerun the provenance audit to ensure no remaining GPL-family restrictions conflict with MPL-2.0 relicensing.

Until these steps are complete, all relicensing, CI enforcement, SPDX header updates, and NOTICE adjustments must remain on hold. The CI status for the relicensing workflow should be marked as `blocked-by-consent` to reflect this dependency.

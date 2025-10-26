# License Provenance Audit — MPL Relicensing Blocked

**Audit timestamp:** 2025-10-26T22:30:37Z (UTC)

## Repository Inventory
- **Tracked files:** 707 (`git ls-files`)
- **Contributors (git shortlog -sne):**
  - 4 commits — Augusto Ochoa Ughini <lexsightllc@lexsightllc.com>
  - 1 commit — Your Name <you@example.com>

No dedicated `THIRD_PARTY_NOTICES` artifact or vendor subtree was identified in the repository. Any inbound third-party code should be cataloged before proceeding with relicensing.

## License Scan Findings
A search for GPL-family identifiers (`rg "GPL" --hidden --glob '!node_modules' --glob '!.git'`) returned multiple matches indicating GNU Affero General Public License v3.0 only (AGPL-3.0-only) coverage. Representative files include:

- `varkiel_agent_main/src/varkiel/central_controller.py`
- `varkiel_agent_main/src/varkiel/structural_constraint_engine.py`
- `src/api/varkiel_agent-main/src/varkiel/central_controller.py`
- `src/api/varkiel_agent-main/src/varkiel/structural_constraint_engine.py`

Each of these files declares the SPDX header `SPDX-License-Identifier: AGPL-3.0-only OR Commercial`.

## Blocking Components
The following components prevent relicensing to MPL-2.0 without additional consent:

- `src/api/varkiel_agent-main/` — introduced in commit `26af91278f4a59cf74e6865badd79964b9b0bba3` by `Your Name <you@example.com>`.
- `varkiel_agent_main/` — introduced in commit `26af91278f4a59cf74e6865badd79964b9b0bba3` by `Your Name <you@example.com>`.

These directories contain Python source files, scripts, and documentation that explicitly embed the SPDX notice `SPDX-License-Identifier: AGPL-3.0-only OR Commercial`. The inbound AGPL-3.0-only grant is incompatible with unilateral relicensing to MPL-2.0.

## Required Actions Before Relicensing
1. Obtain written consent from `Your Name <you@example.com>` (author of commit `26af91278f4a59cf74e6865badd79964b9b0bba3`) to relicense the affected files under MPL-2.0 **or** replace the AGPL-covered code with original work that is explicitly offered under MPL-2.0.
2. Catalogue any third-party code (if present) in a `THIRD_PARTY_NOTICES` register including the original license texts.
3. Rerun this provenance audit after addressing the above items to confirm that no GPL-only material remains and that all inbound licenses are documented.

## CI / Workflow Status
Until the required consents or replacements are secured, the relicensing initiative must remain on hold. CI workflows enforcing the relicensing effort should report `blocked-by-consent` rather than succeeding or silently skipping steps.

**Conclusion:** Relicensing to MPL-2.0 is currently **blocked** by AGPL-3.0-only inbound code. Do not modify LICENSE, NOTICE, SPDX headers, or package metadata until the required consents are acquired and the third-party catalog is complete.

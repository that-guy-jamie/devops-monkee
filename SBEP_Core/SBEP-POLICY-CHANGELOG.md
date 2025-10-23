# SBEP Policy Changelog
All substantive changes to SBEP rules are tracked here.

## 2025-10-23
- v2.2 Complete operational framework integration with CI/CD pipeline
- v2.2 Added ops/scripts/sbep-verify-links.js for automatic link verification
- v2.2 Added ops/scripts/sbep-doc-integrity-check.py for document corruption detection
- v2.2 Added ops/scripts/sbep-retention-cleaner.py for automated retention management
- v2.2 Added ops/scripts/sbep-env-guard.sh for production operation safety
- v2.2 Added ci/.gitlab-ci.fragment.yml with test-stage quality gates
- v2.2 Added EXCEPTION-POLICIES/EP-DEP-001.md for structured exception handling
- v2.2 Added SBEP-ADDENDUM-SCP.md for canonical SCP deployment procedures
- v2.2 Added housekeeping.config.json for retention and quality configuration
- v2.2 Added .sbep-link-ignore for link verification exclusions
- v2.2 Added package.json with operational scripts and dependencies
- v2.1 Updated SBEP Protocol repository with deprecation workflow policy
- v2.1 Replaced absolute "never delete" rule with structured 5-step deletion process
- v2.1 Added retention windows for archived items (180d docs, 90d builds/artifacts)
- v2.1 Enhanced HOUSEKEEPING-SOP.md with link integrity checks and work-in-progress guards

## 2025-10-21
- v1.2 Align defaults with repo conventions (`/Archive/**`), CI images per-job (node:lts, python:3.11).
- v1.2 Link verifier supports `.sbep-link-ignore` and limited default scan scope.
- v1.2 Critical doc paths corrected for repo layout.
- v1.2 Added manual-only retention apply job in CI.
- v1.2 Stub addendum points to canonical SCP addendum in SBEP_Core.

## 2025-10-20
- Added EP-DEP-001 (Manual Deployment Exception Policy).
- Clarified housekeeping retention and link verification steps.
- Replaced absolute prohibitions ("NEVER delete/move") with a deprecation workflow and retention windows.
- Added doc integrity and link verification CI checks.


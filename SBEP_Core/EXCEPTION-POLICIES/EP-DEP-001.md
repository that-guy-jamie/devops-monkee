# EP-DEP-001 — Manual Deployment Exception Policy
Version: 1.2
Last-Updated: 2025-10-21

## Purpose
Allow a narrowly-scoped, auditable exception to the "scripted deploys only" rule when CI/CD is unavailable and the deployment script cannot succeed.

## When This Policy Applies
- CI/CD service is degraded or unreachable, and
- `ops/scripts/*` deployment script has failed after at least 1 retry with logs collected.

## Required Steps
1. Create an exception log file at `ops/logs/deploy-exceptions/{timestamp}-{env}.md`.
2. Use the approved manual path (SCP or WP-CLI over SSH) exactly as documented.
3. Capture:
   - Who, when, environment, commit SHA
   - Root cause summary
   - Exact commands executed (with redactions)
   - Validation checks/results
4. Open a follow-up ticket for remediation and to restore scripted deploys.

## Prohibited
- Using this policy for convenience or speed.
- Skipping step 3 (evidence capture).

## Sunset
This exception is valid only for the specific incident. It does not authorize future manual deploys.
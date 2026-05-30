# PR-14A Validation Report

Date: 2026-05-30  
Branch: `production/pr-14a-github-actions-staging-validation`  
Base branch: `master`  
Base commit: `1b8a979fd60b44c31467026fd429bf8a9c6c1521`

## Scope

PR-14A prepares the repository for owner-approved staging deployment and evidence capture. It adds a manual GitHub Actions workflow, staging scripts, GitHub Environment documentation, and production-control status updates.

PR-14A does not deploy to a VPS, change DNS, issue certificates, activate payments, onboard customers, use real customer data, or change public production status.

## Validation Results

| Area | Command / Method | Result | Notes |
| --- | --- | --- | --- |
| Workflow YAML syntax | `ruby -e "require 'yaml'; YAML.load_file('.github/workflows/staging-deploy-validation.yml'); puts 'yaml ok'"` | PASS | Ruby YAML loader parsed the workflow. |
| Staging shell syntax | `bash -n scripts/staging/*.sh` | PASS | All staging scripts parsed. |
| Shellcheck | `command -v shellcheck` | NOT RUN | `shellcheck` is not installed in this environment. |
| Status JSON | `python3 -m json.tool production-control/status/production-status.json` | PASS | JSON parsed successfully. |
| Roadmap SVG | Python `xml.etree.ElementTree` parse | PASS | SVG parsed successfully. |
| Dashboard/status consistency | `rg` across status JSON, Mermaid, SVG and dashboard for PR-14A/PR-14B/NO-GO | PASS | Visible status artifacts include PR-14A, PR-14B and NO-GO state. |
| Git whitespace | `git diff --check` | PASS | No whitespace errors. |
| Frontend install | `npm ci` | PASS | Required because workflow files changed. |
| Frontend lint | `npm run lint` | PASS | ESLint passed. |
| Frontend typecheck | `npm run typecheck` | PASS | TypeScript passed. |
| Frontend unit/static tests | `npm test` | PASS | Static check passed. |
| Frontend browser E2E | `npm run test:e2e` | PASS | Passed after sandbox escalation for local server binding; 5 Chromium tests passed. |
| Frontend production build | `npm run build` | PASS | Next.js build completed. |
| Frontend dependency audit | `npm audit --audit-level=high` | PASS WITH WARNING | High threshold passed after sandbox network escalation; two moderate transitive PostCSS advisories through Next.js remain below the gate. |

## External Evidence Not Produced

PR-14A intentionally did not produce live external evidence. PR-14B must still capture:

- owner-approved staging/VPS deployment smoke;
- TLS certificate issuance and renewal proof;
- firewall/private-port proof for PostgreSQL and Redis;
- backup creation and restore drill;
- live PostgreSQL/pgvector migration and RAG smoke;
- live Redis worker and multi-worker job claim smoke;
- controlled website/document ingestion smoke;
- live rate-limit analytics and quota/abuse smoke;
- backend-integrated browser smoke with synthetic data;
- monitoring/logging/alerting evidence;
- owner approval.

## Current Recommendation

PR-14A is repository-complete after local validation. Public production remains NO-GO. The next phase is PR-14B after the owner configures the GitHub `staging` Environment variables/secrets and manually approves the staging workflow using synthetic data only.

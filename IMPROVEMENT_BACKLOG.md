# Improvement Backlog — v16

## Completed in v16

### Interpret

- Added persistent local run metrics history for Interpret.
- Added run-to-run metric comparison.
- Added reviewer mode for obligations: `Correct`, `Needs review`, `Incorrect`.
- Added final review report: `supported`, `weak`, `missing`, `reviewed`.
- Added downloadable final review report JSON.
- Added local review report persistence.
- Added decision log to Interpret output schema and demo output.

### Discover

- Added optional upstream Interpret JSON input.
- Added explicit `obligation → requirement → Jira → QA` pipeline.
- Added rule-based PRD completeness scoring independent of the LLM.
- Added `what_would_invalidate_this_feature` criteria.
- Added approval workflow by team.
- Added enterprise controls in product discovery output.

### Communicate

- Added sentence-level `claim → risk → reason → safer rewrite` table.
- Added stronger Interpret/Discover upstream link table.
- Added approval workflow by Product, QA, Support and Legal/Compliance.
- Added realistic before/after copy examples.
- Added customer escalation / compliance-boundary wording.

### Investigate

- Strengthened sample incident with customer escalation, filing deadline and compliance-sensitive impact.
- Added owner, timestamp and severity score per event.
- Added severity chart and max severity metric.
- Added customer escalation context and compliance boundary.
- Made postmortem actions more actionable with owner, due date and evidence required.

### Enterprise readiness

- Added Enterprise Readiness app page.
- Added enterprise control matrix covering authentication, RBAC, secure storage, audit, versioning, integrations, observability, cost monitoring, retention and deployment.
- Added proposed RBAC matrix.
- Added secure deployment checklist.
- Added `docs/ENTERPRISE_PRODUCT_SPEC.md`.

## Still not production-ready — honest gaps

- Authentication is not implemented; needs OIDC/SAML SSO.
- RBAC is specified but not enforced.
- Secure encrypted document storage is not implemented.
- Audit logs are local JSONL, not immutable enterprise audit storage.
- Document versioning is represented through diffing, not a full version store.
- Jira/Confluence/Slack/GitHub integrations are parser/export stubs, not OAuth-backed syncs.
- Observability is UI-level only; no traces, alerts or production dashboards.
- Cost monitoring is per-run estimate only; no budget enforcement.
- Data retention policy is documented but not enforced by purge/legal-hold jobs.
- Deployment remains Streamlit prototype; production needs containers, secrets manager, CI security checks and infrastructure controls.

## P0 — before sharing with hiring teams

- Deploy on Streamlit Cloud using only synthetic/public data.
- Replace mockup SVGs with real screenshots from the deployed app.
- Capture screenshots of: Interpret Reviewer & History, Discover Pipeline, Communicate Claim Risk, Investigate Severity Timeline and Enterprise Readiness.
- Record a 60–90 second demo video.
- Run all tests and benchmarks and include generated results in the repo.
- Add one public hero case study walkthrough with screenshots.

## P1 — deeper credibility

- Increase benchmark size to at least 25–50 questions and 25–50 gold obligations.
- Add a reviewer identity simulation to saved review reports.
- Add tests for reviewer report generation and PRD completeness scoring.
- Add a second-model judge as optional comparison, clearly separated from deterministic checks.
- Add tests for contradictory source text and modality conflicts.
- Add GitHub Actions badge to README once pushed.

## P2 — real enterprise platform path

- Authentication and role-based access control.
- Persistent audit logs and document versioning.
- Private document storage and retention policy.
- Observability and cost monitoring.
- Real integrations with Jira, Confluence, Slack, GitHub and Zendesk.

## Completed in v17 — hiring signal layer

- Repositioned README opening to state clearly that this is a portfolio case study, not a commercial product.
- Added `PORTFOLIO_REVIEW_GUIDE.md` with 5-minute, 15-minute and 45-minute review paths.
- Added `WHAT_THIS_DEMONSTRATES.md` with a skills-to-evidence map.
- Added `INTERVIEW_TALKING_POINTS.md` for concise interview positioning.
- Added `docs/ERROR_TAXONOMY_FAILURE_MODES.md` with formal error taxonomy, intentional failure cases and trade-off analysis.
- Updated the 90-second demo script to focus on one hero workflow instead of showing every module equally.
- Clarified the portfolio hierarchy: hero workflow first; supporting workflows, synthetic evaluation and enterprise controls as evidence.

## Next hiring-signal improvements

- Replace SVG mockups with real screenshots from a deployed app.
- Add a 90-second demo video link to the README.
- Add a short “Lessons learned” section after running the project with 2–3 real reviewers.
- Expand synthetic evaluation into a small human-reviewed benchmark.

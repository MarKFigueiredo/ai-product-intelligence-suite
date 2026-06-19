# Enterprise Readiness Roadmap — v1.02

This repository is a portfolio prototype. It demonstrates product thinking and AI workflow design, not a production enterprise system.

## Implemented or demoed in the prototype

- Local `.env` / Streamlit secrets pattern.
- `.gitignore` for secrets and local audit/run files.
- Exportable audit trail JSON per output package.
- Persistent local Interpret run metrics in `.local_runs/interpret_run_history.jsonl`.
- Persistent local review reports in `.local_runs/interpret_review_history.jsonl`.
- SQLite audit store in `.local_runs/enterprise_audit.db` with actor, role, action, workflow, document hash, output hash and signature fields.
- Sidebar role simulation for Admin, Product Manager, Compliance Reviewer, QA, Support, Legal/Compliance, Auditor and Viewer.
- Deterministic permission checks in `services/enterprise_controls_service.py`.
- SHA-256 document version hash records.
- Signed report manifest export using demo HMAC integrity signing.
- Jira and GitHub API-shaped mock connector payload builders.
- Reviewer mode for obligations: correct / incorrect / needs review.
- Run-to-run comparison of average support, weak/missing claims and quote integrity.
- Rule-based citation support checks.
- Rule-based PRD completeness checks in Discover.
- Interpret → Discover pipeline: obligation → requirement → Jira → QA.
- Release sentence-risk review: claim → risk → reason → safer rewrite.
- Incident timeline owner/timestamp/severity scoring.
- Synthetic benchmark runner for the Interpret module.
- Synthetic hero-case evaluation runner for SAF-T/e-invoicing.
- GitHub Actions smoke tests.
- Enterprise Readiness UI page with control matrix, RBAC proposal, implemented local controls and deployment checklist.

## Required for real enterprise use

- Authentication with OIDC/SAML SSO.
- Role-based access control enforced in application, API and storage layers.
- Private encrypted document storage with tenant isolation and retention policy.
- Persistent append-only audit log with immutable run IDs and reviewer identity.
- Source document versioning with source/extraction hashes and immutable review history.
- Observability for cost, latency, retrieval quality and failure modes.
- Real OAuth/webhook integrations with Jira, Confluence, Slack, GitHub and Zendesk.
- Human review workflow with approval states and separation of duties.
- Security review for regulated documents.
- Larger evaluation dataset and human-reviewed gold outputs.

## Recommended implementation epics

1. **Identity and access** — SSO, tenant model, RBAC, reviewer permissions.
2. **Secure evidence store** — encrypted document/object storage, metadata database, immutable hashes.
3. **Workflow persistence** — run history, review states, approval workflow, document versions.
4. **Integrations** — Jira, Confluence, Slack, GitHub and Zendesk OAuth apps and sync jobs.
5. **Observability and FinOps** — traces, errors, quality metrics, cost dashboards and budget alerts.
6. **Retention and compliance operations** — legal hold, purge jobs, export, data processing records.
7. **Secure deployment** — container, CI security checks, secrets manager, network controls and IaC.

## Portfolio proof now visible in v1.02

The strongest evidence path is:

```text
HERO_SAF_T_EINVOICING_CASE.md
→ PRODUCT_STRATEGY.md
→ SYNTHETIC_EVALUATION_RESULTS.md
→ enterprise_controls_service.py
→ tests/test_v1.02_enterprise_controls.py
```

That path shows not only a product idea, but a measurable workflow and implemented local control surface.

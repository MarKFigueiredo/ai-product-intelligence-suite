# Enterprise Product Spec — v1.02

This document captures the enterprise product elements represented in the suite, what is now genuinely implemented as local prototype control, and what still requires production platform engineering.

## Implemented or demoed in v1.02

| Area | v1.02 implementation | Production note |
|---|---|---|
| Run history | Local JSONL run metric history for Interpret | Move to tenant-scoped encrypted database / audit store |
| Run comparison | Latest runs table with metric deltas | Add dashboards, filtering and tenant/project dimensions |
| Reviewer mode | Correct / incorrect / needs-review verdicts per obligation | Bind decisions to authenticated identity and approval workflow state |
| Final review report | JSON export with supported / weak / missing / reviewed buckets | Store immutable signed report with source/output hashes |
| Decision log | Interpret and Discover outputs include decision logs | Add approval events, sign-off and change history |
| Role simulation | Sidebar demo identity and role selector; deterministic permission matrix in `enterprise_controls_service.py` | Replace with OIDC/SAML SSO and service-layer RBAC enforcement |
| Document version hashes | SHA-256 document version records with metadata and no default source-text persistence | Persist version metadata in tenant DB; store content in encrypted object store under retention policy |
| Persistent audit events | SQLite audit table with actor, role, action, workflow, document hash, output hash and HMAC demo signature | Replace with append-only audit store, KMS signing, retention and export controls |
| Signed report manifest | HMAC-SHA256 demo manifest with report hash, document hash, signer and approval status | Replace with KMS/HSM-backed signing and identity-bound approval |
| Jira/GitHub mock connector | API-shaped payload builders for Jira and GitHub issue creation | Add OAuth apps, scopes, retries, rate limits, webhook audit logs |
| PRD completeness | Deterministic rule-based completeness score in Discover | Make rules configurable by product/org policy |
| Pipeline | Discover shows obligation → requirement → Jira → QA | Sync to Jira and test management system through OAuth/webhooks |
| Release risk | Sentence-level claim → risk → reason → safer rewrite | Add policy library and required approval thresholds |
| Incident severity | Owner, timestamp and severity score per event | Add integrations to incident systems and SLA tracking |
| Synthetic evaluation | One deep SAF-T/e-invoicing hero evaluation with manual, simple-LLM and assisted workflow baselines | Replace with human-reviewed multi-document benchmark before production claims |

## Production control requirements

### Authentication

Use OIDC/SAML SSO, tenant-aware session handling, service accounts for integrations and token rotation. v1.02 only simulates user and role locally.

### RBAC

Minimum roles: Admin, Product Manager, Compliance Reviewer, QA, Support, Legal/Compliance, Auditor and Viewer. Reviewer approval should require a reviewer/compliance role; export/admin functions should be gated separately. v1.02 demonstrates the matrix and permission checks, but does not secure an API boundary.

### Secure storage

Source documents, embeddings, outputs and review decisions should be encrypted at rest with tenant boundaries. v1.02 stores metadata, hashes and audit events locally; it does not provide encrypted tenant storage.

### Persistent audit logs

Production logs should be append-only and include source hash, prompt/config metadata, output hash, model, reviewer identity, verdict, export timestamp and retention policy. v1.02 includes a SQLite audit store to show the data model and persistence path.

### Document versioning

Each uploaded source should have immutable versions with content hash, extracted text hash, parser metadata and reviewer status. v1.02 includes SHA-256 document version records and Interpret diff view, but not a full version store.

### Integrations

Jira, Confluence, Slack and GitHub should use OAuth apps or installation tokens, with scope minimization, retry queues, webhook event logs, rate-limit handling and admin approval. v1.02 includes API-shaped mock payloads and parser stubs.

### Observability

Add structured logs, run trace IDs, latency/error dashboards, alerting and model quality drift monitoring.

### Cost monitoring

Keep per-run estimates, but add tenant/project budgets, spend dashboards, model routing policies and budget alerts.

### Data retention policy

Add tenant-specific retention, legal hold, export and purge workflows. Retention events must be auditable.

### Secure deployment

Use containerized deployment, CI checks, vulnerability scanning, managed secrets, network controls and infrastructure-as-code.

## Honest positioning

v1.02 goes beyond slides by implementing a few local controls: role simulation, permission checks, document version hashes, SQLite audit persistence, signed manifests and Jira/GitHub payload builders. It is still not a production enterprise system. The correct claim is:

> The suite demonstrates the product workflow, control model, review/audit artefacts and implementation path needed for enterprise readiness; full enforcement requires production platform engineering.

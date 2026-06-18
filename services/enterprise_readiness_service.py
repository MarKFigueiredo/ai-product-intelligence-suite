"""Enterprise product readiness control matrix."""
from __future__ import annotations

from typing import Dict, List


def enterprise_control_matrix() -> List[Dict[str, str]]:
    return [
        {"control": "Authentication", "current_state": "Demo user/role simulation in sidebar", "target_state": "OIDC/SAML SSO, service accounts, token rotation", "status": "Partially demoed", "owner": "Platform/Security"},
        {"control": "RBAC", "current_state": "Role simulation with deterministic permission matrix and gated examples", "target_state": "Identity-bound RBAC enforced at API/service layer", "status": "Partially demoed", "owner": "Product/Platform"},
        {"control": "Secure storage", "current_state": "Local files for demo metadata", "target_state": "Encrypted object storage plus encrypted relational metadata store", "status": "Roadmap", "owner": "Platform"},
        {"control": "Persistent audit logs", "current_state": "Local JSONL plus SQLite audit store with signed event manifests", "target_state": "Append-only audit store with retention, signing and export", "status": "Partially demoed", "owner": "Security/Compliance"},
        {"control": "Document versioning", "current_state": "Version diff plus SHA-256 document version records", "target_state": "Immutable document versions with source hashes and reviewer sign-off", "status": "Partially demoed", "owner": "Product/Platform"},
        {"control": "Jira/Confluence/Slack/GitHub integrations", "current_state": "Parser stubs plus Jira/GitHub payload builders with API-shaped schemas", "target_state": "OAuth apps, webhooks, scopes, retry queues and rate-limit handling", "status": "Partially demoed", "owner": "Integrations"},
        {"control": "Observability", "current_state": "UI metrics only", "target_state": "Structured logs, traces, latency/error dashboards and alerting", "status": "Roadmap", "owner": "SRE"},
        {"control": "Cost monitoring", "current_state": "Per-run estimate", "target_state": "Budget alerts, model spend dashboard and tenant-level chargeback", "status": "Partially demoed", "owner": "FinOps/Product"},
        {"control": "Data retention", "current_state": "Local demo files can be deleted", "target_state": "Tenant retention policy, legal hold, purge jobs and export", "status": "Roadmap", "owner": "Compliance/Platform"},
        {"control": "Secure deployment", "current_state": "Streamlit prototype", "target_state": "Containerized deployment, secrets manager, CI checks, IaC and vulnerability scanning", "status": "Roadmap", "owner": "Platform/SecOps"},
    ]


def rbac_matrix() -> List[Dict[str, str]]:
    return [
        {"role": "Admin", "can_upload_sources": "Yes", "can_generate": "Yes", "can_review": "Yes", "can_export": "Yes", "can_manage_retention": "Yes"},
        {"role": "Product Manager", "can_upload_sources": "Yes", "can_generate": "Yes", "can_review": "Comment", "can_export": "Yes", "can_manage_retention": "No"},
        {"role": "Compliance Reviewer", "can_upload_sources": "Yes", "can_generate": "No", "can_review": "Approve/Reject", "can_export": "Yes", "can_manage_retention": "No"},
        {"role": "QA", "can_upload_sources": "No", "can_generate": "No", "can_review": "Test evidence", "can_export": "QA assets", "can_manage_retention": "No"},
        {"role": "Auditor", "can_upload_sources": "No", "can_generate": "No", "can_review": "Read-only", "can_export": "Audit package", "can_manage_retention": "No"},
    ]


def deployment_checklist() -> List[Dict[str, str]]:
    return [
        {"area": "Secrets", "requirement": "Use managed secrets, never .env in production", "evidence": "Secrets manager reference in deployment config"},
        {"area": "Network", "requirement": "Private ingress for internal tenants or WAF for public access", "evidence": "Network policy / WAF rule"},
        {"area": "Storage", "requirement": "Encryption at rest and per-tenant access boundaries", "evidence": "KMS key policy and storage ACL"},
        {"area": "Audit", "requirement": "Append-only log of source hash, prompt metadata, output hash and review decision", "evidence": "Audit export"},
        {"area": "Retention", "requirement": "Configurable purge and legal hold", "evidence": "Retention policy config and purge job log"},
        {"area": "Observability", "requirement": "Trace ID per run, latency/error/cost metrics", "evidence": "Dashboard link and alert policy"},
    ]

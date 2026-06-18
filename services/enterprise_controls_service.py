"""Enterprise control utilities for the portfolio prototype.

These functions deliberately implement a small, inspectable subset of enterprise
controls instead of pretending the Streamlit demo is production-ready:

- role simulation with deterministic permission checks;
- immutable-ish document version hashes;
- SQLite-backed persistent audit events;
- signed report manifests;
- Jira/GitHub mock connector payloads that resemble real integration contracts.

The signing helper is a portfolio demo integrity checksum, not a replacement for
managed keys, KMS/HSM signing, append-only storage or enterprise identity.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

ROOT = Path(__file__).resolve().parents[1]
LOCAL_DIR = ROOT / ".local_runs"
SQLITE_AUDIT_FILE = LOCAL_DIR / "enterprise_audit.db"

ROLES = [
    "Admin",
    "Product Manager",
    "Compliance Reviewer",
    "QA",
    "Support",
    "Legal/Compliance",
    "Auditor",
    "Viewer",
]

ROLE_PERMISSIONS: Dict[str, set[str]] = {
    "Admin": {
        "upload_source",
        "generate_output",
        "review_obligation",
        "approve_requirement",
        "approve_release_copy",
        "export_report",
        "sign_report",
        "view_audit_log",
        "manage_retention",
        "create_jira_payload",
    },
    "Product Manager": {
        "upload_source",
        "generate_output",
        "comment_review",
        "approve_requirement",
        "export_report",
        "create_jira_payload",
    },
    "Compliance Reviewer": {
        "upload_source",
        "review_obligation",
        "approve_requirement",
        "approve_release_copy",
        "export_report",
        "sign_report",
        "view_audit_log",
    },
    "QA": {
        "view_requirement",
        "add_test_evidence",
        "comment_review",
        "export_report",
        "create_jira_payload",
    },
    "Support": {
        "view_requirement",
        "comment_review",
        "approve_release_copy",
        "export_report",
    },
    "Legal/Compliance": {
        "review_obligation",
        "approve_release_copy",
        "sign_report",
        "view_audit_log",
        "export_report",
    },
    "Auditor": {"view_requirement", "view_audit_log", "export_report"},
    "Viewer": {"view_requirement"},
}

ACTION_DESCRIPTIONS = {
    "upload_source": "Upload or paste compliance source material",
    "generate_output": "Generate AI-assisted product output",
    "review_obligation": "Mark an obligation correct/incorrect/needs review",
    "approve_requirement": "Approve a requirement for engineering handoff",
    "approve_release_copy": "Approve customer-facing release copy",
    "export_report": "Export markdown/HTML/audit package",
    "sign_report": "Create a signed report manifest",
    "view_audit_log": "Inspect persistent audit events",
    "manage_retention": "Change retention or purge policy",
    "create_jira_payload": "Create a Jira-style issue payload",
    "add_test_evidence": "Attach QA evidence to a requirement/test case",
    "comment_review": "Add reviewer comments without final sign-off",
    "view_requirement": "Read product requirements and traceability",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, default=str, separators=(",", ":"))


def stable_hash(value: Any, *, length: int = 16) -> str:
    payload = canonical_json(value) if not isinstance(value, str) else value
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:length]


def can(role: str, action: str) -> bool:
    return action in ROLE_PERMISSIONS.get(role, set())


def permission_rows(role: str | None = None) -> List[Dict[str, Any]]:
    roles = [role] if role else ROLES
    actions = sorted(ACTION_DESCRIPTIONS.keys())
    rows: List[Dict[str, Any]] = []
    for role_name in roles:
        for action in actions:
            rows.append(
                {
                    "role": role_name,
                    "action": action,
                    "allowed": can(role_name, action),
                    "description": ACTION_DESCRIPTIONS[action],
                }
            )
    return rows


def document_version_record(
    *,
    document_name: str,
    content: str,
    uploaded_by: str = "demo-user",
    role: str = "Product Manager",
    version_label: str = "v1",
    previous_hash: str = "",
) -> Dict[str, Any]:
    normalized = (content or "").replace("\r\n", "\n").strip()
    content_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    record = {
        "document_name": document_name or "unnamed_document",
        "version_label": version_label,
        "document_hash": content_hash,
        "short_hash": content_hash[:16],
        "previous_hash": previous_hash,
        "uploaded_by": uploaded_by,
        "role": role,
        "created_at_utc": utc_now(),
        "bytes": len(normalized.encode("utf-8")),
        "line_count": len(normalized.splitlines()) if normalized else 0,
        "note": "Stores the hash and metadata only; source text is not persisted by default.",
    }
    return record


def _connect(db_path: Path = SQLITE_AUDIT_FILE) -> sqlite3.Connection:
    LOCAL_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_audit_db(db_path: Path = SQLITE_AUDIT_FILE) -> Path:
    conn = _connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp_utc TEXT NOT NULL,
                actor TEXT NOT NULL,
                role TEXT NOT NULL,
                action TEXT NOT NULL,
                workflow TEXT NOT NULL,
                document_hash TEXT,
                output_hash TEXT,
                signature TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_events(timestamp_utc)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_workflow ON audit_events(workflow)")
        conn.commit()
    finally:
        conn.close()
    return db_path


def _demo_secret() -> bytes:
    # Portfolio-only default. Production should use KMS-managed secrets and key rotation.
    return os.getenv("AI_PM_DEMO_SIGNING_SECRET", "portfolio-demo-local-signing-key").encode("utf-8")


def sign_payload(payload: Dict[str, Any]) -> str:
    digest = hmac.new(_demo_secret(), canonical_json(payload).encode("utf-8"), hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def record_audit_event(
    *,
    actor: str,
    role: str,
    action: str,
    workflow: str,
    document_hash: str = "",
    output: Any | None = None,
    metadata: Dict[str, Any] | None = None,
    db_path: Path = SQLITE_AUDIT_FILE,
) -> Dict[str, Any]:
    init_audit_db(db_path)
    output_hash = stable_hash(output or {}, length=64) if output is not None else ""
    payload = {
        "timestamp_utc": utc_now(),
        "actor": actor or "demo-user",
        "role": role,
        "action": action,
        "workflow": workflow,
        "document_hash": document_hash,
        "output_hash": output_hash,
        "metadata": metadata or {},
    }
    payload["signature"] = sign_payload(payload)
    conn = _connect(db_path)
    try:
        cursor = conn.execute(
            """
            INSERT INTO audit_events (
                timestamp_utc, actor, role, action, workflow, document_hash,
                output_hash, signature, payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["timestamp_utc"],
                payload["actor"],
                payload["role"],
                payload["action"],
                payload["workflow"],
                payload["document_hash"],
                payload["output_hash"],
                payload["signature"],
                canonical_json(payload),
            ),
        )
        conn.commit()
        payload["audit_event_id"] = int(cursor.lastrowid)
    finally:
        conn.close()
    return payload


def list_audit_events(limit: int = 25, db_path: Path = SQLITE_AUDIT_FILE) -> List[Dict[str, Any]]:
    init_audit_db(db_path)
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            "SELECT id, timestamp_utc, actor, role, action, workflow, document_hash, output_hash, signature FROM audit_events ORDER BY id DESC LIMIT ?",
            (int(limit),),
        ).fetchall()
    finally:
        conn.close()
    return [dict(row) for row in rows]


def signed_report_manifest(
    *,
    report: Dict[str, Any],
    signer: str,
    signer_role: str,
    document_hash: str = "",
    approval_status: str = "Reviewed",
) -> Dict[str, Any]:
    report_hash = stable_hash(report, length=64)
    manifest = {
        "signed_at_utc": utc_now(),
        "signer": signer or "demo-user",
        "signer_role": signer_role,
        "approval_status": approval_status,
        "document_hash": document_hash,
        "report_hash": report_hash,
        "algorithm": "HMAC-SHA256 demo manifest",
        "production_note": "For production, replace this with KMS-backed signing, immutable storage and identity-bound approval.",
    }
    manifest["signature"] = sign_payload(manifest)
    return manifest


def build_jira_issue_payload(
    *,
    requirement: Dict[str, Any],
    pipeline_row: Dict[str, Any] | None = None,
    project_key: str = "COMP",
    issue_type: str = "Story",
) -> Dict[str, Any]:
    pipeline_row = pipeline_row or {}
    summary = requirement.get("requirement") or requirement.get("summary") or pipeline_row.get("requirement") or "Compliance requirement"
    requirement_id = requirement.get("requirement_id") or pipeline_row.get("requirement_id") or "REQ-TBD"
    obligation_id = requirement.get("obligation_id") or pipeline_row.get("obligation_id") or pipeline_row.get("obligation") or "OBL-TBD"
    description = {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": f"Requirement: {summary}"}]},
            {"type": "paragraph", "content": [{"type": "text", "text": f"Source obligation: {obligation_id}"}]},
            {"type": "paragraph", "content": [{"type": "text", "text": f"Traceability: {pipeline_row.get('pipeline', 'obligation → requirement → Jira → QA')}"}]},
        ],
    }
    return {
        "endpoint": "/rest/api/3/issue",
        "method": "POST",
        "fields": {
            "project": {"key": project_key},
            "issuetype": {"name": issue_type},
            "summary": summary[:255],
            "description": description,
            "labels": ["ai-assisted", "compliance", "traceability", str(requirement_id).lower()],
            "priority": {"name": requirement.get("priority", "High")},
            "customfield_obligation_id": obligation_id,
            "customfield_requirement_id": requirement_id,
            "customfield_source_hash": requirement.get("source_hash", ""),
        },
    }


def build_github_issue_payload(*, title: str, body: str, labels: Iterable[str] | None = None) -> Dict[str, Any]:
    return {
        "endpoint": "POST /repos/{owner}/{repo}/issues",
        "title": title[:256],
        "body": body,
        "labels": list(labels or ["compliance", "ai-assisted", "needs-review"]),
    }

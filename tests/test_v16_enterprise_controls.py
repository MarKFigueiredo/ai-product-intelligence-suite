from pathlib import Path

from services.enterprise_controls_service import (
    build_jira_issue_payload,
    can,
    document_version_record,
    init_audit_db,
    list_audit_events,
    record_audit_event,
    signed_report_manifest,
)


def test_role_simulation_enforces_different_permissions():
    assert can("Compliance Reviewer", "review_obligation") is True
    assert can("Viewer", "review_obligation") is False
    assert can("Product Manager", "create_jira_payload") is True
    assert can("Auditor", "manage_retention") is False


def test_document_version_hash_is_stable_for_same_content():
    a = document_version_record(document_name="sample.txt", content="A\nB", uploaded_by="Marco", role="Product Manager")
    b = document_version_record(document_name="sample.txt", content="A\r\nB", uploaded_by="Marco", role="Product Manager")
    assert a["document_hash"] == b["document_hash"]
    assert len(a["document_hash"]) == 64
    assert a["short_hash"] == a["document_hash"][:16]


def test_sqlite_audit_store_persists_events(tmp_path: Path):
    db_path = tmp_path / "audit.db"
    init_audit_db(db_path)
    event = record_audit_event(
        actor="marco@example.com",
        role="Compliance Reviewer",
        action="sign_report",
        workflow="Interpret",
        document_hash="abc123",
        output={"supported": 4},
        metadata={"case": "hero"},
        db_path=db_path,
    )
    rows = list_audit_events(limit=10, db_path=db_path)
    assert event["audit_event_id"] == rows[0]["id"]
    assert rows[0]["role"] == "Compliance Reviewer"
    assert rows[0]["signature"].startswith("sha256=")


def test_signed_report_manifest_and_jira_payload():
    report = {"summary": {"supported": 4, "weak": 1}}
    manifest = signed_report_manifest(report=report, signer="Marco", signer_role="Compliance Reviewer", document_hash="abc")
    assert manifest["report_hash"]
    assert manifest["signature"].startswith("sha256=")
    payload = build_jira_issue_payload(
        requirement={"requirement_id": "R1", "requirement": "Validate AccountID before export", "priority": "High"},
        pipeline_row={"obligation_id": "O1", "pipeline": "obligation → requirement → Jira → QA"},
        project_key="SAFT",
    )
    assert payload["endpoint"] == "/rest/api/3/issue"
    assert payload["fields"]["project"]["key"] == "SAFT"
    assert payload["fields"]["customfield_obligation_id"] == "O1"

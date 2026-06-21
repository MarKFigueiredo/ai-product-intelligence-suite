import json

from services import audit_service, release_gate_service
from services.claim_hygiene_service import (
    audit_portfolio_claims,
    classify_context,
    safe_positioning_statement,
    scan_text,
)


def test_claim_hygiene_classifies_safe_context():
    assert classify_context("This is a demo and does not guarantee compliance.") == "Framed/acceptable"
    assert classify_context("This guarantees full legal compliance.") == "Needs review"


def test_claim_hygiene_flags_absolute_compliance_guarantee():
    findings = scan_text("This guarantees full legal compliance.", source="README.md")

    assert any(
        finding["rule_id"] == "CH02"
        and finding["severity"] == "High"
        and finding["context"] == "Needs review"
        for finding in findings
    )


def test_claim_hygiene_downgrades_framed_risky_examples():
    findings = scan_text(
        "Bad example: guaranteed compliance is risky and must not be claimed.",
        source="docs/VALIDATION_LIMITATIONS.md",
    )

    assert findings
    assert all(finding["context"] == "Framed/acceptable" for finding in findings)
    assert all(finding["severity"] == "Info" for finding in findings)


def test_audit_portfolio_claims_scans_repository_like_folder(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("This guarantees full legal compliance.", encoding="utf-8")

    result = audit_portfolio_claims(tmp_path)

    assert result["files_scanned"] == 1
    assert result["needs_review_total"] >= 1
    assert result["high_risk_total"] >= 1
    assert result["summary"] == "Review recommended"


def test_safe_positioning_statement_avoids_guaranteed_hiring_outcomes():
    statement = safe_positioning_statement().lower()

    assert "does not guarantee interviews" in statement
    assert "depends on" in statement


def test_stable_hash_is_deterministic_and_short():
    first = audit_service.stable_hash("same input")
    second = audit_service.stable_hash("same input")

    assert first == second
    assert len(first) == 16


def test_build_audit_event_uses_hash_not_raw_input_text():
    event = audit_service.build_audit_event(
        workflow="Interpret",
        model="demo-model",
        demo_mode=True,
        input_text="Sensitive source text",
        output_summary={"obligations": 3},
        source_count=2,
    )

    assert event["workflow"] == "Interpret"
    assert event["model"] == "demo-model"
    assert event["demo_mode"] is True
    assert event["source_count"] == 2
    assert event["output_summary"] == {"obligations": 3}
    assert event["input_hash"] == audit_service.stable_hash("Sensitive source text")
    assert "Sensitive source text" not in json.dumps(event)


def test_append_audit_event_writes_jsonl(tmp_path, monkeypatch):
    audit_dir = tmp_path / "audit"
    audit_file = audit_dir / "run_log.jsonl"

    monkeypatch.setattr(audit_service, "AUDIT_DIR", audit_dir)
    monkeypatch.setattr(audit_service, "AUDIT_FILE", audit_file)

    event = audit_service.build_audit_event(
        workflow="Discover",
        model="demo-model",
        demo_mode=True,
        input_text="input",
    )

    written_path = audit_service.append_audit_event(event)

    assert written_path == audit_file
    assert audit_file.exists()

    lines = audit_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["workflow"] == "Discover"


def test_release_gate_passes_when_required_controls_pass(monkeypatch):
    monkeypatch.setattr(
        release_gate_service,
        "validate_negative_test_coverage",
        lambda output: {"release_gate_status": "Pass"},
    )

    result = release_gate_service.evaluate_release_gate({"risks": []}, citation_rows=[])

    assert result["status"] == "Pass"
    assert result["blockers"] == []
    assert result["warnings"] == []


def test_release_gate_blocks_when_negative_test_coverage_fails(monkeypatch):
    monkeypatch.setattr(
        release_gate_service,
        "validate_negative_test_coverage",
        lambda output: {"release_gate_status": "Fail"},
    )

    result = release_gate_service.evaluate_release_gate({"risks": []}, citation_rows=[])

    assert result["status"] == "Blocked"
    assert "Mandatory negative test coverage is incomplete." in result["blockers"]


def test_release_gate_warns_on_weak_grounding_and_unresolved_risks(monkeypatch):
    monkeypatch.setattr(
        release_gate_service,
        "validate_negative_test_coverage",
        lambda output: {"release_gate_status": "Pass"},
    )
    monkeypatch.setattr(
        release_gate_service,
        "grounding_summary",
        lambda citation_rows: {
            "checked_claims": 2,
            "weak_or_missing_claims": 1,
            "human_review_required": True,
        },
    )

    result = release_gate_service.evaluate_release_gate(
        {"risks": [{"title": "Unresolved scope risk"}]},
        citation_rows=[{"claim": "Supported claim"}],
    )

    assert result["status"] == "Review required"
    assert "Some claims have weak or missing source support." in result["warnings"]
    assert "Risk register contains unresolved items." in result["warnings"]

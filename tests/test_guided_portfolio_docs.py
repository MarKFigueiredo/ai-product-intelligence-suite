from pathlib import Path

from services.connector_handoff_service import handoff_payloads
from services.evidence_report_service import generate_real_usage_evidence_markdown
from services.lineage_service import detect_stale_artifacts, hero_lineage_state, impact_analysis
from services.portfolio_demo_service import (
    PERSONA_REVIEW_PATHS,
    REAL_VS_SIMULATED,
    SKILL_EVIDENCE,
    evidence_drawer_items,
    hero_output_shape,
    release_gate_dashboard,
)
from services.run_comparison_service import compare_runs
from services.qa_coverage_service import validate_negative_test_coverage


def test_guided_hero_output_has_release_ready_negative_coverage():
    output = hero_output_shape()
    gate = release_gate_dashboard(output)
    negative_gate = gate["negative_gate"]
    assert negative_gate["obligations_total"] >= 4
    assert negative_gate["release_gate_status"] == "Pass"
    assert negative_gate["negative_test_coverage_rate"] == 100
    assert gate["overall_status"] in {"Ready", "Warning"}


def test_evidence_drawer_links_obligations_to_requirements_and_qa():
    items = evidence_drawer_items(hero_output_shape())
    obligation_items = [row for row in items if row["artifact_type"] == "Obligation"]
    assert obligation_items
    assert any(row["linked_requirement"] != "Missing" for row in obligation_items)
    assert any("QA-SAF-T" in row["linked_qa"] for row in obligation_items)


def test_lineage_detects_stale_downstream_artifact_and_impact():
    state = hero_lineage_state()
    stale = detect_stale_artifacts(state["artifacts"], state["links"])
    assert any(row["artifact_id"] == "REQ-SAF-T-001" for row in stale)
    impact = impact_analysis("O-SAF-T-002", state)
    affected = {row["artifact_id"] for row in impact["affected_artifacts"]}
    assert {"REQ-SAF-T-001", "JIRA-SAF-T-001", "QA-SAF-T-002-NEG"}.issubset(affected)


def test_persona_and_skill_tables_cover_hiring_reviewers():
    assert {"Recruiter", "Hiring Manager", "Principal PM", "QA Lead", "Compliance Reviewer", "Engineering Lead"}.issubset(PERSONA_REVIEW_PATHS)
    assert any(row["skill"] == "QA/product quality judgment" for row in SKILL_EVIDENCE)
    assert any(row["capability"] == "SQLite usage metrics store" and row["status"] == "Real local" for row in REAL_VS_SIMULATED)


def test_connector_handoff_payloads_are_previewable():
    payloads = handoff_payloads()
    connectors = {row["connector"] for row in payloads}
    assert connectors == {"Jira", "GitHub", "Slack"}
    assert all(row["payload"] for row in payloads)


def test_run_comparison_marks_positive_and_negative_metrics():
    run_a = {"metrics": {"qa_coverage_rate": 60, "unsupported_claim_rate": 22}, "latency_ms": 1000}
    run_b = {"metrics": {"qa_coverage_rate": 90, "unsupported_claim_rate": 6}, "latency_ms": 800}
    rows = {row["metric"]: row for row in compare_runs(run_a, run_b)}
    assert rows["qa_coverage_rate"]["direction"] == "improved"
    assert rows["unsupported_claim_rate"]["direction"] == "improved"
    assert rows["latency_ms"]["direction"] == "improved"


def test_real_usage_evidence_report_is_generated():
    report = generate_real_usage_evidence_markdown()
    assert "# Real Usage Evidence Report" in report
    assert "Total workflow runs" in report


def test_v20_docs_exist():
    for filename in [
        "docs/UI_UX_REVIEW.md",
        "docs/reviewer/DEMO_WALKTHROUGH.md",
        "docs/STALENESS_AND_LINEAGE_POLICY.md",
        "docs/CONNECTOR_HANDOFF_CENTER.md",
        "REAL_USAGE_EVIDENCE_REPORT.md",
    ]:
        assert Path(filename).exists(), filename

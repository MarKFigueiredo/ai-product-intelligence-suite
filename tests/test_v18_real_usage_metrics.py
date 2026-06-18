from pathlib import Path

from services.real_connectors_service import connector_statuses
from services.usage_metrics_service import (
    derive_metrics,
    export_usage_payload,
    import_usage_payload,
    init_usage_db,
    list_workflow_runs,
    record_workflow_run,
    usage_summary,
)


def test_derive_interpret_metrics_from_real_output_shape():
    output = {
        "obligation_extraction": [{"obligation_id": "O1"}, {"obligation_id": "O2"}],
        "product_requirements": [{"requirement_id": "R1"}],
        "qa_test_cases": [{"test_id": "TC1"}, {"test_id": "TC2"}],
        "validation_rules": [{"rule_id": "VR1"}],
    }
    citation_rows = [
        {"exists": True, "support_score": 88, "review_required": False},
        {"exists": False, "support_score": 0, "review_required": True},
    ]
    metrics = derive_metrics("Interpret", output, citation_rows=citation_rows, latency_ms=123, source_count=3)
    assert metrics["obligations_total"] == 2
    assert metrics["qa_coverage_rate"] == 100.0
    assert metrics["requirement_coverage_rate"] == 50.0
    assert metrics["unsupported_claim_rate"] == 50.0
    assert metrics["human_review_rate"] == 50.0
    assert metrics["latency_ms"] == 123


def test_usage_metrics_persist_and_export_import(tmp_path: Path):
    db_path = tmp_path / "usage.db"
    init_usage_db(db_path)
    record_workflow_run(
        workflow="Interpret",
        actor="tester",
        role="Product Manager",
        model="demo-model",
        demo_mode=True,
        input_payload={"input": "abc"},
        output_payload={"obligation_extraction": []},
        latency_ms=42,
        source_count=1,
        metrics={"latency_ms": 42, "obligations_total": 0},
        db_path=db_path,
    )
    runs = list_workflow_runs(db_path=db_path)
    assert len(runs) == 1
    assert runs[0]["metrics"]["latency_ms"] == 42
    summary = usage_summary(db_path)
    assert summary["runs_total"] == 1
    payload = export_usage_payload(db_path)
    imported_db = tmp_path / "imported.db"
    result = import_usage_payload(payload, db_path=imported_db)
    assert result["imported_runs"] == 1
    assert usage_summary(imported_db)["runs_total"] == 1


def test_connector_statuses_are_inspectable():
    statuses = connector_statuses()
    assert {row["name"] for row in statuses} >= {"Jira", "GitHub", "Slack webhook"}
    assert all("configured" in row and "missing" in row for row in statuses)

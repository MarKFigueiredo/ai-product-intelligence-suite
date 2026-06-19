from __future__ import annotations

from pathlib import Path

from core.pipeline import pipeline_plan, run_interpret_review_discover_pipeline
from services.citation_verifier import support_components
from services.human_feedback_service import (
    apply_feedback_examples_to_output,
    feedback_examples_for_next_run,
    init_human_feedback_db,
    record_human_review,
    summarize_feedback_inventory,
)
from services.portfolio_demo_service import GUIDED_STEPS
from services.qa_coverage_service import validate_negative_test_coverage


def test_core_pipeline_plan_is_declarative_and_ordered():
    steps = pipeline_plan()
    assert [s["step_id"] for s in steps][:3] == ["interpret", "verify", "review"]
    assert "qa" in [s["step_id"] for s in steps]
    assert "learn" in [s["step_id"] for s in steps]
    assert all(s["owner"] for s in steps)


def test_core_pipeline_runs_guardrails_without_streamlit():
    output = {
        "obligation_extraction": [{"obligation_id": "O1", "obligation": "Validate invoice totals before export", "source": "[S1]"}],
        "qa_test_cases": [{"test_id": "T1", "obligation_id": "O1", "type": "Negative", "scenario": "Invalid total is blocked"}],
    }
    result = run_interpret_review_discover_pipeline(output, include_feedback=False)
    assert result.negative_gate["release_gate_status"] == "Pass"
    assert result.steps[-1]["step_id"] == "learn"
    assert result.output["_pipeline"]["negative_gate_status"] == "Pass"


def test_human_feedback_table_and_reuse_examples(tmp_path):
    db = tmp_path / "usage_metrics.db"
    init_human_feedback_db(db)
    record_human_review(
        original_text="The system guarantees full legal compliance automatically.",
        review_label="incorrect",
        corrected_text="The system supports review against configured compliance rules.",
        review_reason="Avoid compliance guarantee.",
        domain="SAF-T invoice export validation",
        reviewer_role="Compliance Reviewer",
        reviewer_name="Reviewer A",
        db_path=db,
    )
    summary = summarize_feedback_inventory(domain="SAF-T invoice export validation", db_path=db)
    assert summary["human_reviews_total"] == 1
    assert summary["feedback_examples_available"] == 1
    examples = feedback_examples_for_next_run(domain="SAF-T invoice export validation", db_path=db)
    assert len(examples) == 1


def test_feedback_examples_adjust_unsafe_obligation_wording():
    output = {
        "obligation_extraction": [
            {"obligation_id": "O1", "obligation": "The system guarantees full legal compliance automatically."}
        ]
    }
    examples = [{"review_id": "hr-test", "review_label": "incorrect", "original_text": "guarantees full legal compliance", "review_reason": "Avoid compliance guarantee."}]
    adjusted, summary = apply_feedback_examples_to_output(output, examples)
    assert summary["obligations_adjusted_by_feedback"] == 1
    assert "guarantees full legal compliance" not in adjusted["obligation_extraction"][0]["obligation"].lower()


def test_qa_negative_gate_blocks_happy_path_only():
    data = {
        "obligation_extraction": [{"obligation_id": "O1", "obligation": "Validate invoice total"}],
        "qa_test_cases": [{"test_id": "T1", "obligation_id": "O1", "type": "Positive", "scenario": "Valid invoice passes validation"}],
    }
    gate = validate_negative_test_coverage(data)
    assert gate["release_gate_status"] == "Blocked"
    assert gate["missing_negative_coverage"] == ["O1"]


def test_citation_verifier_unit_negation_and_numbers():
    supported = support_components("The export report must show failed records and reasons.", "Export reports must show which invoice records failed validation and why.")
    negated = support_components("The export report must not show failed records.", "Export reports must show which invoice records failed validation and why.")
    numeric = support_components("Records must be retained for 10 years.", "Records must be retained for 5 years.")
    assert supported["support_score"] > negated["support_score"]
    assert negated["negation_mismatch"] is True
    assert "10" in numeric["missing_numbers"]


def test_guided_demo_is_eight_step_progressive_flow():
    assert len(GUIDED_STEPS) == 8
    assert GUIDED_STEPS[0]["title"] == "Source"
    assert GUIDED_STEPS[-1]["title"] == "Learning loop"
    ui = Path("ui/guided_demo_page.py").read_text(encoding="utf-8")
    assert "Step {step['step']}/8" in ui
    assert "st.progress" in ui
    assert "Show all 8 steps" in ui

from prompts.product_prompt import build_product_prompt
from prompts.release_prompt import build_release_prompt
from prompts.timeline_prompt import build_timeline_prompt
from services.product_quality_service import compute_prd_rule_completeness
from services.run_history_service import (
    build_final_review_report,
    build_reviewer_items,
    summarise_interpret_run,
)


def _complete_discovery_payload():
    return {
        "problem_statement": "Users need safer compliance export validation.",
        "personas": [{"persona": "PM"}],
        "assumptions_to_test": [{"assumption": "Blocking is acceptable"}],
        "trade_off_analysis": [{"decision": "Block vs warn"}],
        "success_metrics": [{"metric": "Detection", "target": "95%"}],
        "jira_tickets": [{"summary": "Validate tax ID"}],
        "qa_test_matrix": [{"test_case": "Missing tax ID"}],
        "compliance_pipeline": [{"obligation": "O1", "requirement": "R1", "jira": "J1", "qa": "TC1"}],
        "decision_log": [{"decision": "Block critical errors"}],
        "what_would_invalidate_this_feature": [{"signal": "False negatives"}],
        "approval_workflow": [{"team": "QA"}],
        "security_and_enterprise_controls": [{"control": "Audit"}],
    }


def test_prd_completeness_scores_complete_payload_high():
    result = compute_prd_rule_completeness(_complete_discovery_payload())
    assert result["score"] == 100
    assert "Obligation → requirement → Jira → QA pipeline" not in result["missing"]


def test_prompts_include_v16_enterprise_requirements():
    product_prompt = build_product_prompt({"interpret_context": "O1"})
    release_prompt = build_release_prompt({"upstream_context": "R1"})
    timeline_prompt = build_timeline_prompt({"raw_notes": "2026-01-10 incident"})
    assert "obligation → requirement → Jira → QA" in product_prompt
    assert "claim → risk → reason → safer_rewrite" in release_prompt
    assert "severity_score" in timeline_prompt


def test_run_history_report_groups_review_statuses():
    data = {
        "obligation_extraction": [
            {"obligation_id": "O1", "obligation": "Must include tax ID", "source": "[S1]", "quote_support": "must include tax ID"}
        ],
        "product_requirements": [{"requirement_id": "R1"}],
        "qa_test_cases": [{"test_id": "TC1"}],
    }
    citation_rows = [
        {"section": "obligation_extraction", "row": "1", "claim": "Must include tax ID", "citation": "S1", "exists": True, "support_score": 90, "verification_status": "Supported", "review_required": False, "supporting_quote": "must include tax ID"}
    ]
    items = build_reviewer_items(data, citation_rows)
    assert items[0]["default_status"] == "Correct"
    report = build_final_review_report(data, citation_rows, [{"obligation_id": "O1", "status": "Correct", "comment": "ok"}])
    assert report["summary"]["supported"] == 1
    record = summarise_interpret_run(data, citation_rows, model="demo", demo_mode=True, input_hash="abc", source_count=1)
    assert record["supported_obligations"] == 1

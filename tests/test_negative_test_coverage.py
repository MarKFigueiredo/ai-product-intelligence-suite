from services.product_quality_service import compute_prd_rule_completeness
from services.qa_coverage_service import is_negative_test, validate_negative_test_coverage
from services.usage_metrics_service import derive_metrics


def test_negative_test_classifier_detects_failure_cases():
    assert is_negative_test({"type": "Negative", "test_case": "Missing CustomerTaxID is blocked"})
    assert is_negative_test({"scenario": "Invalid VAT code", "expected_result": "Validation error shown"})
    assert not is_negative_test({"type": "Positive", "scenario": "Valid invoice passes validation"})


def test_negative_coverage_blocks_when_obligation_has_only_happy_path():
    data = {
        "obligation_extraction": [{"obligation_id": "O1", "obligation": "CustomerTaxID is required"}],
        "qa_test_cases": [
            {"obligation_id": "O1", "type": "Positive", "scenario": "Valid invoice passes validation"}
        ],
    }
    result = validate_negative_test_coverage(data)
    assert result["release_gate_status"] == "Blocked"
    assert result["negative_test_coverage_rate"] == 0
    assert result["missing_negative_coverage"] == ["O1"]


def test_negative_coverage_passes_only_when_each_obligation_has_mapped_negative_test():
    data = {
        "obligation_extraction": [
            {"obligation_id": "O1", "obligation": "CustomerTaxID is required"},
            {"obligation_id": "O2", "obligation": "Failure report must include reason"},
        ],
        "qa_test_cases": [
            {"obligation_id": "O1", "type": "Negative", "scenario": "Missing CustomerTaxID is blocked"},
            {"obligation_id": "O2", "type": "Edge", "scenario": "Failed invoice without reason is rejected"},
        ],
    }
    result = validate_negative_test_coverage(data)
    assert result["release_gate_status"] == "Pass"
    assert result["negative_test_coverage_rate"] == 100
    assert result["missing_negative_coverage"] == []


def test_unmapped_negative_test_does_not_satisfy_multi_obligation_gate():
    data = {
        "obligation_extraction": [
            {"obligation_id": "O1", "obligation": "CustomerTaxID is required"},
            {"obligation_id": "O2", "obligation": "Failure report must include reason"},
        ],
        "qa_test_cases": [
            {"type": "Negative", "scenario": "Missing CustomerTaxID is blocked"}
        ],
    }
    result = validate_negative_test_coverage(data)
    assert result["release_gate_status"] == "Blocked"
    assert result["unmapped_negative_tests"] == 1
    assert set(result["missing_negative_coverage"]) == {"O1", "O2"}


def test_prd_completeness_includes_mandatory_negative_coverage_rule():
    data = {
        "problem_statement": "Problem",
        "jobs_to_be_done": [{"job": "Validate"}],
        "assumptions_to_test": [{"assumption": "Users accept blocking"}],
        "trade_off_analysis": [{"decision": "Block vs warn"}],
        "success_metrics": [{"metric": "Detection"}],
        "jira_tickets": [{"summary": "Validate"}],
        "qa_test_matrix": [{"obligation_id": "O1", "type": "Positive", "test_case": "Valid invoice passes"}],
        "compliance_pipeline": [{"obligation": "O1 — Tax ID required"}],
        "decision_log": [{"decision": "Block"}],
        "what_would_invalidate_this_feature": [{"signal": "False negatives"}],
        "approval_workflow": [{"team": "QA"}],
        "security_and_enterprise_controls": [{"control": "Audit"}],
    }
    result = compute_prd_rule_completeness(data)
    assert "Mandatory negative test coverage" in result["missing"]
    assert result["negative_test_gate"]["release_gate_status"] == "Blocked"


def test_usage_metrics_persist_negative_coverage_metrics_from_actual_output():
    output = {
        "obligation_extraction": [{"obligation_id": "O1"}],
        "qa_test_cases": [{"obligation_id": "O1", "type": "Negative", "scenario": "Missing tax ID is blocked"}],
    }
    metrics = derive_metrics("Interpret", output)
    assert metrics["negative_test_coverage_rate"] == 100
    assert metrics["negative_tests_total"] == 1
    assert metrics["missing_negative_tests_total"] == 0

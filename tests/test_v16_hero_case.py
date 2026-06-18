import json
from pathlib import Path

from scripts.run_synthetic_hero_evaluation import run


def test_hero_case_contains_full_product_loop():
    text = Path("docs/HERO_SAF_T_EINVOICING_CASE.md").read_text(encoding="utf-8")
    required = [
        "Synthetic input document excerpt",
        "Extracted obligations",
        "Reviewer corrections",
        "Before / after requirement",
        "Jira ticket",
        "QA case",
        "Risky release note vs safer release note",
        "Incident if missed",
        "Final audit report",
    ]
    for phrase in required:
        assert phrase in text


def test_synthetic_hero_evaluation_outputs_metrics():
    result = run()
    assert result["headline"]["time_to_first_requirement_set"] == "45 min manual → 8 min assisted"
    rows = {row["metric"]: row for row in result["rows"]}
    assert rows["Unsupported claim rate"]["assisted_workflow"] == 6
    assert rows["QA coverage"]["assisted_workflow"] == 90
    output = Path("benchmark/results/synthetic_hero_evaluation.json")
    assert output.exists()
    assert json.loads(output.read_text(encoding="utf-8"))["honesty_note"]


def test_product_strategy_has_required_sections():
    text = Path("PRODUCT_STRATEGY.md").read_text(encoding="utf-8")
    for phrase in [
        "ICP",
        "User personas",
        "Buyer",
        "Strategic wedge",
        "Adoption path",
        "Pricing hypothesis",
        "North Star Metric",
        "Activation metric",
        "Retention metric",
        "Expansion strategy",
    ]:
        assert phrase in text

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from config import APP_NAME, APP_VERSION


def test_v24_version_and_scope_docs_exist():
    assert APP_VERSION == "1.04"
    assert APP_NAME.endswith("1.04")
    scope = Path("PORTFOLIO_SCOPE_DISCIPLINE.md").read_text(encoding="utf-8")
    assert "What I intentionally did not build" in scope
    assert "production SSO" in scope
    assert "v24 focuses on validation and generalization" in scope or "v25 focuses on core pipeline" in scope


def test_auto_score_to_claim_scanner_story_is_documented():
    text = Path("docs/AUTO_SCORE_TO_CLAIM_SCANNER_STORY.md").read_text(encoding="utf-8")
    assert "self-scores" in text
    assert "claim_hygiene_service.py" in text
    assert "prevent regression" in text or "prevention mechanism" in text


def test_citation_validation_pack_is_present_and_honest():
    study = Path("docs/CITATION_VERIFIER_VALIDATION_STUDY.md").read_text(encoding="utf-8")
    assert "Human review has not yet been collected" in study
    assert "must not pretend" in study
    sample = Path("validation/citation_claims_sample.csv").read_text(encoding="utf-8")
    assert sample.count("\n") >= 30
    assert "human_reviewer_1" in sample
    template = Path("validation/human_review_template.csv").read_text(encoding="utf-8")
    assert "human_label" in template


def test_citation_error_analysis_publishes_failure_modes():
    text = Path("docs/CITATION_VERIFIER_ERROR_ANALYSIS.md").read_text(encoding="utf-8")
    assert "False positive from keyword overlap" in text
    assert "False negative from paraphrase" in text
    assert "The verifier makes grounding risk visible before review" in text


def test_swiss_qr_bill_second_domain_case_runs():
    assert Path("sample_inputs/swiss_qr_bill_sample.txt").exists()
    assert Path("sample_inputs/swiss_qr_bill_gold_obligations.json").exists()
    subprocess.run([sys.executable, "scripts/run_swiss_qr_bill_benchmark.py"], check=True)
    result = json.loads(Path("benchmark/results/second_domain_swiss_qr_bill_benchmark.json").read_text(encoding="utf-8"))
    assert result["domain"] == "Swiss QR-Bill / invoice payment compliance"
    assert result["gold_obligations"] == 10
    assert "not legal correctness" in " ".join(result["limitations"])


def test_citation_validation_analysis_reports_pending_without_fake_human_labels():
    subprocess.run([sys.executable, "scripts/analyze_citation_validation.py"], check=True)
    result = json.loads(Path("validation/citation_validation_results.json").read_text(encoding="utf-8"))
    assert result["claims_total"] == 30
    assert result["claims_with_human_labels"] == 0
    assert result["claims_pending_human_labels"] == 30
    assert result["simple_agreement_rate"] is None

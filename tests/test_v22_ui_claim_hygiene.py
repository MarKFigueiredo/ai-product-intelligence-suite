from pathlib import Path

from config import APP_NAME, AVAILABLE_MODELS, WORKFLOWS
from services.claim_hygiene_service import audit_portfolio_claims, safe_positioning_statement, scan_text


def test_v22_config_and_claim_hygiene_page_are_present():
    assert APP_NAME.startswith("AI Product Intelligence Suite ")
    assert WORKFLOWS["Claim Hygiene Audit"] == "claim_hygiene"
    assert not any("gpt-5.4" in model or "gpt-5.5" in model for model in AVAILABLE_MODELS)


def test_claim_hygiene_flags_unframed_overclaim():
    findings = scan_text("This will guarantee interviews and guarantees legal compliance.", "sample.md")
    assert any(row["context"] == "Needs review" for row in findings)
    assert any(row["severity"] == "High" for row in findings)


def test_claim_hygiene_accepts_safe_framing():
    findings = scan_text("This portfolio does not guarantee interviews and does not guarantee compliance.", "sample.md")
    assert findings
    assert all(row["context"] == "Framed/acceptable" for row in findings)


def test_portfolio_claim_audit_has_no_unframed_high_medium_findings():
    result = audit_portfolio_claims(Path("."))
    assert result["summary"] == "Pass"
    assert result["needs_review_total"] == 0


def test_v22_docs_and_timeline_asset_exist():
    assert Path("docs/UI_UX_POLISH_V22.md").exists()
    assert Path("docs/CLAIM_HYGIENE_AUDIT.md").exists()
    assert Path("assets/screenshots/04_guided_timeline.svg").exists()



def test_safe_hiring_statement_is_bounded():
    text = safe_positioning_statement().lower()
    assert "does not guarantee interviews" in text
    assert "targeting" in text

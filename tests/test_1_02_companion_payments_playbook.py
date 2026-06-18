from pathlib import Path

from config import APP_NAME, APP_VERSION

ROOT = Path(__file__).resolve().parents[1]


def test_public_version_is_1_02():
    assert APP_VERSION == "1.04"
    assert APP_NAME.endswith("1.04")


def test_payments_companion_playbook_is_present_but_not_a_workflow():
    companion = ROOT / "companion_playbooks" / "ai_payments_compliance" / "Playbook_Draft_AI_Payments_Compliance_EN.docx"
    companion_readme = ROOT / "companion_playbooks" / "ai_payments_compliance" / "README.md"
    summary = ROOT / "docs" / "AI_PAYMENTS_COMPLIANCE_MIT_COURSE_COMPANION.md"
    assert companion.exists()
    assert companion_readme.exists()
    assert summary.exists()
    text = summary.read_text(encoding="utf-8")
    assert "SEPA / ISO 20022" in text
    assert "not part of the core Streamlit app" in text


def test_companion_docs_preserve_scope_discipline():
    docs = (ROOT / "docs" / "COMPANION_PLAYBOOKS.md").read_text(encoding="utf-8")
    assert "Why it is not a new app module" in docs
    assert "scope discipline" in docs


def test_payments_sample_scaffolding_exists():
    sample = ROOT / "sample_inputs" / "payments_iso20022_structured_address_sample.txt"
    expected = ROOT / "sample_inputs" / "payments_iso20022_expected_outputs.json"
    assert sample.exists()
    assert expected.exists()
    assert "structured" in sample.read_text(encoding="utf-8").lower() and "address" in sample.read_text(encoding="utf-8").lower()
    assert "PAY-ADDR-001" in expected.read_text(encoding="utf-8")

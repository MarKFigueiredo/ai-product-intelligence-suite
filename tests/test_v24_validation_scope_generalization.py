from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_validation_limitations_document_exists():
    path = ROOT / "VALIDATION_LIMITATIONS.md"
    assert path.exists()

    text = path.read_text(encoding="utf-8", errors="ignore").lower()

    assert "portfolio" in text
    assert "validation" in text or "limitation" in text


def test_second_domain_generalization_is_documented():
    path = ROOT / "docs" / "SWISS_QR_BILL_SECOND_DOMAIN_CASE.md"
    assert path.exists()

    text = path.read_text(encoding="utf-8", errors="ignore").lower()

    assert "swiss" in text
    assert "qr" in text
    assert "compliance" in text


def test_claim_hygiene_public_document_replaces_old_auto_score_story():
    new_path = ROOT / "docs" / "CLAIM_HYGIENE_SCANNER.md"
    old_path = ROOT / "docs" / "AUTO_SCORE_TO_CLAIM_SCANNER_STORY.md"

    assert new_path.exists()
    assert not old_path.exists()

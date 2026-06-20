from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_claim_hygiene_scanner_story_is_documented():
    path = ROOT / "docs" / "CLAIM_HYGIENE_SCANNER.md"
    text = path.read_text(encoding="utf-8", errors="ignore")

    required_phrases = [
        "Claim Hygiene Scanner",
        "risk-aware communication",
        "human-in-the-loop review",
        "evaluation discipline",
        "enterprise readiness judgment",
        "not a production legal review system",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_old_auto_score_story_document_is_not_public():
    old_path = ROOT / "docs" / "AUTO_SCORE_TO_CLAIM_SCANNER_STORY.md"
    assert not old_path.exists()

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_payments_companion_summary_is_present_but_not_a_workflow():
    companion_dir = ROOT / "companion_playbooks" / "ai_payments_compliance"
    summary = ROOT / "docs" / "AI_PAYMENTS_COMPLIANCE_MIT_COURSE_COMPANION.md"
    readme = companion_dir / "README.md"

    assert companion_dir.exists()
    assert summary.exists()
    assert readme.exists()

    app_files = list((ROOT / "ui").glob("*.py")) + [ROOT / "app.py"]
    app_text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore") for path in app_files
    )

    assert "AI Payments Compliance Assistant" not in app_text
    assert "payments compliance" not in app_text.lower()

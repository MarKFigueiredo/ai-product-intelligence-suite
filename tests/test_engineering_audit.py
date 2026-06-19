from pathlib import Path

from scripts import engineering_audit


def test_engineering_audit_renders_report_sections():
    report = engineering_audit.render_markdown()

    expected_sections = [
        "# Engineering Hardening Report",
        "## Summary",
        "## Largest Python files",
        "## Largest Markdown files",
        "## Large functions",
        "## Streamlit usage",
        "## Tone findings",
        "## Suspicious filenames",
        "## Recommended next refactor",
    ]

    for section in expected_sections:
        assert section in report


def test_engineering_audit_uses_tracked_files_only():
    files = engineering_audit.tracked_files()

    assert files
    assert all(Path(path).is_absolute() for path in files)
    assert not any(".venv" in Path(path).parts for path in files)
    assert not any(".git" in Path(path).parts for path in files)

from pathlib import Path


def test_version_file_exists_and_is_current_public_version():
    version = Path("VERSION").read_text(encoding="utf-8").strip()

    assert version == "1.04"


def test_readme_uses_version_badge_and_current_version():
    version = Path("VERSION").read_text(encoding="utf-8").strip()
    readme = Path("README.md").read_text(encoding="utf-8")

    assert f"version-{version}-blue" in readme
    assert "actions/workflows/ci.yml/badge.svg" in readme
    assert ".github/badges/coverage.svg" in readme
    assert "ai-app-intelligence-suite.streamlit.app" in readme


def test_public_docs_do_not_reference_old_or_invalid_versions():
    forbidden = [
        "v" + "1.01",
        "v" + "1.02",
        "v" + "1.03",
        "v" + "11.02",
        "v" + "20",
        "V" + "20",
        "V" + "11.02",
    ]

    allowed_files = {
        "CHANGELOG.md",
        "tests/test_version_single_source.py",
    }

    findings = []

    for path in Path(".").rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts or ".venv" in path.parts:
            continue
        if path.as_posix() in allowed_files:
            continue
        if path.suffix not in {".md", ".py", ".toml", ".yml", ".yaml"}:
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        for token in forbidden:
            if token in text:
                findings.append(f"{path}: {token}")

    assert findings == []

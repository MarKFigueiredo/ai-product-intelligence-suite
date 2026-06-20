from __future__ import annotations

import re
from pathlib import Path

from config import APP_NAME, APP_VERSION, CORE_REVIEW_WORKFLOWS, REVIEW_MODES, WORKFLOWS

RUNTIME_PATHS = [Path("app.py"), Path("config.py"), Path("ui"), Path("modules"), Path("services"), Path("assets/screenshots")]
STALE_SUITE_RE = re.compile(r"AI Product Intelligence Suite v\d+(?:\.\d+)?", re.I)


def iter_runtime_files():
    for root in RUNTIME_PATHS:
        if root.is_file():
            yield root
        elif root.exists():
            for path in root.rglob("*"):
                if path.suffix in {".py", ".svg"} and "__pycache__" not in path.parts:
                    yield path


def test_v24_app_name_is_single_source_for_audit_exports():
    visual_components = Path("ui/visual_components.py").read_text(encoding="utf-8")
    assert APP_VERSION == "1.04"
    assert APP_NAME.endswith(APP_VERSION)
    assert "from config import APP_NAME" in visual_components
    assert '"suite": APP_NAME' in visual_components
    assert "AI Product Intelligence Suite v16" not in visual_components
    assert "AI Product Intelligence Suite v22" not in visual_components
    assert "AI Product Intelligence Suite 1.04" in APP_NAME


def test_runtime_files_do_not_contain_stale_suite_version_labels():
    offenders = []
    for path in iter_runtime_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        if STALE_SUITE_RE.search(text):
            offenders.append(str(path))
    assert offenders == []


def test_sidebar_defaults_to_focused_review_path_not_full_artifact_map():
    assert "Focused review path" in REVIEW_MODES
    assert "Full artifact map" in REVIEW_MODES
    assert REVIEW_MODES["Focused review path"] == CORE_REVIEW_WORKFLOWS
    assert len(CORE_REVIEW_WORKFLOWS) < len(WORKFLOWS)
    assert len(CORE_REVIEW_WORKFLOWS) <= 7

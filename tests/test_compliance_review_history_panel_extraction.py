from pathlib import Path


def test_review_history_panel_exists_in_ui_layer():
    panel_text = Path("ui/compliance_review_history_panel.py").read_text(encoding="utf-8")

    assert "def render_reviewer_and_run_history_panel" in panel_text
    assert "streamlit" in panel_text or "st." in panel_text


def test_compliance_studio_keeps_backward_compatible_review_history_wrapper():
    module_text = Path("modules/compliance_studio.py").read_text(encoding="utf-8")

    assert "from ui.compliance_review_history_panel import render_reviewer_and_run_history_panel" in module_text
    assert "def render_reviewer_and_run_history(*args, **kwargs):" in module_text
    assert "return render_reviewer_and_run_history_panel(*args, **kwargs)" in module_text


def test_review_history_panel_is_not_in_service_layer():
    service_files = list(Path("services").glob("*review*history*.py"))

    assert service_files == []

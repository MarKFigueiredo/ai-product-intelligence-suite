from pathlib import Path

from services import openai_service


def test_openai_service_has_no_ui_framework_dependency():
    service_text = Path("services/openai_service.py").read_text(encoding="utf-8")

    assert "streamlit" not in service_text
    assert "st." not in service_text
    assert "render_openai_error" not in service_text


def test_openai_service_reads_api_key_from_environment(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    assert openai_service.get_api_key() == "test-key"


def test_openai_service_accepts_explicit_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    client = openai_service.get_client(api_key="explicit-test-key")

    assert client is not None


def test_app_initializes_streamlit_secrets_bridge():
    app_text = Path("app.py").read_text(encoding="utf-8")

    assert "from ui.streamlit_secrets import sync_streamlit_secrets_to_env" in app_text
    assert "sync_streamlit_secrets_to_env()" in app_text


def test_openai_error_handler_owns_ui_error_rendering():
    ui_text = Path("ui/openai_error_handler.py").read_text(encoding="utf-8")

    assert "import streamlit as st" in ui_text
    assert "def render_openai_error" in ui_text

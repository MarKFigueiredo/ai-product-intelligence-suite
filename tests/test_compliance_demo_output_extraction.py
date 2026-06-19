from pathlib import Path

from services.compliance_demo_output import build_demo_output


def test_compliance_demo_output_service_is_ui_free():
    service_text = Path("services/compliance_demo_output.py").read_text(encoding="utf-8")

    assert "streamlit" not in service_text
    assert "st." not in service_text
    assert "from ui." not in service_text
    assert "import ui." not in service_text


def test_compliance_demo_output_builder_returns_non_empty_dict():
    output = build_demo_output()

    assert isinstance(output, dict)
    assert output


def test_compliance_studio_keeps_backward_compatible_demo_output_wrapper():
    module_text = Path("modules/compliance_studio.py").read_text(encoding="utf-8")

    assert "from services.compliance_demo_output import build_demo_output" in module_text
    assert "def demo_output(*args, **kwargs):" in module_text
    assert "return build_demo_output(*args, **kwargs)" in module_text

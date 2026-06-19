from pathlib import Path


def test_visual_components_do_not_use_custom_html_for_kpi_or_timeline():
    source = Path("ui/visual_components.py").read_text()
    kpi_start = source.index("def render_kpi_grid")
    timeline_start = source.index("def render_vertical_timeline")
    compact_start = source.index("def render_compact_card_grid")
    kpi_source = source[kpi_start:timeline_start]
    timeline_source = source[timeline_start:compact_start]
    assert "kpi-card" not in kpi_source
    assert "compact-grid" not in kpi_source
    assert "timeline-node" not in timeline_source
    assert "timeline-wrap" not in timeline_source
    assert "st.container(border=True)" in kpi_source
    assert "st.container(border=True)" in timeline_source


def test_public_version_is_104():
    config = Path("config.py").read_text()
    assert 'APP_VERSION = "1.04"' in config

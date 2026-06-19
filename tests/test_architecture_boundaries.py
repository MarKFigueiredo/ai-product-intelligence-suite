from scripts import architecture_guard


def test_core_layer_has_no_streamlit_dependency():
    findings = architecture_guard.boundary_findings()

    core_violations = [
        item for item in findings
        if item.layer == "core" and item.status == "violation"
    ]

    assert core_violations == []


def test_no_new_service_ui_leakage_outside_known_debt_allowlist():
    hard_violations = architecture_guard.violations()

    assert hard_violations == []


def test_architecture_report_contains_boundary_policy_sections():
    report = architecture_guard.render_markdown()

    expected_sections = [
        "# Architecture Boundary Report",
        "## Boundary policy",
        "## Summary",
        "## Violations",
        "## Known service UI debt",
        "## Recommended next refactor order",
    ]

    for section in expected_sections:
        assert section in report

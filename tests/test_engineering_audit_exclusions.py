from scripts import engineering_audit


def test_engineering_audit_excludes_generated_report_from_scan_inputs():
    scanned = {path.relative_to(engineering_audit.ROOT).as_posix() for path in engineering_audit.tracked_files()}

    assert "docs/ENGINEERING_HARDENING_REPORT.md" not in scanned

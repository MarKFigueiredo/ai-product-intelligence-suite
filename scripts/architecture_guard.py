from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# Existing service files with known UI references. These are allowed for now so
# the guard can be introduced without a risky refactor. Future sprints should
# remove these entries one by one.
LEGACY_SERVICE_UI_EXCEPTIONS = {
    "services/citation_verifier.py",
    "services/evidence_report_service.py",
    "services/usage_metrics_service.py",
}

UI_ALLOWED_PREFIXES = (
    "app.py",
    "ui/",
    "modules/",
    "tests/",
    "scripts/",
)

UI_PATTERNS = (
    re.compile(r"\bimport\s+streamlit\b"),
    re.compile(r"\bfrom\s+streamlit\b"),
    re.compile(r"\bst\."),
)


@dataclass(frozen=True)
class BoundaryFinding:
    path: str
    layer: str
    issue: str
    status: str


def tracked_python_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "*.py"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return [ROOT / line.strip() for line in result.stdout.splitlines() if line.strip()]


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def contains_streamlit_reference(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return any(pattern.search(text) for pattern in UI_PATTERNS)


def classify_layer(rel_path: str) -> str:
    if rel_path.startswith("core/"):
        return "core"
    if rel_path.startswith("services/"):
        return "service"
    if rel_path.startswith("ui/"):
        return "ui"
    if rel_path.startswith("modules/"):
        return "module"
    if rel_path.startswith("tests/"):
        return "test"
    if rel_path == "app.py":
        return "app"
    if rel_path.startswith("scripts/"):
        return "script"
    return "other"


def is_ui_allowed(rel_path: str) -> bool:
    if rel_path in LEGACY_SERVICE_UI_EXCEPTIONS:
        return True
    if rel_path == "app.py":
        return True
    return any(rel_path.startswith(prefix) for prefix in UI_ALLOWED_PREFIXES if prefix.endswith("/"))


def boundary_findings() -> list[BoundaryFinding]:
    findings: list[BoundaryFinding] = []

    for path in tracked_python_files():
        rel = relative(path)
        layer = classify_layer(rel)
        has_streamlit = contains_streamlit_reference(path)

        if layer == "core" and has_streamlit:
            findings.append(BoundaryFinding(rel, layer, "Core layer references Streamlit", "violation"))
            continue

        if layer == "service" and has_streamlit:
            if rel in LEGACY_SERVICE_UI_EXCEPTIONS:
                findings.append(BoundaryFinding(rel, layer, "Legacy service references Streamlit", "known debt"))
            else:
                findings.append(BoundaryFinding(rel, layer, "Service layer references Streamlit", "violation"))
            continue

        if has_streamlit and not is_ui_allowed(rel):
            findings.append(BoundaryFinding(rel, layer, "Unexpected Streamlit reference", "violation"))

    return sorted(findings, key=lambda item: (item.status, item.layer, item.path))


def violations() -> list[BoundaryFinding]:
    return [item for item in boundary_findings() if item.status == "violation"]


def known_debt() -> list[BoundaryFinding]:
    return [item for item in boundary_findings() if item.status == "known debt"]


def render_markdown() -> str:
    all_findings = boundary_findings()
    hard_violations = violations()
    debt = known_debt()

    lines: list[str] = [
        "# Architecture Boundary Report",
        "",
        "This report checks tracked Python files for UI-layer leakage.",
        "",
        "## Boundary policy",
        "",
        "- `core/` must not import or reference Streamlit.",
        "- New `services/` files must not import or reference Streamlit.",
        "- `app.py`, `ui/` and `modules/` are the current presentation surfaces.",
        "- Existing service UI references are tracked as known debt until removed in later sprints.",
        "",
        "## Summary",
        "",
        f"- Violations: {len(hard_violations)}",
        f"- Known service UI debt files: {len(debt)}",
        "",
        "## Violations",
        "",
    ]

    if hard_violations:
        lines += ["| File | Layer | Issue |", "|---|---|---|"]
        for item in hard_violations:
            lines.append(f"| `{item.path}` | {item.layer} | {item.issue} |")
    else:
        lines.append("No architecture boundary violations found.")

    lines += ["", "## Known service UI debt", ""]

    if debt:
        lines += ["| File | Issue | Next action |", "|---|---|---|"]
        for item in debt:
            lines.append(
                f"| `{item.path}` | {item.issue} | Move UI formatting/rendering out of the service layer. |"
            )
    else:
        lines.append("No known service UI debt found.")

    lines += [
        "",
        "## Recommended next refactor order",
        "",
        "1. Remove Streamlit references from `services/evidence_report_service.py`.",
        "2. Remove Streamlit references from `services/citation_verifier.py`.",
        "3. Remove Streamlit references from `services/usage_metrics_service.py`.",
        "4. Then split `modules/compliance_studio.py` into smaller UI wrappers and pure services.",
        "",
    ]

    return "\n".join(lines)


def write_report() -> Path:
    output_path = ROOT / "docs" / "ARCHITECTURE_BOUNDARY_REPORT.md"
    output_path.write_text(render_markdown() + "\n", encoding="utf-8")
    return output_path


def main() -> None:
    output_path = write_report()
    print(output_path.relative_to(ROOT))

    hard_violations = violations()
    if hard_violations:
        print("Architecture boundary violations found:")
        for finding in hard_violations:
            print(f"- {finding.path}: {finding.issue}")


if __name__ == "__main__":
    main()

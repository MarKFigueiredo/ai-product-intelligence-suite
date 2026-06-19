from __future__ import annotations

import ast
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PYTHON_LARGE_FILE_LINES = 400
PYTHON_LARGE_FUNCTION_LINES = 80
MARKDOWN_LARGE_FILE_LINES = 220

UI_ALLOWED_PREFIXES = (
    "app.py",
    "ui/",
    "modules/compliance_studio.py",  # temporary allowlist until this file is split
)


@dataclass(frozen=True)
class FileMetric:
    path: str
    lines: int


@dataclass(frozen=True)
class FunctionMetric:
    path: str
    name: str
    line_start: int
    line_end: int
    lines: int


@dataclass(frozen=True)
class StreamlitUsage:
    path: str
    count: int
    allowed: bool


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return [ROOT / line.strip() for line in result.stdout.splitlines() if line.strip()]


def line_count(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
    except OSError:
        return 0


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def largest_files(suffix: str, threshold: int) -> list[FileMetric]:
    metrics: list[FileMetric] = []
    for path in tracked_files():
        if path.suffix != suffix:
            continue
        lines = line_count(path)
        if lines >= threshold:
            metrics.append(FileMetric(relative(path), lines))
    return sorted(metrics, key=lambda item: item.lines, reverse=True)


def large_functions() -> list[FunctionMetric]:
    metrics: list[FunctionMetric] = []

    for path in tracked_files():
        if path.suffix != ".py":
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not hasattr(node, "end_lineno") or node.end_lineno is None:
                continue

            lines = int(node.end_lineno) - int(node.lineno) + 1
            if lines >= PYTHON_LARGE_FUNCTION_LINES:
                metrics.append(
                    FunctionMetric(
                        path=relative(path),
                        name=node.name,
                        line_start=int(node.lineno),
                        line_end=int(node.end_lineno),
                        lines=lines,
                    )
                )

    return sorted(metrics, key=lambda item: item.lines, reverse=True)


def streamlit_usage() -> list[StreamlitUsage]:
    usage: list[StreamlitUsage] = []

    for path in tracked_files():
        if path.suffix != ".py":
            continue

        rel = relative(path)
        text = path.read_text(encoding="utf-8", errors="ignore")
        count = len(re.findall(r"\bst\.", text))
        if count == 0:
            continue

        allowed = rel == "app.py" or any(rel.startswith(prefix) for prefix in UI_ALLOWED_PREFIXES if prefix.endswith("/"))
        allowed = allowed or rel in UI_ALLOWED_PREFIXES
        usage.append(StreamlitUsage(rel, count, allowed))

    return sorted(usage, key=lambda item: item.count, reverse=True)


def tone_scan() -> list[tuple[str, int, str]]:
    # Keep this strict and review-oriented. Do not flag ordinary domain terms such as "generated".
    pattern = re.compile(
        r"\b(world[- ]class|top[- ]tier|best[- ]in[- ]class|elite|brilliant|"
        r"above average|classe mundial|this candidate|my skills|i design|i built|i created)\b",
        re.IGNORECASE,
    )

    findings: list[tuple[str, int, str]] = []
    for path in tracked_files():
        if path.suffix not in {".md", ".html"}:
            continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
            if pattern.search(line):
                findings.append((relative(path), line_no, line.strip()))
    return findings


def suspicious_filenames() -> list[str]:
    pattern = re.compile(
        r"(WORLD|PREMIUM|INTERVIEW|LINKEDIN|START_HERE|UX_DENSITY_REDUCTION_V\d+|"
        r"V16|V17|V18|V19|V21|V22|V23|V24|V25|AUTO_SCORE)",
        re.IGNORECASE,
    )
    return sorted(relative(path) for path in tracked_files() if pattern.search(relative(path)))


def render_markdown() -> str:
    py_files = largest_files(".py", PYTHON_LARGE_FILE_LINES)
    md_files = largest_files(".md", MARKDOWN_LARGE_FILE_LINES)
    functions = large_functions()
    st_usage = streamlit_usage()
    tone = tone_scan()
    filenames = suspicious_filenames()

    lines: list[str] = [
        "# Engineering Hardening Report",
        "",
        "This report is generated from tracked repository files only. It excludes `.venv`, local caches and untracked scratch files.",
        "",
        "## Summary",
        "",
        f"- Python files over {PYTHON_LARGE_FILE_LINES} lines: {len(py_files)}",
        f"- Markdown files over {MARKDOWN_LARGE_FILE_LINES} lines: {len(md_files)}",
        f"- Functions over {PYTHON_LARGE_FUNCTION_LINES} lines: {len(functions)}",
        f"- Files using Streamlit: {len(st_usage)}",
        f"- Tone findings: {len(tone)}",
        f"- Suspicious filenames: {len(filenames)}",
        "",
        "## Largest Python files",
        "",
    ]

    if py_files:
        lines += ["| File | Lines |", "|---|---:|"]
        lines += [f"| `{item.path}` | {item.lines} |" for item in py_files]
    else:
        lines.append("No Python files above threshold.")

    lines += ["", "## Largest Markdown files", ""]
    if md_files:
        lines += ["| File | Lines |", "|---|---:|"]
        lines += [f"| `{item.path}` | {item.lines} |" for item in md_files]
    else:
        lines.append("No Markdown files above threshold.")

    lines += ["", "## Large functions", ""]
    if functions:
        lines += ["| File | Function | Lines | Location |", "|---|---|---:|---|"]
        lines += [
            f"| `{item.path}` | `{item.name}` | {item.lines} | L{item.line_start}-L{item.line_end} |"
            for item in functions
        ]
    else:
        lines.append("No functions above threshold.")

    lines += ["", "## Streamlit usage", ""]
    if st_usage:
        lines += ["| File | `st.` count | Current status |", "|---|---:|---|"]
        for item in st_usage:
            status = "allowed UI surface" if item.allowed else "review for UI leakage"
            lines.append(f"| `{item.path}` | {item.count} | {status} |")
    else:
        lines.append("No Streamlit usage found.")

    lines += ["", "## Tone findings", ""]
    if tone:
        lines += ["| File | Line | Text |", "|---|---:|---|"]
        for path, line_no, text in tone:
            safe_text = text.replace("|", "\\|")
            lines.append(f"| `{path}` | {line_no} | {safe_text} |")
    else:
        lines.append("No promotional tone findings found by the strict scanner.")

    lines += ["", "## Suspicious filenames", ""]
    if filenames:
        lines += [f"- `{name}`" for name in filenames]
    else:
        lines.append("No suspicious filenames found by the strict scanner.")

    lines += [
        "",
        "## Recommended next refactor",
        "",
        "1. Split `modules/compliance_studio.py` into a Streamlit page wrapper and pure services.",
        "2. Keep `ui/` and `app.py` as presentation surfaces only.",
        "3. Add domain dataclasses for obligations, evidence, QA cases, release-risk findings and audit summaries.",
        "4. Convert selected service outputs from loosely-shaped dictionaries to typed objects.",
        "5. Add behavior tests for gates: missing source, unsupported claim, missing negative QA and stale evidence.",
        "",
    ]

    return "\n".join(lines)


def main() -> None:
    report = render_markdown()
    output_path = ROOT / "docs" / "ENGINEERING_HARDENING_REPORT.md"
    output_path.write_text(report + "\n", encoding="utf-8")
    print(output_path.relative_to(ROOT))


if __name__ == "__main__":
    main()

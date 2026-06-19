from __future__ import annotations

import ast
import importlib
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SOURCE = ROOT / "modules" / "compliance_studio.py"
TARGET = ROOT / "ui" / "compliance_review_history_panel.py"
BACKUP = ROOT / ".local_refactor_backup" / "compliance_studio.py.before_review_history_extract"

OLD_FUNCTION = "render_reviewer_and_run_history"
NEW_FUNCTION = "render_reviewer_and_run_history_panel"


def line_span(node: ast.AST) -> tuple[int, int]:
    start = getattr(node, "lineno", None)
    end = getattr(node, "end_lineno", None)
    if start is None or end is None:
        raise ValueError(f"Cannot locate source lines for {node!r}")
    return int(start), int(end)


def find_top_level_function(tree: ast.Module, name: str) -> ast.FunctionDef:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise ValueError(f"Missing expected top-level function in {SOURCE}: {name}")


def extract_imports(tree: ast.Module, lines: list[str]) -> list[str]:
    imports: list[str] = []
    seen: set[str] = set()

    for node in tree.body:
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue

        start, end = line_span(node)
        block = "\n".join(lines[start - 1:end]).rstrip()

        if "modules.compliance_studio" in block:
            continue

        if block not in seen:
            imports.append(block)
            seen.add(block)

    return imports


def build_ui_source(lines: list[str], tree: ast.Module, function_node: ast.FunctionDef) -> str:
    imports = extract_imports(tree, lines)

    start, end = line_span(function_node)
    function_block = "\n".join(lines[start - 1:end]).rstrip()
    function_block = function_block.replace(
        f"def {OLD_FUNCTION}(",
        f"def {NEW_FUNCTION}(",
        1,
    )

    parts = [
        '"""Reviewer and run-history UI panel for the compliance studio."""',
        "",
        "from __future__ import annotations",
        "",
    ]

    if imports:
        parts.extend(imports)
        parts.append("")

    parts.append(function_block)
    parts.append("")

    return "\n".join(parts)


def insert_import(source_text: str) -> str:
    import_line = "from ui.compliance_review_history_panel import render_reviewer_and_run_history_panel"

    if import_line in source_text:
        return source_text

    tree = ast.parse(source_text)
    lines = source_text.splitlines()

    import_end_lines: list[int] = []

    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            end = getattr(node, "end_lineno", None)
            if end is not None:
                import_end_lines.append(int(end))

    insert_at = max(import_end_lines) if import_end_lines else 0
    lines.insert(insert_at, import_line)

    return "\n".join(lines) + "\n"


def replace_function_with_wrapper(source_text: str, function_node: ast.FunctionDef) -> str:
    lines = source_text.splitlines()
    start, end = line_span(function_node)

    wrapper = (
        f"def {OLD_FUNCTION}(*args, **kwargs):\n"
        f'    """Backward-compatible wrapper for the extracted reviewer/run-history panel."""\n'
        f"    return {NEW_FUNCTION}(*args, **kwargs)\n"
    )

    lines[start - 1:end] = wrapper.rstrip().splitlines()
    return "\n".join(lines) + "\n"


def restore() -> None:
    if BACKUP.exists():
        shutil.copyfile(BACKUP, SOURCE)
    if TARGET.exists():
        TARGET.unlink()


def validate() -> None:
    subprocess.run(
        ["python", "-m", "compileall", "modules/compliance_studio.py", "ui/compliance_review_history_panel.py"],
        cwd=ROOT,
        check=True,
    )

    module = importlib.import_module("ui.compliance_review_history_panel")
    if not hasattr(module, NEW_FUNCTION):
        raise ValueError(f"Missing {NEW_FUNCTION} in extracted UI module.")


def main() -> None:
    BACKUP.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, BACKUP)

    if TARGET.exists():
        raise SystemExit(f"Target already exists: {TARGET}. Remove it before rerunning.")

    try:
        source_text = SOURCE.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source_text)
        function_node = find_top_level_function(tree, OLD_FUNCTION)
        lines = source_text.splitlines()

        TARGET.write_text(build_ui_source(lines, tree, function_node), encoding="utf-8")

        updated_source = replace_function_with_wrapper(source_text, function_node)
        updated_source = insert_import(updated_source)
        SOURCE.write_text(updated_source, encoding="utf-8")

        validate()

    except Exception as exc:
        restore()
        raise SystemExit(f"Extraction failed and was restored: {type(exc).__name__}: {exc}") from exc

    print(f"Created {TARGET.relative_to(ROOT)}")
    print(f"Updated {SOURCE.relative_to(ROOT)}")
    print(f"Extracted: {OLD_FUNCTION} -> ui.compliance_review_history_panel.{NEW_FUNCTION}")


if __name__ == "__main__":
    main()

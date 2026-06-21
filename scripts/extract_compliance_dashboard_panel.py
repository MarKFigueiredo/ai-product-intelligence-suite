from __future__ import annotations

import ast
import builtins
import importlib
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SOURCE = ROOT / "modules" / "compliance_studio.py"
TARGET = ROOT / "ui" / "compliance_dashboard_panel.py"
BACKUP = ROOT / ".local_refactor_backup" / "compliance_studio.py.before_dashboard_extract"

OLD_FUNCTION = "render_compliance_dashboard"
NEW_FUNCTION = "render_compliance_dashboard_panel"

SAFE_GLOBAL_NAMES = {
    "st",
    "Path",
    "Dict",
    "Any",
    "List",
    "Optional",
    "Tuple",
    "Mapping",
    "Sequence",
}


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


def extract_imports(tree: ast.Module, lines: list[str]) -> tuple[list[str], set[str]]:
    imports: list[str] = []
    imported_names: set[str] = set()
    seen: set[str] = set()

    for node in tree.body:
        if isinstance(node, ast.Import):
            start, end = line_span(node)
            block = "\n".join(lines[start - 1:end]).rstrip()

            if "modules.compliance_studio" in block:
                continue

            for alias in node.names:
                imported_names.add(alias.asname or alias.name.split(".")[0])

            if block not in seen:
                imports.append(block)
                seen.add(block)

        elif isinstance(node, ast.ImportFrom):
            start, end = line_span(node)
            block = "\n".join(lines[start - 1:end]).rstrip()

            if "modules.compliance_studio" in block:
                continue

            for alias in node.names:
                if alias.name == "*":
                    continue
                imported_names.add(alias.asname or alias.name)

            if block not in seen:
                imports.append(block)
                seen.add(block)

    return imports, imported_names


def top_level_defined_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = []
            if isinstance(node, ast.Assign):
                targets = list(node.targets)
            else:
                targets = [node.target]
            for target in targets:
                for child in ast.walk(target):
                    if isinstance(child, ast.Name):
                        names.add(child.id)

    return names


class LocalNameCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.names: set[str] = set()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        for arg in list(node.args.posonlyargs) + list(node.args.args) + list(node.args.kwonlyargs):
            self.names.add(arg.arg)
        if node.args.vararg:
            self.names.add(node.args.vararg.arg)
        if node.args.kwarg:
            self.names.add(node.args.kwarg.arg)

        for item in node.body:
            self.visit(item)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            self.names.add(node.id)

    def visit_comprehension(self, node: ast.comprehension) -> None:
        self.visit(node.target)
        self.visit(node.iter)
        for condition in node.ifs:
            self.visit(condition)


class LoadedNameCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.names: set[str] = set()

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            self.names.add(node.id)


def risky_local_dependencies(
    tree: ast.Module,
    function_node: ast.FunctionDef,
    imported_names: set[str],
) -> set[str]:
    top_level_names = top_level_defined_names(tree)
    top_level_names.discard(OLD_FUNCTION)

    local_collector = LocalNameCollector()
    local_collector.visit(function_node)

    loaded_collector = LoadedNameCollector()
    loaded_collector.visit(function_node)

    builtin_names = set(dir(builtins))

    external_reads = (
        loaded_collector.names
        - local_collector.names
        - imported_names
        - builtin_names
        - SAFE_GLOBAL_NAMES
    )

    return external_reads & top_level_names


def build_ui_source(lines: list[str], tree: ast.Module, function_node: ast.FunctionDef, imports: list[str]) -> str:
    start, end = line_span(function_node)
    function_block = "\n".join(lines[start - 1:end]).rstrip()
    function_block = function_block.replace(
        f"def {OLD_FUNCTION}(",
        f"def {NEW_FUNCTION}(",
        1,
    )

    parts = [
        '"""Compliance dashboard UI panel.',
        "",
        "This module keeps Streamlit rendering for the compliance dashboard",
        "separate from the main compliance studio page orchestrator.",
        '"""',
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
    import_line = "from ui.compliance_dashboard_panel import render_compliance_dashboard_panel"

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
        f'    """Backward-compatible wrapper for the extracted compliance dashboard panel."""\n'
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
        ["python", "-m", "compileall", "modules/compliance_studio.py", "ui/compliance_dashboard_panel.py"],
        cwd=ROOT,
        check=True,
    )

    module = importlib.import_module("ui.compliance_dashboard_panel")
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
        lines = source_text.splitlines()
        function_node = find_top_level_function(tree, OLD_FUNCTION)
        imports, imported_names = extract_imports(tree, lines)

        risky = risky_local_dependencies(tree, function_node, imported_names)
        if risky:
            details = ", ".join(sorted(risky))
            raise ValueError(
                "Extraction is not safe because the function reads local module names: "
                f"{details}. Choose a smaller cut or move those dependencies first."
            )

        TARGET.write_text(build_ui_source(lines, tree, function_node, imports), encoding="utf-8")

        updated_source = replace_function_with_wrapper(source_text, function_node)
        updated_source = insert_import(updated_source)
        SOURCE.write_text(updated_source, encoding="utf-8")

        validate()

    except Exception as exc:
        restore()
        raise SystemExit(f"Extraction failed and was restored: {type(exc).__name__}: {exc}") from exc

    print(f"Created {TARGET.relative_to(ROOT)}")
    print(f"Updated {SOURCE.relative_to(ROOT)}")
    print(f"Extracted: {OLD_FUNCTION} -> ui.compliance_dashboard_panel.{NEW_FUNCTION}")


if __name__ == "__main__":
    main()

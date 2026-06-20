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
TARGET = ROOT / "services" / "compliance_demo_output.py"
BACKUP = ROOT / ".local_refactor_backup" / "compliance_studio.py.before_demo_output_extract"

OLD_FUNCTION = "demo_output"
NEW_FUNCTION = "build_demo_output"


def _line_span(node: ast.AST) -> tuple[int, int]:
    start = getattr(node, "lineno", None)
    end = getattr(node, "end_lineno", None)
    if start is None or end is None:
        raise ValueError(f"Cannot locate source lines for {node!r}")
    return int(start), int(end)


def _find_top_level_function(tree: ast.Module, name: str) -> ast.FunctionDef:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise ValueError(f"Missing expected top-level function in {SOURCE}: {name}")


def _extract_top_level_imports(tree: ast.Module, lines: list[str]) -> list[str]:
    imports: list[str] = []
    seen: set[str] = set()

    for node in tree.body:
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue

        start, end = _line_span(node)
        block = "\n".join(lines[start - 1 : end]).rstrip()

        # Pure service must not import Streamlit or UI rendering helpers.
        lowered = block.lower()
        if "streamlit" in lowered or "from ui." in lowered or "import ui." in lowered:
            continue

        if block not in seen:
            imports.append(block)
            seen.add(block)

    return imports


def _rename_function_source(source: str) -> str:
    return source.replace(f"def {OLD_FUNCTION}(", f"def {NEW_FUNCTION}(", 1)


def _build_service_source(lines: list[str], tree: ast.Module, function_node: ast.FunctionDef) -> str:
    imports = _extract_top_level_imports(tree, lines)

    start, end = _line_span(function_node)
    function_block = "\n".join(lines[start - 1 : end]).rstrip()
    function_block = _rename_function_source(function_block)

    service_lines = [
        '"""Pure demo-output artifact builder for the compliance studio.',
        "",
        "This module was extracted from the Streamlit compliance studio page so",
        "the demo artifact payload can be tested independently from UI rendering.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
    ]

    if imports:
        service_lines.extend(imports)
        service_lines.append("")

    service_lines.append(function_block)
    service_lines.append("")

    text = "\n".join(service_lines)

    forbidden = ["streamlit", "st.", "from ui.", "import ui."]
    for token in forbidden:
        if token in text:
            raise ValueError(f"Extraction would create a non-pure service containing {token!r}")

    return text


def _insert_import(source_text: str) -> str:
    import_line = "from services.compliance_demo_output import build_demo_output"

    if import_line in source_text:
        return source_text

    lines = source_text.splitlines()
    insert_at = 0

    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            insert_at = idx + 1

    lines.insert(insert_at, import_line)
    return "\n".join(lines) + "\n"


def _replace_function_with_wrapper(source_text: str, function_node: ast.FunctionDef) -> str:
    lines = source_text.splitlines()
    start, end = _line_span(function_node)

    wrapper = (
        f"def {OLD_FUNCTION}(*args, **kwargs):\n"
        f'    """Backward-compatible wrapper for the extracted demo output builder."""\n'
        f"    return {NEW_FUNCTION}(*args, **kwargs)\n"
    )

    lines[start - 1 : end] = wrapper.rstrip().splitlines()
    return "\n".join(lines) + "\n"


def _validate_extraction() -> None:
    subprocess.run(["python", "-m", "compileall", "services/compliance_demo_output.py"], cwd=ROOT, check=True)

    module = importlib.import_module("services.compliance_demo_output")
    builder = getattr(module, NEW_FUNCTION)
    result = builder()

    if not isinstance(result, dict):
        raise ValueError(f"{NEW_FUNCTION}() must return dict, got {type(result)!r}")

    if not result:
        raise ValueError(f"{NEW_FUNCTION}() returned an empty dict")


def _restore() -> None:
    if BACKUP.exists():
        shutil.copyfile(BACKUP, SOURCE)
    if TARGET.exists():
        TARGET.unlink()


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Missing source file: {SOURCE}")

    BACKUP.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, BACKUP)

    if TARGET.exists():
        raise SystemExit(f"Target already exists: {TARGET}. Inspect before rerunning.")

    try:
        source_text = SOURCE.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source_text)
        function_node = _find_top_level_function(tree, OLD_FUNCTION)
        lines = source_text.splitlines()

        service_text = _build_service_source(lines, tree, function_node)
        updated_source = _replace_function_with_wrapper(source_text, function_node)
        updated_source = _insert_import(updated_source)

        TARGET.write_text(service_text, encoding="utf-8")
        SOURCE.write_text(updated_source, encoding="utf-8")

        _validate_extraction()

    except Exception as exc:
        _restore()
        raise SystemExit(f"Extraction failed and was restored: {type(exc).__name__}: {exc}") from exc

    print(f"Created {TARGET.relative_to(ROOT)}")
    print(f"Updated {SOURCE.relative_to(ROOT)}")
    print(f"Extracted: {OLD_FUNCTION} -> services.compliance_demo_output.{NEW_FUNCTION}")


if __name__ == "__main__":
    main()

"""Export helpers for Markdown, HTML, and CSV."""
from __future__ import annotations

import csv
import html
import io
import re
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd


def safe_filename(text: str, suffix: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", text.lower()).strip("_") or "ai_pm_output"
    return f"{cleaned}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{suffix}"


def rows_to_csv_bytes(rows: List[Dict[str, Any]]) -> bytes:
    if not rows:
        return b""
    output = io.StringIO()
    fieldnames = list(rows[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def rows_to_df(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows or [])


def markdown_to_html_document(markdown_text: str, title: str) -> str:
    escaped = html.escape(markdown_text or "")
    body = escaped.replace("\n", "<br>\n")
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>
body {{ font-family: Arial, sans-serif; max-width: 980px; margin: 40px auto; line-height: 1.55; color: #111827; }}
h1, h2, h3 {{ color: #0f172a; }}
.box {{ background: #f8fafc; padding: 18px; border-radius: 12px; border: 1px solid #e5e7eb; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #e5e7eb; padding: 8px; }}
</style>
</head>
<body>
<h1>{html.escape(title)}</h1>
<div class="box">{body}</div>
</body>
</html>"""


def dict_to_markdown(data: Dict[str, Any], title: str) -> str:
    lines = [f"# {title}", ""]
    for key, value in data.items():
        heading = str(key).replace("_", " ").title()
        lines.append(f"## {heading}")
        if isinstance(value, list):
            if value and isinstance(value[0], dict):
                headers = list(value[0].keys())
                lines.append("| " + " | ".join(headers) + " |")
                lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
                for row in value:
                    lines.append("| " + " | ".join(str(row.get(h, "")).replace("\n", " ") for h in headers) + " |")
            else:
                for item in value:
                    lines.append(f"- {item}")
        elif isinstance(value, dict):
            for k, v in value.items():
                lines.append(f"- **{k}:** {v}")
        else:
            lines.append(str(value))
        lines.append("")
    return "\n".join(lines).strip()


def extract_named_tables(data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """Find top-level list-of-dict tables suitable for CSV exports."""
    tables: Dict[str, List[Dict[str, Any]]] = {}
    for key, value in data.items():
        if isinstance(value, list) and value and isinstance(value[0], dict):
            tables[key] = value
    return tables

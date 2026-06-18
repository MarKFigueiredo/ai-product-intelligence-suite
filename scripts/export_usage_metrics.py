"""Export the local usage metrics database to JSON and ZIP files."""
from __future__ import annotations

from pathlib import Path

from services.usage_metrics_service import export_usage_json_bytes, export_usage_zip_bytes

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmark" / "results"
OUT.mkdir(exist_ok=True)

json_path = OUT / "real_usage_metrics_export.json"
zip_path = OUT / "real_usage_metrics_export.zip"
json_path.write_bytes(export_usage_json_bytes())
zip_path.write_bytes(export_usage_zip_bytes())
print(f"Wrote {json_path}")
print(f"Wrote {zip_path}")

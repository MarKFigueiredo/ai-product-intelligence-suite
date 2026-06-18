"""Generate real usage evidence reports from persisted metrics."""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List

from services.usage_metrics_service import list_data_events, list_metric_snapshots, list_workflow_runs, usage_summary, utc_now

ROOT = Path(__file__).resolve().parents[1]
REPORT_FILE = ROOT / "REAL_USAGE_EVIDENCE_REPORT.md"


def _avg(values: List[float]) -> float:
    return round(sum(values) / max(1, len(values)), 2) if values else 0.0


def aggregate_quality_metrics(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    bucket: Dict[str, List[float]] = defaultdict(list)
    for run in runs:
        for key, value in (run.get("metrics") or {}).items():
            if isinstance(value, (int, float)):
                bucket[key].append(float(value))
    selected = [
        "unsupported_claim_rate",
        "qa_coverage_rate",
        "negative_test_coverage_rate",
        "missing_negative_tests_total",
        "human_review_rate",
        "release_risk_rewrite_rate",
        "high_risk_claim_rate",
        "stale_artifact_rate",
    ]
    return {key: _avg(bucket[key]) for key in selected if key in bucket}


def generate_real_usage_evidence_markdown() -> str:
    runs = list_workflow_runs(limit=10_000)
    events = list_data_events(limit=10_000)
    metrics = list_metric_snapshots(limit=100_000)
    summary = usage_summary()
    workflow_counts = Counter(run.get("workflow", "unknown") for run in runs)
    event_counts = Counter(event.get("event_type", "unknown") for event in events)
    quality = aggregate_quality_metrics(runs)
    latest = runs[0] if runs else {}

    lines: List[str] = []
    lines.append("# Real Usage Evidence Report")
    lines.append("")
    lines.append("This report is generated from the local SQLite usage metrics store. It is portfolio evidence, not production analytics.")
    lines.append("")
    lines.append(f"Generated at: `{utc_now()}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(f"| Total workflow runs | {summary.get('runs_total', 0)} |")
    lines.append(f"| Data events | {summary.get('data_events_total', 0)} |")
    lines.append(f"| Workflows observed | {summary.get('workflows_total', 0)} |")
    lines.append(f"| Average latency | {summary.get('avg_latency_ms', 0)} ms |")
    lines.append(f"| Metric snapshots | {len(metrics)} |")
    lines.append("")
    lines.append("## Runs by workflow")
    lines.append("")
    lines.append("| Workflow | Runs |")
    lines.append("|---|---:|")
    for workflow, count in workflow_counts.most_common():
        lines.append(f"| {workflow} | {count} |")
    if not workflow_counts:
        lines.append("| No runs recorded yet | 0 |")
    lines.append("")
    lines.append("## Quality/review metrics observed")
    lines.append("")
    lines.append("| Metric | Average observed value |")
    lines.append("|---|---:|")
    for key, value in quality.items():
        lines.append(f"| {key} | {value} |")
    if not quality:
        lines.append("| No quality metrics recorded yet | 0 |")
    lines.append("")
    lines.append("## Data events")
    lines.append("")
    lines.append("| Event type | Count |")
    lines.append("|---|---:|")
    for event_type, count in event_counts.most_common():
        lines.append(f"| {event_type} | {count} |")
    if not event_counts:
        lines.append("| No data events recorded yet | 0 |")
    lines.append("")
    lines.append("## Latest run")
    lines.append("")
    if latest:
        lines.append(f"- Run ID: `{latest.get('run_id')}`")
        lines.append(f"- Workflow: `{latest.get('workflow')}`")
        lines.append(f"- Timestamp UTC: `{latest.get('timestamp_utc')}`")
        lines.append(f"- Actor/role: `{latest.get('actor')}` / `{latest.get('role')}`")
        lines.append(f"- Output hash: `{latest.get('output_hash')}`")
    else:
        lines.append("No workflow runs have been recorded yet. Use the app or seed script to create portfolio evidence.")
    lines.append("")
    lines.append("## How to interpret this report")
    lines.append("")
    lines.append("Synthetic benchmark metrics show controlled evaluation examples. This report shows observed local usage metrics accumulated as the app is used.")
    lines.append("The strongest portfolio signal is not the absolute number; it is the product discipline of capturing, exporting and learning from usage evidence.")
    lines.append("")
    return "\n".join(lines)


def save_real_usage_evidence_report(path: Path = REPORT_FILE) -> Path:
    path.write_text(generate_real_usage_evidence_markdown(), encoding="utf-8")
    return path

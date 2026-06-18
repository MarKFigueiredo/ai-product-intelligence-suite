"""Quality learning summaries from persisted usage metrics."""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Dict, List

from services.usage_metrics_service import list_metric_snapshots, list_workflow_runs

QUALITY_METRICS = [
    "unsupported_claim_rate",
    "qa_coverage_rate",
    "negative_test_coverage_rate",
    "reviewer_correction_rate",
    "missing_negative_tests_total",
    "high_risk_claim_rate",
    "stale_artifact_rate",
]


def metric_trends(limit: int = 1000) -> List[Dict[str, Any]]:
    snapshots = list_metric_snapshots(limit=limit)
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in reversed(snapshots):
        if row.get("metric_name") in QUALITY_METRICS:
            grouped[row["metric_name"]].append(row)
    rows: List[Dict[str, Any]] = []
    for metric, values in grouped.items():
        nums = [float(v.get("metric_value") or 0) for v in values]
        if not nums:
            continue
        first = nums[0]
        latest = nums[-1]
        delta = round(latest - first, 2)
        lower_is_better = any(token in metric for token in ["unsupported", "missing", "risk", "stale"])
        improving = delta < 0 if lower_is_better else delta > 0
        rows.append({
            "metric": metric,
            "first_value": first,
            "latest_value": latest,
            "delta": delta,
            "runs_observed": len(nums),
            "direction": "improving" if improving else "flat/regressing" if delta else "unchanged",
        })
    return sorted(rows, key=lambda r: r["metric"])


def workflow_learning_summary(limit: int = 500) -> Dict[str, Any]:
    runs = list_workflow_runs(limit=limit)
    by_workflow = Counter(r.get("workflow", "unknown") for r in runs)
    blockers = 0
    exported = 0
    for r in runs:
        md = r.get("metadata") or {}
        if str(md.get("release_gate_status", "")).lower() in {"blocked", "fail"}:
            blockers += 1
        if md.get("exported") or md.get("ui_event") == "export_package_saved":
            exported += 1
    return {
        "runs_total": len(runs),
        "workflow_mix": [{"workflow": k, "runs": v} for k, v in by_workflow.most_common()],
        "release_block_events": blockers,
        "export_or_handoff_events": exported,
        "metric_trends": metric_trends(),
    }

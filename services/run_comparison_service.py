"""Compare persisted workflow runs."""
from __future__ import annotations

from typing import Any, Dict, List

from services.usage_metrics_service import list_workflow_runs


def numeric_metrics(run: Dict[str, Any]) -> Dict[str, float]:
    metrics = run.get("metrics") or {}
    result: Dict[str, float] = {}
    for key, value in metrics.items():
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            result[key] = float(value)
    for key in ["latency_ms", "input_bytes", "output_bytes", "source_count"]:
        if isinstance(run.get(key), (int, float)):
            result[key] = float(run[key])
    return result


def compare_runs(run_a: Dict[str, Any], run_b: Dict[str, Any]) -> List[Dict[str, Any]]:
    a = numeric_metrics(run_a)
    b = numeric_metrics(run_b)
    rows: List[Dict[str, Any]] = []
    for metric in sorted(set(a) | set(b)):
        av = a.get(metric)
        bv = b.get(metric)
        if av is None or bv is None:
            change = None
            pct = None
        else:
            change = round(bv - av, 2)
            pct = round(((bv - av) / av) * 100, 2) if av else None
        rows.append(
            {
                "metric": metric,
                "run_a": av,
                "run_b": bv,
                "delta": change,
                "delta_pct": pct,
                "direction": "improved" if _is_improvement(metric, change) else "regressed" if change not in (None, 0) else "unchanged",
            }
        )
    return rows


def _is_improvement(metric: str, delta: float | None) -> bool:
    if delta is None:
        return False
    lower = metric.lower()
    lower_is_better = any(token in lower for token in ["unsupported", "missing", "latency", "weak", "error", "blocked", "stale", "risk"])
    return delta < 0 if lower_is_better else delta > 0


def latest_run_comparison(limit: int = 50) -> Dict[str, Any]:
    runs = list_workflow_runs(limit=limit)
    if len(runs) < 2:
        return {"available": False, "reason": "At least two workflow runs are required for comparison.", "runs": runs, "comparison": []}
    return {"available": True, "run_a": runs[1], "run_b": runs[0], "comparison": compare_runs(runs[1], runs[0])}

"""Persistent run history and reviewer workflow utilities.

The suite deliberately stores only run metadata, scores, hashes and reviewer
verdicts by default. This keeps the portfolio demo useful without silently
persisting source documents or customer-sensitive text.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from services.citation_verifier import build_obligation_support_matrix, grounding_summary

ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / ".local_runs"
RUN_HISTORY_FILE = RUN_DIR / "interpret_run_history.jsonl"
REVIEW_HISTORY_FILE = RUN_DIR / "interpret_review_history.jsonl"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def make_run_id(workflow: str, data: Dict[str, Any], citation_rows: Iterable[Dict[str, Any]]) -> str:
    return f"{workflow}-{stable_hash({'data': data, 'citations': list(citation_rows)})}"


def summarise_interpret_run(
    data: Dict[str, Any],
    citation_rows: List[Dict[str, Any]],
    *,
    model: str = "unknown",
    demo_mode: bool = True,
    input_hash: str = "",
    source_count: int = 0,
) -> Dict[str, Any]:
    """Build a compact, privacy-conscious run summary."""
    summary = grounding_summary(citation_rows)
    support_matrix = build_obligation_support_matrix(data, citation_rows)
    supported = [r for r in support_matrix if int(r.get("support_score") or 0) >= 75 and not r.get("review_required")]
    weak = [r for r in support_matrix if 1 <= int(r.get("support_score") or 0) < 75]
    missing = [r for r in support_matrix if int(r.get("support_score") or 0) <= 0 or r.get("support_status") == "Missing citation"]
    review = [r for r in support_matrix if r.get("review_required")]
    record = {
        "run_id": make_run_id("interpret", data, citation_rows),
        "timestamp_utc": _utc_now(),
        "workflow": "Interpret",
        "model": model,
        "demo_mode": bool(demo_mode),
        "input_hash": input_hash,
        "source_count": int(source_count or 0),
        "obligations": len(data.get("obligation_extraction", []) or []),
        "requirements": len(data.get("product_requirements", []) or []),
        "validation_rules": len(data.get("validation_rules", []) or []),
        "qa_test_cases": len(data.get("qa_test_cases", []) or []),
        "checked_claims": int(summary.get("verified_claims", 0) or 0),
        "average_support_score": int(summary.get("average_support_score", 0) or 0),
        "quote_integrity_rate": int(summary.get("quote_integrity_rate", 0) or 0),
        "weak_or_missing_claims": int(summary.get("weak_or_missing_claims", 0) or 0),
        "human_review_required": bool(summary.get("human_review_required")),
        "supported_obligations": len(supported),
        "weak_obligations": len(weak),
        "missing_obligations": len(missing),
        "review_obligations": len(review),
        "unsupported_claim_rate": _safe_rate(summary.get("weak_or_missing_claims", 0), summary.get("verified_claims", 0)),
        "note": "Local demo run history; source documents are not stored by default.",
    }
    return record


def append_run_history(record: Dict[str, Any]) -> Path:
    RUN_DIR.mkdir(exist_ok=True)
    with RUN_HISTORY_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    return RUN_HISTORY_FILE


def load_run_history(limit: int = 25) -> List[Dict[str, Any]]:
    if not RUN_HISTORY_FILE.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with RUN_HISTORY_FILE.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    rows.sort(key=lambda row: row.get("timestamp_utc", ""), reverse=True)
    return rows[:limit]


def compare_recent_runs(runs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return newest-first rows with deltas versus the next older run."""
    compared: List[Dict[str, Any]] = []
    for idx, run in enumerate(runs):
        previous = runs[idx + 1] if idx + 1 < len(runs) else {}
        compared.append(
            {
                "timestamp_utc": run.get("timestamp_utc"),
                "run_id": run.get("run_id"),
                "model": run.get("model"),
                "obligations": run.get("obligations", 0),
                "avg_support": run.get("average_support_score", 0),
                "avg_support_delta": _delta(run, previous, "average_support_score"),
                "weak_or_missing_claims": run.get("weak_or_missing_claims", 0),
                "weak_or_missing_delta": _delta(run, previous, "weak_or_missing_claims"),
                "quote_integrity_rate": run.get("quote_integrity_rate", 0),
                "review_obligations": run.get("review_obligations", 0),
            }
        )
    return compared


def build_reviewer_items(data: Dict[str, Any], citation_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    matrix = build_obligation_support_matrix(data, citation_rows)
    items: List[Dict[str, Any]] = []
    for row in matrix:
        score = int(row.get("support_score") or 0)
        default_status = "Correct" if score >= 80 and not row.get("review_required") else "Needs review"
        if score < 40 or row.get("support_status") == "Missing citation":
            default_status = "Incorrect"
        items.append(
            {
                "obligation_id": row.get("obligation_id", ""),
                "claim": row.get("obligation", ""),
                "citation": row.get("source", ""),
                "support_score": score,
                "support_status": row.get("support_status", ""),
                "best_supporting_quote": row.get("best_supporting_quote", ""),
                "review_reason": row.get("review_reason", ""),
                "default_status": default_status,
            }
        )
    return items


def build_final_review_report(
    data: Dict[str, Any],
    citation_rows: List[Dict[str, Any]],
    reviewer_decisions: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Group generated obligations into supported, weak, missing and reviewed buckets."""
    items = build_reviewer_items(data, citation_rows)
    decisions_by_id = {d.get("obligation_id"): d for d in reviewer_decisions if d.get("obligation_id")}
    supported: List[Dict[str, Any]] = []
    weak: List[Dict[str, Any]] = []
    missing: List[Dict[str, Any]] = []
    reviewed: List[Dict[str, Any]] = []
    for item in items:
        decision = decisions_by_id.get(item.get("obligation_id"), {})
        status = decision.get("status") or item.get("default_status")
        merged = {**item, "review_status": status, "review_comment": decision.get("comment", "")}
        if status in {"Correct", "Incorrect", "Needs review"}:
            reviewed.append(merged)
        if status == "Correct" and int(item.get("support_score") or 0) >= 70:
            supported.append(merged)
        elif status == "Incorrect" or int(item.get("support_score") or 0) < 40:
            missing.append(merged)
        else:
            weak.append(merged)
    return {
        "report_id": f"review-{stable_hash({'items': items, 'decisions': reviewer_decisions})}",
        "generated_at_utc": _utc_now(),
        "summary": {
            "supported": len(supported),
            "weak": len(weak),
            "missing": len(missing),
            "reviewed": len(reviewed),
            "obligations_total": len(items),
            "requirements_total": len(data.get("product_requirements", []) or []),
            "qa_test_cases_total": len(data.get("qa_test_cases", []) or []),
        },
        "supported": supported,
        "weak": weak,
        "missing": missing,
        "reviewed": reviewed,
        "decision_log": data.get("decision_log", []) or [],
        "note": "Final review report summarises what was supported, weak, missing and reviewed. Human sign-off is still required for production compliance decisions.",
    }


def append_review_report(report: Dict[str, Any]) -> Path:
    RUN_DIR.mkdir(exist_ok=True)
    with REVIEW_HISTORY_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(report, ensure_ascii=False, default=str) + "\n")
    return REVIEW_HISTORY_FILE


def _delta(current: Dict[str, Any], previous: Dict[str, Any], key: str) -> int | None:
    if not previous:
        return None
    try:
        return int(current.get(key, 0) or 0) - int(previous.get(key, 0) or 0)
    except Exception:
        return None


def _safe_rate(numerator: Any, denominator: Any) -> float:
    try:
        denominator_int = int(denominator or 0)
        if denominator_int <= 0:
            return 0.0
        return round((int(numerator or 0) / denominator_int) * 100, 1)
    except Exception:
        return 0.0

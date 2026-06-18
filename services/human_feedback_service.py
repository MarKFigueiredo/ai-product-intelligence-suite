"""Human feedback flywheel for reviewer decisions.

Reviewer decisions are stored separately from workflow metrics so they can be
reused as simple few-shot examples in future runs. This is not model training;
it is a transparent local feedback loop that shows how human corrections can
shape the next prompt/run.
"""
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from services.enterprise_controls_service import sign_payload, stable_hash
from services.usage_metrics_service import USAGE_DB_FILE, connect, init_usage_db, utc_now

HUMAN_REVIEW_SCHEMA_VERSION = "human_reviews_v1"

REVIEW_LABELS = {
    "correct",
    "incorrect",
    "needs_review",
    "needs_clarification",
    "missing_evidence",
    "too_broad",
    "out_of_scope",
    "duplicate",
    "needs_negative_test",
}

SAFE_REVIEW_LABEL_MAP = {
    "Correct": "correct",
    "Incorrect": "incorrect",
    "Needs review": "needs_review",
    "Needs clarification": "needs_clarification",
    "Missing evidence": "missing_evidence",
    "Too broad": "too_broad",
    "Out of scope": "out_of_scope",
    "Duplicate": "duplicate",
    "Needs negative test": "needs_negative_test",
}


def init_human_feedback_db(db_path: Path = USAGE_DB_FILE) -> Path:
    init_usage_db(db_path)
    conn = connect(db_path)
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS human_reviews (
                review_id TEXT PRIMARY KEY,
                timestamp_utc TEXT NOT NULL,
                run_id TEXT,
                document_hash TEXT,
                domain TEXT,
                artifact_type TEXT NOT NULL,
                artifact_id TEXT,
                original_text TEXT NOT NULL,
                review_label TEXT NOT NULL,
                corrected_text TEXT,
                review_reason TEXT,
                reviewer_role TEXT NOT NULL,
                reviewer_name TEXT NOT NULL,
                used_as_feedback_example INTEGER DEFAULT 0,
                metadata_json TEXT NOT NULL,
                signature TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_human_reviews_domain ON human_reviews(domain);
            CREATE INDEX IF NOT EXISTS idx_human_reviews_label ON human_reviews(review_label);
            CREATE INDEX IF NOT EXISTS idx_human_reviews_timestamp ON human_reviews(timestamp_utc);
            """
        )
        conn.commit()
    finally:
        conn.close()
    return db_path


def _normalise_label(label: str) -> str:
    raw = str(label or "needs_review").strip()
    mapped = SAFE_REVIEW_LABEL_MAP.get(raw, raw.lower().replace(" ", "_"))
    return mapped if mapped in REVIEW_LABELS else "needs_review"


def _json(value: Any) -> str:
    return json.dumps(value or {}, sort_keys=True, ensure_ascii=False, default=str)


def record_human_review(
    *,
    run_id: str = "",
    document_hash: str = "",
    domain: str = "",
    artifact_type: str = "obligation",
    artifact_id: str = "",
    original_text: str,
    review_label: str,
    corrected_text: str = "",
    review_reason: str = "",
    reviewer_role: str = "Product Manager",
    reviewer_name: str = "demo-reviewer",
    metadata: Dict[str, Any] | None = None,
    db_path: Path = USAGE_DB_FILE,
) -> Dict[str, Any]:
    """Persist one human review decision."""
    init_human_feedback_db(db_path)
    timestamp = utc_now()
    label = _normalise_label(review_label)
    base = {
        "timestamp_utc": timestamp,
        "run_id": run_id,
        "document_hash": document_hash,
        "domain": domain,
        "artifact_type": artifact_type,
        "artifact_id": artifact_id,
        "original_text": original_text or "",
        "review_label": label,
        "corrected_text": corrected_text or "",
        "review_reason": review_reason or "",
        "reviewer_role": reviewer_role or "Product Manager",
        "reviewer_name": reviewer_name or "demo-reviewer",
        "metadata": {"schema_version": HUMAN_REVIEW_SCHEMA_VERSION, **(metadata or {})},
    }
    review_id = "hr-" + stable_hash(base, length=20)
    row = {**base, "review_id": review_id, "used_as_feedback_example": 0}
    row["signature"] = sign_payload(row)
    conn = connect(db_path)
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO human_reviews (
                review_id, timestamp_utc, run_id, document_hash, domain,
                artifact_type, artifact_id, original_text, review_label,
                corrected_text, review_reason, reviewer_role, reviewer_name,
                used_as_feedback_example, metadata_json, signature
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                review_id,
                row["timestamp_utc"],
                row["run_id"],
                row["document_hash"],
                row["domain"],
                row["artifact_type"],
                row["artifact_id"],
                row["original_text"],
                row["review_label"],
                row["corrected_text"],
                row["review_reason"],
                row["reviewer_role"],
                row["reviewer_name"],
                row["used_as_feedback_example"],
                _json(row["metadata"]),
                row["signature"],
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return row


def record_human_reviews(decisions: Sequence[Dict[str, Any]], *, domain: str = "", run_id: str = "", document_hash: str = "", reviewer_role: str = "Product Manager", reviewer_name: str = "demo-reviewer", db_path: Path = USAGE_DB_FILE) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for decision in decisions:
        original = str(decision.get("original_text") or decision.get("claim") or decision.get("obligation") or "").strip()
        if not original:
            continue
        rows.append(record_human_review(
            run_id=run_id,
            document_hash=document_hash,
            domain=domain,
            artifact_type=str(decision.get("artifact_type") or "obligation"),
            artifact_id=str(decision.get("artifact_id") or decision.get("obligation_id") or ""),
            original_text=original,
            review_label=str(decision.get("review_label") or decision.get("status") or "needs_review"),
            corrected_text=str(decision.get("corrected_text") or decision.get("correction") or ""),
            review_reason=str(decision.get("review_reason") or decision.get("comment") or ""),
            reviewer_role=reviewer_role,
            reviewer_name=reviewer_name,
            metadata={k: v for k, v in decision.items() if k not in {"original_text", "claim", "obligation", "status", "review_label", "corrected_text", "correction", "comment", "review_reason"}},
            db_path=db_path,
        ))
    return rows


def list_human_reviews(*, limit: int = 100, domain: str = "", db_path: Path = USAGE_DB_FILE) -> List[Dict[str, Any]]:
    init_human_feedback_db(db_path)
    conn = connect(db_path)
    try:
        if domain:
            rows = conn.execute(
                "SELECT * FROM human_reviews WHERE domain = ? OR domain = '' ORDER BY timestamp_utc DESC LIMIT ?",
                (domain, int(limit)),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM human_reviews ORDER BY timestamp_utc DESC LIMIT ?", (int(limit),)).fetchall()
    finally:
        conn.close()
    result: List[Dict[str, Any]] = []
    for row in rows:
        d = dict(row)
        try:
            d["metadata"] = json.loads(d.pop("metadata_json") or "{}")
        except Exception:
            d["metadata"] = {}
        result.append(d)
    return result


def feedback_examples_for_next_run(*, domain: str = "", limit: int = 5, db_path: Path = USAGE_DB_FILE) -> List[Dict[str, Any]]:
    """Return useful reviewer corrections for few-shot prompting/review hints."""
    reviews = list_human_reviews(limit=200, domain=domain, db_path=db_path)
    candidates = [
        r for r in reviews
        if r.get("review_label") in {"incorrect", "needs_review", "needs_clarification", "missing_evidence", "too_broad", "needs_negative_test"}
        and (r.get("corrected_text") or r.get("review_reason"))
    ]
    return candidates[: int(limit)]


def mark_feedback_examples_used(review_ids: Iterable[str], *, db_path: Path = USAGE_DB_FILE) -> int:
    ids = [str(rid) for rid in review_ids if rid]
    if not ids:
        return 0
    init_human_feedback_db(db_path)
    conn = connect(db_path)
    try:
        conn.executemany("UPDATE human_reviews SET used_as_feedback_example = 1 WHERE review_id = ?", [(rid,) for rid in ids])
        conn.commit()
    finally:
        conn.close()
    return len(ids)


def summarize_feedback_inventory(*, domain: str = "", db_path: Path = USAGE_DB_FILE) -> Dict[str, Any]:
    reviews = list_human_reviews(limit=10_000, domain=domain, db_path=db_path)
    reusable = feedback_examples_for_next_run(domain=domain, limit=10_000, db_path=db_path)
    used = [r for r in reviews if int(r.get("used_as_feedback_example") or 0)]
    labels: Dict[str, int] = {}
    for row in reviews:
        labels[row.get("review_label", "unknown")] = labels.get(row.get("review_label", "unknown"), 0) + 1
    return {
        "human_reviews_total": len(reviews),
        "feedback_examples_available": len(reusable),
        "feedback_examples_previously_used": len(used),
        "review_labels": labels,
    }


def _terms(value: str) -> set[str]:
    return {t for t in re.findall(r"[A-Za-z0-9]{4,}", (value or "").lower()) if t not in {"this", "that", "with", "from", "system", "product"}}


def _relevant(example: Dict[str, Any], text: str) -> bool:
    example_terms = _terms(str(example.get("original_text", "")) + " " + str(example.get("review_reason", "")))
    text_terms = _terms(text)
    if not example_terms or not text_terms:
        return False
    return bool(example_terms & text_terms)


def apply_feedback_examples_to_output(output: Dict[str, Any], examples: Sequence[Dict[str, Any]]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Apply simple reviewer examples to obligation wording.

    This is deliberately conservative and transparent. It does not claim model
    training. It only applies corrections when prior reviewer feedback is either
    directly relevant or captures a known unsafe wording pattern.
    """
    adjusted = 0
    used_ids: List[str] = []
    result = json.loads(json.dumps(output or {}, ensure_ascii=False, default=str))
    obligations = result.get("obligation_extraction") or result.get("obligations") or []
    if not isinstance(obligations, list):
        obligations = []

    unsafe_patterns = [
        (re.compile(r"\bguarantees?\s+(full\s+)?(legal\s+)?compliance\b", re.I), "supports review against configured compliance rules"),
        (re.compile(r"\bfully\s+compliant\b", re.I), "designed to support compliance review"),
        (re.compile(r"\bautomatically\s+ensures\b", re.I), "helps reviewers assess"),
    ]

    for row in obligations:
        if not isinstance(row, dict):
            continue
        key = "obligation" if "obligation" in row else "text" if "text" in row else "requirement"
        current = str(row.get(key, ""))
        if not current:
            continue
        changed = current
        matched_example = None
        for example in examples:
            correction = str(example.get("corrected_text") or "").strip()
            if correction and (_relevant(example, current) or str(example.get("review_label")) in {"too_broad", "incorrect"}):
                # Do not overwrite detailed requirements with unrelated examples.
                if _relevant(example, current):
                    changed = correction
                    matched_example = example
                    break
            for pattern, replacement in unsafe_patterns:
                if pattern.search(changed):
                    changed = pattern.sub(replacement, changed)
                    matched_example = example
                    break
            if matched_example:
                break
        if changed != current:
            row[key] = changed
            row["human_feedback_applied"] = True
            row["feedback_review_id"] = matched_example.get("review_id") if matched_example else "pattern_guardrail"
            adjusted += 1
            if matched_example and matched_example.get("review_id"):
                used_ids.append(matched_example["review_id"])

    if used_ids:
        mark_feedback_examples_used(used_ids)
    summary = {
        "feedback_examples_used": len(set(used_ids)) if used_ids else 0,
        "obligations_adjusted_by_feedback": adjusted,
        "feedback_review_ids_used": sorted(set(used_ids)),
        "method_note": "Prior reviewer examples are used as local few-shot hints/pattern guardrails. This is not model training and does not prove quality improvement without human validation.",
    }
    result.setdefault("_human_feedback", summary)
    return result, summary

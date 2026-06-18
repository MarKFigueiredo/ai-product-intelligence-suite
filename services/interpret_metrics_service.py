"""Interpret quality metrics.

Run metrics and benchmark metrics are intentionally separated:
- citation support, unsupported-claim and human-review rates are calculated from
  the actual current run: the generated output + the currently retrieved source
  chunks;
- obligation precision and recall are calculated only when a reviewer provides a
  gold-standard obligations file for the document being tested.

This avoids presenting synthetic demo numbers as product performance. When no
run-specific gold set is provided, precision/recall are shown as N/A rather than
being silently calculated from the bundled sample benchmark.
"""
from __future__ import annotations

import csv
import io
import json
from typing import Any, Dict, List, Optional

from services.interpret_benchmark_service import compare_generated_to_gold, generated_obligations_from_output

SUPPORT_THRESHOLD = 64
UNSUPPORTED_THRESHOLD = 42


def _pct(numerator: int, denominator: int) -> Optional[int]:
    if denominator <= 0:
        return None
    return round(100 * numerator / denominator)


def _tone(value: Optional[int], *, higher_is_better: bool = True) -> str:
    if value is None:
        return "neutral"
    if higher_is_better:
        if value >= 80:
            return "good"
        if value >= 60:
            return "mid"
        return "bad"
    if value <= 10:
        return "good"
    if value <= 30:
        return "mid"
    return "bad"


def _status(value: Optional[int], *, higher_is_better: bool = True) -> str:
    if value is None:
        return "Needs gold set"
    if higher_is_better:
        if value >= 80:
            return "Strong"
        if value >= 60:
            return "Review"
        return "Weak"
    if value <= 10:
        return "Low"
    if value <= 30:
        return "Monitor"
    return "High"


def _display_fraction(numerator: Optional[int], denominator: Optional[int]) -> str:
    if numerator is None or denominator is None:
        return "N/A"
    return f"{numerator}/{denominator}"


def _split_required_terms(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value).replace(";", ",")
    return [part.strip() for part in text.split(",") if part.strip()]


def normalize_gold_benchmark(raw: Any, *, name: str = "Run-specific gold obligations") -> Dict[str, Any]:
    """Normalize reviewer-provided gold obligations.

    Accepted shapes:
    - {"name": "...", "gold_obligations": [{"id": "G1", "obligation": "..."}]}
    - {"obligations": [{"obligation": "..."}]}
    - [{"obligation": "..."}, "plain obligation text"]

    Optional fields supported per obligation: id, required_terms, expected_source,
    expected_quote, notes.
    """
    if isinstance(raw, dict):
        items = raw.get("gold_obligations") or raw.get("obligations") or raw.get("items") or []
        benchmark_name = raw.get("name") or name
        document_text = raw.get("document_text", "")
    elif isinstance(raw, list):
        items = raw
        benchmark_name = name
        document_text = ""
    else:
        raise ValueError("Gold benchmark must be a JSON object, JSON list, or CSV table.")

    normalized: List[Dict[str, Any]] = []
    for idx, item in enumerate(items, start=1):
        if isinstance(item, str):
            obligation = item.strip()
            row: Dict[str, Any] = {"id": f"G{idx}", "obligation": obligation, "required_terms": []}
        elif isinstance(item, dict):
            obligation = str(item.get("obligation") or item.get("text") or item.get("expected_obligation") or "").strip()
            row = {
                "id": str(item.get("id") or item.get("gold_id") or f"G{idx}"),
                "obligation": obligation,
                "required_terms": _split_required_terms(item.get("required_terms") or item.get("terms")),
                "expected_source": item.get("expected_source") or item.get("source") or "",
                "expected_quote": item.get("expected_quote") or item.get("quote") or "",
                "notes": item.get("notes") or "",
            }
        else:
            continue
        if row.get("obligation"):
            normalized.append(row)

    return {
        "name": benchmark_name,
        "document_text": document_text,
        "gold_obligations": normalized,
        "method_note": (
            "Run-specific gold obligations provided by the reviewer. Precision and recall are only meaningful "
            "if this gold set was written independently of the model output."
        ),
    }


def parse_gold_benchmark_text(text: str, *, filename: str = "uploaded_gold") -> Dict[str, Any]:
    """Parse JSON or CSV gold obligations text."""
    stripped = (text or "").strip()
    if not stripped:
        raise ValueError("Gold benchmark file is empty.")

    if filename.lower().endswith(".csv"):
        reader = csv.DictReader(io.StringIO(stripped))
        rows = list(reader)
        if not rows:
            raise ValueError("CSV gold benchmark has no rows.")
        return normalize_gold_benchmark({"name": filename, "gold_obligations": rows}, name=filename)

    try:
        raw = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise ValueError("Gold benchmark must be valid JSON or CSV with an 'obligation' column.") from exc
    return normalize_gold_benchmark(raw, name=filename)


def citation_quality_counts(citation_rows: List[Dict[str, Any]]) -> Dict[str, int]:
    checked = len(citation_rows)
    supported = len([
        r for r in citation_rows
        if bool(r.get("exists", False)) and int(r.get("support_score") or 0) >= SUPPORT_THRESHOLD
    ])
    unsupported = len([
        r for r in citation_rows
        if (not bool(r.get("exists", False))) or int(r.get("support_score") or 0) < UNSUPPORTED_THRESHOLD
    ])
    review = len([r for r in citation_rows if bool(r.get("review_required", False))])
    partial = max(0, checked - supported - unsupported)
    return {
        "checked_claims": checked,
        "supported_claims": supported,
        "partial_claims": partial,
        "unsupported_claims": unsupported,
        "human_review_claims": review,
    }


def calculate_interpret_quality_metrics(
    data: Dict[str, Any],
    citation_rows: List[Dict[str, Any]],
    benchmark: Dict[str, Any] | None = None,
    threshold: int = 58,
) -> Dict[str, Any]:
    """Return the five portfolio-facing Interpret metrics.

    Metrics from actual current run:
    - citation support rate;
    - unsupported claim rate;
    - human review rate.

    Metrics requiring a run-specific gold set:
    - obligation precision;
    - obligation recall.
    """
    generated = generated_obligations_from_output(data)
    generated_count = len(generated)

    obligation_results: Dict[str, Any]
    has_gold = bool(benchmark and benchmark.get("gold_obligations"))
    if has_gold:
        try:
            obligation_results = compare_generated_to_gold(data, benchmark, threshold=threshold)
        except Exception as error:  # pragma: no cover - defensive for UI use
            obligation_results = {
                "error": str(error),
                "generated_count": generated_count,
                "gold_count": 0,
                "matched_gold_count": 0,
                "generated_matrix": [],
                "match_matrix": [],
            }
            has_gold = False
    else:
        obligation_results = {
            "benchmark_name": "No run-specific gold obligations provided",
            "generated_count": generated_count,
            "gold_count": 0,
            "matched_gold_count": 0,
            "generated_matrix": [],
            "match_matrix": [],
            "missing_gold_obligations": [],
            "method_note": "Precision and recall require a reviewer-provided gold-standard obligation set for this document.",
        }

    if has_gold:
        gold_count = int(obligation_results.get("gold_count") or 0)
        generated_matches = len([
            row for row in obligation_results.get("generated_matrix", []) or []
            if row.get("status") == "Matched"
        ])
        matched_gold = int(obligation_results.get("matched_gold_count") or 0)
        obligation_precision = _pct(generated_matches, generated_count)
        obligation_recall = _pct(matched_gold, gold_count)
        precision_num: Optional[int] = generated_matches
        precision_den: Optional[int] = generated_count
        recall_num: Optional[int] = matched_gold
        recall_den: Optional[int] = gold_count
        obligation_basis = "Run-specific gold set"
    else:
        gold_count = 0
        obligation_precision = None
        obligation_recall = None
        precision_num = None
        precision_den = None
        recall_num = None
        recall_den = None
        obligation_basis = "Not calculated — no gold set provided"

    counts = citation_quality_counts(citation_rows)
    checked = counts["checked_claims"]

    citation_support_rate = _pct(counts["supported_claims"], checked)
    unsupported_claim_rate = _pct(counts["unsupported_claims"], checked)
    human_review_rate = _pct(counts["human_review_claims"], checked)

    metrics = [
        {
            "metric": "Obligation precision",
            "value": obligation_precision,
            "display_value": "N/A" if obligation_precision is None else f"{obligation_precision}%",
            "numerator": precision_num,
            "denominator": precision_den,
            "fraction": _display_fraction(precision_num, precision_den),
            "status": _status(obligation_precision),
            "tone": _tone(obligation_precision),
            "evidence_basis": obligation_basis,
            "definition": "Generated obligations that match the reviewer-provided gold obligations divided by generated obligations.",
            "method": "Calculated only when a run-specific gold-standard obligations file is provided.",
            "limitation": "Not available without independent gold obligations for the same document. A weak gold set creates weak metrics.",
        },
        {
            "metric": "Obligation recall",
            "value": obligation_recall,
            "display_value": "N/A" if obligation_recall is None else f"{obligation_recall}%",
            "numerator": recall_num,
            "denominator": recall_den,
            "fraction": _display_fraction(recall_num, recall_den),
            "status": _status(obligation_recall),
            "tone": _tone(obligation_recall),
            "evidence_basis": obligation_basis,
            "definition": "Reviewer-provided gold obligations found by the generated output divided by total gold obligations.",
            "method": "Gold-centric matching against the run-specific gold set.",
            "limitation": "Requires independent human gold obligations. Not calculated from the model output alone.",
        },
        {
            "metric": "Citation support rate",
            "value": citation_support_rate,
            "display_value": "N/A" if citation_support_rate is None else f"{citation_support_rate}%",
            "numerator": counts["supported_claims"],
            "denominator": checked,
            "fraction": _display_fraction(counts["supported_claims"], checked),
            "status": _status(citation_support_rate),
            "tone": _tone(citation_support_rate),
            "evidence_basis": "Actual current run",
            "definition": f"Checked claims with an existing citation and support score ≥ {SUPPORT_THRESHOLD}% divided by checked claims.",
            "method": "Rule-based citation support check using quote integrity, token overlap, n-grams, numbers and modality/negation checks.",
            "limitation": "Textual support is not legal interpretation; human review remains required.",
        },
        {
            "metric": "Unsupported claim rate",
            "value": unsupported_claim_rate,
            "display_value": "N/A" if unsupported_claim_rate is None else f"{unsupported_claim_rate}%",
            "numerator": counts["unsupported_claims"],
            "denominator": checked,
            "fraction": _display_fraction(counts["unsupported_claims"], checked),
            "status": _status(unsupported_claim_rate, higher_is_better=False),
            "tone": _tone(unsupported_claim_rate, higher_is_better=False),
            "evidence_basis": "Actual current run",
            "definition": f"Claims with missing source IDs or support score < {UNSUPPORTED_THRESHOLD}% divided by checked claims.",
            "method": "Rule-based weak support detection against the cited source chunks used in the run.",
            "limitation": "A low rate is encouraging but does not guarantee correctness.",
        },
        {
            "metric": "Human review rate",
            "value": human_review_rate,
            "display_value": "N/A" if human_review_rate is None else f"{human_review_rate}%",
            "numerator": counts["human_review_claims"],
            "denominator": checked,
            "fraction": _display_fraction(counts["human_review_claims"], checked),
            "status": _status(human_review_rate, higher_is_better=False),
            "tone": _tone(human_review_rate, higher_is_better=False),
            "evidence_basis": "Actual current run",
            "definition": "Claims flagged for human review divided by checked claims.",
            "method": "Deterministic review flags from weak support, missing quotes, number mismatches and modality/negation issues.",
            "limitation": "A high rate can be positive in regulated workflows because it surfaces uncertainty instead of hiding it.",
        },
    ]

    method_note = (
        "Citation support, unsupported-claim and human-review rates are calculated from the actual current run. "
        "Obligation precision and recall are calculated only when you provide an independent gold-standard obligations file for the same document. "
        "These are deterministic support metrics, not model self-scores and not legal/compliance proof."
    )

    return {
        "benchmark_name": obligation_results.get("benchmark_name", "Run-specific gold obligations"),
        "has_gold_benchmark": has_gold,
        "threshold": threshold,
        "support_threshold": SUPPORT_THRESHOLD,
        "unsupported_threshold": UNSUPPORTED_THRESHOLD,
        "metrics": metrics,
        "citation_counts": counts,
        "obligation_results": obligation_results,
        "method_note": method_note,
    }


def metrics_as_rows(metrics_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for m in metrics_payload.get("metrics", []):
        rows.append({
            "metric": m.get("metric"),
            "value": m.get("display_value"),
            "fraction": m.get("fraction"),
            "status": m.get("status"),
            "evidence_basis": m.get("evidence_basis"),
            "method": m.get("method"),
            "limitation": m.get("limitation"),
        })
    return rows

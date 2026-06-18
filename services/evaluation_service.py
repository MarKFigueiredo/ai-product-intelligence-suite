"""Quality gates and evaluation helpers.

This module intentionally avoids model self-scoring. Scores here are computed
from deterministic checks: schema completeness, citation support rows and
risk/ambiguity patterns in the generated output.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List


def score_completion(data: Dict[str, Any], expected_keys: List[str]) -> int:
    if not expected_keys:
        return 0
    present = sum(1 for key in expected_keys if data.get(key))
    return round(100 * present / len(expected_keys))


def risky_claims(markdown: str) -> List[str]:
    patterns = [
        r"fully compliant",
        r"guarantee[s]? compliance",
        r"ensures compliance",
        r"no risk",
        r"always compliant",
        r"never fails",
    ]
    found = []
    for pat in patterns:
        if re.search(pat, markdown or "", re.IGNORECASE):
            found.append(pat)
    return found


def ambiguity_warnings(markdown: str) -> List[str]:
    warnings = []
    text = (markdown or "").lower()
    if "tbd" in text or "to be confirmed" in text:
        warnings.append("Contains TBD / to be confirmed items.")
    if "assumption" not in text:
        warnings.append("Assumptions may not be explicit.")
    if "open question" not in text and "open_questions" not in text:
        warnings.append("Open questions may be missing.")
    if "human review" not in text and "needs review" not in text:
        warnings.append("Human review flags may be missing.")
    return warnings


def citation_support_score(citation_rows: List[Dict[str, Any]]) -> int:
    """Average rule-based support score across claim/citation rows."""
    if not citation_rows:
        return 0
    scores = [int(row.get("support_score") or 0) for row in citation_rows]
    return round(sum(scores) / max(1, len(scores)))


def citation_precision_proxy(citation_rows: List[Dict[str, Any]], threshold: int = 58) -> int:
    """Proxy precision: share of cited claims with at least partial support.

    This is not a legal proof. It is a transparent portfolio-quality metric.
    """
    if not citation_rows:
        return 0
    supported = sum(1 for row in citation_rows if row.get("exists") and int(row.get("support_score") or 0) >= threshold)
    return round(100 * supported / len(citation_rows))


def evaluate_output(
    data: Dict[str, Any],
    markdown: str,
    expected_keys: List[str],
    source_coverage: Dict[str, Any] | None = None,
    citation_rows: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    completeness = score_completion(data, expected_keys)
    citation_rows = citation_rows or []
    avg_support = citation_support_score(citation_rows)
    precision_proxy = citation_precision_proxy(citation_rows)
    risks = risky_claims(markdown)
    amb = ambiguity_warnings(markdown)

    weak_rows = [row for row in citation_rows if int(row.get("support_score") or 0) < 58 or not row.get("exists")]
    if avg_support >= 75 and precision_proxy >= 75 and not risks:
        hallucination_risk = "Lower"
    elif avg_support >= 50 and precision_proxy >= 50:
        hallucination_risk = "Moderate"
    else:
        hallucination_risk = "Higher"

    return {
        "completeness_score": completeness,
        "rule_verified_support_score": avg_support,
        "citation_precision_proxy": precision_proxy,
        "hallucination_risk": hallucination_risk,
        "risky_claims": risks,
        "ambiguity_warnings": amb,
        "weak_citation_rows": len(weak_rows),
        "missing_inputs": [key for key in expected_keys if not data.get(key)],
        "source_coverage": source_coverage or {},
        "recommendation": (
            "Suitable as a reviewed portfolio output"
            if completeness >= 80 and hallucination_risk != "Higher"
            else "Needs human review before portfolio use"
        ),
        "method_note": "Scores are computed by deterministic checks, not self-reported by the language model.",
    }

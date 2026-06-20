"""Mandatory negative test coverage checks.

The goal is not to pretend QA is fully automated. It is to make a product-quality
rule explicit: every source obligation that reaches PRD/Jira/QA handoff must have
at least one mapped negative test, not only a happy path or generic acceptance
criterion.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Sequence

NEGATIVE_KEYWORDS = {
    "negative",
    "missing",
    "invalid",
    "blank",
    "empty",
    "incorrect",
    "inconsistent",
    "unauthorised",
    "unauthorized",
    "expired",
    "duplicate",
    "malformed",
    "out of range",
    "reject",
    "rejected",
    "block",
    "blocked",
    "fail",
    "fails",
    "failure",
    "error",
    "exception",
    "not allowed",
    "without",
    "cannot",
}

POSITIVE_ONLY_HINTS = {
    "happy path",
    "valid invoice passes",
    "valid data passes",
    "successful export",
    "success path",
    "passes validation",
}

OBLIGATION_ID_RE = re.compile(r"\bO(?:[-_A-Za-z0-9]*\d[A-Za-z0-9_-]*)\b", re.IGNORECASE)


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(f"{k} {_text(v)}" for k, v in value.items())
    if isinstance(value, (list, tuple, set)):
        return " ".join(_text(v) for v in value)
    return str(value)


def _norm_obligation_id(value: str) -> str:
    return str(value or "").strip().upper()


def _ids_from_text(value: Any) -> List[str]:
    found = [_norm_obligation_id(m.group(0)) for m in OBLIGATION_ID_RE.finditer(_text(value))]
    # preserve order and remove duplicates
    seen: set[str] = set()
    ordered: List[str] = []
    for item in found:
        if item and item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def _ids_from_field(row: Dict[str, Any]) -> List[str]:
    candidates: List[str] = []
    for key in [
        "obligation_id",
        "source_obligation_id",
        "covers_obligation",
        "covered_obligation",
        "mapped_obligation",
        "obligation",
        "source",
        "evidence",
        "traceability",
    ]:
        value = row.get(key)
        if isinstance(value, list):
            candidates.extend(_norm_obligation_id(v) for v in value)
        elif isinstance(value, str):
            # Accept direct O1 and text such as "O1 — ...".
            ids = _ids_from_text(value)
            candidates.extend(ids if ids else [_norm_obligation_id(value) if value.strip().upper().startswith("O") else ""])
    seen: set[str] = set()
    ordered: List[str] = []
    for item in candidates:
        if item and OBLIGATION_ID_RE.fullmatch(item) and item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def extract_obligation_ids(data: Dict[str, Any] | None) -> List[str]:
    """Extract obligation IDs from Interpret or Discover shaped outputs."""
    data = data or {}
    ids: List[str] = []
    for row in data.get("obligation_extraction", []) or []:
        if isinstance(row, dict):
            value = row.get("obligation_id") or row.get("id")
            if value:
                ids.append(_norm_obligation_id(str(value)))
    for row in data.get("interpret_inputs_used", []) or []:
        if isinstance(row, dict):
            value = row.get("obligation_id") or row.get("id")
            if value:
                ids.append(_norm_obligation_id(str(value)))
    for section in ["compliance_pipeline", "negative_test_coverage", "qa_test_matrix", "qa_test_cases", "gherkin_acceptance_criteria"]:
        for row in data.get(section, []) or []:
            ids.extend(_ids_from_text(row))
    seen: set[str] = set()
    ordered: List[str] = []
    for item in ids:
        item = _norm_obligation_id(item)
        if item and OBLIGATION_ID_RE.fullmatch(item) and item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def iter_qa_rows(data: Dict[str, Any] | None) -> List[Dict[str, Any]]:
    """Return QA-like rows across Interpret, Discover and explicit negative coverage sections."""
    data = data or {}
    rows: List[Dict[str, Any]] = []
    section_names = [
        "qa_test_cases",
        "qa_test_matrix",
        "gherkin_acceptance_criteria",
        "negative_test_coverage",
    ]
    for section in section_names:
        for idx, item in enumerate(data.get(section, []) or []):
            if isinstance(item, dict):
                row = {**item, "_section": section, "_row_index": idx}
            else:
                row = {"test_case": str(item), "_section": section, "_row_index": idx}
            rows.append(row)
    return rows


def is_negative_test(row: Dict[str, Any] | str) -> bool:
    """Classify whether a QA row is a negative/edge/failure test case."""
    if isinstance(row, str):
        raw = row
        row_dict: Dict[str, Any] = {"text": row}
    else:
        row_dict = row
        raw = _text(row)
    lower = raw.lower()
    row_type = str(row_dict.get("type") or row_dict.get("test_type") or row_dict.get("case_type") or "").lower()
    if "negative" in row_type or "edge" in row_type or "failure" in row_type:
        return True
    if any(hint in lower for hint in POSITIVE_ONLY_HINTS) and not any(word in lower for word in ["missing", "invalid", "error", "blocked", "reject"]):
        return False
    return any(keyword in lower for keyword in NEGATIVE_KEYWORDS)


def mapped_obligation_ids(row: Dict[str, Any], known_obligation_ids: Sequence[str]) -> List[str]:
    explicit = _ids_from_field(row)
    if explicit:
        return [item for item in explicit if not known_obligation_ids or item in known_obligation_ids]
    text_ids = _ids_from_text(row)
    if text_ids:
        return [item for item in text_ids if not known_obligation_ids or item in known_obligation_ids]
    # If there is exactly one obligation, allow a generic QA row to map to it. For
    # multiple obligations this would create false confidence, so it stays unmapped.
    if len(known_obligation_ids) == 1:
        return [known_obligation_ids[0]]
    return []


def validate_negative_test_coverage(data: Dict[str, Any] | None) -> Dict[str, Any]:
    """Check mandatory negative test coverage at obligation level."""
    data = data or {}
    obligation_ids = extract_obligation_ids(data)
    qa_rows = iter_qa_rows(data)
    coverage_rows: List[Dict[str, Any]] = []
    negative_total = 0
    unmapped_negative = 0

    for oid in obligation_ids:
        mapped = [row for row in qa_rows if oid in mapped_obligation_ids(row, obligation_ids)]
        negative = [row for row in mapped if is_negative_test(row)]
        positive = [row for row in mapped if not is_negative_test(row)]
        negative_total += len(negative)
        example = negative[0] if negative else (mapped[0] if mapped else {})
        coverage_rows.append(
            {
                "obligation_id": oid,
                "positive_tests": len(positive),
                "negative_tests": len(negative),
                "has_negative_test": bool(negative),
                "status": "Pass" if negative else "Blocked",
                "example_test": example.get("test_case") or example.get("scenario") or example.get("negative_test") or example.get("steps") or "Missing negative test",
                "required_action": "None" if negative else f"Add at least one mapped negative/edge/failure test for {oid}.",
            }
        )

    # Count negative tests that could not be mapped to an obligation. These are
    # useful, but they cannot satisfy mandatory coverage.
    for row in qa_rows:
        if is_negative_test(row) and not mapped_obligation_ids(row, obligation_ids):
            unmapped_negative += 1
            negative_total += 1

    obligations_total = len(obligation_ids)
    obligations_with_negative = len([r for r in coverage_rows if r["has_negative_test"]])
    coverage_rate = round((obligations_with_negative / obligations_total) * 100, 2) if obligations_total else 0.0
    missing = [r["obligation_id"] for r in coverage_rows if not r["has_negative_test"]]
    if not obligations_total:
        status = "Needs obligation mapping"
    elif missing:
        status = "Blocked"
    else:
        status = "Pass"
    return {
        "policy": "Every source obligation that enters product/Jira/QA handoff must have at least one mapped negative test before release-ready status.",
        "release_gate_status": status,
        "obligations_total": obligations_total,
        "qa_rows_total": len(qa_rows),
        "negative_tests_total": negative_total,
        "unmapped_negative_tests": unmapped_negative,
        "obligations_with_negative_test": obligations_with_negative,
        "negative_test_coverage_rate": coverage_rate,
        "missing_negative_coverage": missing,
        "rows": coverage_rows,
    }


def negative_coverage_metrics(data: Dict[str, Any] | None) -> Dict[str, Any]:
    result = validate_negative_test_coverage(data)
    return {
        "negative_test_coverage_rate": result["negative_test_coverage_rate"],
        "negative_tests_total": result["negative_tests_total"],
        "obligations_with_negative_test": result["obligations_with_negative_test"],
        "missing_negative_tests_total": len(result["missing_negative_coverage"]),
    }

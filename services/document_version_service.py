"""Document version and impact helpers.

This gives the portfolio a concrete versioning behavior: when an imported source
changes, added/removed/changed obligations can be detected and downstream
artefacts can be marked for review.
"""
from __future__ import annotations

import difflib
from datetime import datetime, timezone
from typing import Any, Dict, List

from services.enterprise_controls_service import stable_hash
from services.lineage_service import impact_analysis


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_text(text: str) -> str:
    return " ".join((text or "").split()).strip()


def document_version_record(*, document_id: str, version: str, text: str, imported_by: str = "demo-user", source_type: str = "uploaded_text") -> Dict[str, Any]:
    normalized = normalize_text(text)
    return {
        "document_id": document_id,
        "version": version,
        "hash": stable_hash(normalized, length=64),
        "bytes": len((text or "").encode("utf-8")),
        "normalized_chars": len(normalized),
        "imported_by": imported_by,
        "source_type": source_type,
        "imported_at": utc_now(),
    }


def compare_obligation_sets(previous: List[Dict[str, Any]], current: List[Dict[str, Any]]) -> Dict[str, Any]:
    prev = {row.get("obligation_id") or row.get("id"): row for row in previous}
    curr = {row.get("obligation_id") or row.get("id"): row for row in current}
    added = [curr[k] for k in sorted(set(curr) - set(prev))]
    removed = [prev[k] for k in sorted(set(prev) - set(curr))]
    changed: List[Dict[str, Any]] = []
    for key in sorted(set(prev) & set(curr)):
        a = normalize_text(prev[key].get("obligation", ""))
        b = normalize_text(curr[key].get("obligation", ""))
        if a != b:
            changed.append({
                "obligation_id": key,
                "previous": prev[key].get("obligation", ""),
                "current": curr[key].get("obligation", ""),
                "diff_hint": " ".join(difflib.ndiff([a], [b])),
            })
    return {"added": added, "removed": removed, "changed": changed, "added_count": len(added), "removed_count": len(removed), "changed_count": len(changed)}


def hero_document_version_diff() -> Dict[str, Any]:
    previous = [
        {"obligation_id": "O-SAF-T-001", "obligation": "Validate invoice mandatory fields before export."},
        {"obligation_id": "O-SAF-T-002", "obligation": "Keep accounting traceability where applicable."},
        {"obligation_id": "O-SAF-T-003", "obligation": "Flag inconsistent totals before export."},
    ]
    current = [
        {"obligation_id": "O-SAF-T-001", "obligation": "Validate invoice mandatory fields before export, including customer tax ID and tax code."},
        {"obligation_id": "O-SAF-T-002", "obligation": "Preserve JournalID, TransactionDate and DocArchivalNumber for accounting/integrated modes."},
        {"obligation_id": "O-SAF-T-003", "obligation": "Flag inconsistent totals before export."},
        {"obligation_id": "O-SAF-T-004", "obligation": "Block critical validation failures unless corrected or explicitly reviewed."},
    ]
    diff = compare_obligation_sets(previous, current)
    impacted = []
    for row in diff["changed"] + diff["added"] + diff["removed"]:
        oid = row.get("obligation_id") or row.get("id")
        if oid:
            impacted.append({"obligation_id": oid, "impact": impact_analysis(oid).get("affected_artifacts", [])})
    return {
        "previous_document": document_version_record(document_id="DOC-SAF-T-001", version="v1", text="\n".join(r["obligation"] for r in previous)),
        "current_document": document_version_record(document_id="DOC-SAF-T-001", version="v2", text="\n".join(r["obligation"] for r in current)),
        "diff": diff,
        "impacted_downstream": impacted,
    }

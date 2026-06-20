"""Lineage and staleness helpers for portfolio artefacts.

The goal is to show a concrete enterprise AI product behavior: when an upstream
source or reviewer decision changes, downstream requirements, tickets, QA cases,
release notes and reports can become stale.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Set


def parse_time(value: str | None) -> datetime:
    if not value:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return datetime.min.replace(tzinfo=timezone.utc)


def hero_lineage_state() -> Dict[str, Any]:
    """Return a realistic lineage graph with one reviewer change making children stale."""
    artifacts = [
        {"artifact_id": "DOC-SAF-T-001", "type": "Source document", "title": "SAF-T/e-invoicing source excerpt", "updated_at": "2026-06-18T09:10:00Z", "owner": "Compliance"},
        {"artifact_id": "O-SAF-T-001", "type": "Obligation", "title": "Validate required invoice fields", "updated_at": "2026-06-18T09:12:00Z", "owner": "Product"},
        {"artifact_id": "O-SAF-T-002", "type": "Obligation", "title": "Preserve accounting journal traceability", "updated_at": "2026-06-18T09:21:00Z", "owner": "Compliance Reviewer"},
        {"artifact_id": "REQ-SAF-T-001", "type": "Requirement", "title": "Pre-export validation and traceability", "updated_at": "2026-06-18T09:18:00Z", "owner": "Product"},
        {"artifact_id": "JIRA-SAF-T-001", "type": "Jira ticket", "title": "Validate SAF-T invoice fields and traceability", "updated_at": "2026-06-18T09:19:00Z", "owner": "Engineering"},
        {"artifact_id": "QA-SAF-T-002-NEG", "type": "QA case", "title": "Missing journal traceability blocks export", "updated_at": "2026-06-18T09:20:00Z", "owner": "QA"},
        {"artifact_id": "REL-SAF-T-001", "type": "Release note", "title": "Safer release communication", "updated_at": "2026-06-18T09:27:00Z", "owner": "Support"},
        {"artifact_id": "AUD-SAF-T-001", "type": "Audit report", "title": "Final supported/weak/missing/reviewed report", "updated_at": "2026-06-18T09:30:00Z", "owner": "Product Ops"},
    ]
    links = [
        {"from": "DOC-SAF-T-001", "to": "O-SAF-T-001", "relation": "source_supports"},
        {"from": "DOC-SAF-T-001", "to": "O-SAF-T-002", "relation": "source_supports"},
        {"from": "O-SAF-T-001", "to": "REQ-SAF-T-001", "relation": "obligation_to_requirement"},
        {"from": "O-SAF-T-002", "to": "REQ-SAF-T-001", "relation": "obligation_to_requirement"},
        {"from": "REQ-SAF-T-001", "to": "JIRA-SAF-T-001", "relation": "requirement_to_jira"},
        {"from": "REQ-SAF-T-001", "to": "QA-SAF-T-002-NEG", "relation": "requirement_to_qa"},
        {"from": "REQ-SAF-T-001", "to": "REL-SAF-T-001", "relation": "requirement_to_release_claim"},
        {"from": "JIRA-SAF-T-001", "to": "AUD-SAF-T-001", "relation": "handoff_evidence"},
        {"from": "QA-SAF-T-002-NEG", "to": "AUD-SAF-T-001", "relation": "qa_evidence"},
        {"from": "REL-SAF-T-001", "to": "AUD-SAF-T-001", "relation": "communication_evidence"},
    ]
    return {"artifacts": artifacts, "links": links}


def downstream_ids(changed_artifact_id: str, links: List[Dict[str, Any]]) -> List[str]:
    graph: Dict[str, List[str]] = {}
    for link in links:
        graph.setdefault(link["from"], []).append(link["to"])
    seen: Set[str] = set()
    queue = list(graph.get(changed_artifact_id, []))
    ordered: List[str] = []
    while queue:
        current = queue.pop(0)
        if current in seen:
            continue
        seen.add(current)
        ordered.append(current)
        queue.extend(graph.get(current, []))
    return ordered


def detect_stale_artifacts(artifacts: List[Dict[str, Any]], links: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Mark child artifacts stale when any direct upstream was updated later."""
    by_id = {row["artifact_id"]: row for row in artifacts}
    stale: List[Dict[str, Any]] = []
    for link in links:
        parent = by_id.get(link["from"])
        child = by_id.get(link["to"])
        if not parent or not child:
            continue
        if parse_time(parent.get("updated_at")) > parse_time(child.get("updated_at")):
            stale.append(
                {
                    "artifact_id": child["artifact_id"],
                    "artifact_type": child.get("type", "Artifact"),
                    "title": child.get("title", ""),
                    "stale_because": f"Upstream {parent['artifact_id']} was updated at {parent.get('updated_at')} after this artifact was updated at {child.get('updated_at')}.",
                    "upstream_artifact_id": parent["artifact_id"],
                    "recommended_action": "Review or regenerate this artifact before export/release.",
                }
            )
    # de-duplicate by artifact/reason
    seen = set()
    unique: List[Dict[str, Any]] = []
    for row in stale:
        key = (row["artifact_id"], row["upstream_artifact_id"])
        if key not in seen:
            seen.add(key)
            unique.append(row)
    return unique


def impact_analysis(changed_artifact_id: str, state: Dict[str, Any] | None = None) -> Dict[str, Any]:
    state = state or hero_lineage_state()
    artifacts = state["artifacts"]
    links = state["links"]
    by_id = {row["artifact_id"]: row for row in artifacts}
    affected_ids = downstream_ids(changed_artifact_id, links)
    return {
        "changed_artifact_id": changed_artifact_id,
        "changed_artifact": by_id.get(changed_artifact_id, {}),
        "affected_artifacts": [by_id[item] for item in affected_ids if item in by_id],
        "affected_count": len(affected_ids),
    }


def timeline_events(state: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    state = state or hero_lineage_state()
    events = [
        {
            "timestamp_utc": row.get("updated_at", ""),
            "event": f"{row.get('type')} updated",
            "artifact_id": row.get("artifact_id"),
            "owner": row.get("owner", ""),
            "detail": row.get("title", ""),
        }
        for row in state.get("artifacts", [])
    ]
    return sorted(events, key=lambda row: row.get("timestamp_utc", ""))

"""Approval workflow state machine for portfolio artefacts.

This module makes review/approval behavior explicit instead of leaving it as
static documentation. It is intentionally local and deterministic so the
portfolio can demonstrate enterprise AI product judgment without pretending to
be production IAM/workflow software.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List

from services.enterprise_controls_service import stable_hash, sign_payload

APPROVAL_STATES = [
    "Draft",
    "AI-generated",
    "PM reviewed",
    "QA reviewed",
    "Compliance reviewed",
    "Approved",
    "Blocked",
    "Exported",
]

VALID_TRANSITIONS = {
    "Draft": {"AI-generated", "Blocked"},
    "AI-generated": {"PM reviewed", "Blocked"},
    "PM reviewed": {"QA reviewed", "Compliance reviewed", "Blocked"},
    "QA reviewed": {"Compliance reviewed", "Blocked"},
    "Compliance reviewed": {"Approved", "Blocked"},
    "Approved": {"Exported", "Blocked"},
    "Blocked": {"Draft", "AI-generated"},
    "Exported": set(),
}

ROLE_STATE_PERMISSIONS = {
    "Product Manager": {"AI-generated", "PM reviewed", "Blocked", "Exported"},
    "QA Lead": {"QA reviewed", "Blocked"},
    "Compliance Reviewer": {"Compliance reviewed", "Approved", "Blocked"},
    "Support Lead": {"Blocked", "Exported"},
    "Engineering Lead": {"Blocked", "Exported"},
    "Admin": set(APPROVAL_STATES),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_approval_item(artifact_id: str, artifact_type: str, title: str, state: str = "AI-generated", owner: str = "Product Manager") -> Dict[str, Any]:
    if state not in APPROVAL_STATES:
        raise ValueError(f"Unsupported approval state: {state}")
    return {
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "title": title,
        "state": state,
        "owner": owner,
        "updated_at": utc_now(),
        "history": [
            {
                "timestamp_utc": utc_now(),
                "actor": "system",
                "role": "system",
                "from_state": "",
                "to_state": state,
                "reason": "Initial approval state for portfolio workflow.",
            }
        ],
    }


def can_transition(current_state: str, target_state: str, role: str) -> Dict[str, Any]:
    transition_allowed = target_state in VALID_TRANSITIONS.get(current_state, set())
    role_allowed = target_state in ROLE_STATE_PERMISSIONS.get(role, set()) or "Admin" == role
    return {
        "current_state": current_state,
        "target_state": target_state,
        "role": role,
        "allowed": bool(transition_allowed and role_allowed),
        "transition_allowed": transition_allowed,
        "role_allowed": role_allowed,
        "reason": "Allowed" if transition_allowed and role_allowed else _transition_reason(current_state, target_state, role, transition_allowed, role_allowed),
    }


def _transition_reason(current_state: str, target_state: str, role: str, transition_allowed: bool, role_allowed: bool) -> str:
    if not transition_allowed:
        return f"Invalid state transition from {current_state} to {target_state}."
    if not role_allowed:
        return f"Role {role} is not allowed to move artefacts to {target_state}."
    return "Transition blocked."


def transition_item(item: Dict[str, Any], target_state: str, *, actor: str, role: str, reason: str = "") -> Dict[str, Any]:
    decision = can_transition(item.get("state", "Draft"), target_state, role)
    updated = {**item}
    updated.setdefault("history", list(item.get("history", [])))
    event = {
        "timestamp_utc": utc_now(),
        "actor": actor or "demo-user",
        "role": role or "Product Manager",
        "from_state": item.get("state", "Draft"),
        "to_state": target_state,
        "reason": reason or decision["reason"],
        "allowed": decision["allowed"],
    }
    if decision["allowed"]:
        updated["state"] = target_state
        updated["updated_at"] = event["timestamp_utc"]
    event["signature"] = sign_payload(event)
    updated["history"] = [*updated.get("history", []), event]
    updated["last_transition"] = event
    updated["state_signature"] = stable_hash({"artifact_id": updated.get("artifact_id"), "state": updated.get("state"), "history": updated.get("history")}, length=32)
    return updated


def approval_gate(items: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    rows = list(items)
    blocked = [row for row in rows if row.get("state") == "Blocked"]
    unapproved = [row for row in rows if row.get("state") not in {"Approved", "Exported"}]
    return {
        "status": "Blocked" if blocked else "Ready" if not unapproved else "Review required",
        "total_artifacts": len(rows),
        "approved_or_exported": len([r for r in rows if r.get("state") in {"Approved", "Exported"}]),
        "blocked": len(blocked),
        "review_required": len(unapproved) - len(blocked),
        "rows": rows,
    }


def hero_approval_workflow() -> List[Dict[str, Any]]:
    """Approval items aligned with the SAF-T hero workflow."""
    return [
        build_approval_item("O-SAF-T-001", "Obligation", "Validate required invoice fields", "Compliance reviewed", "Compliance Reviewer"),
        build_approval_item("REQ-SAF-T-001", "Requirement", "Pre-export validation and traceability", "PM reviewed", "Product Manager"),
        build_approval_item("QA-SAF-T-002-NEG", "QA case", "Missing journal traceability blocks export", "QA reviewed", "QA Lead"),
        build_approval_item("REL-SAF-T-001", "Release note", "Safer scoped release communication", "Compliance reviewed", "Support Lead"),
        build_approval_item("AUD-SAF-T-001", "Audit report", "Supported/weak/missing/reviewed report", "AI-generated", "Product Ops"),
    ]

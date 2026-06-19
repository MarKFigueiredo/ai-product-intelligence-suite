"""Pure compliance workflow assessment service.

This service adapts loosely shaped workflow dictionaries into typed domain
models. It is intentionally independent from Streamlit so it can be tested and
reused by UI, exports, reports and future integrations.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from core.compliance_models import (
    ComplianceWorkflowAssessment,
    EvidenceItem,
    Obligation,
    QACase,
    ReleaseRiskFinding,
    RequirementCandidate,
    RiskLevel,
)


def _get(mapping: Mapping[str, Any], *keys: str, default: Any = "") -> Any:
    """Return the first present, non-empty value for any of the provided keys."""

    for key in keys:
        if key in mapping and mapping[key] not in (None, ""):
            return mapping[key]
    return default


def _as_text(value: Any) -> str:
    """Normalize arbitrary values into safe display text."""

    if value is None:
        return ""
    return str(value).strip()


def _as_sequence(value: Any) -> list[Any]:
    """Normalize a value into a list while avoiding string iteration."""

    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, Mapping):
        return list(value.values())
    if isinstance(value, Sequence):
        return list(value)
    return [value]


def _as_string_tuple(value: Any) -> tuple[str, ...]:
    """Normalize a field to a tuple of non-empty strings."""

    return tuple(_as_text(item) for item in _as_sequence(value) if _as_text(item))


def normalize_risk_level(value: Any, default: RiskLevel = RiskLevel.MEDIUM) -> RiskLevel:
    """Normalize common risk labels to the domain enum."""

    text = _as_text(value).lower()

    if text in {"low", "minor", "green"}:
        return RiskLevel.LOW
    if text in {"high", "critical", "red", "blocker", "blocking"}:
        return RiskLevel.HIGH
    if text in {"medium", "moderate", "yellow", "amber", ""}:
        return default

    return default


def evidence_from_mapping(item: Mapping[str, Any]) -> EvidenceItem:
    """Build an EvidenceItem from common source/citation dictionary shapes."""

    return EvidenceItem(
        source_id=_as_text(_get(item, "source_id", "source", "source_ref", "citation_id", "document_id")),
        quote=_as_text(_get(item, "quote", "source_quote", "text", "excerpt")),
        location=_as_text(_get(item, "location", "page", "section", "line_ref")),
    )


def obligation_from_mapping(item: Mapping[str, Any]) -> Obligation:
    """Build an Obligation from common obligation dictionary shapes."""

    evidence_value = _get(item, "evidence", "citations", "sources", default=())
    evidence_items: list[EvidenceItem] = []

    for evidence in _as_sequence(evidence_value):
        if isinstance(evidence, Mapping):
            evidence_items.append(evidence_from_mapping(evidence))
        else:
            evidence_text = _as_text(evidence)
            if evidence_text:
                evidence_items.append(EvidenceItem(source_id="inline", quote=evidence_text))

    return Obligation(
        obligation_id=_as_text(_get(item, "obligation_id", "id", "key", default="OBL-UNSPECIFIED")),
        text=_as_text(_get(item, "text", "obligation", "description", "title")),
        evidence=tuple(evidence_items),
        risk_level=normalize_risk_level(_get(item, "risk_level", "risk", "severity")),
    )


def requirement_from_mapping(item: Mapping[str, Any]) -> RequirementCandidate:
    """Build a RequirementCandidate from common requirement dictionary shapes."""

    obligation_ids = _get(
        item,
        "obligation_ids",
        "source_obligation_ids",
        "linked_obligations",
        "traceability",
        default=(),
    )

    return RequirementCandidate(
        requirement_id=_as_text(_get(item, "requirement_id", "id", "key", default="REQ-UNSPECIFIED")),
        title=_as_text(_get(item, "title", "name", default="Untitled requirement")),
        description=_as_text(_get(item, "description", "body", "requirement", "text")),
        obligation_ids=_as_string_tuple(obligation_ids),
    )


def qa_case_from_mapping(item: Mapping[str, Any]) -> QACase:
    """Build a QACase from common QA/test dictionary shapes."""

    negative_value = _get(item, "is_negative", "negative", "negative_test", "type", "category", default=False)
    negative_text = _as_text(negative_value).lower()

    is_negative = bool(negative_value is True or negative_text in {"negative", "true", "yes", "1", "failure", "edge"})

    return QACase(
        case_id=_as_text(_get(item, "case_id", "test_id", "id", "key", default="QA-UNSPECIFIED")),
        title=_as_text(_get(item, "title", "name", "scenario", default="Untitled QA case")),
        requirement_id=_as_text(_get(item, "requirement_id", "req_id", "linked_requirement", default="")),
        is_negative=is_negative,
    )


def release_finding_from_mapping(item: Mapping[str, Any]) -> ReleaseRiskFinding:
    """Build a ReleaseRiskFinding from common release-risk dictionary shapes."""

    return ReleaseRiskFinding(
        claim=_as_text(_get(item, "claim", "text", "statement", default="Unspecified claim")),
        reason=_as_text(_get(item, "reason", "risk_reason", "explanation", "why")),
        suggested_wording=_as_text(_get(item, "suggested_wording", "safer_wording", "replacement", "suggestion")),
        risk_level=normalize_risk_level(_get(item, "risk_level", "risk", "severity")),
    )


def build_assessment_from_mapping(payload: Mapping[str, Any]) -> ComplianceWorkflowAssessment:
    """Build a typed assessment from a workflow payload dictionary."""

    obligations = tuple(
        obligation_from_mapping(item)
        for item in _as_sequence(_get(payload, "obligations", "generated_obligations", default=()))
        if isinstance(item, Mapping)
    )

    requirements = tuple(
        requirement_from_mapping(item)
        for item in _as_sequence(_get(payload, "requirements", "requirement_candidates", "tickets", default=()))
        if isinstance(item, Mapping)
    )

    qa_cases = tuple(
        qa_case_from_mapping(item)
        for item in _as_sequence(_get(payload, "qa_cases", "tests", "qa_matrix", default=()))
        if isinstance(item, Mapping)
    )

    release_findings = tuple(
        release_finding_from_mapping(item)
        for item in _as_sequence(_get(payload, "release_findings", "release_risks", "claim_risks", default=()))
        if isinstance(item, Mapping)
    )

    return ComplianceWorkflowAssessment(
        obligations=obligations,
        requirements=requirements,
        qa_cases=qa_cases,
        release_findings=release_findings,
    )


def summarize_release_readiness(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return a compact release-readiness summary for UI/export layers."""

    assessment = build_assessment_from_mapping(payload)
    blockers = assessment.release_ready_blockers()

    return {
        "is_release_ready": assessment.is_release_ready,
        "blocker_count": len(blockers),
        "blockers": list(blockers),
        "obligation_count": len(assessment.obligations),
        "requirement_count": len(assessment.requirements),
        "qa_case_count": len(assessment.qa_cases),
        "release_finding_count": len(assessment.release_findings),
        "has_negative_qa_coverage": assessment.has_negative_qa_coverage(),
    }

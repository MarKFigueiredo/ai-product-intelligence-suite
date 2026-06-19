from pathlib import Path

from core.compliance_models import RiskLevel
from services.compliance_assessment_service import (
    build_assessment_from_mapping,
    normalize_risk_level,
    summarize_release_readiness,
)


def test_normalize_risk_level_accepts_common_labels():
    assert normalize_risk_level("critical") is RiskLevel.HIGH
    assert normalize_risk_level("red") is RiskLevel.HIGH
    assert normalize_risk_level("minor") is RiskLevel.LOW
    assert normalize_risk_level("unknown") is RiskLevel.MEDIUM


def test_build_assessment_from_mapping_converts_loose_payload_to_domain_models():
    payload = {
        "generated_obligations": [
            {
                "id": "OBL-001",
                "obligation": "Store source-linked evidence for tax decisions.",
                "risk": "high",
                "citations": [
                    {
                        "source": "SAF-T PT",
                        "quote": "Source references must remain auditable.",
                        "section": "Header",
                    }
                ],
            }
        ],
        "requirement_candidates": [
            {
                "id": "REQ-001",
                "title": "Persist evidence metadata",
                "description": "Store source id, quote and location for reviewer inspection.",
                "linked_obligations": ["OBL-001"],
            }
        ],
        "qa_matrix": [
            {
                "id": "QA-001",
                "title": "Reject unsupported obligation",
                "linked_requirement": "REQ-001",
                "type": "negative",
            }
        ],
        "claim_risks": [
            {
                "claim": "Fully compliant for every tax case.",
                "reason": "Absolute compliance wording is unsupported.",
                "suggestion": "Supports reviewer-led checks for selected SAF-T scenarios.",
                "severity": "high",
            }
        ],
    }

    assessment = build_assessment_from_mapping(payload)

    assert assessment.obligations[0].obligation_id == "OBL-001"
    assert assessment.obligations[0].has_source_support
    assert assessment.requirements[0].is_traceable
    assert assessment.qa_cases[0].is_negative
    assert assessment.release_findings[0].blocks_release_ready_status


def test_release_readiness_summary_blocks_when_negative_qa_is_missing():
    payload = {
        "obligations": [
            {
                "id": "OBL-001",
                "text": "Store source-linked evidence.",
                "evidence": [{"source_id": "SAF-T", "quote": "Evidence must be traceable."}],
            }
        ],
        "requirements": [
            {
                "id": "REQ-001",
                "title": "Persist evidence metadata",
                "description": "Store source id, quote and location.",
                "obligation_ids": ["OBL-001"],
            }
        ],
        "qa_cases": [
            {
                "id": "QA-001",
                "title": "Accept supported obligation",
                "requirement_id": "REQ-001",
            }
        ],
    }

    summary = summarize_release_readiness(payload)

    assert summary["is_release_ready"] is False
    assert summary["blocker_count"] == 1
    assert summary["blockers"] == ["No negative QA coverage is present."]
    assert summary["has_negative_qa_coverage"] is False


def test_release_readiness_summary_passes_for_supported_traceable_negative_qa_payload():
    payload = {
        "obligations": [
            {
                "id": "OBL-001",
                "text": "Store source-linked evidence.",
                "evidence": [{"source_id": "SAF-T", "quote": "Evidence must be traceable."}],
            }
        ],
        "requirements": [
            {
                "id": "REQ-001",
                "title": "Persist evidence metadata",
                "description": "Store source id, quote and location.",
                "obligation_ids": ["OBL-001"],
            }
        ],
        "qa_cases": [
            {
                "id": "QA-NEG-001",
                "title": "Reject unsupported obligation",
                "requirement_id": "REQ-001",
                "is_negative": True,
            }
        ],
    }

    summary = summarize_release_readiness(payload)

    assert summary["is_release_ready"] is True
    assert summary["blocker_count"] == 0
    assert summary["obligation_count"] == 1
    assert summary["requirement_count"] == 1
    assert summary["qa_case_count"] == 1


def test_assessment_service_has_no_streamlit_dependency():
    service_text = Path("services/compliance_assessment_service.py").read_text(encoding="utf-8")

    assert "streamlit" not in service_text
    assert "st." not in service_text

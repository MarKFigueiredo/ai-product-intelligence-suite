from pathlib import Path

from core.compliance_models import (
    ComplianceWorkflowAssessment,
    EvidenceItem,
    Obligation,
    QACase,
    ReleaseRiskFinding,
    RequirementCandidate,
    RiskLevel,
)


def test_evidence_item_requires_source_and_quote():
    assert EvidenceItem(source_id="SAF-T", quote="TaxAccountingBasis must be populated.").is_usable
    assert not EvidenceItem(source_id="", quote="TaxAccountingBasis must be populated.").is_usable
    assert not EvidenceItem(source_id="SAF-T", quote="").is_usable


def test_obligation_without_usable_evidence_is_not_supported():
    obligation = Obligation(
        obligation_id="OBL-001",
        text="System must preserve source-linked tax evidence.",
        evidence=(EvidenceItem(source_id="", quote=""),),
    )

    assert not obligation.has_source_support


def test_assessment_blocks_release_ready_when_source_support_is_missing():
    assessment = ComplianceWorkflowAssessment(
        obligations=(
            Obligation(
                obligation_id="OBL-001",
                text="System must preserve source-linked tax evidence.",
                evidence=(),
            ),
        ),
        requirements=(
            RequirementCandidate(
                requirement_id="REQ-001",
                title="Store source evidence",
                description="Persist source ID and quote for reviewer inspection.",
                obligation_ids=("OBL-001",),
            ),
        ),
        qa_cases=(QACase(case_id="QA-001", title="Reject unsupported obligation", requirement_id="REQ-001", is_negative=True),),
    )

    blockers = assessment.release_ready_blockers()

    assert not assessment.is_release_ready
    assert "Obligation lacks source support: OBL-001" in blockers


def test_assessment_requires_negative_qa_coverage():
    assessment = ComplianceWorkflowAssessment(
        obligations=(
            Obligation(
                obligation_id="OBL-001",
                text="System must preserve source-linked tax evidence.",
                evidence=(EvidenceItem(source_id="SAF-T", quote="Tax evidence must be traceable."),),
            ),
        ),
        requirements=(
            RequirementCandidate(
                requirement_id="REQ-001",
                title="Store source evidence",
                description="Persist source ID and quote for reviewer inspection.",
                obligation_ids=("OBL-001",),
            ),
        ),
        qa_cases=(QACase(case_id="QA-001", title="Accept supported obligation", requirement_id="REQ-001"),),
    )

    assert not assessment.is_release_ready
    assert "No negative QA coverage is present." in assessment.release_ready_blockers()


def test_high_risk_release_claim_blocks_release_ready_status():
    assessment = ComplianceWorkflowAssessment(
        obligations=(
            Obligation(
                obligation_id="OBL-001",
                text="System must preserve source-linked tax evidence.",
                evidence=(EvidenceItem(source_id="SAF-T", quote="Tax evidence must be traceable."),),
            ),
        ),
        requirements=(
            RequirementCandidate(
                requirement_id="REQ-001",
                title="Store source evidence",
                description="Persist source ID and quote for reviewer inspection.",
                obligation_ids=("OBL-001",),
            ),
        ),
        qa_cases=(QACase(case_id="QA-001", title="Reject unsupported obligation", requirement_id="REQ-001", is_negative=True),),
        release_findings=(
            ReleaseRiskFinding(
                claim="Fully compliant for all tax scenarios.",
                reason="Absolute compliance claim is unsupported.",
                suggested_wording="Supports reviewer-led checks for selected SAF-T scenarios.",
                risk_level=RiskLevel.HIGH,
            ),
        ),
    )

    assert not assessment.is_release_ready
    assert "High-risk release claim: Fully compliant for all tax scenarios." in assessment.release_ready_blockers()


def test_model_layer_has_no_streamlit_dependency():
    model_text = Path("core/compliance_models.py").read_text(encoding="utf-8")

    assert "streamlit" not in model_text
    assert "st." not in model_text

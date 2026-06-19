"""Typed domain models for compliance-to-product workflows.

These models keep domain concepts separate from Streamlit rendering.
They are intentionally small and dependency-free so services and tests can use
the same contracts before UI-specific formatting is applied.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RiskLevel(str, Enum):
    """Normalized risk levels used by compliance workflow artifacts."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class EvidenceItem:
    """Source-linked evidence used to support an obligation or claim."""

    source_id: str
    quote: str
    location: str = ""

    @property
    def is_usable(self) -> bool:
        """Return whether the evidence is specific enough for review."""

        return bool(self.source_id.strip()) and bool(self.quote.strip())


@dataclass(frozen=True)
class Obligation:
    """A compliance obligation extracted from source material."""

    obligation_id: str
    text: str
    evidence: tuple[EvidenceItem, ...] = field(default_factory=tuple)
    risk_level: RiskLevel = RiskLevel.MEDIUM

    @property
    def has_source_support(self) -> bool:
        """Return whether the obligation has at least one usable evidence item."""

        return any(item.is_usable for item in self.evidence)


@dataclass(frozen=True)
class RequirementCandidate:
    """A product requirement candidate linked back to obligations."""

    requirement_id: str
    title: str
    description: str
    obligation_ids: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_traceable(self) -> bool:
        """Return whether the requirement links back to at least one obligation."""

        return bool(self.obligation_ids)


@dataclass(frozen=True)
class QACase:
    """A QA case linked to a requirement candidate."""

    case_id: str
    title: str
    requirement_id: str
    is_negative: bool = False


@dataclass(frozen=True)
class ReleaseRiskFinding:
    """A release-note or communication risk finding."""

    claim: str
    reason: str
    suggested_wording: str
    risk_level: RiskLevel = RiskLevel.MEDIUM

    @property
    def blocks_release_ready_status(self) -> bool:
        """Return whether this finding should block release-ready messaging."""

        return self.risk_level is RiskLevel.HIGH


@dataclass(frozen=True)
class ComplianceWorkflowAssessment:
    """Review summary for a compliance-to-product workflow run."""

    obligations: tuple[Obligation, ...] = field(default_factory=tuple)
    requirements: tuple[RequirementCandidate, ...] = field(default_factory=tuple)
    qa_cases: tuple[QACase, ...] = field(default_factory=tuple)
    release_findings: tuple[ReleaseRiskFinding, ...] = field(default_factory=tuple)

    def unsupported_obligations(self) -> tuple[Obligation, ...]:
        """Return obligations without usable source evidence."""

        return tuple(item for item in self.obligations if not item.has_source_support)

    def untraceable_requirements(self) -> tuple[RequirementCandidate, ...]:
        """Return requirements that do not link to source obligations."""

        return tuple(item for item in self.requirements if not item.is_traceable)

    def has_negative_qa_coverage(self) -> bool:
        """Return whether at least one negative QA case is present."""

        return any(item.is_negative for item in self.qa_cases)

    def blocking_release_findings(self) -> tuple[ReleaseRiskFinding, ...]:
        """Return release findings that should block release-ready status."""

        return tuple(item for item in self.release_findings if item.blocks_release_ready_status)

    def release_ready_blockers(self) -> tuple[str, ...]:
        """Return human-readable blockers for release-ready status."""

        blockers: list[str] = []

        for obligation in self.unsupported_obligations():
            blockers.append(f"Obligation lacks source support: {obligation.obligation_id}")

        for requirement in self.untraceable_requirements():
            blockers.append(f"Requirement lacks obligation traceability: {requirement.requirement_id}")

        if not self.has_negative_qa_coverage():
            blockers.append("No negative QA coverage is present.")

        for finding in self.blocking_release_findings():
            blockers.append(f"High-risk release claim: {finding.claim}")

        return tuple(blockers)

    @property
    def is_release_ready(self) -> bool:
        """Return whether the workflow has no release-ready blockers."""

        return not self.release_ready_blockers()

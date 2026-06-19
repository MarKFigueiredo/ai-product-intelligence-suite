"""Guided portfolio demo data and UX helpers.

The v1.04 portfolio experience is intentionally demo-friendly but not fake in its
product logic. It uses the SAF-T/e-invoicing hero case to show one complete
workflow from source input to obligation, requirement, Jira, QA, release risk,
incident and audit evidence.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from services.enterprise_controls_service import stable_hash
from services.qa_coverage_service import validate_negative_test_coverage

ROOT = Path(__file__).resolve().parents[1]
HERO_CASE_FILE = ROOT / "sample_inputs" / "hero_case_saf_t_einvoicing_deep_case.json"


PERSONA_REVIEW_PATHS: Dict[str, Dict[str, Any]] = {
    "Recruiter": {
        "goal": "Understand in 90 seconds what the project proves about the candidate.",
        "start_here": ["Guided hero demo", "What this demonstrates", "Portfolio review guide"],
        "look_for": ["Clear problem framing", "Senior AI PM signal", "Concrete artefacts", "Honest limitations"],
    },
    "Hiring Manager": {
        "goal": "Evaluate whether this demonstrates AI PM/product judgment for regulated enterprise workflows.",
        "start_here": ["Hero workflow", "Synthetic + real metrics", "Product strategy", "Trade-offs"],
        "look_for": ["Workflow design", "Evaluation discipline", "Risk controls", "Cross-functional thinking"],
    },
    "Principal PM": {
        "goal": "Assess systems thinking, sequencing, operating model and trade-offs.",
        "start_here": ["Release gate dashboard", "Lineage & staleness", "Product strategy", "Run comparison"],
        "look_for": ["Wedge clarity", "Downstream impact analysis", "Decision quality", "Metrics that inform learning"],
    },
    "QA Lead": {
        "goal": "Check whether obligations become testable coverage, including negative/failure paths.",
        "start_here": ["QA coverage", "Negative test gate", "Failure mode explorer"],
        "look_for": ["Mapped negative tests", "Blocked gate when coverage is missing", "Stale QA detection"],
    },
    "Compliance Reviewer": {
        "goal": "Assess support evidence, review workflow, approval and auditability.",
        "start_here": ["Evidence drawer", "Reviewer workbench", "Audit report", "Real vs simulated"],
        "look_for": ["Source support", "Reviewer decisions", "No legal overclaims", "Traceable exports"],
    },
    "Engineering Lead": {
        "goal": "Check what is implemented locally, what is simulated, and how handoff payloads are shaped.",
        "start_here": ["Real vs simulated", "Connector handoff", "SQLite metrics", "Architecture docs"],
        "look_for": ["Separation of concerns", "Persistent usage data", "Connector fallback", "Production gaps stated honestly"],
    },
}


SKILL_EVIDENCE: List[Dict[str, str]] = [
    {
        "skill": "Domain understanding",
        "evidence": "SAF-T PT/e-invoicing hero case with obligations, accounting traceability, validation and release communication risk.",
        "why_it_matters": "Shows ability to reason in compliance-heavy enterprise software, not only generic AI tooling.",
    },
    {
        "skill": "AI workflow design",
        "evidence": "Source → obligation → reviewer correction → requirement → Jira → QA → release note → incident → audit report.",
        "why_it_matters": "Shows a complete operating workflow rather than one-off prompt output.",
    },
    {
        "skill": "Human-in-the-loop review",
        "evidence": "Reviewer statuses, corrections, downstream impact and approval gates.",
        "why_it_matters": "Enterprise AI needs accountability before outputs affect customers or releases.",
    },
    {
        "skill": "QA/product quality judgment",
        "evidence": "Mandatory negative test coverage and release gate blocking when only happy-path tests exist.",
        "why_it_matters": "Shows that product readiness includes failure paths, not just PRD text.",
    },
    {
        "skill": "Risk-aware communication",
        "evidence": "Claim → risk → reason → safer rewrite; release note overclaim prevention.",
        "why_it_matters": "Reduces compliance/support risk from unsafe external messaging.",
    },
    {
        "skill": "Evaluation discipline",
        "evidence": "Synthetic benchmark plus real usage metrics persisted to SQLite and exportable as JSON/CSV/ZIP.",
        "why_it_matters": "Shows measurement thinking and honesty about synthetic vs observed data.",
    },
    {
        "skill": "Enterprise readiness judgment",
        "evidence": "Role simulation, audit store, document hashes, signed report manifest and local connector outbox.",
        "why_it_matters": "Shows production awareness without pretending the prototype is full SaaS.",
    },
    {
        "skill": "Product strategy",
        "evidence": "ICP, personas, buyer, wedge, adoption path, metrics, pricing hypothesis, risks and roadmap.",
        "why_it_matters": "Shows product leadership altitude beyond feature generation.",
    },
]


REAL_VS_SIMULATED: List[Dict[str, str]] = [
    {"capability": "SQLite usage metrics store", "status": "Real local", "note": "Workflow runs, metric snapshots and data events are persisted locally."},
    {"capability": "Import/export JSON/CSV/ZIP", "status": "Real local", "note": "Usage datasets and local output packages can be exported/imported."},
    {"capability": "Document/output hashes", "status": "Real local", "note": "SHA-256-style hashes preserve provenance without storing raw confidential text by default."},
    {"capability": "Mandatory negative test gate", "status": "Real local", "note": "Release readiness blocks obligations without mapped negative tests."},
    {"capability": "Connector outbox", "status": "Real local", "note": "Jira/GitHub/Slack payloads are written to a local reviewable outbox."},
    {"capability": "Jira/GitHub/Slack live send", "status": "Optional", "note": "Available only when credentials are configured and live mode is explicitly enabled."},
    {"capability": "RBAC", "status": "Simulated", "note": "Roles and permissions demonstrate product behavior; not production SSO/RBAC."},
    {"capability": "SSO/multi-tenancy/encrypted storage", "status": "Not implemented", "note": "Documented as production roadmap items, not claimed as portfolio functionality."},
    {"capability": "Immutable audit logs", "status": "Not implemented", "note": "Local signed events exist; production-grade immutability would require append-only storage and admin controls."},
]


GUIDED_STEPS: List[Dict[str, str]] = [
    {"step": "1", "title": "Source", "outcome": "Document scope is captured with a hash and review boundary."},
    {"step": "2", "title": "Obligations", "outcome": "Source-backed obligations get stable IDs for traceability."},
    {"step": "3", "title": "Review", "outcome": "Human corrections are saved as reusable feedback examples."},
    {"step": "4", "title": "Requirement", "outcome": "Vague wording becomes scoped, testable and evidence-aware."},
    {"step": "5", "title": "QA gate", "outcome": "Every obligation needs mapped negative/failure coverage."},
    {"step": "6", "title": "Safer release", "outcome": "Risky external claims are rewritten with scope and caveats."},
    {"step": "7", "title": "Audit trail", "outcome": "The package shows supported, weak, missing and reviewed artefacts."},
    {"step": "8", "title": "Learning loop", "outcome": "Usage metrics and reviewer feedback become evidence for future runs."},
]


def load_hero_case() -> Dict[str, Any]:
    """Load the deep SAF-T/e-invoicing case, with fallback sample data."""
    if HERO_CASE_FILE.exists():
        return json.loads(HERO_CASE_FILE.read_text(encoding="utf-8"))
    return {
        "case_name": "SAF-T PT / E-invoicing Compliance-to-Product Traceability",
        "input_document_excerpt": "Synthetic realistic portfolio case, not legal guidance.",
        "obligations": [],
        "before_requirement": "The system should validate SAF-T invoice data before export.",
        "after_requirement": "The system must validate SAF-T invoice records before export with accounting traceability where applicable.",
    }


def hero_output_shape() -> Dict[str, Any]:
    """Return an Interpret/Discover-like output used by gates and pages."""
    case = load_hero_case()
    obligations = case.get("obligations", []) or []
    obligation_rows = [
        {
            "obligation_id": row.get("id", f"O{idx+1}"),
            "obligation": row.get("obligation", ""),
            "review_status": row.get("review_status", "Needs review"),
        }
        for idx, row in enumerate(obligations)
        if row.get("review_status") != "Incorrect"
    ]
    qa_cases = [
        {
            "test_id": "QA-SAF-T-001-POS",
            "obligation_id": "O-SAF-T-001",
            "type": "Positive",
            "scenario": "Valid invoice with tax ID, date, tax code, total and AccountID passes pre-export validation.",
            "expected_result": "Invoice is eligible for export.",
        },
        {
            "test_id": "QA-SAF-T-001-NEG",
            "obligation_id": "O-SAF-T-001",
            "type": "Negative",
            "scenario": "Invoice missing CustomerTaxID is blocked before export.",
            "expected_result": "Validation error includes failed field and owner.",
        },
        {
            "test_id": "QA-SAF-T-002-NEG",
            "obligation_id": "O-SAF-T-002",
            "type": "Negative",
            "scenario": "Integrated accounting export missing JournalID/TransactionDate/DocArchivalNumber is blocked.",
            "expected_result": "Export cannot be finalized until traceability is corrected or reviewed.",
        },
        {
            "test_id": "QA-SAF-T-003-NEG",
            "obligation_id": "O-SAF-T-003",
            "type": "Edge",
            "scenario": "Inconsistent invoice total is flagged before export and appears in the validation report.",
            "expected_result": "Record is flagged with severity, reason and correction status.",
        },
        {
            "test_id": "QA-SAF-T-004-NEG",
            "obligation_id": "O-SAF-T-004",
            "type": "Failure",
            "scenario": "Critical validation failure cannot be exported without authorized Compliance Reviewer override.",
            "expected_result": "Release gate is blocked unless correction or override evidence exists.",
        },
    ]
    return {
        "case_name": case.get("case_name"),
        "input_document_excerpt": case.get("input_document_excerpt"),
        "input_document_hash": stable_hash(case.get("input_document_excerpt", ""), length=64),
        "obligation_extraction": obligation_rows,
        "reviewer_corrections": [
            {
                "obligation_id": "O-SAF-T-002",
                "from": "Needs review",
                "to": "Correct with clarification",
                "reason": "Requirement must explicitly preserve JournalID, TransactionDate and DocArchivalNumber in accounting/integrated modes.",
                "downstream_impact": ["REQ-SAF-T-002", "JIRA-SAF-T-002", "QA-SAF-T-002-NEG", "REL-SAF-T-001"],
            },
            {
                "obligation_id": "O-SAF-T-009",
                "from": "Generated obligation",
                "to": "Incorrect / removed",
                "reason": "Source requires evidence, reviewer decisions, document version hash and timestamp; it does not require storing source text indefinitely.",
                "downstream_impact": ["AUD-SAF-T-001", "RETENTION-POLICY"],
            },
        ],
        "product_requirements": [
            {
                "requirement_id": "REQ-SAF-T-001",
                "requirement": case.get("after_requirement"),
                "source_obligations": ["O-SAF-T-001", "O-SAF-T-002", "O-SAF-T-003", "O-SAF-T-004"],
                "status": "Review-ready",
            }
        ],
        "jira_tickets": [
            {
                "issue_key": "JIRA-SAF-T-001",
                "summary": case.get("jira_story_summary"),
                "type": "Story",
                "acceptance_criteria": [
                    "Validate required invoice fields before export.",
                    "Block critical failures unless corrected or authorized reviewer override exists.",
                    "Preserve accounting journal traceability for accounting/integrated modes.",
                    "Create validation report evidence with failed field, severity, reason, owner and correction status.",
                ],
                "linked_obligations": ["O-SAF-T-001", "O-SAF-T-002", "O-SAF-T-003", "O-SAF-T-004"],
            }
        ],
        "qa_test_cases": qa_cases,
        "claim_risk_table": [
            {
                "claim_id": "REL-SAF-T-001",
                "claim": case.get("risky_release_note"),
                "risk": "High",
                "reason": "Guarantees legal compliance and all incorrect filings, which is broader than the supported feature behavior.",
                "safer_rewrite": case.get("safer_release_note"),
            }
        ],
        "incident_if_missed": case.get("incident_if_missed"),
        "audit_report": {
            "supported": ["field validation", "accounting traceability where applicable", "validation report evidence"],
            "weak": ["legal compliance outcome cannot be guaranteed by product behavior alone"],
            "missing": [],
            "reviewed": ["O-SAF-T-002 clarified", "O-SAF-T-009 removed"],
            "blocked": [],
        },
    }


def release_gate_dashboard(output: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Compute visible release gates for the guided hero demo."""
    output = output or hero_output_shape()
    negative_gate = validate_negative_test_coverage(output)
    obligations = output.get("obligation_extraction", []) or []
    reviewer_corrections = output.get("reviewer_corrections", []) or []
    requirements = output.get("product_requirements", []) or []
    qa = output.get("qa_test_cases", []) or []
    claim_risks = output.get("claim_risk_table", []) or []
    high_risk = [r for r in claim_risks if str(r.get("risk", "")).lower() in {"high", "critical"}]
    gates = [
        {"gate": "Obligations extracted", "status": "Passed" if obligations else "Blocked", "reason": f"{len(obligations)} obligation(s) available."},
        {"gate": "Reviewer corrections completed", "status": "Passed" if reviewer_corrections else "Warning", "reason": f"{len(reviewer_corrections)} correction(s) recorded."},
        {"gate": "Requirements mapped", "status": "Passed" if requirements else "Blocked", "reason": f"{len(requirements)} requirement artefact(s) linked."},
        {"gate": "QA coverage", "status": "Passed" if qa else "Blocked", "reason": f"{len(qa)} QA case(s) linked."},
        {"gate": "Mandatory negative test coverage", "status": "Passed" if negative_gate["release_gate_status"] == "Pass" else "Blocked", "reason": f"{negative_gate['negative_test_coverage_rate']}% obligation-level negative coverage."},
        {"gate": "Unsupported/high-risk claims", "status": "Warning" if high_risk else "Passed", "reason": f"{len(high_risk)} high-risk claim(s) require safer rewrite."},
        {"gate": "Audit report export", "status": "Ready", "reason": "Supported, weak, missing and reviewed sections available."},
    ]
    overall = "Blocked" if any(row["status"] == "Blocked" for row in gates) else ("Warning" if any(row["status"] == "Warning" for row in gates) else "Ready")
    return {
        "overall_status": overall,
        "overall_reason": "Release cannot be considered ready while blocked gates remain." if overall == "Blocked" else "Release can proceed only after warnings are reviewed." if overall == "Warning" else "All visible gates are passed.",
        "gates": gates,
        "negative_gate": negative_gate,
    }


def evidence_drawer_items(output: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    """Return evidence cards used by the UI drawer/expander."""
    output = output or hero_output_shape()
    source_hash = output.get("input_document_hash")
    source_excerpt = output.get("input_document_excerpt", "")
    items: List[Dict[str, Any]] = []
    for obligation in output.get("obligation_extraction", []) or []:
        oid = obligation.get("obligation_id")
        linked_req = [r.get("requirement_id") for r in output.get("product_requirements", []) if oid in (r.get("source_obligations") or [])]
        linked_qa = [q.get("test_id") for q in output.get("qa_test_cases", []) if q.get("obligation_id") == oid]
        items.append(
            {
                "artifact_id": oid,
                "artifact_type": "Obligation",
                "support_status": "Reviewed" if obligation.get("review_status", "").startswith("Correct") else "Needs review",
                "source_excerpt": source_excerpt[:420] + ("..." if len(source_excerpt) > 420 else ""),
                "source_hash": source_hash,
                "reviewer_decision": obligation.get("review_status", "Needs review"),
                "linked_requirement": ", ".join(linked_req) or "Missing",
                "linked_qa": ", ".join(linked_qa) or "Missing",
                "last_modified": "2026-06-18T09:20:00Z",
            }
        )
    for claim in output.get("claim_risk_table", []) or []:
        items.append(
            {
                "artifact_id": claim.get("claim_id", "REL-CLAIM"),
                "artifact_type": "Release claim",
                "support_status": "High risk / safer rewrite required",
                "source_excerpt": claim.get("claim", ""),
                "source_hash": stable_hash(claim.get("claim", ""), length=64),
                "reviewer_decision": "Rewrite required before external publication",
                "linked_requirement": "REQ-SAF-T-001",
                "linked_qa": "QA-SAF-T-001-NEG, QA-SAF-T-002-NEG",
                "last_modified": "2026-06-18T09:27:00Z",
                "safer_rewrite": claim.get("safer_rewrite"),
            }
        )
    return items

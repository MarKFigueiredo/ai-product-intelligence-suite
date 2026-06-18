"""Prompt for Compliance-to-Product Studio."""
from __future__ import annotations

import json
from typing import Dict, List, Optional

from services.rag_service import SourceChunk, build_source_context


def build_compliance_prompt(inputs: Dict[str, str], sources: List[SourceChunk], comparison_sources: Optional[List[SourceChunk]] = None) -> str:
    schema = {
        "executive_summary": "string",
        "obligation_extraction": [{"obligation_id": "O1", "obligation": "string", "mandatory_fields": "string", "deadline_or_timing": "string", "exceptions": "string", "source": "[S1]", "quote_support": "exact short quote from cited source", "model_confidence": "High/Medium/Needs review", "human_review": "string"}],
        "traceability_matrix": [{"source": "[S1]", "obligation": "string", "product_impact": "string", "data_field": "string", "validation_rule": "string", "test_case": "string", "release_note": "string", "quote_support": "exact short quote from cited source", "model_confidence": "High/Medium/Needs legal review"}],
        "product_requirements": [{"requirement_id": "R1", "requirement": "string", "source": "[S1]", "quote_support": "exact short quote from cited source", "implementation_readiness": "Ready/Needs SME review/Needs legal review/Needs engineering discovery"}],
        "validation_rules": [{"rule_id": "VR1", "field": "string", "logic": "string", "failure_message": "string", "source": "[S1]", "quote_support": "exact short quote from cited source"}],
        "qa_test_cases": [{"test_id": "TC1", "obligation_id": "O1", "type": "Positive/Negative/Edge", "scenario": "string", "steps": "string", "expected_result": "string", "source": "[S1]"}],
        "negative_test_coverage": [{"obligation_id": "O1", "negative_test": "string", "owner": "QA", "evidence_required": "string"}],
        "qa_release_gate": {"status": "Pass/Blocked", "rule": "Every obligation requires at least one mapped negative test", "negative_test_coverage_rate": 1},
        "version_comparison": [{"change_type": "Added/Removed/Changed/Unclear", "old_obligation": "string", "new_obligation": "string", "product_action": "string", "risk": "string"}],
        "source_quote_candidates": [{"claim": "string", "citation": "[S1]", "quote_support": "short quote from cited source"}],
        "human_review_queue": [{"item": "string", "reason": "string", "reviewer": "Compliance/Legal/Product/Engineering"}],
        "decision_log": [{"decision": "string", "owner": "string", "reason": "string", "evidence": "source/obligation id", "status": "Open/Recommended/Approved/Rejected"}],
        "source_coverage_summary": "string",
        "risks": [{"risk": "string", "severity": "Low/Medium/High", "mitigation": "string"}],
        "open_questions": ["string"],
    }
    comparison_context = build_source_context(comparison_sources or [])
    return f"""
You are a Regulatory Product Intelligence Assistant for compliance-heavy enterprise software.
Return ONLY valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Business context: {inputs.get('business_context','')}
Target product/module: {inputs.get('target_module','')}
Persona: {inputs.get('persona','')}
Focus: {inputs.get('focus','')}
Output language: {inputs.get('language','English')}
Detail level: {inputs.get('detail','Standard')}

Current source excerpts. Every material product claim must cite one or more of these source IDs exactly, for example [S1].
{build_source_context(sources)}

Previous/version comparison excerpts, if provided:
{comparison_context if comparison_context else 'No previous document provided.'}

Premium requirements:
- Extract obligations, mandatory fields, deadlines/timing, validation logic, reporting requirements, exceptions, and risks.
- Produce traceability: Source | Obligation | Product impact | Data field | Validation rule | Test case | Release note.
- Mandatory negative test coverage: for every obligation_id, include at least one mapped Negative or Edge qa_test_case that proves the system rejects, blocks or flags invalid/missing/exception data.
- Add negative_test_coverage and qa_release_gate. If any obligation lacks negative coverage, set qa_release_gate.status to Blocked and name the missing obligation.
- For every obligation, requirement and validation rule, include a quote_support value copied from the cited source. Do not paraphrase quote_support. The application will separately check whether the quote is actually present in the source.
- Include source_quote_candidates with short source quotes that appear to support material claims. The application will verify those quotes with a separate rule-based citation support checker.
- Do not invent legal obligations. Use Needs review when unclear.
- Do not invent numeric grounding or readiness scores. Use textual confidence only. External rule-based checks will compute support scores after generation. Include human-in-the-loop review flags.
- If a claim is only partially supported, write Needs review and explain the uncertainty in the human_review_queue.
- Include a decision_log capturing interpretation decisions, owner, evidence and status.
- The application will persist run/review metadata locally and let reviewers mark obligations correct/incorrect/needs-review.
- Include a version comparison if previous document excerpts are provided.
"""

"""Prompt for Release Readiness Copilot."""
from __future__ import annotations

import json
from typing import Dict


def build_release_prompt(inputs: Dict[str, str]) -> str:
    schema = {
        "executive_summary": "string",
        "customer_facing_release_note": "string",
        "internal_support_note": "string",
        "engineering_summary": "string",
        "customer_success_talking_points": ["string"],
        "interpret_discover_links": [{"upstream_item": "string", "release_asset": "string", "risk_or_note": "string"}],
        "before_after_behaviour": [{"before": "string", "after": "string", "customer_impact": "string"}],
        "before_after_copy_examples": [{"before_claim": "string", "risk": "string", "after_safer_copy": "string"}],
        "support_faq": [{"question": "string", "answer": "string"}],
        "qa_checklist": [{"check": "string", "owner": "string", "status": "Not started", "risk_if_missed": "string"}],
        "known_limitations": ["string"],
        "audience_risk_scoring": [{"audience": "Customer/Support/QA/Engineering/Executive/Compliance", "risk_score": 1, "risk_reason": "string", "recommended_tone": "string"}],
        "sentence_risk_review": [{"sentence_or_claim": "string", "risk": "Low/Medium/High", "reason": "string", "safer_rewrite": "string", "risk_score": 1}],
        "claim_safety_review": [{"risky_claim": "string", "classification": "Risky/Ambiguous/Overclaiming/Safe", "why_risky": "string", "safer_rewrite": "string", "risk_score": 1}],
        "what_not_to_say": ["string"],
        "approval_workflow": [{"team": "Product/QA/Support/Legal/Compliance", "approval_scope": "string", "owner": "string", "required_before_release": True, "status": "Required/Approved/Blocked"}],
        "release_approval_checklist": [{"approval_item": "string", "owner": "string", "required_before_release": True, "status": "Required/Approved/Blocked"}],
        "screenshot_placeholders": [{"screenshot": "Before/After/Error/Success", "purpose": "string", "caption": "string"}],
        "confluence_export_outline": [{"section": "string", "content": "string"}],
        "zendesk_support_macro": "string",
        "customer_escalation_note": {"when_to_escalate": "string", "customer_safe_wording": "string", "compliance_boundary": "string"},
        "open_questions": ["string"],
    }
    return f"""
You are an Enterprise Release Readiness Copilot.
Return ONLY valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Technical change notes:
{inputs.get('technical_notes','')}

Upstream Interpret/Discover context, if provided:
{inputs.get('upstream_context','No upstream context provided.')}

Audience: {inputs.get('audience','')}
Product context: {inputs.get('product_context','')}
Release type: {inputs.get('release_type','')}
Compliance sensitivity: {inputs.get('compliance_sensitivity','')}
Output language: {inputs.get('language','English')}
Detail level: {inputs.get('detail','Standard')}

Premium requirements:
- Separate customer-facing, support, engineering, customer success, QA and executive language.
- Include sentence-level risk review: sentence_or_claim → risk → reason → safer_rewrite.
- Include audience risk scoring and risky claim rewrites with classification and numeric risk_score from 1 to 100.
- Include approval workflow by Product, QA, Support and Legal/Compliance.
- Include what not to say to customers.
- Include realistic before/after copy examples, not generic placeholders.
- Link release assets to upstream Interpret/Discover outputs where possible.
- Include customer escalation and compliance-boundary wording.
- Include release approval checklist, screenshot placeholders, known limitations, FAQ, QA checklist.
- Add Confluence export outline and Zendesk-style support macro.
"""

"""Declarative core pipeline for the portfolio hero workflow.

This module keeps the product thesis visible in code instead of hiding the
Interpret → Review → Discover chain inside Streamlit pages. It intentionally
stays lightweight: orchestration, guardrail calls, and run summaries live here;
UI rendering stays in modules/ui and domain-specific heuristics stay in services.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Sequence

from services.citation_verifier import grounding_summary, verify_citations_advanced
from services.human_feedback_service import (
    apply_feedback_examples_to_output,
    feedback_examples_for_next_run,
    summarize_feedback_inventory,
)
from services.product_quality_service import compute_prd_rule_completeness
from services.qa_coverage_service import validate_negative_test_coverage
from services.rag_service import SourceChunk


@dataclass(frozen=True)
class PipelineStep:
    """Declarative representation of one pipeline step."""

    step_id: str
    title: str
    owner: str
    input_artifact: str
    output_artifact: str
    gate: str = ""


@dataclass
class PipelineResult:
    """Structured output from the core compliance-to-product pipeline."""

    output: Dict[str, Any]
    steps: List[Dict[str, Any]]
    citation_rows: List[Dict[str, Any]] = field(default_factory=list)
    grounding: Dict[str, Any] = field(default_factory=dict)
    negative_gate: Dict[str, Any] = field(default_factory=dict)
    prd_completeness: Dict[str, Any] = field(default_factory=dict)
    feedback_summary: Dict[str, Any] = field(default_factory=dict)
    feedback_examples: List[Dict[str, Any]] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "output": self.output,
            "steps": self.steps,
            "citation_rows": self.citation_rows,
            "grounding": self.grounding,
            "negative_gate": self.negative_gate,
            "prd_completeness": self.prd_completeness,
            "feedback_summary": self.feedback_summary,
            "feedback_examples": self.feedback_examples,
        }


PIPELINE_STEPS: List[PipelineStep] = [
    PipelineStep("interpret", "Extract obligations", "AI + Product", "source_document", "obligations", "source_required"),
    PipelineStep("verify", "Verify citation support", "System", "obligations", "citation_rows", "weak_claims_to_review"),
    PipelineStep("review", "Apply human feedback", "Reviewer", "citation_rows", "reviewed_obligations", "review_decisions_saved"),
    PipelineStep("discover", "Map to requirements", "Product", "reviewed_obligations", "requirements_and_jira", "traceability_required"),
    PipelineStep("qa", "Evaluate QA coverage", "QA", "requirements_and_jira", "qa_cases", "negative_tests_required"),
    PipelineStep("release", "Calculate release readiness", "Product + Compliance", "qa_cases", "release_gate", "no_blocking_gaps"),
    PipelineStep("learn", "Persist learning signals", "Product Ops", "review_decisions", "feedback_examples", "future_runs_can_use_feedback"),
]


def pipeline_plan() -> List[Dict[str, Any]]:
    """Return the public pipeline plan as simple dictionaries for UI/tests."""
    return [step.__dict__.copy() for step in PIPELINE_STEPS]


def _step_status(step: PipelineStep, context: Dict[str, Any]) -> str:
    if step.step_id == "verify" and context.get("citation_rows"):
        weak = context.get("grounding", {}).get("weak_or_missing_claims", 0)
        return "Review required" if weak else "Pass"
    if step.step_id == "qa" and context.get("negative_gate"):
        return context["negative_gate"].get("release_gate_status", "Not evaluated")
    if step.step_id == "learn" and context.get("feedback_summary"):
        used = context["feedback_summary"].get("feedback_examples_used", 0)
        return "Applied" if used else "No prior examples"
    return "Completed"


def _materialize_steps(context: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for idx, step in enumerate(PIPELINE_STEPS, start=1):
        rows.append({
            "step": idx,
            "step_id": step.step_id,
            "title": step.title,
            "owner": step.owner,
            "input": step.input_artifact,
            "output": step.output_artifact,
            "gate": step.gate,
            "status": _step_status(step, context),
        })
    return rows


def run_interpret_review_discover_pipeline(
    output: Dict[str, Any],
    *,
    sources: Sequence[SourceChunk] | None = None,
    domain: str = "",
    include_feedback: bool = True,
    feedback_lookup: Callable[..., List[Dict[str, Any]]] | None = None,
) -> PipelineResult:
    """Run the local guardrail pipeline around a generated Interpret/Discover output.

    The model generation itself is intentionally outside this function. This
    pipeline makes the non-generative controls composable and unit-testable:
    citation verification, reviewer feedback reuse, negative QA gates, PRD
    completeness, and structured step status.
    """
    working_output: Dict[str, Any] = dict(output or {})
    source_list = list(sources or [])

    citation_rows = verify_citations_advanced(working_output, source_list) if source_list else []
    grounding = grounding_summary(citation_rows) if citation_rows else {
        "checked_claims": 0,
        "weak_or_missing_claims": 0,
        "human_review_required": False,
        "average_support_score": 0,
    }

    examples: List[Dict[str, Any]] = []
    feedback_summary: Dict[str, Any] = summarize_feedback_inventory(domain=domain)
    if include_feedback:
        lookup = feedback_lookup or feedback_examples_for_next_run
        examples = lookup(domain=domain, limit=5)
        working_output, applied = apply_feedback_examples_to_output(working_output, examples)
        feedback_summary.update(applied)

    negative_gate = validate_negative_test_coverage(working_output)
    prd_completeness = compute_prd_rule_completeness(working_output)
    context = {
        "citation_rows": citation_rows,
        "grounding": grounding,
        "negative_gate": negative_gate,
        "feedback_summary": feedback_summary,
    }
    steps = _materialize_steps(context)
    working_output["_pipeline"] = {
        "steps": steps,
        "feedback_summary": feedback_summary,
        "negative_gate_status": negative_gate.get("release_gate_status"),
    }
    return PipelineResult(
        output=working_output,
        steps=steps,
        citation_rows=citation_rows,
        grounding=grounding,
        negative_gate=negative_gate,
        prd_completeness=prd_completeness,
        feedback_summary=feedback_summary,
        feedback_examples=examples,
    )

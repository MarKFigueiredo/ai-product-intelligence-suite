"""Reviewer and run-history UI panel for the compliance studio."""

from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from services.enterprise_controls_service import (
    can,
    document_version_record,
    record_audit_event,
    signed_report_manifest,
)
from services.human_feedback_service import record_human_reviews, summarize_feedback_inventory
from services.rag_service import (
    SourceChunk,
)
from services.run_history_service import (
    append_review_report,
    append_run_history,
    build_final_review_report,
    build_reviewer_items,
    compare_recent_runs,
    load_run_history,
    summarise_interpret_run,
)
from services.run_history_service import (
    stable_hash as run_stable_hash,
)
from ui.visual_components import (
    render_metric_pill,
)


def render_reviewer_and_run_history_panel(
    data: Dict[str, Any],
    citation_rows: List[Dict[str, Any]],
    current_text: str,
    sources: List[SourceChunk],
    settings: Dict[str, Any],
) -> None:
    st.subheader("Reviewer mode and persistent run history")
    st.caption(
        "Reviewer mode turns generated obligations into explicit correct/incorrect/needs-review decisions. "
        "Run history stores privacy-conscious metadata and metrics locally so runs can be compared over time."
    )

    reviewer_items = build_reviewer_items(data, citation_rows)
    if reviewer_items:
        st.markdown("**Reviewer mode — obligation verdicts**")
        decisions: List[Dict[str, Any]] = []
        for idx, item in enumerate(reviewer_items):
            with st.container(border=True):
                st.write(f"**{item.get('obligation_id')} — {item.get('claim')}**")
                st.write(f"Citation: {item.get('citation')} · Support: {item.get('support_score')}% · Status: {item.get('support_status')}")
                if item.get("best_supporting_quote"):
                    st.caption(f"Quote: {item.get('best_supporting_quote')}")
                options = ["Correct", "Needs review", "Incorrect"]
                default = item.get("default_status", "Needs review")
                default_idx = options.index(default) if default in options else 1
                status = st.radio(
                    "Reviewer verdict",
                    options,
                    index=default_idx,
                    horizontal=True,
                    key=f"review_status_{item.get('obligation_id')}_{idx}",
                )
                comment = st.text_input(
                    "Reviewer comment / evidence needed",
                    value=item.get("review_reason", ""),
                    key=f"review_comment_{item.get('obligation_id')}_{idx}",
                )
                correction = st.text_input(
                    "Optional corrected wording",
                    value="",
                    key=f"review_correction_{item.get('obligation_id')}_{idx}",
                    help="Saved corrections can be reused as local few-shot examples in future runs.",
                )
                decisions.append({
                    "obligation_id": item.get("obligation_id"),
                    "artifact_id": item.get("obligation_id"),
                    "artifact_type": "obligation",
                    "status": status,
                    "comment": comment,
                    "corrected_text": correction,
                    "original_text": item.get("claim", ""),
                })
    else:
        st.info("No obligation-level reviewer items were available for this run.")
        decisions = []

    report = build_final_review_report(data, citation_rows, decisions)
    st.markdown("**Final report — supported, weak, missing, reviewed**")
    cols = st.columns(4)
    summary = report.get("summary", {})
    with cols[0]:
        render_metric_pill("Supported", str(summary.get("supported", 0)), "good")
    with cols[1]:
        render_metric_pill("Weak", str(summary.get("weak", 0)), "mid")
    with cols[2]:
        render_metric_pill("Missing", str(summary.get("missing", 0)), "bad" if summary.get("missing") else "good")
    with cols[3]:
        render_metric_pill("Reviewed", str(summary.get("reviewed", 0)), "good" if summary.get("reviewed") else "mid")

    actor = settings.get("demo_user", "demo-user")
    role = settings.get("role", "Product Manager")
    inventory = summarize_feedback_inventory(domain="SAF-T invoice export validation")
    st.markdown("**Human feedback flywheel**")
    fcols = st.columns(3)
    with fcols[0]:
        render_metric_pill("Stored reviews", str(inventory.get("human_reviews_total", 0)), "good" if inventory.get("human_reviews_total", 0) else "mid")
    with fcols[1]:
        render_metric_pill("Reusable examples", str(inventory.get("feedback_examples_available", 0)), "good" if inventory.get("feedback_examples_available", 0) else "mid")
    with fcols[2]:
        applied = data.get("_human_feedback", {}) if isinstance(data.get("_human_feedback"), dict) else {}
        render_metric_pill("Adjusted this run", str(applied.get("obligations_adjusted_by_feedback", 0)), "mid" if applied.get("obligations_adjusted_by_feedback", 0) else "neutral")
    if decisions and st.button("Save reviewer decisions to human feedback flywheel", width="stretch"):
        saved = record_human_reviews(
            decisions,
            domain="SAF-T invoice export validation",
            document_hash=run_stable_hash(current_text),
            reviewer_role=role,
            reviewer_name=actor,
        )
        st.success(f"Saved {len(saved)} human review decision(s). Future runs can retrieve these as local few-shot examples.")

    c1, c2, c3, c4 = st.columns(4)
    report_json = __import__("json").dumps(report, ensure_ascii=False, indent=2)
    doc_version = document_version_record(
        document_name="interpret_current_source",
        content=current_text,
        uploaded_by=actor,
        role=role,
        version_label="current-run",
    )
    manifest = signed_report_manifest(
        report=report,
        signer=actor,
        signer_role=role,
        document_hash=doc_version["document_hash"],
        approval_status="Signed" if can(role, "sign_report") else "Draft only - role cannot sign",
    )
    manifest_json = __import__("json").dumps(manifest, ensure_ascii=False, indent=2)
    with c1:
        st.download_button("Download final review report JSON", report_json.encode("utf-8"), "interpret_final_review_report.json", "application/json", width="stretch", key="download_interpret_final_review_report_json")
    with c2:
        st.download_button("Download signed manifest", manifest_json.encode("utf-8"), "interpret_signed_report_manifest.json", "application/json", width="stretch", key="download_interpret_signed_manifest_json")
        if not can(role, "sign_report"):
            st.caption(f"Role `{role}` cannot sign in the RBAC simulation; manifest is marked draft-only.")
    with c3:
        if st.button("Save review report locally", width="stretch"):
            path = append_review_report(report)
            record_audit_event(
                actor=actor,
                role=role,
                action="save_review_report",
                workflow="Interpret",
                document_hash=doc_version["document_hash"],
                output=report,
                metadata={"report_id": report.get("report_id"), "role_can_sign": can(role, "sign_report")},
            )
            st.success(f"Saved review report and SQLite audit event: {path}")
    with c4:
        input_hash = run_stable_hash({"current_text": current_text, "sources": [s.id for s in sources]})
        run_record = summarise_interpret_run(
            data,
            citation_rows,
            model=settings.get("model", "unknown"),
            demo_mode=bool(settings.get("demo_mode", True)),
            input_hash=input_hash,
            source_count=len(sources),
        )
        if st.button("Save run metrics locally", width="stretch"):
            path = append_run_history(run_record)
            record_audit_event(
                actor=actor,
                role=role,
                action="save_run_metrics",
                workflow="Interpret",
                document_hash=doc_version["document_hash"],
                output=run_record,
                metadata={"run_id": run_record.get("run_id")},
            )
            st.success(f"Saved run metrics and SQLite audit event: {path}")

    with st.expander("Document version hash and signed report manifest", expanded=False):
        st.json({"document_version": doc_version, "signed_report_manifest": manifest})

    runs = load_run_history(limit=20)
    st.markdown("**Compare metrics between runs**")
    if runs:
        compare_rows = compare_recent_runs(runs)
        st.dataframe(pd.DataFrame(compare_rows), width="stretch", hide_index=True)
    else:
        st.info("No saved run metrics yet. Save the current run to start a comparison history.")

    if data.get("decision_log"):
        st.markdown("**Decision log**")
        st.dataframe(pd.DataFrame(data.get("decision_log", [])), width="stretch", hide_index=True)

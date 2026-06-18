"""Approval Workflow UI."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from services.approval_workflow_service import APPROVAL_STATES, approval_gate, can_transition, hero_approval_workflow, transition_item
from services.usage_metrics_service import record_data_event


def render_approval_workflow_page(settings):
    st.subheader("✅ Approval Workflow")
    st.caption("A concrete local state machine for Product, QA, Compliance, Support and Engineering review. This is portfolio workflow logic, not production IAM.")

    items = hero_approval_workflow()
    gate = approval_gate(items)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Status", gate["status"])
    c2.metric("Artifacts", gate["total_artifacts"])
    c3.metric("Approved/exported", gate["approved_or_exported"])
    c4.metric("Blocked", gate["blocked"])
    st.dataframe(pd.DataFrame([{k: v for k, v in row.items() if k != "history"} for row in items]), width="stretch", hide_index=True)

    st.markdown("### Simulate a transition")
    artifact = st.selectbox("Artifact", [row["artifact_id"] for row in items])
    current = next(row for row in items if row["artifact_id"] == artifact)
    target = st.selectbox("Target state", APPROVAL_STATES, index=APPROVAL_STATES.index("Approved"))
    decision = can_transition(current["state"], target, settings.get("role", "Product Manager"))
    st.write(decision)
    if st.button("Apply transition locally"):
        updated = transition_item(current, target, actor=settings.get("demo_user", "demo-user"), role=settings.get("role", "Product Manager"), reason="Portfolio reviewer simulated approval transition.")
        record_data_event(
            event_type="approval_transition",
            actor=settings.get("demo_user", "demo-user"),
            role=settings.get("role", "Product Manager"),
            workflow="Approval Workflow",
            object_type="approval_item",
            obj=updated,
            metadata={"allowed": updated.get("last_transition", {}).get("allowed"), "target_state": target},
        )
        if updated.get("last_transition", {}).get("allowed"):
            st.success(f"Transition applied: {current['state']} → {updated['state']}")
        else:
            st.error(updated.get("last_transition", {}).get("reason"))

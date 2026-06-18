"""Sidebar rendering."""
from __future__ import annotations

from typing import Dict, Any

import streamlit as st

from config import AVAILABLE_MODELS, DEFAULT_EMBEDDING_MODEL, DEFAULT_MODEL, DETAIL_LEVELS, LANGUAGES, REVIEW_MODES, WORKFLOWS
from services.enterprise_controls_service import ROLES


def render_sidebar() -> Dict[str, Any]:
    with st.sidebar:
        st.header("🧭 Navigation")
        review_mode = st.radio("Review mode", list(REVIEW_MODES.keys()), index=0, help="Focused review keeps the app intentionally scoped for hiring review. Full artifact map exposes every deep-dive page.")
        available_workflows = REVIEW_MODES[review_mode]
        workflow_label = st.radio("Workflow", list(available_workflows.keys()), index=0)
        st.divider()
        st.header("🔐 Demo identity")
        user_name = st.text_input("Demo user", value="Marco Figueiredo")
        role = st.selectbox("Role simulation", ROLES, index=ROLES.index("Product Manager"))
        st.caption("Portfolio control: role simulation is local and not a substitute for SSO/RBAC in production.")
        st.divider()
        st.header("⚙️ Settings")
        demo_mode = st.toggle("Demo Mode", value=True, help="Use deterministic demo outputs and avoid API cost.")
        model = st.selectbox("Generation model", AVAILABLE_MODELS, index=AVAILABLE_MODELS.index(DEFAULT_MODEL))
        embedding_model = st.text_input("Embedding model", value=DEFAULT_EMBEDDING_MODEL)
        language = st.selectbox("Output language", LANGUAGES, index=0)
        detail = st.selectbox("Detail level", DETAIL_LEVELS, index=1)
        max_output_tokens = st.slider("Max output tokens", 1000, 7000, 3200, 250)
        top_k = st.slider("RAG top-k sources", 3, 12, 7, 1)
        st.divider()
        st.caption("Portfolio thesis: AI workflows for compliance-heavy enterprise software. Scope discipline: start with the guided path, then open the full artifact map only for deep review.")
    return {
        "workflow_label": workflow_label,
        "review_mode": review_mode,
        "workflow": available_workflows[workflow_label],
        "demo_user": user_name,
        "role": role,
        "demo_mode": demo_mode,
        "model": model,
        "embedding_model": embedding_model,
        "language": language,
        "detail": detail,
        "max_output_tokens": max_output_tokens,
        "top_k": top_k,
    }

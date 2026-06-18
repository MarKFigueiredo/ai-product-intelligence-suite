"""Evaluation panel."""
from __future__ import annotations

from typing import Any, Dict

import pandas as pd
import streamlit as st

from ui.visual_components import render_score_bar


def render_evaluation(evaluation: Dict[str, Any], citation_rows=None) -> None:
    citation_rows = citation_rows or []
    st.subheader("AI Safety & Evaluation Layer")
    st.caption("These checks are rule-based/product-quality checks. They are not model self-ratings and not legal/compliance validation.")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Completeness", f"{evaluation.get('completeness_score', 0)}%")
    col2.metric("Rule support", f"{evaluation.get('rule_verified_support_score', 0)}%")
    col3.metric("Citation precision proxy", f"{evaluation.get('citation_precision_proxy', 0)}%")
    col4.metric("Risk", evaluation.get("hallucination_risk", "N/A"))

    render_score_bar("Completeness score", evaluation.get("completeness_score", 0), "Output section coverage")
    render_score_bar("Rule-verified source support", evaluation.get("rule_verified_support_score", 0), "Average claim/citation lexical support")
    render_score_bar("Citation precision proxy", evaluation.get("citation_precision_proxy", 0), "Share of cited claims above support threshold")

    if evaluation.get("method_note"):
        st.info(evaluation["method_note"])
    if evaluation.get("recommendation"):
        st.info(evaluation["recommendation"])

    if evaluation.get("missing_inputs"):
        with st.expander("Missing inputs / missing sections", expanded=False):
            for item in evaluation.get("missing_inputs", []):
                st.write(f"- {item}")

    if evaluation.get("risky_claims"):
        st.warning("Risky claims detected: " + ", ".join(evaluation["risky_claims"]))

    if evaluation.get("ambiguity_warnings"):
        with st.expander("Ambiguity warnings", expanded=True):
            for warning in evaluation["ambiguity_warnings"]:
                st.write(f"- {warning}")

    if evaluation.get("source_coverage"):
        with st.expander("Used / not-used source coverage", expanded=False):
            st.json(evaluation["source_coverage"])

    if citation_rows:
        with st.expander("Rule-based citation support table", expanded=True):
            st.dataframe(pd.DataFrame(citation_rows), width="stretch", hide_index=True)

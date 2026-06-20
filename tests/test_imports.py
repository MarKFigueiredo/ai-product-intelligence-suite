"""Smoke tests for the AI PM Winning Suite."""


def test_core_imports():
    # Optional app dependencies are installed in CI; locally, this test skips if Streamlit is absent.
    import pytest
    pytest.importorskip("streamlit")
    import config  # noqa: F401
    from modules import (  # noqa: F401
        compliance_studio,
        decision_timeline,
        product_discovery,
        release_readiness,
    )
    from services import citation_verifier, cost_service, export_service, rag_service  # noqa: F401


def test_local_rag_ranking():
    from services.rag_service import chunk_text, rank_chunks

    chunks = chunk_text("Invoices require tax IDs. Releases require support notes.", "sample")
    ranked = rank_chunks("tax IDs invoice validation", chunks, top_k=1)
    assert ranked
    assert ranked[0].id == "S1"


def test_citation_verifier_supports_claim():
    from services.citation_verifier import support_score

    score = support_score("Invoices require customer tax IDs", "Invoices must include customer tax identification numbers before export.")
    assert score >= 40

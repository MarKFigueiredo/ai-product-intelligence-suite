from services.citation_verifier import (
    build_human_review_queue,
    build_obligation_support_matrix,
    fuzzy_quote_present,
    grounding_summary,
    rule_based_version_diff,
    verify_citations_advanced,
)
from services.rag_service import SourceChunk


def test_supported_claim_scores_above_threshold():
    sources = [SourceChunk(id="S1", chunk_index=1, text="Invoices must include customer tax identification number before SAF-T export.", score=0.9, method="test", doc_name="doc")]
    data = {"product_requirements": [{"requirement": "Validate customer tax identification number before SAF-T export", "source": "[S1]", "quote_support": "customer tax identification number before SAF-T export"}]}
    rows = verify_citations_advanced(data, sources)
    assert rows
    assert rows[0]["exists"] is True
    assert rows[0]["support_score"] >= 58


def test_missing_source_is_flagged():
    sources = []
    data = {"product_requirements": [{"requirement": "Validate invoice totals", "source": "[S1]"}]}
    rows = verify_citations_advanced(data, sources)
    assert rows[0]["exists"] is False
    assert rows[0]["support_score"] == 0
    assert grounding_summary(rows)["human_review_required"] is True


def test_quote_integrity_checks_exact_quote():
    source = "Records with missing tax identifiers or inconsistent totals should be corrected before export."
    assert fuzzy_quote_present("missing tax identifiers or inconsistent totals", source)[0] is True
    assert fuzzy_quote_present("must be approved by the CFO", source)[0] is False


def test_obligation_support_matrix_and_review_queue():
    sources = [SourceChunk(id="S1", chunk_index=1, text="Export reports must show which invoice records failed validation and why.", score=0.8, method="test", doc_name="doc")]
    data = {
        "obligation_extraction": [{"obligation_id": "O1", "obligation": "Export reports must show failed validation records and why", "source": "[S1]"}],
        "human_review_queue": [],
    }
    rows = verify_citations_advanced(data, sources)
    matrix = build_obligation_support_matrix(data, rows)
    assert matrix
    assert matrix[0]["support_score"] >= 50
    queue = build_human_review_queue(data, rows)
    assert isinstance(queue, list)


def test_rule_based_version_diff_detects_added_obligation():
    previous = "Invoices should include invoice date and tax code."
    current = "Invoices should include invoice date and tax code. Export reports must show records that failed validation."
    diff = rule_based_version_diff(previous, current)
    assert any(row["change_type"] in {"Added", "Changed"} for row in diff)

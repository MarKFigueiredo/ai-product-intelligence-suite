from services.citation_verifier import verify_citations_advanced
from services.interpret_metrics_service import (
    calculate_interpret_quality_metrics,
    citation_quality_counts,
    parse_gold_benchmark_text,
)
from services.rag_service import SourceChunk


def _sources():
    return [
        SourceChunk(
            id="S1",
            doc_name="sample.txt",
            chunk_index=1,
            text="Invoices included in a Portuguese SAF-T export must include the customer tax identification number, invoice date, tax code, invoice total and customer account reference where applicable. Records with missing tax identifiers or inconsistent totals should be corrected before export. Export reports must show which invoice records failed validation and why.",
            score=0.92,
            method="test",
        )
    ]


def _data():
    return {
        "obligation_extraction": [
            {
                "obligation_id": "O1",
                "obligation": "Validate customer tax identification number, invoice date, tax code and invoice total before SAF-T export",
                "source": "[S1]",
                "quote_support": "Invoices included in a Portuguese SAF-T export must include the customer tax identification number, invoice date, tax code, invoice total and customer account reference where applicable.",
            },
            {
                "obligation_id": "O2",
                "obligation": "Export reports must show failed invoice records and reasons",
                "source": "[S1]",
                "quote_support": "Export reports must show which invoice records failed validation and why.",
            },
        ]
    }


def test_citation_quality_counts():
    rows = verify_citations_advanced(_data(), _sources())
    counts = citation_quality_counts(rows)
    assert counts["checked_claims"] >= 2
    assert counts["supported_claims"] >= 1
    assert counts["human_review_claims"] >= 0


def test_interpret_quality_metrics_without_gold_marks_precision_recall_na():
    rows = verify_citations_advanced(_data(), _sources())
    payload = calculate_interpret_quality_metrics(_data(), rows)
    metrics = {m["metric"]: m for m in payload["metrics"]}
    assert metrics["Obligation precision"]["display_value"] == "N/A"
    assert metrics["Obligation recall"]["display_value"] == "N/A"
    assert metrics["Citation support rate"]["display_value"] != "N/A"
    assert payload["has_gold_benchmark"] is False
    assert "actual current run" in payload["method_note"]


def test_interpret_quality_metrics_with_gold_calculates_precision_recall():
    rows = verify_citations_advanced(_data(), _sources())
    gold = {
        "name": "test gold",
        "gold_obligations": [
            {"id": "G1", "obligation": "Customer tax identification number must be validated before SAF-T export", "required_terms": ["customer tax identification", "SAF-T"]},
            {"id": "G2", "obligation": "Export reports must show failed invoice records and reasons", "required_terms": ["export reports", "failed"]},
        ],
    }
    payload = calculate_interpret_quality_metrics(_data(), rows, benchmark=gold)
    metrics = {m["metric"]: m for m in payload["metrics"]}
    assert metrics["Obligation precision"]["display_value"] != "N/A"
    assert metrics["Obligation recall"]["display_value"] != "N/A"
    assert payload["has_gold_benchmark"] is True


def test_parse_gold_benchmark_text_json():
    gold = parse_gold_benchmark_text('{"gold_obligations":[{"obligation":"Validate invoice totals","required_terms":["invoice totals"]}]}')
    assert gold["gold_obligations"][0]["obligation"] == "Validate invoice totals"


def test_parse_gold_benchmark_text_csv():
    gold = parse_gold_benchmark_text("id,obligation,required_terms\nG1,Validate invoice totals,invoice totals;validation\n", filename="gold.csv")
    assert gold["gold_obligations"][0]["required_terms"] == ["invoice totals", "validation"]

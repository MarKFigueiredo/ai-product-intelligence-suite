from services.interpret_benchmark_service import compare_generated_to_gold, load_gold_obligations


def test_interpret_gold_benchmark_loads():
    benchmark = load_gold_obligations()
    assert len(benchmark["gold_obligations"]) >= 8


def test_interpret_benchmark_returns_metrics():
    data = {
        "obligation_extraction": [
            {"obligation_id": "O1", "obligation": "Customer tax identification number must be included in SAF-T export invoices", "source": "[S1]"},
            {"obligation_id": "O2", "obligation": "Export reports must show why invoice records failed validation", "source": "[S1]"},
        ]
    }
    results = compare_generated_to_gold(data)
    assert results["gold_count"] >= 8
    assert "precision_proxy" in results
    assert "recall_proxy" in results
    assert isinstance(results["match_matrix"], list)

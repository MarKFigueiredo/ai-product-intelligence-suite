import json
from pathlib import Path


def test_interpret_benchmark_has_minimum_questions():
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root / "benchmark" / "interpret_gold.json").read_text())
    assert len(data["questions"]) >= 8
    assert data["document_text"]

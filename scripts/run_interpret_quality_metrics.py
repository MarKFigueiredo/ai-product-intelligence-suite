#!/usr/bin/env python3
"""Run the consolidated Interpret Quality Metrics report.

This combines the synthetic obligation benchmark with rule-based citation support
checks. It reports the five portfolio-facing metrics used in the app:
obligation precision, obligation recall, citation support rate, unsupported
claim rate and human review rate.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from services.citation_verifier import verify_citations_advanced  # noqa: E402
from services.interpret_benchmark_service import load_gold_obligations  # noqa: E402
from services.interpret_metrics_service import calculate_interpret_quality_metrics, metrics_as_rows  # noqa: E402
from services.rag_service import SourceChunk  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", default=str(ROOT / "benchmark" / "generated_sample_interpret_output.json"))
    parser.add_argument("--gold", default=str(ROOT / "benchmark" / "interpret_gold_obligations.json"))
    parser.add_argument("--output", default=str(ROOT / "benchmark" / "results" / "interpret_quality_metrics.json"))
    args = parser.parse_args()

    with open(args.generated, "r", encoding="utf-8") as f:
        generated = json.load(f)
    benchmark = load_gold_obligations(args.gold)
    source = SourceChunk(
        id="S1",
        doc_name="synthetic_gold_document.txt",
        chunk_index=1,
        text=benchmark.get("document_text", ""),
        score=1.0,
        method="synthetic-gold-source",
    )
    citation_rows = verify_citations_advanced(generated, [source])
    payload = calculate_interpret_quality_metrics(generated, citation_rows, benchmark=benchmark)
    result = {
        "method_note": payload["method_note"],
        "metrics": metrics_as_rows(payload),
        "citation_counts": payload["citation_counts"],
        "thresholds": {
            "obligation_match_threshold": payload["threshold"],
            "citation_support_threshold": payload["support_threshold"],
            "unsupported_threshold": payload["unsupported_threshold"],
        },
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

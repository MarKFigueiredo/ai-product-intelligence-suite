"""Generate the SAF-T/e-invoicing synthetic evaluation report.

This script is intentionally deterministic and transparent. It does not claim
production accuracy; it packages a portfolio evaluation around one hero case.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "benchmark" / "synthetic_hero_metrics.json"
OUTPUT = ROOT / "benchmark" / "results" / "synthetic_hero_evaluation.json"


def _delta(metric: Dict[str, Any]) -> Dict[str, Any]:
    manual = float(metric["manual_baseline"])
    llm = float(metric["simple_llm_baseline"])
    assisted = float(metric["assisted_workflow"])
    direction = metric["direction"]
    if direction == "lower_is_better":
        improvement_vs_manual = round(((manual - assisted) / manual) * 100, 1) if manual else 0
        improvement_vs_llm = round(((llm - assisted) / llm) * 100, 1) if llm else 0
    elif direction == "higher_is_better":
        improvement_vs_manual = round(((assisted - manual) / manual) * 100, 1) if manual else 0
        improvement_vs_llm = round(((assisted - llm) / llm) * 100, 1) if llm else 0
    else:
        improvement_vs_manual = None
        improvement_vs_llm = None
    return {
        **metric,
        "improvement_vs_manual_percent": improvement_vs_manual,
        "improvement_vs_simple_llm_percent": improvement_vs_llm,
    }


def run() -> Dict[str, Any]:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows: List[Dict[str, Any]] = [_delta(row) for row in payload["metrics"]]
    result = {
        "name": payload["name"],
        "scope_note": payload["scope_note"],
        "rows": rows,
        "headline": {
            "time_to_first_requirement_set": "45 min manual → 8 min assisted",
            "unsupported_claim_rate": "22% simple LLM → 6% assisted after reviewer pass",
            "qa_coverage": "60% manual → 90% assisted obligation-to-QA coverage",
            "negative_test_coverage": "0% happy-path manual baseline → 100% assisted mapped negative coverage",
            "release_risk_reduction": "4 high-risk release claims rewritten",
        },
        "honesty_note": "Synthetic one-case evaluation. Use to demonstrate measurement thinking, not to claim production accuracy.",
    }
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))

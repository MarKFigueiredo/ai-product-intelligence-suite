#!/usr/bin/env python3
"""Run the Interpret synthetic obligation benchmark.

Usage:
  python scripts/run_interpret_obligation_benchmark.py
  python scripts/run_interpret_obligation_benchmark.py --generated path/to/generated.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from services.interpret_benchmark_service import compare_generated_to_gold, load_gold_obligations  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", default=str(ROOT / "benchmark" / "generated_sample_interpret_output.json"))
    parser.add_argument("--gold", default=str(ROOT / "benchmark" / "interpret_gold_obligations.json"))
    parser.add_argument("--output", default=str(ROOT / "benchmark" / "results" / "interpret_obligation_benchmark.json"))
    args = parser.parse_args()

    with open(args.generated, "r", encoding="utf-8") as f:
        generated = json.load(f)
    gold = load_gold_obligations(args.gold)
    result = compare_generated_to_gold(generated, gold)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

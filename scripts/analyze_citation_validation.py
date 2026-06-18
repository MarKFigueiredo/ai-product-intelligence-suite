"""Analyze citation-verifier agreement against human labels.

Input: a CSV such as validation/citation_claims_sample.csv after reviewers fill
human_reviewer_1..3 or majority_human_label with Supported / Weak / Unsupported.

This script is intentionally transparent and lightweight. It reports simple
agreement rather than claiming a statistically robust academic study.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
import sys
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]

LABELS = {"supported": "Supported", "weak": "Weak", "unsupported": "Unsupported"}


def normalize_label(value: str) -> str:
    value = (value or "").strip().lower()
    if value in LABELS:
        return LABELS[value]
    if value.startswith("support"):
        return "Supported"
    if value.startswith("weak") or value.startswith("partial"):
        return "Weak"
    if value.startswith("unsupported") or value.startswith("not supported"):
        return "Unsupported"
    return ""


def heuristic_label(score: int) -> str:
    if score >= 82:
        return "Supported"
    if score >= 64:
        return "Weak"
    return "Unsupported"


def majority(labels: List[str]) -> str:
    valid = [normalize_label(label) for label in labels if normalize_label(label)]
    if not valid:
        return ""
    counts = Counter(valid)
    top = counts.most_common()
    if len(top) > 1 and top[0][1] == top[1][1]:
        return "Tie"
    return top[0][0]


def main() -> None:
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "validation" / "citation_claims_sample.csv"
    rows: List[Dict[str, str]] = []
    with input_path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    evaluated = []
    pending = []
    for row in rows:
        human = normalize_label(row.get("majority_human_label", "")) or majority([
            row.get("human_reviewer_1", ""),
            row.get("human_reviewer_2", ""),
            row.get("human_reviewer_3", ""),
        ])
        if not human or human == "Tie":
            pending.append(row["claim_id"])
            continue
        score = int(float(row.get("heuristic_support_score") or 0))
        pred = heuristic_label(score)
        evaluated.append({**row, "human_label": human, "heuristic_label": pred, "agreement": human == pred})

    total = len(evaluated)
    agreements = sum(1 for row in evaluated if row["agreement"])
    by_label: Dict[str, Dict[str, int]] = {}
    for row in evaluated:
        human = row["human_label"]
        by_label.setdefault(human, {"total": 0, "agreements": 0})
        by_label[human]["total"] += 1
        by_label[human]["agreements"] += int(row["agreement"])

    result = {
        "input_file": str(input_path),
        "claims_total": len(rows),
        "claims_with_human_labels": total,
        "claims_pending_human_labels": len(pending),
        "pending_claim_ids": pending[:50],
        "simple_agreement_rate": round(agreements / total, 3) if total else None,
        "by_human_label": by_label,
        "false_positives": [r["claim_id"] for r in evaluated if r["heuristic_label"] == "Supported" and r["human_label"] != "Supported"],
        "false_negatives": [r["claim_id"] for r in evaluated if r["heuristic_label"] == "Unsupported" and r["human_label"] == "Supported"],
        "limitations": [
            "This reports simple agreement only, not a statistically robust validation study.",
            "Human labels must be collected externally; blank templates are not evidence.",
            "The score thresholds are heuristic and should be revisited after reviewer feedback.",
        ],
    }
    out = ROOT / "validation" / "citation_validation_results.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

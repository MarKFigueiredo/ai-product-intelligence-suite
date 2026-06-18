"""Small benchmark helpers for the Interpret module.

This benchmark is intentionally simple and transparent. It compares generated
obligation text against a hand-written synthetic gold set. It does not prove
production compliance quality; it provides a repeatable baseline for portfolio
review and future improvements.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from services.citation_verifier import claim_similarity, support_score

DEFAULT_BENCHMARK_PATH = Path(__file__).resolve().parents[1] / "benchmark" / "interpret_gold_obligations.json"


def load_gold_obligations(path: str | Path = DEFAULT_BENCHMARK_PATH) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def generated_obligations_from_output(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for item in data.get("obligation_extraction", []) or []:
        if isinstance(item, dict):
            rows.append({
                "id": item.get("obligation_id", "generated"),
                "text": str(item.get("obligation", "")),
                "source": item.get("source", ""),
            })
    for item in data.get("traceability_matrix", []) or []:
        if isinstance(item, dict) and item.get("obligation"):
            rows.append({
                "id": item.get("obligation_id", "traceability"),
                "text": str(item.get("obligation", "")),
                "source": item.get("source", ""),
            })
    # de-duplicate
    seen = set()
    unique = []
    for row in rows:
        key = row["text"].lower().strip()
        if key and key not in seen:
            seen.add(key)
            unique.append(row)
    return unique


def compare_generated_to_gold(data: Dict[str, Any], benchmark: Dict[str, Any] | None = None, threshold: int = 58) -> Dict[str, Any]:
    """Compare generated obligations against a hand-written gold set.

    A generated obligation may legitimately cover multiple granular gold obligations
    (for example, one sentence may include tax ID, invoice date and tax code). For
    that reason, the primary recall calculation is gold-centric: each gold item is
    matched against the best generated obligation.
    """
    benchmark = benchmark or load_gold_obligations()
    gold = benchmark.get("gold_obligations", []) or []
    generated = generated_obligations_from_output(data)

    gold_matrix: List[Dict[str, Any]] = []
    matched_gold = set()
    generated_with_match = set()

    for gold_idx, gold_item in enumerate(gold):
        best_generated = None
        best_score = -1
        for gen_idx, g in enumerate(generated):
            score = claim_similarity(g.get("text", ""), gold_item.get("obligation", ""))
            required_terms = " ".join(gold_item.get("required_terms", []) or [])
            term_score = support_score(required_terms, g.get("text", "")) if required_terms else 0
            combined = round(0.68 * score + 0.32 * term_score)
            if combined > best_score:
                best_score = combined
                best_generated = (gen_idx, g, score, term_score)
        matched = bool(best_generated and best_score >= threshold)
        if matched:
            matched_gold.add(gold_idx)
            generated_with_match.add(best_generated[0])
        gold_matrix.append({
            "gold_id": gold_item.get("id"),
            "gold_obligation": gold_item.get("obligation"),
            "best_generated_id": best_generated[1].get("id") if best_generated else "",
            "best_generated_obligation": best_generated[1].get("text") if best_generated else "",
            "match_score": best_score,
            "status": "Matched" if matched else "Missing / weak match",
        })

    generated_matrix: List[Dict[str, Any]] = []
    for gen_idx, g in enumerate(generated):
        best_gold = None
        best_score = -1
        for gold_idx, gold_item in enumerate(gold):
            score = claim_similarity(g.get("text", ""), gold_item.get("obligation", ""))
            required_terms = " ".join(gold_item.get("required_terms", []) or [])
            term_score = support_score(required_terms, g.get("text", "")) if required_terms else 0
            combined = round(0.68 * score + 0.32 * term_score)
            if combined > best_score:
                best_score = combined
                best_gold = (gold_idx, gold_item)
        generated_matrix.append({
            "generated_id": g.get("id"),
            "generated_obligation": g.get("text"),
            "best_gold_id": best_gold[1].get("id") if best_gold else "",
            "best_gold_obligation": best_gold[1].get("obligation") if best_gold else "",
            "match_score": best_score,
            "status": "Matched" if gen_idx in generated_with_match else "No strong gold match",
        })

    precision = round(100 * len(generated_with_match) / max(1, len(generated)))
    recall = round(100 * len(matched_gold) / max(1, len(gold)))
    f1 = round(2 * precision * recall / max(1, precision + recall)) if precision + recall else 0

    missing_gold = [
        {"gold_id": item.get("id"), "gold_obligation": item.get("obligation")}
        for idx, item in enumerate(gold)
        if idx not in matched_gold
    ]

    return {
        "benchmark_name": benchmark.get("name", "Interpret synthetic gold obligations"),
        "threshold": threshold,
        "generated_count": len(generated),
        "gold_count": len(gold),
        "precision_proxy": precision,
        "recall_proxy": recall,
        "f1_proxy": f1,
        "matched_gold_count": len(matched_gold),
        "method_note": "Rule-based proxy benchmark against a hand-written synthetic gold set. A generated obligation may match multiple granular gold obligations. Not a production compliance evaluation.",
        "match_matrix": gold_matrix,
        "generated_matrix": generated_matrix,
        "missing_gold_obligations": missing_gold,
    }

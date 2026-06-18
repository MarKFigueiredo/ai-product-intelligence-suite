"""Run a small transparent retrieval benchmark for the Interpret module.

This benchmark is intentionally simple and local. It does not claim production
validity. It checks whether the retrieval layer surfaces chunks containing
hand-written gold terms for a synthetic compliance document.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from services.rag_service import chunk_text, local_hash_embedding, rank_chunks  # noqa: E402


def contains_any(text: str, terms: list[str]) -> bool:
    low = text.lower()
    return any(term.lower() in low for term in terms)


def main() -> None:
    data_path = ROOT / "benchmark" / "interpret_gold.json"
    data = json.loads(data_path.read_text(encoding="utf-8"))
    chunks = chunk_text(data["document_text"], data["document_name"], chunk_size=360, overlap=60)
    chunk_embeddings = [local_hash_embedding(c.text) for c in chunks]

    rows = []
    hits = 0
    top_scores = []
    for question in data["questions"]:
        query = question["query"]
        query_embedding = local_hash_embedding(query)
        ranked = rank_chunks(query, chunks, chunk_embeddings, query_embedding, top_k=3)
        combined = "\n".join(c.text for c in ranked)
        hit = contains_any(combined, question["expected_terms"])
        hits += int(hit)
        top_scores.append(float(ranked[0].score if ranked else 0.0))
        rows.append({
            "id": question["id"],
            "query": query,
            "expected_terms": question["expected_terms"],
            "retrieved_sources": [c.id for c in ranked],
            "top_score": round(float(ranked[0].score if ranked else 0.0), 4),
            "hit": hit,
        })

    result = {
        "evaluation_type": "local retrieval benchmark; no LLM generation",
        "questions": len(data["questions"]),
        "retrieval_hit_rate": hits / max(1, len(data["questions"])),
        "average_top_score": sum(top_scores) / max(1, len(top_scores)),
        "limitations": [
            "Synthetic document and hand-written expected terms.",
            "Measures retrieval coverage only, not full obligation extraction accuracy.",
            "Uses deterministic local embeddings for reproducibility and zero API cost.",
        ],
        "rows": rows,
    }
    out = ROOT / "benchmark" / "results" / "interpret_retrieval_benchmark.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

"""Run a compact second-domain benchmark for the Swiss QR-Bill sample.

This benchmark is intentionally local and synthetic. It checks whether the
citation-support heuristic can find textual support for hand-written gold
obligations in a second domain. It does not validate legal correctness or bank
acceptance.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from services.citation_verifier import support_components  # noqa: E402


def source_sections(text: str) -> Dict[str, str]:
    sections: Dict[str, str] = {}
    current = None
    buffer: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^(S\d+)\.\s*(.*)", line.strip())
        if m:
            if current:
                sections[current] = " ".join(buffer).strip()
            current = m.group(1)
            buffer = [m.group(2)]
        elif current and line.strip():
            buffer.append(line.strip())
    if current:
        sections[current] = " ".join(buffer).strip()
    return sections


def main() -> None:
    sample_path = ROOT / "sample_inputs" / "swiss_qr_bill_sample.txt"
    gold_path = ROOT / "sample_inputs" / "swiss_qr_bill_gold_obligations.json"
    text = sample_path.read_text(encoding="utf-8")
    gold = json.loads(gold_path.read_text(encoding="utf-8"))
    sections = source_sections(text)

    rows = []
    strong = partial = unsupported = 0
    for item in gold["obligations"]:
        source_text = sections.get(item["source"], "")
        comps = support_components(item["obligation"], source_text)
        score = int(comps["support_score"])
        if score >= 82:
            status = "Strong support"
            strong += 1
        elif score >= 64:
            status = "Partial support"
            partial += 1
        else:
            status = "Needs review"
            unsupported += 1
        rows.append({
            "id": item["id"],
            "source": item["source"],
            "obligation": item["obligation"],
            "support_score": score,
            "status": status,
            "components": comps,
        })

    total = len(rows)
    result = {
        "evaluation_type": "second-domain local support benchmark; no LLM generation",
        "domain": gold["domain"],
        "source_file": str(sample_path.relative_to(ROOT)),
        "gold_obligations": total,
        "strong_support_count": strong,
        "partial_support_count": partial,
        "needs_review_count": unsupported,
        "support_rate_at_64": round((strong + partial) / max(1, total), 3),
        "strong_support_rate_at_82": round(strong / max(1, total), 3),
        "limitations": [
            "Synthetic second-domain document and hand-written obligations.",
            "Measures textual support in cited sections, not legal correctness.",
            "Does not prove the citation verifier generalizes to all QR-Bill documents.",
            "Human review is still required for production compliance interpretation.",
        ],
        "rows": rows,
    }
    out = ROOT / "benchmark" / "results" / "second_domain_swiss_qr_bill_benchmark.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

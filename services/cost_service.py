"""Conservative cost estimation utilities for portfolio demos.

The suite avoids hard-coding unverified current model pricing. If you want cost
estimates, configure illustrative prices through environment variables or keep
Demo Mode enabled. The output is intentionally labelled as planning-only.
"""
from __future__ import annotations

import os
from typing import Dict


def estimate_tokens(text: str) -> int:
    """Very rough English/token approximation for UI planning."""
    return max(1, round(len(text or "") / 4))


def _pricing_from_env() -> Dict[str, float] | None:
    try:
        input_price = float(os.getenv("OPENAI_INPUT_COST_PER_1M", ""))
        output_price = float(os.getenv("OPENAI_OUTPUT_COST_PER_1M", ""))
    except ValueError:
        return None
    return {"input": input_price, "output": output_price}


def estimate_run_cost(model: str, input_text: str, max_output_tokens: int) -> Dict[str, float | int | str | None]:
    pricing = _pricing_from_env()
    input_tokens = estimate_tokens(input_text)
    output_tokens = int(max_output_tokens or 0)
    if not pricing:
        return {
            "model": model,
            "estimated_input_tokens": input_tokens,
            "max_output_tokens": output_tokens,
            "estimated_cost_usd": None,
            "note": "Cost pricing is not configured. Set OPENAI_INPUT_COST_PER_1M and OPENAI_OUTPUT_COST_PER_1M for a planning-only estimate.",
        }
    input_cost = input_tokens * pricing["input"] / 1_000_000
    output_cost = output_tokens * pricing["output"] / 1_000_000
    return {
        "model": model,
        "estimated_input_tokens": input_tokens,
        "max_output_tokens": output_tokens,
        "estimated_cost_usd": round(input_cost + output_cost, 4),
        "note": "Planning-only estimate based on locally configured prices. Actual API billing may differ.",
    }

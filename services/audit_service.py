"""Local audit trail utilities for portfolio demos.

The audit trail is intentionally local and disabled for public demos unless the
caller explicitly writes it. It demonstrates the kind of metadata a production
system would persist to an enterprise audit store.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / ".local_audit"
AUDIT_FILE = AUDIT_DIR / "run_log.jsonl"


def stable_hash(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:16]


def build_audit_event(
    workflow: str,
    model: str,
    demo_mode: bool,
    input_text: str,
    output_summary: Dict[str, Any] | None = None,
    source_count: int = 0,
) -> Dict[str, Any]:
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "workflow": workflow,
        "model": model,
        "demo_mode": demo_mode,
        "input_hash": stable_hash(input_text),
        "source_count": source_count,
        "output_summary": output_summary or {},
        "note": "Local demo audit event. Do not store sensitive document text in public repos.",
    }


def append_audit_event(event: Dict[str, Any]) -> Path:
    AUDIT_DIR.mkdir(exist_ok=True)
    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    return AUDIT_FILE

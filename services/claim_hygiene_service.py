"""Claim-hygiene checks for portfolio review.

This service is intentionally conservative. It does not try to prove the whole
repository is perfect; it highlights phrases that a skeptical reviewer could
challenge unless they are clearly framed as synthetic, local, optional or not
production-ready.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Iterable, List

SCAN_GLOBS = ["*.md", "docs/*.md", "*.py", "services/*.py", "ui/*.py", "modules/*.py", "benchmark/**/*.json"]
EXCLUDED_PATH_PARTS = {".pytest_cache", "claim_hygiene_service.py"}

RISK_PATTERNS = [
    {
        "rule_id": "CH01",
        "label": "Unverified model name",
        "pattern": re.compile(r"\bgpt-5\.4\b|\bgpt-5\.4-mini\b|\bgpt-5\.4-nano\b|\bgpt-5\.5\b", re.I),
        "severity": "High",
        "risk": "A reviewer could challenge model names or pricing if they look invented or current without verification.",
        "safer_guidance": "Use configurable model names and avoid hard-coded pricing unless sourced and maintained.",
    },
    {
        "rule_id": "CH02",
        "label": "Absolute compliance guarantee",
        "pattern": re.compile(r"guarantee(?:s|d)?\s+(?:full\s+)?(?:legal\s+)?compliance|guaranteed\s+(?:legal\s+)?compliance", re.I),
        "severity": "High",
        "risk": "Absolute compliance wording is risky unless explicitly shown as a bad example or negated.",
        "safer_guidance": "Say the workflow supports review, traceability and validation; do not claim legal compliance guarantees.",
    },
    {
        "rule_id": "CH03",
        "label": "Production readiness ambiguity",
        "pattern": re.compile(r"production[-\s]?ready|production SaaS|enterprise[-\s]?ready", re.I),
        "severity": "Medium",
        "risk": "Production-readiness language can be misread if local prototype limitations are not visible nearby.",
        "safer_guidance": "Prefer 'portfolio prototype with local controls' and list production gaps explicitly.",
    },
    {
        "rule_id": "CH04",
        "label": "Interview/hiring outcome overclaim",
        "pattern": re.compile(r"will\s+(?:increase|guarantee|get).*interviews|guarantee.*interview|guarantee.*job", re.I),
        "severity": "Medium",
        "risk": "Career outcomes depend on targeting, CV, network, market and outreach; the project can improve signal but cannot guarantee interviews.",
        "safer_guidance": "Say it can improve interview conversion when packaged and targeted well, not that it guarantees interviews.",
    },
    {
        "rule_id": "CH05",
        "label": "Synthetic metric missing context",
        "pattern": re.compile(r"\b(?:90|95|100)%\b|\b\d+(?:\.\d+)?/10\b", re.I),
        "severity": "Medium",
        "risk": "Precise metrics can look like production evidence if synthetic/local scope is not visible.",
        "safer_guidance": "Label metrics as synthetic benchmark, local usage, or reviewer-assessed portfolio signal.",
    },
]

SAFE_CONTEXT_HINTS = [
    "not production",
    "not a production",
    "not claimed",
    "not independently validated",
    "not to prove",
    "not to claim",
    "synthetic",
    "portfolio",
    "demo",
    "does not guarantee",
    "cannot guarantee",
    "must not",
    "must not state",
    "do not claim",
    "avoid claiming",
    "implying",
    "imply",
    "broader than",
    "what would make",
    "disputes",
    "what_not_to_say",
    "bad example",
    "risky",
    "safer rewrite",
    "not legal guidance",
    "not legal advice",
    "review remains",
    "optional",
    "local",
]


def classify_context(line: str) -> str:
    lower = line.lower()
    return "Framed/acceptable" if any(hint in lower for hint in SAFE_CONTEXT_HINTS) else "Needs review"


def scan_text(text: str, source: str = "inline") -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for rule in RISK_PATTERNS:
            if rule["pattern"].search(line):
                context = classify_context(line)
                if any(part in source.lower() for part in ["benchmark/", "error_taxonomy", "synthetic_evaluation", "validation_limitations"]):
                    context = "Framed/acceptable"
                severity = rule["severity"] if context == "Needs review" else "Info"
                findings.append(
                    {
                        "source": source,
                        "line": line_no,
                        "rule_id": rule["rule_id"],
                        "label": rule["label"],
                        "severity": severity,
                        "context": context,
                        "excerpt": line.strip()[:260],
                        "risk": rule["risk"],
                        "safer_guidance": rule["safer_guidance"],
                    }
                )
    return findings


def iter_files(root: Path, globs: Iterable[str] = SCAN_GLOBS) -> Iterable[Path]:
    seen: set[Path] = set()
    for pattern in globs:
        for path in root.glob(pattern):
            if path.is_file() and path not in seen and not (set(path.parts) & EXCLUDED_PATH_PARTS):
                seen.add(path)
                yield path


def audit_portfolio_claims(root: str | Path = ".") -> Dict[str, Any]:
    root_path = Path(root)
    findings: List[Dict[str, Any]] = []
    scanned = 0
    for path in iter_files(root_path):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        scanned += 1
        findings.extend(scan_text(text, str(path.relative_to(root_path))))

    needs_review = [row for row in findings if row["context"] == "Needs review"]
    high = [row for row in needs_review if row["severity"] == "High"]
    medium = [row for row in needs_review if row["severity"] == "Medium"]
    return {
        "files_scanned": scanned,
        "findings_total": len(findings),
        "needs_review_total": len(needs_review),
        "high_risk_total": len(high),
        "medium_risk_total": len(medium),
        "findings": findings,
        "summary": "Pass" if not needs_review else "Review recommended",
        "note": "This is a conservative portfolio claim-hygiene scan, not a legal or brand review.",
    }


def safe_positioning_statement() -> str:
    return (
        "This portfolio can improve interview conversion by making skills easier to assess, "
        "but it does not guarantee interviews. The hiring impact depends on targeting, CV, outreach, "
        "market conditions and how clearly the demo is packaged."
    )

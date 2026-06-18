"""Simulated enterprise source parsers for product incident timelines.

These are deliberately lightweight portfolio parsers. They demonstrate product vision
for Slack, Jira and Git ingestion without requiring external credentials.
"""
from __future__ import annotations

import re
from typing import Dict, List


def parse_slack_export(text: str) -> List[Dict[str, str]]:
    rows = []
    for line in (text or "").splitlines():
        m = re.match(r"\[?([0-9]{4}-[0-9]{2}-[0-9]{2}[^\]]*)\]?\s*([^:]+):\s*(.*)", line.strip())
        if m:
            rows.append({"source": "Slack", "timestamp": m.group(1), "actor": m.group(2).strip(), "event": m.group(3).strip()})
    return rows


def parse_jira_export(text: str) -> List[Dict[str, str]]:
    rows = []
    for line in (text or "").splitlines():
        if not line.strip():
            continue
        parts = [p.strip() for p in re.split(r"[,|;]", line)]
        if len(parts) >= 3 and re.search(r"[A-Z]+-\d+", parts[0]):
            rows.append({"source": "Jira", "ticket": parts[0], "status": parts[1], "event": " | ".join(parts[2:])})
    return rows


def parse_git_log(text: str) -> List[Dict[str, str]]:
    rows = []
    for line in (text or "").splitlines():
        m = re.match(r"([a-f0-9]{7,40})\s+(.+)", line.strip(), flags=re.IGNORECASE)
        if m:
            rows.append({"source": "Git", "commit": m.group(1)[:10], "event": m.group(2)})
    return rows


def parse_enterprise_sources(text: str) -> Dict[str, List[Dict[str, str]]]:
    return {
        "slack_events": parse_slack_export(text),
        "jira_events": parse_jira_export(text),
        "git_events": parse_git_log(text),
    }

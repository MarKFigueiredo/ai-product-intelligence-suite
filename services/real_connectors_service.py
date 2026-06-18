"""Real connector helpers with safe local fallback.

The portfolio app should not pretend that mock payloads are full integrations.
This module provides:
- configuration detection for Jira, GitHub and Slack;
- real HTTP calls when credentials are explicitly provided and live mode is enabled;
- local outbox persistence for inspectable connector payloads when live mode is off.

No credentials are required for normal portfolio review.
"""
from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from services.enterprise_controls_service import stable_hash
from services.usage_metrics_service import record_data_event

ROOT = Path(__file__).resolve().parents[1]
OUTBOX_DIR = ROOT / ".local_connector_outbox"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_bytes(payload: Dict[str, Any]) -> bytes:
    return json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")


def _request_json(url: str, *, method: str, payload: Dict[str, Any], headers: Dict[str, str], timeout: int = 20) -> Dict[str, Any]:
    request = urllib.request.Request(url, data=_json_bytes(payload), method=method, headers={"Content-Type": "application/json", **headers})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - explicitly user-configured external connector
            body = response.read().decode("utf-8")
            parsed = json.loads(body) if body else {}
            return {"ok": True, "status": response.status, "response": parsed}
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        return {"ok": False, "status": error.code, "error": body[:2000]}
    except Exception as error:  # pragma: no cover - network environment dependent
        return {"ok": False, "status": 0, "error": str(error)}


@dataclass(frozen=True)
class ConnectorStatus:
    name: str
    configured: bool
    mode: str
    missing: List[str]

    def as_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "configured": self.configured, "mode": self.mode, "missing": ", ".join(self.missing)}


def connector_statuses() -> List[Dict[str, Any]]:
    return [jira_status().as_dict(), github_status().as_dict(), slack_status().as_dict()]


def jira_status() -> ConnectorStatus:
    required = ["JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN", "JIRA_PROJECT_KEY"]
    missing = [name for name in required if not os.getenv(name)]
    return ConnectorStatus("Jira", not missing, "live when enabled; local outbox otherwise", missing)


def github_status() -> ConnectorStatus:
    required = ["GITHUB_TOKEN", "GITHUB_REPOSITORY"]
    missing = [name for name in required if not os.getenv(name)]
    return ConnectorStatus("GitHub", not missing, "live when enabled; local outbox otherwise", missing)


def slack_status() -> ConnectorStatus:
    required = ["SLACK_WEBHOOK_URL"]
    missing = [name for name in required if not os.getenv(name)]
    return ConnectorStatus("Slack webhook", not missing, "live when enabled; local outbox otherwise", missing)


def save_connector_payload_locally(*, connector: str, payload: Dict[str, Any], actor: str = "demo-user", role: str = "Product Manager") -> Dict[str, Any]:
    OUTBOX_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    digest = stable_hash(payload, length=12)
    path = OUTBOX_DIR / f"{connector.lower()}_{stamp}_{digest}.json"
    envelope = {
        "connector": connector,
        "created_at_utc": utc_now(),
        "mode": "local_outbox",
        "payload_hash": stable_hash(payload, length=64),
        "payload": payload,
        "note": "This is a real local connector outbox file. Configure credentials and enable live mode to send externally.",
    }
    path.write_text(json.dumps(envelope, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    event = record_data_event(
        event_type="connector_outbox",
        actor=actor,
        role=role,
        workflow="Enterprise Connector",
        object_type=f"{connector}_payload",
        obj=envelope,
        path=str(path),
        metadata={"connector": connector, "mode": "local_outbox"},
    )
    return {"ok": True, "mode": "local_outbox", "path": str(path), "event_id": event.get("event_id"), "payload_hash": envelope["payload_hash"]}


def create_jira_issue(payload: Dict[str, Any], *, live: bool = False, actor: str = "demo-user", role: str = "Product Manager") -> Dict[str, Any]:
    if not live:
        return save_connector_payload_locally(connector="jira", payload=payload, actor=actor, role=role)
    status = jira_status()
    if not status.configured:
        return {"ok": False, "mode": "live", "error": f"Jira connector is not configured. Missing: {', '.join(status.missing)}"}
    base = os.environ["JIRA_BASE_URL"].rstrip("/")
    url = f"{base}/rest/api/3/issue"
    raw_auth = f"{os.environ['JIRA_EMAIL']}:{os.environ['JIRA_API_TOKEN']}".encode("utf-8")
    headers = {"Authorization": "Basic " + base64.b64encode(raw_auth).decode("ascii")}
    body = {"fields": payload.get("fields", payload)}
    response = _request_json(url, method="POST", payload=body, headers=headers)
    record_data_event(event_type="connector_live_call", actor=actor, role=role, workflow="Enterprise Connector", object_type="jira_issue", obj={"request_hash": stable_hash(body, length=64), "response": response}, metadata={"connector": "jira", "ok": response.get("ok")})
    return {"mode": "live", **response}


def create_github_issue(payload: Dict[str, Any], *, live: bool = False, actor: str = "demo-user", role: str = "Product Manager") -> Dict[str, Any]:
    if not live:
        return save_connector_payload_locally(connector="github", payload=payload, actor=actor, role=role)
    status = github_status()
    if not status.configured:
        return {"ok": False, "mode": "live", "error": f"GitHub connector is not configured. Missing: {', '.join(status.missing)}"}
    repo = os.environ["GITHUB_REPOSITORY"].strip("/")
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}", "Accept": "application/vnd.github+json", "User-Agent": "ai-pm-winning-suite-portfolio"}
    body = {"title": payload.get("title", "AI PM portfolio issue"), "body": payload.get("body", ""), "labels": payload.get("labels", [])}
    response = _request_json(url, method="POST", payload=body, headers=headers)
    record_data_event(event_type="connector_live_call", actor=actor, role=role, workflow="Enterprise Connector", object_type="github_issue", obj={"request_hash": stable_hash(body, length=64), "response": response}, metadata={"connector": "github", "ok": response.get("ok")})
    return {"mode": "live", **response}


def post_slack_message(payload: Dict[str, Any], *, live: bool = False, actor: str = "demo-user", role: str = "Product Manager") -> Dict[str, Any]:
    if not live:
        return save_connector_payload_locally(connector="slack", payload=payload, actor=actor, role=role)
    status = slack_status()
    if not status.configured:
        return {"ok": False, "mode": "live", "error": f"Slack connector is not configured. Missing: {', '.join(status.missing)}"}
    response = _request_json(os.environ["SLACK_WEBHOOK_URL"], method="POST", payload=payload, headers={})
    record_data_event(event_type="connector_live_call", actor=actor, role=role, workflow="Enterprise Connector", object_type="slack_message", obj={"request_hash": stable_hash(payload, length=64), "response": response}, metadata={"connector": "slack", "ok": response.get("ok")})
    return {"mode": "live", **response}


def list_local_outbox(limit: int = 50) -> List[Dict[str, Any]]:
    if not OUTBOX_DIR.exists():
        return []
    rows = []
    for path in sorted(OUTBOX_DIR.glob("*.json"), reverse=True)[:limit]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
        rows.append({"filename": path.name, "path": str(path), "connector": payload.get("connector", "unknown"), "created_at_utc": payload.get("created_at_utc", ""), "payload_hash": payload.get("payload_hash", "")})
    return rows

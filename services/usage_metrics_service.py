"""Persistent usage metrics for the portfolio app.

This module stores metrics created by real app usage. Synthetic benchmark numbers
remain in the benchmark folder; the database here is populated when a user runs a
workflow, saves an export, imports data, or sends/saves connector payloads.

The store is intentionally local SQLite so reviewers can inspect it without a
cloud account. It persists only hashes, metadata and derived metrics by default,
not confidential source documents.
"""
from __future__ import annotations

import csv
import io
import json
import sqlite3
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from services.enterprise_controls_service import canonical_json, sign_payload, stable_hash
from services.qa_coverage_service import negative_coverage_metrics

ROOT = Path(__file__).resolve().parents[1]
LOCAL_DIR = ROOT / ".local_runs"
USAGE_DB_FILE = LOCAL_DIR / "usage_metrics.db"
EXPORT_DIR = ROOT / ".local_exports"
SCHEMA_VERSION = "v19.usage.1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def now_ms() -> int:
    return int(time.perf_counter() * 1000)


def elapsed_ms(start_ms: int) -> int:
    return max(0, int(time.perf_counter() * 1000) - int(start_ms or 0))


def connect(db_path: Path = USAGE_DB_FILE) -> sqlite3.Connection:
    LOCAL_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_usage_db(db_path: Path = USAGE_DB_FILE) -> Path:
    conn = connect(db_path)
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS workflow_runs (
                run_id TEXT PRIMARY KEY,
                timestamp_utc TEXT NOT NULL,
                workflow TEXT NOT NULL,
                actor TEXT NOT NULL,
                role TEXT NOT NULL,
                model TEXT NOT NULL,
                demo_mode INTEGER NOT NULL,
                input_hash TEXT,
                output_hash TEXT,
                input_bytes INTEGER DEFAULT 0,
                output_bytes INTEGER DEFAULT 0,
                source_count INTEGER DEFAULT 0,
                latency_ms INTEGER DEFAULT 0,
                metrics_json TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                signature TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS metric_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                timestamp_utc TEXT NOT NULL,
                workflow TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                numerator REAL,
                denominator REAL,
                unit TEXT,
                metric_source TEXT NOT NULL,
                FOREIGN KEY(run_id) REFERENCES workflow_runs(run_id)
            );

            CREATE TABLE IF NOT EXISTS data_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp_utc TEXT NOT NULL,
                event_type TEXT NOT NULL,
                actor TEXT NOT NULL,
                role TEXT NOT NULL,
                workflow TEXT NOT NULL,
                object_type TEXT NOT NULL,
                object_hash TEXT NOT NULL,
                path TEXT,
                metadata_json TEXT NOT NULL,
                signature TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_usage_runs_timestamp ON workflow_runs(timestamp_utc);
            CREATE INDEX IF NOT EXISTS idx_usage_runs_workflow ON workflow_runs(workflow);
            CREATE INDEX IF NOT EXISTS idx_metric_snapshots_run ON metric_snapshots(run_id);
            CREATE INDEX IF NOT EXISTS idx_data_events_type ON data_events(event_type);
            """
        )
        conn.commit()
    finally:
        conn.close()
    return db_path


def _as_json(value: Any) -> str:
    return canonical_json(value or {})


def _bytes_len(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, bytes):
        return len(value)
    if isinstance(value, str):
        return len(value.encode("utf-8"))
    return len(_as_json(value).encode("utf-8"))


def _safe_rate(numerator: float | int | None, denominator: float | int | None) -> float | None:
    try:
        den = float(denominator or 0)
        if den <= 0:
            return None
        return round((float(numerator or 0) / den) * 100, 2)
    except Exception:
        return None


def _metric_row(run_id: str, workflow: str, metric_name: str, metric_value: Any, *, numerator: Any = None, denominator: Any = None, unit: str = "", metric_source: str = "real_usage") -> Dict[str, Any]:
    return {
        "run_id": run_id,
        "timestamp_utc": utc_now(),
        "workflow": workflow,
        "metric_name": metric_name,
        "metric_value": None if metric_value is None else float(metric_value),
        "numerator": None if numerator is None else float(numerator),
        "denominator": None if denominator is None else float(denominator),
        "unit": unit,
        "metric_source": metric_source,
    }


def derive_metrics(workflow: str, output: Dict[str, Any] | None, *, evaluation: Dict[str, Any] | None = None, citation_rows: List[Dict[str, Any]] | None = None, latency_ms: int = 0, source_count: int = 0) -> Dict[str, Any]:
    """Derive comparable metrics from an actual workflow output."""
    output = output or {}
    evaluation = evaluation or {}
    citation_rows = citation_rows or []
    workflow_lower = workflow.lower()

    metrics: Dict[str, Any] = {
        "latency_ms": int(latency_ms or 0),
        "source_count": int(source_count or 0),
        "output_sections": len([k for k, v in output.items() if v]),
        "output_bytes": _bytes_len(output),
        "completeness_score": evaluation.get("completeness_score"),
        "rule_verified_support_score": evaluation.get("rule_verified_support_score"),
        "citation_precision_proxy": evaluation.get("citation_precision_proxy"),
        "weak_citation_rows": evaluation.get("weak_citation_rows"),
    }
    metrics.update(negative_coverage_metrics(output))
    feedback = output.get("_human_feedback", {}) if isinstance(output.get("_human_feedback"), dict) else {}
    if feedback:
        for key in ["feedback_examples_used", "obligations_adjusted_by_feedback"]:
            if key in feedback and isinstance(feedback.get(key), (int, float)):
                metrics[key] = feedback.get(key)

    if citation_rows:
        checked = len(citation_rows)
        unsupported = len([r for r in citation_rows if (not r.get("exists")) or int(r.get("support_score") or 0) < 42])
        review = len([r for r in citation_rows if r.get("review_required")])
        metrics.update(
            {
                "checked_claims": checked,
                "unsupported_claims": unsupported,
                "unsupported_claim_rate": _safe_rate(unsupported, checked),
                "human_review_claims": review,
                "human_review_rate": _safe_rate(review, checked),
                "average_citation_support": round(sum(int(r.get("support_score") or 0) for r in citation_rows) / max(1, checked), 2),
            }
        )

    if "interpret" in workflow_lower or "compliance" in workflow_lower:
        obligations = output.get("obligation_extraction", []) or []
        requirements = output.get("product_requirements", []) or []
        qa = output.get("qa_test_cases", []) or []
        validations = output.get("validation_rules", []) or []
        metrics.update(
            {
                "obligations_total": len(obligations),
                "requirements_total": len(requirements),
                "qa_test_cases_total": len(qa),
                "validation_rules_total": len(validations),
                "qa_coverage_rate": _safe_rate(len(qa), len(obligations)),
                "requirement_coverage_rate": _safe_rate(len(requirements), len(obligations)),
            }
        )
    elif "discover" in workflow_lower or "product" in workflow_lower:
        pipeline = output.get("compliance_pipeline", []) or []
        tickets = output.get("jira_tickets", []) or []
        qa = output.get("qa_test_matrix", []) or []
        approvals = output.get("approval_workflow", []) or []
        metrics.update(
            {
                "pipeline_rows_total": len(pipeline),
                "jira_tickets_total": len(tickets),
                "qa_rows_total": len(qa),
                "approval_steps_total": len(approvals),
                "jira_to_pipeline_rate": _safe_rate(len(tickets), len(pipeline)),
                "qa_to_pipeline_rate": _safe_rate(len(qa), len(pipeline)),
            }
        )
    elif "communicate" in workflow_lower or "release" in workflow_lower:
        claim_risks = output.get("claim_risk_review", []) or output.get("claim_risk_table", []) or []
        rewrites = output.get("safer_rewrites", []) or output.get("safer_release_copy", []) or []
        approvals = output.get("approval_workflow", []) or []
        high_risk = [r for r in claim_risks if str(r.get("risk", r.get("severity", ""))).lower() in {"high", "critical"} or int(r.get("severity_score") or 0) >= 8]
        metrics.update(
            {
                "claims_reviewed_total": len(claim_risks),
                "high_risk_claims_total": len(high_risk),
                "safer_rewrites_total": len(rewrites),
                "approval_steps_total": len(approvals),
                "high_risk_claim_rate": _safe_rate(len(high_risk), len(claim_risks)),
                "release_risk_rewrite_rate": _safe_rate(len(rewrites), len(claim_risks)),
            }
        )
    elif "investigate" in workflow_lower or "timeline" in workflow_lower:
        events = output.get("chronological_timeline", []) or []
        actions = output.get("recommended_next_actions", []) or []
        contradictions = output.get("contradictions_or_inconsistencies", []) or []
        max_sev = max([int(e.get("severity_score") or 0) for e in events] or [0])
        metrics.update(
            {
                "events_total": len(events),
                "recommended_actions_total": len(actions),
                "contradictions_total": len(contradictions),
                "max_severity_score": max_sev,
                "action_to_event_rate": _safe_rate(len(actions), len(events)),
            }
        )
    return {k: v for k, v in metrics.items() if v is not None}


def record_workflow_run(*, workflow: str, actor: str, role: str, model: str, demo_mode: bool, input_payload: Any = None, output_payload: Any = None, latency_ms: int = 0, source_count: int = 0, metrics: Dict[str, Any] | None = None, metadata: Dict[str, Any] | None = None, db_path: Path = USAGE_DB_FILE) -> Dict[str, Any]:
    init_usage_db(db_path)
    timestamp = utc_now()
    input_hash = stable_hash(input_payload or {}, length=64) if input_payload is not None else ""
    output_hash = stable_hash(output_payload or {}, length=64) if output_payload is not None else ""
    metrics = metrics or {}
    metadata = {"schema_version": SCHEMA_VERSION, **(metadata or {})}
    run_id = f"run-{stable_hash({'timestamp': timestamp, 'workflow': workflow, 'input_hash': input_hash, 'output_hash': output_hash}, length=20)}"
    row = {
        "run_id": run_id,
        "timestamp_utc": timestamp,
        "workflow": workflow,
        "actor": actor or "demo-user",
        "role": role or "Product Manager",
        "model": model or "unknown",
        "demo_mode": 1 if demo_mode else 0,
        "input_hash": input_hash,
        "output_hash": output_hash,
        "input_bytes": _bytes_len(input_payload),
        "output_bytes": _bytes_len(output_payload),
        "source_count": int(source_count or 0),
        "latency_ms": int(latency_ms or 0),
        "metrics_json": _as_json(metrics),
        "metadata_json": _as_json(metadata),
    }
    row["signature"] = sign_payload(row)
    conn = connect(db_path)
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO workflow_runs (
                run_id, timestamp_utc, workflow, actor, role, model, demo_mode,
                input_hash, output_hash, input_bytes, output_bytes, source_count,
                latency_ms, metrics_json, metadata_json, signature
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["run_id"], row["timestamp_utc"], row["workflow"], row["actor"], row["role"], row["model"], row["demo_mode"],
                row["input_hash"], row["output_hash"], row["input_bytes"], row["output_bytes"], row["source_count"], row["latency_ms"],
                row["metrics_json"], row["metadata_json"], row["signature"],
            ),
        )
        for metric_name, value in metrics.items():
            if isinstance(value, (int, float)):
                conn.execute(
                    """
                    INSERT INTO metric_snapshots (run_id, timestamp_utc, workflow, metric_name, metric_value, numerator, denominator, unit, metric_source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (run_id, timestamp, workflow, metric_name, float(value), None, None, "", "real_usage"),
                )
        conn.commit()
    finally:
        conn.close()
    return row


def record_output_run(*, workflow: str, settings: Dict[str, Any], input_payload: Any, output_payload: Dict[str, Any], evaluation: Dict[str, Any] | None = None, citation_rows: List[Dict[str, Any]] | None = None, latency_ms: int = 0, source_count: int = 0, metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
    metrics = derive_metrics(workflow, output_payload, evaluation=evaluation, citation_rows=citation_rows, latency_ms=latency_ms, source_count=source_count)
    return record_workflow_run(
        workflow=workflow,
        actor=settings.get("demo_user", "demo-user"),
        role=settings.get("role", "Product Manager"),
        model=settings.get("model", "unknown"),
        demo_mode=bool(settings.get("demo_mode", True)),
        input_payload=input_payload,
        output_payload=output_payload,
        latency_ms=latency_ms,
        source_count=source_count,
        metrics=metrics,
        metadata=metadata or {},
    )


def record_data_event(*, event_type: str, actor: str, role: str, workflow: str, object_type: str, obj: Any, path: str = "", metadata: Dict[str, Any] | None = None, db_path: Path = USAGE_DB_FILE) -> Dict[str, Any]:
    init_usage_db(db_path)
    timestamp = utc_now()
    object_hash = stable_hash(obj or {}, length=64)
    row = {
        "timestamp_utc": timestamp,
        "event_type": event_type,
        "actor": actor or "demo-user",
        "role": role or "Product Manager",
        "workflow": workflow,
        "object_type": object_type,
        "object_hash": object_hash,
        "path": path,
        "metadata": metadata or {},
    }
    row["signature"] = sign_payload(row)
    conn = connect(db_path)
    try:
        cursor = conn.execute(
            """
            INSERT INTO data_events (timestamp_utc, event_type, actor, role, workflow, object_type, object_hash, path, metadata_json, signature)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (timestamp, event_type, row["actor"], row["role"], workflow, object_type, object_hash, path, _as_json(row["metadata"]), row["signature"]),
        )
        conn.commit()
        row["event_id"] = int(cursor.lastrowid)
    finally:
        conn.close()
    return row


def list_workflow_runs(limit: int = 100, db_path: Path = USAGE_DB_FILE) -> List[Dict[str, Any]]:
    init_usage_db(db_path)
    conn = connect(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM workflow_runs ORDER BY timestamp_utc DESC LIMIT ?",
            (int(limit),),
        ).fetchall()
    finally:
        conn.close()
    result: List[Dict[str, Any]] = []
    for row in rows:
        d = dict(row)
        try:
            d["metrics"] = json.loads(d.pop("metrics_json") or "{}")
        except Exception:
            d["metrics"] = {}
        try:
            d["metadata"] = json.loads(d.pop("metadata_json") or "{}")
        except Exception:
            d["metadata"] = {}
        result.append(d)
    return result


def list_metric_snapshots(limit: int = 500, db_path: Path = USAGE_DB_FILE) -> List[Dict[str, Any]]:
    init_usage_db(db_path)
    conn = connect(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM metric_snapshots ORDER BY id DESC LIMIT ?",
            (int(limit),),
        ).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]


def list_data_events(limit: int = 100, db_path: Path = USAGE_DB_FILE) -> List[Dict[str, Any]]:
    init_usage_db(db_path)
    conn = connect(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM data_events ORDER BY id DESC LIMIT ?",
            (int(limit),),
        ).fetchall()
    finally:
        conn.close()
    result = []
    for row in rows:
        d = dict(row)
        try:
            d["metadata"] = json.loads(d.pop("metadata_json") or "{}")
        except Exception:
            d["metadata"] = {}
        result.append(d)
    return result


def usage_summary(db_path: Path = USAGE_DB_FILE) -> Dict[str, Any]:
    runs = list_workflow_runs(limit=10_000, db_path=db_path)
    events = list_data_events(limit=10_000, db_path=db_path)
    workflows = sorted({r["workflow"] for r in runs})
    total_latency = sum(int(r.get("latency_ms") or 0) for r in runs)
    avg_latency = round(total_latency / max(1, len(runs))) if runs else 0
    by_workflow: List[Dict[str, Any]] = []
    for wf in workflows:
        wf_runs = [r for r in runs if r["workflow"] == wf]
        latest = wf_runs[0] if wf_runs else {}
        by_workflow.append(
            {
                "workflow": wf,
                "runs": len(wf_runs),
                "latest_timestamp_utc": latest.get("timestamp_utc", ""),
                "avg_latency_ms": round(sum(int(r.get("latency_ms") or 0) for r in wf_runs) / max(1, len(wf_runs))),
                "latest_output_bytes": latest.get("output_bytes", 0),
                "latest_signature_prefix": str(latest.get("signature", ""))[:18],
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "runs_total": len(runs),
        "data_events_total": len(events),
        "workflows_total": len(workflows),
        "avg_latency_ms": avg_latency,
        "by_workflow": by_workflow,
    }


def flatten_run_for_csv(run: Dict[str, Any]) -> Dict[str, Any]:
    flat = {k: v for k, v in run.items() if k not in {"metrics", "metadata"}}
    for key, value in (run.get("metrics") or {}).items():
        flat[f"metric_{key}"] = value
    for key, value in (run.get("metadata") or {}).items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            flat[f"metadata_{key}"] = value
    return flat


def rows_to_csv_bytes(rows: List[Dict[str, Any]]) -> bytes:
    if not rows:
        return b""
    output = io.StringIO()
    fieldnames: List[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def export_usage_payload(db_path: Path = USAGE_DB_FILE) -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "exported_at_utc": utc_now(),
        "summary": usage_summary(db_path),
        "workflow_runs": list_workflow_runs(limit=10000, db_path=db_path),
        "metric_snapshots": list_metric_snapshots(limit=100000, db_path=db_path),
        "data_events": list_data_events(limit=10000, db_path=db_path),
    }


def export_usage_json_bytes(db_path: Path = USAGE_DB_FILE) -> bytes:
    return json.dumps(export_usage_payload(db_path), indent=2, ensure_ascii=False, default=str).encode("utf-8")


def export_usage_zip_bytes(db_path: Path = USAGE_DB_FILE) -> bytes:
    payload = export_usage_payload(db_path)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("usage_metrics_export.json", json.dumps(payload, indent=2, ensure_ascii=False, default=str))
        zf.writestr("workflow_runs.csv", rows_to_csv_bytes([flatten_run_for_csv(r) for r in payload["workflow_runs"]]))
        zf.writestr("metric_snapshots.csv", rows_to_csv_bytes(payload["metric_snapshots"]))
        zf.writestr("data_events.csv", rows_to_csv_bytes(payload["data_events"]))
    return buf.getvalue()


def import_usage_payload(payload: Dict[str, Any], *, actor: str = "import-user", role: str = "Admin", db_path: Path = USAGE_DB_FILE) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Usage import must be a JSON object.")
    init_usage_db(db_path)
    imported_runs = 0
    imported_events = 0
    conn = connect(db_path)
    try:
        for run in payload.get("workflow_runs", []) or []:
            metrics = run.get("metrics") or {}
            metadata = {"imported_from_schema": payload.get("schema_version", "unknown"), **(run.get("metadata") or {})}
            conn.execute(
                """
                INSERT OR REPLACE INTO workflow_runs (
                    run_id, timestamp_utc, workflow, actor, role, model, demo_mode, input_hash, output_hash,
                    input_bytes, output_bytes, source_count, latency_ms, metrics_json, metadata_json, signature
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.get("run_id"), run.get("timestamp_utc") or utc_now(), run.get("workflow", "Imported"), run.get("actor", actor),
                    run.get("role", role), run.get("model", "unknown"), int(bool(run.get("demo_mode", True))), run.get("input_hash", ""), run.get("output_hash", ""),
                    int(run.get("input_bytes") or 0), int(run.get("output_bytes") or 0), int(run.get("source_count") or 0), int(run.get("latency_ms") or 0),
                    _as_json(metrics), _as_json(metadata), run.get("signature") or sign_payload(run),
                ),
            )
            imported_runs += 1
        conn.commit()
    finally:
        conn.close()
    record_data_event(event_type="import", actor=actor, role=role, workflow="Usage Metrics", object_type="usage_payload", obj=payload, metadata={"imported_runs": imported_runs, "source_schema": payload.get("schema_version")}, db_path=db_path)
    imported_events += 1
    return {"imported_runs": imported_runs, "imported_data_events": imported_events, "schema_version": payload.get("schema_version", "unknown")}


def save_export_package_locally(*, workflow: str, title: str, payload: Dict[str, Any], actor: str, role: str, output_dir: Path = EXPORT_DIR) -> Path:
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in title.lower()).strip("_") or "export"
    path = output_dir / f"{safe}_{timestamp}.json"
    package = {
        "schema_version": "v19.export.1",
        "exported_at_utc": utc_now(),
        "workflow": workflow,
        "title": title,
        "payload_hash": stable_hash(payload, length=64),
        "payload": payload,
    }
    package["signature"] = sign_payload(package)
    path.write_text(json.dumps(package, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    record_data_event(event_type="export", actor=actor, role=role, workflow=workflow, object_type="output_package", obj=package, path=str(path), metadata={"title": title})
    return path

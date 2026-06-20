"""Seed local usage metrics for portfolio review.

This creates realistic *local demo usage* runs so reviewers can inspect run
comparison and evidence report behavior. These are not production metrics.
"""
from services.connector_handoff_service import handoff_payloads
from services.portfolio_demo_service import hero_output_shape, release_gate_dashboard
from services.real_connectors_service import save_connector_payload_locally
from services.usage_metrics_service import record_data_event, record_output_run

settings = {
    "demo_user": "Marco Figueiredo",
    "role": "Product Manager",
    "model": "demo-mode",
    "demo_mode": True,
}

output = hero_output_shape()
release_gate = release_gate_dashboard(output)

for workflow, latency, metadata in [
    ("Interpret", 8200, {"session": "seed", "step": "obligations"}),
    ("Discover", 9300, {"session": "seed", "step": "requirement_jira_qa"}),
    ("Communicate", 4100, {"session": "seed", "step": "release_risk"}),
    ("Guided Portfolio Demo", 1200, {"session": "seed", "step": "hero", "release_gate_status": release_gate["overall_status"]}),
]:
    record_output_run(
        workflow=workflow,
        settings=settings,
        input_payload={"seed": True, "workflow": workflow, "source_hash": output["input_document_hash"]},
        output_payload=output,
        latency_ms=latency,
        source_count=1,
        metadata=metadata,
    )

for row in handoff_payloads(output):
    save_connector_payload_locally(connector=row["connector"], payload=row["payload"], actor="Marco Figueiredo", role="Product Manager")

record_data_event(
    event_type="seed_demo_usage_metrics",
    actor="Marco Figueiredo",
    role="Product Manager",
    workflow="Usage Metrics",
    object_type="seed_run",
    obj={"runs": 4, "note": "Local portfolio demo seed data"},
    metadata={"source": "scripts/seed_demo_usage_metrics.py"},
)

print("Seeded local portfolio usage metrics.")

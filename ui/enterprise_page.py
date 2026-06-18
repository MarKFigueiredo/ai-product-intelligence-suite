"""Enterprise readiness page."""
from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from services.enterprise_controls_service import (
    build_github_issue_payload,
    build_jira_issue_payload,
    can,
    document_version_record,
    list_audit_events,
    permission_rows,
    record_audit_event,
    signed_report_manifest,
)
from services.enterprise_readiness_service import deployment_checklist, enterprise_control_matrix, rbac_matrix
from services.real_connectors_service import (
    connector_statuses,
    create_github_issue,
    create_jira_issue,
    list_local_outbox,
)
from ui.visual_components import render_metric_pill, render_section_kicker


def render_enterprise_readiness_page(settings: dict | None = None) -> None:
    settings = settings or {}
    role = settings.get("role", "Product Manager")
    actor = settings.get("demo_user", "demo-user")

    st.header("Enterprise readiness — product controls")
    st.caption(
        "Transparent view of what the prototype now demonstrates versus what a production enterprise deployment still needs. "
        "v19 includes real local controls: role simulation, document hashes, SQLite audit events, signed report manifests and QA release gates."
    )

    controls = enterprise_control_matrix()
    partial = len([row for row in controls if "Partially" in row.get("status", "")])
    roadmap = len([row for row in controls if row.get("status") == "Roadmap"])
    cols = st.columns(4)
    with cols[0]:
        render_metric_pill("Controls mapped", str(len(controls)), "good")
    with cols[1]:
        render_metric_pill("Partially demoed", str(partial), "mid")
    with cols[2]:
        render_metric_pill("Roadmap gaps", str(roadmap), "bad" if roadmap else "good")
    with cols[3]:
        render_metric_pill("Production claim", "Not yet", "mid")

    render_section_kicker("Current demo identity and permissions")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_pill("Actor", actor, "neutral")
    with c2:
        render_metric_pill("Role", role, "good" if role in {"Admin", "Compliance Reviewer"} else "mid")
    with c3:
        render_metric_pill("Can sign reports", "Yes" if can(role, "sign_report") else "No", "good" if can(role, "sign_report") else "bad")
    with c4:
        render_metric_pill("Can view audit", "Yes" if can(role, "view_audit_log") else "No", "good" if can(role, "view_audit_log") else "bad")
    st.dataframe(pd.DataFrame(permission_rows(role)), width="stretch", hide_index=True)

    render_section_kicker("Implemented local controls")
    sample_doc = st.text_area(
        "Sample source text for document-version hash",
        value="SAF-T export validation must check customer tax ID, account reference, invoice totals and validation report evidence before release.",
        height=95,
    )
    version = document_version_record(
        document_name="hero_case_saf_t_einvoicing_sample.txt",
        content=sample_doc,
        uploaded_by=actor,
        role=role,
        version_label="hero-case-v1",
    )
    st.json(version)

    sample_report = {
        "case": "SAF-T / e-invoicing hero case",
        "summary": {"supported": 7, "weak": 2, "missing": 1, "reviewed": 10},
        "document_hash": version["document_hash"],
        "approval_boundary": "Portfolio demo report; not legal/compliance certification.",
    }
    manifest = signed_report_manifest(
        report=sample_report,
        signer=actor,
        signer_role=role,
        document_hash=version["document_hash"],
        approval_status="Reviewed" if can(role, "sign_report") else "Draft only - role cannot sign",
    )
    st.markdown("**Signed report manifest preview**")
    st.json(manifest)
    st.download_button(
        "Download signed report manifest JSON",
        json.dumps(manifest, indent=2, ensure_ascii=False).encode("utf-8"),
        "signed_report_manifest_demo.json",
        "application/json",
        width="stretch",
        key="download_enterprise_signed_report_manifest_json",
    )

    if st.button("Record demo audit event in SQLite", width="stretch"):
        event = record_audit_event(
            actor=actor,
            role=role,
            action="sign_report" if can(role, "sign_report") else "attempt_sign_report",
            workflow="Enterprise Readiness",
            document_hash=version["document_hash"],
            output=sample_report,
            metadata={"permission_allowed": can(role, "sign_report")},
        )
        st.success(f"Recorded SQLite audit event #{event['audit_event_id']} with signature {event['signature'][:20]}...")

    events = list_audit_events(limit=10)
    if events:
        st.markdown("**Recent SQLite audit events**")
        st.dataframe(pd.DataFrame(events), width="stretch", hide_index=True)
    else:
        st.info("No SQLite audit events recorded yet. Use the button above to persist one locally.")

    render_section_kicker("Connector configuration and local/live handoff")
    st.caption("v19 supports real local connector outbox files and optional live Jira/GitHub calls when credentials are configured via environment variables. Live mode is off by default.")
    st.dataframe(pd.DataFrame(connector_statuses()), width="stretch", hide_index=True)

    live_connectors = st.toggle("Enable live connector calls if credentials are configured", value=False, help="Off = save real payloads to local outbox. On = attempt live HTTP calls only if environment variables are present.")

    render_section_kicker("Jira connector payload")
    jira_payload = build_jira_issue_payload(
        requirement={
            "requirement_id": "R-SAF-T-001",
            "requirement": "Validate customer tax identifier, account reference and invoice total consistency before SAF-T export.",
            "priority": "High",
            "source_hash": version["document_hash"],
        },
        pipeline_row={"obligation_id": "O-SAF-T-001", "pipeline": "obligation → requirement → Jira → QA"},
        project_key="SAFT",
    )
    st.json(jira_payload)
    c_jira_1, c_jira_2 = st.columns(2)
    with c_jira_1:
        if st.button("Save/send Jira payload", width="stretch"):
            result = create_jira_issue(jira_payload, live=live_connectors, actor=actor, role=role)
            st.json(result)
    with c_jira_2:
        github_payload = build_github_issue_payload(
            title="Validate SAF-T invoice fields before export",
            body="Traceability: O-SAF-T-001 → R-SAF-T-001 → QA regression coverage. Source hash: " + version["document_hash"],
            labels=["compliance", "saf-t", "ai-assisted", "needs-review"],
        )
        if st.button("Save/send GitHub issue payload", width="stretch"):
            result = create_github_issue(github_payload, live=live_connectors, actor=actor, role=role)
            st.json(result)

    outbox = list_local_outbox(limit=20)
    if outbox:
        st.markdown("**Local connector outbox**")
        st.dataframe(pd.DataFrame(outbox), width="stretch", hide_index=True)

    render_section_kicker("Enterprise control matrix")
    st.dataframe(pd.DataFrame(controls), width="stretch", hide_index=True)

    render_section_kicker("Proposed RBAC")
    st.dataframe(pd.DataFrame(rbac_matrix()), width="stretch", hide_index=True)

    render_section_kicker("Secure deployment checklist")
    st.dataframe(pd.DataFrame(deployment_checklist()), width="stretch", hide_index=True)

    st.info(
        "v19 goes beyond slides with role simulation, permission checks, document hashes, SQLite audit events, signed report manifests, mandatory negative QA gates and API-shaped Jira/GitHub payload builders. "
        "Production SSO, tenant isolation, encrypted storage, managed OAuth integrations and production observability remain explicit roadmap items."
    )

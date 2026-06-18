"""Connector handoff center UI."""
from __future__ import annotations

import json
from typing import Any, Dict

import pandas as pd
import streamlit as st

from services.connector_handoff_service import handoff_payloads, send_or_save
from services.real_connectors_service import connector_statuses, list_local_outbox


def render_connector_handoff_page(settings: Dict[str, Any]) -> None:
    st.header("🔌 Connector Handoff Center")
    st.markdown("Preview, export or send Jira/GitHub/Slack-shaped payloads. Local outbox is the safe default; live send requires credentials and explicit opt-in.")

    st.subheader("Connector configuration")
    st.dataframe(pd.DataFrame(connector_statuses()), width="stretch", hide_index=True)

    live = st.toggle("Enable live connector send", value=False, help="When off, payloads are saved to the local connector outbox.")
    payloads = handoff_payloads()
    connector_names = [row["connector"] for row in payloads]
    selected = st.selectbox("Connector", connector_names)
    row = next(item for item in payloads if item["connector"] == selected)
    st.markdown(f"**Mode:** {'live' if live else row['default_mode']}")
    st.json(row["payload"])
    st.download_button(
        "Download payload JSON",
        json.dumps(row["payload"], indent=2, ensure_ascii=False).encode("utf-8"),
        f"{selected.lower()}_payload.json",
        mime="application/json",
        key=f"download_connector_payload_{selected.lower()}",
    )
    if st.button("Save/send payload"):
        result = send_or_save(
            selected,
            row["payload"],
            live=live,
            actor=settings.get("demo_user", "demo-user"),
            role=settings.get("role", "Product Manager"),
        )
        if result.get("ok"):
            st.success(result)
        else:
            st.error(result)

    st.subheader("Local connector outbox")
    outbox = list_local_outbox()
    if outbox:
        st.dataframe(pd.DataFrame(outbox), width="stretch", hide_index=True)
    else:
        st.info("No local connector payloads saved yet.")

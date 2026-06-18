"""Reusable visual components for the AI Product Intelligence Suite UI layer."""
from __future__ import annotations

import html
from typing import Any, Dict, Iterable, List, Sequence

from config import APP_NAME

import pandas as pd
import streamlit as st

from services.export_service import (
    dict_to_markdown,
    extract_named_tables,
    markdown_to_html_document,
    rows_to_csv_bytes,
    safe_filename,
)


def render_demo_banner(demo_mode: bool) -> None:
    if demo_mode:
        st.markdown(
            """
            <div class="demo-banner">
              <b>Demo Mode is ON</b> — the app uses synthetic portfolio outputs and does not call the OpenAI API.
              Turn Demo Mode off in the sidebar when you want live generation.
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_section_kicker(text: str) -> None:
    st.markdown(f'<div class="section-kicker">{html.escape(text)}</div>', unsafe_allow_html=True)


def render_card(title: str, body: Any = "", icon: str = "▣", badge: str | None = None) -> None:
    body_html = _format_body(body)
    badge_html = f'<span class="mini-badge">{html.escape(badge)}</span>' if badge else ""
    st.markdown(
        f"""
        <div class="ux-card">
          <div class="ux-card-title"><span class="ux-card-icon">{html.escape(icon)}</span>{html.escape(title)} {badge_html}</div>
          <div class="ux-card-body">{body_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_pill(label: str, value: str, tone: str = "neutral") -> None:
    st.markdown(
        f"""
        <div class="metric-pill metric-{tone}">
          <div class="metric-label">{html.escape(label)}</div>
          <div class="metric-value">{html.escape(str(value))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_score_bar(label: str, score: int | float | None, note: str = "") -> None:
    if score is None:
        score = 0
    score = max(0, min(100, int(round(float(score)))))
    tone = "good" if score >= 80 else "mid" if score >= 55 else "bad"
    st.markdown(
        f"""
        <div class="score-row">
          <div class="score-label"><b>{html.escape(label)}</b><span>{html.escape(note)}</span></div>
          <div class="score-track"><div class="score-fill score-{tone}" style="width:{score}%"></div></div>
          <div class="score-num">{score}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_grounding_heatmap(items: Sequence[Dict[str, Any]], title: str = "Grounding heatmap") -> None:
    st.subheader(title)
    if not items:
        st.info("No grounding items available yet.")
        return
    cols = st.columns(min(4, max(1, len(items))))
    for idx, item in enumerate(items):
        label = str(item.get("label") or item.get("obligation_id") or item.get("requirement_id") or f"Item {idx+1}")
        score = _extract_score(item)
        review = str(item.get("review") or item.get("human_review") or item.get("confidence") or "Review")
        with cols[idx % len(cols)]:
            render_score_bar(label, score, review)


def _unique_download_key(base: str) -> str:
    """Return a per-render unique key for Streamlit download buttons.

    Streamlit requires keys to be unique across the full rendered page. Some
    portfolio export panels can appear more than once with the same title and
    filename, so filename-derived keys alone are not safe.
    """
    counter_key = "_ai_pm_download_button_counter"
    st.session_state[counter_key] = int(st.session_state.get(counter_key, 0)) + 1
    return f"{base}_{st.session_state[counter_key]}"


def render_standard_export_bar(data: Dict[str, Any], title: str) -> str:
    markdown = dict_to_markdown(data, title)
    html_doc = markdown_to_html_document(markdown, title)
    tables = extract_named_tables(data)
    export_slug = safe_filename(title, "export").replace(".", "_")

    st.markdown('<div class="export-bar"><b>Export package</b></div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.download_button(
            "Markdown",
            markdown.encode("utf-8"),
            safe_filename(title, "md"),
            "text/markdown",
            width="stretch",
            key=_unique_download_key(f"download_{export_slug}_markdown"),
        )

    with c2:
        st.download_button(
            "HTML / Print to PDF",
            html_doc.encode("utf-8"),
            safe_filename(title, "html"),
            "text/html",
            width="stretch",
            key=_unique_download_key(f"download_{export_slug}_html"),
        )

    with c3:
        confluence = _to_confluence_markdown(markdown)
        st.download_button(
            "Confluence-style MD",
            confluence.encode("utf-8"),
            safe_filename(title + "_confluence", "md"),
            "text/markdown",
            width="stretch",
            key=_unique_download_key(f"download_{export_slug}_confluence"),
        )

    with c4:
        audit = _audit_trail(data, title)
        st.download_button(
            "Audit trail JSON",
            audit.encode("utf-8"),
            safe_filename(title + "_audit", "json"),
            "application/json",
            width="stretch",
            key=_unique_download_key(f"download_{export_slug}_audit"),
        )

    if tables:
        with st.expander("Structured CSV exports", expanded=False):
            for name, rows in tables.items():
                csv_slug = safe_filename(name, "csv").replace(".", "_")
                st.download_button(
                    f"{name}.csv",
                    rows_to_csv_bytes(rows),
                    safe_filename(name, "csv"),
                    "text/csv",
                    key=_unique_download_key(f"download_{export_slug}_{csv_slug}"),
                )

    return markdown


def render_table_preview(data: Dict[str, Any], preferred_keys: Iterable[str]) -> None:
    for key in preferred_keys:
        value = data.get(key)
        if isinstance(value, list) and value and isinstance(value[0], dict):
            st.subheader(key.replace("_", " ").title())
            st.dataframe(pd.DataFrame(value), width="stretch", hide_index=True)


def render_quality_gate_card(title: str, score: Any, missing: Any = None, recommendation: str = "") -> None:
    st.markdown('<div class="quality-card">', unsafe_allow_html=True)
    st.subheader(title)
    render_score_bar("Quality gate", _numeric_or_default(score, 75), recommendation)
    if missing:
        st.write("Missing / needs work")
        if isinstance(missing, list):
            for item in missing:
                st.write(f"- {item}")
        else:
            st.write(missing)
    st.markdown('</div>', unsafe_allow_html=True)


def render_placeholder_panel(title: str, placeholders: List[Dict[str, Any]]) -> None:
    st.subheader(title)
    if not placeholders:
        st.info("No screenshot placeholders generated yet.")
        return
    cols = st.columns(min(2, len(placeholders)))
    for idx, item in enumerate(placeholders):
        with cols[idx % len(cols)]:
            st.markdown(
                f"""
                <div class="screenshot-placeholder">
                  <div class="placeholder-title">{html.escape(str(item.get('screenshot') or item.get('title') or 'Screenshot'))}</div>
                  <div>{html.escape(str(item.get('purpose') or item.get('caption') or 'Add screenshot here'))}</div>
                  <small>{html.escape(str(item.get('caption') or 'Recommended for demo / README'))}</small>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _format_body(body: Any) -> str:
    if isinstance(body, list):
        return "<ul>" + "".join(f"<li>{html.escape(str(item))}</li>" for item in body[:6]) + "</ul>"
    if isinstance(body, dict):
        return "<br>".join(f"<b>{html.escape(str(k))}:</b> {html.escape(str(v))}" for k, v in list(body.items())[:6])
    return html.escape(str(body))


def _numeric_or_default(value: Any, default: int = 70) -> int:
    try:
        return int(float(value))
    except Exception:
        return default


def _extract_score(item: Dict[str, Any]) -> int:
    for key in ["grounding_score", "confidence_score", "score", "source_score", "readiness_score", "risk_score"]:
        if key in item:
            val = item.get(key)
            if isinstance(val, str):
                lowered = val.lower()
                if "high" in lowered:
                    return 90
                if "medium" in lowered:
                    return 65
                if "low" in lowered:
                    return 35
            return _numeric_or_default(val, 70)
    confidence = str(item.get("confidence", "")).lower()
    if "high" in confidence:
        return 90
    if "medium" in confidence:
        return 65
    if "low" in confidence:
        return 35
    return 72


def _to_confluence_markdown(markdown: str) -> str:
    intro = "# Confluence-ready page\n\n> Paste this into Confluence or use it as a structured page draft.\n\n"
    return intro + markdown


def _audit_trail(data: Dict[str, Any], title: str) -> str:
    import json
    from datetime import datetime
    payload = {
        "title": title,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "suite": APP_NAME,
        "audit_note": "Portfolio prototype export. Human review required before operational use.",
        "sections": list(data.keys()),
        "data": data,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)

# presentation helpers ------------------------------------------------------

def render_status_badge(label: str, tone: str = "info") -> str:
    """Return a compact status badge as HTML."""
    tone = tone if tone in {"good", "warning", "bad", "info"} else "info"
    return f'<span class="status-badge badge-{tone}">{html.escape(str(label))}</span>'


def status_tone(status: str) -> str:
    lower = str(status or "").lower()
    if any(word in lower for word in ["pass", "ready", "approved", "real local", "reviewed", "supported"]):
        return "good"
    if any(word in lower for word in ["block", "missing", "incorrect", "not implemented", "high risk", "failed"]):
        return "bad"
    if any(word in lower for word in ["warning", "weak", "optional", "simulated", "needs"]):
        return "warning"
    return "info"


def render_page_intro(title: str, subtitle: str, badges: Sequence[str] | None = None) -> None:
    badge_html = "".join(render_status_badge(badge, "info") for badge in (badges or []))
    st.markdown(
        f"""
        <div class="page-intro">
          <div class="section-kicker">Portfolio review path</div>
          <h2 style="margin:.1rem 0 .25rem 0;color:#0f172a;letter-spacing:-.02em;">{html.escape(title)}</h2>
          <div style="color:#475569;line-height:1.45;max-width:980px;">{html.escape(subtitle)}</div>
          <div style="margin-top:.65rem;">{badge_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_grid(items: Sequence[Dict[str, Any]]) -> None:
    """Render compact KPI cards using native Streamlit containers.

    Earlier versions used a single custom HTML grid. On some Streamlit
    versions, nested HTML blocks were partially interpreted as Markdown code
    blocks, exposing raw ``<div>`` text in the app. Native containers are less
    decorative but much safer for public deployment.
    """
    if not items:
        return
    cols = st.columns(min(4, max(1, len(items))))
    for idx, item in enumerate(items):
        with cols[idx % len(cols)]:
            with st.container(border=True):
                st.caption(str(item.get("label", "")))
                st.markdown(f"**{html.escape(str(item.get('value', '')))}**")
                note = str(item.get("note", ""))
                if note:
                    st.caption(note)

def render_vertical_timeline(events: Sequence[Dict[str, Any]], title: str | None = None) -> None:
    """Render a timeline with native Streamlit elements to avoid raw HTML leaks."""
    if title:
        st.markdown(f"### {html.escape(title)}")
    if not events:
        st.info("No timeline events available yet.")
        return

    for index, event in enumerate(events, start=1):
        time = event.get("timestamp") or event.get("time") or event.get("date") or ""
        event_title = event.get("event") or event.get("title") or event.get("artifact_id") or "Event"
        body = event.get("description") or event.get("status") or event.get("owner") or event.get("artifact_type") or ""
        badge_parts = []
        if event.get("owner"):
            badge_parts.append(f"Owner: {event['owner']}")
        if event.get("status"):
            badge_parts.append(f"Status: {event['status']}")
        if event.get("artifact_id"):
            badge_parts.append(f"Artifact: {event['artifact_id']}")

        with st.container(border=True):
            heading = f"{index}. {event_title}"
            st.markdown(f"**{html.escape(str(heading))}**")
            if time:
                st.caption(str(time))
            if body:
                st.write(str(body))
            if badge_parts:
                st.caption(" · ".join(str(part) for part in badge_parts))

def render_compact_card_grid(items: Sequence[Dict[str, Any]], columns: int = 3) -> None:
    cols = st.columns(columns)
    for idx, item in enumerate(items):
        with cols[idx % columns]:
            render_card(
                str(item.get("title", "Card")),
                item.get("body", ""),
                str(item.get("icon", "▣")),
                str(item.get("badge")) if item.get("badge") else None,
            )


def render_callout(text: str, tone: str = "info", title: str | None = None) -> None:
    safe_title = f"<b>{html.escape(title)}</b><br/>" if title else ""
    st.markdown(f'<div class="callout {html.escape(tone)}">{safe_title}{html.escape(text)}</div>', unsafe_allow_html=True)

"""Central configuration for AI PM Winning Suite."""
from __future__ import annotations

import os

APP_VERSION = "1.04"
APP_NAME = f"AI Product Intelligence Suite {APP_VERSION}"
APP_TAGLINE = (
    "Portfolio case study for regulated enterprise AI workflows — core pipeline, human feedback flywheel, and guided UX review."
)

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
DEFAULT_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

AVAILABLE_MODELS = [
    DEFAULT_MODEL,
    "gpt-4.1-mini",
    "gpt-4o-mini",
    "o4-mini",
]
# Keep unique order while allowing env default to appear first.
AVAILABLE_MODELS = list(dict.fromkeys(AVAILABLE_MODELS))

LANGUAGES = [
    "English",
    "Portuguese (Portugal)",
    "Portuguese (Brazil)",
    "Spanish",
    "French",
    "German",
    "Italian",
]

DETAIL_LEVELS = ["Concise", "Standard", "Detailed"]

WORKFLOWS = {
    "Guided Demo — Portfolio Review": "guided_demo",
    "Landing — Public Portfolio Page": "landing_page",
    "About — Marco Figueiredo": "about_me",
    "Discover — Product Discovery Studio": "product_discovery",
    "Interpret — Compliance-to-Product Studio": "compliance_studio",
    "Communicate — Release Readiness Copilot": "release_readiness",
    "Investigate — Decision Timeline Builder": "decision_timeline",
    "Limitations & Benchmark": "limitations",
    "Enterprise Readiness": "enterprise_readiness",
    "Usage Metrics & Data": "usage_metrics",
    "Lineage & Staleness": "lineage",
    "Connector Handoff Center": "connector_handoff",
    "Real Usage Evidence Report": "evidence_report",
    "Approval Workflow": "approval_workflow",
    "Document Versions & Impact": "document_versions",
    "Quality Learning Loop": "quality_learning",
    "Claim Hygiene Audit": "claim_hygiene",
}

# The full app deliberately keeps every artifact available, but the sidebar defaults to
# a focused review path so hiring reviewers are not overwhelmed by every deep-dive tab.
CORE_REVIEW_WORKFLOWS = {
    "Guided Demo — Portfolio Review": "guided_demo",
    "Interpret — Compliance-to-Product Studio": "compliance_studio",
    "Discover — Product Discovery Studio": "product_discovery",
    "Communicate — Release Readiness Copilot": "release_readiness",
    "Investigate — Decision Timeline Builder": "decision_timeline",
    "Real Usage Evidence Report": "evidence_report",
    "Claim Hygiene Audit": "claim_hygiene",
}

DEEP_DIVE_WORKFLOWS = {
    key: value for key, value in WORKFLOWS.items() if key not in CORE_REVIEW_WORKFLOWS
}

REVIEW_MODES = {
    "Focused review path": CORE_REVIEW_WORKFLOWS,
    "Full artifact map": WORKFLOWS,
}

CSS = """
<style>
:root {
    --bg-dark: #020617;
    --bg-panel: #0f172a;
    --blue: #2563eb;
    --cyan: #06b6d4;
    --violet: #7c3aed;
    --green: #10b981;
    --amber: #f59e0b;
    --red: #ef4444;
    --slate: #475569;
    --border: #e2e8f0;
    --muted: #64748b;
    --card: #ffffff;
}
.block-container { padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1280px; }
[data-testid="stSidebar"] { background: #f8fafc; border-right: 1px solid #e2e8f0; }
.hero {
    padding: 1.45rem 1.55rem;
    border-radius: 26px;
    background:
        radial-gradient(circle at 18% 18%, rgba(37,99,235,.40), transparent 30%),
        radial-gradient(circle at 80% 12%, rgba(6,182,212,.24), transparent 34%),
        linear-gradient(135deg, #020617 0%, #0f172a 56%, #172554 100%);
    color: white;
    margin-bottom: 1.1rem;
    border: 1px solid rgba(148, 163, 184, 0.22);
    box-shadow: 0 22px 55px rgba(2, 6, 23, 0.28);
}
.hero h1 { color: white; font-size: 2.15rem; margin: 0 0 .18rem 0; letter-spacing: -0.035em; }
.hero p { color: #dbeafe; font-size: 1rem; max-width: 1050px; margin: 0; line-height:1.45; }
.page-intro {
    padding: 1rem 1.05rem;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    margin-bottom: 1rem;
    color:#334155;
}
.demo-banner {
    padding: .75rem 1rem;
    border-radius: 16px;
    background: linear-gradient(90deg, #ecfeff, #eff6ff);
    border: 1px solid #bae6fd;
    color: #075985;
    margin-bottom: 1rem;
}
.section-kicker { color: #2563eb; font-weight: 900; letter-spacing: .055em; text-transform: uppercase; font-size: .72rem; margin: .7rem 0 .25rem; }
.ux-card, .landing-card, .quality-card, .persona-card, .evidence-card, .claim-card {
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 1rem 1.05rem;
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    margin-bottom: 0.82rem;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06), 0 12px 28px rgba(15, 23, 42, 0.035);
}
.ux-card.compact { padding: .82rem .9rem; border-radius: 16px; }
.ux-card-title { font-weight: 850; color: #0f172a; margin-bottom: .35rem; line-height:1.25; }
.ux-card-icon { display: inline-flex; width: 1.55rem; height: 1.55rem; align-items: center; justify-content: center; border-radius: .55rem; background: #dbeafe; color: #1d4ed8; margin-right: .48rem; font-size:.88rem; font-weight:900; }
.ux-card-body { color: #334155; font-size: .90rem; line-height: 1.45; }
.compact-grid { display:grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap:.72rem; margin:.75rem 0 1rem; }
@media (max-width: 900px) { .compact-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.kpi-card { border:1px solid #e2e8f0; border-radius:18px; padding:.85rem .95rem; background:#fff; }
.kpi-label { font-size:.70rem; text-transform:uppercase; letter-spacing:.055em; font-weight:850; color:#64748b; }
.kpi-value { font-size:1.25rem; font-weight:900; color:#0f172a; margin-top:.15rem; }
.kpi-note { font-size:.76rem; color:#64748b; margin-top:.15rem; }
.status-badge, .mini-badge, .badge {
    display: inline-block;
    padding: 0.22rem 0.58rem;
    border-radius: 999px;
    background: #e0e7ff;
    color: #3730a3;
    font-size: 0.74rem;
    margin-right: 0.35rem;
    margin-bottom: 0.35rem;
    font-weight: 850;
    border:1px solid transparent;
}
.badge-good { background:#dcfce7; color:#166534; border-color:#bbf7d0; }
.badge-warning { background:#fef3c7; color:#92400e; border-color:#fde68a; }
.badge-bad { background:#fee2e2; color:#991b1b; border-color:#fecaca; }
.badge-info { background:#dbeafe; color:#1d4ed8; border-color:#bfdbfe; }
.metric-pill {
    border-radius: 18px;
    padding: .85rem 1rem;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    margin-bottom: .7rem;
}
.metric-label { font-size: .72rem; color: #64748b; text-transform: uppercase; font-weight: 850; letter-spacing: .05em; }
.metric-value { font-size: 1.35rem; font-weight: 900; color: #0f172a; }
.metric-good { background:#ecfdf5; border-color:#bbf7d0; }
.metric-mid { background:#fffbeb; border-color:#fde68a; }
.metric-bad { background:#fef2f2; border-color:#fecaca; }
.export-bar { padding: .75rem 1rem; border-radius: 16px; border: 1px solid #dbeafe; background: #eff6ff; margin: .7rem 0; color:#1e3a8a; }
.score-row { margin: .55rem 0 .9rem; }
.score-label { display:flex; justify-content:space-between; gap:1rem; font-size:.86rem; color:#334155; margin-bottom:.25rem; }
.score-label span { color:#64748b; font-size:.78rem; }
.score-track { height: 10px; background: #e2e8f0; border-radius: 999px; overflow: hidden; }
.score-fill { height: 10px; border-radius:999px; }
.score-good { background: linear-gradient(90deg, #10b981, #22c55e); }
.score-mid { background: linear-gradient(90deg, #f59e0b, #facc15); }
.score-bad { background: linear-gradient(90deg, #ef4444, #fb7185); }
.score-num { font-size:.78rem; color:#64748b; text-align:right; }
.module-tile {
    border: 1px solid rgba(219, 234, 254, .45);
    background: rgba(15, 23, 42, .72);
    color: #dbeafe;
    border-radius: 18px;
    padding: 1rem;
    height: 100%;
}
.module-tile h4 { color: white; margin: 0 0 .3rem 0; }
.source-panel {
    border: 1px solid #e2e8f0;
    background: #ffffff;
    border-radius: 16px;
    padding: .9rem 1rem;
    max-height: 520px;
    overflow-y: auto;
}
.source-id { font-weight: 850; color: #1d4ed8; }
mark { background: #fef08a; padding: 0.05rem 0.15rem; border-radius: 0.2rem; }
.timeline-wrap { position:relative; margin: .7rem 0 1rem 0; padding-left:1.1rem; }
.timeline-wrap:before { content:""; position:absolute; left:.35rem; top:.25rem; bottom:.25rem; width:2px; background:#cbd5e1; }
.timeline-node { position:relative; margin:0 0 .72rem 0; padding:.76rem .9rem; border-radius:16px; background:#fff; border:1px solid #e2e8f0; box-shadow:0 1px 2px rgba(15,23,42,.05); }
.timeline-node:before { content:""; position:absolute; left:-1.02rem; top:.95rem; width:.62rem; height:.62rem; border-radius:999px; background:#2563eb; border:2px solid #dbeafe; }
.timeline-time { font-size:.72rem; color:#64748b; font-weight:850; text-transform:uppercase; letter-spacing:.045em; }
.timeline-title { font-weight:900; color:#0f172a; margin-top:.12rem; }
.timeline-body { font-size:.86rem; color:#334155; margin-top:.14rem; }
.actor-chip { display:inline-block; padding:.35rem .55rem; border-radius:999px; background:#ecfeff; color:#0e7490; border:1px solid #a5f3fc; margin:.2rem; font-size:.83rem; }
.alert-card { border:1px solid #fecaca; background:#fef2f2; color:#7f1d1d; border-radius:14px; padding:.8rem .95rem; margin-bottom:.6rem; }
.callout { border-radius:18px; padding:1rem 1.05rem; margin:.8rem 0; border:1px solid #e2e8f0; }
.callout.info { background:#eff6ff; border-color:#bfdbfe; color:#1e3a8a; }
.callout.warning { background:#fffbeb; border-color:#fde68a; color:#92400e; }
.callout.good { background:#ecfdf5; border-color:#bbf7d0; color:#166534; }
.screenshot-placeholder {
    border: 1.5px dashed #93c5fd;
    background: linear-gradient(180deg, #eff6ff, #f8fafc);
    border-radius: 18px;
    padding: 1rem;
    min-height: 145px;
    color:#334155;
}
.placeholder-title { font-weight: 850; color:#1d4ed8; margin-bottom:.35rem; }
.cta-box {
    padding: 1.1rem 1.2rem;
    border-radius: 18px;
    background: #0f172a;
    color: white;
    margin-top: 1rem;
}
.cta-box a { color: #bfdbfe; }
.small-muted { color:#64748b; font-size:.85rem; }
</style>
"""

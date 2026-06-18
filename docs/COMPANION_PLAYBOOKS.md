# Companion playbooks

The core public app remains focused on AI product workflows for regulated enterprise software. Companion playbooks are kept separate so they can support future projects without expanding the Streamlit app scope.

## Companion 1 — AI Payments Compliance Assistant

Path:

```text
companion_playbooks/ai_payments_compliance/Playbook_Draft_AI_Payments_Compliance_EN.docx
```

Related summary:

```text
docs/AI_PAYMENTS_COMPLIANCE_MIT_COURSE_COMPANION.md
```

Purpose:

- support the MIT Sloan Executive Education course **Implementing Agentic AI: Building Your Organizational Playbook**;
- demonstrate a third regulated domain: SEPA / ISO 20022 / CBPR+ payments compliance;
- serve as the seed for a separate project using different AI/low-code tooling;
- show governance, stakeholder mapping, rollout and adoption thinking beyond the main app.

Why it is not a new app module:

The main app already contains enough breadth. Adding the payments assistant as another tab would weaken scope discipline. The better signal is to keep it as a companion artifact and develop it as a separate course/project deliverable.

How it complements the portfolio:

| Portfolio asset | What it demonstrates |
|---|---|
| AI Product Intelligence Suite 1.04 | product workflow, testing, evaluation, traceability and local instrumentation |
| Payments Compliance Assistant playbook | organizational implementation, governance, stakeholder adoption and phased rollout |

Recommended next step:

Use the course frameworks to refine the playbook, then build a lightweight prototype in a different toolchain such as n8n + Airtable/Sheets + LLM + Slack/email notification.

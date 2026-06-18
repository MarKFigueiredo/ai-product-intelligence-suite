# AI Payments Compliance Assistant — MIT course companion playbook

Status: working companion artifact, not part of the core Streamlit app.

This companion playbook adds a third domain to the portfolio story: **payments compliance / ISO 20022 / SEPA structured addresses**. It is intentionally kept separate from the main app because the next project is expected to use different agentic-AI and low-code tools.

## Why this belongs beside, not inside, the app

The public app demonstrates a Python/Streamlit product case study: compliance source material → obligations → requirements → QA → release communication → audit evidence.

The MIT course companion demonstrates a different skill: designing an **organizational playbook** for implementing an agentic workflow in a regulated payments process.

Keeping it separate avoids scope creep while still showing generalization across domains:

1. SAF-T PT / e-invoicing — main hero workflow.
2. Swiss QR-Bill — compact second-domain generalization check.
3. SEPA / ISO 20022 structured addresses — companion MIT playbook for agentic workflow implementation.

## Course fit

The course goal is to develop a practical playbook that maps an existing business process to an AI agent-driven workflow, while considering governance, risk and stakeholder trust. This companion playbook is well aligned because it starts from a real business process: interpreting payments rule changes and translating them into functional requirements, validation rules, test cases and release communication.

The draft already includes:

- existing process / as-is workflow;
- proposed to-be agentic workflow;
- Tool vs. Teammate positioning;
- stakeholder map and RACI;
- build-vs-buy and design alternatives;
- governance and risk management;
- incident response scenario;
- success metrics and evaluation plan;
- phased implementation roadmap;
- change management and adoption;
- limitations and next steps.

## How it maps to the main portfolio pipeline

| Main portfolio concept | Payments playbook equivalent |
|---|---|
| Source document | SEPA / ISO 20022 / CBPR+ structured-address regulatory change |
| Obligation extraction | Mandatory structured address fields, hybrid vs. fully structured handling, free-text limits |
| Reviewer mode | Compliance specialist checkpoint |
| Requirement generation | Functional requirements and validation rules |
| QA coverage | Test cases for missing town/country, long free-text lines, partial addresses, non-Latin characters |
| Negative test gate | Reject missing mandatory fields, over-length lines, unsupported address formats |
| Release communication | Customer-facing release notes and support guidance |
| Incident learning | Wrong threshold example: 80 characters generated instead of 70 |
| Governance | Tool-not-teammate, RACI, audit trail, confidence calibration, escalation |

## What should be improved during the MIT course

This draft is strong as a starting point, but should be refined as the course introduces its own frameworks and templates.

Priorities:

1. Replace placeholders with course-specific framework language.
2. Add a real workflow diagram for the as-is and to-be process.
3. Add a one-page final canvas using the course template when available.
4. Validate the regulatory requirement details with public sources before public portfolio use.
5. Add one sample structured JSON output from the proposed agent.
6. Add a manual baseline estimate, clearly marked as estimated or anonymized.
7. Add a small shadow-run evaluation table once a real or historical example is tested.

## Recommended separate project shape

This should become a separate project from the Streamlit app, using a different toolchain to diversify the portfolio.

Suggested stack:

- n8n, Make or Zapier for orchestration;
- Airtable or Google Sheets for review queue / approval status;
- Claude, ChatGPT, Gemini or other LLM tools for agent outputs;
- Slack or email for notification;
- a simple dashboard for review metrics.

Suggested workflow:

```text
regulatory change pasted/uploaded
→ agent drafts summary, requirements, validation rules, test cases and release notes
→ output lands in review table as Pending
→ compliance specialist edits/approves/rejects
→ feedback is saved as examples for prompt improvement
→ approved output is exported to product/engineering handoff
```

## Boundaries

This companion artifact should not claim production readiness. It should remain framed as a course playbook and future project concept until it has real user feedback, baseline data and reviewed outputs.

Do not claim:

- autonomous compliance approval;
- legal correctness;
- production deployment;
- measured productivity gains without baseline data.

Safe claim:

> This companion playbook demonstrates how I would frame, govern and pilot an agentic AI workflow for payments compliance, using human review and phased rollout before any production reliance.

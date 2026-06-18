# Screenshot and 90-Second Demo Script

This script is optimized for hiring conversations. The goal is not to show every feature. The goal is to show one credible hero workflow that demonstrates AI product judgment.

## Required screenshots

1. Landing page hero with the portfolio-case-study positioning.
2. Interpret dashboard with the SAF-T/e-invoicing source document, extracted obligations and citations.
3. Reviewer mode showing one corrected/missing obligation.
4. Discover pipeline showing `obligation → requirement → Jira → QA`.
5. Communicate table showing `claim → risk → reason → safer rewrite`.
6. Enterprise Readiness page showing local controls: role simulation, audit store, document hashes and signed report manifest.
7. Synthetic evaluation results.
8. Portfolio review guide / What This Demonstrates page.

## 90-second demo script

### 0–10s — Positioning

“This is a portfolio case study, not a commercial product. It demonstrates how I design AI product workflows for regulated enterprise software: domain understanding, workflow design, human review, risk-aware communication, evaluation discipline, enterprise readiness judgment and product strategy.”

### 10–25s — The problem

“Compliance-heavy product teams often lose traceability between source obligations, product requirements, QA coverage, release communication and incident learning. The result is slow delivery, weak auditability and risky customer-facing claims.”

### 25–45s — Hero workflow: Interpret

“The hero case uses SAF-T PT / e-invoicing. The workflow starts with a source document, extracts obligations, checks source support and asks a human reviewer to mark items as correct, weak, missing or incorrect.”

### 45–60s — Product pipeline: Discover

“Reviewed obligations are then converted into implementation artefacts: a before/after requirement, a Jira-style ticket, acceptance criteria and QA cases. The important chain is `obligation → requirement → Jira → QA`.”

### 60–73s — Risk-aware communication: Communicate

“The same change is checked before customer communication. The release note review identifies risky claims, explains the risk and generates a safer rewrite so the team avoids overpromising compliance.”

### 73–83s — Enterprise judgment

“This is still a prototype, so I do not claim production SSO or real OAuth integrations. I implemented local controls to show product and technical judgment: role simulation, SQLite audit events, document hashes and signed report manifests.”

### 83–90s — Close

“The point is not that AI writes faster. The point is that AI-assisted product work in regulated environments needs evidence, review, risk controls and auditable decisions.”

## 15-second version

“This project demonstrates how I think as an AI PM: I take ambiguous compliance input, turn it into reviewed obligations, product requirements, Jira tickets, QA cases, safer release communication and audit evidence — while showing failure modes, trade-offs and limitations honestly.”

## What not to do in a live demo

- Do not click through every module equally.
- Do not lead with screenshots before explaining the hero workflow.
- Do not describe it as a commercial product.
- Do not overstate synthetic metrics as production evidence.
- Do not claim legal/compliance advice.

## Best live-demo path

1. Open README and state the portfolio positioning.
2. Open Interpret with the SAF-T sample.
3. Show extracted obligations and reviewer correction.
4. Show generated requirement/Jira/QA pipeline.
5. Show release-risk rewrite.
6. Show final audit report / evaluation metrics.
7. End with what the project demonstrates about your PM skills.


## v19 note — mandatory negative test coverage

v19 adds a deterministic QA release gate: every obligation mapped into the product workflow must have at least one obligation-linked negative/edge/failure test. This demonstrates product-quality judgment beyond happy-path generation.

---

## v20 guided demo update

For hiring conversations, start in the app with **Guided Demo — Portfolio Review** instead of opening individual modules first.

Recommended flow:

```text
Guided Demo — Portfolio Review
→ Persona paths: Hiring Manager or Principal PM
→ Hero workflow: show the 10-step SAF-T/e-invoicing chain
→ Release gates: show mandatory negative test coverage
→ Evidence drawer: show one obligation and one risky release claim
→ Lineage & staleness: show downstream impact of reviewer correction
→ What this proves: map skills to evidence
→ Real vs simulated: show honest implementation boundaries
→ Connector Handoff Center: preview Jira/GitHub/Slack payloads
→ Real Usage Evidence Report: show persisted usage metrics/export
```

The goal is to demonstrate product judgment and reviewability, not every feature.

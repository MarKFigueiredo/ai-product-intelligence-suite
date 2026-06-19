
## v1.04 15-second opening option

“This is a portfolio case study, not a commercial product. One important lesson in building it was claim hygiene: an earlier version used self-scoring language, so I removed that and built an automated scanner to prevent overclaims from returning. The project now demonstrates not only AI workflow generation, but also review, validation, scope discipline and evidence.”

# Demo Walkthrough for Hiring Conversations

This project is a portfolio case study, not a commercial product. The demo should show how I design AI product workflows for regulated enterprise software.

## 90-second demo

1. Open the app and select **Guided Demo — Portfolio Review**.
2. Choose the **Hiring Manager** or **Principal PM** persona.
3. Show the 10-step SAF-T/e-invoicing workflow.
4. Highlight the before/after requirement:
   - Before: vague validation requirement.
   - After: scoped, testable, source-aware requirement.
5. Open **Release gates**.
6. Show mandatory negative test coverage and explain why happy-path QA is insufficient.
7. Open **Evidence drawer** for one obligation.
8. Show source excerpt, hash, reviewer decision, linked requirement and linked QA.
9. Open **Lineage & staleness**.
10. Show how a reviewer correction can make downstream artefacts stale.
11. Open **What this proves**.
12. Summarize skills demonstrated: domain understanding, AI workflow design, human review, QA thinking, risk-aware communication, evaluation and enterprise readiness judgment.

## 30-second explanation

I built a portfolio-grade AI product case study for regulated enterprise software. It turns a SAF-T/e-invoicing source excerpt into obligations, reviewer corrections, product requirements, Jira-shaped tickets, QA cases with mandatory negative coverage, safer release communication, incident learning and an audit-ready report. The project also persists real usage metrics locally, supports import/export, creates connector handoff payloads and clearly separates real local controls from simulated production controls.

## What to emphasize

- This is not for sale; it is a proof of product judgment and execution.
- The strongest signal is the complete workflow, not any single feature.
- Metrics are separated into synthetic evaluation and real usage telemetry.
- The product blocks release readiness when negative QA coverage is missing.
- The lineage view shows downstream impact when source/reviewer decisions change.
- The connector handoff center shows real payload thinking without pretending full enterprise integration.

## Likely interview questions

### What is real?

Real local: SQLite usage metrics, import/export JSON/CSV/ZIP, document/output hashes, local connector outbox, release gates, negative test coverage checks, evidence report generation and local export packages.

### What is simulated?

RBAC is simulated. Live Jira/GitHub/Slack sending is optional and credential-dependent. SSO, multi-tenancy, encrypted storage and immutable audit logs are documented roadmap items, not implemented SaaS capabilities.

### What was the hardest product trade-off?

Depth vs breadth. I chose to keep the portfolio broad enough to show cross-functional PM judgment, then sharpened it around one hero workflow so reviewers can see a coherent product narrative.

### What would you do next with real users?

Run 10–20 realistic sessions with Product, QA and Compliance reviewers, export the usage data, analyze reviewer correction patterns and use that to refine obligation extraction, QA coverage and communication risk scoring.

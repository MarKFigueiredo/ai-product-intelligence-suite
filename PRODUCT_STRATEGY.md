# Product Strategy — AI Product Intelligence Suite

## One-line positioning

**Compliance-to-Product Traceability Copilot for regulated enterprise software teams.**

The product helps teams convert compliance, regulatory and technical source material into auditable obligations, product requirements, Jira-ready implementation work, QA coverage, safer release communication and post-incident learning.

## Strategic wedge

Start with one painful workflow:

> **Interpret:** upload/paste a compliance source document and produce a reviewed, source-grounded compliance-to-product traceability package.

Expansion modules should support this wedge, not compete with it:

```text
Interpret → Discover → Communicate → Investigate
source obligations → product scope → safe release → learning loop
```

## ICP — Ideal Customer Profile

| ICP dimension | Definition |
|---|---|
| Company type | B2B enterprise software companies serving regulated industries. |
| Stage | Series B–public companies with product, QA, support and compliance functions. |
| Domains | Tax compliance, logistics ERP, finance, RegTech, GovTech, healthcare admin, enterprise workflow platforms. |
| Trigger event | Regulatory change, audit preparation, customer escalation, release risk, compliance-heavy roadmap item. |
| Existing workflow | Product/legal/compliance guidance scattered across PDFs, Confluence, spreadsheets, Jira tickets, QA matrices and support notes. |
| Pain severity | High when missed requirements can cause customer escalations, delayed releases, audit exposure or unsafe claims. |

## User personas

| Persona | Jobs to be done | Pain | Product value |
|---|---|---|---|
| Compliance Product Manager | Translate regulatory guidance into product scope and engineering work. | Manual interpretation, weak traceability, review bottlenecks. | Faster requirement drafting with source evidence and reviewer workflow. |
| QA Lead | Ensure obligations have test coverage. | Requirements arrive late or lack testable rules. | Obligation-to-QA matrix and evidence checklist. |
| Compliance / Legal Reviewer | Approve obligations and customer-facing wording. | Hard to see what is supported versus inferred. | Reviewer mode, claim risk table, signed report manifest. |
| Support Lead | Explain release changes safely to customers. | Overclaim risk and inconsistent answers. | Safer release copy and customer escalation boundaries. |
| Engineering Lead | Understand implementation-ready scope. | Ambiguous requirements and shifting interpretations. | Jira-style tickets with source obligations and acceptance criteria. |
| Product Ops / Auditor | Reconstruct decisions months later. | Decisions live in Slack/docs and are hard to audit. | Run history, document hashes, audit events and final reports. |

## Buyer

| Buyer | Why they care |
|---|---|
| VP Product / Head of Product | Reduce release risk, accelerate compliance roadmap work and improve cross-functional quality. |
| Head of Compliance / Legal Ops | Preserve evidence, reduce unsupported claims and maintain review boundaries. |
| VP Engineering / QA | Improve requirement clarity, testability and traceability. |
| COO / GM for regulated product line | Reduce customer escalations and audit/rework cost. |

## Primary use cases

1. **Regulatory change intake** — turn new guidance into obligations and product impact.
2. **Compliance-heavy PRD creation** — generate requirements, validation rules, acceptance criteria and Jira-ready tickets.
3. **QA coverage review** — map obligations to test cases and evidence.
4. **Release communication safety** — rewrite risky customer-facing claims.
5. **Customer escalation/postmortem** — reconstruct what was missed and how to prevent recurrence.

## Adoption path

| Phase | User action | Product capability | Success signal |
|---|---|---|---|
| 1. Try | Upload one known compliance/source document. | Interpret extracts obligations and source quotes. | User finds the traceability matrix useful enough to review. |
| 2. Trust | Reviewer marks obligations Correct / Needs review / Incorrect. | Reviewer mode and final report. | User corrects at least one AI output and sees a better package. |
| 3. Operationalise | Export requirements/Jira/QA package. | Discover pipeline and Jira-shaped payloads. | Engineering/QA accepts the package as a starting point. |
| 4. Govern | Use signed manifest and audit events. | Document hash, output hash, SQLite audit log, report manifest. | Team can reconstruct what changed and who reviewed it. |
| 5. Expand | Add release copy and incident learning. | Communicate and Investigate modules. | Reduction in unsafe release claims and recurring incidents. |

## Pricing hypothesis

| Tier | Target | Packaging | Hypothesis |
|---|---|---|---|
| Team | Small product/compliance team | Limited documents/runs, export package, local review workflow. | Good for pilots and proof of value. |
| Business | Department or product line | Shared workspace, Jira/Confluence integration, reviewer workflows, run history. | Main monetisation tier. |
| Enterprise | Multi-tenant regulated org | SSO/RBAC, encrypted storage, audit retention, legal hold, custom connectors, deployment controls. | Required for procurement and production use. |

Potential pricing metric: number of reviewed traceability packages per month, with enterprise add-ons for retention, connectors and advanced audit.

## North Star Metric

**Reviewed obligations converted into accepted product/QA artefacts per month.**

Why: it measures the core value loop, not just AI generation volume.

## Activation metric

A new workspace is activated when:

1. at least one source document is processed;
2. at least five obligations are extracted;
3. at least one reviewer decision is recorded;
4. at least one requirement or QA artefact is exported.

## Retention metric

**Monthly teams with at least one reviewed traceability package and one downstream artefact export.**

Supporting retention signals:

- repeat use after regulatory/source document changes;
- reviewer decisions per run;
- Jira/QA export frequency;
- reduction in repeated unsupported claims;
- audit report downloads during customer/security reviews.

## Expansion strategy

| Expansion | Why it follows naturally |
|---|---|
| Jira/Confluence sync | Requirements and QA evidence already need to enter delivery tools. |
| Slack/Support escalation ingestion | Incidents reveal gaps in requirements, release notes and customer promises. |
| Compliance rule packs | Reusable domain-specific obligations improve speed and consistency. |
| Audit/retention controls | Enterprise buyers need evidence and governance. |
| Team approval workflow | Product, QA, Support and Legal need role-specific sign-off. |
| Benchmark/evaluation dashboard | Buyers need evidence that the tool reduces risk and review burden. |

## Roadmap

### P0 — Make the hero workflow undeniable

- Deep SAF-T/e-invoicing hero case.
- Reviewer corrections and final audit report.
- Synthetic evaluation metrics with clear limitations.
- Role simulation, document hashes, SQLite audit events and signed report manifest.
- Jira mock payload with API-shaped schema.

### P1 — Make it usable for a pilot

- Real workspace objects: source document, run, obligation, requirement, test case, review decision.
- SQLite/Postgres persistence beyond local demo JSONL.
- RBAC enforced across core actions.
- Jira/Confluence export/import with OAuth mock or sandbox.
- Evaluation dashboard comparing manual baseline, simple LLM baseline and assisted workflow.

### P2 — Make it enterprise-procurable

- SSO/SAML/OIDC.
- Tenant isolation and encrypted object storage.
- Managed audit log retention and legal hold.
- Secrets manager and production deployment pipeline.
- Observability: trace ID, latency, failure rate, model spend and reviewer SLA.
- Data retention policy UI and purge jobs.

### P3 — Make it defensible

- Domain-specific rule packs.
- Reviewer feedback dataset.
- Continuous evaluation on source/output pairs.
- Integration marketplace.
- Customer-specific compliance workflow templates.

## Key risks and mitigations

| Risk | Why it matters | Mitigation |
|---|---|---|
| False confidence | Users may overtrust AI outputs. | Always show source quotes, support scores, reviewer status and limitations. |
| Unsupported legal claims | Release notes may imply guaranteed compliance. | Claim-risk table and Legal/Compliance approval workflow. |
| Data sensitivity | Source documents can contain customer or confidential data. | Hash-by-default, retention policy, encrypted storage roadmap. |
| Integration friction | Enterprise workflows live in Jira/Confluence/Slack/GitHub. | Start with export payloads, then OAuth connectors. |
| Reviewer burden | Human-in-the-loop can become slow. | Prioritise weak/missing claims and high-risk obligations. |
| Evaluation credibility | Synthetic metrics can be overread. | Label clearly as synthetic; add human-reviewed gold sets and baselines. |
| Procurement blockers | SSO/RBAC/audit/retention required. | Implement minimal controls now, document production path clearly. |

## Competitive angle

This should not be positioned as a generic PM assistant or chatbot. The differentiated angle is:

1. source-grounded obligations;
2. human reviewer decisions;
3. requirement/Jira/QA traceability;
4. safer external communication;
5. audit reconstruction and incident learning.

## What not to build first

- Do not build a broad “AI suite for every PM task.”
- Do not claim legal compliance automation.
- Do not prioritise polished dashboards over reviewer trust and traceability.
- Do not add many shallow modules before the hero workflow is credible.

## Strategic summary

The winning product narrative is:

> “We help regulated enterprise software teams turn compliance ambiguity into auditable product delivery.”

The winning demo narrative is:

> “Here is one source document. Here are the obligations. Here is what the AI got wrong. Here is how the reviewer corrected it. Here is the requirement, Jira ticket, QA test, release-safe copy, incident if missed and final signed audit report.”


## Companion artifact boundary — Payments Compliance Assistant

The AI Payments Compliance Assistant playbook is a useful third-domain companion, but it should not be folded into the core app as another module. It is intended for a separate MIT course project using different tools, which strengthens the portfolio by showing that the same product judgment can be applied across implementation styles without expanding the Streamlit app scope.

# What This Project Demonstrates

This is a portfolio case study, not a commercial product.

It demonstrates how I approach AI product management for regulated enterprise workflows: problem framing, workflow design, human review, risk controls, evaluation, enterprise readiness and product strategy.

## Core thesis

Regulated product teams lose traceability between source obligations, product requirements, QA coverage, release communication and incident learning. This project shows how an AI-assisted workflow can preserve that chain while keeping humans accountable for review and approval.

## Skills-to-evidence map

| Skill | Evidence in this repo | Why it matters for hiring |
|---|---|---|
| Domain understanding | SAF-T PT / e-invoicing hero case | Shows I can work in complex compliance/product domains. |
| Product systems thinking | Source → obligation → requirement → Jira → QA → release → incident | Shows I think in end-to-end workflows, not isolated features. |
| AI product judgment | RAG, citation support, reviewer mode, supported/weak/missing reports | Shows I design AI with controls, not just generation. |
| Human-in-the-loop design | Reviewer corrections, approval workflow, decision log | Shows I understand accountability in enterprise AI. |
| Risk communication | `claim → risk → reason → safer rewrite` | Shows I can reduce customer-facing and compliance risk. |
| Evaluation discipline | Synthetic benchmark, gold-set metrics, limitation notes | Shows I know the difference between demo metrics and product proof. |
| Enterprise readiness awareness | Role simulation, SQLite audit store, document hashes, signed manifest | Shows production awareness without pretending to have full enterprise infrastructure. |
| Product strategy | `PRODUCT_STRATEGY.md` | Shows ICP, buyer, wedge, adoption path, roadmap and metrics. |
| Technical PM execution | Tests, services, scripts, mock connectors, sample inputs | Shows I can prototype and collaborate credibly with engineering. |
| Communication | README, review guide, demo script, case study | Shows I can package complexity for different audiences. |

## What this intentionally does not claim

- It does not claim to be a commercial product.
- It does not claim production-grade SSO, RBAC, tenancy or encrypted storage.
- It does not claim legal/compliance advice.
- It does not claim production performance from synthetic metrics.
- It does not replace Product, QA, Legal or Compliance review.

## Interview positioning

Use this sentence:

> “This project demonstrates how I design AI product workflows that turn ambiguous compliance inputs into auditable product decisions.”

Then explain the workflow:

1. Input source document.
2. Extract obligations.
3. Reviewer corrects unsupported, weak or missing items.
4. Convert reviewed obligations into requirements, Jira tickets and QA cases.
5. Rewrite risky release communication.
6. Preserve audit evidence, version hashes and decision history.
7. Show failure modes and trade-offs explicitly.



## v1.04 note — mandatory negative test coverage

v1.04 adds a deterministic QA release gate: every obligation mapped into the product workflow must have at least one obligation-linked negative/edge/failure test. This demonstrates product-quality judgment beyond happy-path generation.

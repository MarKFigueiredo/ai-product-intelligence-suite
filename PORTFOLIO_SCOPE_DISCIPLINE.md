# Portfolio Scope Discipline

This repository intentionally contains more than one module because the case study demonstrates a cross-functional AI product workflow: compliance interpretation, product discovery, QA coverage, release communication, incident learning, enterprise controls and metrics.

The risk is obvious: too many tabs can make the portfolio feel unfocused. v23 introduced focused navigation, and v1.04 makes the scope decision explicit. It addresses that risk by separating the project into two review modes.

## Focused review path

This is the default app mode. It shows only the smallest path needed to evaluate the product judgment:

1. Guided Demo — Portfolio Review
2. Interpret — Compliance-to-Product Studio
3. Discover — Product Discovery Studio
4. Communicate — Release Readiness Copilot
5. Investigate — Decision Timeline Builder
6. Real Usage Evidence Report
7. Claim Hygiene Audit

Use this mode for recruiters, hiring managers and time-boxed reviewers.

## Full artifact map

This mode exposes every deep-dive artifact: enterprise readiness, usage metrics, lineage/staleness, connector handoff, approval workflow, document versions, quality learning and limitations.

Use this mode for Principal/Staff PM, Engineering, QA, Compliance or academic reviewers who want to inspect how the system thinks about governance, quality and operational evidence.

## Scope decision

The project is deliberately not positioned as a commercial SaaS product. The scope boundary is:

- show the end-to-end regulated product workflow;
- implement local evidence, metrics, export/import and governance controls where useful;
- document production gaps honestly;
- avoid building full SSO, multi-tenancy, deployment hardening or production connector infrastructure.

The intended signal is not “I built everything.”

The intended signal is: **I know which parts matter for product judgment, which parts need evidence, which parts should be gated, and which parts should remain out of scope for a portfolio prototype.**


## What I intentionally did not build

I intentionally did not build:

- production SSO/SAML/OIDC;
- multi-tenant RBAC enforcement;
- encrypted tenant document storage;
- full Jira OAuth or marketplace app;
- full Slack bot;
- Confluence sync;
- billing, admin console or commercial packaging;
- production deployment hardening.

Reason: these would make the repository look broader, but they would not materially improve the hiring signal for AI product judgment. For a portfolio prototype, the better signal is to show local evidence of the right product concerns — hashes, audit events, import/export, connector outbox, approval states, claim hygiene and quality gates — while clearly stating what production would require.

## What I stopped adding after v1.04

The next step is not another enterprise module. v24 focuses on validation and generalization:

- validate the citation verifier against human labels;
- publish error analysis;
- add one compact second-domain case;
- make the auto-score-to-scanner learning story visible;
- keep advanced modules behind the full artifact map.

## 1.01 scope decision

1.01 focuses on core pipeline structure, human feedback reuse and guided UX. It intentionally does not add new domains, new connectors, new approval states or new dashboards. The aim is to show that the portfolio can get deeper without getting broader.

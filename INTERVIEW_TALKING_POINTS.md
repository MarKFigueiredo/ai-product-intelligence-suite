# Interview Talking Points

This document helps explain the portfolio case study in interviews. The goal is to show product judgment, not to sell the prototype as production software.

## 30-second version

I built a portfolio case study for AI product workflows in regulated enterprise software. The hero case uses SAF-T PT / e-invoicing and shows how source material can be transformed into obligations, reviewed requirements, Jira-style tickets, QA cases, safer release communication and an audit-ready report. The project demonstrates product strategy, human-in-the-loop AI, evaluation discipline, enterprise readiness judgment and hands-on prototyping.

## Why I built this

I wanted to demonstrate that AI PM work is not just prompt writing. In enterprise and compliance-heavy environments, the hard problem is preserving trust across the whole workflow: source evidence, product decisions, QA coverage, customer communication and post-incident learning.

## Why SAF-T / e-invoicing

SAF-T and e-invoicing are strong portfolio cases because they contain the type of ambiguity, conditional logic and audit expectations that enterprise product teams face in real life. They are specific enough to be credible and complex enough to show product judgment.

## What I intentionally did not build

I did not build production SSO, real tenant isolation, encrypted document storage, OAuth-backed integrations or production observability. Instead, I implemented local controls such as role simulation, SQLite audit events, document hashes, signed report manifests and API-shaped Jira/GitHub mock payloads. This shows production awareness without pretending a portfolio prototype is a production platform.

## Biggest trade-off

The main trade-off was breadth vs depth. Earlier versions showed multiple workflows. v16/v18 reposition the project around one hero workflow: compliance-to-product traceability. The other modules now support that story instead of competing with it.

## How I would measure success with real users

I would compare manual work, a simple LLM baseline and this assisted workflow across the same compliance input. I would measure time to first requirement set, obligation recall, unsupported claim rate, QA coverage, reviewer correction rate, release-risk reduction and user confidence after review.

## How I would improve it with real data

I would run a human study with PM, QA and Compliance reviewers, expand the gold set, classify errors using the formal taxonomy, test failure cases, validate Jira/Confluence payloads with real workflows and add stronger security architecture only after confirming the highest-value workflow.

## What this project demonstrates about me

- I can frame an ambiguous enterprise problem.
- I can design an AI workflow with review, evidence and risk controls.
- I can think across Product, QA, Support, Legal/Compliance and Engineering.
- I can define synthetic evaluation honestly when real data is unavailable.
- I can prototype enough to make the strategy concrete.
- I can communicate limitations without weakening the value of the work.

## Questions I expect and how I would answer

### Is this a product you are trying to sell?

No. It is a portfolio case study. It demonstrates how I approach AI product management in regulated enterprise workflows.

### Why not build full enterprise auth and integrations?

Because that would be the wrong portfolio trade-off. I wanted to show product and technical judgment with local controls, then document what production-grade implementation would require.

### How do you avoid hallucinations?

The workflow uses source grounding, quote-level support checks, supported/weak/missing classifications, reviewer mode, decision logs and safer release rewrites. It does not treat AI output as final truth.

### What is the most important product insight?

In regulated AI workflows, value comes from auditable decisions, not just faster generation.

### What would you build next?

I would run a small user evaluation, expand the gold-set benchmark, add stale-output propagation after reviewer corrections, and validate real Jira/Confluence workflow payloads.



## v19 note — mandatory negative test coverage

v19 adds a deterministic QA release gate: every obligation mapped into the product workflow must have at least one obligation-linked negative/edge/failure test. This demonstrates product-quality judgment beyond happy-path generation.

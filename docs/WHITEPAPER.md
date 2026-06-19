# Whitepaper: AI Product Intelligence Suite 1.04

**Subtitle:** Human-in-the-loop AI workflows for regulated enterprise product teams  
**Format:** Portfolio case study, not a commercial product  
**Primary domain:** SAF-T PT / e-invoicing compliance-to-product traceability

---

## Abstract

AI Product Intelligence Suite 1.04 demonstrates how AI-assisted workflows can help regulated enterprise product teams convert ambiguous compliance source material into reviewable, testable and audit-aware product decisions.

The project is intentionally not positioned as a production compliance platform. Instead, it shows how a product team can design a workflow that combines domain understanding, AI-assisted drafting, human review, QA coverage, release-risk communication and audit traceability.

The central artifact is not a chatbot. It is a structured product workflow:

```text
source material → obligations → reviewer corrections → requirements → Jira-style tickets → QA coverage → safer release communication → audit evidence
```

---

## 1. Background

Enterprise software teams working in compliance-heavy domains face recurring problems:

- regulatory text is difficult to translate into product requirements;
- traceability is often lost between source obligations and implementation artifacts;
- QA coverage may focus on positive paths and miss failure modes;
- release notes may overclaim what a feature supports;
- audit evidence is distributed across documents, tickets, conversations and test plans.

Large language models can help draft, structure and summarize this work, but they introduce new risks: unsupported claims, hallucinated obligations, weak evidence alignment and over-automation of decisions that should remain human-reviewed.

This project explores a safer pattern: use AI to accelerate structured product work, while keeping review, evidence, limitations and approval visible.

---

## 2. Design principles

### 2.1 Human review before product decisions

AI output is treated as draft material. The system design assumes a reviewer must confirm or correct obligations before they become requirements, QA cases or release statements.

### 2.2 Evidence over fluency

The workflow prioritizes source-linked evidence and citation-support checks over polished narrative output.

### 2.3 Negative testing as a release gate

For regulated workflows, positive-path QA is insufficient. The system requires negative or failure-mode coverage for obligations that enter the release pipeline.

### 2.4 Real vs simulated capability labeling

The project distinguishes local portfolio controls from production enterprise capabilities. This prevents the portfolio from overclaiming maturity.

### 2.5 Scope discipline

The hero case remains SAF-T PT / e-invoicing. Companion domains, such as Swiss QR-Bill and ISO 20022, are used to show generalization thinking without diluting the core workflow.

---

## 3. System workflow

```text
Regulatory source material
        ↓
Interpret: obligations, evidence and traceability
        ↓
Review: human corrections and reviewer state
        ↓
Discover: requirements, assumptions, risks and gaps
        ↓
QA: positive and negative coverage mapping
        ↓
Communicate: risky claims and safer release wording
        ↓
Investigate: incident timeline and decision log
        ↓
Audit package: supported, weak, missing and reviewed artifacts
```

The workflow is designed to make product decisions more traceable rather than to replace expert judgment.

---

## 4. Core modules

### Interpret — Compliance-to-Product Studio

Converts source material into obligation candidates, evidence snippets, reviewer decisions and traceable product inputs.

### Discover — Product Discovery Studio

Turns reviewed inputs into requirement candidates, assumptions, Jira-style tickets, Gherkin acceptance criteria and PRD completeness checks.

### Communicate — Release Readiness Copilot

Flags risky product claims and suggests safer language with scope boundaries and approval caveats.

### Investigate — Decision Timeline Builder

Builds incident timelines with owners, severity, customer impact, contradictions and postmortem actions.

---

## 5. Quality controls

Implemented as local portfolio controls:

- citation-support heuristics;
- claim hygiene scanner;
- mandatory negative test coverage;
- reviewer mode;
- approval workflow simulation;
- document hashes and versioning;
- local usage metrics;
- connector outbox payloads;
- final audit report export.

These controls demonstrate product judgment and system design. They are not claims of production SaaS readiness.

---

## 6. Evaluation approach

The project uses a mix of deterministic checks and portfolio evaluations:

| Evaluation area | Method |
|---|---|
| Obligation extraction | Gold-set comparison and support scoring |
| Claim hygiene | Rule-based risky-claim scanner |
| Citation support | Token, semantic and mismatch heuristics |
| QA coverage | Positive and mandatory negative coverage matrix |
| Scope discipline | Real vs simulated capability labeling |
| Documentation quality | Portfolio review paths and limitation docs |

A future production-grade evaluation would require larger labeled datasets, human inter-rater review and domain-specific validation by compliance experts.

---

## 7. Enterprise readiness boundaries

The project demonstrates readiness judgment by explicitly naming what is not production-ready:

- production SSO;
- multi-tenant RBAC;
- encrypted tenant storage;
- immutable audit logging;
- real OAuth integrations with Jira, Slack or Confluence;
- production observability;
- legal/compliance approval;
- deployment hardening.

This is important because overstating maturity would weaken trust. The value of the portfolio is showing how these controls should be reasoned about, not pretending a local prototype is a production platform.

---

## 8. Why this matters for AI product management

A common AI demo pattern is a model connected to an interface. This project shows a broader product discipline:

- defining a regulated workflow;
- designing a human-in-the-loop review pattern;
- translating compliance text into product artifacts;
- requiring QA and negative coverage;
- controlling release communication risk;
- producing audit-ready evidence;
- acknowledging limitations and scope.

This combination emphasizes enterprise AI product patterns rather than a generic chatbot demo.

---

## 9. Future work

The most valuable next improvements are not more modules. They are sharper evaluation and better storytelling:

1. 60–90 second demo video;
2. three real screenshots in the README;
3. human validation of citation-support heuristics;
4. lightweight external reviewer feedback;
5. one real connector integration or a stricter mock connector contract;
6. simplified Start Here / Hero Demo app route.

---

## 10. Conclusion

AI Product Intelligence Suite 1.04 is a portfolio case study showing how AI can support product teams in regulated domains when paired with human review, evidence, QA coverage and explicit limitations.

Its value is not that it automates compliance. Its value is that it demonstrates how to design AI product workflows that respect compliance-sensitive decision-making.


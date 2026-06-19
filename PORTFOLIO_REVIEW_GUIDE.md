# Portfolio Review Guide

This project is a portfolio case study, not a commercial product.

It demonstrates how I design AI product workflows for regulated enterprise software:

1. domain understanding;
2. AI workflow design;
3. human-in-the-loop review;
4. risk-aware communication;
5. evaluation discipline;
6. enterprise readiness judgment;
7. product strategy.

The goal is not to prove that this Streamlit prototype is production-ready. The goal is to show how I think, design, evaluate, communicate and execute as an AI/Product Manager working in compliance-heavy enterprise environments.

---

## Read this in 5 minutes

Start here if you are a recruiter, hiring manager or interviewer doing a first-pass screen.

1. **App: Guided Demo — Portfolio Review** — use the persona paths and hero workflow for fastest understanding.
2. **README opening section** — understand the positioning and what the project is / is not.
3. **`HERO_CASE_STUDY.md`** — read the short hero case summary.
4. **`WHAT_THIS_DEMONSTRATES.md`** — see the skills-to-evidence mapping.
5. **`docs/HERO_SAF_T_EINVOICING_CASE.md`** — skim the workflow headings only.
6. **`docs/SYNTHETIC_EVALUATION_RESULTS.md`** — review the metric table and honesty note.

What you should learn in 5 minutes:

- The project is a portfolio proof of AI PM ability, not a SaaS pitch.
- The hero workflow is SAF-T PT / e-invoicing compliance-to-product traceability.
- The strongest signal is the chain from source obligation to requirement, Jira, QA, safer release communication and audit report.
- The project includes honest limitations and synthetic evaluation labels.

---

## Review this in 15 minutes

Use this path if you are a hiring manager, Principal PM, product leader or technical interviewer.

1. **App: Guided Demo — Portfolio Review** — release gates, evidence drawer, lineage and real-vs-simulated table.
2. **`README.md`** — product thesis, workflow summary and local run instructions.
3. **`docs/HERO_SAF_T_EINVOICING_CASE.md`** — deep case walkthrough.
4. **`docs/ERROR_TAXONOMY_FAILURE_MODES.md`** — formal error taxonomy, failure cases and trade-offs.
5. **`PRODUCT_STRATEGY.md`** — ICP, personas, wedge, adoption path, metrics and roadmap.
6. **`docs/SYNTHETIC_EVALUATION_RESULTS.md`** — benchmark framing and synthetic results.
7. **`SCREENSHOT_AND_DEMO_SCRIPT.md`** — how the project should be presented live.

What you should learn in 15 minutes:

- How I structure ambiguous regulatory input into product decisions.
- How I use AI without hiding uncertainty or failure modes.
- How I think about human review, risk, quality and downstream workflow integration.
- How I separate prototype implementation from production-readiness claims.

---

## Deep dive in 45 minutes

Use this path for serious evaluation of product judgment, implementation and technical PM credibility.

1. Open the Interpret workflow and use the SAF-T/e-invoicing sample input.
2. Review how obligations, citation support, reviewer corrections and final reports are represented.
3. Open Discover and inspect the `obligation → requirement → Jira → QA` pipeline.
4. Open Communicate and review the `claim → risk → reason → safer rewrite` table.
5. Open Enterprise Readiness and inspect local role simulation, audit store, document hashes and signed report manifest.
6. Run tests with `pytest`.
7. Run the synthetic hero evaluation with:

```bash
python scripts/run_synthetic_hero_evaluation.py
```

What you should learn in 45 minutes:

- I can move from product thesis to working prototype.
- I can define evaluation metrics and limitations.
- I can model enterprise controls without pretending a prototype is production software.
- I can communicate product strategy, risk and implementation trade-offs.

---

## What this project demonstrates about my skills

| Skill | Where to see it | What it demonstrates |
|---|---|---|
| Domain understanding | SAF-T / e-invoicing hero case | Ability to work with compliance-heavy enterprise workflows. |
| Product framing | README, `PRODUCT_STRATEGY.md` | Ability to define ICP, wedge, users, buyer, metrics and roadmap. |
| AI workflow design | Interpret → Discover → Communicate → Investigate | Ability to design AI as a workflow, not a single prompt. |
| Human-in-the-loop judgment | Reviewer mode, decision log, approval workflow | Ability to place humans at the right decision points. |
| Risk-aware communication | Claim risk table and safer rewrites | Ability to prevent unsafe customer-facing claims. |
| Evaluation discipline | Synthetic evaluation, gold-set framing, metric limitations | Ability to measure quality honestly without overstating results. |
| Enterprise readiness judgment | RBAC simulation, audit store, hashes, signed report manifest | Ability to reason about production needs without overbuilding. |
| Technical PM execution | Services, scripts, tests, sample data | Ability to prototype concretely and collaborate with engineering. |
| Storytelling | Hero case, demo script, review guide | Ability to package complexity for different audiences. |

---

## Recommended reviewer path by persona

| Reviewer | Best path |
|---|---|
| Recruiter | README → `WHAT_THIS_DEMONSTRATES.md` → `HERO_CASE_STUDY.md` |
| Hiring manager | README → Hero case → Product strategy → Demo script |
| Principal PM | Product strategy → Error taxonomy/trade-offs → Hero case → Evaluation results |
| Engineering lead | Architecture → Enterprise controls service → Tests → Evaluation scripts |
| Compliance/legal stakeholder | Hero case → Claim risk table → Error taxonomy → Validation limitations |
| Startup product leader | README → Product strategy → Enterprise readiness → Interview talking points |

---

## One-sentence summary

I design AI product workflows that turn ambiguous compliance inputs into auditable product decisions.



## v1.02 note — mandatory negative test coverage

v11.02 adds a deterministic QA release gate: every obligation mapped into the product workflow must have at least one obligation-linked negative/edge/failure test. This demonstrates product-quality judgment beyond happy-path generation.


## v1.03 note — guided review experience

v1.03 adds an in-app **Guided Demo — Portfolio Review** workflow so reviewers do not need to infer the product story from repository structure. It includes persona paths, release gates, evidence drawer, lineage/staleness, run comparison, skill evidence and real-vs-simulated capability status.


## v1.04 validation-first review path

After the 5-minute portfolio review, use these files to inspect the two concerns a skeptical reviewer is likely to raise:


1. **Is the citation verifier credible beyond hand-tuned heuristics?**
   - Read `docs/CITATION_VERIFIER_VALIDATION_STUDY.md`.
   - Inspect `validation/citation_claims_sample.csv`.
   - Note that human labels are intentionally pending, not fabricated.

2. **Does the Interpret workflow generalize beyond SAF-T?**
   - Read `docs/SWISS_QR_BILL_SECOND_DOMAIN_CASE.md`.
   - Run `python scripts/run_swiss_qr_bill_benchmark.py`.

This is the intended v1.04 signal: fewer new modules, more validation discipline.

## v1.04 scope discipline note

The app now defaults to a focused review path. This is intentional: a hiring reviewer should not need to inspect every deep-dive tab to understand the thesis. The full artifact map remains available for detailed Principal PM, Engineering, QA, Compliance or academic review.


## 1.01 technical review additions

For architecture and AI product learning-loop review, see:

- `docs/CORE_PIPELINE_ARCHITECTURE.md`
- `docs/HUMAN_FEEDBACK_FLYWHEEL.md`
- `docs/UX_DENSITY_REDUCTION_V25.md`


## Companion course artifact

For reviewers interested in how this work extends into agentic AI implementation and organizational playbook design, see:

- `docs/COMPANION_PLAYBOOKS.md`
- `docs/AI_PAYMENTS_COMPLIANCE_MIT_COURSE_COMPANION.md`

The payments playbook is intentionally not another app module. It is a separate MIT course companion that shows governance, adoption and rollout thinking for a payments compliance workflow.

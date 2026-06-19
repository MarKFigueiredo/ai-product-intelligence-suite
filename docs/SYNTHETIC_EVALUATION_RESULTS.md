# Synthetic Evaluation Results — SAF-T/e-invoicing Hero Case

## Scope and honesty note

This is a **synthetic one-case evaluation**. It is designed to show measurement discipline for a portfolio project. It does not prove legal accuracy, production compliance readiness or performance across industries.

The evaluation compares three baselines:

1. **Manual baseline estimate** — how a PM/QA team might work from docs/spreadsheets without the tool.
2. **Simple LLM baseline** — a one-shot prompt with no reviewer workflow, traceability matrix or deterministic checks.
3. **Assisted workflow** — the v1.04 hero workflow using source-grounded obligations, reviewer mode, rule-based checks, QA mapping, release risk review and audit manifest.

## Headline metrics

| Metric | Manual baseline | Simple LLM baseline | Assisted workflow | Interpretation |
|---|---:|---:|---:|---|
| Time to first requirement set | 45 min | 14 min | 8 min | Faster drafting because obligations and traceability templates are reused. |
| Unsupported claim rate | 18% | 22% | 6% | Reviewer mode and claim risk checks reduce unsupported or overbroad statements. |
| QA coverage | 60% | 68% | 90% | Explicit obligation-to-QA mapping surfaces gaps. |
| Negative test coverage | 0% | 35% | 100% | v1.04 blocks release-ready status unless every mapped obligation has a negative/edge/failure test. |
| Reviewer correction rate | N/A | 30% | 40% | Higher is acceptable here because the workflow exposes uncertainty and corrections. |
| Missing obligation recall on gold set | 70% | 80% | 90% | RAG plus reviewer corrections recover more expected synthetic obligations. |
| Release risk reduction | 1 claim | 2 claims | 4 claims | Claim-risk table rewrites more unsafe customer-facing claims. |

## How to reproduce

```bash
python scripts/run_synthetic_hero_evaluation.py
```

Output:

```text
benchmark/results/synthetic_hero_evaluation.json
```

## What improved by v1.04

The project no longer presents “18 tests passed” as the main proof. Tests still matter, but the portfolio evidence now includes:

- a deep hero case;
- before/after requirements;
- reviewer corrections;
- unsupported claim reduction;
- obligation-to-QA coverage;
- mandatory obligation-level negative test coverage;
- release risk rewriting;
- signed report manifest;
- document version hashes;
- persistent SQLite audit events.

## What this still does not prove

It does not prove:

- production regulatory correctness;
- safety across all SAF-T/e-invoicing scenarios;
- user adoption;
- legal acceptance;
- secure enterprise deployment;
- quality on confidential customer documents.

## Next evaluation step

The next credible step is a small human evaluation:

| Experiment | Design |
|---|---|
| Human baseline | Ask 2–3 PM/QA/compliance reviewers to produce obligations/QA/release wording manually. |
| Simple LLM baseline | Give the same input to a one-shot prompt. |
| Assisted workflow | Use Interpret → Discover → Communicate with reviewer mode. |
| Metrics | Time, obligation recall, unsupported claim rate, QA coverage, reviewer confidence and rework. |
| Output | A short case-study appendix with anonymised reviewer feedback. |

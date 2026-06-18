# Evaluation Methodology

The v16 evaluation layer deliberately avoids model self-scoring.

## Signal types

1. **Model output**  
   Generated obligations, requirements, release notes, risks and summaries.

2. **Rule-verified checks**  
   Deterministic checks over output structure, cited source IDs, quote presence, textual support between claims and cited chunks, modality/negation warnings and risky wording patterns.

3. **Human review**  
   Required for compliance interpretation, legal meaning, production implementation and customer-facing release communication.

## Current rule-based metrics

The Interpret module now surfaces five portfolio-facing quality metrics:

| Metric | Calculation | Interpretation |
|---|---|---|
| **Obligation precision** | Generated obligations matching the synthetic gold set / generated obligations | Higher means fewer generated obligations look unsupported by the current gold set. |
| **Obligation recall** | Gold obligations recovered by the generated output / total gold obligations | Higher means the output covers more of the expected gold obligations. |
| **Citation support rate** | Checked claims with existing source and support score above threshold / checked claims | Higher means more claims have visible textual support in the cited chunks. |
| **Unsupported claim rate** | Missing-source or very weak claims / checked claims | Lower means fewer claims appear weakly grounded. |
| **Human review rate** | Claims routed to human review / checked claims | Lower can be good, but in regulated workflows a higher rate may also show that uncertainty is being surfaced rather than hidden. |

Other supporting checks:

- **Completeness score** — expected structured sections present.
- **Rule-verified support score** — average support between generated claims and cited source chunks.
- **Quote integrity rate** — share of model-proposed quotes that are found in the cited source text.
- **Risky claim detection** — pattern-based detection of unsafe wording such as “guarantees compliance”.
- **Ambiguity warnings** — missing assumptions, open questions or review flags.

## Interpret-specific quality gates

The Interpret module now has additional guardrails:

- obligation → source → quote matrix;
- citation deep-link source inspector;
- best supporting quote per obligation;
- rule-based version diff for obligation-like statements;
- human review queue combining model-suggested and rule-detected issues;
- synthetic obligation benchmark against hand-written gold obligations.

## What these metrics are not

They are not legal validation, compliance certification or proof that an extracted obligation is correct. They are product-quality guardrails that make weak grounding visible before human review.

## Benchmarks

Run:

```bash
python scripts/run_interpret_benchmark.py
python scripts/run_interpret_obligation_benchmark.py
python scripts/run_interpret_quality_metrics.py
```

The first benchmark checks retrieval coverage. The second compares generated obligations against a hand-written synthetic gold set and reports precision/recall/F1 proxies.

## v16 update — run-specific metrics

v16 changes the Quality Metrics tab so that it no longer shows synthetic precision/recall values unless a reviewer provides a gold obligations file for the current document.

- **Calculated on every run:** citation support rate, unsupported claim rate, human review rate.
- **Calculated only with uploaded gold obligations:** obligation precision, obligation recall.

This is intentional: the application can inspect whether generated claims are textually supported by retrieved source chunks, but it cannot calculate true extraction precision/recall without a ground truth set.

See `docs/INTERPRET_METRICS.md` for formulas and validation details.


## Error taxonomy and trade-offs

v17 adds a formal error taxonomy and failure-mode analysis in `docs/ERROR_TAXONOMY_FAILURE_MODES.md`. This is used to classify unsupported claims, weak support, missing obligations, hallucinated obligations, lost conditions, unsafe customer wording, QA coverage gaps and document version drift.

# Benchmarks

v16 includes two transparent local benchmarks for the **Interpret — Compliance-to-Product Studio** module. Both are synthetic and intentionally limited, but they avoid model self-scoring and give reviewers something reproducible to inspect.

## 1. Retrieval benchmark

- Dataset: synthetic SAF-T / e-invoicing guidance text.
- Questions: 8 hand-written retrieval questions.
- Gold data: expected terms that should appear in retrieved chunks.
- Metric: retrieval hit rate.
- Mode: deterministic local embeddings; no API cost.

Run:

```bash
python scripts/run_interpret_benchmark.py
```

Output:

```text
benchmark/results/interpret_retrieval_benchmark.json
```

## 2. Obligation extraction benchmark

- Dataset: synthetic SAF-T / e-invoicing guidance text.
- Gold data: 10 hand-written expected obligations.
- Generated fixture: `benchmark/generated_sample_interpret_output.json` deliberately includes one unsupported claim and omits two expected reporting obligations so the metrics demonstrate both success and review flags.
- Metrics: obligation precision proxy, obligation recall proxy and F1 proxy.
- Method: deterministic rule-based matching between generated obligation text and the hand-written gold set.

Run:

```bash
python scripts/run_interpret_obligation_benchmark.py
python scripts/run_interpret_quality_metrics.py
```

Output:

```text
benchmark/results/interpret_obligation_benchmark.json
```

## Interpret Quality Metrics in the app

The app combines the obligation benchmark with rule-based citation checks and displays five metrics in the **Quality Metrics** tab:

- obligation precision;
- obligation recall;
- citation support rate;
- unsupported claim rate;
- human review rate.

These metrics are designed to be inspectable and honest. They are not model self-scores and they are not compliance certification. The included sample result is intentionally not perfect; it shows how unsupported claims and missing obligations are surfaced.

## What these benchmarks prove

They show that the project can run repeatable checks against a gold set and report transparent metrics without asking the model to score itself.

## What these benchmarks do not prove

They do **not** prove:

- legal correctness;
- production compliance readiness;
- full extraction accuracy on real regulations;
- human acceptance rate;
- quality across multiple industries or jurisdictions.

## Next benchmark iteration

- 25–50 questions and 25–50 gold obligations.
- Human-reviewed expected traceability matrix.
- Separate API-mode retrieval benchmark.
- Multiple public/synthetic document types.
- Reviewer column: `accepted`, `rejected`, `needs rewrite`.

## v16 update — avoiding static demo metrics

The bundled benchmark still exists for reproducible demonstration, but the app's **Quality Metrics** tab now treats precision and recall as run-specific gold-set metrics.

If no gold file is uploaded, obligation precision and recall are displayed as **N/A**. This prevents synthetic sample metrics from being interpreted as real product performance.

A template is available in the app and at `sample_inputs/interpret_gold_obligations_sample.json`.


## 3. Synthetic hero-case evaluation

v16 adds a portfolio-oriented synthetic evaluation for the deep SAF-T/e-invoicing hero case. It compares a manual baseline estimate, a simple LLM baseline and the assisted workflow.

Run:

```bash
python scripts/run_synthetic_hero_evaluation.py
```

Output:

```text
benchmark/results/synthetic_hero_evaluation.json
```

Headline metrics:

| Metric | Result |
|---|---|
| Time to first requirement set | 45 min manual → 8 min assisted |
| Unsupported claim rate | 22% simple LLM → 6% assisted after reviewer pass |
| QA coverage | 60% manual → 90% assisted obligation-to-QA coverage |
| Reviewer correction rate | 40% of generated obligations required comment/correction |
| Missing obligation recall | 90% on the synthetic gold set |
| Release risk reduction | 4 high-risk release claims rewritten |

These figures are explicitly labelled synthetic. They demonstrate measurement design and product-thinking maturity; they are not production performance claims.

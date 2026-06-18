# Citation Verifier Error Analysis

This document publishes the expected failure modes of the rule-based citation verifier. It is intentionally candid: the verifier is a product-quality guardrail, not a legal entailment model.

## Heuristic components

`support_components()` currently uses:

| Component | Purpose | Risk |
|---|---|---|
| Token containment | Checks whether claim terms appear in the source | Can over-reward keyword overlap even when meaning differs |
| Jaccard overlap | Rewards shared vocabulary | Can punish long source excerpts with extra context |
| Character n-grams | Catches phrase-level similarity | Can miss valid paraphrases |
| Sequence ratio | Catches close wording | Can be noisy on long excerpts |
| Modal alignment | Checks obligation terms such as must/required/block | Can under-score claims where obligation is implied |
| Number penalty | Penalizes missing numeric values | Can penalize if number is written in words |
| Negation penalty | Flags must/must-not style contradictions | Can over-flag if source contains an exception or optionality context |

## Published failure cases

| Failure mode | Example | Why it matters | Mitigation |
|---|---|---|---|
| False positive from keyword overlap | “QR reference may be combined with regular IBAN” against a source saying it must not be combined | Same keywords, opposite meaning | Negation/modality penalty and human review |
| False negative from paraphrase | A valid paraphrase uses different terms from the source | Low overlap despite support | Route weak scores to reviewer rather than reject automatically |
| Numeric mismatch false alarm | Source says “twenty-five” while claim says “25” | Number extractor may not normalize words | Treat as review warning, not automatic failure |
| Scope mismatch | “all invoices” vs “customer invoices with QR reference” | Text overlap may hide condition loss | Reviewer must check lost conditions |
| Modal mismatch | “should validate” vs “must block” | The claim strengthens the source | Modal alignment and status warning |
| Negation context error | Source uses “not” in an exception but claim is valid | Negation detector may over-warn | Keep status as “needs human review” instead of final verdict |
| Long-source dilution | Relevant sentence is inside a long chunk | Jaccard can fall because of extra terms | Use sentence-level best quote search |
| Unsafe compliance claim | “guarantees full compliance” | The source may mention compliance but not guarantee it | Claim hygiene scanner and release-note safer rewrite |

## Component-level checks to monitor

When human labels are available, inspect:

- high support score + human unsupported = likely false positive;
- low support score + human supported = likely false negative;
- `negation_mismatch = true` rows marked supported by humans;
- rows with missing numbers where humans still mark supported;
- rows with high containment but low modal alignment.

## Product decision

The verifier should not be used as a hidden quality score. It should be used as a visible triage mechanism:

- strong support: likely safe to review quickly;
- partial/weak support: reviewer should inspect evidence;
- unsupported/negation mismatch: block or route to human review.

The correct product claim is:

> The verifier makes grounding risk visible before review.

The incorrect claim would be:

> The verifier proves legal correctness.

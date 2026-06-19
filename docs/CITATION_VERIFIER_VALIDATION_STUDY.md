# Citation Verifier Validation Study

v1.04 adds a validation pack for the rule-based citation verifier. This is deliberately framed as a validation workflow, not as completed human evidence.

## Why this exists

The `support_components()` score is a heuristic. It combines token containment, Jaccard overlap, character n-grams, sequence similarity, modal-term alignment and penalties for missing numbers or negation mismatch.

That is better than only checking whether a citation ID exists, but it still needs validation against human judgment.

## Research question

Does the heuristic support score correlate with human judgment about whether a claim is supported by the cited source text?

## Proposed method

| Step | Detail |
|---|---|
| Claim set | 30 claims across SAF-T PT and Swiss QR-Bill |
| Reviewers | 2–3 human reviewers |
| Human labels | Supported / Weak / Unsupported |
| Comparator | Heuristic label derived from support score |
| Reported metric | Simple agreement rate and false positive/false negative list |
| Scope | Portfolio validation, not legal/compliance certification |

## Files

- `validation/citation_claims_sample.csv` — 30 claims with source excerpts, author expected labels and heuristic scores.
- `validation/human_review_template.csv` — blank reviewer template.
- `scripts/analyze_citation_validation.py` — computes agreement after human labels are added.
- `validation/citation_validation_results.json` — generated result file.

## Current status

Human review has not yet been collected inside this repository. The current generated result therefore reports:

- 30 claims total;
- 0 claims with human labels;
- 30 claims pending human labels;
- no agreement rate yet.

That is intentional. The project must not pretend that author-created labels are external human validation.

## How to complete the validation

1. Send `validation/human_review_template.csv` to 2–3 reviewers.
2. Ask each reviewer to label each row as `Supported`, `Weak` or `Unsupported`.
3. Copy their labels into `human_reviewer_1`, `human_reviewer_2` and `human_reviewer_3` in `validation/citation_claims_sample.csv`, or fill `majority_human_label` directly.
4. Run:

```bash
python scripts/analyze_citation_validation.py
```

5. Review:

```text
validation/citation_validation_results.json
```

## What would make the verifier more credible

The verifier becomes more credible if:

- human agreement is high on clearly supported/unsupported claims;
- false positives are rare for risky compliance claims;
- weak claims are routed to human review rather than treated as strong support;
- errors are documented rather than hidden.

## What would invalidate the verifier

The verifier should be revisited if:

- reviewers mark many high-score claims as unsupported;
- negation or numeric mismatch warnings create many false alarms;
- paraphrased but valid claims are repeatedly scored as unsupported;
- the heuristic only works on the SAF-T hero case and fails on Swiss QR-Bill.

# Swiss QR-Bill second-domain case

This is a small second-domain validation case added in v24 to reduce overfitting to the SAF-T PT / e-invoicing hero case.

It is intentionally narrower than the SAF-T hero case. Its purpose is not to create a second full product module; it is to test whether the same Interpret workflow can handle a different compliance-heavy invoice/payment domain.

## Why this domain

Swiss QR-Bill is useful as a second domain because it is still enterprise/invoice/compliance adjacent, but it has different failure modes from SAF-T:

- reference/account combinations matter;
- machine-readable QR payload and human-readable payment part must stay aligned;
- structured address validation can block export;
- unsafe communication claims such as “guarantees acceptance” must be avoided.

## Scope

Included:

- synthetic source brief;
- hand-written gold obligations;
- local benchmark output;
- citation-validation examples;
- error-analysis examples.

Not included:

- production QR-bill generation;
- bank validation;
- live payment processing;
- legal/compliance certification;
- replacement for official Swiss QR-bill implementation guidelines.

## Files

- `sample_inputs/swiss_qr_bill_sample.txt`
- `sample_inputs/swiss_qr_bill_gold_obligations.json`
- `scripts/run_swiss_qr_bill_benchmark.py`
- `benchmark/results/second_domain_swiss_qr_bill_benchmark.json`

## Expected learning

The project should now demonstrate one strong hero workflow and one small generalization check:

| Case | Role |
|---|---|
| SAF-T PT / e-invoicing | Deep hero workflow |
| Swiss QR-Bill | Second-domain generalization check |

This is a deliberate scope choice. v24 does not add another broad module; it adds a compact validation case.

# Swiss QR-Bill Generalization Case

This is a **second-domain portfolio fixture**, not a legal/compliance opinion. Its purpose is to show that the Interpret workflow is not only tuned to the SAF-T PT / e-invoicing hero case.

## Why this domain

Swiss QR-Bill is a useful generalization case because it is still enterprise/compliance-adjacent, but it is not Portuguese SAF-T. It tests whether the system can handle payment-format obligations, reference-type constraints, layout/processing risks and invoice/payment handoff rules.

## Public source basis

The sample is based on public Swiss QR-Bill guidance from SIX and the Swiss QR-Bill implementation-guideline concepts available at the time of this portfolio update. Production work must verify the latest official version before implementation.

Useful source anchors for human reviewers:

- SIX QR-bill overview: payment section + receipt, Swiss QR Code, plain-text payment information and validation portal.
- SIX Implementation Guidelines QR-bill v2.4: QR-IBAN, QR reference, Creditor Reference, structured address and layout/printing constraints.

## Portfolio artefacts

- `sample_inputs/swiss_qr_bill_generalization_sample.txt`
- `benchmark/swiss_qr_bill_gold_obligations.json`
- `benchmark/generated_sample_swiss_qr_bill_output.json`
- `benchmark/results/swiss_qr_bill_obligation_benchmark.json`

## What this proves — and does not prove

It shows:

- the same obligation-extraction benchmark structure works for a second domain;
- the workflow can represent Swiss QR-Bill obligations, validation rules and negative QA cases;
- the portfolio can discuss generalization without adding another large UI module.

It does **not** prove:

- production Swiss QR-Bill compliance;
- legal correctness;
- that the heuristic generalizes to all domains;
- that the generated sample was evaluated by external users.

## Example obligation chain

```text
Swiss QR-Bill source text
→ QR reference / QR-IBAN obligation
→ validation rule: block QR reference with standard IBAN
→ negative QA: reject wrong reference/account combination
→ release gate: blocked if negative test is missing
→ audit report: source support + reviewer decision
```

## Scope discipline note

This second domain was intentionally added as **sample data + benchmark + documentation**, not as another full app module. That keeps the portfolio focused while answering the academic/PM critique that one SAF-T-only case could look over-curated.

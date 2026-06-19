# Mandatory Negative Test Coverage Policy

## Why this exists

Compliance-heavy product workflows fail when teams only validate the happy path. In the SAF-T/e-invoicing hero case, a feature can look release-ready because the PRD, Jira ticket and acceptance criteria exist, while still missing tests for invalid, missing or exception data.

v1.03 makes negative test coverage an explicit release gate.

## Policy

Every source obligation that enters product/Jira/QA handoff must have at least one mapped negative, edge or failure test before the feature can be marked release-ready.

A generic QA matrix is not enough. The test must be mapped back to the obligation ID, for example `O1`, `O2`, or `O4`.

## What counts as a negative test

A negative test proves that the system rejects, blocks, flags, escalates or safely handles invalid or incomplete input.

Examples:

| Obligation | Positive test | Required negative test |
|---|---|---|
| O1 — CustomerTaxID must be present | Valid invoice exports successfully | Invoice without CustomerTaxID is blocked before export |
| O2 — Totals must be consistent | Invoice with correct total passes | Invoice with inconsistent total is rejected or flagged |
| O3 — Evidence must be retained | Validation evidence is saved | Report cannot be finalized if evidence metadata is missing |
| O4 — Failed records must show reasons | Report lists valid failure details | Report flags any failed record with blank reason |

## What does not count

These do not satisfy mandatory negative coverage:

- a happy-path test only;
- an acceptance criterion without a failure condition;
- a negative test that is not mapped to an obligation;
- a generic statement such as “test error handling”;
- a screenshot or manual note without owner/evidence.

## Release gate

The rule-based gate returns:

- `Pass` when every mapped obligation has at least one negative test;
- `Blocked` when one or more obligations lack negative coverage;
- `Needs obligation mapping` when there are QA tests but no obligation IDs to validate against.

The app records these metrics as real usage telemetry:

- `negative_test_coverage_rate`;
- `negative_tests_total`;
- `obligations_with_negative_test`;
- `missing_negative_tests_total`.

## Trade-off

This rule intentionally increases friction before release. That is the point. In regulated workflows, speed without failure-case coverage creates false confidence. The intended compromise is:

- happy-path tests remain useful for functional validation;
- negative tests become mandatory for release-readiness;
- unmapped negative tests are still shown, but they do not satisfy the gate;
- human QA/Compliance reviewers can override only by recording an explicit decision and evidence.

## Portfolio skill demonstrated

This addition demonstrates that the project is not only generating PRDs or QA rows. It applies a deterministic product-quality rule that blocks release-readiness when compliance obligations do not have failure-case evidence.

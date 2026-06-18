# Claim Hygiene Story: From Self-Scoring to Scanner

An earlier version of this portfolio used self-scoring language such as app-internal “9.x/10” ratings. That was a weak signal: it looked like validation, but it was actually self-assessment.

The correction was not just to delete the text. The correction was to build a guardrail that prevents the same failure mode from returning.

## What changed

- Removed app-internal self-score claims.
- Reframed portfolio metrics as portfolio/demo signals unless explicitly marked as real local usage metrics.
- Added `services/claim_hygiene_service.py`.
- Added a Claim Hygiene Audit page.
- Added tests that fail on unframed overclaims.

## What the scanner looks for

- unsupported compliance guarantees;
- unqualified claims that a portfolio prototype is ready for production use;
- unverifiable model/pricing claims;
- unframed synthetic metrics;
- interview/hiring guarantees;
- inflated score-style claims that could be mistaken for external validation.

## Why this is central to the portfolio

The story is not “the project never made a bad claim.”

The story is: **a bad claim pattern was found, corrected, and turned into an automated regression guardrail.**

That is the product judgment being demonstrated: responsible AI product work is not only about generating better outputs; it is about preventing misleading outputs from becoming product claims.

## Interview framing

> I received a skeptical critique that the app was self-scoring. I agreed with it, removed the inflated framing, and built a claim-hygiene scanner so future versions would fail tests if they reintroduced unsupported compliance, production-readiness or hiring-outcome claims.

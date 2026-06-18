# From Auto-Score to Claim Hygiene Scanner

This is one of the most important product lessons in the portfolio.

An earlier version of the project used portfolio-style self-scores such as “9.x/10”. A skeptical reviewer correctly pointed out that these scores could look like validation when they were really self-assessment.

The fix was not just to remove the scores. The fix was to build a prevention mechanism.

## What changed

| Before | After |
|---|---|
| Portfolio pages could contain self-scoring language | Static scores removed or reframed as bounded portfolio signals |
| Risky claims were caught by manual review | `claim_hygiene_service.py` scans for risky patterns |
| Synthetic metrics could be misread as production proof | Synthetic, local usage and portfolio signal types are separated |
| Compliance wording could overclaim | Scanner flags compliance guarantees and production-readiness ambiguity |
| Hiring impact could be overstated | Wording is bounded: can improve signal, cannot guarantee interviews |

## Why this matters

Responsible AI product work is not only about generating better outputs. It is about preventing misleading outputs from becoming product claims.

The claim hygiene scanner demonstrates that feedback was converted into a guardrail:

```bash
python - <<'PY'
from services.claim_hygiene_service import audit_portfolio_claims
print(audit_portfolio_claims('.')['summary'])
PY
```

## Correct positioning

Use this wording:

> The project demonstrates claim hygiene: when an overclaim risk was identified, I removed the risky pattern and added an automated scan to prevent regression.

Avoid this wording:

> The project proves all claims are correct.

The scanner is a conservative portfolio review tool, not legal, brand or factual certification.

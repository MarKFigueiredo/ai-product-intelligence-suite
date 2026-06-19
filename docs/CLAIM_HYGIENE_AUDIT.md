# Claim Hygiene Audit — v1.04

This project is intended to increase hiring signal, not to claim commercial traction, production SaaS readiness, legal compliance guarantees or endorsement from any university/company.

## What was reviewed

The v1.04 audit focuses on claims that a skeptical reviewer could reasonably challenge:

| Claim category | Risk | v1.04 mitigation |
|---|---|---|
| Model names/pricing | Hard-coded or invented model names/prices can look unreliable. | Removed fictitious `gpt-5.4`/`gpt-5.5` options and moved cost estimates to optional local env pricing. |
| Synthetic metrics | Precise numbers can look like production evidence. | Synthetic metrics remain labelled as synthetic portfolio benchmarks. |
| Real usage metrics | Local telemetry can be mistaken for production analytics. | UI and docs state that usage metrics are real local evidence, not production analytics. |
| Connectors | Mock/API-shaped payloads can be mistaken for full integrations. | Connector outbox is labelled real local; live mode is optional and credential-gated. |
| Enterprise readiness | Local controls can be mistaken for SSO/RBAC/tenancy. | Real vs simulated table explicitly separates local controls from production roadmap gaps. |
| Hiring outcomes | Portfolio quality can help conversion but cannot guarantee interviews. | v1.04 uses bounded wording: may improve interview conversion when targeted and packaged well. |
| Compliance/legal | Product validation cannot guarantee legal compliance. | Release wording and docs use safer language: supports validation/review, not legal guarantees. |

## Current scan result

The conservative local claim-hygiene scanner reports:

```text
Pass: no unframed high/medium claim risks found by the v1.04 scan.
```

The scanner is not a legal review. It is a portfolio hygiene tool to catch obvious overclaims before publishing.

## Safe answer to “will this increase interviews?”

A safe answer is:

> This can improve interview conversion because it gives hiring managers concrete evidence of AI PM/product judgment, but it does not guarantee interviews. The impact depends on role targeting, CV clarity, outreach quality, network, timing and market conditions.

## Recommended publishing checklist

- Keep the first README line: “portfolio case study, not a commercial product.”
- Do not claim production SaaS readiness.
- Do not claim legal/compliance accuracy.
- Do not claim university/company endorsement.
- Label synthetic benchmarks and local usage metrics separately.
- Use the guided demo and 90-second walkthrough as the first review path.

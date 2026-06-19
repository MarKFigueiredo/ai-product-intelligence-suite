# Core Pipeline Architecture — v1.04

v1.04 reduces implementation risk by moving the product thesis out of Streamlit-only pages and into a small, testable core pipeline.

## Why this matters

Earlier versions had strong product logic, but too much orchestration lived near UI code. That made the app harder to reason about for an Engineering Lead or Staff PM reviewer.

The v1.04 target is simple:

```text
UI pages collect inputs and display results.
Services own domain-specific logic.
core/pipeline.py orchestrates Interpret → Review → Discover.
```

## Declarative pipeline

`core/pipeline.py` defines the workflow as explicit steps:

```text
1. Extract obligations
2. Verify citation support
3. Apply human feedback
4. Map to requirements
5. Evaluate QA coverage
6. Calculate release readiness
7. Persist learning signals
```

This is not a new product module. It is a refactor that makes the existing workflow visible, testable and easier to review.

## What stayed out of scope

The pipeline does not introduce production orchestration, background jobs, workflow queues, SSO, tenant routing, or distributed tracing. Those would be production concerns. The portfolio goal is to demonstrate structure and judgment, not to simulate a full SaaS backend.

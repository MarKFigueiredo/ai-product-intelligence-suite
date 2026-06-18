# Release 1.04 — Streamlit UI compatibility fix

This patch fixes two publish-readiness issues found during local Ubuntu testing:

- KPI cards in the Guided Demo no longer render raw HTML text in newer Streamlit versions.
- Deprecated `use_container_width=True` calls were replaced with `width="stretch"` to reduce terminal warning noise during local runs and deployment.

No product features were removed. This is a visual/runtime compatibility patch for the public app.

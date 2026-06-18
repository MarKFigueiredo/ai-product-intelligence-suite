# Release 1.04 — Native UI Patch for Public Deployment

This patch fixes a public-deployment UX issue found during local Ubuntu/VS Code testing.

## Fixed

- Replaced the custom HTML KPI grid with native Streamlit containers.
- Replaced the custom HTML vertical timeline with native Streamlit containers.
- Prevents raw `<div>` blocks from appearing in the Guided Demo tabs on some Streamlit versions.
- Keeps the app focused on public portfolio review rather than custom frontend complexity.

## Why this matters

For a portfolio app, reliability and clarity are more important than decorative custom HTML. This patch favors native Streamlit components so the public app renders consistently on local Ubuntu and Streamlit Community Cloud.

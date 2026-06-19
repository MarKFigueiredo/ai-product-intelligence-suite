# Staleness and Lineage Policy

## Purpose

In regulated enterprise workflows, a requirement, QA case or release note can become unsafe if the upstream source or reviewer decision changes after it was generated. v1.04 makes this explicit through lineage and staleness checks.

## Artefact chain

```text
source document
→ obligation
→ reviewer decision
→ requirement
→ Jira ticket
→ QA case
→ release note
→ audit report
```

## Staleness rule

An artefact is stale when a direct upstream artefact has a later `updated_at` timestamp than the artefact itself.

Example:

```text
O-SAF-T-002 updated at 09:21
REQ-SAF-T-001 updated at 09:18
→ REQ-SAF-T-001 is stale
```

## Required product behavior

When an artefact becomes stale, the app should show:

- stale artefact ID;
- upstream artefact that caused staleness;
- reason;
- recommended action;
- impacted downstream artefacts.

## Release readiness impact

A stale requirement, Jira ticket, QA case, release note or audit report should prevent a clean “release-ready” state until it is reviewed or regenerated.

## Portfolio signal

This demonstrates that AI-generated artefacts are not static outputs. They are part of a living workflow where upstream changes must propagate through downstream product, QA, support and compliance artefacts.

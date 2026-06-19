# Approval Workflow State Machine

This project is a portfolio case study, not production workflow software. v1.03 adds a concrete local approval state machine so reviewers can see how AI-generated artefacts move through Product, QA, Compliance, Support and Engineering review.

## States

`Draft → AI-generated → PM reviewed → QA reviewed → Compliance reviewed → Approved → Exported`

`Blocked` can be used when an artefact has unsupported evidence, missing negative test coverage, unsafe communication, stale lineage, or an invalid role transition.

## Why this matters for hiring

Enterprise AI product work is not just generation. It needs clear ownership, review states, role boundaries, rejection paths and audit-friendly history. This service demonstrates the product behavior locally without claiming SSO/RBAC is implemented.

## What is real locally

- state transition rules;
- role-to-state permissions;
- transition history;
- signed transition events;
- data event persisted to the usage metrics store when a UI transition is simulated.

## What would be needed in production

- SSO-backed identity;
- real RBAC/ABAC enforcement;
- workflow engine or durable state store;
- immutable audit logging;
- notification and escalation policies;
- admin review UI.

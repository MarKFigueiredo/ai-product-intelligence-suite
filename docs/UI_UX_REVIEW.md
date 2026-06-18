# UI/UX Review — v20 Guided Portfolio Experience

## Current UX problem

The project contains strong product thinking, metrics, enterprise controls and documentation, but a reviewer can still get lost if they open the repository without guidance. The v20 goal is to make the value legible in the first two minutes while preserving depth for Principal PM, QA, Compliance and Engineering reviewers.

## Target UX

The app should feel like a guided case study, not a collection of disconnected tools.

Primary journey:

```text
Open app
→ Guided Demo — Portfolio Review
→ choose reviewer persona
→ walk through SAF-T/e-invoicing hero workflow
→ inspect release gates
→ open evidence drawer
→ inspect lineage/staleness
→ compare usage runs
→ export evidence/report/handoff payloads
```

## Design principles

1. **One hero workflow before many modules** — SAF-T/e-invoicing is the narrative spine.
2. **Progressive disclosure** — show status first; expose evidence/details only when needed.
3. **Persona-based navigation** — recruiter, hiring manager, Principal PM, QA, Compliance and Engineering leads should have clear entry points.
4. **Evidence over claims** — every important artefact should show source, hash, reviewer state and downstream links.
5. **Failure visibility** — show where the system can fail: unsupported claims, missing negative tests, stale artefacts.
6. **Real vs simulated transparency** — make local/real controls and production gaps explicit.
7. **Actionable gates** — release readiness should explain what is blocked, why and what to do next.

## Key user journeys

### Recruiter

Needs a fast answer: “What does this project prove about Marco?”

Path:

```text
Guided Demo → Persona paths → What this proves → Portfolio Review Guide
```

### Hiring Manager

Needs to evaluate AI PM/product judgment.

Path:

```text
Guided Demo → Hero workflow → Release gates → Product Strategy → Metrics
```

### Principal PM

Needs to assess systems thinking and sequencing.

Path:

```text
Guided Demo → Lineage & staleness → Run comparison → Trade-offs → Product strategy
```

### QA Lead

Needs to verify requirements are testable and include failure paths.

Path:

```text
Release Gate Dashboard → Negative test coverage → QA cases → Staleness
```

### Compliance Reviewer

Needs to know what is supported, weak, missing, reviewed and auditable.

Path:

```text
Evidence Drawer → Reviewer corrections → Audit report → Real vs simulated
```

### Engineering Lead

Needs to understand what is real locally and what is production roadmap.

Path:

```text
Real vs simulated → Connector Handoff Center → Usage Metrics & Data → Architecture
```

## v20 UX additions

- Guided Portfolio Demo page.
- Persona-based review paths.
- 10-step hero workflow.
- Release Gate Dashboard.
- Evidence Drawer.
- Lineage & Staleness view.
- Run comparison view.
- What this demonstrates page inside the app.
- Real vs simulated capability table.
- Connector Handoff Center.
- Real Usage Evidence Report page.

## Future improvements

- Full visual graph rendering for lineage.
- Side-by-side before/after artefact diffing.
- Reviewer state machine UI by artefact.
- Comment threads attached to obligation/requirement/QA artefacts.
- More visual screenshots for the README and portfolio page.

## v22 polish update

v22 improves the review experience by reducing visual density and making the hierarchy explicit:

- high-level status appears before raw tables;
- hero workflow steps are displayed as compact cards;
- lineage events are shown in a vertical visual timeline;
- evidence remains available through drawers/expanders;
- the landing page avoids aggressive target claims and labels portfolio/demo signals clearly;
- a new Claim Hygiene Audit page helps catch overclaims before publishing.

# UI/UX Polish — v22

v22 focuses on making the portfolio easier to review quickly. The goal is not to add more surface area; it is to make the existing product judgment easier to understand.

## Problems addressed

| Problem | v22 change | Why it matters for hiring review |
|---|---|---|
| Visual density | Added compact KPI cards, persona cards and step cards. | Reviewers see the story before opening detailed tables. |
| Weak hierarchy | Added page intros, badges, callouts and consistent status language. | The most important decision/status is visible first. |
| Table-heavy timeline | Added a vertical visual timeline component. | Makes lineage and staleness easier to understand at a glance. |
| Hard-to-scan evidence | Kept evidence in drawers/expanders and added concise source/reviewer/link metadata. | Shows depth without overwhelming the main flow. |
| Overclaim risk | Added Claim Hygiene Audit page and documentation. | Makes synthetic/local/optional/non-production boundaries explicit. |

## Design principles

1. **Decision first, evidence second** — show status and why it matters before raw tables.
2. **One hero workflow** — use SAF-T/e-invoicing as the coherent story.
3. **Progressive disclosure** — default view is concise; evidence, lineage and tables are available on demand.
4. **Persona-based navigation** — recruiters, HMs, Principal PMs, QA, Compliance and Engineering should know where to look.
5. **Claim hygiene by design** — real local, simulated, optional and roadmap capabilities must be visibly separated.

## New visual elements

- `render_page_intro()` for consistent page framing.
- `render_kpi_grid()` for fast status scanning.
- `render_vertical_timeline()` for graphical event sequencing.
- `render_status_badge()` for consistent status language.
- `render_callout()` for important review notes and caveats.

## What still needs human polish

- Replace SVG placeholders with actual screenshots from a live run.
- Record a 90-second walkthrough video.
- Run one external usability review with a PM/QA/Compliance reviewer.
- Reduce remaining long markdown pages into optional deep-dive appendices.

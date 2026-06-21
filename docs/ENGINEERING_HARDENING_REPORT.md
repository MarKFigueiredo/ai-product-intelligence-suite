# Engineering Hardening Report

This report is generated from tracked repository files only. It excludes `.venv`, local caches and untracked scratch files.

## Summary

- Python files over 400 lines: 3
- Markdown files over 220 lines: 1
- Functions over 80 lines: 14
- Files using Streamlit: 35
- Tone findings: 8
- Suspicious filenames: 0

## Largest Python files

| File | Lines |
|---|---:|
| `modules/compliance_studio.py` | 647 |
| `services/usage_metrics_service.py` | 551 |
| `services/citation_verifier.py` | 508 |

## Largest Markdown files

| File | Lines |
|---|---:|
| `docs/SYSTEM_OVERVIEW.md` | 234 |

## Large functions

| File | Function | Lines | Location |
|---|---|---:|---|
| `ui/guided_demo_page.py` | `render_guided_demo_page` | 175 | L48-L222 |
| `services/interpret_metrics_service.py` | `calculate_interpret_quality_metrics` | 168 | L174-L341 |
| `ui/compliance_review_history_panel.py` | `render_reviewer_and_run_history_panel` | 165 | L37-L201 |
| `services/compliance_demo_output.py` | `build_demo_output` | 149 | L12-L160 |
| `ui/enterprise_page.py` | `render_enterprise_readiness_page` | 145 | L29-L173 |
| `ui/about_page.py` | `render_about_me` | 127 | L9-L135 |
| `services/portfolio_demo_service.py` | `hero_output_shape` | 112 | L137-L248 |
| `modules/compliance_studio.py` | `render` | 109 | L539-L647 |
| `modules/compliance_studio.py` | `render_compliance_dashboard` | 106 | L144-L249 |
| `services/usage_metrics_service.py` | `derive_metrics` | 99 | L154-L252 |
| `ui/limitations_page.py` | `render_limitations_page` | 99 | L21-L119 |
| `ui/portfolio_page.py` | `render_landing_page` | 87 | L16-L102 |
| `scripts/engineering_audit.py` | `render_markdown` | 86 | L170-L255 |
| `services/interpret_benchmark_service.py` | `compare_generated_to_gold` | 85 | L51-L135 |

## Streamlit usage

| File | `st.` count | Current status |
|---|---:|---|
| `modules/compliance_studio.py` | 136 | allowed UI surface |
| `ui/guided_demo_page.py` | 57 | allowed UI surface |
| `ui/visual_components.py` | 46 | allowed UI surface |
| `modules/product_discovery.py` | 36 | review for UI leakage |
| `modules/decision_timeline.py` | 32 | review for UI leakage |
| `ui/compliance_review_history_panel.py` | 32 | allowed UI surface |
| `modules/release_readiness.py` | 30 | review for UI leakage |
| `ui/enterprise_page.py` | 30 | allowed UI surface |
| `ui/metrics_page.py` | 25 | allowed UI surface |
| `ui/sidebar.py` | 20 | allowed UI surface |
| `ui/about_page.py` | 19 | allowed UI surface |
| `ui/limitations_page.py` | 19 | allowed UI surface |
| `ui/document_versions_page.py` | 16 | allowed UI surface |
| `ui/connector_handoff_page.py` | 15 | allowed UI surface |
| `ui/lineage_page.py` | 15 | allowed UI surface |
| `ui/evaluation_panel.py` | 14 | allowed UI surface |
| `ui/portfolio_page.py` | 14 | allowed UI surface |
| `ui/approval_workflow_page.py` | 11 | allowed UI surface |
| `ui/claim_hygiene_page.py` | 10 | allowed UI surface |
| `ui/evidence_report_page.py` | 10 | allowed UI surface |
| `ui/quality_learning_page.py` | 9 | allowed UI surface |
| `ui/result_panel.py` | 6 | allowed UI surface |
| `ui/openai_error_handler.py` | 5 | allowed UI surface |
| `app.py` | 3 | allowed UI surface |
| `tests/test_native_ui_patch.py` | 2 | review for UI leakage |
| `scripts/engineering_audit.py` | 1 | review for UI leakage |
| `scripts/extract_compliance_demo_output.py` | 1 | review for UI leakage |
| `tests/test_compliance_assessment_service.py` | 1 | review for UI leakage |
| `tests/test_compliance_demo_output_extraction.py` | 1 | review for UI leakage |
| `tests/test_compliance_models.py` | 1 | review for UI leakage |
| `tests/test_compliance_review_history_panel_extraction.py` | 1 | review for UI leakage |
| `tests/test_core_pipeline_feedback_ux.py` | 1 | review for UI leakage |
| `tests/test_download_button_keys.py` | 1 | review for UI leakage |
| `tests/test_openai_service_boundaries.py` | 1 | review for UI leakage |
| `ui/streamlit_secrets.py` | 1 | allowed UI surface |

## Tone findings

| File | Line | Text |
|---|---:|---|
| `HERO_CASE_STUDY.md` | 14 | A top-tier portfolio cannot rely only on generic AI outputs. It needs one workflow that proves product judgment: |
| `PORTFOLIO_SCOPE_DISCIPLINE.md` | 36 | The intended signal is not “I built everything.” |
| `WHAT_THIS_DEMONSTRATES.md` | 17 | \| AI product judgment \| RAG, citation support, reviewer mode, supported/weak/missing reports \| Shows I design AI with controls, not just generation. \| |
| `WHAT_THIS_DEMONSTRATES.md` | 38 | > “This project demonstrates how I design AI product workflows that turn ambiguous compliance inputs into auditable product decisions.” |
| `docs/CONNECTOR_HANDOFF_CENTER.md` | 27 | The product signal is not “I built perfect connectors.” It is: |
| `docs/DEMO_SCRIPT.md` | 13 | “This is a portfolio case study, not a commercial product. It demonstrates how I design AI product workflows for regulated enterprise software.” |
| `docs/reviewer/DEMO_WALKTHROUGH.md` | 8 | This project is a portfolio case study, not a commercial product. The demo should show how I design AI product workflows for regulated enterprise software. |
| `docs/reviewer/DEMO_WALKTHROUGH.md` | 29 | I built a portfolio-grade AI product case study for regulated enterprise software. It turns a SAF-T/e-invoicing source excerpt into obligations, reviewer corrections, product requirements, Jira-shaped tickets, QA cases with mandatory negative coverage, safer release communication, incident learning and an audit-ready report. The project also persists real usage metrics locally, supports import/export, creates connector handoff payloads and clearly separates real local controls from simulated production controls. |

## Suspicious filenames

No suspicious filenames found by the strict scanner.

## Recommended next refactor

1. Split `modules/compliance_studio.py` into a Streamlit page wrapper and pure services.
2. Keep `ui/` and `app.py` as presentation surfaces only.
3. Add domain dataclasses for obligations, evidence, QA cases, release-risk findings and audit summaries.
4. Convert selected service outputs from loosely-shaped dictionaries to typed objects.
5. Add behavior tests for gates: missing source, unsupported claim, missing negative QA and stale evidence.


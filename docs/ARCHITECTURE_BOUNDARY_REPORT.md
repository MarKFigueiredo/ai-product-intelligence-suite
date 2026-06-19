# Architecture Boundary Report

This report checks tracked Python files for UI-layer leakage.

## Boundary policy

- `core/` must not import or reference Streamlit.
- New `services/` files must not import or reference Streamlit.
- `app.py`, `ui/` and `modules/` are the current presentation surfaces.
- Existing service UI references are tracked as known debt until removed in later sprints.

## Summary

- Violations: 0
- Known service UI debt files: 0

## Violations

No architecture boundary violations found.

## Known service UI debt

No known service UI debt found.

## Recommended next refactor order

1. Remove Streamlit references from `services/evidence_report_service.py`.
2. Remove Streamlit references from `services/citation_verifier.py`.
3. Remove Streamlit references from `services/usage_metrics_service.py`.
4. Then split `modules/compliance_studio.py` into smaller UI wrappers and pure services.


# Real Usage Evidence Report

This report is generated from the local SQLite usage metrics store. It is portfolio evidence, not production analytics.

Run the following command to regenerate it from current local usage data:

```bash
python scripts/generate_real_usage_evidence_report.py
```

If the app has not been used yet, the report will show zero workflow runs. That is expected. The important v1.04 capability is that usage runs, metric snapshots, connector events, imports and exports can now be accumulated and exported over time.

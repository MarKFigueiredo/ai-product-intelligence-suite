# Document Versioning and Impact

v21 adds local document versioning and impact analysis helpers. The goal is to show how a changed compliance source should propagate through obligations, requirements, QA, release communication and audit evidence.

## Local behavior

- Create a document version record with a hash, byte count, version and importer.
- Compare previous and current obligation sets.
- Classify obligations as added, removed or changed.
- Identify downstream artefacts affected by changed obligations.
- Persist document import events in the usage metrics database.

## Why this matters

Compliance-heavy product teams often work with changing source material. A strong AI PM workflow must avoid stale artefacts. If an obligation changes, downstream requirements, tickets, QA cases and release notes may need review/regeneration.

## Production gaps

This is local portfolio logic. Production implementation would require durable document storage, version permissions, retention policy, encryption, tenant isolation and legal hold support.

# Hero Case — SAF-T PT / E-invoicing Compliance-to-Product Workflow

> **Important scope note:** this is a realistic synthetic product case based on common SAF-T/e-invoicing product workflows. It is not official tax/legal guidance and must not be used as compliance advice. The purpose is to show how the product turns source material into traceable product work, review decisions, safer communication and audit evidence.

## 1. The problem

Enterprise accounting/logistics software teams often receive compliance guidance as dense regulatory, tax authority, support or internal implementation notes. The hard product problem is not only extracting rules. It is preserving traceability across the full delivery chain:

```text
source text → obligation → requirement → Jira story → QA test → release note → audit report → incident learning
```

Without that chain, teams can ship incomplete validation, overclaim compliance in release notes, or fail to reconstruct why a requirement was implemented months later.

## 2. Synthetic input document excerpt

```text
For Portuguese SAF-T invoice exports, the application must validate that each exported sales invoice contains a customer tax identification number, invoice date, tax code, invoice total and customer account reference where applicable.

When the product is configured for accounting or integrated accounting with billing, exported invoice records must be traceable to the originating accounting journal transaction. The exported transaction reference must preserve the journal identifier, transaction date and archival/document number used by the accounting subsystem.

Records with missing customer tax identifiers, invalid tax codes, inconsistent invoice totals or missing accounting traceability for applicable configurations must be flagged before export. Critical validation failures must prevent final export until corrected or explicitly reviewed by an authorised compliance reviewer.

The export validation report must show every failed invoice record, the failed field, severity, reason, owner and correction status. The system must maintain validation evidence, reviewer decisions, document version hash and export/report timestamp so Product, QA and Compliance can reconstruct what was checked and why.

Customer-facing release communication must not state that the product guarantees legal compliance. Safer wording should explain that the feature helps users identify incomplete or inconsistent records before export and that final compliance review remains the customer's responsibility.
```

## 3. Extracted obligations

| ID | Extracted obligation | Source support | Product interpretation | Review status |
|---|---|---|---|---|
| O-SAF-T-001 | Validate customer tax ID, invoice date, tax code, invoice total and AccountID where applicable before export. | Directly supported by paragraph 1. | Build pre-export invoice field validation. | Correct |
| O-SAF-T-002 | For accounting/integrated modes, preserve accounting journal traceability from invoice to transaction. | Supported by paragraph 2. | Add transaction reference mapping for applicable configurations. | Needs review |
| O-SAF-T-003 | Flag missing tax ID, invalid tax code, inconsistent totals and missing accounting traceability before export. | Supported by paragraph 3. | Add blocking/warning validation outcomes by severity. | Correct |
| O-SAF-T-004 | Critical validation failures must prevent final export unless corrected or authorised reviewer override exists. | Supported by paragraph 3. | Add RBAC-gated reviewer override. | Correct |
| O-SAF-T-005 | Validation report must include failed record, failed field, severity, reason, owner and correction status. | Supported by paragraph 4. | Add structured export validation report table. | Correct |
| O-SAF-T-006 | Maintain validation evidence, reviewer decisions, document version hash and timestamp for audit reconstruction. | Supported by paragraph 4. | Add persistent audit record and report manifest. | Correct |
| O-SAF-T-007 | Customer-facing copy must not claim guaranteed legal compliance. | Supported by paragraph 5. | Add release wording review and approval workflow. | Correct |
| O-SAF-T-008 | Final compliance review remains customer responsibility. | Supported by paragraph 5. | Add safer release note disclaimer. | Correct |
| O-SAF-T-009 | Store source document text indefinitely for audit. | Not supported. | Dangerous overreach; source text retention must follow policy. | Incorrect |
| O-SAF-T-010 | Automatically file customer tax submissions with no human review. | Not supported. | Out of scope and high risk. | Incorrect |

## 4. Reviewer corrections

| Generated item | Initial AI output | Reviewer correction | Why it matters |
|---|---|---|---|
| O-SAF-T-002 | “All invoice records must include a transaction ID.” | “Transaction traceability applies when accounting or integrated accounting with billing is configured.” | Prevents over-scoping for billing-only configurations. |
| O-SAF-T-004 | “Block all failures.” | “Block critical failures; allow authorised reviewer workflow for edge cases.” | Balances compliance risk with operational exceptions. |
| O-SAF-T-009 | “Persist full source document indefinitely.” | “Persist hash, metadata and reviewer decisions by default; source text follows retention policy.” | Avoids privacy/security over-retention. |
| O-SAF-T-010 | “Automatically submit compliant records.” | “Feature validates and exports; customer submission workflow remains separate.” | Avoids unsafe automation and legal overclaim. |

## 5. Before / after requirement

### Before

> The system should validate SAF-T invoice data before export.

### After

> **R-SAF-T-001 — Pre-export invoice validation and traceability**  
> The system must validate sales invoice records before SAF-T export for customer tax identification number, invoice date, tax code, invoice total and customer account reference where applicable. For accounting or integrated accounting with billing configurations, the system must preserve traceability to the originating journal transaction using journal identifier, transaction date and archival/document number. Critical validation failures must prevent final export until corrected or explicitly reviewed by an authorised Compliance Reviewer. The validation report must include record identifier, failed field, severity, reason, owner and correction status. The system must persist a privacy-conscious audit trail containing source document hash, output hash, reviewer decision, report timestamp and signed manifest.

## 6. Jira ticket

```json
{
  "endpoint": "/rest/api/3/issue",
  "method": "POST",
  "fields": {
    "project": {"key": "SAFT"},
    "issuetype": {"name": "Story"},
    "summary": "Validate SAF-T invoice fields and accounting traceability before export",
    "description": {
      "type": "doc",
      "version": 1,
      "content": [
        {"type": "paragraph", "content": [{"type": "text", "text": "Requirement: R-SAF-T-001"}]},
        {"type": "paragraph", "content": [{"type": "text", "text": "Source obligations: O-SAF-T-001, O-SAF-T-002, O-SAF-T-003, O-SAF-T-004, O-SAF-T-005, O-SAF-T-006"}]},
        {"type": "paragraph", "content": [{"type": "text", "text": "Traceability: obligation → requirement → Jira → QA"}]}
      ]
    },
    "labels": ["saf-t", "compliance", "ai-assisted", "traceability"],
    "priority": {"name": "High"},
    "customfield_obligation_id": "O-SAF-T-001..006",
    "customfield_requirement_id": "R-SAF-T-001",
    "customfield_source_hash": "<document_sha256>"
  }
}
```

## 7. QA case

| Field | Value |
|---|---|
| Test ID | TC-SAF-T-001 |
| Requirement | R-SAF-T-001 |
| Source obligations | O-SAF-T-001, O-SAF-T-003, O-SAF-T-004, O-SAF-T-005 |
| Scenario | Missing customer tax ID blocks export and appears in validation report. |
| Given | A sales invoice is selected for SAF-T export and the customer tax identification number is blank. |
| When | The user runs pre-export validation. |
| Then | The invoice is marked as Critical, final export is blocked, the report shows invoice ID, field `CustomerTaxID`, reason, owner and correction status. |
| Evidence required | Screenshot/export of validation report plus audit event containing document hash and reviewer state. |
| Negative test | If a user with Viewer role attempts reviewer override, override is denied. |

## 8. Risky release note vs safer release note

### Risky version

> “This release guarantees SAF-T compliance for Portuguese invoice exports and automatically prevents all incorrect filings.”

### Safer version

> “This release adds pre-export validation checks for Portuguese SAF-T invoice exports. The feature helps users identify missing customer tax identifiers, inconsistent totals and applicable accounting traceability gaps before export. Final compliance review and submission responsibility remain with the customer.”

## 9. Claim → risk → reason → safer rewrite

| Claim | Risk | Reason | Safer rewrite |
|---|---|---|---|
| “Guarantees SAF-T compliance.” | High | Product validation cannot guarantee legal compliance across all customer configurations. | “Helps users identify selected SAF-T data quality issues before export.” |
| “Automatically prevents all incorrect filings.” | High | Export validation does not control customer submission decisions or all possible filing errors. | “Can block configured critical validation failures before final export.” |
| “Works for every accounting setup.” | Medium | Accounting traceability rules can vary by configuration and customer setup. | “Supports configured accounting and integrated accounting workflows covered by the rule pack.” |
| “No review needed.” | High | Human review remains part of compliance governance. | “Routes uncertain or high-risk items to authorised review.” |

## 10. Incident if missed

### Incident summary

A customer exports invoices after a release note states “SAF-T compliance guaranteed.” The validation feature checks missing tax IDs but does not check accounting traceability for integrated accounting mode. During customer audit preparation, the customer cannot reconcile several exported invoice records to accounting journal transactions.

### Timeline

| Timestamp | Event | Owner | Severity score | Evidence |
|---|---|---|---:|---|
| 2026-05-04 09:12 | Customer reports that exported records cannot be traced to journal transactions. | Support | 78 | Customer escalation ticket |
| 2026-05-04 10:05 | Support finds release note claim “guarantees SAF-T compliance.” | Support/Product | 82 | Release note version |
| 2026-05-04 11:20 | QA confirms tests covered tax ID and totals, but not integrated-accounting traceability. | QA | 88 | QA matrix gap |
| 2026-05-04 14:40 | Product identifies missing obligation O-SAF-T-002 in Jira scope. | Product | 91 | Requirement traceability report |
| 2026-05-05 09:30 | Compliance reviewer classifies communication as unsafe overclaim. | Compliance | 86 | Claim risk review |

### Postmortem actions

| Action | Owner | Due | Evidence required |
|---|---|---|---|
| Add integrated-accounting traceability validation. | Engineering | 2026-05-17 | Passing TC-SAF-T-006 and traceability matrix update |
| Add release communication approval by Legal/Compliance. | Product Ops | 2026-05-10 | Approval workflow record |
| Add gold obligation covering TransactionID/accounting traceability. | Compliance SME | 2026-05-12 | Updated gold set and benchmark result |
| Block “guarantee compliance” wording in release review. | PM/Support | 2026-05-10 | Claim risk rule and safer rewrite example |

## 11. Final audit report

| Section | Result |
|---|---|
| Source document hash | `<sha256>` |
| Output/report hash | `<sha256>` |
| Supported obligations | 7 |
| Weak obligations | 1 |
| Missing obligations | 1 |
| Reviewed obligations | 10 |
| Reviewer correction rate | 40% of generated obligations required reviewer comment or correction |
| QA coverage | 90% of accepted obligations mapped to at least one QA case |
| Unsupported claim rate | 22% initial → 6% after reviewer pass in synthetic evaluation |
| Release risk reduction | 4 high-risk claims rewritten to safer wording |
| Approval state | Product: approved with comments; QA: approved after test gap added; Support: approved safer copy; Legal/Compliance: required before external release |
| Production limitation | Demo controls are local. Production requires SSO/RBAC, encrypted tenant storage, managed audit logs and real OAuth integrations. |

## 12. Why this is stronger than “demo output”

This case shows the full product loop:

1. The source document is not simply summarised.
2. Obligations are extracted and challenged.
3. Reviewer corrections change product scope.
4. The requirement becomes a Jira-style implementation ticket.
5. QA cases trace back to obligations.
6. Release communication is risk-reviewed.
7. A plausible incident shows why missed traceability matters.
8. The final audit report captures support, weak points, missing evidence and human review.

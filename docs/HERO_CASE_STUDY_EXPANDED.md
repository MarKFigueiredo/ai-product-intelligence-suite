# Hero Case Study: SAF-T PT / E-invoicing Compliance-to-Product Traceability

**Project:** AI Product Intelligence Suite 1.04  
**Positioning:** Portfolio case study, not a commercial product.  
**Hero claim:** In 60 seconds, this app shows how a regulated product team can convert ambiguous compliance input into reviewed requirements, QA coverage and safer release communication.

---

## 1. The problem

Regulated enterprise product teams often receive compliance input that is difficult to translate into product work:

- source text is dense and ambiguous;
- product requirements lose traceability to the original obligation;
- QA cases do not always cover negative/failure conditions;
- release notes can overclaim compliance support;
- incidents become hard to reconstruct because decisions, evidence and approvals are scattered.

The hero case demonstrates a workflow for converting compliance source material into product artifacts that are **reviewable, testable and auditable**.

---

## 2. Hero source input

Example source material:

> Invoices included in a Portuguese SAF-T export must include the customer tax identification number, invoice date, tax code, invoice total and customer account reference where applicable. Records with missing tax identifiers or inconsistent totals should be corrected before export. The product should maintain sufficient validation evidence to support user review and audit checks. Export reports must show which invoice records failed validation and why.

---

## 3. Extracted obligations

| ID | Extracted obligation | Source support | Initial confidence | Reviewer decision |
|---|---|---:|---:|---|
| O-SAF-T-001 | SAF-T invoice exports must include customer tax identification number. | Strong | High | Correct |
| O-SAF-T-002 | SAF-T invoice exports must include invoice date, tax code and invoice total. | Strong | High | Correct |
| O-SAF-T-003 | Inconsistent totals and missing tax identifiers should block or flag export. | Strong | Medium | Correct, wording tightened |
| O-SAF-T-004 | Export reports should show which records failed validation and why. | Strong | High | Correct |
| O-SAF-T-005 | The product should maintain validation evidence for review and audit checks. | Medium | Medium | Correct, needs product scope caveat |

---

## 4. Reviewer correction example

### AI-assisted draft

> The system validates SAF-T invoice data before export.

### Reviewer issue

This is too broad. It does not specify fields, failure behavior or evidence requirements.

### Reviewed requirement

> The system must validate sales invoice records before SAF-T export for customer tax identification number, invoice date, tax code, invoice total and customer account reference when applicable. If required identifiers are missing or totals are inconsistent, the export workflow must flag the record, prevent unattended completion and include the validation reason in the export review report.

---

## 5. Requirement artifact

**Requirement ID:** REQ-SAF-T-001  
**Title:** Pre-export invoice validation and traceability  
**User:** Compliance analyst / product manager  
**Goal:** Detect invoice records that may make the SAF-T export incomplete or unreliable before the export is finalized.

### Acceptance criteria

- Given an invoice with missing customer tax identification number, when the export validation runs, then the invoice is flagged with a failure reason.
- Given an invoice with inconsistent totals, when the export validation runs, then the invoice is flagged and the reason is shown in the review report.
- Given a valid invoice record, when the export validation runs, then the invoice is marked eligible for export.
- Given validation failures, when the export report is generated, then failed records and failure reasons are included.

---

## 6. Jira-style ticket

**Ticket:** JIRA-SAF-T-001  
**Summary:** Validate SAF-T invoice fields and export review evidence  
**Type:** Story  
**Priority:** High  
**Owner:** Product / Engineering  
**Linked obligations:** O-SAF-T-001, O-SAF-T-002, O-SAF-T-003, O-SAF-T-004, O-SAF-T-005

### Description

Build a pre-export validation check for SAF-T invoice exports that checks required identifiers, tax fields, totals and evidence reporting. The implementation must support human review and not claim full compliance automation.

### Definition of done

- Validation checks exist for required invoice fields.
- Export workflow exposes failed records and reasons.
- QA includes positive and negative cases.
- Release note avoids unsupported compliance guarantees.
- Audit export includes source obligation, requirement, QA mapping and reviewer status.

---

## 7. QA cases, including mandatory negative coverage

| QA ID | Scenario | Type | Expected result | Linked obligation |
|---|---|---|---|---|
| QA-SAF-T-001 | Valid invoice record has tax ID, invoice date, tax code and total. | Positive | Record eligible for export. | O-SAF-T-001, O-SAF-T-002 |
| QA-SAF-T-002-NEG | Missing customer tax ID. | Negative | Record flagged; reason shown. | O-SAF-T-001, O-SAF-T-004 |
| QA-SAF-T-003-NEG | Inconsistent invoice total. | Negative | Record blocked or flagged; reason shown. | O-SAF-T-003, O-SAF-T-004 |
| QA-SAF-T-004-NEG | Validation evidence missing from export report. | Negative | Release gate fails. | O-SAF-T-005 |

**Mandatory gate:** every obligation that enters the requirement/Jira/QA handoff must have at least one mapped negative or failure-mode test before release-ready status.

---

## 8. Release communication risk

### Risky version

> This release guarantees SAF-T compliance for invoice exports.

### Risk table

| Claim | Risk | Reason | Safer rewrite |
|---|---|---|---|
| “guarantees SAF-T compliance” | High | Overclaims legal/compliance outcome and removes human review boundary. | “supports SAF-T review workflows by validating key invoice fields and surfacing export issues for human review.” |

### Safer release note

> This release adds SAF-T invoice export review support by validating key invoice fields, surfacing missing identifiers or inconsistent totals, and including validation reasons in the export review report. The feature is designed to support user review and audit preparation; it does not replace compliance, tax or legal approval.

---

## 9. Incident if missed

**Incident:** Customer exports invoices with missing tax identifiers.  
**Severity:** High  
**Customer impact:** Export review fails during audit preparation; customer support escalation opened.  
**Likely missed control:** Missing negative test for missing customer tax ID.  
**Preventive control:** Mandatory negative coverage gate and release claim scanner.

### Timeline

| Time | Event | Owner | Severity |
|---|---|---|---|
| T0 | Requirement created without explicit missing-tax-ID failure mode. | Product | Medium |
| T1 | QA covers valid export only. | QA | Medium |
| T2 | Release note says “validates SAF-T export”. | Product Marketing | Medium |
| T3 | Customer export has missing tax identifiers. | Customer | High |
| T4 | Support escalation opened. | Support | High |
| T5 | Postmortem links missing QA coverage to source obligation. | Product / QA | High |

---

## 10. Final audit report structure

The final export package should include:

- supported obligations;
- weakly supported obligations;
- missing obligations;
- reviewer corrections;
- requirement mapping;
- Jira-style tickets;
- QA positive and negative coverage;
- risky claims and safer rewrites;
- decision log;
- what would invalidate the feature;
- real vs simulated capability label.

---

## 11. What this demonstrates about my skills

| Skill | Evidence in the case |
|---|---|
| Domain understanding | SAF-T/e-invoicing source material translated into product artifacts. |
| AI workflow design | Source → obligation → review → requirement → QA → release → audit. |
| Human-in-the-loop product thinking | Reviewer corrections and approval gates. |
| QA discipline | Mandatory negative test coverage. |
| Risk-aware communication | Claim → risk → reason → safer rewrite. |
| Enterprise readiness judgment | Explicit real vs simulated boundaries. |
| Product strategy | Hero case kept focused while companion domains remain separate. |


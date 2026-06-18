# Error Taxonomy, Failure Cases and Product Trade-offs

This project is a portfolio case study, not a commercial product. This document makes the evaluation more credible by showing not only what the system does well, but also how it can fail, how those failures should be classified, and what product trade-offs were made.

## Why this document exists

AI portfolio demos often over-index on clean outputs. Regulated enterprise workflows need a different standard: they need failure visibility, reviewer correction, traceability and clear limits.

This document demonstrates three PM skills:

1. the ability to define a formal error taxonomy;
2. the ability to show realistic failure cases instead of hiding them;
3. the ability to reason about trade-offs such as speed vs precision, automation vs review and coverage vs noise.

---

## Formal error taxonomy

| ID | Error class | Definition | Example in SAF-T / e-invoicing workflow | Impact | Detection method | Mitigation |
|---|---|---|---|---|---|---|
| E01 | Unsupported claim | The output makes a claim that is not supported by the retrieved source text. | Release note says “fully compliant with SAF-T requirements” when only one TransactionID rule was checked. | High customer/legal risk. | Citation support check; sentence-level claim review. | Rewrite as scoped claim; require Legal/Compliance approval. |
| E02 | Weak source support | The output is directionally related to the source but lacks enough specificity. | Requirement says “link invoices to accounting entries” but omits `TransactionDate`, `JournalID` and `DocArchivalNumber`. | Medium/high implementation ambiguity. | Obligation quote matrix; reviewer mode. | Ask reviewer to mark weak support and add required fields. |
| E03 | Missing obligation | A relevant obligation in the source is not extracted. | Source states TransactionID is required for accounting/integrated files, but the obligation is absent. | High compliance and QA coverage risk. | Gold-set recall; reviewer missing-obligation workflow. | Add missing obligation and propagate to requirement/Jira/QA. |
| E04 | Hallucinated obligation | The system invents an obligation not present in the source. | Output requires a customer VAT check that is not in the uploaded excerpt. | High false-work / false-compliance risk. | Source quote required for every obligation. | Block export unless source support exists or marked as assumption. |
| E05 | Incorrect scope / jurisdiction | The system applies an obligation to the wrong filing type, country or process. | Applies accounting-file rules to billing-only export. | High compliance risk. | Scope field in obligation schema; reviewer check. | Make TaxAccountingBasis / jurisdiction explicit in every requirement. |
| E06 | Lost condition / threshold | The system captures an obligation but drops a condition, exception, date or threshold. | Captures TransactionID requirement but drops “when TaxAccountingBasis is C or I”. | High edge-case risk. | Condition extraction checks; QA negative tests. | Add condition field and require conditional QA cases. |
| E07 | Over-broad requirement | Requirement is too general to implement or test. | “System must support SAF-T compliance.” | Medium delivery risk. | Rule-based PRD completeness; QA testability review. | Rewrite into observable, testable behaviours. |
| E08 | Unsafe customer wording | Communication overpromises compliance or legal certainty. | “This release guarantees compliance with Portuguese tax law.” | High reputational/legal risk. | Claim-risk table. | Safer rewrite with scope, dependency and review caveat. |
| E09 | QA coverage gap | An obligation has no corresponding QA case or negative test. | Requirement exists but no test for TaxAccountingBasis = F. | High regression risk. | Obligation → requirement → QA coverage matrix. | Require QA case before “ready for release”. |
| E10 | Reviewer decision not propagated | Human correction is captured but not reflected downstream. | Reviewer adds missing obligation, but Jira/QA still use old requirement. | High workflow trust risk. | Run history diff; decision log. | Treat reviewer decisions as new source of truth for downstream generation. |
| E11 | Document version drift | Output was generated from an older document version. | Requirements were created from v1, but source guidance was revised in v2. | High audit and delivery risk. | SHA-256 document version hashes. | Display source version hash on every report/export. |
| E12 | False confidence from metrics | A score appears precise even though evaluation data is limited or synthetic. | “90% recall” is shown without saying it is from a small synthetic gold set. | Medium trust risk. | Evaluation limitation labels. | Mark metrics as synthetic and not production performance. |
| E13 | Noisy over-extraction | The system extracts too many low-value obligations. | Extracts explanatory notes as mandatory requirements. | Medium review burden. | Reviewer correction rate; precision on gold set. | Tune extraction threshold; separate “must/should/context”. |
| E14 | Integration payload mismatch | Jira/GitHub export shape looks plausible but does not match real workflow expectations. | Jira ticket lacks acceptance criteria, source link or compliance owner. | Medium adoption risk. | API-shaped schema review; mock connector tests. | Validate payload schema with real target workflow before production. |
| E15 | Incident lesson not linked back | Postmortem action is written but not linked to obligation/requirement/QA. | Incident says “add test coverage” but does not identify the missed obligation. | Medium recurrence risk. | Incident → obligation → QA link check. | Require every action to cite source obligation and owner. |

---

## Failure cases intentionally shown

### Failure case 1 — Missing condition from source text

**Source pattern:** The requirement applies only when `TaxAccountingBasis` is `C` or `I`.

**Bad output:**

> “The system must populate TransactionID for all sales invoices.”

**Why it fails:** It loses the condition. The actual rule is scoped to accounting/integrated accounting files, not necessarily every billing-only export.

**Risk:** Engineering may overbuild, QA may test the wrong cases, and release communication may imply broader compliance coverage than delivered.

**Corrected output:**

> “When `TaxAccountingBasis` is `C` or `I`, the system must populate `TransactionID` in `SalesInvoices` using the originating GL journal transaction fields: `TransactionDate`, `JournalID` and `DocArchivalNumber`.”

---

### Failure case 2 — Unsupported release claim

**Risky release note:**

> “This release guarantees SAF-T compliance for Portuguese e-invoicing exports.”

**Why it fails:** The claim is broader than the tested/source-grounded change. It also sounds like a legal guarantee.

**Safer rewrite:**

> “This release improves SAF-T traceability for supported accounting and integrated accounting exports by deriving `TransactionID` from linked GL journal transaction data. Final filing responsibility and compliance review remain with the customer’s finance/compliance process.”

---

### Failure case 3 — High PRD completeness but weak QA

**Bad outcome:** The PRD has problem statement, requirement, acceptance criteria and dependencies, so the completeness score is high. However, the QA matrix lacks negative cases for `TaxAccountingBasis = F` and missing GL journal linkage.

**Why it fails:** A PRD can be structurally complete but operationally unsafe.

**Mitigation:** Completeness is measured by rule, but release readiness also requires obligation-level QA coverage and negative tests.

---

### Failure case 4 — Reviewer correction not propagated

**Bad outcome:** A reviewer marks an obligation as missing, but the Jira ticket and QA case were already generated from the earlier run.

**Why it fails:** The human-in-the-loop step is only valuable if downstream artefacts are regenerated or flagged stale.

**Mitigation:** Reviewer decisions should create a new run version, update the decision log and mark downstream outputs as stale until regenerated.

---

### Failure case 5 — Document version drift

**Bad outcome:** The final audit report references an earlier source document, but the compliance guidance was later updated.

**Why it fails:** The report may be internally consistent but externally outdated.

**Mitigation:** Every report includes a document hash, run timestamp, source version and reviewer status.

---

## Trade-off analysis

| Trade-off | Product tension | Portfolio decision | Why this is the right signal |
|---|---|---|---|
| Speed vs precision | Faster generation increases risk of shallow or unsupported outputs. | The app shows time savings, but adds citation checks, reviewer mode and supported/weak/missing labels. | Demonstrates that speed is valuable only when trust controls are visible. |
| Automation vs human review | Full automation looks impressive but is risky in compliance workflows. | Human review is explicit and downstream artefacts depend on review state. | Shows enterprise AI judgment: AI assists, humans approve. |
| Coverage vs noise | Extracting more obligations can improve recall but increase reviewer burden. | Metrics include both recall and reviewer correction rate. | Shows understanding that “more output” is not always better product value. |
| Rule-based evaluation vs LLM judgment | Rules are transparent but limited; LLM judges are flexible but subjective. | PRD completeness and support checks are rule-based where possible; LLM output is treated as draft. | Shows preference for deterministic checks in high-trust workflows. |
| Broad suite vs focused hero workflow | Four modules demonstrate breadth but may dilute the message. | v17 positions SAF-T/e-invoicing as the hero workflow and the other modules as supporting workflows. | Maximizes hiring signal by showing depth first, breadth second. |
| Enterprise realism vs prototype scope | Full SSO/RBAC/tenancy would be overkill for a portfolio. | v16/v17 implement local role simulation, audit store, document hashes and signed report manifest. | Shows production awareness without pretending the prototype is production software. |
| Simplicity vs auditability | Simple UI is easier to demo, but enterprise trust requires detail. | The demo uses a simple linear story, while deep docs expose audit details. | Supports both recruiter screening and senior technical review. |
| Synthetic metrics vs no metrics | Synthetic metrics are imperfect, but no metrics suggests weak evaluation discipline. | Metrics are labelled synthetic and not production performance. | Shows honest measurement discipline. |

---

## How this should be discussed in interviews

Use this framing:

> “I intentionally included failure modes and trade-offs because regulated AI workflows should not be evaluated only on clean demo outputs. The important product question is not whether the AI can generate something plausible; it is whether the workflow can surface uncertainty, route the right decisions to humans, preserve evidence and prevent unsafe downstream claims.”



## v19 extension — mandatory negative test coverage

| Error ID | Error class | Definition | Example | Product risk | Detection | Required response |
|---|---|---|---|---|---|---|
| E16 | Unmapped or missing negative coverage | A requirement has happy-path QA but no obligation-linked negative/edge/failure test. | O1 validates CustomerTaxID, but QA only tests valid invoices. | High false-confidence and release regression risk. | Mandatory negative coverage gate. | Block release-ready status until each obligation has at least one mapped negative test. |

This extends E09. E09 flags a general QA coverage gap; E16 specifically catches the dangerous case where positive coverage exists but failure-case coverage is missing or unmapped.

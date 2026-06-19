# Human Feedback Flywheel — v1.04

v1.04 separates reviewer decisions from generic usage metrics and stores them in a dedicated `human_reviews` table.

## What is stored

Each review can store:

- run ID;
- document hash;
- domain;
- artifact type and ID;
- original text;
- review label;
- optional corrected text;
- review reason;
- reviewer role/name;
- signature metadata.

Supported labels include:

```text
correct
incorrect
needs_review
needs_clarification
missing_evidence
too_broad
out_of_scope
duplicate
needs_negative_test
```

## How it is reused

Future runs can retrieve a small number of relevant reviewer corrections and use them as local few-shot examples or pattern guardrails.

This is intentionally conservative:

- it is not model training;
- it does not claim quality improvement without human validation;
- it records how many examples were available, used, and how many obligations were adjusted.

## UI signal

The Interpret reviewer tab now shows:

- stored reviews;
- reusable examples;
- obligations adjusted by prior feedback in the current run.

Safer wording in the UI is “adjusted using prior reviewer examples”, not “improved”, unless human validation later confirms improvement.

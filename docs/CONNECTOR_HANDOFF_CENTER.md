# Connector Handoff Center

## Purpose

The Connector Handoff Center demonstrates how AI-generated product artefacts can move toward operational workflows without pretending that the portfolio prototype is a full enterprise integration platform.

## Modes

### Local outbox mode

Default and safe. Payloads are written to `.local_connector_outbox/` as JSON files. This creates reviewable handoff evidence without sending data externally.

### Live mode

Optional. Live Jira/GitHub/Slack calls require credentials in `.env` and explicit opt-in from the UI.

## Payloads

v20 includes previewable payloads for:

- Jira issue creation;
- GitHub issue creation;
- Slack webhook message.

## Why this matters

The product signal is not “I built perfect connectors.” It is:

- I understand where product artefacts need to go next;
- I can shape realistic handoff payloads;
- I can separate safe local review from live external sending;
- I can record connector events for audit and usage metrics.

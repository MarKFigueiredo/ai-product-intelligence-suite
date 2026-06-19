# Quality Learning Loop

v1.03 adds a quality learning layer on top of persisted usage metrics. This moves the project beyond “we collect metrics” toward “we use metrics to learn where the workflow improves or fails.”

## Current local signals

- workflow run mix;
- release block events;
- export/handoff events;
- quality metric trends for unsupported claims, QA coverage, negative coverage, high-risk claims and stale artefacts when those metrics exist.

## What this demonstrates

A product manager should not only instrument usage. They should define what the data means and how it changes product decisions. This page turns local telemetry into reviewable product evidence.

## Next step with real reviewers

Run 10–20 realistic sessions, export the usage evidence ZIP, and summarize:

- which workflow created the most reviewer corrections;
- which obligations most often caused stale downstream artefacts;
- whether negative test coverage reduced release blocks;
- whether safer rewrites reduced high-risk claims;
- what should be improved next.

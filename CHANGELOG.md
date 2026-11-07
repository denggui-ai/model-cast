# Changelog

## 2026-11-07 — public V0.2 experiment snapshot (unreleased)

- Trigger: publish the separately reviewed face-casting guidance without private runs or internal history.
- Behavior before: private event-file dependencies prevented other developers from running the complete test suite.
- Behavior after: tests use synthetic events and colour-block fixtures with current hashes. Production scripts, fixed prompts and face-casting guidance are unchanged from this workstream.
- Eval coverage: 23 scenario definitions, including IDs 19–23 for feature preservation, clarification, single-objective editing, side effects and dialogue replay; these definitions are not evidence of model-driven evaluation.
- Verification: see the public verification document; automated checks do not establish visual quality.
- Practical acceptance: two authorized images did not establish a visibly rounder nose tip. Recovery from real eye drift remains unverified. The experiment is not accepted for this case.

## Packaging separation

This branch retains the V2 ZIP packaging baseline. T15/V3 direct upload is a separate, unmerged workstream.

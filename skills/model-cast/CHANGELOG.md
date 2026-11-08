# Changelog

## 2026-11-07 — public T15 snapshot (unreleased)

- Trigger: publish a reusable, privacy-screened source snapshot without pushing private development history.
- Behavior before: local-only tests depended on a private event transcript and source-specific image hashes.
- Behavior after: public tests use separate clean/contaminated synthetic event streams and deterministic colour-block assets with matching manifest/provenance hashes; runtime scripts and fixed C2 prompts are unchanged.
- T15: V3 direct upload uses originals 01/04/06/07; rejects V1/V2 layouts and accepts V10+ manifest versions.
- Eval coverage: original T15 regressions plus six public-distribution integrity checks.
- Public usability: remove a one-off implementation-session instruction from the installed skill; restore the project-level `state/` ignore guard.
- Verification: see the repository verification document; tests do not establish image quality.

## Legacy public main

The existing public main and its historical prerelease are unchanged. These branches do not merge into it or create a new release.

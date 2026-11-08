# Changelog

## 2026-11-07 — public T15 snapshot (unreleased)

- Trigger: publish a reusable, privacy-screened source snapshot without pushing private development history.
- Behavior before: local-only tests depended on a private event transcript and source-specific image hashes.
- Behavior after: public tests use separate clean/contaminated synthetic event streams and deterministic colour-block assets with matching manifest/provenance hashes; runtime scripts and fixed C2 prompts are unchanged.
- T15: V3 direct upload uses originals 01/04/06/07; rejects V1/V2 layouts and accepts V10+ manifest versions.
- Eval coverage: original T15 regressions plus four public-distribution integrity checks.
- Verification: see `docs/VERIFICATION.md` in the repository; tests do not establish image quality.

## Legacy public main

The historical `v0.1.0-beta.1` prerelease remains unchanged.

## 2026-11-08 — v0.2.0 release candidate

- Prepare the merged multi-file AI model library, Yuning showcase, and selectively integrated face-casting guidance for formal publication as `v0.2.0`.
- The seller-package format remains V3.0; it is distinct from the software release version `v0.2.0`.
- C10 human-pose line art remains unimplemented and is not included. N2 remains the existing grey mannequin camera/framing guide.
- Verification: 242 automated tests passed on the exact merged main commit; all tracked distribution files pass SHA-256 verification. Git metadata is excluded from `SHA256SUMS` because `.git` is checkout/worktree-specific. The formal tag and GitHub Release are still pending.
- Codex multi-file end-to-end behavior remains unverified; ChatGPT's one side-view generation test did not conclusively prove independent identity control from both references.

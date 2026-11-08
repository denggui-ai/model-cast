# model-cast v0.2.0 — release candidate

This release candidate packages the merged T15 finalization work for the proposed `v0.2.0` formal release: the ordinary ChatGPT/Codex multi-file visual-reference library, the Owner-authorized Yuning project showcase, and the selectively integrated face-casting design guidance with Evals 19–23. The Git tag and GitHub Release are not created yet.

The seller-package format is V3.0; it is not the software release version. The release source contains the package builder and templates, not private RUN records, private handoffs, or owner-specific generated seller packages.

## Included

- Original adult AI model casting, identity approval and visual-asset handoff workflow.
- Twelve C6 model views, three accepted action/expression examples, and the N2 grey mannequin camera/framing guide in the documented V3.0 package workflow.
- Bilingual multi-file library instructions and generated asset index; the existing four-image core set remains available.
- Separate Lookset D2 adapter and selectively integrated face-casting design guidance.

## Explicit limitations

- C10 human-pose line art is not implemented and is not included.
- N2 is a camera/framing guide, not model identity, a pose drawing, clothing reference, or image-edit base.
- ChatGPT recognized 16/16 library assets. One side-view generation test was limited and did not conclusively establish independent identity control from both references.
- Codex CLI 0.161.0 multi-file end-to-end behavior remains unverified after two timed-out attempts.
- Fine local facial editing, reliable garment fidelity, and the complete Lookset commercial image workflow are not claimed.

## Verification and environment

The full automated suite passed 242 tests on the exact merged main commit. Tracked project files pass `SHA256SUMS`; Git metadata is intentionally excluded because `.git` is a checkout/worktree-specific pointer rather than a distributable source file. `git diff --check` passed.

The complete workflow is verified on macOS with Python 3.10+; `crop.py` uses system `sips`. Pillow and available system CJK fonts are required for relevant packaging operations. Codex CLI 0.161.0 is the pinned generation baseline; validate another version before use.

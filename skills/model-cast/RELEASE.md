# model-cast v0.2.0 — formal source release

This formal release packages the merged T15 finalization work: the ordinary ChatGPT/Codex multi-file visual-reference library, the Owner-authorized Yuning project showcase, and the selectively integrated face-casting design guidance with Evals 19–23.

The seller-package format is V3.0; it is not the software release version. The release source contains the package builder and templates, not private RUN records, private handoffs, or owner-specific generated seller packages.

## Included

- Original adult AI model casting, identity approval and visual-asset handoff workflow.
- Twelve C6 model views, three accepted action/expression examples, and the N2 grey mannequin camera/framing guide in the documented V3.0 package workflow.
- Bilingual multi-file library instructions and generated asset index; the existing four-image core set remains available.
- Separate Lookset D2 adapter and selectively integrated face-casting design guidance.

## Explicit limitations

- C10 is not included in the v0.2.0 release artifact. After that release, PR #7 added three optional grey-mannequin pose references to current `main` as a separate supplement; they do not alter the v0.2.0 tag/archive.
- N2 is a camera/framing guide, not model identity, a pose drawing, clothing reference, or image-edit base.
- ChatGPT recognized 16/16 library assets. The original v0.2.0 side-view test did not conclusively establish independent identity control from both references. Post-release C10 tests generated walking, side-sitting, and hands-in-pockets results; pose execution was visually checked, while identity preservation remains qualitative and not independently verified.
- Codex CLI 0.161.0 multi-file end-to-end behavior remains unverified after two timed-out attempts.
- Fine local facial editing, reliable garment fidelity, and the complete Lookset commercial image workflow are not claimed.

## Verification and environment

The full automated suite passed 242 tests on the exact merged main commit. Tracked project files pass `SHA256SUMS`; Git metadata is intentionally excluded because `.git` is a checkout/worktree-specific pointer rather than a distributable source file. `git diff --check` passed.

The complete workflow is verified on macOS with Python 3.10+; `crop.py` uses system `sips`. Pillow and available system CJK fonts are required for relevant packaging operations. Codex CLI 0.161.0 is the pinned generation baseline; validate another version before use.


## Post-v0.2.0 source supplement (2026-11-09)

The current `main` branch includes three optional C10 grey-mannequin pose references (PR #7) and their ChatGPT usage-status documentation (PR #9). These are separate post-release additions. They are not part of the immutable v0.2.0 tag or release archive, and they do not modify owner-specific V3.0 seller packages or Lookset D2.

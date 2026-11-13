# Public project status — 2026-11-13

| Workstream | Location | Status |
|---|---|---|
| Core model creation (C1–C8/C11) | `main` | Public source integrated. Covers original adult AI model creation, identity approval, model views/actions, N2 camera guide, and asset handoff. |
| Ordinary AI asset library | `main` (this finalization PR) | Builder now creates a multi-file ChatGPT/Codex library with 12 model views, 3 action examples, N2, START-HERE and asset-index. ChatGPT recognized 16/16 assets; one side-view generation test was limited and did not prove independent identity control from both references. |
| Lookset D2 | `main` | Separate adapter export and structure/readback validation; full downstream commercial image workflow is not claimed as verified. |
| C10 pose supplement | Three grey mannequin pose assets merged to `main` in PR #7 | ChatGPT pose-execution checks: C10-01 walking, C10-02 side sitting, and C10-03 hands-in-pockets each have a generated result. C10-02 and C10-03 were visually checked and show the requested pose. Face appearance is qualitatively consistent with the supplied C6 face reference, but identity preservation has not been independently or biometrically verified. Not included in v0.2.0 or existing V3.0 packages. |
| Face-casting design guidance | `main` + `opensource/v0.2-face-casting` | Guidance and Evals 19–23 selectively integrated; real nose-tip edit target not accepted. Remaining experimental branch is not merged wholesale. |
| Public showcase | `main` (this finalization PR) | Owner-authorized AI-generated Yuning face/full-body/C6/N2 examples documented with limitations. |
| Approved identity delivery | Post-v0.2.0 source update | Minimal delivery of approved 01/04, traceable casting rationale, and a host-invoked check of actual native-request identity slots against approved C4 originals. One correct-source downstream image was accepted by the Owner for identity reuse; garment QA remained separate and unmet. This does not establish cross-product, cross-angle or cross-host stability. |
| Formal release | v0.2.0 | Formal source release published after merge and clean archive verification; see GitHub Releases. |

## Product boundary

model-cast creates an original AI model and hands off visual assets. It does not provide ongoing garment try-on, clothing design, or commercial photography. Ordinary ChatGPT/Codex use and Lookset are separate downstream paths. N2 is a camera/framing guide, not an identity reference. Lookset D2 remains separate and does not receive N2 or C10 by default.

Automated tests verify code and package structure, not image quality. ChatGPT and Codex host behavior must not be described as equivalent until each is tested. See [README](../README.md) and [VERIFICATION](VERIFICATION.md).

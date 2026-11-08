# Verification — public model-cast source and multi-file library

Tested on macOS with Python 3.14; 2026-11-08.

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider
242 passed in 33.18s
```

The suite uses synthetic fixtures and does not invoke image generation. It covers source/manifest hashes, version boundaries, package structure, the four-image core set, the 16-image AI library, generated asset-index integrity, no-overwrite behavior, synthetic receipts/contamination, image-source checks, and the pinned Lookset exporter.

## Actual Yuning package verification

A new V3.0 multi-file candidate was built into a new output directory; the previous V3.0 candidate and original source assets were not overwritten.

- Chinese and English packages each contain a `4_...MultiUpload` folder.
- Each folder contains exactly 16 PNG assets: 12 C6 model views, three accepted action/expression examples, and the N2 grey mannequin camera/framing guide.
- Each folder also contains `START-HERE.md` and `asset-index.json`.
- All 16 image hashes match the source files; both language indexes match the manifest.
- `check_pack.py --require-lookset` returned `problems=0`.
- Lookset D2 was exported and structurally validated separately; it does not include N2 or the ordinary-user guide.

## ChatGPT direct multi-file test

- The Owner uploaded the direct multi-file test folder containing 16 source images, a contact sheet, `asset-index.json`, and `START-HERE.md`.
- ChatGPT identified and classified all 16 source images, distinguishing four core identity references, eight supplementary angles, three action/expression examples, and N2.
- For a hypothetical full-body side-view request, it selected the face identity anchor plus the full-body side reference.
- A separately authorized one-image generation test used the uploaded face-front and full-body-side references. The output preserved side framing, body proportions, hairstyle and outfit reasonably well. Because the output was a strict side view, it did not provide enough visible facial information to conclusively verify facial identity or prove each reference's independent contribution.
- The authorized generation allowance was 1 image and was fully used. No further image generation is part of this source update.
- Codex CLI 0.161.0 was attempted in read-only mode with the full 16-image attachment set and then a reduced 5-image set. Both model requests timed out before returning a recognition result; no generation or file modification occurred. Therefore Codex image-recognition/reference-selection behavior remains unverified, not failed. A future retry should be smaller or use a different session/network window.

## Limits

Reading/selecting attachments does not prove that a downstream image-generation/editing tool received them. The user instructions require the host to confirm actual reference handoff or ask for direct re-upload. ChatGPT and Codex behavior must not be described as identical until both are tested.

The face-casting guide is documentation/eval guidance, not a precise facial-edit controller. The V0.2 face-casting guide is selectively integrated with Evals 19–23; this validates guidance/eval structure, not actual edit quality. C10 human-pose line art remains unimplemented. N2 is a camera/framing guide, not model identity, a pose drawing, or a clothing drawing. C5 was an internal identity-continuity check, not garment-fidelity validation. V0.2's practical nose-tip edit target was not accepted. Automated tests and package validation do not prove image quality or Owner acceptance.

## Release candidate re-verification — 2026-11-08

On the exact merged `main` commit `041d3ac0aaa3de90c69bb07848f1c1e9ce5c0514` in a clean detached worktree:

- `python3 -m pytest -q -p no:cacheprovider`: **242 passed in 30.64s**.
- `git diff --check`: passed.
- `shasum -a 256 -c SHA256SUMS`: every tracked distribution file passed after excluding the `.git` entry. `.git` is not tracked by Git and is represented differently in linked worktrees; hashing it makes the manifest non-portable and is not a project-file integrity check.
- The V3.0 bilingual package candidate was checked with `check_pack.py --require-lookset`: `problems=0`. This verifies package structure and byte provenance, not visual quality or public redistribution rights for the generated seller package.

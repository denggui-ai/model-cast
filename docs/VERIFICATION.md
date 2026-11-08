# Verification — public T15 snapshot

Snapshot tested on macOS with Python 3.14; 2026-11-07.

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider
240 passed in 35.00s
```

This is a fresh full-suite run of the public working tree, not a reused private-worktree result. The 240 cases include the original T15 regression coverage (the real-event dependency is replaced by an equivalent synthetic case) and six public-snapshot integrity checks, including a guard against one-off internal instructions and an explicit private-state ignore rule. None of these tests invokes image generation.

Covered: source/manifest hashes, new-version rejection boundaries, package structure, exact upload set, no-overwrite behavior, synthetic receipts and contamination, image-source checks, and the pinned Lookset exporter. Eval JSON files describe scenarios; this result is not a model-driven execution of every scenario.

The production Python files and fixed workflow prompts are compared byte-for-byte with the reviewed source. Vendor provenance is verified against its pinned upstream commit. Before push, every new-tree file is scanned for personal paths, credentials and private runtime artifacts, and SHA256SUMS is recomputed.

The file scan cannot certify absence of every possible secret. It is an automated pattern/content and file-set check plus manual review of the exported tree. No private development commit is an ancestor of this snapshot. Previously public main history is retained.

Passing tests do not prove identity preservation, garment fidelity or visual acceptance. Live generation requires separate authorization; V0.2's two-image nose-edit case did not meet its target. No generation is authorized by this source publication.

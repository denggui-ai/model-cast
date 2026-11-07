# Verification — public V0.2 experiment

The code and fixed prompts retain this workstream's reviewed baseline. Public tests replace private logs with synthetic fixtures; they do not invoke generation. The full public-tree suite was executed on macOS / Python 3.14 on 2026-11-07:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider
211 passed in 23.99s
```

These are 207 workstream cases (the private-event dependency is replaced by a synthetic case) plus four public-distribution checks. The result has zero failures and zero skips. Lookset export/validate runs only on synthetic fixtures. The runtime, fixed prompts and face-casting guide are checked byte-for-byte against the reviewed workstream source. Vendor files are unmodified and match their pinned upstream commit.

Before publication, the staged public tree is checked for credentials, personal paths, private runtime files, local-link validity and checksum coverage. This does not certify the absence of every possible secret, and no private development history is pushed. Skill strict and quick validation are also run on the public tree.

The separately authorized two-image practical test did not clearly achieve the requested nose-tip rounding. Both candidates were judged recognizable with almond-shaped eyes retained; this is a case-specific observation, not a statistical identity-preservation claim. No real eye drift occurred, so repair of such drift remains unverified. These private images and run records are excluded from the repository.

The experiment remains NOT ACCEPTED for this case. Static tests, scenario definitions, code review and Owner visual acceptance are separate gates. No new generation, main merge or tagged release is authorized by the source publication.

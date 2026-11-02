# Verification scope — v0.1.0-beta.1

This is a source prerelease of a guided workflow, not a claim of general production readiness.

## Verified before this release

- One scoped POC: save an already accepted AI face with original bytes retained, validate/read its package, import it into Caiguang beta.18, generate one garment image, and obtain the user's acceptance of the reused person. Caiguang code was not modified.
- The POC's main garment structure passed assistant review. Framing, lighting ratio and fine material fidelity retain open review items; it is not full commercial image approval. Private references, the result and third-party garment images are withheld from this public repository.
- 25 offline tests from this source layout passed on the maintainer's macOS machine against the real beta.18 model-reference interface. They cover private isolation, budget locking, zero-generation saves, supplements, immutable returns, failure recovery and missing acceptance notes. No cases were skipped. Synthetic test colors are not image-quality evidence.
- Runtime skill structure and the runtime/evidence separation passed deterministic validation. Eval definitions include 19 scenarios; many remain author walkthroughs or unexecuted definitions, not implicit invocation evidence.

## Release review

The reviewed runtime lives in skills/model-cast. Tests, eval definitions, this record, the changelog and the offline guide are source/release material and are not copied into the installed runtime. Only two approved public seeds and six original WebP reference images are included. Runtime Python logic is unchanged from the POC implementation; release edits clarify completion, dependencies and data flow.

An independent read-only reviewer found no blocking defect and completed two explicit instruction-following text simulations (missing consumer/text-only request; unaccepted candidate/completion question). These are not implicit-trigger tests. The offline guide passed desktop (1440 px) and mobile (390 px) layout, local-link, keyboard-focus and console/network checks; body text contrast is greater than 5.8:1 for the shipped color combinations.

Storage enforcement is limited: code rejects paths within the installed runtime subtree. In a source checkout it does not reject every sibling directory; the assistant must obey the documented requirement to place private tasks outside the whole checkout. The task-level .gitignore reduces accidental staging but is not access control. This remains a disclosed boundary of the guided workflow.

The file inventory and per-file digests are recorded in SHA256SUMS. The initial public commit is created from this reviewed allowlist, without the private development Git history. The digest file itself is excluded from its own inventory. A digest verifies bytes against a trusted expected value; it does not independently authenticate the maintainer.

## Unverified and deferred

Fresh-host installation/discovery, implicit triggering, other operating systems, the minimum Codex client version, actual upgrade/rollback/uninstall, cross-product identity stability, arbitrary aesthetic requests, exact size/fit and comprehensive commercial QA remain unverified. Windows is unsupported by the current fcntl-based ledger. No automatic self-evolution or closed-loop quality claim is made.

Aesthetic refinement, more public models, a plugin-marketplace package and cross-platform adapters are backlog. Uninstall and rollback procedures are documented in USER-GUIDE.html; they are not represented as observed lifecycle tests.

## Reproduce the local tests

Use the README command with MODEL_CAST_THREADTRUTH set to the actual Caiguang skill directory. Check the output for skips. All tests are offline; a real native generation call is a separate action requiring its own authorization. The original private POC cannot be reproduced from this public repository without supplying new authorized identity and garment inputs.

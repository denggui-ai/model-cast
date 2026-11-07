# model-cast Project Adapter

**Standard:** AI Development Operating Standard V2.0
**Selected mode:** Standard + local Controlled safeguards
**Owner:** Repository maintainer
**Public adaptation:** 2026-11-07; private paths and internal handoff records omitted.

## 1. Project purpose and critical workflows

model-cast is a local Codex/Claude Skill (the complete toolchain is currently validated on macOS) for selecting an original model for a product line, fixing the selected model, validating the approved workflow and delivering a model reference pack. It is not a general-purpose clothing try-on or image-generation service.

Critical workflows and acceptance gates are defined by the approved project blueprint and phase specifications, not by this adapter.

## 2. Authority and project-specific rules

The following remain authoritative and are not replaced by the generic standard:

- Applicable repository instructions and the approved contribution/task scope.
- Owner-approved project blueprint and phase-specific specifications.
- A single maintainer-selected progress record for each task; no private ledger is distributed here.
- Owner decisions recorded in the project schedule, specifications and handoffs.

If this adapter conflicts with any of the above, stop and follow the higher-authority project rule or ask the Owner.

## 3. Roles and work lanes

| Responsibility | model-cast assignment | Boundary |
|---|---|---|
| Project coordination / architecture / specifications / visual acceptance | Claude, under existing Owner-approved division | Does not write the implementation-owned skill code; maintains project schedule and designated rule files |
| Skill code / scripts / tests / technical text drafts | Codex in dedicated worktrees | Does not modify Claude-owned files or external output directories unless a phase spec explicitly authorizes it |
| Independent code review | An independent non-author reviewer after the implementation commit | Must inspect actual diff; unavailable/access-blocked means review blocked, not passed |
| Final acceptance / merge / release | Owner | Explicit approval required for each merge/publish operation |
| ChatGPT | Cross-session coordination, analysis and handoff support when authorized | Does not override Codex/Claude file ownership or project rules |

One writer per worktree. Reviewers are read-only. Keep T15/V3.0 and V0.2 isolated.

## 4. Risk mode

Use **Standard** for ordinary documentation, skill instructions, tests and code changes.

Apply **Controlled safeguards** to:
- original model images and private identity assets;
- personal or customer data;
- credentials, tokens and account access;
- external uploads or third-party processing;
- image-generation quota and paid API usage;
- deletion, overwrite, bulk move/rename and irreversible changes;
- Lookset/vendor files and licensed reference libraries.

Before a high-risk action: identify exact target and side effects, verify authorization, preserve originals/backup, preview bulk changes, and record the action. Do not upload private material without explicit destination/purpose authorization.

## 5. Git and worktree conventions

- All writes occur in a dedicated `.worktrees/<task>` worktree and task branch.
- Do not write directly to `main`.
- Do not push or merge without explicit Owner authorization.
- Before work: inspect root, branch, HEAD, dirty/staged state and relevant worktree.
- Before commit: inspect staged diff, secrets, generated files and `git diff --check`.
- Do not reset, clean, overwrite user changes or delete lock files to force progress.
- Do not concurrently edit the same worktree/file from multiple agents.

## 6. Specifications, schedule and acceptance

- Every meaningful phase follows its Owner-approved SPEC.
- Reuse the maintainer-selected task record instead of creating competing schedules.
- Reuse the phase's existing checklist/evals. Do not create duplicate acceptance ledgers.
- `docs/PROJECT-STATUS.md` is a concise cross-workstream snapshot only; verify its branch/commit facts before relying on it.
- Completion claims distinguish implemented, locally verified, independently reviewed, Owner accepted, merged and released.

## 7. Tests and evidence

For each task, record the actual commit tested, environment, exact commands, output, pass/fail/skip counts and timestamp. Historical results must be labeled historical. Static checks do not prove image quality or Owner acceptance.

Retain project-specific evidence requirements, including quota checks and exporter/readback evidence. Store private reference hashes and real run records outside public commits; use synthetic data in public tests.

## 8. Handoff and session recovery

For meaningful task/phase boundaries, maintain one canonical handoff or START-HERE per workstream. Avoid creating multiple competing summaries. New sessions must:
1. Read the relevant START-HERE and approved SPEC.
2. Verify live branch, HEAD, dirty state and files.
3. Cross-check previous completion claims.
4. Report current state and one next action.
5. Continue without repeating completed work.

At pause/finish, update the approved task record through its designated owner. Do not overwrite another work lane’s uncommitted work.

## 9. Public entry points

- Runtime packaging: `opensource/t15-direct-upload` branch README.
- Experimental face-casting: `opensource/v0.2-face-casting` branch README and verification document.
- Public workstream snapshot: [PROJECT-STATUS](PROJECT-STATUS.md).

These are separate source snapshots, not an integrated release. This protocol grants no generation, push, merge or release authority by itself.

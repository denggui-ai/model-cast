# model-cast Development Protocol

**Version:** 1.0 — public adaptation
**Public adaptation date:** 2026-11-07
**Purpose:** Keep development continuous even when a model, app, or conversation becomes unavailable.

## 1. Core principle

model-cast is **Git-driven, handoff-backed, conversation-assisted**. A conversation is a temporary workspace, not the project's memory or source of truth.

A task must be recoverable from the repository state and its handoff without rereading the full prior chat. If a previously reported commit differs from the live worktree, trust the live Git state and correct the status snapshot before proceeding.

## 2. Four work lanes

| Lane | Purpose | Allowed work | Must not do |
|---|---|---|---|
| Project coordination | Maintain priorities, schedule, status, blockers and Owner decisions | Read all workstream handoffs; update project status and schedule when authorized | Quietly modify implementation owned by another lane; claim unverified completion |
| Development | Implement one approved task in its dedicated worktree | Code, tests, task-specific docs, commits and handoff | Review own change as independent approval; edit another active worktree; push/merge without approval |
| Independent review | Inspect a fixed commit/diff read-only | Report findings with severity, file/line, evidence and recommendation | Edit files, commit, or rely on the implementer's narrative instead of source |
| Release and acceptance | Verify the release candidate and obtain Owner decision | Run release checks, compare artifacts, record acceptance and prepare merge | Treat tests as Owner acceptance; merge or publish without explicit Owner approval |

These are **work lanes**, not a requirement to create a new conversation for every small action. Keep one conversation per coherent deliverable or review. Start a new conversation when the current one becomes long, blocked, rate-limited, or changes lane materially.

## 3. Source of truth

Separate factual state from authority:

- **For factual state**, the live repository wins: actual branch, commit, worktree, diff and files. A stale handoff or status snapshot must be corrected to match live Git.
- **For what is allowed**, approved task specifications and applicable repository rules govern. A newer commit or handoff cannot silently override an Owner-approved rule or gate.
- **For task continuity**, use the latest task handoff under `docs/handoff/`, then the workstream schedule and `docs/PROJECT-STATUS.md` snapshot.
- Chat history is context only and may be incomplete; it cannot override current files or approved rules.

A status file is a snapshot, not a substitute for checking Git. Before resuming work, verify the current branch, HEAD, dirty state and relevant handoff.

## 4. Branch and worktree isolation

- One implementation task or coherent feature uses one dedicated branch and worktree.
- Never have two writers editing the same worktree concurrently.
- Reviewers use a read-only view of a fixed base/head diff.
- Keep T15/V3.0, V0.2, and future release work separate unless an approved integration task explicitly combines them.
- Do not switch a worktree to another task merely to save setup time.
- Do not push, merge, rebase shared branches, or alter `main` unless the Owner explicitly authorizes that operation.
- Before committing, inspect `git status`, staged diff and `git diff --check`.

## 5. Project rules and authority

This protocol does not override applicable repository rules and approved task specifications, file ownership, privacy rules, image-generation quotas, or Owner gates. Where a generic lane description conflicts with a project rule, the project rule wins until the Owner explicitly changes it.

In particular:
- Preserve the existing model-cast C1–C8/C11 workflow and its approved gates unless a new spec authorizes changes.
- Image generation requires the existing explicit quota/authorization checks; this protocol grants no image-generation budget.
- Private assets, original images, credentials, vendor code and external output directories remain subject to their existing restrictions.
- A code author cannot count their own review as independent review.

## 6. Handoff contract

Every meaningful task ends with a concise handoff in `docs/handoff/` containing:

- Task name and date; do not publish private client data in handoffs.
- Repository, repository-relative worktree path, branch, base commit and final commit (never personal absolute paths).
- Files changed and a short description of behavior changes.
- Tests actually run, exact commands and relevant output; label older results as historical.
- Independent review status and findings (or explicit blocker).
- Remaining work, risks and Owner decisions required.
- Image-generation accounting if applicable; keep real account ledgers and private receipts outside the public repository. Otherwise state `0 images generated`.
- Explicit statement of whether push/merge occurred (normally no).

Never claim a test, review, build, artifact or Owner acceptance that has not actually happened.

## 7. Conversation lifecycle

### Start

1. Read the task's `START-HERE` handoff.
2. Verify current Git branch, HEAD, worktree and dirty state.
3. Read the approved spec and only the relevant project rules/files.
4. Report current state, completed work, blockers and the next bounded action.
5. Do not reimplement work already present in Git.

Suggested start prompt:

> 接手 model-cast 的 [任务/工作线]。先读取 [START-HERE 路径]，核对 Git 分支、HEAD、工作区和实际 diff。以仓库文件与 handoff 为准，不依赖旧聊天历史，不重复实现。先报告状态和待办，再按已批准规格执行。未经授权不 push、不 merge、不生图。

### End or pause

Before ending a meaningful work session:
1. Commit coherent completed changes, or explicitly list uncommitted changes and why they remain.
2. Update the task handoff and schedule/status evidence.
3. Record exact tests and review state.
4. State one concrete next action.

Suggested end prompt/report fields:

> 当前分支/commit；工作区状态；本次完成；测试命令和实际结果；审查状态；未完成事项；下一步；push/merge/生图状态。

## 8. Review and release gates

- Review is performed against a fixed commit range and exact source diff.
- Findings are classified Critical / Important / Minor and include file/line plus rationale.
- Critical and Important findings must be resolved or explicitly accepted by Owner before release acceptance.
- After review fixes, rerun affected tests and record the new commit.
- Owner acceptance is separate from automated tests and independent review.
- Release/merge occurs only after explicit Owner approval.

## 9. Keep the process lightweight

- Four lanes are enough; do not create a new conversation for every tiny task.
- One progress source per workstream; checklists define acceptance, schedules track status.
- Prefer one canonical `START-HERE` per active task, not multiple competing summaries.
- Do not duplicate full specs in handoffs; link to the approved spec and summarize only task-specific decisions.
- When a conversation is blocked, continue from Git/handoff in a fresh conversation rather than repeatedly reloading a long history.

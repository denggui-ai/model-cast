# Handoff: model-cast architecture review — README, C10 and final deliverables

**Date:** 2026-11-09  
**Repository:** `denggui-ai/model-cast`  
**Target branch:** `main`  
**Purpose:** transfer the current product/documentation issues to a new conversation for an independent architecture-level review and decision.

> **Important instruction for the next conversation:** Act as an independent product architect. Re-read the source files and current GitHub state. Do not assume the previous assistant's proposed fixes are correct. First analyze and make a decision; do not edit files, create images, open PRs, merge, or change packages until the Owner approves the proposed direction.

## 1. Owner's latest request

The Owner is dissatisfied with the current README and with repeated attempts to make it more presentable. The Owner has explicitly asked for the current findings to be written down and handed to a new conversation, where the assistant should act as an architect and independently analyze before deciding.

The next conversation must not simply execute the previous assistant's four proposed fixes. It must reassess:
- What is the actual product and final deliverable?
- What should the public README communicate and visually demonstrate?
- What is the correct role of C6, N2 and C10?
- Is C10 genuinely integrated into the Skill's user-facing workflow, or is it currently only a repository asset/documentation supplement?
- Which documentation statements are stale, contradictory, or misleading?
- What is the smallest correct change set?

## 2. Current project facts

### Main product

model-cast creates an original adult fictional AI fashion model, obtains Owner approval of the identity, and prepares a reusable visual reference package for downstream AI work.

The primary deliverable is the **model and her identity/model-view reference package**, not a grey mannequin and not a collection of engineering documents.

### Visual assets and responsibilities

- **C6:** the actual AI model's face identity, body proportions and model views. Current showcase includes a face reference, approved front full-body reference, a 12-view overview and three selected action/expression examples.
- **N2:** 12 grey, faceless, hairless and clothing-free 3D mannequin views. It communicates camera direction, view angle, framing and crop.
- **C10:** three optional grey, faceless 3D mannequin references: side walking, side sitting, hands-in-pockets standing. It communicates body action and limb/pose relationships.
- **N2 and C10 use the same grey 3D mannequin visual language, but have different functions:** N2 = camera/framing; C10 = action/pose.
- **The grey 3D mannequins are supporting guides, not the main model deliverable.**
- The approved direction is grey 3D mannequins, not black line-art drawings and not a parallel white-mannequin/line-art family. Do not reopen this choice without new Owner authorization.

### Downstream and release boundaries

- ChatGPT/Codex multi-file library and a separate Lookset D2 adapter exist.
- model-cast does not itself provide a bundled image-generation model, guarantee garment fidelity, or produce commercial photography.
- C10 was added after v0.2.0 to current `main`; it is not part of the immutable v0.2.0 release archive or existing Owner-specific V3.0 seller packages.
- Do not overwrite or regenerate existing V3.0 packages.
- Codex local-folder-to-image-tool end-to-end handoff remains unverified.
- Strict/independent identity preservation is not verified. ChatGPT pose-generation examples exist, but do not overstate them as biometric identity validation.

## 3. Existing public assets to inspect and reuse

Use these exact repository assets as the source for any visual presentation analysis. Do not use generic stock imagery, web-search thumbnails, invented substitutes, or new image generation.

- `docs/assets/showcase/yuning-face-identity.png`
- `docs/assets/showcase/yuning-fullbody-front.png`
- `docs/assets/showcase/yuning-c6-angle-overview.png`
- `docs/assets/showcase/n2-grey-mannequin-camera-guide.png`
- `docs/assets/c10/C10-01-Walk-Side.png`
- `docs/assets/c10/C10-02-Sit-Side.png`
- `docs/assets/c10/C10-03-Hands-In-Pockets.png`

The Yuning showcase images are AI-generated fictional imagery, not photos of a real person; public showcase use is Owner-authorized.

## 4. Concrete inconsistencies found in the current source

These are verified source observations, not yet a decision about how to fix them.

### A. Skill source contradicts shipped C10

In `skills/model-cast/SKILL.md`:
- The workflow introduction says the Skill executes C1–C8 and C11 (including N2), but does not list C10.
- Later, the C8 package description says: **“C10 人物姿势线稿当前未实现，不得宣称已交付。”**

This is stale and conflicts with the actual C10 PNG/SVG assets merged to `main` in PR #7, with `docs/C10-USAGE.md`, and with the current README.

Architectural question: Is C10 supposed to be a user-facing optional Skill capability, a post-workflow reference supplement that users manually select, or merely a repository-level add-on? The next architect must decide this from the approved product scope and Owner intent before changing SKILL.md. Simply replacing the stale sentence may be insufficient if the actual workflow/instructions still omit how C10 is selected and handed to the image tool.

### B. C10 documentation title and terms remain stale

`docs/C10-USAGE.md` begins:
- Title: `C10 人物姿势线稿：使用规范与最小补充方案`
- Multiple phrases still call C10 a “线稿”, including the attachment boundary and acceptance criteria.

But the accepted deliverable is the grey, faceless 3D mannequin style matching N2. The file body already describes that style correctly in several places, so title/terminology are inconsistent.

Architectural question: choose one accurate, user-friendly Chinese and English naming convention (e.g. “灰色 3D 人偶姿势参考”) and apply only where needed; do not expand the document unnecessarily.

### C. README presentation remains unaccepted

PR #13 and PR #16 are merged, but the Owner has explicitly rejected the presentation. Current README still has:
- Technical/project language before the user sees a compelling result.
- Repeated descriptions of C6/N2/C10 and technical responsibilities.
- Status/validation and host limitations taking up too much of the main product narrative.
- A weak distinction between the repository's public source/showcase assets and the Owner's complete V3.0 seller package.
- Insufficiently direct explanation that the main deliverable is the original AI model and reusable identity/model-view package; grey mannequins only support camera and pose communication.

The previous assistant tried to fix this by adding a “final deliverables” list and image links, then a more explicit section. The Owner still rejected the overall presentation. Do not repeat this same pattern with more bullets/tables/headings.

Architectural question: what is the smallest visual-first README structure that communicates the product in 10–20 seconds? Consider an editorial/product showcase, not an engineering report. Use the actual images above. The first screen should make the finished AI model and the usable reference deliverable unmistakable; then visually explain N2/C10 as supporting guides; only after that provide a concise “how to use” path and a compact limitations/footer section.

### D. Public repository vs generated seller package boundary

README currently risks implying that cloning the source repository gives users the complete Owner-specific V3.0 seller package. It does not. The repo contains source, builder, public showcase assets and reference guides; the complete seller pack is generated for a specific model/project and the Owner's V3.0 package remains separate.

The next architect should define a single clear sentence distinguishing:
1. what is directly in this public repository;
2. what the Skill/build workflow creates for a user's own model;
3. what is private/Owner-specific and is not distributed in this repository.

## 5. Previous handoff and PR history

- `docs/HANDOFF-README-PRODUCT-PRESENTATION.md` was created after the Owner asked for a new-conversation handoff. It correctly states the main product and desired direction, but it predates the latest detailed source audit and should be supplemented by this document.
- PR #7: C10 grey mannequin assets merged.
- PR #9: C10 ChatGPT validation notes merged.
- PR #10: post-v0.2.0 history wording corrected.
- PR #11: initial bilingual README merged.
- PR #13: first deliverables-first README edit merged.
- PR #16: README product-showcase revision merged as `dd6e1c4f178ddf1ff78d6df64b740fb7053652f2`.
- The Owner explicitly rejected the presentation even after PR #16. Merge status is not Owner acceptance.

## 6. Required next-conversation procedure

1. Read this handoff completely.
2. Fetch and read live `main` versions of:
   - `README.md`
   - `README.zh-CN.md`
   - `skills/model-cast/SKILL.md`
   - `docs/C10-USAGE.md`
   - `docs/PROJECT-STATUS.md`
   - `docs/RELEASE-NOTES.md)
3. Inspect the actual referenced images, especially C6 contact sheet, N2 guide and all three C10 images.
4. Separate:
   - confirmed facts from repository sources;
   - Owner intent from the conversation;
   - architectural interpretation/recommendation.
5. Deliver an independent diagnosis and a concise proposed content/visual outline for Owner approval.
6. Explicitly state whether C10 is a Skill capability or a supplementary manual asset and explain why.
7. Do not make changes until the Owner approves the plan.

## 7. Strict non-goals until new approval

- No image generation.
- No new line-art or mannequin assets.
- No additional poses.
- No changes to C6/N2/C10 source images or specifications.
- No changes to V3.0 packages.
- No changes to v0.2.0 tag/release.
- No code refactor or test framework.
- No README edits or merges before architectural proposal approval.

**Handoff outcome sought:** a fresh architect-level product and documentation decision based on the real source and shipped assets—not another round of premature README edits.

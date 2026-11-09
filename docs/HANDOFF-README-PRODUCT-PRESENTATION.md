# Handoff: model-cast README product presentation

**Date:** 2026-11-09  
**Repository:** `denggui-ai/model-cast`  
**Current public branch:** `main`  
**Purpose:** hand off the README presentation problem accurately. This is not authorization to redesign the product, generate images, alter seller packages, or create new product assets.

## 1. Why this handoff exists

The Owner explicitly rejected the current README presentation, even after PR #13 and PR #16. The problem is not whether the README is bilingual or whether it contains links. The problem is that the page still reads like an engineering/project report instead of showing the product and its finished outputs.

The Owner's criticism, in substance:
- The final deliverables are not being shown clearly enough.
- The README over-emphasizes engineering structure, tables, status language, and implementation detail.
- The product's actual distinguishing value has not been explained correctly.
- The question of line art versus grey 3D mannequins has been handled carelessly.

Do not treat the previous assistant's claim that PR #16 solved the problem as Owner acceptance. **PR #16 is merged, but the presentation is not accepted.**

## 2. Product truth — use this as the source of truth

model-cast's core output is **an original adult fictional AI fashion model with an approved identity, plus a reusable visual reference package for downstream AI work**.

The main product is the model and her visual identity/reference library. The grey mannequins are supporting visual guides, not the model itself.

### Actual deliverables

1. **C6 — the model's identity and model-view library**
   - Face identity reference and approved front full-body reference.
   - 12 model views.
   - Three selected action/expression examples (walking, sitting, natural smile).
   - The public Yuning example is AI-generated fictional imagery, not a real person; public showcase images have Owner authorization.

2. **N2 — camera/framing guide**
   - 12 grey, faceless, hairless, clothing-free 3D mannequin views.
   - Used to express camera direction, view angle, framing and crop.
   - It is not an identity reference and does not define the action pose.

3. **C10 — action/body-pose supplement**
   - Three optional grey 3D mannequin references: side walking, side sitting, hands-in-pockets standing.
   - Same grey mannequin visual language as N2.
   - C10 controls action/limb arrangement; N2 controls camera/framing. Different jobs, same visual representation.
   - C10 is post-v0.2.0 and lives on current `main`; it is not in the immutable v0.2.0 release archive or existing V3.0 seller package.

4. **Practical handoff materials**
   - Four-image lightweight identity set.
   - Full multi-file AI library with asset index and START-HERE guidance.
   - model-cast Skill source.
   - Separate Lookset D2 adapter/export path.

### Line art vs 3D mannequin — final decision

For N2 and C10, the approved direction is **grey, faceless 3D mannequins**, not black line-art drawings and not a parallel white-model/line-art asset family.

Why:
- A neutral 3D mannequin communicates spatial orientation, limb articulation, depth and front/back relationships more clearly than a flat contour drawing.
- Removing face, hair and clothing avoids competing with C6 identity and avoids implying garment design.
- Reusing one grey mannequin visual language across N2 and C10 reduces user confusion.
- N2 and C10 are not duplicate functions: N2 is camera/framing; C10 is action/pose.

Do not re-open this decision without new Owner authorization.

## 3. Relevant existing public assets

Use the actual repository assets, not invented imagery, external search thumbnails, or newly generated substitutes.

- Face identity: `docs/assets/showcase/yuning-face-identity.png`
- Approved front full-body: `docs/assets/showcase/yuning-fullbody-front.png`
- C6 contact sheet: `docs/assets/showcase/yuning-c6-angle-overview.png`
- N2 guide: `docs/assets/showcase/n2-grey-mannequin-camera-guide.png`
- C10 walking: `docs/assets/c10/C10-01-Walk-Side.png`
- C10 sitting: `docs/assets/c10/C10-02-Sit-Side.png`
- C10 hands in pockets: `docs/assets/c10/C10-03-Hands-In-Pockets.png`

The Owner-provided screenshots in the preceding conversation show how the current GitHub README renders. They are feedback evidence, not replacement product assets.

## 4. What is wrong with the current README approach

PR #16 moved deliverables higher and embedded more image links, but the resulting page still contains:
- Repeated project/showcase explanations.
- Too many tables and engineering status descriptions near the user-facing story.
- A document structure that feels like implementation documentation rather than a product showcase.
- No sufficiently clear, immediate statement that the **main output is the finished AI model and its reusable model-view package**; N2/C10 mannequins are supporting references.
- No simple visual narrative connecting C6 identity -> model views/actions -> N2 camera guide -> C10 pose guides -> downloadable/usable package.

Do not solve this by adding more headings, matrices, architecture vocabulary, or process descriptions.

## 5. Desired README experience

A first-time visitor should understand the project within roughly 10–20 seconds, mainly by looking at images.

Recommended presentation order:

1. **One-sentence product promise** — create an original AI fashion model and deliver her reusable visual reference package.
2. **Large C6 result showcase** — show the face identity + approved full-body image + C6 multi-view contact sheet. This is the hero output and should dominate the page.
3. **What is included in the deliverable** — concise, visual grouping:
   - Model identity and 12 views + 3 action/expression examples (C6).
   - Camera/framing guide (N2, 12 grey 3D mannequin views).
   - Optional action/pose guides (C10, 3 grey 3D mannequin poses).
   - Practical AI handoff library (lightweight 4-image set and full multi-file library).
4. **How the pieces work together** — one simple explanation: C6 = who the model is; N2 = where/how the camera sees her; C10 = what action the body performs. Product image is a separate user-provided downstream input.
5. **How to use/get the deliverable** — short, actionable route to the Skill and package builder/usage instructions. Do not imply the repository contains a ready-to-download owner-specific V3.0 package; it contains public source/build workflow and authorized showcase examples.
6. **Limitations and technical details** — short and lower on page: image generation is provided by host; garment fidelity is not guaranteed; Codex end-to-end handoff and strict identity preservation remain unverified.
7. **Language switch** — English and Simplified Chinese should have matching structure and equivalent facts.

Visual guidelines:
- Prefer actual repository images embedded at useful display sizes over tables of links.
- Use a contact sheet for C6 and N2 if it tells the story clearly; do not add redundant images merely to fill space.
- Show the three C10 images together as a simple trio.
- Avoid generic web-search pictures or image placeholders that are not the project's actual assets.
- Avoid overengineering: no new site, docs framework, design system, test harness, or release process.

## 6. Facts and limitations that must remain accurate

- v0.2.0 is the formal source release. It remains unchanged.
- C10 was merged after v0.2.0 in PR #7; do not imply it is part of the v0.2.0 archive.
- Existing V3.0 seller packages must not be modified or overwritten.
- C6 is the identity authority.
- N2 is camera/framing guidance.
- C10 is optional action/pose guidance.
- model-cast is not an image-generation service, garment try-on system, clothing-design tool, or commercial photography pipeline.
- ChatGPT recognized 16/16 assets in the direct multi-file POC. That does not prove every selected image reaches the image tool as a reference.
- Codex local-folder-to-image-tool end-to-end handoff remains unverified.
- C10 pose-generation examples exist; strict identity preservation is not independently/biometrically verified.
- Do not describe the 3D mannequins as the product's main deliverable. The original AI model and reusable visual package are the main deliverable; mannequins support camera and pose communication.

## 7. Current GitHub history / work already done

- PR #7: C10 grey mannequin supplement merged.
- PR #9: C10 ChatGPT validation notes merged.
- PR #10: post-v0.2.0 history wording corrected.
- PR #11: initial bilingual README merged.
- PR #13: first deliverables-first README edit merged.
- PR #16: added deliverables section and actual C6/N2/C10 image links; merged as `dd6e1c4f178ddf1ff78d6df64b740fb7053652f2`.

Important: PR #16 being merged does **not** mean the Owner accepted the result. The Owner explicitly said the presentation remains unsatisfactory and asked for handoff.

## 8. Next operator's task

Do not start by editing files. First read this handoff and inspect the live `main` README in both languages. Then produce a concise proposed page outline and visual order for Owner review before making another README edit.

If later authorized to implement:
- Work on a separate branch and change only `README.md` and `README.zh-CN.md`.
- Reuse the existing assets listed above.
- Keep English and Chinese visually/structurally aligned.
- Check every relative image link against an existing file.
- Do not alter SKILL.md, C10/N2 assets, V3.0 packages, code, tests, tags or Release.
- Do not merge without explicit Owner approval.

## 9. Explicit non-goals

- No new image generation.
- No new mannequin/line-art assets.
- No new poses or expanded feature scope.
- No changes to C6, N2, C10 specifications or source assets.
- No V3.0 package regeneration/overwrite.
- No new software release.
- No extra documentation architecture or automated visual testing system.

**Handoff conclusion:** The product assets and source implementation are already present. The remaining issue is the quality of the public-facing product explanation and visual presentation. The next operator should fix the communication, not redesign or redevelop model-cast.

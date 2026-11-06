# model-cast V0.2 — Face Casting Design Decisions

**Status:** Proposed design baseline  
**Target:** model-cast Codex Skill  
**Branch:** `docs/model-cast-v0.2-design-decisions`  
**Scope:** Product and Skill design decisions only. This document does not change runtime code or claim that proposed capabilities are implemented.

## 1. Product direction

model-cast is an **independent AI virtual model design Skill for Codex**.

Its primary job is to help a user design, refine, and approve a high-quality fictional adult virtual model, then save the accepted final portrait and its relevant identity package.

Caiguang remains an optional downstream handoff for product photography. It is not the center of model-cast's product identity.

**Product promise:** turn natural-language creative direction into a well-designed virtual model through guided face casting, controlled image iteration, and explicit user acceptance.

## 2. Runtime and architecture constraints

The supported product workflow is Codex with its host-provided native `image_gen` capability.

- Use the host's native image generation/editing capability for image creation and edits.
- Keep model-cast responsible for design reasoning, prompt construction, iteration planning, user feedback, acceptance, and local asset workflow.
- Keep the existing private workflow, authorization ledger, immutable source-image handling, and package export boundary.
- Do not assume that third-party Diffusers/ComfyUI models or APIs can directly control the host's native `image_gen`.
- Optional local image-analysis scripts may be invoked by Codex when installed, but missing analysis dependencies must not block ordinary model design or image generation.

This is a Codex Skill workflow, not a new image-generation model or a requirement to operate a separate GPU image platform.

## 3. Adopted face-casting principles

The supplied six-page article, *数字人第一步：先做定妆照*, is the source for the following design ideas. They are adapted as flexible creative heuristics, not universal facial beauty standards.

### 3.1 Signature Feature — establish a face's visual anchor

Identify the main facial feature the user most wants to preserve. Treat it as a high-priority design anchor during subsequent edits.

- It may be an eye shape, brow-eye relationship, nose shape, lip shape, or contour characteristic.
- One primary anchor may have supporting features; do not force every person to have only one defining feature.
- Do not turn the article's example (almond eyes) into a default model-cast beauty template.

### 3.2 Facial Harmony — evaluate features as a composition

Do not optimize eyes, nose, lips, and jaw independently. Consider their relative visual weight, spacing, negative space, and transitions.

Useful review relationships include:
- eye shape, eye spacing, and nose width;
- nose base, upper lip, lower lip, and chin spacing;
- cheekbone-to-cheek-to-jaw transition;
- facial width/height and the relative scale of features.

This is an aesthetic reasoning framework, not an automatic beauty score.

### 3.3 Independent Feature Attributes — disambiguate edits

Translate vague whole-feature requests into the specific property the user intends to change.

Examples:
- Lips: upper/lower lip thickness, horizontal mouth width, cupid's bow.
- Nose: bridge height/straightness, tip projection/rotation, alar width.
- Eyes: shape, visible size, interocular distance, eyelid opening, canthal direction.
- Chin: length, width, roundness/pointedness.
- Face contour: cheek fullness, jaw width, contour transition.

Do not interpret "make the mouth smaller" as permission to change both lip thickness and mouth width unless that is what the user means.

### 3.4 Contour Transition — smooth the shape before changing dimensions

When a contour feels abrupt, first consider the transition between cheekbone, cheek, jaw, and chin. Treat contour shape, face width, and chin length as distinct edit dimensions.

### 3.5 Shape Before Proportion — settle form before placement

Recommended sequence:
1. Establish feature and contour shapes.
2. Review harmony and spacing.
3. Adjust feature positions and overall proportions only after the shapes are reasonably settled.

The article's three-part face and one-eye-width spacing references may be used as observation aids only. They are not mandatory ratios or a universal standard of attractiveness.

### 3.6 Single-Objective Iteration — one primary change per round

Each image-edit round should have one clearly stated primary objective.

Every round should specify:
- **Change:** the intended primary change.
- **Preserve:** the accepted features and image properties to retain.
- **Allowed coupling:** any necessary secondary changes that are reasonably connected to the primary edit.
- **Do not change:** unrelated features and presentation dimensions.

This is not a claim that the image model will modify only the named region. Results must be inspected for collateral changes.

### 3.7 Change Verification — inspect side effects after every edit

After each returned image, compare it with the prior accepted reference and the current edit request.

Review:
- whether the requested change occurred;
- whether the signature feature remains recognizable;
- whether supposedly preserved features changed unexpectedly;
- whether facial harmony improved or degraded;
- whether local artifacts, texture damage, or unnatural transitions appeared.

The assistant must not claim identity preservation or visual verification merely because the prompt requested it. User acceptance and technical/file validation are separate states.

### 3.8 Separate Visual Dimensions — do not mix unrelated changes

Treat these as distinct edit dimensions:
- facial geometry;
- apparent adult age presentation;
- hair and makeup;
- lighting and color;
- camera angle, lens, and framing;
- expression and gaze;
- clothing and styling.

Unless the user explicitly requests a combined change, do not change several dimensions in the same iteration. In particular, do not mix face-geometry changes with lighting or camera-angle changes when trying to diagnose a specific facial edit.

## 4. Recommended user workflow

1. **Understand the brief:** derive the intended model use, style, mood, explicit constraints, and exclusions from natural language. Separate user requirements from assistant suggestions and unknowns.
2. **Choose a face direction:** propose or clarify the main facial direction and signature feature. Do not impose a default face template.
3. **Generate a first candidate:** use native Codex `image_gen` only when the user has authorized generation.
4. **Review the face:** assess feature harmony and identify the most important mismatch.
5. **Iterate one primary objective at a time:** state what changes, what stays, and what may be coupled.
6. **Inspect the returned image:** report what appears successful, what changed unintentionally, and what remains unresolved.
7. **Obtain user acceptance:** a direction being approved is not the same as accepting a generated image.
8. **Save the accepted result:** preserve the original accepted image, source/provenance, confirmed scope, and relevant package data through the existing private workflow.

## 5. Technology adoption decisions

| Technology | V0.2 decision | Reason |
|---|---|---|
| PDF-derived face-casting principles | Adopt now in Skill guidance | Directly improves design reasoning and iteration discipline |
| Codex native `image_gen` | Keep as the image-generation/editing path | Matches the actual runtime environment |
| Face Alignment | Do not make a dependency now; reconsider only if measurement is a demonstrated bottleneck | Landmark detection measures geometry but does not judge aesthetics or perform edits |
| Face Parsing / BiSeNet | Defer | Adds model/runtime dependencies; useful only when reliable region masks become a concrete need |
| PhotoMaker / PuLID / InstantID / InfiniteYou | Do not integrate into the current Codex-native workflow | Separate model pipelines cannot be assumed to control host `image_gen`; model and weight licenses also need review |
| Caiguang package handoff | Retain as optional integration | Useful downstream, but not the primary product identity |

### Why Face Alignment is deferred

Face Alignment can estimate 2D/3D landmarks and support repeatable measurements such as eye spacing or mouth-corner distance. It cannot determine whether a face is beautiful, whether features are aesthetically harmonious, or what edit best matches a user's taste. Landmark estimates can also be unreliable with pose, occlusion, makeup, and image quality.

Therefore it is not a required V0.2 dependency. Revisit it only after real model-cast use shows repeated, material problems with proportion measurement that cannot be handled adequately by visual review.

## 6. V0.2 implementation scope

Recommended initial work:
1. Add a dedicated `references/face-casting.md` containing the principles in Section 3.
2. Update `references/natural-language-design.md` to route facial-design and edit feedback through those principles.
3. Update `SKILL.md` to reference the new face-casting guidance at the relevant design/edit stages.
4. Keep `private-workflow.md`, authorization, immutable source handling, and save/export behavior unchanged unless a separately reviewed need arises.
5. Add instruction-following eval scenarios for signature-feature preservation, disambiguating feature attributes, single-objective edits, and side-effect review.

Out of scope for this initial V0.2 design:
- installing Face Alignment or Face Parsing;
- adding PhotoMaker, PuLID, InstantID, or another local image-generation engine;
- automatic beauty scoring or a universal ideal-face ratio;
- claiming pixel-level preservation or guaranteed same-identity results;
- rewriting the private Python execution workflow.

## 7. Acceptance criteria for the Skill guidance

The revised Skill should:
- identify the user's desired visual anchor without forcing a stock beauty template;
- distinguish explicit user requirements, assistant suggestions, and unknowns;
- translate ambiguous facial edits into independent feature attributes when needed;
- plan one primary edit objective per round;
- state preservation constraints and acknowledge that image models may still alter surrounding regions;
- inspect actual returned images for target changes and collateral changes;
- keep geometry, styling, lighting, camera, and expression changes separate unless requested;
- distinguish candidate, user-approved, and technically verified states;
- preserve the existing generation authorization and private-save safeguards.

## 8. Evidence and limitations

The face-design heuristics in this document are derived from the supplied article *数字人第一步：先做定妆照* (six pages, especially pages 2–5).

The Codex-only runtime constraint and existing private workflow are based on the current model-cast repository documentation and code.

The technology deferral decisions are architecture recommendations, not benchmark results. No new model integration or image-quality experiment has been performed as part of this document.

---

**Decision summary:** For V0.2, improve the design intelligence and controlled iteration of model-cast first. Keep Codex native `image_gen`; do not add Face Alignment, Face Parsing, or separate diffusion identity models as required dependencies at this stage.

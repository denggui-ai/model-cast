# C10 grey 3D mannequin pose references (post-v0.2.0 supplement)

Three optional pose references in the same grey, faceless mannequin visual system as N2:

- `C10-01-Walk-Side.png` — side-view walking stride.
- `C10-02-Sit-Side.png` — side-view seated pose.
- `C10-03-Hands-In-Pockets.png` — front-facing relaxed stance with hands placed at the hip/pocket position.

SVG files are the editable vector sources; PNG files are the upload-ready references.

## Use

Select one C10 image only when C6 does not already show the required pose. C6 controls identity and body proportions; C10 controls pose and limb placement. N2 is optional and controls camera/framing only. Add a user-provided product image only for a downstream product-image task; model-cast does not guarantee garment fidelity or produce the final image.

C10 is a standalone optional reference supplement. It is not a stage in the standard model-cast Skill workflow, is not included in the standard 16-image AI library, and is not part of Lookset D2.

## Validation status

- C10-01: one user-provided ChatGPT result clearly showed side-view walking. This supports pose execution, but does not independently prove identity preservation.
- C10-02 and C10-03: each has a ChatGPT generation result; both were visually checked and show the requested pose.
- Codex end-to-end handoff: not tested; this does not block use of the standalone supplement.

This post-release supplement does not change v0.2.0, does not overwrite existing V3.0 seller packages, and is not included in the Lookset D2 contract.

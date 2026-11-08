# Complete AI Model Library | Multi-file upload

For ordinary ChatGPT and Codex use. In a new conversation, select all images, this guide, and `asset-index.json` in this folder and upload them together. Then send:

> Read START-HERE.md and asset-index.json, identify the model identity and visual references, and select the smallest relevant set of identity, angle, and action references for each natural-language task. Preserve the model's identity. Tell me which files you selected. Do not treat the N2 mannequin as the model, and do not pass every image to an image tool indiscriminately.

## Roles

- `01`: primary face identity anchor.
- `04`: primary front full-body and body-proportion anchor.
- `06` and `07`: side and back body references; the back view has no face and cannot prove facial identity.
- `02`, `03`, `05`, `08`–`12`: supplementary angles. Images without a visible face are not facial identity evidence.
- `13`–`15`: accepted walking, sitting, and natural-smile examples; use only when relevant.
- `16`: N2 grey faceless mannequin camera-angle/framing guide only. It is not the model, a pose drawing, a clothing image, or an image-edit base.

## Usage limits

1. Identify files using both `asset-index.json` and visual content. Filenames are labels, not proof.
2. For a new pose, usually select `01` plus the most relevant body/angle reference. Add `13` or `14` for relevant action tasks, and `15` for expression tasks.
3. Use N2 `16` only to understand camera direction and framing. Never substitute it for a real model image.
4. Reading or selecting an attachment does not prove a downstream image-generation/editing tool received it. Before execution, confirm that the selected images were actually passed as references. If the host cannot pass them, explain the limitation and ask the user to attach the required images directly.
5. Do not claim C10 pose line art is included; it is not delivered in this version.
6. This library supports model identity and visual references. It does not provide clothing design, garment try-on, or commercial photography workflows. Users must supply product facts separately; Lookset users should use the separate D2 adapter package.

## Suggested opening message

“Please understand this model library first. For each later creative or photography request, choose the most suitable reference images and briefly explain why. Only generate or edit after confirming that the image tool can actually receive those selected references.”

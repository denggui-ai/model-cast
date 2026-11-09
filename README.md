# model-cast

**Create an original AI fashion model, establish a reusable identity, and hand off a visual reference library.**

[简体中文](README.zh-CN.md) · **English**

model-cast is an open-source Skill for creating original adult fictional e-commerce models and preparing their reusable visual references.

It is **not** an image-generation service, virtual try-on system, clothing-design tool, or commercial photography pipeline. Final image generation and garment fidelity depend on the downstream tools and the user's workflow.

## Final deliverables

This repository gives you the Skill, its reference workflow, and a public example of the resulting assets:

- **The model-cast Skill** — casting, identity approval, asset preparation, and handoff workflow in [`skills/model-cast/`](skills/model-cast/).
- **C6 model reference set** — 12 model views plus three selected action/expression examples. The [Yuning overview](docs/assets/showcase/yuning-c6-angle-overview.png) shows the delivered view set.
- **N2 camera/framing guide** — 12 grey, faceless mannequin views for camera direction and crop: [view the N2 guide](docs/assets/showcase/n2-grey-mannequin-camera-guide.png).
- **C10 pose supplement** — three optional grey mannequin pose references: [side walking](docs/assets/c10/C10-01-Walk-Side.png) · [side sitting](docs/assets/c10/C10-02-Sit-Side.png) · [hands-in-pockets standing](docs/assets/c10/C10-03-Hands-In-Pockets.png). These were added after v0.2.0 to current `main`; they are not part of the v0.2.0 release archive or existing V3.0 seller package.
- **ChatGPT/Codex multi-file library workflow** — builder, file index, and upload instructions for handing off the selected visual references.
- **Lookset D2 adapter** — a separate export path for the Lookset workflow.

The Yuning images in this README are an AI-generated fictional model example, not a photograph of a real person. The Owner authorized the selected images for this public showcase.

## Use the references

| Asset | Use it for |
|---|---|
| **C6** | Model identity, face, and body proportions |
| **N2** | Camera direction, framing, and crop |
| **C10** | Optional action and limb-pose guidance |
| **Product image** | User-provided product appearance reference for downstream generation |

Use the smallest relevant reference set. C6 remains the identity authority; C10 only guides pose; N2 only guides camera/framing. None of these assets guarantees garment fidelity in the final generated image.

## Quick start

### 1. Install

```sh
git clone https://github.com/denggui-ai/model-cast.git
cd model-cast
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
shasum -a 256 -c SHA256SUMS
```

### 2. Install the Skill

Install only `skills/model-cast` into your supported agent skill directory. Back up any existing installation first; this repository does not overwrite an existing installation automatically.

### 3. Start a project

> Use model-cast to create an original adult virtual fashion model for my product line. First inspect the inputs and propose the casting plan; do not generate images until I approve.

Image generation requires the host's native image capability, account access, and explicit user authorization. This Skill does not bundle an image model or provide generation credits.

## Example: Yuning

| Face identity reference | Approved front full-body reference |
|---|---|
| ![Yuning face identity](docs/assets/showcase/yuning-face-identity.png) | ![Yuning front full-body](docs/assets/showcase/yuning-fullbody-front.png) |

The C6 overview documents 12 model views and three action/expression examples. Owner visual feedback accepted the 13 supplementary outputs. Views without a visible face are body/framing references, not facial-identity proof.

![Yuning C6 model-view overview](docs/assets/showcase/yuning-c6-angle-overview.png)

### N2 camera/framing guide

N2 contains 12 faceless, hairless, clothing-free grey mannequin views. It communicates camera direction and framing/crop; it is not Yuning, a clothing drawing, or an image-edit base.

![N2 grey mannequin camera guide](docs/assets/showcase/n2-grey-mannequin-camera-guide.png)

## Downstream workflows

### ChatGPT or Codex

The seller pack includes `4_完整AI资料库（多文件上传）` / `4_AI_Model_Library_MultiUpload`. Upload the files together when using the full library. It contains 12 model views (including four core identity anchors), three accepted action/expression examples, N2, `START-HERE.md`, and `asset-index.json`.

The index explains each asset and helps the AI select the smallest relevant reference set. A four-image lightweight set remains available in `2_上传给AI` / `2_Upload_to_AI`.

**Host limitation:** recognizing or selecting an uploaded image does not prove that a downstream image-generation/editing tool received it as a reference. ChatGPT recognized 16/16 assets in a multi-file test, and limited pose-generation checks were performed. Independent identity control from multiple references is not conclusively established. Codex local-folder-to-image-tool handoff remains unverified. If a host cannot pass selected images to its image tool, it must ask for the images to be attached directly rather than claim they were used.

### Lookset D2

Use the separate D2 adapter: P3-2 identity reference, model supplements 01–12, and `model.json`. Do not automatically add N2, C10, or ordinary-user instructions to D2. Lookset owns its separate pose planning, garment editing, photography workflow, and commercial QA.

## What has been verified

- Core model-creation workflow and package scripts: implemented; automated tests passed.
- C6: reference set generated and Owner-reviewed.
- N2: 12-view grey mannequin guide generated and self-checked.
- C10: three pose references are on current `main`; ChatGPT pose-generation examples were recorded. Identity preservation is qualitative, not independently verified.
- ChatGPT multi-file library: recognition test identified 16/16 assets; generation evidence is limited.
- Codex local-folder-to-image-tool handoff: not verified.
- Lookset D2: package structure and readback validated; the complete commercial workflow is not verified.
- Fine local face editing: not established as reliable; the practical nose-tip target was not accepted.

Automated tests validate scripts, manifests, package contents, and synthetic fixtures. They do not prove generated-image quality, identity preservation, garment fidelity, or Owner acceptance.

## Release and project documents

- **Formal source release:** [v0.2.0](https://github.com/denggui-ai/model-cast/releases/tag/v0.2.0). C10 was added later to current `main`; the v0.2.0 tag/archive remains unchanged.
- [Public project status](docs/PROJECT-STATUS.md) · [Release notes](docs/RELEASE-NOTES.md)
- [C10 usage specification](docs/C10-USAGE.md) · [Public POC results](docs/POC-RESULTS.md)
- [Development Protocol](docs/DEVELOPMENT-PROTOCOL.md) · [Project Adapter](docs/PROJECT-ADAPTER.md)

## Validation

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider
git diff --check
```

The verified project snapshot passed 242 automated tests. The full workflow is currently verified on macOS; Python 3.10+ is required, and `crop.py` uses the system `sips` utility.

## License

Original project code and documentation use MIT. Vendored Lookset files retain Apache-2.0 and their upstream notices. Public example images are authorized AI-generated project assets; this does not grant rights to unrelated user assets.

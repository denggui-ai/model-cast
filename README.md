# model-cast

**Create an original AI fashion model, establish a reusable identity, and hand off a structured visual reference library.**

[简体中文](README.zh-CN.md) · **English**

model-cast is an open-source creation-and-handoff Skill for original adult fictional e-commerce models. It guides casting, face/body identity approval, visual-reference preparation, and handoff to downstream AI tools.

It is **not** an image-generation service, virtual try-on system, clothing-design tool, or commercial photography pipeline. Final image generation and garment fidelity depend on the downstream tools and the user's workflow.

## Final deliverables

This repository gives you the Skill, its reference workflow, and a public example of the resulting assets:

- **The model-cast Skill** — casting, identity approval, asset preparation, and handoff workflow in [`skills/model-cast/`](skills/model-cast/).
- **C6 model reference set** — 12 model views plus three selected action/expression examples. The [Yuning overview](docs/assets/showcase/yuning-c6-angle-overview.png) shows the delivered view set.
- **N2 camera/framing guide** — 12 grey, faceless mannequin views: [view the N2 guide](docs/assets/showcase/n2-grey-mannequin-camera-guide.png).
- **C10 pose supplement** — three optional references: [walking](docs/assets/c10/C10-01-Walk-Side.png) · [sitting](docs/assets/c10/C10-02-Sit-Side.png) · [hands-in-pockets](docs/assets/c10/C10-03-Hands-In-Pockets.png).
- **ChatGPT/Codex multi-file handoff workflow** — builder, index, and upload instructions.
- **Lookset D2 adapter** — a separate export path.

C10 was added after v0.2.0 to current `main`; it is not part of the v0.2.0 release archive or existing V3.0 seller package.

## Visual reference system

| Asset | Purpose | Not responsible for |
|---|---|---|
| **C6** | Model identity, face, and body proportions | Specifying a new pose or camera angle |
| **N2** | Camera direction, framing, and crop, using grey faceless mannequins | Model identity or action-pose control |
| **C10** | Optional action and limb-pose references, using the same grey mannequin style | Identity, clothing design, or garment fidelity |
| **Product image** | User-provided product appearance reference for downstream generation | Model identity |

Use the smallest relevant reference set. C6 remains the identity authority; C10 only guides pose; N2 only guides camera/framing. C10 is a post-v0.2.0 supplement on current `main`, not part of the immutable v0.2.0 release archive or the existing V3.0 seller package. See [C10 usage](docs/C10-USAGE.md).

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

Try this prompt:

> Use model-cast to create an original adult virtual fashion model for my product line. First inspect the inputs and propose the casting plan; do not generate images until I approve.

Image generation requires the host's native image capability, account access, and explicit user authorization. This Skill does not bundle an image model or provide generation credits.

## Example: Yuning

Yuning is an AI-generated fictional model, not a photograph of a real person. The Owner authorized the selected images below for this public project showcase.

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

## Capability and validation status

| Area | Current status |
|---|---|
| C1–C8 and C11 model-creation workflow | Implemented; workflow and code checks passed |
| C6 identity approval and visual references | Implemented; final identity approval depends on Owner review |
| N2 12-view grey mannequin guide | Generated and self-checked |
| C10 three-pose supplement | Implemented on current `main` after v0.2.0; ChatGPT pose-generation examples recorded. Identity preservation is qualitative, not independently verified |
| ChatGPT multi-file library | Implemented; recognition test identified 16/16 assets; generation evidence is limited |
| Codex multi-file end-to-end handoff | Not verified |
| Lookset D2 export | Implemented; package structure and readback validated, not the complete commercial workflow |
| Face-casting fine local edits | Not established as reliable; practical nose-tip target was not accepted |

Automated tests validate scripts, manifests, package contents, and synthetic fixtures. They do not prove generated-image quality, identity preservation, garment fidelity, or Owner acceptance.

## Release and project documents

- **Formal source release:** [v0.2.0](https://github.com/denggui-ai/model-cast/releases/tag/v0.2.0). C10 was added later to current `main`; the v0.2.0 tag/archive remains unchanged.
- [Public project status](docs/PROJECT-STATUS.md)
- [Release notes and post-release history](docs/RELEASE-NOTES.md)
- [C10 usage specification](docs/C10-USAGE.md)
- [Public POC results](docs/POC-RESULTS.md)
- [Development Protocol](docs/DEVELOPMENT-PROTOCOL.md)
- [Project Adapter](docs/PROJECT-ADAPTER.md)
- [Third-party notices](skills/model-cast/THIRD_PARTY_NOTICES.md)

## Validation

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider
git diff --check
```

The full automated suite has passed 242 tests on the verified project snapshot. The full workflow is currently verified on macOS; Python 3.10+ is required, and `crop.py` uses the system `sips` utility.

## License

Original project code and documentation use MIT. Vendored Lookset files retain Apache-2.0 and their upstream notices. Public example images are authorized AI-generated project assets; this does not grant rights to unrelated user assets.

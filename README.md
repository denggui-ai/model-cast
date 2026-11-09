# model-cast

**Create an original AI fashion model. Establish her visual identity. Build a reusable reference library.**

[简体中文](README.zh-CN.md) · **English**

model-cast is an open-source Skill for creating original adult fictional fashion models and preparing structured visual references for downstream AI workflows.

It guides casting, identity approval, model-view preparation, and reference handoff. The central deliverable is **the model and her reusable identity/reference set**—not the grey mannequins used to explain camera angles or poses.

## Meet the model

Yuning is an AI-generated fictional model, not a photograph of a real person. The Owner authorized these selected images for this public showcase.

![Yuning — approved front full-body model reference](docs/assets/showcase/yuning-fullbody-front.png)

| Face identity | Full model-view set |
|---|---|
| ![Yuning face identity](docs/assets/showcase/yuning-face-identity.png) | ![C6 model views and action examples](docs/assets/showcase/yuning-c6-angle-overview.png) |

The C6 reference set contains 12 model views and three selected action/expression examples. C6 is the identity source: use it to establish the model's face, body proportions, and accepted model views.

## Supporting visual guides

The model comes first. The grey, faceless 3D mannequins below are optional supporting references; they are not alternative models, identity references, or clothing assets.

### N2 — Camera and framing

![N2 grey 3D mannequin camera guide](docs/assets/showcase/n2-grey-mannequin-camera-guide.png)

N2 communicates camera direction, viewing angle, framing, and crop.

### C10 — Optional pose references

| Side walking | Side sitting | Hands-in-pockets |
|---|---|---|
| ![C10 side walking mannequin](docs/assets/c10/C10-01-Walk-Side.png) | ![C10 side sitting mannequin](docs/assets/c10/C10-02-Sit-Side.png) | ![C10 hands-in-pockets mannequin](docs/assets/c10/C10-03-Hands-In-Pockets.png) |

C10 communicates body action and limb placement when C6 does not already show the required pose. It is an optional, separately selected supplement—not a stage in the standard Skill workflow or part of the current 16-image library package.

**Keep the references distinct:** C6 = who the model is; C10 = how the body moves; N2 = how the scene is framed. Select only what the task needs. See [C10 usage](docs/C10-USAGE.md) for the reference-selection rules.

## What the workflow prepares

The repository includes the model-cast Skill, the multi-file ChatGPT/Codex library builder and index, and a separate Lookset D2 adapter.

The standard AI reference library contains:

- 12 views of the actual model.
- Three selected model action/expression examples.
- One N2 grey-mannequin camera/framing guide.
- `START-HERE.md` and a machine-readable `asset-index.json`.

That is 16 image assets plus the usage guide and index. A lightweight four-image identity set is also prepared for tasks that need fewer references.

### What is in this repository—and what is not

This public repository contains the model-cast Skill, packaging tools, documentation, and public showcase assets. Running the workflow prepares a separate model-specific reference package from your own approved assets. The Owner-specific V3.0 seller package is private and is not included in this repository. C10 is a post-v0.2.0 supplement on `main`; it does not alter the v0.2.0 release archive or existing V3.0 packages.

## Get started

### 1. Install the repository

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

### 3. Start with an approval-first request

> Use model-cast to create an original adult fictional fashion model for my product line. First inspect the inputs and propose the casting plan; do not generate images until I approve.

Image generation requires the host's native image capability, account access, and explicit user authorization. The Skill does not bundle an image model or provide generation credits.

## Downstream use

### ChatGPT and Codex

Upload the files in `4_完整AI资料库（多文件上传）` / `4_AI_Model_Library_MultiUpload` together when using the full library. The index describes each asset and helps the AI select the smallest relevant reference set. Use the four-image lightweight set in `2_上传给AI` / `2_Upload_to_AI` when that is sufficient.

**Reference handoff depends on the host.** Recognizing or selecting an uploaded image does not prove that a downstream image-generation/editing tool received it as a reference. ChatGPT recognized 16/16 assets in a multi-file test, and limited pose-generation checks were performed; independent identity control from multiple references is not conclusively established. Codex local-folder-to-image-tool handoff remains unverified. If a host cannot pass selected images to its image tool, attach the selected originals directly rather than claiming they were used.

### Lookset D2

Use the separate D2 adapter: P3-2 identity reference, model supplements 01–12, and `model.json`. Do not automatically add N2, C10, or ordinary-user instructions to D2. Lookset owns its separate pose planning, garment editing, photography workflow, and commercial QA.

## Scope and validation

model-cast prepares a model identity/reference set and hands it off to other tools. It is **not** an image-generation service, virtual try-on system, clothing-design tool, or commercial photography pipeline. Final image generation and garment fidelity depend on downstream tools and the user's workflow.

| Area | Current status |
|---|---|
| C1–C8 and C11 model-creation workflow | Implemented; workflow and code checks passed |
| C6 identity approval and visual references | Implemented; final identity approval depends on Owner review |
| N2 12-view camera/framing guide | Generated and self-checked |
| C10 three-pose supplement | Available on current `main`; ChatGPT pose-generation examples recorded. Identity preservation is qualitative, not independently verified |
| ChatGPT multi-file library | Implemented; 16/16 asset recognition recorded; generation evidence is limited |
| Codex multi-file end-to-end handoff | Not verified |
| Lookset D2 export | Package structure and readback validated; complete commercial workflow not verified |

Automated tests validate scripts, manifests, package contents, and synthetic fixtures. They do not prove generated-image quality, identity preservation, garment fidelity, or Owner acceptance. Fine local face editing has not been established as reliable.

## Project resources

- **Formal source release:** [v0.2.0](https://github.com/denggui-ai/model-cast/releases/tag/v0.2.0)
- [Public project status](docs/PROJECT-STATUS.md) · [Release notes](docs/RELEASE-NOTES.md)
- [C10 usage](docs/C10-USAGE.md) · [Public POC results](docs/POC-RESULTS.md)
- [Development Protocol](docs/DEVELOPMENT-PROTOCOL.md) · [Project Adapter](docs/PROJECT-ADAPTER.md)
- [Third-party notices](skills/model-cast/THIRD_PARTY_NOTICES.md)

To run the automated checks:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider
git diff --check
```

The verified project snapshot passed 242 automated tests. The full workflow is currently verified on macOS; Python 3.10+ is required, and `crop.py` uses the system `sips` utility.

## License

Original project code and documentation use MIT. Vendored Lookset files retain Apache-2.0 and their upstream notices. Public example images are authorized AI-generated project assets; this does not grant rights to unrelated user assets.

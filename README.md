# model-cast

**Create an original AI fashion model, establish her identity, and deliver a reusable visual asset library.**

`model-cast` is a creation-and-handoff Skill for original adult fictional e-commerce models. It covers casting, face design and identity approval, model-view/action assets, a camera-angle guide, and two downstream handoff paths. It does **not** perform ongoing garment try-on, clothing design, or commercial product photography; those tasks belong to the user's downstream AI workflow or to Lookset.

## What it creates

1. **An original model** — casting brief, candidate selection, face/body identity approval, and an identity record.
2. **A visual reference set** — core identity images, supplementary model angles, selected action/expression examples, and the N2 faceless mannequin camera/framing guide.
3. **A reusable handoff** — an ordinary ChatGPT/Codex multi-file library and a separate Lookset D2 adapter.

## Showcase: Yuning

The following is an AI-generated fictional model case, not a photograph of a real person. The Owner authorized these selected images for this public project showcase.

### Identity and model views

| Face identity reference | Approved front full-body reference |
|---|---|
| ![Yuning face identity](docs/assets/showcase/yuning-face-identity.png) | ![Yuning front full-body](docs/assets/showcase/yuning-fullbody-front.png) |

The C6 overview documents 12 model views and three action/expression examples. Owner visual feedback accepted the 13 supplementary outputs. Some views do not show a face; those are body/framing references, not facial-identity proof.

![Yuning C6 model-view overview](docs/assets/showcase/yuning-c6-angle-overview.png)

### N2 camera/framing guide

N2 contains 12 faceless, hairless, clothing-free grey mannequin views. It illustrates camera direction and framing/crop; it is not Yuning, not a pose line drawing, not a clothing drawing, and not an image-edit base.

![N2 grey mannequin camera guide](docs/assets/showcase/n2-grey-mannequin-camera-guide.png)

### What is not claimed

- C10 was not included in v0.2.0. A separate post-release grey-mannequin pose supplement (three optional references) was added to `main` in PR #7; see `docs/C10-USAGE.md` for scope and validation limits.
- The V0.2 face-casting design guidance and Evals 19–23 are selectively integrated. The two-image practical nose-tip test did not clearly achieve its target; fine local facial editing is not claimed as reliable. The older V0.2 branch remains separate and is not merged wholesale.
- C5's three-product trial was an internal identity-continuity check. It is not evidence of reliable garment fidelity or a public try-on feature.
- D2 passed package structure/export/readback validation. That is not a claim that the complete Lookset commercial image workflow has been independently validated with this model.

## Two downstream paths

### A. Ordinary AI use — ChatGPT or Codex

The seller pack contains a folder named `4_完整AI资料库（多文件上传）` / `4_AI_Model_Library_MultiUpload`. Select all files in that folder and upload them together. It contains 12 real model views (including the four core identity anchors), three accepted examples (walking, sitting, natural smile), the N2 grey mannequin camera/framing guide, `START-HERE.md`, and `asset-index.json`.

The index tells the AI what each file is for and when to use it. The AI should inspect the files, select the smallest relevant reference set for the user's natural-language task, and say which files it selected. The four-image folder `2_上传给AI` / `2_Upload_to_AI` remains as a lightweight core set for tasks that need only the main identity anchors.

**Important host limitation:** reading or selecting an uploaded image does not prove that a downstream image-generation/editing tool received it as a reference. ChatGPT's multi-file recognition test identified 16/16 assets; one side-view generation test preserved framing/body/outfit reasonably well, but did not conclusively prove independent identity control from both references. Codex local-folder behavior has not yet received the same end-to-end test. If the host cannot pass the selected images to its image tool, it must ask the user to attach those images directly rather than pretending they were used.

### B. Lookset integration

Use the separate D2 adapter: P3-2 identity reference, model supplements 01–12, and `model.json`. Do not automatically add N2, C10 pose references, or ordinary-user instructions to D2. Lookset owns its own pose planning, garment editing, photography workflow, and commercial QA.

## Capability status

| Capability | Status |
|---|---|
| C1–C8 and C11 model-creation workflow | Implemented; workflow and code checks passed |
| Face/body identity approval and identity record | Implemented; depends on Owner review |
| C6 12 model views + 3 action/expression examples | Generated; Owner accepted; views without faces are not face-identity proof |
| N2 12-view grey mannequin guide | Generated and self-checked; included as a visual guide |
| C10 pose supplement | Three optional grey-mannequin pose references implemented after v0.2.0; see validation limits in `docs/C10-USAGE.md` |
| Ordinary AI multi-file library | Implemented in this package builder; ChatGPT recognition 16/16, one limited generation test; Codex end-to-end not yet verified |
| Lookset D2 export | Implemented; structure and readback validated, not full commercial workflow validation |
| Face-casting design guidance | Integrated with Evals 19–23; actual fine nose-tip edit target not passed |

## POC evidence and optional pose guidance

- [Public POC results](docs/POC-RESULTS.md) summarizes ZIP reading, direct multi-file recognition, minimum-reference selection, the limited side-view generation test, and the Codex timeout result. It separates observed outcomes from unverified host behavior and excludes private RUN records and source images.
- [C10 pose-guide usage specification](docs/C10-USAGE.md) defines how optional pose references differ from C6 identity references and N2 camera/framing references. The three-image C10 set is a post-v0.2.0 supplement and is not included in the v0.2.0 release.

**Scope boundary:** model-cast provides model identity and pose references. Final image generation, garment fidelity and commercial image quality depend on downstream AI tools and the user's workflow. model-cast does not guarantee garment reproduction or produce the final commercial image.

## Install

```sh
git clone https://github.com/denggui-ai/model-cast.git
cd model-cast
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
shasum -a 256 -c SHA256SUMS
```

Install only `skills/model-cast` into your supported agent skill directory. Back up any existing installation first; the repository does not overwrite it automatically.

Start with:

> Use model-cast to create an original adult virtual fashion model for my product line. First inspect the inputs and propose the casting plan; do not generate images until I approve.

Python 3.10+ is required. The full workflow is currently verified on macOS; `crop.py` uses `sips`. Image generation requires the host's native image capability, account access, and explicit user authorization. This Skill does not bundle an image model or provide image-generation credits.

## Validation

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider
git diff --check
```

Automated tests validate scripts, manifests, package contents, and synthetic fixtures. They do not prove generated-image quality or user acceptance. See [verification notes](docs/VERIFICATION.md).

## Project documents and licensing

- [Development Protocol](docs/DEVELOPMENT-PROTOCOL.md)
- [Project Adapter](docs/PROJECT-ADAPTER.md)
- [Public Project Status](docs/PROJECT-STATUS.md)
- [Release notes](docs/RELEASE-NOTES.md)
- [Third-party notices](skills/model-cast/THIRD_PARTY_NOTICES.md)

Original project code and documentation use MIT. Vendored Lookset files retain Apache-2.0 and their upstream notices. Public example images are authorized AI-generated project assets; this does not grant rights to unrelated user assets.

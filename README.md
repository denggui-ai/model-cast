<div align="center">

# model-cast

### Create a dedicated AI fashion model for your product line.

From casting and identity approval to a reusable visual reference library.

<img src="docs/assets/showcase/yuning-fullbody-front.png" alt="Yuning — original fictional AI fashion model, front full-body" width="58%"/>

**Yuning · Original AI-generated fictional model**

</div>

model-cast is an open-source Skill for creating original adult fictional fashion models, approving their visual identity, and preparing reusable references for downstream AI workflows.

The showcase images are authorized AI-generated project assets, not photographs of a real person.

---

## Build a complete model identity from the face

<div align="center">
<img src="docs/assets/showcase/yuning-face-identity.png" alt="Yuning face identity reference" width="42%"/>

**Face identity reference**
</div>

A model should be more than a collection of images that merely look alike. model-cast guides casting, identity approval, and the preparation of consistent model views.

### C6 · Model visual references

<img src="docs/assets/showcase/yuning-c6-angle-overview.png" alt="C6 model reference sheet with 12 views and 3 action or expression examples" width="100%"/>

**12 model views · 3 action/expression examples**

C6 is the core of the deliverable: the actual model images define face identity, body proportions, and approved views. The overview above is for browsing; downstream work uses the individual original files in the reference package.

---

## References prepared for downstream AI workflows

The standard AI library contains 16 images:

- **12** views of the actual model
- **3** model action/expression examples
- **1** N2 grey-mannequin camera/framing guide

It also includes `START-HERE.md` and a machine-readable `asset-index.json`. A lightweight four-image identity set is available when fewer references are sufficient.

<details>
<summary><strong>N2 · Camera and framing guide (expand)</strong></summary>

<img src="docs/assets/showcase/n2-grey-mannequin-camera-guide.png" alt="N2 grey faceless 3D mannequin camera and framing guide" width="100%"/>

N2 uses grey, faceless 3D mannequins to communicate camera direction, viewing angle, framing, and crop. It defines camera and composition only—not model identity or body action.
</details>

<details>
<summary><strong>C10 · Optional pose references (expand)</strong></summary>

C10 is a standalone optional supplement, used only when C6 does not already show the required pose. It is not a stage in the standard Skill workflow, is not part of the 16-image library, and is not included in Lookset D2.

- [Side walking PNG](docs/assets/c10/C10-01-Walk-Side.png) · [SVG source](docs/assets/c10/C10-01-Walk-Side.svg)
- [Side sitting PNG](docs/assets/c10/C10-02-Sit-Side.png) · [SVG source](docs/assets/c10/C10-02-Sit-Side.svg)
- [Hands-in-pockets PNG](docs/assets/c10/C10-03-Hands-In-Pockets.png) · [SVG source](docs/assets/c10/C10-03-Hands-In-Pockets.svg)

C6 defines identity and body proportions; C10 communicates pose and limb placement only.
</details>

---

## From casting to reference handoff

1. **Cast** — Prepare a casting brief from the product line and compare candidates.
2. **Approve identity** — Have the user approve the face and body references.
3. **Prepare views** — Organize model angles and action/expression references, then run a product try-on test.
4. **Hand off** — Build Chinese and English packages and a multi-file AI reference library.

## Get started

```sh
git clone https://github.com/denggui-ai/model-cast.git
cd model-cast
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
shasum -a 256 -c SHA256SUMS
```

Install `skills/model-cast` into your supported agent skill directory. Back up any existing installation first; this repository does not overwrite an existing installation automatically.

Start with an approval-first request:

> Use model-cast to create an original adult fictional fashion model for my product line. First inspect the inputs and propose the casting plan; do not generate images until I approve.

Image generation uses the host's native image capability. The Skill does not bundle an image model or provide generation credits; host access and explicit user authorization are required.

## Downstream workflows and scope

**ChatGPT / Codex:** Upload the files in `4_完整AI资料库（多文件上传）` / `4_AI_Model_Library_MultiUpload` together. The index helps select the minimum relevant references. Recognizing an attachment does not prove that a downstream image tool received it. ChatGPT has a recorded 16/16 asset-recognition test, but independent identity control from multiple references is not conclusively established. Codex local-folder-to-image-tool handoff remains unverified. If the host cannot pass selected images through, attach the originals directly.

**Lookset D2:** Use the separate adapter with P3-2 as the identity reference, model supplements 01–12, and `model.json`. Do not automatically add N2, C10, or ordinary-user instructions to D2. Lookset owns its separate pose planning, garment editing, photography workflow, and commercial QA.

model-cast prepares a model identity/reference set and hands it off to other tools. It is not an image-generation service, virtual try-on system, clothing-design tool, or commercial photography pipeline. Final image generation, identity preservation, and garment fidelity depend on downstream tools and the actual workflow. Automated tests do not prove image quality or commercial results.

### Public repository and model-specific packages

This public repository contains the Skill, packaging tools, documentation, and public showcase assets. Running the workflow prepares a separate reference package from your own approved model assets. The Owner-specific V3.0 seller package is private and is not included here. C10 is a standalone supplement added to `main` after v0.2.0; the v0.2.0 release and existing V3.0 packages remain unchanged.

## Project resources

- **Formal source release:** [v0.2.0](https://github.com/denggui-ai/model-cast/releases/tag/v0.2.0)
- [Project status](docs/PROJECT-STATUS.md) · [Release notes](docs/RELEASE-NOTES.md) · [Public POC results](docs/POC-RESULTS.md)
- [C10 usage](docs/C10-USAGE.md) · [Development Protocol](docs/DEVELOPMENT-PROTOCOL.md) · [Project Adapter](docs/PROJECT-ADAPTER.md)
- [Third-party notices](skills/model-cast/THIRD_PARTY_NOTICES.md)

Run the automated checks:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider
git diff --check
```

The verified project snapshot passed 242 automated tests. The full workflow is currently verified on macOS; Python 3.10+ is required, and `crop.py` uses the system `sips` utility.

## License

Original project code and documentation use MIT. Vendored Lookset files retain Apache-2.0 and their upstream notices. Public example images are authorized AI-generated project assets; this does not grant rights to unrelated user assets.

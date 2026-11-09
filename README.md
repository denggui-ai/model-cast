# model-cast

**Create an original AI fashion model, approve her visual identity, and build a reusable reference library.**

[简体中文](README.zh-CN.md) · **English**

model-cast is an open-source Skill and packaging toolkit for creating original adult fictional fashion models. It guides casting, identity approval, model-view preparation, and handoff of structured visual references to downstream AI workflows.

## Meet the model

The public showcase features **Yuning**, an AI-generated fictional model—not a photograph of a real person. These selected project images are authorized for this showcase.

![Yuning — approved full-body model reference](docs/assets/showcase/yuning-fullbody-front.png)

![Yuning — face identity reference](docs/assets/showcase/yuning-face-identity.png)

The C6 visual set contains 12 model views and three selected action/expression examples:

![C6 — model views and action/expression examples](docs/assets/showcase/yuning-c6-angle-overview.png)

C6 is the core deliverable: the actual model's face identity, body proportions, and model views.

## Supporting visual guides

The mannequin guides support the model references; they are not additional models or identity references.

### N2 — Camera and framing

N2 uses 12 grey, faceless 3D mannequin views to communicate camera direction, viewing angle, framing, and crop.

![N2 — grey mannequin camera and framing guide](docs/assets/showcase/n2-grey-mannequin-camera-guide.png)

### C10 — Optional pose references

C10 provides three separate grey, faceless 3D mannequin references for poses that are not already shown clearly in C6: side walking, side sitting, and hands-in-pockets standing.

| Side walking | Side sitting | Hands-in-pockets |
|---|---|---|
| ![C10 side walking](docs/assets/c10/C10-01-Walk-Side.png) | ![C10 side sitting](docs/assets/c10/C10-02-Sit-Side.png) | ![C10 hands-in-pockets](docs/assets/c10/C10-03-Hands-In-Pockets.png) |

Use at most the relevant C10 reference when needed. C6 defines identity and body proportions; C10 communicates pose. C10 is a standalone optional supplement—not a stage in the Skill workflow, not part of the standard 16-image AI library, and not part of Lookset D2.

## What you can create

The model-cast workflow helps you:

1. Cast an original adult fictional model from an authorized product image and a brief.
2. Compare candidates and approve the model's face and body identity.
3. Prepare model views and selected action/expression examples.
4. Build a structured, model-specific reference package for downstream AI use.

The standard multi-file ChatGPT/Codex library contains:

- 12 actual model-view images.
- Three model action/expression examples.
- The N2 grey-mannequin camera guide.
- `START-HERE.md` and a machine-readable `asset-index.json`.

The index describes each asset and helps downstream workflows select only the references relevant to a task. C10 remains a separate optional supplement.

## How to use it

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

Install only `skills/model-cast` into your supported agent Skill directory. Back up any existing installation first; this repository does not automatically overwrite an existing installation.

### 3. Start a project

Try this prompt:

> Use model-cast to create an original adult fictional fashion model for my product line. First inspect the inputs and propose the casting plan; do not generate images until I approve.

### 4. Hand off the reference library

Use the generated multi-file library with a downstream workflow such as ChatGPT or Codex. Attach the selected source images to the image tool itself when the host does not pass them through automatically. Reading or selecting an uploaded file does not prove that an image-generation tool received it.

Lookset D2 is a separate downstream adapter. It uses its own reference contract and does not receive N2 or C10 by default.

## What is included—and what is not

This public repository contains the model-cast Skill, packaging and validation tools, documentation, and public showcase/reference assets. Running the workflow creates a separate model-specific package from the user's own approved assets.

The Owner-specific V3.0 seller package is private and is **not** included in this repository. The public source repository, a package generated for your own model, and the Owner's existing V3.0 package are three different things.

model-cast does not bundle an image-generation model, provide generation credits, guarantee identity preservation or garment fidelity, or produce commercial photography. Final image generation depends on the host's native image capability and the user's authorized workflow. Identity consistency from multiple references has not been independently or biometrically verified. Codex local-folder-to-image-tool handoff remains unverified.

## Project status and documentation

- [Public project status](docs/PROJECT-STATUS.md)
- [Release notes](docs/RELEASE-NOTES.md)
- [C10 pose-reference usage](docs/C10-USAGE.md)
- [Public POC results](docs/POC-RESULTS.md)
- [Development protocol](docs/DEVELOPMENT-PROTOCOL.md)
- [Project adapter](docs/PROJECT-ADAPTER.md)
- [Third-party notices](skills/model-cast/THIRD_PARTY_NOTICES.md)

**Formal source release:** [v0.2.0](https://github.com/denggui-ai/model-cast/releases/tag/v0.2.0). C10 was added to the current `main` branch after v0.2.0; the v0.2.0 tag/archive and existing V3.0 seller package are unchanged.

## Validation

Automated tests validate scripts, manifests, and package structure; they do not establish image quality, identity preservation, garment fidelity, or Owner acceptance. See [project status](docs/PROJECT-STATUS.md) and [verification notes](docs/VERIFICATION.md) for the current evidence and host-specific limitations.

## License

Original project code and documentation use MIT. Vendored Lookset files retain Apache-2.0 and their upstream notices. Public showcase images are authorized AI-generated project assets; this does not grant rights to unrelated user assets.

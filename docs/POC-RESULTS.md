# Public POC results: model-cast visual-reference handoff

**Purpose:** publish a reproducible, privacy-screened summary of selected project POCs. This report records observed outcomes and limitations; it does not claim that every host or image-tool handoff is reliable.

**Privacy boundary:** private conversations, account/session identifiers, original generated outputs, source identity images, customer/product photographs, local paths, raw RUN records and quota ledgers are intentionally not included. Only aggregate findings and sanitized procedures are published here. The selected public showcase assets remain governed by the existing README authorization note.

## 1. Executive result

| POC | Observed result | Evidence strength | What it does not prove |
|---|---|---|---|
| ChatGPT ZIP reading / natural-language selection (2026-11-06) | Two Pro-mode trials read package instructions and produced a plausible requested outfit result; the second recognized the project model name written only in the ZIP instructions | Two observed end-to-end conversational trials | Does not prove ZIP-internal images are always passed as native image-tool references; only Pro was tested; one ambiguous product request replaced only the top |
| ChatGPT direct multi-file recognition (2026-11-08) | 16/16 images recognized and classified into four core identity images, eight supplementary views, three action/expression examples and one N2 guide | Direct observation with a fixed 16-image test set | Does not prove image-generation tools receive every selected attachment |
| ChatGPT minimum-reference selection | For a full-body side-view task, selected the face-front identity anchor plus full-body side reference | Observed selection decision | Does not independently prove each reference affected generated pixels |
| ChatGPT one-image side-view test | One authorized output broadly retained side framing, body proportions, hairstyle and outfit continuity | One limited visual test | Strict side view did not adequately verify facial identity; it did not isolate the contribution of each reference |
| Codex multi-file recognition attempt | Full 16-image and reduced 5-image attempts timed out before a result | Observed timeout | Not a failure result; Codex end-to-end behavior remains unverified |
| ChatGPT vs Codex casting-method comparison (2026-11-04) | Three candidates per host were compared using the same reference image and second-round prompts; reviewers found garment features broadly matched, while ChatGPT faces were more standardized/less mature-looking than the Codex set | Small comparative visual review | Not a controlled benchmark, not statistically generalizable, and not evidence that switching image hosts fixes casting quality |

## 2. ZIP POC: two distinct questions

The 2026-11-06 ZIP experiment tested whether ChatGPT could read instructions inside a ZIP and act on a short natural-language request. Both Pro-mode trials produced a plausible result. In the second trial, the assistant used the model name that appeared in the ZIP instructions even though it was not repeated in the user message; this supports that the instructions were read.

The trials also exposed two limitations:

- The first ZIP used macOS ZIP filename encoding that did not reliably preserve Chinese filenames. The later ZIP was produced with Python `zipfile` and a UTF-8-compatible filename path.
- In the second trial, the product image showed a coordinated outfit, but the request “put on this clothing” was interpreted as replacing only the top. The instruction was ambiguous about whether the whole outfit or one garment should be replaced.

**Interpretation:** ZIP reading and instruction-following were demonstrated in two Pro-mode trials. This is separate from proving that a downstream image-generation/editing tool receives the ZIP's internal image files as native references. The later direct-upload experiment was designed to make that reference boundary explicit. Do not describe the ZIP POC as proof of universal image-tool reference handoff.

## 3. Direct multi-file POC

The 2026-11-08 ChatGPT test supplied 16 source images, a contact sheet, an asset index, and a START-HERE instruction file. The assistant identified all 16 images and correctly separated the intended groups:

- 4 core identity references;
- 8 supplementary model angles;
- 3 action/expression examples (walking, sitting, natural smile);
- 1 N2 camera/framing guide.

For a hypothetical full-body side-view task, it selected the face-front identity image and full-body side image. This is evidence for file recognition, classification and textual reference selection in that ChatGPT session.

One separately authorized side-view generation test used directly uploaded face-front and full-body-side images. The output broadly retained side composition, body proportions, hairstyle and outfit. Because the output was a strict side view, the face was not sufficiently visible to establish facial identity robustly, and the experiment did not isolate the contribution of each input image.

## 4. Codex result

Codex CLI 0.161.0 was attempted with both the complete 16-image set and a reduced 5-image set. Both requests timed out before returning a recognition result. No image generation or file modification occurred in those attempts.

Correct status: **unverified due to timeout**. It is inaccurate to report this as either a successful test or a functional failure. A future test should use a smaller set or a different session/network window and record the exact host version and attachment handoff.

## 5. ChatGPT vs Codex casting-method comparison

On 2026-11-04, three candidates per host were generated using the same reference image and the same second-round prompt set. A visual reviewer found the requested garment features present across the six images (hood, gold zipper placket, two gold zip pockets and horizontal quilting). The reviewer also judged the ChatGPT faces more standardized and more heavily smoothed, while the Codex candidates showed more mature facial character.

This was a small qualitative comparison, not a controlled model benchmark. It suggests that prompt design and candidate-selection method may matter at least as much as changing hosts; it does not establish a general superiority of one host.

## 6. Reproduction outline

The public source repository provides the package builder, templates, synthetic tests and public asset-index contract. To reproduce the non-private parts of the POCs:

1. Build a fresh synthetic or explicitly authorized 16-file reference set; do not reuse private identity images without permission.
2. Include an asset index and START-HERE instructions with unambiguous asset categories.
3. Upload the files directly to ChatGPT and ask for a classification count and a minimum-reference selection for one specified task.
4. Record recognition, classification and selection separately from actual image-tool attachment receipt.
5. If an image generation/edit test is authorized, supply the selected source images directly and record which inputs were actually attached to the image tool.
6. For Codex, record the exact CLI version, local file paths, model/tool route, timeout/error and whether any image tool actually received the selected images.
7. Use a new test directory and synthetic or consented assets. Do not overwrite existing package candidates or publish raw conversation logs.

## 7. Product decisions supported by these POCs

- Keep the multi-file folder plus `START-HERE` and asset index as the primary ordinary-AI package path; retain the four-image core set as a lightweight alternative.
- Treat ZIP reading as a convenience for instructions and archive inspection, not as a guaranteed native image-reference transport.
- Distinguish recognition, classification, reference selection, image-tool handoff and visual output quality as separate acceptance gates.
- Keep ChatGPT and Codex host claims separate until each has a successful end-to-end test.
- Do not use these POCs to claim reliable garment fidelity, perfect identity control, or commercial photography readiness.

## 8. Evidence status

| Claim | Status |
|---|---|
| ChatGPT direct multi-file recognition: 16/16 | Observed / verified for that session and test set |
| ChatGPT minimum-reference selection | Observed for one specified task |
| ChatGPT side-view generation | One limited test; partial visual success, identity contribution inconclusive |
| ZIP instruction reading | Observed in two Pro-mode trials |
| ZIP internal images always passed to image tool | Not verified |
| Codex multi-file recognition and image-tool handoff | Unverified; two timeouts |
| Cross-host equivalence | Not established |
| General garment fidelity or commercial output quality | Not established |

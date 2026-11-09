# model-cast

**创建原创 AI 时尚模特，建立可复用的人物身份，并交付结构化视觉参考资料库。**

**简体中文** · [English](README.md)

model-cast 是一个开源 Skill，用于创建原创成年虚构电商模特，并整理可复用的视觉资料。它覆盖选角、面部与身体身份确认、视觉参考资料准备，以及向下游 AI 工具交付资料。

它**不是**生图服务、虚拟试穿系统、服装设计工具或商业摄影流水线。最终图像生成和服装还原效果取决于下游工具及用户工作流。

## 可以获得什么

- 原创成年虚构模特、选角说明和人物身份记录。
- 用于身份、身体视角、指定动作及镜头构图的视觉参考资料库。
- 面向普通 ChatGPT/Codex 使用的多文件资料交付方式。
- 独立的 Lookset D2 适配器。

## 视觉参考体系

| 资料 | 负责什么 | 不负责什么 |
|---|---|---|
| **C6** | 模特身份、面部特征和身体比例 | 指定新姿势或镜头角度 |
| **N2** | 使用灰色无脸人偶表达相机方向、景别和裁切 | 人物身份或动作控制 |
| **C10** | 使用与 N2 同风格的灰色人偶，提供可选动作和肢体姿势参考 | 人物身份、服装设计或服装还原 |
| **商品图** | 用户提供，供下游生成参考商品外观 | 模特身份 |

只选择当前任务需要的最少参考资料。C6 是人物身份依据；C10 只指导姿势；N2 只指导镜头和构图。C10 是 v0.2.0 发布后加入当前 `main` 的独立补充，不属于不可变的 v0.2.0 Release 归档，也不会自动进入现有 V3.0 卖家资料包。详见 [C10 使用规范](docs/C10-USAGE.md)。

## 快速开始

### 1. 安装

```sh
git clone https://github.com/denggui-ai/model-cast.git
cd model-cast
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
shasum -a 256 -c SHA256SUMS
```

### 2. 安装 Skill

只将 `skills/model-cast` 安装到你所使用的 Agent Skill 目录。安装前请备份已有版本；本仓库不会自动覆盖已有安装。

### 3. 开始一个项目

可以从以下提示词开始：

> 使用 model-cast 为我的产品线创建一位原创成年虚拟时尚模特。请先检查输入并提出选角方案；在我批准之前不要生成图片。

生图需要宿主工具具备原生图像能力、账户权限，并获得用户明确授权。本 Skill 不捆绑图像模型，也不提供生图额度。

## 项目示例：语宁（Yuning）

语宁是 AI 生成的虚构模特，不是真人照片。Owner 已授权将以下选定图片用于本项目公开展示。

| 面部身份参考 | 已确认的正面全身参考 |
|---|---|
| ![语宁面部身份参考](docs/assets/showcase/yuning-face-identity.png) | ![语宁正面全身参考](docs/assets/showcase/yuning-fullbody-front.png) |

C6 概览包含 12 个模特视角和 3 个动作/表情示例。Owner 的视觉反馈接受了 13 张补充输出。部分视角不展示面部，因此只能作为身体或构图参考，不能作为面部身份验证依据。

![语宁 C6 模特视角概览](docs/assets/showcase/yuning-c6-angle-overview.png)

### N2 镜头与构图参考

N2 包含 12 张无脸、无发型、无服装的灰色人偶图，用于表达相机方向、景别和裁切。它不是语宁本人、服装线稿或图像编辑底图。

![N2 灰色人偶镜头参考](docs/assets/showcase/n2-grey-mannequin-camera-guide.png)

## 下游工作流

### ChatGPT 或 Codex

卖家资料包包含 `4_完整AI资料库（多文件上传）` / `4_AI_Model_Library_MultiUpload`。使用完整资料库时，请将该目录中的文件一起上传。目录包含 12 张模特视角图（包括 4 张核心身份锚点）、3 张已接受的动作/表情示例、N2、`START-HERE.md` 和 `asset-index.json`。

索引说明每个文件的用途，并帮助 AI 选择当前任务所需的最少参考资料。对于只需要核心身份锚点的任务，也可以使用轻量目录 `2_上传给AI` / `2_Upload_to_AI` 中的 4 张图片。

**宿主能力限制：** AI 能识别或选中已上传图片，并不代表下游图像生成/编辑工具实际收到了这些图片作为参考。ChatGPT 多文件测试识别了 16/16 个资产，也完成了有限的姿势生成测试，但尚未确证多个参考能独立、稳定地控制人物身份。Codex 从本地文件夹到图像工具的完整传递仍未验证。如果宿主无法把所选图片传递给图像工具，必须要求用户直接附加图片，不能声称已经使用了未传递的图片。

### Lookset D2

使用独立的 D2 适配器：P3-2 身份参考、模特补充图 01–12，以及 `model.json`。不要默认将 N2、C10 或普通用户说明加入 D2。Lookset 自行负责其姿势规划、服装编辑、摄影工作流和商业质量检查。

## 功能与验证状态

| 模块 | 当前状态 |
|---|---|
| C1–C8、C11 模特创建流程 | 已实现；工作流和代码检查通过 |
| C6 身份确认与视觉参考 | 已实现；最终身份确认依赖 Owner 审核 |
| N2 12 视角灰色人偶参考 | 已生成并完成自检 |
| C10 三姿势补充 | 已在 v0.2.0 之后加入当前 `main`；有 ChatGPT 姿势生成记录。身份保持仅有定性观察，未独立验证 |
| ChatGPT 多文件资料库 | 已实现；识别测试为 16/16，生图证据有限 |
| Codex 多文件端到端传递 | 尚未验证 |
| Lookset D2 导出 | 已实现；资料结构和回读已验证，完整商业工作流未验证 |
| 面部局部精修 | 尚未证明可靠；实际鼻尖目标未通过验收 |

自动化测试验证脚本、清单、资料包内容和合成测试数据；不能证明生成图片质量、人物身份保持、服装还原或 Owner 接受。

## Release 与项目文档

- **正式源码 Release：** [v0.2.0](https://github.com/denggui-ai/model-cast/releases/tag/v0.2.0)。C10 在此版本发布后才加入当前 `main`；v0.2.0 标签和归档保持不变。
- [项目公开状态](docs/PROJECT-STATUS.md)
- [Release 说明与后续历史](docs/RELEASE-NOTES.md)
- [C10 使用规范](docs/C10-USAGE.md)
- [公开 POC 测试结果](docs/POC-RESULTS.md)
- [开发协议](docs/DEVELOPMENT-PROTOCOL.md)
- [项目适配说明](docs/PROJECT-ADAPTER.md)
- [第三方许可声明](skills/model-cast/THIRD_PARTY_NOTICES.md)

## 验证

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider
git diff --check
```

当前已验证项目快照的完整自动化测试为 242 项通过。完整工作流目前在 macOS 上验证；需要 Python 3.10+，且 `crop.py` 使用系统自带的 `sips` 工具。

## 许可证

原创项目代码和文档采用 MIT 许可证。Vendored Lookset 文件保留 Apache-2.0 许可证及其上游声明。公开示例图片是经授权的 AI 生成项目资产；这不代表用户其他资产也获得相同授权。

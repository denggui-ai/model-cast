# model-cast

**创建原创 AI 时尚模特，确认人物视觉身份，建立可复用的模特参考资料库。**

**简体中文** · [English](README.md)

model-cast 是一个开源 Skill，用于创建原创成年虚构时尚模特，并为后续 AI 工作流准备结构化视觉参考。它覆盖选角、身份确认、多视角资料整理，以及向下游工具交付参考资料。

核心交付是**模特本人及其可复用的身份与视觉参考资料**。灰色人偶只是辅助表达镜头或姿势的参考，不是模特本身。

## 先看模特成果

语宁是 AI 生成的虚构模特，不是真人照片。Owner 已授权将以下选定图片用于本项目公开展示。

<table>
  <tr>
    <td width="50%" align="center">
      <img src="docs/assets/showcase/yuning-face-identity.png" width="100%" alt="语宁面部身份参考"/>
      <br/><strong>面部身份</strong>
    </td>
    <td width="50%" align="center">
      <img src="docs/assets/showcase/yuning-fullbody-front.png" width="100%" alt="语宁正面全身参考"/>
      <br/><strong>正面全身</strong>
    </td>
  </tr>
</table>

### C6 — 完整模特视角资料

C6 包含 12 个模特视角和 3 个选定的动作/表情示例。它是人物身份的主要依据，用于表达模特的面部、身体比例及已确认的模特视角。

![C6 完整模特视角与动作/表情资料](docs/assets/showcase/yuning-c6-angle-overview.png)

## 辅助视觉参考

先确定模特，再按任务选择辅助参考。下面的灰色无脸 3D 人偶不是另一套模特，也不是身份参考或服装素材。

### N2 — 镜头与构图参考

![N2 灰色 3D 人偶镜头参考](docs/assets/showcase/n2-grey-mannequin-camera-guide.png)

N2 用于表达相机方向、观察角度、景别和裁切范围。它只在镜头或构图需要进一步明确时使用。

### C10 — 可选姿势参考

C10 用于表达 C6 尚未直接展示的身体动作和四肢位置。它是独立的可选补充，不属于标准 Skill 工作流阶段，也不包含在当前 16 张图片的正式资料库中。

目前有三种姿势参考，可按需打开原图：

- [侧面行走（PNG）](docs/assets/c10/C10-01-Walk-Side.png) · [SVG 源文件](docs/assets/c10/C10-01-Walk-Side.svg)
- [侧面坐姿（PNG）](docs/assets/c10/C10-02-Sit-Side.png) · [SVG 源文件](docs/assets/c10/C10-02-Sit-Side.svg)
- [双手插兜（PNG）](docs/assets/c10/C10-03-Hands-In-Pockets.png) · [SVG 源文件](docs/assets/c10/C10-03-Hands-In-Pockets.svg)

**三者职责不同：** C6 说明人物是谁；C10 说明身体如何动作；N2 说明镜头如何取景。按任务选择必要参考即可。具体选择方式见 [C10 使用规范](docs/C10-USAGE.md)。

## 工作流准备什么

仓库包含 model-cast Skill、多文件 ChatGPT/Codex 资料库构建工具与索引，以及独立的 Lookset D2 适配器。

标准 AI 参考资料库包含：

- 12 张真实模特视角图。
- 3 张选定的模特动作/表情示例。
- 1 张 N2 灰色人偶镜头/构图参考。
- `START-HERE.md` 使用说明和机器可读的 `asset-index.json`。

共 16 张图片，另附使用说明和索引。对于只需要少量参考的任务，也提供轻量的四图身份参考集。

### 公开仓库包含什么，不包含什么

本公开仓库提供 model-cast Skill、资料包构建工具、文档及公开展示资产。用户运行工作流后，可根据自己确认的模特素材生成独立的专属参考资料包。Owner 专属的 V3.0 卖家资料包属于私有交付，不包含在本仓库中。C10 是 v0.2.0 发布后加入当前 `main` 的补充，不会改变 v0.2.0 Release 归档或现有 V3.0 资料包。

## 快速开始

### 1. 安装仓库

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

### 3. 从“先审批、后生成”开始

> 使用 model-cast 为我的产品线创建一位原创成年虚构时尚模特。请先检查输入并提出选角方案；在我批准之前不要生成图片。

生图需要宿主工具具备原生图像能力、账户权限，并获得用户明确授权。本 Skill 不捆绑图像模型，也不提供生图额度。

## 下游使用

### ChatGPT 与 Codex

使用完整资料库时，请将目录 `4_完整AI资料库（多文件上传）` / `4_AI_Model_Library_MultiUpload` 中的文件一起上传。索引说明每个资产的用途，并帮助 AI 选择当前任务所需的最少参考资料。若任务只需要少量身份参考，也可以使用 `2_上传给AI` / `2_Upload_to_AI` 中的四张图片。

**参考图能否传递取决于宿主工具。** AI 能识别或选中已上传图片，并不代表下游图像生成/编辑工具实际收到了这些图片作为参考。ChatGPT 多文件测试识别了 16/16 个资产，也完成了有限的姿势生成测试，但尚未确证多个参考能独立、稳定地控制人物身份。Codex 从本地文件夹到图像工具的完整传递仍未验证。如果宿主无法把所选图片传递给图像工具，应直接附加所选原图，不能声称已经使用了未传递的图片。

### Lookset D2

使用独立的 D2 适配器：P3-2 身份参考、模特补充图 01–12，以及 `model.json`。不要默认将 N2、C10 或普通用户说明加入 D2。Lookset 自行负责其姿势规划、服装编辑、摄影工作流和商业质量检查。

## 能力范围与验证状态

model-cast 负责准备模特身份资料和视觉参考交付。它**不是**生图服务、虚拟试穿系统、服装设计工具或商业摄影流水线。最终图像生成和服装还原效果取决于下游工具及用户工作流。

| 模块 | 当前状态 |
|---|---|
| C1–C8、C11 模特创建流程 | 已实现；工作流和代码检查通过 |
| C6 身份确认与视觉参考 | 已实现；最终身份确认依赖 Owner 审核 |
| N2 12 视角镜头/构图参考 | 已生成并完成自检 |
| C10 三姿势补充 | 已加入当前 `main`；有 ChatGPT 姿势生成记录。身份保持仅有定性观察，未独立验证 |
| ChatGPT 多文件资料库 | 已实现；16/16 资产识别记录，生图证据有限 |
| Codex 多文件端到端传递 | 尚未验证 |
| Lookset D2 导出 | 资料结构和回读已验证；完整商业工作流未验证 |

自动化测试验证脚本、清单、资料包内容和合成测试数据；不能证明生成图片质量、人物身份保持、服装还原或 Owner 接受。面部局部精修也尚未证明可靠。

## 项目资源

- **正式源码 Release：** [v0.2.0](https://github.com/denggui-ai/model-cast/releases/tag/v0.2.0)
- [项目公开状态](docs/PROJECT-STATUS.md) · [Release 说明](docs/RELEASE-NOTES.md)
- [C10 使用规范](docs/C10-USAGE.md) · [公开 POC 测试结果](docs/POC-RESULTS.md)
- [开发协议](docs/DEVELOPMENT-PROTOCOL.md) · [项目适配说明](docs/PROJECT-ADAPTER.md)
- [第三方许可声明](skills/model-cast/THIRD_PARTY_NOTICES.md)

运行自动化检查：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider
git diff --check
```

已验证项目快照的完整自动化测试为 242 项通过。完整工作流目前在 macOS 上验证；需要 Python 3.10+，且 `crop.py` 使用系统自带的 `sips` 工具。

## 许可证

原创项目代码和文档采用 MIT 许可证。Vendored Lookset 文件保留 Apache-2.0 许可证及其上游声明。公开示例图片是经授权的 AI 生成项目资产；这不代表用户其他资产也获得相同授权。

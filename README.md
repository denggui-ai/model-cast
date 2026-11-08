# model-cast · T15 / V3 direct upload

用于原创成年虚拟模特选角、人工确认、原图保护和资料包制作的 Codex / Claude Code Skill。
A review-first workflow for casting original adult fictional models and packaging approved references.

**这是经过脱敏的开发源码分支，不是新的正式 Release。** 现有 `main` 保持原样。资料包格式 V3.0 不等于软件发布版本 v3.0；V0.2 是另一条尚未合并的面部定妆实验线。

## 选择分支

| 公开分支 | 内容与状态 |
|---|---|
| `opensource/t15-direct-upload`（本分支） | V3 四张原图直传、双语打包、卡片排版、Lookset D2 导出；自动化结构验证通过 |
| `opensource/v0.2-face-casting` | 独立的面部定妆指导实验；真实鼻尖修改用例未通过；不含 T15 合并结果 |
| `opensource/development-protocol-pr` | 脱敏后的协作规范；仅文档，不是运行技能 |

## 功能与边界

按 C1–C8 / C11 流程记录自有或已授权商品图、比较原创成年候选、人工确认身份、验证商品小试并准备资料包。只对获授权的素材执行操作；不模仿真人或名人。

本分支的中文和英文卖家包分别包含：阅读资料、恰好四张上传原图（01 / 04 / 06 / 07）、三张生活场景图。工程资料和 Lookset D2 分开放置。脚本校验来源、SHA-256、文件集合、卡片来源记录及拒绝覆盖；不会替你判断人脸或商品质量。

**不承诺像素级锁脸、精确局部修改或任何商品都能成功。** `Preserve` 是提示约束。没有公开任何私人人像、商品图、生成结果、真实回执、额度账本或完整私人运行日志。

## 环境

- 当前整套工具以 **macOS** 为验证环境；`crop.py` 使用系统 `sips`，卡片排版需要系统中文字体。未宣称 Linux / Windows 全流程可用；不分发字体文件。
- Python 3.10+；本次在 Python 3.14 上运行测试。
- Pillow（运行时）与 pytest（测试）。Lookset 导出器已按固定版本包含在 `vendor/lookset`，无需另装 Lookset 才能执行导出验证。
- 生图宿主兼容基线锁定 **Codex CLI 0.161.0**；其他版本需要重新完成宿主兼容检查，不能静默跳过。
- 生图需要宿主原生能力、有效账户和单独授权。脚本不会提供独立生图模型或免费额度；本地台账默认 500 是工作流上限，不是账户赠送额度。

## 获取与安装

```sh
git clone --branch opensource/t15-direct-upload --single-branch https://github.com/denggui-ai/model-cast.git
cd model-cast
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
shasum -a 256 -c SHA256SUMS
```

仅将 `skills/model-cast` 复制到技能目录，不复制整个源码仓库；若已有安装，先在外部保留备份，不覆盖：

```sh
python3 - <<'INSTALL'
from pathlib import Path
import shutil
source = Path('skills/model-cast')
target = Path.home() / '.agents/skills/model-cast'
if not (source / 'SKILL.md').is_file():
    raise SystemExit('Run from the source repository.')
if target.exists() or target.is_symlink():
    raise SystemExit('Existing skill found; back it up before installing.')
target.parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(source, target)
print(target)
INSTALL
```

技能位置参考 [官方技能文档](https://learn.chatgpt.com/docs/build-skills#where-to-save-skills)。本仓库不会自动修改全局配置。

开始时可以说：

> 用 $model-cast 为我的自有商品线规划一位原创成年虚拟模特。先确认输入和计划，不生成图片。

运行目录 `RUN` 和资料包输出目录应在源码仓库之外。生成、外部上传和继续重试都需要明确授权；保留原图及所有结果。`references/pack-manifest.example.json` 仅供源码仓库中的合成夹具测试；实际使用须填写自己的已授权来源和真实校验值。身份锁示例中的全零/全一哈希是占位值，不能当作素材证据。卖家文案模板中的案例和测试描述不得未经核实复制成对自己产品的承诺。

## Public development protocol

- [Development Protocol](docs/DEVELOPMENT-PROTOCOL.md)
- [Project Adapter](docs/PROJECT-ADAPTER.md)
- [Public Project Status](docs/PROJECT-STATUS.md)

## 测试

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider
git diff --check
```

测试只使用小尺寸合成色块和合成事件，不生图、不访问私人 RUN。评测 JSON 是场景定义，不等于已经跑过真实模型评测。验证范围与当前结果见 [VERIFICATION](docs/VERIFICATION.md)。

## 许可与贡献

原创代码与文档沿用 [MIT](LICENSE)；vendored Lookset 仍为 Apache-2.0，保留其原许可证和来源信息，见 [第三方说明](skills/model-cast/THIRD_PARTY_NOTICES.md)。旧公开 `main` 的种子阵容不在此分支工作树内，既有公开历史保留；不将私人素材授权为 MIT 或 CC0。

反馈时仅提供脱敏步骤和错误，不上传脸图、商品素材、完整私有提示词、回执或凭证。参见 [贡献说明](CONTRIBUTING.md) 和 [公开分支说明](docs/RELEASE-NOTES.md)。

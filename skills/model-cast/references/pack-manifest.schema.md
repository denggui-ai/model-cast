# pack-manifest schema 2（核心四图 + 完整 AI 多文件资料库；V2.0 ZIP 结构留在 git 历史）

所有对象严格校验：缺键或多键退出 2，错误包含字段位置。所有下列字段必填，无可选键。路径为非空字符串；相对路径以 manifest 所在目录为基准，绝对路径可用。图片须 PNG，sha256 为 64 位小写十六进制。文本必须存在且非空。

| 键 | 类型与约束 |
|---|---|
| schema | 整数 2 |
| model_name | 文件名组件；本阶段 `Yuning` |
| name_zh | 文件名组件；模特中文名，本阶段 `语宁` |
| version | `V主.次`，主版本 ≥ 3；V1.x/V2.x 使用已退役布局 |
| run_dir | RUN 根目录，内部证据写其 c8/，不得位于任何输出包内 |
| originals | 对象，恰好 P3-2、01–12；值为 asset |
| motion | 对象，恰好 walk、sit、smile；值为 asset |
| texts | 对象，恰好 `how_to_use`、`originality`、`boundary`（各为 `{zh, en}`）。源文件不能是 RUN 里的文件（只有 `c7/originality.zh.md`、`c7/originality.en.md` 例外），内容也不能和任何内部证据相同（RUN 里除清单图片和这两份说明之外的所有文件，以及 `references/phase1-prompts.md`、`phase2-prompts.md`）；按内容比对，改了名也会被拦 |
| identity_card | `{zh: asset, en: asset}`，make_card.py 排版的识别卡，只看不传 |
| diagram | asset，拍摄规格示意图，只放工程资料 |
| lookset | 下表对象 |

asset 恰好两个键：`path`、`sha256`。originals 与识别卡、示意图、动态图不得有相同哈希。图片复制后再次核对；不缩放、不转格式。

## 输出（名字由脚本推出，清单里不写）

```
<model>_品牌模特资料包_<V>/                       <model>_Brand_Model_Pack_<V>_EN/
├── 1_给你看（不要上传）/                           ├── 1_Read_me (do not upload)/
│   ├── 使用说明.txt          ← how_to_use.zh       │   ├── How_to_use.txt
│   ├── 角色识别卡.png        ← identity_card.zh    │   ├── Model_card.png
│   └── 原创性与使用边界.txt  ← originality + 空行 + boundary（zh）
├── 2_上传给AI/                                  ├── 2_Upload_to_AI/
│   ├── 01_脸部正面.png                           │   ├── 01_脸部正面.png
│   ├── 04_全身正面.png                           │   ├── 04_全身正面.png
│   ├── 06_全身侧面.png                           │   ├── 06_全身侧面.png
│   └── 07_全身背面.png                           │   └── 07_全身背面.png
├── 3_生活场景图（可直接用）/walk sit smile.png    ├── 3_Lifestyle/walk sit smile.png
└── 4_完整AI资料库（多文件上传）/                  └── 4_AI_Model_Library_MultiUpload/
    ├── 01–12 真实模特角度图
    ├── 13–15 行走、坐姿、自然微笑
    ├── 16 N2 灰色人偶相机角度指南
    ├── START-HERE.md
    └── asset-index.json
<model>_<V>_工程资料/（不交付）
├── shooting-guide.png、清单/pack-manifest-<V>.json、清单/version-manifest-<V>.json
└── <model>_品牌模特资料包_<V>-model-reference/   ← export_lookset 写入（D2）
```

`2_上传给AI` 保留恰好 4 张核心原图：01、04、06、07，便于最小参考任务。`4_完整AI资料库` 包含 12 张真实模特角度、3 张动态素材和 N2 指南，共 16 张 PNG，另含双语 START-HERE 与机器可读 `asset-index.json`。用户在 ChatGPT/Codex 中可多选该目录全部文件上传；AI 读取索引和视觉内容后选择最少必要参考。文件名是辅助标签，不是唯一识别依据。N2 仅为角度/景别指南，不是身份参考、姿势线稿或图像编辑底图。C10 人物姿势线稿未实现，不进入当前包。版本清单 `upload_files` 仍记录核心四图，另以 `ai_library_files` 记录完整资料库 16 张图片及 SHA-256。

check_pack 逐项核对：卖家包文件和目录集合、每个复制件哈希、文本与源一致、核心上传目录恰好四张原图、生活场景图恰好三张、AI 资料库恰好 16 张 PNG 且 asset-index 与 manifest 一致、版本清单两组哈希记录与原图一致、工程资料清单与 RUN/c8 一致；D2 仍只包含 Lookset 规定的原图（`--require-lookset` 要求 D2 存在）。

RUN/c8 的证据按版本命名：`version-manifest-<V>.json`、`lookset-spec-<V>.json`、`lookset-validate-<V>.json`；已存在就拒绝（退出 2），旧版本文件不动。

| lookset 键 | 类型与约束 |
|---|---|
| confirmation_note | 非空字符串，Owner 选 P3-2 和认可 01、04 的原话加日期 |
| supplement_notes | 对象，恰好 01–12，每个值为非空字符串（这张的 Owner 原话加日期） |
| locked | 三项非空字符串数组：两处结构记忆点的英文短句；最后一项固定 `balanced regular build, natural waist, realistic leg length` |
| adjustable | 按顺序为 hairstyle、makeup、expression、earrings and accessories 的字符串数组 |
| styling_lock | 字符串 `identity` |

导出器生成 source_type=ai、scope=full、subject=adult female model，不填 consent_note。references 只用 P3-2；supplements 顺序 01、04、02、03、05–12，01–03 scope=face，其余 full。不放动态或示意图。确认原话由 Claude 填写，脚本不能证明话语真实性。

从仓库根运行（示例引用 tests/fixtures/phase2 中的假 PNG 和占位文字，不作身份验收，不是卖家文案）：

```bash
python3 -B skills/model-cast/scripts/build_pack.py --manifest skills/model-cast/references/pack-manifest.example.json --out-dir .example-packs
python3 -B skills/model-cast/scripts/export_lookset.py --manifest skills/model-cast/references/pack-manifest.example.json --out ".example-packs/Yuning_V3.0_工程资料/Yuning_品牌模特资料包_V3.0-model-reference"
python3 -B skills/model-cast/scripts/check_pack.py --out-dir .example-packs --manifest skills/model-cast/references/pack-manifest.example.json --require-lookset
```

示例的内部证据写在仓库 `.example-run/c8/`。复制哈希错误退出 1 并清理这次新建的文件夹；清单错误退出 2；check_pack 输出 problems=N，非零退出 1。Lookset 验证只算结构对，不算人对。

# 私人单人最短路径

`scripts/private_model.py` 只准备任务、登记一次原生调用、回填原图并调用裁光导出器保存。它没有网络调用、自动审核或自动重试。公共阵容旧生成器不参与。

使用环境中已发现的裁光技能目录作为 `--threadtruth`，不要写死缓存位置。本次接入已验证的接口来自裁光 `1.0.0-beta.18`（先前离线验证使用 beta.16）：`model_reference.py` 的 validate_model、validate_image、prompt_lines、export_package、load_package；目标因子由导出器在真实接受后转为固定。脚本需要 Python 3.9+（本次实测 Python 3.14）、可用的 Pillow，以及原生 `image_gen`。找不到依赖时保留已做的文字准备并说明缺项，不复制另一套保存系统。

下面的路径变量由执行助手填入实际位置；任务目录必须在 model-cast 仓库之外。每次一个新目录，内部 `.gitignore` 忽略全部私人产物。

```sh
python3 "$CAST/scripts/private_model.py" prepare --threadtruth "$THREADTRUTH" --task "$TASK" --spec "$SPEC"
```

准备 SPEC 前，按 [自然语言设计](natural-language-design.md) 整理当前人物方向与保留／修改范围。用户只需说需求；由助手填写下面的结构，示例数值不是默认审美。业务用途、原话、建议和未知项可记在私人任务旁的简报中，不新增卡片字段，也不把设计目标当图片已确认。

```json
{
  "model": {
    "source_type": "new",
    "scope": "face",
    "subject": "adult model",
    "locked": ["成年年龄感", "用户指定的短卷发"],
    "adjustable": [],
    "styling_lock": "full",
    "consent_note": ""
  },
  "view": "face",
  "references": [],
  "source_note": "根据本次用户文字创建的虚构成年人物；私人使用，尚未接受图片"
}
```

`source_type=new` 从文字建立新身份，不附旧身份图；`source_type=ai` 必须提供已有 AI 原始参考的绝对路径，1–5 张，脚本会复制并记录哈希。有图片时先亲自打开。`scope` 表示已知身份范围，`view` 表示本次要生成的 face/full 画面；仅正脸无法建立新 full 范围。补全身可用原正脸 `source_type=ai, scope=face, view=full`，保存时作为已接受的 full 补充，原正脸仍在。

### 生成一个候选

```sh
python3 "$CAST/scripts/private_model.py" reserve --threadtruth "$THREADTRUTH" --task "$TASK" --note "本次实际生成授权原话或准确范围"
```

核对输出 `image_gen_arguments` 的人物条件、画面和附件，使用它调用原生 `image_gen` 一次。`prepare` 的容量不是用户授权，`reserve` 的 note 也不能自行编造。读取原生生图要求；调用前准备已知图片路径，不改用公共 CLI 生成器。

```sh
python3 "$CAST/scripts/private_model.py" returned --threadtruth "$THREADTRUTH" --task "$TASK" --file "$RETURNED_IMAGE"
```

脚本复制原始返回、严格解码、记录尺寸/哈希；这只是文件有效，不是视觉通过。展示原图并对照需求检查面部、身体、发型、手和构图，再记录用户实际反馈。脚本不强制特定头身比、盘发或时装身形。

失败或返回未知时：

```sh
python3 "$CAST/scripts/private_model.py" failed --threadtruth "$THREADTRUTH" --task "$TASK" --note "实际失败或未决情况"
```

本次调用保留计数，禁止再 reserve。若找到同次原始返回，用 `returned` 回填；已回填的相同字节可重复恢复，不会再计费，不同图不能覆盖。进程中断时先读 `ledger.json`、`request.json` 及现存原图；不可重新初始化清零或盲目再调用。若中断在预约与请求文件写入之间，停止并说明没有可核对的请求，不自行发起新调用。

修改条件／补图用另一个 TASK。保持同一身份时沿用原参考，用裁光的因子替换功能或完整重写当前条件，保存旧任务供对照；不堆叠旧新要求。每次新增调用沿用实际授权范围，没有授权时先完成新的文字方案。旧包不覆盖。

未接受候选用于编辑时，其参考角色不等于用户已接受。若最终只接受新图，另建 `source_type=ai` 的零调用保存任务，只引用实际接受的新图；不要直接保存编辑任务，把被拒的旧候选留下当原始身份。明确从头换人时使用 `source_type=new`，不带旧候选。

### 确认后保存

```sh
python3 "$CAST/scripts/private_model.py" save --threadtruth "$THREADTRUTH" --task "$TASK" --name "实际人物名或版本" --note "用户对实际图片的接受原话与范围"
python3 "$THREADTRUTH/scripts/model-reference.py" validate --package "$TASK/package"
```

输出在 `TASK/package`，包含裁光标准 `model.json`、原图及说明。`source.json`/`SOURCE.md` 另外保存来源和私人存放信息，不往标准卡片添加私有字段。未接受的设计目标不能作为已确认事实传给 save；先缩小条件到真实接受范围，必要时另开匹配任务，不修改已经预约的输入。

- 新身份：接受的候选成为原始身份参考。
- 已有 AI 且没有调用：可以直接保存已接受原图，调用数为零。
- 已有 AI 的生成补充：保留原图，将本次明确接受的画面写为 supplement，不能冒充原图。
- 失败或未决调用不能保存成已接受候选。只接受脸时不能称完整身形已确认。

### 两位公共种子

读索引与所选 card，打开正脸及实际需要的全身图，按已接受的范围选引用。Lina 正脸/全身发型不同；Jun 正脸/全身也有发型差异，两位全身都带插兜。明确本次妆发目标，不把已有动作固化为身份。两张都属 identity-reference；不要声称硬分离脸和身体，也不因一次仅正脸试验就更改默认策略。

使用现有裁光 `model-reference.py export --spec ... --package ...`，显式 `source_type=ai`、scope、成年 subject、styling_lock。`confirmation_note` 如实记“原卡 Owner 接受、用户本次选用”的实际范围，不冒充本轮商品验收。私人目录的包另写来源、原卡许可和限制，保留 CC0 种子的原许可，不添加独家承诺。

### 交给裁光

交付 `TASK/package` 并说明原始图/补充图范围。下一次有商品素材时，让裁光通过 `model_package` 导入，核对导出的真实 request 条件与附件。人物图和商品图合计不得超过原生工具附件上限；按本次用途选用，不能省略商品关键依据来强行放全套人物图。新商品重新验收，人物确认不等于商品通过。

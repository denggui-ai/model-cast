---
name: model-cast
description: 为一条商品线创建原创成年女性电商模特，从商品图制定选角简报、比较候选、锁定身份并进行真实商品小试。用于选人定人、补角度和资料包打包；单纯换装或模仿真人、明星的请求不触发。
---

# model-cast

## Workflow 与授权

本技能正式工作流执行 C1–C8 和 C11（含 N2 示意图）。C10 是仓库提供的独立可选姿势参考资产，不是本技能的工作流阶段，也不由标准资料包构建流程自动纳入；仅在 C6 未展示所需姿势时，用户才可按 [C10 使用规范](../../docs/C10-USAGE.md) 手动选择并提供对应参考图。C4 主脸描述可用[选角词表](references/casting-vocabulary.md)。用户明确提出面部审美、定妆或面部修改需求时，按[面部定妆设计指导](references/face-casting.md)组织观察与迭代；该指导不改变固定提示词、状态机、授权闸门或原图保护规则。不继承 v0.1 / v0.2 的旧阵容或旧状态机；旧阵容 Lina、Jun 不进新版。仅选择性采用面部定妆设计指导。禁止用真人照片当底图、模仿任何真人或名人；商品图含人物时只取商品，不取人物身份。只用 Owner 自有或获授权的商品图。缺输入则停下索取，不替 Owner 选图。

生图付费闸门：每次生图前确认 Owner 已批额度，报告累计已用和剩余张数（总池 500），以及本批授权余量。额度不足先停下等 Owner；自检淘汰的图片也计数。宿主执行前检查版本锁定为 `codex-cli 0.161.0`，变化时停下重跑 T0。每张单独调用，参考图显式传路径，不依赖最近几张图。Claude Code 宿主用 `codex exec`；Codex 宿主用原生生图。生图由当前宿主提供的原生能力执行；本技能不内置生图模型。

## 状态和流程

1. **C1 → brief_ready**：先记录 Owner 选角商品图的来源、sha256、商品线、穿着者和尺码线；禁止用 `koreatest/` 测试图选角。已有品牌方向、客群和展示目标保留为卖家原话；在同一份简报中区分“用户明确提供 / 图片可见 / 推断 / 未知”。卖家只给商品图和一句话时，不为补齐营销资料停下：能从图中判断的标“推断”，看不出的写“待问”。C2 可先进行，候选比较使用已有信息；到 C11 前再请 Owner 确认商品线、穿着者和尺码线。
2. **C2 → candidates_ready**：3 次独立调用，每次参考图只传选角商品图，选角商品图用 `--ref product=<路径>`。逐字使用[内部临时提示词](references/phase1-prompts.md)中的 C2 固定提示词。宿主不加方向、脸部结构、发型、妆容、构图或任何规则。底线只核对 3 条：回执 `ok`、未污染且尺寸合格（短边 ≥ 1024 且高 ≥ 宽）；成年；不像任何具体真人或明星。不过的那张不展示，可用新 id 重出 1 次。不看衣服，衣服保真归 Lookset 或卖家换装；人不行就换人，不在同一张图上修；不要求脸部结构明显不同。`board.md` 每位候选一行：调用 id、图片路径、回执状态、底线 3 条（尺寸和回执 / 成年 / 不像真人或明星）各自是否通过。宿主看图定框（头顶到下巴，留少量边），用 `scripts/crop.py` 逐张裁出脸；再用任意看图工具把几张裁图拼在一起给 Owner 看。拼图只作展示，不作证据，不需要回执。🔒 关 1 展示 3 张候选原图和脸部并排图，等 Owner 选一位或全拒；Owner 觉得像同一个人时按全拒处理。
   C1 中用户明确给出的品牌/展示要求属于卖家原话，一并原样带入 C2；不把宿主推断改写成生图控制词。看板另附简短选角理由：候选的可见特点如何回应实际商品与卖家目标，哪些只是视觉判断；资料不足时如实标明，不编造客群、点击率或销量依据。这些理由供 Owner 比较，不增加淘汰门槛或替 Owner 选人。
3. **C3 → rejected_r1 / rejected_r2_stopped**：全拒时记录 Owner 原话至 `c3/rejection-rN.md`，将原话原样接在请求后，再出 3 位新的人，产物在 `c2/r2/`。每轮 3 张，最多两轮；两轮全拒就停，不抽第 3 轮。选中后记 **selected**，保存实际选中理由及 Owner 原话，不能把后补推断写成当时的决定依据。超出已批额度先停下，报告已用和剩余，等 Owner 追加额度。
4. **C4 → identity_locked**：生成 01、04 时，选中的候选图用 `--ref selection=<路径>`。先用 `scripts/crop.py` 从选中候选以脸为中心裁出头顶至锁骨的 `c4/01-crop.png`，记录裁剪框，不盲目居中裁。短边 ≥ 1024 直接用作 01；不足则保留裁图证据，按 C4-01 生成 `01.png`。写 `body-plan.md`，不默认细腰长腿；用候选原图和 01 生成 `04.png`。附 `side-by-side.md` 比较候选、01、04，脸和身体矛盾先停下来对比。🔒 等 Owner 认可 01 和 04，两者都认可才锁定。
   需要交付已有 01/04 或转交下游任务时，按[身份资料交付与附件核对](references/identity-delivery.md)从本人物的 C4 认可记录取原图。用户只要求最小资料时可以在此交付，不为凑齐 C8 自动补图库；不把该交付记作完整流程或下游复用通过。
5. **C11**：只判断不生图。`c11/judgment.md` 固定四段：①适合 / 不适合；②商品穿着者、尺码线与 01、04 体型对照的依据；③逐项判断穿着者是否明显不同、体型是否撑不起尺码线；④不适合时只写“建议另建，等 Owner 决定”。🔒 等 Owner 看判断理由，不自动另建。
6. **C5 → tryon_done**：确认商品所指具体件数（T0 的三张测试图为整套搭配，T6 前须定清）。三件各自从 01、04 原图出发，依次显式传 01、04、商品图，不传上次成品。产物在 `c5/{2jpg,3jpg,1png}/try-1.png`，每件最多 `fix-1.png` 一次。核对参考图确实是 01、04、商品图；商品图原有的人物或人台没有残留到脸、肤色、首饰；与 01、04 放大并排看身份，记录全身是否认得脸。写 `c5/RESULT.md`。🔒 关 2 等 Owner：三件都认得出这位模特 → **gate2_pass**；任何一件修过一次仍认不出 → **gate2_fail** 并停。

## 失败与验收

t0 不查尺寸；01 宽高都 ≥ 1024；候选短边 ≥ 1024 且高 ≥ 宽；04、换装和修图短边 ≥ 1024 且高 > 宽。不允许放大补尺寸。侧面、背面或看不清脸标“未验证”，不能作为身份过关证据。

失败类别：④身份漂移；⑤工具错误（包括 no_image、multi_image、没收到参考图、tool_error）；⑥尺寸不达标。同一个目标（同一候选 / 01 / 04 / 同件换装）连续两次出现同一类失败 → **stopped**，保留两次原文证据报告 Owner，不再生成。Owner 拒绝轮次单独计最多两轮；C5 每件最多修一次，以更严规则为准。

不过的那一张可重出 1 次，单位是单张而非整组，须用新 id。同一张同一类失败第 2 次就停；所有重出仍受额度闸门约束。

完整流程闸门：Owner 认可身份，C11 理由已审，三件小试已判 gate2_pass 或 gate2_fail 并按规则停止；回执、额度、参考哈希与实际图一致。仅交付已认可的 01/04 时，完成标准见身份交付参考，不自动进入 C5–C8。T1/T1b 的静态验证只证明脚本与骨架，不能代替宿主兼容性或看图验收。规格没写到、与 T0 矛盾时停下写 handoff。

## 脚本与回执

脚本使用 Python 3；`crop.py` 另调用 macOS 自带的 `sips`；`compose_sheet.py` 和 vendor 的 Lookset 导出器需要宿主自带的 Pillow，缺失时报 `tool-blocked` 并退出 2，不自动安装。`--run-dir` 是 RUN 根目录；每个唯一 `--id` 创建 `RUN/<id>/request.json` 和独立 `receipt.json`，总台账为 `RUN/quota.jsonl`。每次尝试用新 id（末尾 `-1` / `-2` 标识 attempt）。不得在 argv、回执、日志中放凭证；凭证仅经环境变量。

```bash
python3 scripts/gen_request.py --task T2 --purpose candidate --id c2-r1-A-1 --prompt-file /absolute/prompt.txt --ref product=/absolute/selection.png --run-dir /absolute/RUN
python3 scripts/collect_receipt.py --request /absolute/RUN/c2-r1-A-1/request.json --before /absolute/before.txt --exit-code 0 --events /absolute/events.jsonl
python3 scripts/crop.py --src /absolute/RUN/c2/r1/cand-A.png --box 100,50,700,650 --out /absolute/RUN/c4/01-crop.png
python3 scripts/quota.py --run-dir /absolute/RUN
python3 scripts/check_run.py --run-dir /absolute/RUN
```

运行脚本前将工作目录切到本技能目录。`gen_request.py` 只打印 argv 与重定向，不执行。宿主负责执行命令并记录真实调用的时间：request.started_at 默认准备时刻，执行前更新为实际开始 ISO8601+08:00；收集时 finished_at 为收集时刻，宿主有实际结束时间时应在收集前将其写入 request.finished_at。重试 request 的 attempt 取 id 末尾数字。

生成路径隔离采用三层防护：① `gen_request.py` 在 `--json` 前加 `--disable plugins`；② 将新宿主前缀 `【宿主指令】不要调用任何技能、插件或脚本，不要读写文件；使用内置图片生成工具完成下面的请求，生成且只生成 1 张图。`、换行、`请求：` 与提示词文件全文拼为调用目录的 `prompt-sent.txt`，stdin 读取该文件，request 与回执同时记录原提示词及实际发送文件的路径、sha256；③ `collect_receipt.py` 检查 events 中 `item.type == command_execution` 的 command，去掉 `/.codex/skills/.system/imagegen/SKILL.md` 和 `~/.codex/skills/.system/imagegen/SKILL.md` 两种写法后仍包含 `SKILL.md` 或 `/plugins/` 即标 `contaminated`、failure_class=5，并在 contamination 列出命令。污染图仍复制、保留并计入 images_generated；非零 exit_code 优先判 tool_error，其后 contaminated 优先于 no_image / multi_image / size_fail。

按批准规格 2.3，调用前宿主将 `~/.codex/generated_images/` 全部文件绝对路径排序写入 `before.txt`，只作证据；调用后从真实 events 的 `thread.started.thread_id` 取会话 id，收集器仅扫描该会话子目录求差集。全局清单中无该子目录条目说明调用前为空；before 缺失或空文件判 tool_error。不能枚举其他会话的输出来找图。T0 事件无图片路径，使用真实测试样本锁定该事实。

一次调用一份回执、一行 quota；0 图 no_image，1 图按尺寸判断 ok / size_fail，多图 multi_image。所有新增图片都保留，多图按 `<id>-k.png` 存储、全列 outputs，不挑结果；仅 ok 填顶层输出字段。images_generated 为真实新增张数；额度兼容旧 counts_quota。收集器拒绝同 id 重复核销。异常回执和尺寸失败须交宿主处理，不因脚本进程完成就当成生成通过。`check_run.py` 检查每张 PNG 的回执覆盖、哈希、引用和尺寸；`crop.py` 的坐标为左上角起的 `x0,y0,x1,y1`（右、下边界不含），只裁剪、不缩放，输出 PNG 和 `<out>.crop.json` 来源记录；越界退出 2，拒绝覆盖已有输出。C2 看板与 C4 均用它裁图，不算生图额度。`check_run.py` 对带来源记录的裁图免查生图回执，核对当前源图和输出哈希及记录尺寸。

调用目录内 PNG 的 sha256 与本目录 receipt.json 的某张输出相同时，`check_run.py` 将其视为副本，不报 missing receipt；其他目录或不同哈希的 PNG 仍需回执或裁图来源记录。

外部图片用 `python3 scripts/register_external.py --dir D --kind chatgpt-web --source TEXT [--note TEXT] [--file NAME …]` 登记；未指定文件时仅登记 D 直属、未被回执覆盖且无 `.crop.json` 的 PNG。同目录 `EXTERNAL.json` 登记且哈希一致时 `check_run.py` 免查回执和尺寸，哈希变化报 `external hash mismatch`；登记不计额度，`quota.py` 不读取它。

## 第二阶段：C6 / N2 / C7 / C8

在 gate2_pass 后进入 **angles_in_progress**。C6 第一步按 [身份锁示例](references/identity-lock.example.json) 写 RUN/c6/identity-lock.json：01、04 绝对路径、实际 sha256 和 selection.md 两处记忆点原文。已有 C4 身份锁时沿用其已认可原图，不从下游附件反向建锁。face_angle/body_angle/motion 必须带 --identity-lock，按顺序 --ref face01=01 --ref body04=04，绝不接上一张成品。每张独立调用；使用 [内部临时提示词与自检规则](references/phase2-prompts.md)，修一次仍只用 01、04。

face_angle 宽高均 ≥1024；body_angle 短边 ≥1024 且高>宽；motion 短边 ≥1024 且高≥宽；diagram 短边 ≥1024 且不传任何参考图。N2 的 12 张无脸人偶示意图只看不传，不进入上传入口或 D2。compose_sheet.py --out OUT.png --cols N --cell WxH --item 路径=标签 可重复 item，生成 PNG 和 .sheet.json，不计生图额度；check_run 核对源图和输出哈希。

C6 每张与 01、04 并排自检，07/10/11/12 标“身份未验证”，10–12 另与 04 腰以下对照。新增失败⑦规格不符；左右方向相反但角度档位对时照实标注，不默认镜像。自检全合格 → **angles_ready**；Owner 逐张看图通过并记录原话 → **angles_accepted**。同一编号连续两次同类失败 → **stopped**，Owner 要求重出计“修一次”。付费额度、宿主区分及版本锁沿用前述闸门。

C7 用 build_records.py --run-dir RUN --selection-ids <正式选人那一轮的回执 id，逗号分隔> 汇总：第 1 段只放这一轮的固定提示词、候选和选中原话，其余候选回执单列为“历史候选试验”；第 2 段只放定人和补角度的调用；第 4 段只列这两类调用的输出哈希。不写判断。Claude 写中英原创性说明 → **originality_ready**，Owner 认可 → **gate3_pass**。不承诺全球唯一或低撞脸率，不编身高三围。

C8 按 [清单契约与可执行示例](references/pack-manifest.schema.md)（schema 2）填清单，使用 build_pack.py、check_pack.py 和 export_lookset.py。一次打出中文包、英文包和工程资料。卖家包提供四类内容：1 给你看（使用说明、角色识别卡、原创性与使用边界，不上传）；2 核心四图（01、04、06、07，适合只需最小身份参考的任务）；3 生活场景图（walk/sit/smile，可直接展示，不替代身份参考）；4 完整 AI 资料库（12 张真实模特角度、3 张动态素材、N2 灰色人偶相机角度指南、START-HERE 和 asset-index；用户可在 ChatGPT/Codex 一次多选上传）。AI 应根据自然语言任务选择最少必要参考，并说明实际选择；不能把 N2 当模特身份或图像编辑底图。读取/选择附件不代表图像工具一定收到这些参考；宿主无法传递时须提示用户直接补传。C10 三张灰色无脸 3D 人偶姿势参考已存在于仓库，作为独立可选补充资产提供；不属于本次标准 16 张 AI 资料库，不进入 Lookset D2，也不由本技能的标准 C1–C8/C11 工作流自动生成或打包。需要 C6 未覆盖的姿势时，用户可按 C10 使用规范手动选择一张参考图；不得将其描述为人物身份参考、服装图或编辑底图。Lookset D2 独立输出，不混入 N2、C10 或普通用户说明。卖家文案取 [模板目录](references/pack-templates/)，原创性说明取 RUN `c7/originality.*`。角色识别卡用 make_card.py（card-spec schema 2）只拿原图排版，记忆点特写须是 crop.py 从 01 裁的；check_pack 核对卡来源。Owner 看图后才进入最终交付。打包不覆盖旧版，按字节复制；RUN/c8 的证据按版本命名，已有就拒绝。

D2 只调用 vendor/lookset 的 v0.1.0-beta.3（139d178）工具，运行前对比写死哈希及 VENDOR.json；通过 python3 -B 执行 export + validate，读回输出存 RUN/c8/lookset-validate-V主.次.json；D2 导出到工程资料里的 `<中文包名>-model-reference`。reference=P3-2，supplements=01–12，Owner 确认原话加日期。check_pack 的 problems=0 且 Lookset validate 通过 → **pack_built**；Owner 看整包认可 → **gate4_pass**。D2 验证失败不挡 D1：D2 标“未交付”并记原因，以同版本同批原图补出。静态检查只算结构对，不算人对或 L3；Lookset 真正出图与第三阶段网页实测均不在本次任务内。

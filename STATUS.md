# 任务看板

> **唯一真相源。** 开工前先读，改完通过自己的分支提 PR。
> **铁律：认领 = 把任务行从「待认领」整体搬到你的分区；只准动自己分区和「待认领」，禁止改别人的行。**
> 角色身份见 `00_CONTRACT/ROLES.md`。

---

## 🎯 角色

| 角色 | 谁 | 认领人 |
|------|---|--------|
| modeler | 建模手 | kumu314（仓库管理员） |
| coder | 代码手（兼队长） | Blair（Blair-wealthy-2007） |
| writer | 论文手 | ningxiachufang |

## 🚀 进行中

### modeler（建模手）

- [modeler] 数模契约并入仓库 — 100% — 2026-09-03 — FACTS/SPEC/模板/脚本/自动加载 skill 已就位
- [modeler] FACTS 弹射题版 v2（五项参数调研 + 拍板锁定）— 100% — 2026-09-04 — 本 PR

### coder（代码手）

- [coder] 【coder 起步】确认 results.json schema + 搭求解骨架 + 产出首版 results.json — 100% — 2026-09-04 — 骨架已搭好（首版数值 11122 N 为旧参数，已被下方修正版取代）
- [coder] P1 主模型求解与结果 — 100% — 2026-09-05 — solve.py 按 model-spec + FACTS v2.1 重跑（PR #10 七条清单全项落实）：T_min=2474.92 N（≈建模手预演 2520 N），h_min=1912.17 m（开伞前最低海拔，binding=H7 垂尾），a_max_g=3.75（<5g），sep_x_min=2.59 m，vt_clear_min=1.17 m，burn_clear_min=5.98 m；fig4-1 轨迹图 + fig5-1 帕累托前沿（膝点 T*=6246.47 N）；results.json 全精度、通过 check_schema.py
- [coder] 敏感性分析 — 100% — 2026-09-05 — v0/h0/β/m 四参数扫描入 results.json.sensitivity：v0↑/β↑/m↑→T_req↑，h0 不变（T_req 与 h0 解耦，符合 H7 早期掠过判据）
- [coder] P2 倾角 θ 扫描与最优弹射方案 — 100% — 2026-09-05 — θ∈[0°,30°] 步长 2.5° 全部可行；**最优倾角 θ*=7.5°**（可行 θ 中推荐推力最小：T_opt=1491 N，h_min=1517.6 m）。发现低倾角端（θ≤7.5°）卡的是开伞触发约束（人椅过早弹道顶点、|v| 未降到 45 m/s，伞无法打开），θ≥10° 起转由 H7 垂尾约束卡下界；fig6-1 + table6-1 已产出

### writer（论文手）

- [writer] 【writer 任务2】产出《AI 工具使用详情》PDF + 正文逐处标注 — 进行中（已指派，待 writer 开工）— 预估 1.5h — 脚手架：`论文生产规范库/01_官方红线与合规/AI合规三件套.md`（三件套：①§3.1 前声明块 ②参考文献 [5] WorkBuddy ③1 页 A4 PDF）；生成脚本 make_ai_decl_pdf.py 仓库内尚未落地，可改走 `.tex`+xelatex（件套3 允许）；队号/姓名/签名为人工填
- [writer] 【writer 任务3】章节 3–4 建模过程与求解算法写作 — 进行中（已指派，与任务2 并行）— 预估 6h — 照 `docs/model-spec.md` 起草：§3 模型建立＝§一运动方程+§二安全判据(H7/H8/H4/H5/H6/不撞地)+§五决策点；§4 求解算法＝§三优化问题表述(Q1水平飞行)+「最佳推力定义」+§六实现清单。数字纪律：最终数值结果一律 `{{占位符}}` 禁手抄 model-spec §四预演值当定稿；参数引 FACTS（t1/a_lim/h_ox 为题面硬约束，余为文献假设）
- [writer] 【writer 任务4】章节 5 结果分析写作 — 进行中（已指派，results.json 已落定）— 预估 4h — 数据源 `01_OUTBOX/coder/results.json`（全精度）+ fig4-1/5-1/6-1 + table5-1/6-1。数字纪律：一律 `{{占位符}}`（fill.py 从 results.json 回填），禁手抄。**必讲清的口径**：①P1.T_min=2474.92 N 是「H7 垂尾余量 0.5 m」下界 T_req（binding 约束），推荐工作点是帕累托膝点 T*=6246.47 N（meta.T_star_knee_N），5g 上界 T_max=8338.5 N——三者别混；②h_min=1912.17 m 与 a_max_g=3.7456g 在 T* 工作点计算；③开伞物理：T* 下人椅过弹道顶点时 |vx| 已被气动阻力衰减到 45 m/s 以下，下降段即刻满足开伞条件（h_open≈顶点高度）——是阻力衰减的自然结果，不是"顶点开伞 bug"；④P2：θ*=7.5°、T_opt=1491 N、h_min=1517.6 m；低倾角端（θ≤7.5°）binding=开伞触发约束、θ≥10° 转 H7 垂尾约束；θ↑→推力下界↑（后倾减小竖直分量）；⑤敏感性：v0↑/β↑/m↑→T_req↑，h0 与 T_req 解耦（H7 为相对判据），v0≤212.5 m/s 时无需推力
- [writer] 【writer 任务5】代码附录整理 — 进行中（已指派，与任务4 并行）— 预估 2h — 源 `01_OUTBOX/coder/solve.py`（632 行），按 `论文生产规范库/05_代码附录规范/` 整理；关键函数加一句话注释，主流程（读 FACTS → ODE 分段积分 → 六判据 → 帕累托前沿/膝点 → θ 扫描 → 出 JSON/图表）须与 §4 正文对应

## 📋 待认领（认领 = 整行搬到自己的分区）

- 【modeler 起步】填 FACTS.md 口径 + 假设清单 + 符号表（modeler，预估 1h）— ✅ 已完成：弹射版 v2 已入 main
- 摘要 + 关键词 + 模型评价与改进（writer，预估 2.5h）— 待任务4 交稿后开工（摘要必须等结果定稿）；按 `docs/math-section-template.md` 口径
- 全文整合排版 + 质检出稿（modeler 主导、writer 配合，预估 3h）— 占位符回填（fill.py）→ audit.py 数字对账 → 图表规范 → AI 合规三件套落地 → PDF/docx 定稿

## ✅ 已完成

- [writer] 【writer 起步】§1 问题重述 + §2 问题分析 — 100% — 2026-09-04 — sec1_problem.md / sec2_analysis.md 已交稿，数字全占位符（PR #12 合并）
- [modeler] 回应 writer PR #12 反馈 — 100% — 2026-09-04 — PR #13 合并：audit 三类误报过滤 + test_audit.py 回归闸、start-*.md 认领改走 STATUS、FACTS 来源分类说明

## 🚧 待评审

- （暂无）

## ⚠️ 风险 / 阻塞

- ~~FACTS.md 口径待填（全队第一阻塞）~~ → **已解除**：弹射版 v2 已锁定（2026-09-04），coder/writer 可直接开工
- ~~代码手尚未认领角色~~ → **已解除**：coder 已认领（Blair，随 PR #10 登记）
- ~~[coder] PR #10 主线阻塞~~ → **已解除（2026-09-05 17:28 合并，commit 900fdd6）**：七项清单全项落实——T_min=2474.92 N（binding=H7 垂尾，≈建模手预演 2520）、h_min=1912.17 m、a_max_g=3.75g<5、sep_x_min=2.59 m 与 vt_clear_min=1.17 m 分离、全精度 results.json、P2 θ*=7.5°、四参数敏感性齐备。results 流水线解锁，§5/代码附录已派 writer（任务4/任务5）
- ~~[writer] `scripts/audit.py` 三类误判（有序列表编号 / LaTeX 下标 / 行内代码路径）~~ → **已解除**：PR #13 合并，`extract_draft_numbers` 加过滤 + `scripts/test_audit.py` 回归闸（CI 绿）
- ~~[writer] 契约自相矛盾（start-*.md 让 writer/coder 改 ROLES.md 被 premerge_check 挡）~~ → **已解除**：PR #13 改 `docs/start-writer.md`/`start-coder.md` 认领改走 STATUS.md 角色表，禁止改 `00_CONTRACT/ROLES.md`
- ~~[writer] FACTS 假设 H1–H9 待核对~~ → **基本解除**：solve.py v2.2 已严格按 FACTS v2.1 实现（头部注释逐项列出参数口径）；FACTS 文件内逐条打勾并入轮④质检收口
- [writer] 任务3 §3/§4 已并行指派（框架 `docs/model-spec.md` 已锁定）→ coder results.json 已落定（PR #10 合并），`{{占位符}}` 回填条件已具备；任务3 与任务4 可共用同一套回填流程
- [writer] 📌 **赛题原文核对（2026-09-04 已用官方 docx `B 题 飞行员空中弹射问题及其优化.docx` 逐句比对）** —— §1/§2 与 FACTS 已对准题面，发现 4 处须校正：① FACTS 把 `v0/h0/m/β/v_e` 等标「✅ 题面」，但题面仅给 3 个硬约束（推力持续 5s、承受 ≤5g、最高高度 <3000m），其余为团队文献假设，建议改标「✅ 文献假设」；② 题面四阶段自「火箭马达推力加速」起，无独立「导轨射出」段，FACTS 的①导轨射出 + v_e 属建模细化，须在 §2 注明是补充假设；③ 题面明确列「风力」为因素，FACTS 未处理风向，§2 须声明该简化；④ AI 使用声明为学校强制（附件须标注 AI 名称/交互过程/结果，或声明未使用）—— 团队已有 `论文生产规范库/01_官方红线与合规/AI合规三件套.md` 脚手架，非缺口。核验依据见 `01_OUTBOX/writer/sec1_problem.md`、`sec2_analysis.md`。—— 进展：① FACTS 口径标签——**经核验 v0/h0/m/β/v_e 等本就标 ✅ 文献假设，仅 t1/a_lim/h_ox 为 ✅ 题面，标签无误**；PR #13 已在 FACTS §3.1 加来源分类说明，无需改标签；② 导轨段已在 `sec2_analysis.md` 2.3 落实；③ 风力简化已在 2.1 落实；④ AI 声明 PDF 已指派 writer（任务2，进行中），脚手架 `论文生产规范库/01_官方红线与合规/AI合规三件套.md`。

## 📢 公告

- 2026-09-05 17:30：**🔴 主线阻塞解除 —— PR #10 已合并（commit 900fdd6），coder 四项任务全交付**：results.json（全精度）+ solve.py + fig4-1/5-1/6-1 + table5-1/6-1。核心数：**T_min=2474.92 N（binding=H7 垂尾，与建模手预演 2520 对上）、膝点 T*=6246.47 N、5g 上界 T_max=8338.5 N、θ*=7.5°（T_opt=1491 N）**。轮② 已派：writer 任务4（§5 结果分析）+ 任务5（代码附录）。剩余路线：轮③ 摘要+评价改进 → 轮④ 整合质检出稿。**@writer 注意口径：T_min 是 H7 下界 T_req，推荐工作点是膝点 T*，h_min/a_max_g 在 T* 算——三者别混（详见任务4 行）。**

- 2026-09-05 13:35：**@coder 催办（PR #10，全队唯一真阻塞）** —— 七项重跑清单已于 09-04 发出、至今未执行；今日补发：①先 `git pull` + rebase 到最新 main（#12–#16 已合并，你的分支落后且曾标 CONFLICTING）；②按 `docs/decisions-2026-09-04.md` 输出**各约束 binding 情况**（T_min 紧约束可能是「越过垂尾」而非 5g）；③H7 用垂尾口径 s_vt=7 / h_vt=3.5；④在 `STATUS.md` 认领 coder 角色行（认领走角色表，勿改 ROLES.md）；⑤回复 ETA。**§5 结果分析与代码附录全卡在此，writer 侧已无活可派。**

- 2026-09-04 16:20：**代码手两个疑问已由建模手答复**，见 `docs/decisions-2026-09-04.md`（必读，H7/H8 判据公式在里面）。要点：①阶段①＝火箭推力 5s，`v_e` 是 t=0 初始条件、导轨段不单独建模，5g 只约束火箭段；②H8 用飞机随体系喷流锥判据，推力方向与喷流方向无需一致；③**H7 改为以垂尾为准**（新增 s_vt=7、h_vt=5.5）；④SPEC 的 P1 新增 `vt_clear_min`、`burn_clear_min` 两个连续量字段。**粗算提示：T_min 的紧约束可能是"越过垂尾"而非 5g，请 coder 输出各约束的 binding 情况。**
- 2026-09-04 13:30：**赛题 = 模拟三 B 题 飞行员空中弹射，FACTS 已弹射化并锁定全部参数**——输入参数 17 项 + 敏感性区间见 `00_CONTRACT/FACTS.md`；results.json schema 已换新（P1: T_min/h_min/a_max_g…，P2: theta_sweep/T_opt…）见 `00_CONTRACT/SPEC.md`。旧 C 题 schema 作废。
- 2026-09-04 12:40：开工指令已就位——coder 读 `docs/start-coder.md`、writer 读 `docs/start-writer.md`、modeler 读 `docs/start-modeler.md`（契约 skill 会自动指到对应文件）。**先 pull、认领角色、认领起步任务，再动手。**
- 2026-09-04：契约升级 v2——三角色分工（modeler/coder/writer）、PR 自动校验闸、按角色分区看板。**数字一律用 `{{占位符}}`，禁止手抄。**

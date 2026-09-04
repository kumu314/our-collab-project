# 任务看板

> **唯一真相源。** 开工前先读，改完通过自己的分支提 PR。
> **铁律：认领 = 把任务行从「待认领」整体搬到你的分区；只准动自己分区和「待认领」，禁止改别人的行。**
> 角色身份见 `00_CONTRACT/ROLES.md`。

---

## 🎯 角色

| 角色 | 谁 | 认领人 |
|------|---|--------|
| modeler | 建模手 | kumu314（仓库管理员） |
| coder | 代码手（兼队长） | ⬜ 待认领 |
| writer | 论文手 | ningxiachufang |

## 🚀 进行中

### modeler（建模手）

- [modeler] 数模契约并入仓库 — 100% — 2026-09-03 — FACTS/SPEC/模板/脚本/自动加载 skill 已就位
- [modeler] FACTS 弹射题版 v2（五项参数调研 + 拍板锁定）— 100% — 2026-09-04 — 本 PR

### coder（代码手）

- （暂无）

### writer（论文手）

- [writer] 【writer 起步】写 §1 问题重述 + §2 问题分析 — 100% — 预计 3 小时 — sec1_problem.md / sec2_analysis.md 已交稿，数字全占位符

## 📋 待认领（认领 = 整行搬到自己的分区）

- 【coder 起步】确认 results.json schema + 搭求解骨架 + 产出首版 results.json（coder，预估 2h）— P1 有数 / P2 可 null，指令见 docs/start-coder.md
- 【modeler 起步】填 FACTS.md 口径 + 假设清单 + 符号表（modeler，预估 1h）— ✅ 已完成：弹射版 v2 已入 main
- 【writer 起步】产出《AI 工具使用详情》PDF + 正文逐处标注（writer，预估 1.5h）— 按 `论文生产规范库/01_官方红线与合规/` 脚手架，声明本队 AI 使用情况（或声明未使用），生成脚本见 `make_ai_decl_pdf.py`
- P1 主模型求解与结果（coder，预估 6h）— 水平飞行：最小推力 T_min + 最低飞行高度 h_min，输出 results.json + 轨迹图
- P2 倾角 θ 扫描与最优弹射方案（coder，预估 5h）— 输出 results.json P2 字段 + θ 扫描图
- 敏感性分析（coder，预估 3h）— v0/h0/β/m 四参数，输出 sensitivity 字段
- 章节 3–4 建模过程与求解算法写作（writer，预估 6h）— sec3~sec4
- 章节 5 结果分析写作（writer，预估 4h）— sec5，依赖 results.json
- 代码附录整理（writer，预估 2h）— 按代码附录规范

## ✅ 已完成

- （暂无）

## 🚧 待评审

- （暂无）

## ⚠️ 风险 / 阻塞

- ~~FACTS.md 口径待填（全队第一阻塞）~~ → **已解除**：弹射版 v2 已锁定（2026-09-04），coder/writer 可直接开工
- 代码手与论文手尚未在 ROLES.md 认领角色 → writer 已认领（ningxiachufang），coder 仍空缺
- [writer] `scripts/audit.py` 会把三类内容误判为「未溯源数字」：Markdown 有序列表编号（`1. 2. 3.`）、LaTeX 下标（`$h_0$` / `$v_0$`）、行内代码里的路径（`00_CONTRACT/FACTS.md`）—— 阻塞「数字对账」报告可读性（噪声淹没真问题）—— 需要 modeler 在 `extract_draft_numbers` 里加过滤：行首列表序号、反引号内行内代码、`_{...}` 下标
- [writer] **契约自相矛盾**：`docs/start-writer.md` 第 0 步要求 writer 打开 `00_CONTRACT/ROLES.md` 填写姓名与账号完成认领，但 `scripts/premerge_check.py` 规定 `00_CONTRACT/` 只有 modeler 能改 —— writer 照指令做就会 PR 校验失败 —— 需要 modeler 二选一：premerge_check 里把 `00_CONTRACT/ROLES.md` 加白名单（只放行「认领人」列），或改由 modeler 统一登记。当前 writer 已在 STATUS.md 角色表登记为替代方案
- [writer] FACTS 假设 H1–H9 全部「待核对」，且 coder 角色尚未认领 —— 阻塞 §3 模型建立（假设与代码不一致是硬伤）—— 需要 coder 认领后逐条核对并在 FACTS 打勾
- [writer] 📌 **赛题原文核对（2026-09-04 已用官方 docx `B 题 飞行员空中弹射问题及其优化.docx` 逐句比对）** —— §1/§2 与 FACTS 已对准题面，发现 4 处须校正：① FACTS 把 `v0/h0/m/β/v_e` 等标「✅ 题面」，但题面仅给 3 个硬约束（推力持续 5s、承受 ≤5g、最高高度 <3000m），其余为团队文献假设，建议改标「✅ 文献假设」；② 题面四阶段自「火箭马达推力加速」起，无独立「导轨射出」段，FACTS 的①导轨射出 + v_e 属建模细化，须在 §2 注明是补充假设；③ 题面明确列「风力」为因素，FACTS 未处理风向，§2 须声明该简化；④ AI 使用声明为学校强制（附件须标注 AI 名称/交互过程/结果，或声明未使用）—— 团队已有 `论文生产规范库/01_官方红线与合规/AI合规三件套.md` 脚手架，非缺口。核验依据见 `01_OUTBOX/writer/sec1_problem.md`、`sec2_analysis.md`。

## 📢 公告

- 2026-09-04 16:20：**代码手两个疑问已由建模手答复**，见 `docs/decisions-2026-09-04.md`（必读，H7/H8 判据公式在里面）。要点：①阶段①＝火箭推力 5s，`v_e` 是 t=0 初始条件、导轨段不单独建模，5g 只约束火箭段；②H8 用飞机随体系喷流锥判据，推力方向与喷流方向无需一致；③**H7 改为以垂尾为准**（新增 s_vt=7、h_vt=5.5）；④SPEC 的 P1 新增 `vt_clear_min`、`burn_clear_min` 两个连续量字段。**粗算提示：T_min 的紧约束可能是"越过垂尾"而非 5g，请 coder 输出各约束的 binding 情况。**
- 2026-09-04 13:30：**赛题 = 模拟三 B 题 飞行员空中弹射，FACTS 已弹射化并锁定全部参数**——输入参数 17 项 + 敏感性区间见 `00_CONTRACT/FACTS.md`；results.json schema 已换新（P1: T_min/h_min/a_max_g…，P2: theta_sweep/T_opt…）见 `00_CONTRACT/SPEC.md`。旧 C 题 schema 作废。
- 2026-09-04 12:40：开工指令已就位——coder 读 `docs/start-coder.md`、writer 读 `docs/start-writer.md`、modeler 读 `docs/start-modeler.md`（契约 skill 会自动指到对应文件）。**先 pull、认领角色、认领起步任务，再动手。**
- 2026-09-04：契约升级 v2——三角色分工（modeler/coder/writer）、PR 自动校验闸、按角色分区看板。**数字一律用 `{{占位符}}`，禁止手抄。**

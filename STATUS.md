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

- [writer] 【writer 任务2】产出《AI 工具使用详情》PDF + 正文逐处标注 — 进行中（已指派，待 writer 开工）— 预估 1.5h — 脚手架：`论文生产规范库/01_官方红线与合规/AI合规三件套.md`（三件套：①§3.1 前声明块 ②参考文献 [5] WorkBuddy ③1 页 A4 PDF）；生成脚本 make_ai_decl_pdf.py 仓库内尚未落地，可改走 `.tex`+xelatex（件套3 允许）；队号/姓名/签名为人工填

## 📋 待认领（认领 = 整行搬到自己的分区）

- 【coder 起步】确认 results.json schema + 搭求解骨架 + 产出首版 results.json（coder，预估 2h）— P1 有数 / P2 可 null，指令见 docs/start-coder.md
- 【modeler 起步】填 FACTS.md 口径 + 假设清单 + 符号表（modeler，预估 1h）— ✅ 已完成：弹射版 v2 已入 main
- P1 主模型求解与结果（coder，预估 6h）— 水平飞行：最小推力 T_min + 最低飞行高度 h_min，输出 results.json + 轨迹图
- P2 倾角 θ 扫描与最优弹射方案（coder，预估 5h）— 输出 results.json P2 字段 + θ 扫描图
- 敏感性分析（coder，预估 3h）— v0/h0/β/m 四参数，输出 sensitivity 字段
- 章节 3–4 建模过程与求解算法写作（writer，预估 6h）— sec3~sec4
- 章节 5 结果分析写作（writer，预估 4h）— sec5，依赖 results.json
- 代码附录整理（writer，预估 2h）— 按代码附录规范

## ✅ 已完成

- [writer] 【writer 起步】§1 问题重述 + §2 问题分析 — 100% — 2026-09-04 — sec1_problem.md / sec2_analysis.md 已交稿，数字全占位符（PR #12 合并）
- [modeler] 回应 writer PR #12 反馈 — 100% — 2026-09-04 — PR #13 合并：audit 三类误报过滤 + test_audit.py 回归闸、start-*.md 认领改走 STATUS、FACTS 来源分类说明

## 🚧 待评审

- （暂无）

## ⚠️ 风险 / 阻塞

- ~~FACTS.md 口径待填（全队第一阻塞）~~ → **已解除**：弹射版 v2 已锁定（2026-09-04），coder/writer 可直接开工
- 代码手与论文手尚未在 ROLES.md 认领角色 → writer 已认领（ningxiachufang），coder 仍空缺（PR #10 已开，作者 Blair 未正式认领 STATUS 角色行）
- [coder] **🔴 PR #10 是当前主线阻塞**：与 main 冲突（CONFLICTING）且参数陈旧（T_min=11122N>5g 上限、h_open 在顶点、h0=8008 等旧值），coder（Blair）末次提交 2026-09-04 10:26 → 需 `git pull` + rebase 到 main + 按 `docs/decisions-2026-09-04.md` 七项清单重算（v_open=45 下降触发、sep_x_min 真实纵向间隙、H4 5g 上限、h_min 取工作点、全精度 results.json）→ 更新 PR 后 modeler 评审合并。**不解决则 §5 结果分析与整条 results 流水线全卡。**
- ~~[writer] `scripts/audit.py` 三类误判（有序列表编号 / LaTeX 下标 / 行内代码路径）~~ → **已解除**：PR #13 合并，`extract_draft_numbers` 加过滤 + `scripts/test_audit.py` 回归闸（CI 绿）
- ~~[writer] 契约自相矛盾（start-*.md 让 writer/coder 改 ROLES.md 被 premerge_check 挡）~~ → **已解除**：PR #13 改 `docs/start-writer.md`/`start-coder.md` 认领改走 STATUS.md 角色表，禁止改 `00_CONTRACT/ROLES.md`
- [writer] FACTS 假设 H1–H9 全部「待核对」，且 coder 角色尚未认领 —— 阻塞 §3 模型建立（假设与代码不一致是硬伤）—— 需要 coder 认领后逐条核对并在 FACTS 打勾
- [writer] 📌 **赛题原文核对（2026-09-04 已用官方 docx `B 题 飞行员空中弹射问题及其优化.docx` 逐句比对）** —— §1/§2 与 FACTS 已对准题面，发现 4 处须校正：① FACTS 把 `v0/h0/m/β/v_e` 等标「✅ 题面」，但题面仅给 3 个硬约束（推力持续 5s、承受 ≤5g、最高高度 <3000m），其余为团队文献假设，建议改标「✅ 文献假设」；② 题面四阶段自「火箭马达推力加速」起，无独立「导轨射出」段，FACTS 的①导轨射出 + v_e 属建模细化，须在 §2 注明是补充假设；③ 题面明确列「风力」为因素，FACTS 未处理风向，§2 须声明该简化；④ AI 使用声明为学校强制（附件须标注 AI 名称/交互过程/结果，或声明未使用）—— 团队已有 `论文生产规范库/01_官方红线与合规/AI合规三件套.md` 脚手架，非缺口。核验依据见 `01_OUTBOX/writer/sec1_problem.md`、`sec2_analysis.md`。—— 进展：① FACTS 口径标签——**经核验 v0/h0/m/β/v_e 等本就标 ✅ 文献假设，仅 t1/a_lim/h_ox 为 ✅ 题面，标签无误**；PR #13 已在 FACTS §3.1 加来源分类说明，无需改标签；② 导轨段已在 `sec2_analysis.md` 2.3 落实；③ 风力简化已在 2.1 落实；④ AI 声明 PDF 已指派 writer（任务2，进行中），脚手架 `论文生产规范库/01_官方红线与合规/AI合规三件套.md`。

## 📢 公告

- 2026-09-04 16:20：**代码手两个疑问已由建模手答复**，见 `docs/decisions-2026-09-04.md`（必读，H7/H8 判据公式在里面）。要点：①阶段①＝火箭推力 5s，`v_e` 是 t=0 初始条件、导轨段不单独建模，5g 只约束火箭段；②H8 用飞机随体系喷流锥判据，推力方向与喷流方向无需一致；③**H7 改为以垂尾为准**（新增 s_vt=7、h_vt=5.5）；④SPEC 的 P1 新增 `vt_clear_min`、`burn_clear_min` 两个连续量字段。**粗算提示：T_min 的紧约束可能是"越过垂尾"而非 5g，请 coder 输出各约束的 binding 情况。**
- 2026-09-04 13:30：**赛题 = 模拟三 B 题 飞行员空中弹射，FACTS 已弹射化并锁定全部参数**——输入参数 17 项 + 敏感性区间见 `00_CONTRACT/FACTS.md`；results.json schema 已换新（P1: T_min/h_min/a_max_g…，P2: theta_sweep/T_opt…）见 `00_CONTRACT/SPEC.md`。旧 C 题 schema 作废。
- 2026-09-04 12:40：开工指令已就位——coder 读 `docs/start-coder.md`、writer 读 `docs/start-writer.md`、modeler 读 `docs/start-modeler.md`（契约 skill 会自动指到对应文件）。**先 pull、认领角色、认领起步任务，再动手。**
- 2026-09-04：契约升级 v2——三角色分工（modeler/coder/writer）、PR 自动校验闸、按角色分区看板。**数字一律用 `{{占位符}}`，禁止手抄。**

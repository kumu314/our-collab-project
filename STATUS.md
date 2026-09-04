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
| writer | 论文手 | ⬜ 待认领 |

## 🚀 进行中

### modeler（建模手）

- [modeler] 数模契约并入仓库 — 100% — 2026-09-03 — FACTS/SPEC/模板/脚本/自动加载 skill 已就位
- [modeler] FACTS 弹射题版 v2（五项参数调研 + 拍板锁定）— 100% — 2026-09-04 — 本 PR

### coder（代码手）

- [coder] 【coder 起步】确认 results.json schema + 搭求解骨架 + 产出首版 results.json — 100% — 2026-09-04 — 骨架已搭好（首版数值 11122 N 为旧参数，已被下方修正版取代）
- [coder] P1 主模型求解与结果 — 100% — 2026-09-04 — solve.py 按 model-spec + FACTS v2.1 重跑：T_min=2474.92 N（≈建模手预演 2520 N，稠密采样修复后三者吻合），h_min=1912.17 m（开伞高度，H7 为 binding），a_max_g=3.75（<5g），sep_x_min=2.59 m，vt_clear_min=1.17 m，burn_clear_min=5.98 m；fig4-1 轨迹图 + fig5-1 帕累托前沿（膝点 T*=6246.47 N）；results.json 通过 check_schema.py
- [coder] 敏感性分析 — 100% — 2026-09-04 — v0/h0/β/m 四参数扫描入 results.json.sensitivity：v0↑/β↑/m↑→T_req↑，h0 不变（T_req 与 h0 解耦，符合 H7 早期掠过判据）

### writer（论文手）

- （暂无）

## 📋 待认领（认领 = 整行搬到自己的分区）

- 【writer 起步】写 §1 问题重述 + §2 问题分析（writer，预估 3h）— 不依赖数字，数字一律占位符，指令见 docs/start-writer.md
- 【modeler 起步】填 FACTS.md 口径 + 假设清单 + 符号表（modeler，预估 1h）— ✅ 已完成：弹射版 v2 已入 main
- P2 倾角 θ 扫描与最优弹射方案（coder，预估 5h）— 输出 results.json P2 字段 + θ 扫描图
- 章节 3–4 建模过程与求解算法写作（writer，预估 6h）— sec3~sec4
- 章节 5 结果分析写作（writer，预估 4h）— sec5，依赖 results.json
- 代码附录整理（writer，预估 2h）— 按代码附录规范

## ✅ 已完成

- （暂无）

## 🚧 待评审

- （暂无）

## ⚠️ 风险 / 阻塞

- ~~FACTS.md 口径待填（全队第一阻塞）~~ → **已解除**：弹射版 v2 已锁定（2026-09-04），coder/writer 可直接开工
- 论文手尚未在 ROLES.md 认领角色
- ~~【待 modeler 定口径】`h_min` 语义不清~~ → **已解除**：建模手在 PR #10 拍板 `h_min` = 推荐工作点 (T*≈6246 N, h0=1500 m) 下开伞前最低海拔（开伞高度）= 1912.17 m，已写入 results.json.P1.h_min
- ~~【待 modeler 定口径】`vt_clear_min` 精度~~ → **已解除**：results.json 改为存全精度（不四舍五入），vt_clear_min=1.171 m，binding 信息保留

## 📢 公告

- 2026-09-04 16:20：**代码手两个疑问已由建模手答复**，见 `docs/decisions-2026-09-04.md`（必读，H7/H8 判据公式在里面）。要点：①阶段①＝火箭推力 5s，`v_e` 是 t=0 初始条件、导轨段不单独建模，5g 只约束火箭段；②H8 用飞机随体系喷流锥判据，推力方向与喷流方向无需一致；③**H7 改为以垂尾为准**（新增 s_vt=7、h_vt=5.5）；④SPEC 的 P1 新增 `vt_clear_min`、`burn_clear_min` 两个连续量字段。**粗算提示：T_min 的紧约束可能是"越过垂尾"而非 5g，请 coder 输出各约束的 binding 情况。**
- 2026-09-04 13:30：**赛题 = 模拟三 B 题 飞行员空中弹射，FACTS 已弹射化并锁定全部参数**——输入参数 17 项 + 敏感性区间见 `00_CONTRACT/FACTS.md`；results.json schema 已换新（P1: T_min/h_min/a_max_g…，P2: theta_sweep/T_opt…）见 `00_CONTRACT/SPEC.md`。旧 C 题 schema 作废。
- 2026-09-04 12:40：开工指令已就位——coder 读 `docs/start-coder.md`、writer 读 `docs/start-writer.md`、modeler 读 `docs/start-modeler.md`（契约 skill 会自动指到对应文件）。**先 pull、认领角色、认领起步任务，再动手。**
- 2026-09-04：契约升级 v2——三角色分工（modeler/coder/writer）、PR 自动校验闸、按角色分区看板。**数字一律用 `{{占位符}}`，禁止手抄。**

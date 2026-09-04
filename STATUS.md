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
| writer | 论文手 | ⬜ 待认领 |

## 🚀 进行中

### modeler（建模手）

- [modeler] 数模契约并入仓库 — 100% — 2026-09-03 — FACTS/SPEC/模板/脚本/自动加载 skill 已就位

### coder（代码手）

- （暂无）

### writer（论文手）

- （暂无）

## 📋 待认领（认领 = 整行搬到自己的分区）

- 【coder 起步】确认 results.json schema + 搭求解骨架 + 产出首版 results.json（coder，预估 2h）— P1 有数 / P2 P3 可 null，指令见 docs/start-coder.md
- 【writer 起步】写 §1 问题重述 + §2 问题分析（writer，预估 3h）— 不依赖数字，数字一律占位符，指令见 docs/start-writer.md
- 【modeler 起步】填 FACTS.md 口径 + 假设清单 H1–H5 + 符号表（modeler，预估 1h）— 阻塞全队，最优先
- P1 主模型求解与结果（coder，预估 6h）— 输出 results.json + 图
- P2 政策场景建模（coder，预估 5h）— 输出 results.json 增量
- P3 灵敏度分析（coder，预估 4h）— 输出 sensitivity 字段
- 敏感性分析与备选模型（coder，预估 3h）— 独立负责
- 章节 3–4 建模过程与求解算法写作（writer，预估 6h）— sec3~sec4
- 章节 5 结果分析写作（writer，预估 4h）— sec5，依赖 results.json
- 代码附录整理（writer，预估 2h）— 按代码附录规范

## ✅ 已完成

- （暂无）

## 🚧 待评审

- （暂无）

## ⚠️ 风险 / 阻塞

- FACTS.md 口径待 modeler（建模手 kumu314）按真实赛题填——**全队第一阻塞**；填前先统口径再填数
- 代码手与论文手尚未在 ROLES.md 认领角色

## 📢 公告

- 2026-09-04 12:40：开工指令已就位——coder 读 `docs/start-coder.md`、writer 读 `docs/start-writer.md`、modeler 读 `docs/start-modeler.md`（契约 skill 会自动指到对应文件）。**先 pull、认领角色、认领起步任务，再动手。**
- 2026-09-04：契约升级 v2——三角色分工（modeler/coder/writer）、PR 自动校验闸、按角色分区看板。**数字一律用 `{{占位符}}`，禁止手抄。**

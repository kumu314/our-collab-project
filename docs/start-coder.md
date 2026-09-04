# 代码手（兼队长）· 开工指令

> 本文件由建模手（modeler）维护。你的 agent 打开本仓库时会自动加载契约 skill，
> 那里会指向本文件。**照着做，不要自己发明流程。**

## 你是谁

- 角色 id：`coder`
- 团队身份：**代码手，兼队长**（管进度、定技术选型、催活）
- 你能写：`01_OUTBOX/coder/`
- 你不能写：`00_CONTRACT/`（数字口径）、`scripts/`（统稿工具）、别人的 `01_OUTBOX/`
  → 有问题在 STATUS.md「风险/阻塞」登记，让 modeler 改

> 为什么队长不能改数字口径：若一人既能改 FACTS.md 口径、又能改 results.json schema、还能自己合 PR，
> 那套「数字不手抄、脚本自动回填 + 对账」的机制等于没上锁。

---

## 第 0 步：认领角色（10 秒）

```
git checkout main
git pull origin main
```

打开 `00_CONTRACT/ROLES.md`，在 `coder` 那一行填上你的姓名 + GitHub 账号，保存。

---

## 第 1 步：本次任务 —— 出首版 `results.json`

**任务名（认领时照抄）**：
`【coder 起步】确认 results.json schema + 搭求解骨架 + 产出首版 results.json（P1 有数 / P2 P3 可 null）`

### 1.1 认领任务

把 `STATUS.md`「待认领」里上面这一行**整行搬**到「进行中 → coder」分区，行首改成：
```
- [coder] 【coder 起步】… — 0% — 预计 2 小时 — 刚开始
```

### 1.2 建分支

```
git checkout -b agent/coder/first-results main
```

### 1.3 干活

1. **读 `00_CONTRACT/SPEC.md` 第二节**，确认 results.json 的 schema 你能接受。
   - 字段不够用 / 命名不合理 → **不要自己改**，在 STATUS.md 风险区写清楚，让 modeler 改 SPEC。
2. **搭求解骨架**：数据读取 → 模型构建 → 求解入口 → 结果写盘。代码放 `01_OUTBOX/coder/`。
3. **产出首版 `01_OUTBOX/coder/results.json`**：
   - 严格按 SPEC 的字段名，**不许加、不许删、不许改**
   - 跑出来的填数；**跑不出来写 `null`，绝不编数**
   - 不四舍五入到整数，保留 2 位小数
   - **UTF-8 无 BOM**（Windows PowerShell 5.1 写 JSON 默认带 BOM，会炸）
   - 更新 `meta.generated_at` 和 `meta.seed`

### 1.4 交付与验收

```
git add .
git commit -m "feat: coder 首版 results.json（P1 有数 / P2 P3 null）"
git push -u origin agent/coder/first-results
```

提 PR：base `main`，标题 `[coder] 首版 results.json`。

**验收标准（PR 会自动跑校验）**：
- [ ] 只碰了 `01_OUTBOX/coder/`
- [ ] results.json 过 schema 校验（`scripts/check_schema.py`）
- [ ] 没有编造数字（跑不出的字段是 `null`）
- [ ] STATUS.md 只动了自己那一行

---

## 依赖与阻塞

| 你等谁 | 等什么 | 状态 |
|--------|--------|------|
| modeler | FACTS.md 客户总数 / 绿色区客户数 / 时间窗类型 / 是否拆分配送 / 成本口径 | ⬜ 未定（建模手在填） |
| modeler | 假设清单 H1–H5（你要逐条跟代码核对） | ⬜ 未定 |

**口径没定之前**，先搭骨架、跑通数据读取和求解流程，别急着定最终参数。
骨架通了以后口径一变，改参数即可。

## 队长额外职责

- 每天看一眼 STATUS.md，谁卡住就喊一声
- 论文手（writer）的 §5 完全依赖你的 results.json —— **出数后立刻在 STATUS.md 写 `📌 给 writer：P1 数字已出`**

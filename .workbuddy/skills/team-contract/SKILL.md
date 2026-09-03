---
name: team-contract
description: 本仓库的数模协作契约。任何 agent 在本仓库工作前必须先读本文件，严格遵守「分支隔离」「只读区/只写区」与「数字引用」规则。触发词：数模、写论文、写代码、出图、统稿、交接、STATUS。
---

# 数模协作契约（所有 agent 的共同大脑）

> **这份文件会被本仓库下所有人的 agent 自动加载**（位于 .workbuddy/skills/team-contract/）。
> 三个人产出差异巨大、整合要花几小时，根因不是模型不够聪明，而是三个 agent 拿到不同上下文。这份契约把上下文拉齐。

---

## 一、开工前必读（按顺序，30 秒）

| # | 文件 | 读它为了什么 |
|---|------|-------------|
| 1 | `STATUS.md` | 任务看板，看谁在做什么、有没有冲突（仓库统一真相源） |
| 2 | `00_CONTRACT/FACTS.md` | 所有数字、符号、口径的唯一真源 |
| 3 | `00_CONTRACT/SPEC.md` | results.json 的 schema、命名契约、占位符回填机制 |
| 4 | `docs/math-section-template.md` | writer 要填的死模板 |
| 5 | `docs/math-style.md` | 数模文风（去 AI 痕迹） |

**不读完不许动手写。**

---

## 二、分支隔离 + 只读/只写区（Git 仓库版）

本仓库用 **Git 分支隔离**（不是同步盘）：每人从 main 拉自己的分支 `agent/<id>/<任务>`，只在自己分支上改，做完提 PR 由整合人合并。这样从物理上杜绝写冲突。

| 区域 | 你能做什么 | 说明 |
|------|-----------|------|
| `00_CONTRACT/` | **只读** | 只有队长（captain）能改，且通过 PR 合入 main。发现问题 → 在 STATUS.md 的「风险/阻塞」登记，让队长改 |
| `01_OUTBOX/coder/` | coder 在自己的**分支**上写 | results.json + 图 + 表 CSV |
| `01_OUTBOX/writer/` | writer 在自己的**分支**上写 | sec*.md 章节稿 |
| `STATUS.md` | 通过 PR 更新自己的任务行 | 不要直接改别人的任务；看板靠 PR 流转 |
| `scripts/` | **只读**（除 captain） | 统稿脚本，只有队长维护 |
| `.workbuddy/skills/` | **只读** | 本契约自身 |

> 冲突处理见 `docs/integration-guide.md`：谁后提交谁先解决，解决不了找整合人。

---

## 三、数字引用规则（★ 最重要）

1. 论文里每个数字，只能来自 `00_CONTRACT/FACTS.md` 或 coder 产出的 `results.json`
2. 禁止手抄：不要把 A 文件数字敲进 B 文件
3. 禁止估算：agent 不得"合理推测"任何数值
4. FACTS.md 里没有的数字 → 在 STATUS.md 登记为「待产出」，不要自己编

### 写法（与 00_CONTRACT/SPEC.md 第三节、scripts/fill.py 严格一致）
```markdown
❌ 错误：总成本为 76832.06 元。
✅ 正确：总成本为 {{P1.total_cost}} 元。             （来自 results.json 路径）
✅ 正确：新能源车 {{P2.nev_count - P1.nev_count}} 辆。 （支持四则运算）
✅ 正确：绿色区客户 {{FACTS.green_zone_count}} 个。  （来自 FACTS.md 数值表）
```
> 图题注不写占位符：writer 直接把 results.json 的 figures[].caption 复制到 `![图X-X ...](...)` 的 alt 文本。
> 队长统稿跑 `scripts/fill.py` 批量回填，比三人各抄可靠 10 倍。

---

## 四、命名契约

| 类型 | 规范 | 示例 |
|------|------|------|
| 图 | `fig<图号>_<内容>.png` | `fig5-3_p1_vs_p2.png` |
| 表数据 | `table<表号>_<内容>.csv` | `table5-2_p1_vs_p2.csv` |
| 结果 | `results.json`（固定名） | `01_OUTBOX/coder/results.json` |
| 章节稿 | `sec<章号>_<内容>.md` | `sec5_results.md` |
| 代码 | 动词开头小写下划线 | `solve_p1.py` |

coder 必须按 SPEC.md 的 schema 输出 results.json，字段名不许改。

---

## 五、完成信号（在 STATUS.md 认领/更新，让别人看得见）
按 `docs/agent-workflow.md`：在 STATUS.md 把任务从「待认领」移到「进行中」并填进度，提交到自己的分支推 PR。追加不覆盖。

---

## 六、交接规则

| 情况 | 动作 |
|------|------|
| 需别人产出才能继续 | STATUS.md 写 `⏳ 等待 coder 的 results.json` |
| 你产出了别人要的 | STATUS.md 写 `📌 给 writer：P1 数字已出` |
| 发现契约(FACTS/SPEC)有错 | 不要自己改，在 STATUS.md 登记让 captain 修正 |
| 你的产出被依赖 | 完成后立刻更新 STATUS.md |

---

## 七、禁止事项

- ❌ 直接改 main（一切走 PR）
- ❌ 改别人的 `01_OUTBOX/` 文件（在自己的分支也只碰自己目录）
- ❌ 改 `00_CONTRACT/`（发现问题就报告）
- ❌ 手抄/估算数字
- ❌ 自己发明文件名
- ❌ 没做完声称完成

---

## 八、写完自检（30 秒）

- [ ] 产出都在 `01_OUTBOX/<我的角色>/`？
- [ ] 文件名符合命名契约？
- [ ] 数字都是占位符或引用，没手抄？
- [ ] STATUS.md 任务状态已更新并提了 PR？
- [ ] 没动过别人的文件？

---

## 九、角色边界

| 角色 | 负责 | 产出落在 | 不负责 |
|------|------|---------|--------|
| **captain**（队长） | 契约、假设、符号、统稿、合 PR | `00_CONTRACT/` + `scripts/` | 不写代码、不写初稿正文 |
| **coder**（代码手） | 求解、敏感性、**所有图/表数据**、`results.json` | `01_OUTBOX/coder/` | 不写论文段落 |
| **writer**（论文手） | 按模板填章节、图表题注、参考文献 | `01_OUTBOX/writer/` | 不算数、不产图 |

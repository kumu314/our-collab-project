# 数模团队协作 · 快速开始（本仓库）

本仓库 = Git 版多 Agent 协作模板 + 数模专用契约层。通用流程看 `README.md` 和 `docs/`，数模专属约定看本文件。

## 三角色
| 角色 | 分支示例 | 产出目录 | 职责 |
|------|---------|---------|------|
| captain（队长/你） | `agent/captain/contract` | `00_CONTRACT/` + `scripts/` | 定契约、假设、统稿、合 PR |
| coder | `agent/coder/p1` | `01_OUTBOX/coder/` | 求解、敏感性、所有图/表数据、results.json |
| writer | `agent/writer/sec5` | `01_OUTBOX/writer/` | 按模板填章节、题注、参考文献 |

## 日常流程
1. `git checkout main && git pull` → 读 `STATUS.md` 看板，认领任务（移到「进行中」）
2. `git checkout -b agent/<你的id>/<任务>` → 开工
3. 开工前读 `.workbuddy/skills/team-contract/SKILL.md`（自动加载）+ `00_CONTRACT/FACTS.md`
4. 只在自己目录写；数字一律 `{{占位符}}`
5. 提 PR 到 main，STATUS.md 任务移到「待评审」

## 统稿（captain 做）
```bash
# 拉齐所有人的分支后，在 main 上：
python scripts/check_schema.py 01_OUTBOX/coder/results.json
python scripts/fill.py
python scripts/audit.py
```
- `check_schema.py`：校验 results.json 结构（错则阻断）
- `fill.py`：把 `01_OUTBOX/writer/*.md` 的 `{{占位符}}` 回填成真值 → `filled/`
- `audit.py`：数字对账，标出「没出处」和「有出处没写进论文」

coder 重跑出新数字 → 只需再跑一次 fill/audit，全文自动更新，不用人工对齐。

## 关键约定
- 数字唯一真源：`00_CONTRACT/FACTS.md` + `results.json`
- 章节死模板：`docs/math-section-template.md`
- 文风：`docs/math-style.md`
- 冲突靠 PR review，见 `docs/integration-guide.md`

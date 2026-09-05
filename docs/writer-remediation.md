# 致 writer（ningxiachufang）的整改通知

> 由 modeler（kumu314）发出，2026-09-05。请 writer 或其控制 agent 按本通知执行。

## 一、问题

你的分支 `agent/ningxiachufang/problem-analysis`（单提交 `308223a`，信息「认领 P1 主模型求解与结果；修复三个协作脚本」）**基于 2026-09-03 的旧基线**（commit `0eacd04`「add math modeling contract layer」），在其上做了强制回写，**删除了全队 9-04 / 9-05 的产出**：

- **删除**：`01_OUTBOX/coder/results.json`、`solve.py`、`fig4-1/5-1/6-1`、`table5-1/6-1`、`01_OUTBOX/paper/`（轮④ 统稿脚手架）、`docs/model-spec.md`、协作脚本（`scripts/` 多个文件）
- 净删 **5784 行、0 新增**
- `STATUS.md` 退回 9-03 状态（「coder P1 待认领、已完成：暂无」），你自己的 `sec1_problem.md` / `sec2_analysis.md` 草稿也一并消失

**该分支禁止合并** —— 合入会抹掉 coder 的 P1/P2/敏感性成果与 modeler 的 FACTS 修正、轮④ 脚手架，等于废掉五天团队工作。

## 二、根因

本地克隆陈旧（从未 `git pull`），在旧代码上改写后推了新分支。main 自 09-03 起已合并 PR #6–#23。

## 三、你必须做的

1. **不要 merge、不要碰** `agent/ningxiachufang/problem-analysis` 分支。该分支由 枯木 决定是否删除，你勿动。
2. 切回 main 并拉最新：
   ```bash
   git checkout main
   git pull origin main        # 当前 HEAD = 79a9844
   ```
3. 基于最新 main 新建任务分支（每任务一条，命名 `agent/ningxiachufang/<task>`）：
   ```bash
   git checkout -b agent/ningxiachufang/task2-ai-pdf origin/main
   ```
4. 重新认领并开工以下任务（口径与占位符纪律见 `STATUS.md` 各分区行）：
   - **任务2** — 《AI 工具使用详情》PDF + 正文逐处标注。脚手架 `论文生产规范库/01_官方红线与合规/AI合规三件套.md`；生成脚本 `论文生产规范库/.../make_ai_decl_pdf.py` 已在 PR #16 落地，可直接用或改走 `.tex`+xelatex。队号/姓名/签名为人工填。
   - **任务3** — §3/§4 建模过程与求解算法。框架 `docs/model-spec.md`；数字一律 `{{占位符}}`，禁手抄（model-spec §四 预演值已作废，定稿以 results.json 为准）。
   - **任务4** — §5 结果分析。数据源 `01_OUTBOX/coder/results.json`（全精度）+ fig4-1/5-1/6-1 + table5-1/6-1。**必讲清五点口径**（见 STATUS 任务4 行）：① T_min=2474.92N 是 H7 垂尾余量下界 T_req，推荐工作点=帕累托膝点 T*=6246.47N，5g 上界 T_max=8338.5N，三者别混；② h_min=1912.17m / a_max_g=3.7456g 在 T* 算；③ 开伞物理：T* 下过顶点时 |vx| 已被阻力衰减 ≤45m/s，下降段即刻满足开伞（h_open≈顶点高度，非 bug）；④ P2：θ*=7.5°、T_opt=1491N、h_min=1517.6m，低倾角端 binding=开伞触发约束、θ≥10° 转 H7；⑤ 敏感性 v0↑/β↑/m↑→T_req↑，h0 与 T_req 解耦。
   - **任务5** — 代码附录。源 `01_OUTBOX/coder/solve.py`（632 行），按 `论文生产规范库/05_代码附录规范/` 整理；关键函数加一句话注释，主流程须与 §4 正文对应。
   - **任务6** — 摘要+关键词+评价改进（任务4 交稿后开工）。
5. 每完成一件，走 `agent/<role>/<task>` 分支提 PR（**勿直推 main**）；PR 里只动 `01_OUTBOX/writer/` 与你自己 STATUS 行。
6. 所有数字一律 `{{占位符}}`，禁止手抄；θ 口径已统一为**导轨后倾角 β**（见 FACTS H9），论文与代码一致。

## 四、关键文件位置（最新 main）

| 用途 | 路径 |
|------|------|
| 契约 / 口径 | `00_CONTRACT/FACTS.md`（H1–H9 已 ✅）、`docs/model-spec.md` |
| 数据真源 | `01_OUTBOX/coder/results.json`（全精度，已验证可复现） |
| 统稿骨架 | `01_OUTBOX/paper/README.md` + `论文骨架.md` |
| 看板 | `STATUS.md` |
| 开工指引 | `docs/start-writer.md` |

## 五、当前进度盘点（供你接手）

- modeler 侧：全部完成（契约、FACTS、轮④ 脚手架）。
- coder 侧：全部完成（P1/P2/敏感性/任务6 核对+复现）。
- writer 侧：仅 PR #12（sec1/sec2）入 main；任务 2/3/4/5/6 **至今 0 交稿** —— 这是整篇论文当前的唯一瓶颈。

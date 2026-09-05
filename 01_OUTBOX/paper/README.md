# 01_OUTBOX/paper —— 论文定稿统稿区

> 轮④「全文整合排版 + 质检出稿」工作区（modeler 任务6 建立）。
> 章节正稿由 writer 交到 `01_OUTBOX/writer/`，统稿时 `scripts/fill.py` 按文件名排序拼接并回填数字。

## 一、章节文件命名规范（排序即章节序）

fill.py 匹配 `01_OUTBOX/writer/sec*.md` 并**按文件名排序**拼接成 `filled/草稿_回填版.md`。
**文件名字典序 = 论文章节序**，命名错了章节就乱序。

| 文件名 | 章节 | 产出任务 | 状态 |
|---|---|---|---|
| sec0_abstract.md | 摘要 + 关键词 | writer 任务6 | ⬜ 排队 |
| sec1_problem.md | §1 问题重述 | writer 起步 | ✅ PR #12 |
| sec2_analysis.md | §2 问题分析 | writer 起步 | ✅ PR #12 |
| sec3_model.md | §3 模型建立 | writer 任务3 | ⬜ 进行中 |
| sec4_algorithm.md | §4 求解算法 | writer 任务3 | ⬜ 进行中 |
| sec5_results.md | §5 结果分析 | writer 任务4 | ⬜ 进行中 |
| sec6_evaluation.md | §6 模型评价与改进 | writer 任务6 | ⬜ 排队 |
| sec7_references.md | 参考文献 | writer 任务2 一并产出 | ⬜ 进行中 |
| sec8_appendix.md | 附录（§8.1 交付物清单 + 代码附录） | writer 任务5 | ⬜ 进行中 |

**硬规则**：
- 只准 `sec<数字>_名称.md`，禁止中文文件名、禁止跳号；
- 章节标题格式 `## <n>、<章名>`（见 `docs/math-section-template.md`），文件内不带页眉页脚；
- 数字一律 `{{占位符}}`（`{{P1.T_min}}` / `{{FACTS.m}}`），禁手抄——fill.py 统一回填；
- **论文数值唯一来源 = `01_OUTBOX/coder/results.json`**；model-spec §四预演值仅作历史记录，禁止当定稿。

## 二、轮④ 统稿流程（六步）

```bash
# 0. 前置：coder 复现自检（任务6）已过，results.json 结构合规
python scripts/check_schema.py 01_OUTBOX/coder/results.json

# 1. 回填：占位符 -> 真值（输出 filled/）
python scripts/fill.py

# 2. 数字对账：全文数值必须能溯源 results.json / FACTS.md
python scripts/audit.py

# 3. AI 合规三件套自检（缺一即材料不全）
#    ①正文 AI 标注块  ②参考文献 [5] WorkBuddy 条目  ③《AI 工具使用详情》PDF
#    自检命令见 论文生产规范库/01_官方红线与合规/AI合规三件套.md 第四节
#    PDF 生成：python 论文生产规范库/03_流水线与脚本/scripts/make_ai_decl_pdf.py

# 4. 图表核对：fig4-1/5-1/6-1 + table5-1/6-1 的编号、标题、正文引用三方一致

# 5. 拼装定稿：按本目录 论文骨架.md 组装（标题页人工填队号/队员），正文注入 filled/草稿_回填版.md

# 6. 出稿：PDF + docx 双格式（论文生产规范库/03_流水线与脚本/make_docx.py）
```

## 三、出稿前自检清单

- [ ] `fill.py` 报告 0 个未解析占位符
- [ ] `audit.py` 无「未溯源数字」（writer 五件全部交齐后跑）
- [ ] `check_schema.py` 通过
- [ ] **口径三兄弟讲清**：T_min=2474.92 N 是 H7 垂尾余量 0.5 m 下界 T_req；推荐工作点 = 帕累托膝点 T*=6246.47 N；h_min=1912.17 m / a_max_g=3.7456g 在 T* 工作点算——三者别混
- [ ] **开伞物理写对**：T* 下过弹道顶点时 |vx| 已被气动阻力衰减到 45 m/s 以下，下降段条件即刻满足（h_open≈顶点高度）——是阻力衰减的自然结果，不是"顶点开伞 bug"
- [ ] **binding 分析写全**：H7 主导；θ≤7.5° 低倾角端卡开伞触发约束、θ≥10° 转 H7
- [ ] **敏感性结论写全**：v0↑/β↑/m↑→T_req↑；h0 与 T_req 解耦（H7 为相对判据）
- [ ] AI 三件套齐：正文标注块 / 参考文献 [5] 条目 / 1 页 PDF（文件名禁含"占位/示例/草稿"，队号/姓名/签名人工填）
- [ ] 图 4-1/5-1/6-1 与表 5-1/6-1 在正文均有引用且编号一致
- [ ] 标题页队号/队员人工填写，签名留白（AI 不代填）

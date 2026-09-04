# 论文手 · 开工指令

> 本文件由建模手（modeler）维护。你的 agent 打开本仓库时会自动加载契约 skill，
> 那里会指向本文件。**照着做，不要自己发明流程。**

## 你是谁

- 角色 id：`writer`
- 负责：按模板填章节、图表题注、参考文献
- 你能写：`01_OUTBOX/writer/`
- 你不能写：`00_CONTRACT/`、`scripts/`、别人的 `01_OUTBOX/`
- 你**不算数、不产图** —— 一切数字从 `results.json` / `FACTS.md` 来，用占位符引

---

## 第 0 步：认领角色（10 秒）

```
git checkout main
git pull origin main
```

打开 `00_CONTRACT/ROLES.md`，在 `writer` 那一行填上你的姓名 + GitHub 账号，保存。

---

## 第 1 步：本次任务 —— 写 §1 问题重述 + §2 问题分析

**任务名（认领时照抄）**：
`【writer 起步】写 §1 问题重述 + §2 问题分析（不依赖数字，数字一律占位符）`

**为什么先写这两节**：§5 结果分析要等代码手的 results.json，现在写会空转。
§1、§2 只依赖建模手的模型框架，可以立刻动笔。

### 1.1 认领任务

把 `STATUS.md`「待认领」里上面这一行**整行搬**到「进行中 → writer」分区，行首改成：
```
- [writer] 【writer 起步】… — 0% — 预计 3 小时 — 刚开始
```

### 1.2 建分支

```
git checkout -b agent/writer/sec1-sec2 main
```

### 1.3 干活（先读这三份，不读完不许动笔）

1. `docs/math-section-template.md` —— 章节的死模板，按它填
2. `docs/math-style.md` —— 数模文风，去 AI 痕迹
3. `00_CONTRACT/FACTS.md` —— 口径和符号的唯一真源

产出两个文件，放 `01_OUTBOX/writer/`：

| 文件 | 内容 |
|------|------|
| `sec1_problem.md` | 问题重述：背景、两个问题（Q1 水平飞行最小推力+最低高度；Q2 倾角 θ 最优弹射方案）、参数假设来源（FACTS.md） |
| `sec2_analysis.md` | 问题分析：假设、符号说明、建模思路 |

### 1.4 写作硬规则（违反会被打回）

- **一切数字写占位符**，禁止手抄、禁止估算：
  - `最小推力为 {{P1.T_min}} N`
  - `最低飞行高度 {{P1.h_min}} m`（数组可下标：`{{P2.T_opt[1]}}`）
  - `人椅系统质量 {{FACTS.m}} kg`
- 图引用写「**如图 5-1 所示**」，**禁写** `见 xxx.png`
- 图题注不写占位符，直接引用 results.json 里 `figures[].caption`
- 不用「值得注意的是 / 不难看出 / 综上所述 / 随着…的不断发展」
- 段落 3–5 句，长短交替；长句拆短句
- 标题层级：顶级中文数字（一、二、三），子节 `1.1` / `2.1`

### 1.5 交付与验收

```
git add .
git commit -m "feat: writer §1 问题重述 + §2 问题分析"
git push -u origin agent/writer/sec1-sec2
```

提 PR：base `main`，标题 `[writer] §1 + §2`。

**验收标准**：
- [ ] 只碰了 `01_OUTBOX/writer/`
- [ ] 文件名 `sec<章号>_<内容>.md`
- [ ] 所有数字都是 `{{占位符}}`，没有一个手抄
- [ ] 没有禁用套话
- [ ] STATUS.md 只动了自己那一行

---

## 依赖与阻塞

| 你等谁 | 等什么 | 状态 |
|--------|--------|------|
| modeler | FACTS.md 口径定稿 + 假设清单 + 符号表 | ⬜ 在建 |
| coder | results.json（写 §5 结果分析用） | ⬜ 未出 |

写 §1、§2 时若发现口径缺失 → **不要自己编**，在 STATUS.md 风险区登记，让 modeler 补。

## 下一步预告

§5 结果分析要等 coder 出数。出数前你可以先写 §3 模型建立（等 modeler 给框架）和 §4 求解算法（等 coder 给算法流程）。

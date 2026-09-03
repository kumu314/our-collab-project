# 多 Agent 协作模板（Git 版）

> 基于 Git 的轻量级多 Agent 协作方案。每人一个分支，看板同步状态，PR 合并成果。

## 快速开始

### 1. 初始化仓库

```bash
# 克隆或新建仓库
git init my-project
cd my-project

# 复制本模板到你的项目根目录
# （将 collab-template 下的所有文件/文件夹拷过去）
```

### 2. 配置你的身份

编辑 `AGENT_ID` 文件，写入你的 agent 名称（英文、小写、无空格）：

```
alice
```

### 3. 创建你的工作分支

```bash
# 从 main 拉分支，分支名格式：agent/<你的id>/<任务名>
git checkout -b agent/alice/login-page main
```

### 4. 开工前必读

1. `git pull origin main` — 同步最新主干
2. 打开 `STATUS.md` — 看谁在做什么，有没有冲突
3. 在 `STATUS.md` 里认领任务（把任务从「待认领」移到「进行中」，加上你的名字）
4. 提交你的认领变更：

```bash
git add STATUS.md
git commit -m "chore: alice 认领「登录页开发」"
git push origin agent/alice/login-page
```

### 5. 开始干活

- **只在自己的分支上改**，不要直接动 main
- **只碰自己负责的模块文件**，不要改别人模块
- 每完成一个小阶段，更新 `STATUS.md` 里的进度

### 6. 完成后提 PR

1. 把代码推到你的分支
2. 在 Git 平台（GitHub/GitLab/Gitea）发起 Pull Request
3. 目标分支：`main`
4. PR 标题格式：`[<agent-id>] <任务名>`
5. 填好 PR 模板里的 checklist
6. 在 `STATUS.md` 里把任务移到「待评审」

### 7. 评审与合并

由「整合人」负责评审，通过后合并到 `main`。合并后任务移到「已完成」。

---

## 目录结构

```
项目根目录/
├── README.md               ← 你正在看的文件
├── STATUS.md               ← 任务看板（唯一真相源）
├── AGENT_ID                ← 你的 agent 身份标识（每人不同，不提交到 git）
├── .gitignore
├── .github/
│   └── PULL_REQUEST_TEMPLATE.md   ← PR 模板
├── docs/
│   ├── agent-workflow.md   ← Agent 标准工作流程
│   ├── branching-guide.md  ← 分支管理规范
│   ├── commit-convention.md ← 提交信息规范
│   ├── style-guide.md      ← 代码/文档风格统一指南
│   └── integration-guide.md ← 整合人操作手册
└── scripts/
    ├── claim-task.ps1      ← 快速认领任务（Windows）
    ├── update-progress.ps1 ← 快速更新进度（Windows）
    └── submit-pr.ps1       ← 快速提交 PR 辅助（Windows）
```

---

## 核心原则

1. **看板唯一真相源**：谁在做什么，只看 `STATUS.md`，不靠聊天
2. **一人一分支**：每个 agent 在自己的分支干活，互不干扰
3. **模块化拆活**：按功能模块拆任务，每人交一个完整零件
4. **先定接口再开工**：模块之间的衔接处先写死，内部实现自由
5. **整合人制**：有一个最终把关的人（或 agent），负责合并和统一风格

---

## 常见问题

**Q: 两个人改了同一个文件怎么办？**
A: 正常，Git 会提示冲突。谁后提交谁解决冲突，解决不了找整合人。关键是拆任务时尽量避免多人碰同一文件。

**Q: 我想看看别人做到哪了？**
A: `git fetch origin` 然后 `git log origin/agent/<对方id>/<分支名>` 就能看到对方的提交历史。也可以直接看 `STATUS.md` 里的进度。

**Q: 输出风格差异太大合不到一起怎么办？**
A: 见 `docs/style-guide.md` —— 开工前先对齐格式规范。如果差异已经产生，由整合人在评审阶段统一调整。

**Q: 可以多个人用同一个 agent 账号吗？**
A: 不建议。身份乱了看板就没用了。每个操作者一个 `AGENT_ID`。

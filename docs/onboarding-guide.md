# 三 Agent 协作搭建指南（原子步骤）

> 给谁：三个队友，每人一台电脑，每人一个 agent
> 目标：按顺序走完以下步骤，三个人的 agent 就能在同一个 Git 仓库里协作
> 预计耗时：30-60 分钟（取决于 Git 熟悉程度）

---

## 前置准备（每人都要有）

- [ ] 一台能上网的电脑
- [ ] 安装了 Git（命令行输 `git --version` 有版本号就行）
- [ ] 一个 GitHub / GitLab / Gitee 账号（三个人用同一个平台）
- [ ] 一个你喜欢的代码编辑器（VS Code 推荐）

---

## 第 1 步：选一个人当「仓库管理员」

**只需要一个人做**，其他人等他弄好再继续。

### 1.1 新建 GitHub 仓库

1. 打开 GitHub → 右上角 `+` → `New repository`
2. 仓库名：比如 `our-collab-project`
3. 选 `Public` 或 `Private` 都行
4. **不要**勾选 "Add a README file"（我们后面自己加）
5. 点 `Create repository`

### 1.2 把协作模板推上去

仓库管理员在自己电脑上操作：

```bash
# 1. 进入刚才我给你的 collab-template 文件夹
cd d:\collab-template

# 2. 初始化为 git 仓库
git init

# 3. 配置你的身份（第一次用 git 要设）
git config user.name "你的名字"
git config user.email "你的邮箱@example.com"

# 4. 把所有文件加进去
git add .

# 5. 第一次提交
git commit -m "chore: 初始化协作模板"

# 6. 改主分支名叫 main（有的默认是 master）
git branch -M main

# 7. 关联到你刚建的 GitHub 仓库
#    把下面的 URL 换成你自己的仓库地址
git remote add origin https://github.com/你的用户名/our-collab-project.git

# 8. 推上去
git push -u origin main
```

### 1.3 邀请另外两个人加入仓库

1. 在 GitHub 仓库页面 → `Settings` → `Collaborators`
2. 点 `Add people`
3. 输入另外两个人的 GitHub 用户名
4. 点 `Add ... to this repository`
5. 他们会收到邮件/通知，**点接受邀请**

---

## 第 2 步：另外两个人克隆仓库

**另外两个人操作**，仓库管理员不用动。

### 2.1 接受邀请

检查邮箱或 GitHub 通知，点接受仓库邀请。

### 2.2 克隆到本地

```bash
# 找个地方放项目，比如 d:\projects\
cd d:\projects

# 克隆仓库（换成你们的仓库地址）
git clone https://github.com/仓库管理员用户名/our-collab-project.git

# 进入项目目录
cd our-collab-project

# 看看有没有文件
dir
# 应该能看到 README.md、STATUS.md、docs/ 这些
```

### 2.3 配置你的身份

```bash
git config user.name "你的名字"
git config user.email "你的邮箱@example.com"
```

### 2.4 设置你的 AGENT_ID

```bash
# 复制模板文件
copy AGENT_ID.example AGENT_ID

# 用编辑器打开 AGENT_ID，把 your-agent-id-here 改成你的代号
# 比如改成：alice （英文、小写、无空格）
```

> 三个人的 AGENT_ID 不能一样，比如 alice、bob、carol

---

## 第 3 步：第一次试跑——认领任务

**三个人都做一遍**，熟悉流程。

### 3.1 同步最新代码

每次开工前都要做这一步：

```bash
git checkout main
git pull origin main
```

### 3.2 打开 STATUS.md 看看板

用编辑器打开 `STATUS.md`，看看「待认领」里有哪些任务。

### 3.3 认领一个任务

每个人选一个不同的任务认领。

**手动方式（推荐新手）：**

1. 用编辑器打开 `STATUS.md`
2. 从「待认领」里选一个任务，把那一行剪下来
3. 粘贴到「进行中」下面，改成下面的格式：

```
- [你的agent-id] 任务名 — 0% — 预计 X 小时 — 刚开始
```

比如：
```
- [alice] 首页样式优化（4h） — 0% — 预计 4 小时 — 刚开始
```

4. 保存文件

### 3.4 创建你的工作分支

```bash
# 从 main 拉出你的分支，格式：agent/<你的id>/<任务名>
# 任务名用英文短横线连接
git checkout -b agent/alice/homepage-style main
```

### 3.5 提交你的认领

```bash
# 把 STATUS.md 的变更加进去
git add STATUS.md

# 提交（用你自己的 id 和任务名）
git commit -m "chore: alice 认领「首页样式优化」"

# 推送到远端
git push -u origin agent/alice/homepage-style
```

### 3.6 互相看看

这时候三个人都推送了自己的分支，你们可以：

```bash
# 看看远端有哪些分支
git fetch origin
git branch -r
# 应该能看到三个人的分支
```

也可以去 GitHub 仓库页面 → `Code` → `branches`，能看到所有分支。

---

## 第 4 步：第一次试跑——干活 & 更进度

**三个人各自做**，模拟一下真实干活的流程。

### 4.1 在你的分支上改点东西

随便改点什么，比如在 `docs/` 下新建一个文件，或者改改 README。

```bash
# 确认你在自己的分支上
git branch
# 当前分支前面有个 * 号，应该是 agent/xxx/xxx

# 新建一个文件（随便写点什么）
echo "# 我的工作记录" > docs/work-alice.md
```

### 4.2 更新进度

改完一点东西，就更新一下 `STATUS.md` 里的进度：

1. 打开 `STATUS.md`
2. 找到你那一行，把进度从 0% 改成 30%
3. 后面的备注也可以改改，比如「— 已完成首页头部样式」

然后提交：

```bash
git add STATUS.md docs/work-alice.md
git commit -m "feat: 完成首页头部样式"
git push origin agent/alice/homepage-style
```

> 💡 也可以用脚本：`.\scripts\update-progress.ps1 -TaskName "首页样式优化" -Progress 30 -AgentId "alice"`

### 4.3 看看队友的进度

```bash
# 同步远端信息
git fetch origin

# 看看 bob 提交了什么
git log origin/agent/bob/xxx-branch

# 看看 bob 改了哪些文件
git diff main origin/agent/bob/xxx-branch --stat
```

也可以直接打开 GitHub 看每个人的分支。

---

## 第 5 步：第一次试跑——提交 PR

**三个人各自做**，把模拟的任务"做完"，提交评审。

### 5.1 把任务做完

再改点东西，假装任务完成了，进度改成 100%。

```bash
# 再加点内容
echo "## 完成了" >> docs/work-alice.md

# 更新 STATUS.md 进度到 100%
# （手动编辑 STATUS.md）

git add .
git commit -m "feat: 完成首页样式优化"
git push origin agent/alice/homepage-style
```

### 5.2 在 GitHub 上发起 PR

1. 打开 GitHub 仓库页面
2. 会看到一个黄色提示条 "Compare & pull request"，点它
3. 或者：`Pull requests` → `New pull request`
   - base: `main`
   - compare: 你的分支 `agent/alice/homepage-style`
4. 标题格式：`[alice] 首页样式优化`
5. 描述里按模板填（模板会自动加载）
6. 点 `Create pull request`

### 5.3 把任务移到「待评审」

```bash
# 手动编辑 STATUS.md：
# 把你那行从「进行中」移到「待评审」
# 加上 PR 链接

git add STATUS.md
git commit -m "chore: alice 提交「首页样式优化」待评审"
git push origin agent/alice/homepage-style
```

> 💡 也可以用脚本：`.\scripts\submit-pr.ps1 -TaskName "首页样式优化" -AgentId "alice" -PrUrl "https://github.com/..."`

---

## 第 6 步：整合人评审 & 合并

**选一个人当整合人**（先轮流体验也行），做评审和合并。

### 6.1 评审 PR

1. 打开 GitHub → `Pull requests`
2. 点进一个 PR
3. 看改动了什么（`Files changed` 标签页）
4. 没问题就点 `Merge pull request`
5. 选 `Create a merge commit`
6. 点 `Confirm merge`
7. 合并完可以点 `Delete branch` 删掉远端分支

### 6.2 更新看板

合并完成后，整合人在 main 分支上更新 STATUS.md：

```bash
git checkout main
git pull origin main

# 手动编辑 STATUS.md：
# 把任务从「待评审」移到「已完成」，加上完成日期

git add STATUS.md
git commit -m "chore: 合并「首页样式优化」到 main"
git push origin main
```

### 6.3 每个人同步最新的 main

```bash
git checkout main
git pull origin main

# 看看 STATUS.md，任务已经在「已完成」里了
```

---

## 第 7 步：验证——三个人能互相看到

走到这里，你们已经完成了一轮完整的协作。验证一下：

- [ ] 三个人都能看到同一个 `STATUS.md` 看板
- [ ] 每个人都能在 GitHub 上看到另外两个人的分支和提交
- [ ] 任务能从「待认领」→「进行中」→「待评审」→「已完成」流转
- [ ] 代码能通过 PR 合并到 main，大家都能拉到

如果以上都 OK，恭喜，你们的多 agent 协作环境已经跑通了！

---

## 常见问题排查

### Q: git push 被拒绝了？

```
! [rejected]        main -> main (fetch first)
```

A: 别人先推了，你本地不是最新的。先 `git pull --rebase` 再 push。

### Q: 合并冲突了怎么办？

A: Git 会告诉你哪些文件冲突了。打开那些文件，找 `<<<<<<<`、`=======`、`>>>>>>>` 标记，手动选择保留哪一边的内容。改完后 `git add <文件>` 然后 `git rebase --continue`。

### Q: 我不小心改到 main 分支了？

```bash
# 把 main 上的改动移到你的分支
git stash
git checkout agent/你的分支
git stash pop
```

### Q: 怎么看谁改了什么？

```bash
# 看某个文件的修改历史
git log -p 文件名

# 看每一行是谁写的
git blame 文件名
```

### Q: 我想看队友的代码，但不想切分支？

```bash
# 看某个文件在队友分支上的内容
git show origin/agent/bob/xxx-branch:文件名

# 对比你和队友的差异
git diff agent/alice/homepage-style origin/agent/bob/xxx-branch
```

---

## 下一步

跑通第一轮后，就可以用真任务了。建议：

1. 先从简单的小任务开始，熟悉流程
2. 每个任务控制在 2-4 小时能做完的粒度
3. 每天开工前 `git pull` + 看 `STATUS.md`
4. 遇到问题先在 `STATUS.md` 的「风险/阻塞」里登记
5. 每周复盘一次，调整协作方式

祝协作顺利！

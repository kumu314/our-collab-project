# 分支管理规范

## 分支类型

| 类型 | 命名格式 | 说明 | 例子 |
|------|----------|------|------|
| 主干 | `main` | 唯一的稳定分支，永远可部署 | `main` |
| Agent 工作分支 | `agent/<id>/<task>` | 每个 agent 每个任务一条分支 | `agent/alice/login-page` |
| 热修复 | `hotfix/<描述>` | 线上紧急修复 | `hotfix/login-bug` |
| 功能集成分支 | `feature/<大功能名>` | 多个子任务合并用的中间分支 | `feature/user-system` |

---

## 分支生命周期

```
main ──→ agent/alice/login-page ──(PR)──→ main
        （alice 一个人在这上面干活）
```

1. **创建**：从 `main` 拉出
2. **使用**：只有对应的 agent 在上面提交
3. **同步**：定期 rebase 到最新的 main
4. **合并**：通过 PR 合并回 main
5. **删除**：合并后删除远端分支

---

## 同步主干的正确姿势

**用 rebase，不用 merge**，保持提交历史干净：

```bash
git fetch origin
git rebase origin/main
```

如果有冲突：
1. 解决冲突文件
2. `git add <冲突文件>`
3. `git rebase --continue`
4. 推送到远端需要加 `--force-with-lease`：
   ```bash
   git push --force-with-lease origin agent/<id>/<task>
   ```

> **注意**：只在自己的分支上 force push，绝对不要 force push 到 `main`。

---

## 什么时候开集成分支

当一个大功能拆成多个小任务，每个任务都有自己的 agent 分支，但它们需要先整合到一起再进 main 时，用集成分支：

```
main ──→ feature/user-system ──→ agent/alice/login-page ──(PR)──→ feature/user-system
       ↑                          agent/bob/user-api ───(PR)──→ ↑
       └────────────── 全部完成后，feature 分支整体合进 main ────────────────┘
```

操作方式：
1. 整合人从 main 拉出 `feature/user-system`
2. 各 agent 从 feature 分支拉出自己的工作分支
3. 各 agent 的 PR 目标是 feature 分支（不是 main）
4. 全部完成后，feature 分支整体提 PR 到 main

---

## 分支命名禁止事项

- ❌ 不要用中文分支名（Windows/Mac/Linux 处理不一致）
- ❌ 不要用空格，用 `-` 或 `_`
- ❌ 不要起 `dev`、`test` 这种模糊的名字——谁的 dev？测什么？
- ❌ 不要多个人共用一条工作分支

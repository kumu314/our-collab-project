# ============================================================
# 快速认领任务脚本（Windows PowerShell）
# 用法：.\scripts\claim-task.ps1 -TaskName "登录页开发" -AgentId "alice"
# ============================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$TaskName,

    [Parameter(Mandatory=$true)]
    [string]$AgentId,

    [string]$Estimate = ""
)

$ErrorActionPreference = "Stop"

# 检查是否在 git 仓库
if (-not (Test-Path .git)) {
    Write-Error "错误：当前目录不是 Git 仓库，请在项目根目录运行。"
    exit 1
}

$statusFile = "STATUS.md"
if (-not (Test-Path $statusFile)) {
    Write-Error "错误：找不到 $statusFile，请确认在项目根目录。"
    exit 1
}

# 读取 STATUS.md
$content = Get-Content $statusFile -Raw

# 检查任务是否在待认领里
if ($content -notmatch [regex]::Escape("- $TaskName")) {
    Write-Error "错误：在「待认领」里找不到任务「$TaskName」"
    Write-Host "请确认任务名完全一致，包括括号里的预估工时。"
    exit 1
}

# 检查任务是否已被认领
if ($content -match "\[$AgentId\] $TaskName") {
    Write-Error "错误：你已经认领了「$TaskName」"
    exit 1
}

# 生成分支名（任务名转成 kebab-case）
$branchTask = $TaskName.ToLower() -replace '[^\w\u4e00-\u9fa5]+', '-' -replace '^-|-$', ''
$branchName = "agent/$AgentId/$branchTask"

# 构建进行中的任务条目
$estimateText = if ($Estimate) { " — 预计 $Estimate" } else { "" }
$inProgressLine = "- [$AgentId] $TaskName — 0%$estimateText — 刚开始"

# 替换：从「待认领」移除，加到「进行中」
# 1. 移除待认领里的那一行
$content = $content -replace [regex]::Escape("- $TaskName") + ".*\r?\n", ""

# 2. 在「进行中」标题下加入
$content = $content -replace "(## .*进行中.*\r?\n\r?\n)", "`$1$inProgressLine`r`n"

# 写回文件
Set-Content -Path $statusFile -Value $content -NoNewline

Write-Host ""
Write-Host "✅ 已认领任务：$TaskName"
Write-Host "📂 分支名：$branchName"
Write-Host ""

# 询问是否创建分支并提交
$createBranch = Read-Host "要现在创建分支并提交吗？(Y/n)"
if ($createBranch -ne 'n' -and $createBranch -ne 'N') {
    git checkout -b $branchName main
    git add $statusFile
    git commit -m "chore: $AgentId 认领「$TaskName」"
    git push -u origin $branchName
    Write-Host ""
    Write-Host "🎉 搞定！分支 $branchName 已创建并推送到远端。"
} else {
    Write-Host "已更新 STATUS.md，记得手动提交和推送。"
}

# ============================================================
# 提交 PR 辅助脚本（Windows PowerShell）
# 用法：.\scripts\submit-pr.ps1 -TaskName "登录页开发" -AgentId "alice" -PrUrl "https://github.com/..."
# ============================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$TaskName,

    [Parameter(Mandatory=$true)]
    [string]$AgentId,

    [string]$PrUrl = ""
)

$ErrorActionPreference = "Stop"

$statusFile = "STATUS.md"
if (-not (Test-Path $statusFile)) {
    Write-Error "错误：找不到 $statusFile，请在项目根目录运行。"
    exit 1
}

$content = Get-Content $statusFile -Raw

# 找到进行中的任务行
$pattern = "\[{0}\] {1} — (\d+)%( — ([^\r\n]*))?" -f [regex]::Escape($AgentId), [regex]::Escape($TaskName)

if ($content -notmatch $pattern) {
    Write-Error "错误：找不到你进行中的任务「$TaskName」"
    exit 1
}

$oldLine = $Matches[0]

# 1. 从「进行中」移除
$content = $content.Replace($oldLine + "`r`n", "").Replace($oldLine + "`n", "")
# 如果是最后一行，可能没有换行
$content = $content.Replace($oldLine, "")

# 2. 加到「待评审」
$reviewLine = "- [$AgentId] $TaskName — 100%"
if ($PrUrl) { $reviewLine += " — PR: $PrUrl" }

$content = $content -replace "(## .*待评审.*\r?\n\r?\n)", "`$1$reviewLine`r`n"

Set-Content -Path $statusFile -Value $content -NoNewline

Write-Host ""
Write-Host "🚀 任务「$TaskName」已移到待评审"
if ($PrUrl) { Write-Host "🔗 PR 地址：$PrUrl" }
Write-Host ""

# 询问是否提交
$doCommit = Read-Host "要现在提交并推送吗？(Y/n)"
if ($doCommit -ne 'n' -and $doCommit -ne 'N') {
    git add $statusFile
    git commit -m "chore: $AgentId 提交「$TaskName」待评审"
    $currentBranch = git branch --show-current
    git push origin $currentBranch
    Write-Host ""
    Write-Host "✅ 已提交并推送。等整合人评审吧！"
}

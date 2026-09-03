# ============================================================
# 快速更新任务进度脚本（Windows PowerShell）
# 用法：.\scripts\update-progress.ps1 -TaskName "登录页开发" -Progress 60 -AgentId "alice"
# ============================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$TaskName,

    [Parameter(Mandatory=$true)]
    [int]$Progress,

    [Parameter(Mandatory=$true)]
    [string]$AgentId,

    [string]$Note = ""
)

$ErrorActionPreference = "Stop"

$statusFile = "STATUS.md"
if (-not (Test-Path $statusFile)) {
    Write-Error "错误：找不到 $statusFile，请在项目根目录运行。"
    exit 1
}

if ($Progress -lt 0 -or $Progress -gt 100) {
    Write-Error "错误：进度必须在 0-100 之间。"
    exit 1
}

$content = Get-Content $statusFile -Raw

# 找到当前任务行
$pattern = "\[{0}\] {1} — (\d+)%( — ([^\r\n]*))?" -f [regex]::Escape($AgentId), [regex]::Escape($TaskName)

if ($content -notmatch $pattern) {
    Write-Error "错误：找不到你进行中的任务「$TaskName」"
    Write-Host "请确认任务名和 agent id 正确，且任务在「进行中」列表里。"
    exit 1
}

$oldLine = $Matches[0]
$oldProgress = $Matches[1]
$restOfLine = $Matches[3]

# 构建新行
$noteText = if ($Note) { " — $Note" } else { " — $restOfLine" }
$newLine = "[$AgentId] $TaskName — ${Progress}%${noteText}"

# 替换
$content = $content.Replace($oldLine, $newLine)

Set-Content -Path $statusFile -Value $content -NoNewline

Write-Host ""
Write-Host "📊 进度已更新：$TaskName  $oldProgress% → $Progress%"
if ($Note) { Write-Host "📝 备注：$Note" }
Write-Host ""

# 询问是否提交
$doCommit = Read-Host "要现在提交并推送吗？(Y/n)"
if ($doCommit -ne 'n' -and $doCommit -ne 'N') {
    git add $statusFile
    git commit -m "chore: $AgentId 更新「$TaskName」进度 $Progress%"
    $currentBranch = git branch --show-current
    git push origin $currentBranch
    Write-Host ""
    Write-Host "✅ 已提交并推送到远端。"
}

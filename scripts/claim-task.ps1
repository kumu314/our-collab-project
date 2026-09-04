# ============================================================
#  claim-task.ps1 —— 认领「📋 待认领」里的任务：
#                     把行里的 [待认领] 改成你的 AGENT_ID，
#                     并从「待认领」区块挪到「🚧 进行中」区块
#
#  用法（在仓库根目录或任意位置执行都可以）：
#    .\scripts\claim-task.ps1 -TaskName "模型构建与求解" -AgentId ningxiachufang
#    .\scripts\claim-task.ps1 -TaskName "模型构建与求解" -BranchName model-build
#    .\scripts\claim-task.ps1 -TaskName "模型构建与求解" -Estimate "10h" -BranchName model-build
#
#  参数说明：
#    -TaskName   必填。STATUS.md「待认领」里那条任务的名字，可只写一部分（包含匹配）
#    -AgentId    可选。不填时自动读取仓库根目录的 AGENT_ID 文件
#    -Estimate   可选。预估工时，会写进「进行中」那一行（如 "10h"）
#    -BranchName 可选。英文分支名（只含 a-z 0-9 和 -）。不填时按任务名自动生成；
#                任务名全是中文时自动生成会很难看，建议显式传这个参数
#
#  注意：本文件已保存为 UTF-8 with BOM，Windows PowerShell 5.1 才能正确显示中文。
# ============================================================

param(
    [Parameter(Mandatory = $true, HelpMessage = "待认领里任务名，可只写一部分")]
    [string]$TaskName,

    [Parameter(Mandatory = $false, HelpMessage = "你的 AGENT_ID，不填则读 AGENT_ID 文件")]
    [string]$AgentId,

    [Parameter(Mandatory = $false, HelpMessage = "预估工时，如 10h")]
    [string]$Estimate,

    [Parameter(Mandatory = $false, HelpMessage = "英文分支名，只含 a-z0-9-")]
    [string]$BranchName
)

$ErrorActionPreference = 'Stop'

# 让控制台正确显示中文
try {
    & chcp 65001 | Out-Null
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8
} catch {
    # 某些宿主（如 ISE）不支持设置，忽略即可
}

# 显式用 UTF-8（无 BOM）读写，避免 PowerShell 5.1 默认的 GBK 把中文写成乱码
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

# ---------- 1. 定位仓库根目录（脚本在 scripts/ 下，根目录就是上一级）----------
$repoRoot   = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$statusPath = Join-Path $repoRoot 'STATUS.md'

# ---------- 2. 校验 STATUS.md 存在 ----------
if (-not (Test-Path -LiteralPath $statusPath)) {
    Write-Host ""
    Write-Host "[错误] 找不到 STATUS.md：$statusPath" -ForegroundColor Red
    Write-Host "       请确认本脚本位于仓库的 scripts\ 目录下。" -ForegroundColor Red
    Write-Host ""
    exit 1
}

# ---------- 3. 确定 AgentId ----------
if ([string]::IsNullOrWhiteSpace($AgentId)) {
    $agentIdFile = Join-Path $repoRoot 'AGENT_ID'
    if (Test-Path -LiteralPath $agentIdFile) {
        $AgentId = ([System.IO.File]::ReadAllLines($agentIdFile, $utf8NoBom) | Select-Object -First 1)
        if ($AgentId) { $AgentId = $AgentId.Trim() }
    }
}
if ([string]::IsNullOrWhiteSpace($AgentId) -or $AgentId -eq 'your-agent-id-here') {
    Write-Host ""
    Write-Host "[错误] 还没有设置 AGENT_ID。" -ForegroundColor Red
    Write-Host "       请二选一：" -ForegroundColor Red
    Write-Host "         a) 执行命令时加上 -AgentId 你的ID" -ForegroundColor Red
    Write-Host "         b) 复制 AGENT_ID.example 为 AGENT_ID，并把内容改成你的 ID" -ForegroundColor Red
    Write-Host ""
    exit 1
}
$AgentId = $AgentId.Trim()

# ---------- 4. 读取 STATUS.md ----------
$lines = New-Object System.Collections.Generic.List[string]
foreach ($l in [System.IO.File]::ReadAllLines($statusPath, $utf8NoBom)) {
    $lines.Add($l)
}

$sep         = ' — '
$taskPattern = [regex]::Escape($TaskName)
$claimPattern = '\[待认领\]'

$claimStart  = -1
$doingStart  = -1
$targetIndex = -1
$matchCount  = 0

for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    if ($line -match '^##\s+') {
        $heading = $line -replace '^##\s+', ''
        if ($heading -match '待认领') { $claimStart = $i }
        if ($heading -match '进行中')  { $doingStart = $i }
    }
    # 只认真正的任务列表行（以 "- [" 开头），排除区块说明行和表格行
    if ($line.TrimStart() -match '^-\s+\[' -and
        $line -match $claimPattern -and
        $line -match $taskPattern) {
        $matchCount++
        $targetIndex = $i
    }
}

# ---------- 5. 异常：一律报错，绝不静默成功 ----------
if ($claimStart -lt 0) {
    Write-Host ""
    Write-Host "[错误] STATUS.md 里找不到「📋 待认领」区块。" -ForegroundColor Red
    Write-Host ""
    exit 1
}

if ($matchCount -eq 0) {
    Write-Host ""
    Write-Host "[错误] 在「待认领」里没找到任务名包含「$TaskName」的那一行。" -ForegroundColor Red
    Write-Host "       请确认任务名没写错（可以只写一部分），并且改之前先 git pull。" -ForegroundColor Red
    Write-Host ""
    exit 1
}

if ($matchCount -gt 1) {
    Write-Host ""
    Write-Host "[错误] 找到 $matchCount 行都匹配，无法确定认领哪个，请填写更完整的任务名。" -ForegroundColor Red
    Write-Host ""
    exit 1
}

# 目标行必须落在「待认领」区块内（标题之后、下一个二级标题之前）
$claimEnd = $lines.Count
for ($i = $claimStart + 1; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^##\s+') { $claimEnd = $i; break }
}
if ($targetIndex -le $claimStart -or $targetIndex -ge $claimEnd) {
    Write-Host ""
    Write-Host "[错误] 这条任务不在「待认领」区块里，可能已被认领。" -ForegroundColor Red
    Write-Host "       $($lines[$targetIndex])" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# 防重复：进行中里已经有 [AgentId] + TaskName 就报错
$idPattern = '\[' + [regex]::Escape($AgentId) + '\]'
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i].TrimStart() -match '^-\s+\[' -and
        $lines[$i] -match $idPattern -and
        $lines[$i] -match $taskPattern) {
        Write-Host ""
        Write-Host "[错误] 你已经认领过「$TaskName」，无需重复认领：" -ForegroundColor Red
        Write-Host "       $($lines[$i])" -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }
}

if ($doingStart -lt 0) {
    Write-Host ""
    Write-Host "[错误] STATUS.md 里找不到「🚧 进行中」区块，无法插入。" -ForegroundColor Red
    Write-Host ""
    exit 1
}

# ---------- 6. 构造「进行中」那一行 ----------
$oldLine = $lines[$targetIndex]
# 取出任务标题（[待认领] 之后、第一个「 — 」之前的部分），并去掉里面可能带的（预估Xh）
$taskText = $TaskName
if ($oldLine -match '\[待认领\]\s*(.*?)\s*—') {
    $taskText = $Matches[1] -replace '（预估[^）]*）', ''
}
$newLine = "- [$AgentId] $taskText — 0%"
if (-not [string]::IsNullOrWhiteSpace($Estimate)) {
    $newLine += " — 预计 $($Estimate.Trim()) 小时"
}
else {
    $newLine += " — 预计 ? 小时"
}
$newLine += " — 刚开始"

# ---------- 7. 从「待认领」剪切，插入「进行中」末尾 ----------
$doingEnd = $lines.Count
for ($i = $doingStart + 1; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^##\s+') { $doingEnd = $i; break }
}
$lastItem = -1
for ($i = $doingStart + 1; $i -lt $doingEnd; $i++) {
    if ($lines[$i].Trim() -match '^-\s') { $lastItem = $i }
}
if ($lastItem -ge 0) { $insertAt = $lastItem + 1 }
else                 { $insertAt = $doingStart + 1 }

# 从后往前操作，避免下标错位
$lines.RemoveAt($targetIndex)
if ($targetIndex -lt $insertAt) { $insertAt-- }
if ($insertAt -gt $lines.Count) { $insertAt = $lines.Count }
$lines.Insert($insertAt, $newLine)

# ---------- 8. 先写临时文件，再覆盖原文件（避免写坏 STATUS.md）----------
$tmpPath = $statusPath + '.tmp'
[System.IO.File]::WriteAllLines($tmpPath, $lines, $utf8NoBom)
Move-Item -LiteralPath $tmpPath -Destination $statusPath -Force

# ---------- 9. 计算分支名 ----------
# 注意：局部变量千万别叫 $branchName —— PowerShell 变量名不区分大小写，
# 那样会把同名的 -BranchName 参数覆盖成 $null，表现为「参数传了却没生效」。
$suggestedBranch = $null
if (-not [string]::IsNullOrWhiteSpace($BranchName)) {
    $slugIn = $BranchName.Trim().ToLower() -replace '[^a-z0-9-]', '-' -replace '-{2,}', '-' -replace '^-|-$', ''
    if ($slugIn) { $suggestedBranch = "agent/$AgentId/$slugIn" }
}
else {
    $slug = ($TaskName.ToLower() -replace '[^a-z0-9]+', '-' -replace '^-|-$', '')
    if ($slug) { $suggestedBranch = "agent/$AgentId/$slug" }
}

Write-Host ""
Write-Host "[成功] 已认领任务：$TaskName" -ForegroundColor Green
Write-Host "  新: $newLine" -ForegroundColor Green
if ($suggestedBranch) {
    Write-Host "  建议分支名：$suggestedBranch" -ForegroundColor Cyan
}
else {
    Write-Host "  [提示] 任务名不含英文/数字，无法自动生成分支名，请加 -BranchName 参数（如 -BranchName literature-review）。" -ForegroundColor Yellow
}
Write-Host ""

# ---------- 10. 是否创建分支并提交（交互）----------
$answer = Read-Host "现在就创建分支并提交 STATUS.md 吗？(Y/n)"
if ($answer -ne 'n' -and $answer -ne 'N') {
    if (-not $suggestedBranch) {
        $custom = Read-Host "请输入英文分支名（如 literature-review）"
        $custom = ($custom.Trim().ToLower() -replace '[^a-z0-9-]', '-' -replace '^-|-$', '')
        if ($custom) { $suggestedBranch = "agent/$AgentId/$custom" }
    }
    if ($suggestedBranch) {
        git checkout -b $suggestedBranch main
        git add STATUS.md
        git commit -m "chore: $AgentId 认领「$TaskName」"
        Write-Host ""
        Write-Host "[完成] 分支 $suggestedBranch 已创建，STATUS.md 已提交。" -ForegroundColor Green
        Write-Host "       记得推送到远端：git push -u origin $suggestedBranch" -ForegroundColor Cyan
    }
    else {
        Write-Host "[跳过] 没拿到可用的分支名，已更新 STATUS.md，请手动创建分支并提交。" -ForegroundColor Yellow
    }
}
else {
    Write-Host "已更新 STATUS.md，记得手动：git checkout -b agent/$AgentId/你的分支名 main ；git add STATUS.md ；git commit" -ForegroundColor Cyan
}
Write-Host ""
exit 0

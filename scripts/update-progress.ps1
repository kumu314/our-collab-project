# ============================================================
#  update-progress.ps1 —— 更新 STATUS.md 里你那条任务的进度
#
#  用法（在仓库根目录或任意位置执行都可以）：
#    .\scripts\update-progress.ps1 -TaskName "文献调研与赛题拆解" -Progress 60 -AgentId ningxiachufang
#    .\scripts\update-progress.ps1 -TaskName "文献调研与赛题拆解" -Progress 60 -AgentId ningxiachufang -Note "已读完3篇核心文献"
#
#  参数说明：
#    -TaskName  必填。STATUS.md 里那条任务的名字，可以只写一部分（脚本做「包含」匹配）
#    -Progress  必填。0-100 的整数
#    -AgentId   可选。不填时自动读取仓库根目录的 AGENT_ID 文件
#    -Note      可选。填了就替换该行最后的备注；不填则保留原备注
#
#  注意：本文件已保存为 UTF-8 with BOM，
#        Windows PowerShell 5.1 才能正确显示中文提示。
# ============================================================

param(
    [Parameter(Mandatory = $true, HelpMessage = "STATUS.md 里的任务名，可只写一部分")]
    [string]$TaskName,

    [Parameter(Mandatory = $true, HelpMessage = "进度百分比，0-100 的整数")]
    [int]$Progress,

    [Parameter(Mandatory = $false, HelpMessage = "你的 AGENT_ID，不填则读取 AGENT_ID 文件")]
    [string]$AgentId,

    [Parameter(Mandatory = $false, HelpMessage = "可选，替换该行行尾的备注")]
    [string]$Note
)

$ErrorActionPreference = 'Stop'

# 让控制台正确显示中文
try {
    # 先把控制台代码页切到 UTF-8（Windows PowerShell 5.1 默认是 936/GBK，
    # 不切的话下面的 UTF8 输出会被当成 GBK 解码，中文全是乱码）
    & chcp 65001 | Out-Null
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8
} catch {
    # 某些宿主（如 ISE）不支持设置，忽略即可
}

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

# ---------- 1. 定位仓库根目录（脚本在 scripts/ 下，根目录就是上一级）----------
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$statusPath = Join-Path $repoRoot 'STATUS.md'

# ---------- 2. 校验 STATUS.md 存在 ----------
if (-not (Test-Path -LiteralPath $statusPath)) {
    Write-Host ""
    Write-Host "[错误] 找不到 STATUS.md：$statusPath" -ForegroundColor Red
    Write-Host "       请先 cd 到仓库根目录，或确认本脚本位于仓库的 scripts\ 目录下。" -ForegroundColor Red
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

# ---------- 4. 校验进度值 ----------
if ($Progress -lt 0 -or $Progress -gt 100) {
    Write-Host ""
    Write-Host "[错误] -Progress 必须是 0 到 100 之间的整数，你填的是：$Progress" -ForegroundColor Red
    Write-Host ""
    exit 1
}

# ---------- 5. 读取 STATUS.md ----------
$lines = New-Object System.Collections.Generic.List[string]
foreach ($l in [System.IO.File]::ReadAllLines($statusPath, $utf8NoBom)) {
    $lines.Add($l)
}

# ---------- 6. 找到「同时包含 AgentId 和 TaskName」的那一行 ----------
$sep = ' — '                       # STATUS.md 里字段之间的分隔符（空格 + 破折号 + 空格）
$idPattern   = '\[' + [regex]::Escape($AgentId) + '\]'
$taskPattern = [regex]::Escape($TaskName)

$matchIndexes = @()
for ($i = 0; $i -lt $lines.Count; $i++) {
    # 只认真正的任务行（以 "- [" 开头的列表项）。
    # 区块说明里的「> 示例：...」行和「| xxx |」表格行也含 agent-id，必须排除，否则会误判成多行匹配。
    if ($lines[$i].TrimStart() -match '^-\s+\[' -and
        $lines[$i] -match $idPattern -and
        $lines[$i] -match $taskPattern) {
        $matchIndexes += $i
    }
}

if ($matchIndexes.Count -eq 0) {
    Write-Host ""
    Write-Host "[错误] 在 STATUS.md 里没找到属于 [$AgentId] 且任务名包含「$TaskName」的那一行。" -ForegroundColor Red
    Write-Host "       请检查：" -ForegroundColor Red
    Write-Host "         1) 任务名是否写对（可以只写一部分，但不能有错别字）" -ForegroundColor Red
    Write-Host "         2) 这行前面是不是还是 [待认领]，还没改成 [$AgentId]" -ForegroundColor Red
    Write-Host "         3) 改之前有没有先 git pull" -ForegroundColor Red
    Write-Host ""
    exit 1
}

if ($matchIndexes.Count -gt 1) {
    Write-Host ""
    Write-Host "[错误] 找到 $($matchIndexes.Count) 行都匹配，无法确定改哪一行，请填写更完整的任务名。" -ForegroundColor Red
    foreach ($idx in $matchIndexes) {
        Write-Host "       第 $($idx + 1) 行: $($lines[$idx])" -ForegroundColor Yellow
    }
    Write-Host ""
    exit 1
}

# ---------- 7. 改造这一行 ----------
$targetIndex = $matchIndexes[0]
$oldLine = $lines[$targetIndex]
$parts = $oldLine -split $sep

if ($parts.Count -lt 2) {
    Write-Host ""
    Write-Host "[错误] 这一行的格式不标准，找不到进度字段（应该长这样：- [id] 任务名 — 40% — 预计 6 小时 — 备注）：" -ForegroundColor Red
    Write-Host "       $oldLine" -ForegroundColor Red
    Write-Host ""
    exit 1
}

# 第 1 段：- [agent-id] 任务名（保持不变）
# 第 2 段：进度（替换）
# 第 3 段：预计 X 小时（保留）
# 第 4 段起：备注（传了 -Note 就替换，没传就原样保留）
$newLine = $parts[0] + $sep + "$Progress%"

if ($parts.Count -ge 3) {
    $newLine = $newLine + $sep + $parts[2]
}

if (-not [string]::IsNullOrWhiteSpace($Note)) {
    $newLine = $newLine + $sep + $Note.Trim()
}
elseif ($parts.Count -ge 4) {
    $rest = ($parts[3..($parts.Count - 1)] -join $sep).Trim()
    if ($rest) { $newLine = $newLine + $sep + $rest }
}

$lines[$targetIndex] = $newLine

# ---------- 8. 先写临时文件，再覆盖原文件（避免写坏 STATUS.md）----------
$tmpPath = $statusPath + '.tmp'
[System.IO.File]::WriteAllLines($tmpPath, $lines, $utf8NoBom)
Move-Item -LiteralPath $tmpPath -Destination $statusPath -Force

# ---------- 9. 输出结果 ----------
Write-Host ""
Write-Host "[成功] 进度已更新（STATUS.md 第 $($targetIndex + 1) 行）" -ForegroundColor Green
Write-Host "  旧: $oldLine" -ForegroundColor DarkGray
Write-Host "  新: $newLine" -ForegroundColor Green
Write-Host ""
Write-Host "接下来记得：" -ForegroundColor Cyan
Write-Host "  git add STATUS.md" -ForegroundColor Cyan
Write-Host "  git commit -m `"docs: 更新 $TaskName 进度到 ${Progress}%`"" -ForegroundColor Cyan
Write-Host "  git pull && git push" -ForegroundColor Cyan
Write-Host ""
exit 0

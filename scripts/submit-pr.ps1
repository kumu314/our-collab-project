# ============================================================
#  submit-pr.ps1 —— 把你的任务行从「🚧 进行中」挪到「👀 待评审」，并附上 PR 链接
#
#  用法（在仓库根目录或任意位置执行都可以）：
#    .\scripts\submit-pr.ps1 -TaskName "文献调研与赛题拆解" -AgentId ningxiachufang -PrUrl "https://github.com/kumu314/our-collab-project/pull/1"
#
#  参数说明：
#    -TaskName  必填。STATUS.md 里那条任务的名字，可以只写一部分（脚本做「包含」匹配）
#    -AgentId   可选。不填时自动读取仓库根目录的 AGENT_ID 文件
#    -PrUrl     必填。GitHub 上开好的 PR 链接
#
#  行为：
#    - 从「🚧 进行中」区块里剪切掉你那一行
#    - 追加「— PR: <链接>」后，插入到「👀 待评审」区块的末尾
#    - 如果该行不在「进行中」，或已经带过 PR 链接，会报错退出，绝不重复插入
#
#  注意：本文件已保存为 UTF-8 with BOM，
#        Windows PowerShell 5.1 才能正确显示中文提示。
# ============================================================

param(
    [Parameter(Mandatory = $true, HelpMessage = "STATUS.md 里的任务名，可只写一部分")]
    [string]$TaskName,

    [Parameter(Mandatory = $false, HelpMessage = "你的 AGENT_ID，不填则读取 AGENT_ID 文件")]
    [string]$AgentId,

    [Parameter(Mandatory = $true, HelpMessage = "GitHub PR 链接")]
    [string]$PrUrl
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

# ---------- 4. 校验 PR 链接 ----------
$PrUrl = $PrUrl.Trim()
if ($PrUrl -notmatch '^https?://') {
    Write-Host ""
    Write-Host "[错误] -PrUrl 必须是一个以 http:// 或 https:// 开头的链接，你填的是：$PrUrl" -ForegroundColor Red
    Write-Host ""
    exit 1
}

# ---------- 5. 读取 STATUS.md ----------
$lines = New-Object System.Collections.Generic.List[string]
foreach ($l in [System.IO.File]::ReadAllLines($statusPath, $utf8NoBom)) {
    $lines.Add($l)
}

# ---------- 6. 扫描各区块的位置 ----------
$sep = ' — '                       # STATUS.md 里字段之间的分隔符
$idPattern   = '\[' + [regex]::Escape($AgentId) + '\]'
$taskPattern = [regex]::Escape($TaskName)

$doingStart   = -1   # 「🚧 进行中」标题行下标
$reviewStart  = -1   # 「👀 待评审」标题行下标
$reviewEnd    = -1   # 「👀 待评审」区块结束位置（不含）
$targetIndex  = -1
$matchCount   = 0

for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]

    # 记录二级标题（区块起点）
    if ($line -match '^##\s+') {
        $heading = $line -replace '^##\s+', ''
        if ($heading -match '进行中') { $doingStart = $i }
        if ($heading -match '待评审') {
            $reviewStart = $i
            $reviewEnd   = -1          # 先标记未闭合，等遇到下一个标题或文件末尾再定
        }
        elseif ($reviewEnd -eq -1 -and $reviewStart -ge 0) {
            $reviewEnd = $i            # 遇到下一个二级标题，待评审区块到此结束
        }
    }

    # 找任务行：只认以 "- [" 开头的真正任务行。
    # 区块说明里的「> 示例：...」行和「| xxx |」表格行也含 agent-id，必须排除。
    if ($line.TrimStart() -match '^-\s+\[' -and
        $line -match $idPattern -and
        $line -match $taskPattern) {
        $matchCount++
        $targetIndex = $i
    }
}

if ($reviewStart -ge 0 -and $reviewEnd -eq -1) {
    $reviewEnd = $lines.Count          # 待评审区块一直到文件末尾
}

# ---------- 7. 各种异常情况，一律报错，绝不静默成功 ----------
if ($matchCount -eq 0) {
    Write-Host ""
    Write-Host "[错误] 在 STATUS.md 里没找到属于 [$AgentId] 且任务名包含「$TaskName」的那一行。" -ForegroundColor Red
    Write-Host "       请检查任务名有没有写错，或者改之前有没有先 git pull。" -ForegroundColor Red
    Write-Host ""
    exit 1
}

if ($matchCount -gt 1) {
    Write-Host ""
    Write-Host "[错误] 找到 $matchCount 行都匹配，无法确定挪哪一行，请填写更完整的任务名。" -ForegroundColor Red
    Write-Host ""
    exit 1
}

if ($doingStart -lt 0) {
    Write-Host ""
    Write-Host "[错误] STATUS.md 里找不到「🚧 进行中」区块，无法判断该任务当前状态。" -ForegroundColor Red
    Write-Host ""
    exit 1
}

if ($reviewStart -lt 0) {
    Write-Host ""
    Write-Host "[错误] STATUS.md 里找不到「👀 待评审」区块，无法插入。" -ForegroundColor Red
    Write-Host ""
    exit 1
}

# 目标行必须落在「进行中」区块内（即在进行中标题之后、下一个二级标题之前）
$doingEnd = $lines.Count
for ($i = $doingStart + 1; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^##\s+') { $doingEnd = $i; break }
}

if ($targetIndex -le $doingStart -or $targetIndex -ge $doingEnd) {
    $where = 'unknown'
    for ($i = $targetIndex; $i -ge 0; $i--) {
        if ($lines[$i] -match '^##\s+') { $where = ($lines[$i] -replace '^##\s+', ''); break }
    }
    Write-Host ""
    Write-Host "[错误] 这条任务不在「🚧 进行中」区块里，它在「$where」，所以不再重复移动。" -ForegroundColor Red
    Write-Host "       $($lines[$targetIndex])" -ForegroundColor Yellow
    Write-Host "       如果只是想更新 PR 链接，请手动编辑这一行。" -ForegroundColor Red
    Write-Host ""
    exit 1
}

$oldLine = $lines[$targetIndex]

if ($oldLine -match 'PR:\s*https?://') {
    Write-Host ""
    Write-Host "[错误] 这一行已经带过 PR 链接了，不会重复插入：" -ForegroundColor Red
    Write-Host "       $oldLine" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# ---------- 8. 追加 PR 链接 ----------
$newLine = $oldLine.TrimEnd() + $sep + "PR: $PrUrl"

# ---------- 9. 从「进行中」剪切，插入到「待评审」末尾 ----------
# 待评审区块内的插入位置：
#   1) 区块里已经有任务条目 -> 插在最后一条之后
#   2) 还没有条目、但有 <!-- 暂无 --> 占位注释 -> 插在占位注释之前
#   3) 以上都没有 -> 紧跟标题行
$secStart     = $reviewStart + 1
$secEnd       = $reviewEnd          # 不含
$lastItem     = -1
$firstComment = -1
for ($i = $secStart; $i -lt $secEnd; $i++) {
    $t = $lines[$i].Trim()
    if ($t -match '^-\s') { $lastItem = $i }
    if ($firstComment -lt 0 -and $t -match '^<!--') { $firstComment = $i }
}

if ($lastItem -ge 0)         { $insertAt = $lastItem + 1 }
elseif ($firstComment -ge 0) { $insertAt = $firstComment }
else                         { $insertAt = $secStart }

# 从后往前删，避免下标错位
$lines.RemoveAt($targetIndex)
if ($targetIndex -lt $insertAt) { $insertAt-- }   # 删除后插入位置要前移一位

if ($insertAt -gt $lines.Count) { $insertAt = $lines.Count }
$lines.Insert($insertAt, $newLine)

# ---------- 10. 先写临时文件，再覆盖原文件（避免写坏 STATUS.md）----------
$tmpPath = $statusPath + '.tmp'
[System.IO.File]::WriteAllLines($tmpPath, $lines, $utf8NoBom)
Move-Item -LiteralPath $tmpPath -Destination $statusPath -Force

# ---------- 11. 输出结果 ----------
Write-Host ""
Write-Host "[成功] 任务已移到「👀 待评审」（STATUS.md 第 $($insertAt + 1) 行）" -ForegroundColor Green
Write-Host "  新: $newLine" -ForegroundColor Green
Write-Host ""
Write-Host "接下来记得：" -ForegroundColor Cyan
Write-Host "  git pull" -ForegroundColor Cyan
Write-Host "  git add STATUS.md" -ForegroundColor Cyan
Write-Host "  git commit -m `"docs: $TaskName 提交评审`"" -ForegroundColor Cyan
Write-Host "  git push" -ForegroundColor Cyan
Write-Host ""
exit 0

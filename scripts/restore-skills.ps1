# 兜底恢复：把 motion-web 技能文件从 git 历史恢复到工作区，并保持其不被跟踪
# 适用：未配置 hooks 时 pull 导致技能文件被删，或新机器需要重新取回技能
# 用法：powershell -ExecutionPolicy Bypass -File scripts/restore-skills.ps1
$ErrorActionPreference = "Continue"
Set-Location (Join-Path $PSScriptRoot "..")

$paths = @("motion-web-main", ".agents", ".trae")
$restored = @()

function Find-RevWithPath([string]$p) {
    # 遍历改动过该路径的提交，取第一个真正包含它的（跳过删除提交）
    foreach ($r in (git rev-list HEAD -- $p 2>$null)) {
        if (git ls-tree --name-only $r -- $p 2>$null) { return $r }
    }
    return $null
}

foreach ($p in $paths) {
    $rev = Find-RevWithPath $p
    if (-not $rev) {
        Write-Warning "$p 不在当前分支历史中（技能可能从未入库或历史被裁剪），跳过。"
        continue
    }
    git checkout $rev -- $p 2>&1 | Out-Null
    git rm -r --cached --ignore-unmatch --force $p 2>&1 | Out-Null
    if (Test-Path -LiteralPath $p) { $restored += $p }
}

Write-Host "--- 恢复结果 ---" -ForegroundColor Green
foreach ($p in $restored) { Write-Host "  已恢复: $p" -ForegroundColor Green }
if (-not $restored) { Write-Warning "未恢复任何文件，请查看 docs/技能库出库与同步.md 获取技能来源。" }

Write-Host "--- 工作区状态（技能应为 untracked/ignored，不产生待提交变更）---"
git status --short -- motion-web-main .agents .trae

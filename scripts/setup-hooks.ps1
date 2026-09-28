# 一次性配置仓库级 Git Hooks（保护本地 motion-web 技能不被 pull/merge 删除）
# 用法：powershell -ExecutionPolicy Bypass -File scripts/setup-hooks.ps1
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

git config core.hooksPath .githooks
if ($LASTEXITCODE -ne 0) { throw "git config core.hooksPath 失败" }

$path = git config --get core.hooksPath
if ($path -ne ".githooks") { throw "配置校验失败：core.hooksPath=$path" }

Write-Host "OK: core.hooksPath = .githooks" -ForegroundColor Green
Write-Host "此后 git pull / git merge 会自动保留本地 motion-web 技能文件。" -ForegroundColor Green

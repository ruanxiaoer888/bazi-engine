#requires -Version 5.1
<#
.SYNOPSIS
  bazi-engine -> ClawHub 发布脚本（封装 2026-08-20 实战流程，坑 #49 经验沉淀）

.DESCRIPTION
  三步发布：
    1) 准备发布目录（SKILL.md 在根 + skill/ui/engine/kb/tools + LICENSE/LICENSE-DATA/README.md，
       排除内部子路径 drafts/archive/_dbg/__pycache__）
    2) clawhub skill publish（总是先 dry-run 预览）
    3) inspect 验证 latest 版本
  依赖：clawhub CLI（npm i -g clawhub）+ 已登录（clawhub login，登录态存 %APPDATA%\clawhub）

  坑 #49 要点：
    - 非 TTY 下 CLI 退出码 1 可能是进度动画假象，以 --json 输出的 ok:true 为准
    - License 平台强制 MIT-0，任何方式都改不了；靠 SKILL.md description 双许可声明兜底
    - 审计 Review 状态（tools 测试脚本动态执行 + kb/05-reference 超范围内容）不阻塞安装，可接受

.PARAMETER Version
  必填。semver 版本号，如 1.4.0

.PARAMETER Build
  可选。发布前先跑 python tools/build_ui.py 重建 ui/index.html + engine/engine.dist.js
  （默认不跑，避免意外改变构建产物；dist 重建是确定性的，MD5 不变）

.PARAMETER DryRun
  可选。只准备目录 + dry-run 预览，不真正发布

.PARAMETER OutDir
  可选。发布目录路径（默认 %TEMP%\bazi-clawhub-publish，每次重建）

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools/publish_clawhub.ps1 -Version 1.4.0 -DryRun
  powershell -ExecutionPolicy Bypass -File tools/publish_clawhub.ps1 -Version 1.4.0
#>
param(
    [Parameter(Mandatory = $true)][string]$Version,
    [switch]$Build,
    [switch]$DryRun,
    [string]$OutDir = "$env:TEMP\bazi-clawhub-publish"
)

$ErrorActionPreference = 'Stop'
$ROOT = Split-Path -Parent $PSScriptRoot   # 仓库根

# ---- 0. 版本号校验（semver）----
if ($Version -notmatch '^\d+\.\d+\.\d+$') {
    Write-Host "[错误] 版本号必须是 semver 格式（如 1.4.0），收到: $Version" -ForegroundColor Red
    exit 1
}

# ---- 1. 检查 clawhub CLI 与登录态 ----
Write-Host "==> 检查 clawhub CLI..." -ForegroundColor Cyan
$who = & clawhub whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] clawhub 未登录或不可用。请先执行: npm i -g clawhub ; clawhub login" -ForegroundColor Red
    Write-Host $who
    exit 1
}
Write-Host "    已登录: $who"

# ---- 2. 可选：重建 UI ----
if ($Build) {
    Write-Host "==> 重建 UI（python tools/build_ui.py）..." -ForegroundColor Cyan
    Push-Location $ROOT
    python tools/build_ui.py
    $buildCode = $LASTEXITCODE
    Pop-Location
    if ($buildCode -ne 0) { Write-Host "[错误] build_ui.py 失败" -ForegroundColor Red; exit 1 }
}

# ---- 3. 准备发布目录 ----
Write-Host "==> 准备发布目录: $OutDir" -ForegroundColor Cyan
if (Test-Path $OutDir) { Remove-Item $OutDir -Recurse -Force }
New-Item -ItemType Directory -Path $OutDir | Out-Null

# 根文件（SKILL.md 在根，与项目源 skill/SKILL.md 保持同步，对齐坑 #22）
Copy-Item "$ROOT\skill\SKILL.md" "$OutDir\SKILL.md"
Copy-Item "$ROOT\README.md" "$OutDir\README.md"
Copy-Item "$ROOT\LICENSE" "$OutDir\LICENSE"
Copy-Item "$ROOT\LICENSE-DATA" "$OutDir\LICENSE-DATA"

# 白名单目录
$INCLUDE_DIRS = @('skill', 'ui', 'engine', 'kb', 'tools')
foreach ($d in $INCLUDE_DIRS) {
    $src = Join-Path $ROOT $d
    if (Test-Path $src) { Copy-Item $src "$OutDir\$d" -Recurse }
}

# 排除内部子路径
$EXCLUDE_SUB = @(
    'kb\04-rules-db\drafts',   # 内部取材源
    'tools\archive',            # 归档脚本
    'tools\_dbg',               # 调试残留
    'tools\__pycache__'
)
foreach ($ex in $EXCLUDE_SUB) {
    $p = Join-Path $OutDir $ex
    if (Test-Path $p) { Remove-Item $p -Recurse -Force }
}
$count = (Get-ChildItem $OutDir -Recurse -File).Count
Write-Host "    发布目录就绪：$count 个文件（根含 SKILL.md + LICENSE + LICENSE-DATA + README.md）"

# ---- 4. 发布（先 dry-run 预览，再正式发布）----
$commonArgs = @(
    $OutDir,
    '--slug', 'baizi-engine',
    '--name', 'bazi-engine（四柱八字命理引擎）',
    '--version', $Version,
    '--categories', 'productivity',
    '--topics', 'bazi,lunar-calendar,solar-terms,chinese-metaphysics',
    '--json'
)

Write-Host "==> dry-run 预览..." -ForegroundColor Cyan
$dry = & clawhub skill publish @commonArgs --dry-run 2>&1
$dry | Out-String | Write-Host
if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] dry-run 失败，请检查上面的输出" -ForegroundColor Red
    exit 1
}

if ($DryRun) {
    Write-Host ""
    Write-Host "[DryRun 模式] 未真正发布。确认无误后去掉 -DryRun 执行正式发布。" -ForegroundColor Yellow
    exit 0
}

Write-Host "==> 正式发布 v$Version ..." -ForegroundColor Cyan
$pub = & clawhub skill publish @commonArgs 2>&1
$pubJson = ($pub | Out-String) | ConvertFrom-Json -ErrorAction SilentlyContinue
if ($pubJson -and $pubJson.ok -eq $true) {
    Write-Host "    发布已提交：$($pubJson.slug) v$($pubJson.version) status=$($pubJson.status) publicationStatus=$($pubJson.publicationStatus)" -ForegroundColor Green
} else {
    # 坑 #49：非 TTY 下 CLI 退出码 1 可能是进度动画假象；--json 未解析出 ok:true 才需要人工确认
    Write-Host "[警告] 未能从输出解析 ok:true，原始输出如下（坑 #49：非 TTY 下退出码 1 可能是进度动画假象，请人工确认或稍后重跑验证）：" -ForegroundColor Yellow
    $pub | Out-String | Write-Host
}

# ---- 5. 验证最新版本（安全检查约 2-3 分钟后转公开）----
Write-Host "==> 验证 latest 版本（安全检查约 2-3 分钟，可能需稍后重跑本步）..." -ForegroundColor Cyan
Start-Sleep -Seconds 5
$j = clawhub inspect @ruanxiaoer888/baizi-engine --versions --json 2>$null | ConvertFrom-Json
Write-Host "    current latest: v$($j.skill.tags.latest)"
if ($j.skill.tags.latest -eq $Version) {
    Write-Host "    [OK] 发布成功，latest = v$Version" -ForegroundColor Green
} else {
    Write-Host "    [提示] 版本尚未转公开（安全检查中）。版本列表：" -ForegroundColor Yellow
    $j.versions | ForEach-Object { Write-Host "      - v$($_.version)" }
}

Write-Host ""
Write-Host "完成。发布目录保留在: $OutDir（下次发布自动重建）。" -ForegroundColor Cyan

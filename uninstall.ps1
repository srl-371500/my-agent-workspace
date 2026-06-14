# uninstall.ps1 - One-Click Traceless Uninstaller
# Restores Git hooks, removes IDE rules, preserves docs, then self-destructs.

$ErrorActionPreference = "SilentlyContinue"
$ToolkitRoot = $PSScriptRoot
$WorkspaceRoot = $ToolkitRoot

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Traceless Uninstaller" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/4] Restoring Git hooks to default..." -ForegroundColor Yellow
Push-Location $WorkspaceRoot
$hookResult = git config --local --unset core.hooksPath 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] core.hooksPath has been unset." -ForegroundColor Green
} else {
    Write-Host "  [INFO] core.hooksPath was not set (already clean)." -ForegroundColor Gray
}
Pop-Location

Write-Host ""
Write-Host "[2/4] Removing IDE rules and temp artifacts..." -ForegroundColor Yellow

$traePath = Join-Path $WorkspaceRoot ".trae"
if (Test-Path $traePath) {
    Remove-Item -Recurse -Force -Path $traePath
    Write-Host "  [OK] .trae/ removed." -ForegroundColor Green
}

$vscodePath = Join-Path $WorkspaceRoot ".vscode"
if (Test-Path $vscodePath) {
    Remove-Item -Recurse -Force -Path $vscodePath
    Write-Host "  [OK] .vscode/ removed." -ForegroundColor Green
}

$cursorPath = Join-Path $WorkspaceRoot ".cursorrules"
if (Test-Path $cursorPath) {
    Remove-Item -Force -Path $cursorPath
    Write-Host "  [OK] .cursorrules removed." -ForegroundColor Green
}

$claudePath = Join-Path $WorkspaceRoot "CLAUDE.md"
if (Test-Path $claudePath) {
    Remove-Item -Force -Path $claudePath
    Write-Host "  [OK] CLAUDE.md removed." -ForegroundColor Green
}

$envPath = Join-Path $WorkspaceRoot ".env"
if (Test-Path $envPath) {
    Remove-Item -Force -Path $envPath
    Write-Host "  [OK] .env removed (secrets purged)." -ForegroundColor Green
} else {
    Write-Host "  [INFO] .env not found." -ForegroundColor Gray
}

$venvPath = Join-Path $WorkspaceRoot ".venv"
if (Test-Path $venvPath) {
    Remove-Item -Recurse -Force -Path $venvPath -ErrorAction SilentlyContinue
    Write-Host "  [OK] .venv/ removed." -ForegroundColor Green
} else {
    Write-Host "  [INFO] .venv/ not found." -ForegroundColor Gray
}

foreach ($f in @("requirements.txt")) {
    $fPath = Join-Path $WorkspaceRoot $f
    if (Test-Path $fPath) {
        Remove-Item -Force -Path $fPath
        Write-Host "  [OK] $f removed." -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "  Preserved (served to client):" -ForegroundColor Cyan
foreach ($f in @("docs/MEMORY.md", "docs/SPEC.md", ".gitignore")) {
    $fPath = Join-Path $WorkspaceRoot $f
    if (Test-Path $fPath) { Write-Host "  [KEEP] $f" -ForegroundColor Green }
}

Write-Host ""
Write-Host "[3/4] Force-killing locked processes..." -ForegroundColor Yellow

$escapedToolkitPath = [regex]::Escape($ToolkitRoot)
$killedCount = 0

$procNames = @("python", "pythonw", "node", "npm", "npx",
               "chrome", "chromium", "chrome-headless-shell",
               "playwright", "msedge")
foreach ($procName in $procNames) {
    Get-Process -Name $procName -ErrorAction SilentlyContinue | Where-Object {
        try {
            $_.Path -and $_.Path -match $escapedToolkitPath
        } catch { $false }
    } | ForEach-Object {
        Write-Host "  [KILL] $($_.ProcessName) (PID $($_.Id)) - $($_.Path)" -ForegroundColor Red
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        $killedCount++
    }
}
if ($killedCount -gt 0) {
    Start-Sleep -Seconds 2
    Write-Host "  [OK] Killed $killedCount locked process(es)." -ForegroundColor Green
} else {
    Write-Host "  [OK] No locked processes found." -ForegroundColor Green
}

Write-Host ""
Write-Host "[4/4] Physically shredding src/ and tests/ directories..." -ForegroundColor Yellow

Set-Location $WorkspaceRoot

foreach ($dir in @("src", "tests")) {
    $dirPath = Join-Path $WorkspaceRoot $dir
    if (Test-Path $dirPath) {
        Remove-Item -Recurse -Force -Path $dirPath -ErrorAction SilentlyContinue
        if (-not (Test-Path $dirPath)) {
            Write-Host "  [OK] $dir/ removed." -ForegroundColor Green
        } else {
            Write-Host "  [WARN] $dir/ could not be fully removed." -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[OK] Git Hook restored, IDE rules uninstalled." -ForegroundColor Green
Write-Host "[OK] docs/MEMORY.md / docs/SPEC.md / .gitignore safely preserved." -ForegroundColor Green
Write-Host "[OK] src/ and tests/ physically shredded." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

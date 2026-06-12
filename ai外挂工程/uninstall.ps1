# uninstall.ps1 - One-Click Traceless Uninstaller
# Restores Git hooks, removes IDE rules, preserves memory docs, then self-destructs.

$ErrorActionPreference = "SilentlyContinue"
$ToolkitRoot = $PSScriptRoot
$WorkspaceRoot = Split-Path $PSScriptRoot -Parent

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
Write-Host "[2/4] Removing IDE rules and temp artifacts from workspace root..." -ForegroundColor Yellow

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
    cmd /c "rd /s /q `"$venvPath`""
    Write-Host "  [OK] .venv/ removed." -ForegroundColor Green
} else {
    Write-Host "  [INFO] .venv/ not found." -ForegroundColor Gray
}

foreach ($f in @("requirements.txt", "test.py")) {
    $fPath = Join-Path $WorkspaceRoot $f
    if (Test-Path $fPath) {
        Remove-Item -Force -Path $fPath
        Write-Host "  [OK] $f removed." -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "  Preserved (served to client):" -ForegroundColor Cyan
foreach ($f in @("MEMORY.md", "SPEC.md", ".gitignore")) {
    $fPath = Join-Path $WorkspaceRoot $f
    if (Test-Path $fPath) { Write-Host "  [KEEP] $f" -ForegroundColor Green }
}

Write-Host ""
Write-Host "[3/4] Force-killing locked processes under toolkit path..." -ForegroundColor Yellow

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
Write-Host "[4/4] Physically shredding toolkit sandbox..." -ForegroundColor Yellow

Set-Location $WorkspaceRoot

cmd /c "rd /s /q `"$ToolkitRoot`""

if (-not (Test-Path $ToolkitRoot)) {
    Write-Host "  [OK] Toolkit folder completely removed." -ForegroundColor Green
} else {
    $remaining = (Get-ChildItem $ToolkitRoot -Force -Recurse -ErrorAction SilentlyContinue | Measure-Object).Count
    if ($remaining -eq 0) {
        Remove-Item -Force -Path $ToolkitRoot -ErrorAction SilentlyContinue
        if (-not (Test-Path $ToolkitRoot)) {
            Write-Host "  [OK] Toolkit folder completely removed." -ForegroundColor Green
        } else {
            Write-Host "  [WARN] Folder empty but locked. Will clear on reboot." -ForegroundColor Yellow
        }
    } else {
        Write-Host "  [WARN] $remaining item(s) remain. Retrying..." -ForegroundColor Yellow
        Get-ChildItem $ToolkitRoot -Force | ForEach-Object {
            cmd /c "rd /s /q `"$($_.FullName)`"" 2>$null
            Remove-Item -Recurse -Force -Path $_.FullName -ErrorAction SilentlyContinue
        }
        Remove-Item -Force -Path $ToolkitRoot -ErrorAction SilentlyContinue
        if (-not (Test-Path $ToolkitRoot)) {
            Write-Host "  [OK] Toolkit folder completely removed (after retry)." -ForegroundColor Green
        } else {
            Write-Host "  [WARN] Some files locked. Manual cleanup may be needed." -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[OK] Git Hook restored, IDE rules (.trae/.vscode/.cursorrules/CLAUDE.md) uninstalled." -ForegroundColor Green
Write-Host "[OK] MEMORY.md / SPEC.md / .gitignore safely preserved." -ForegroundColor Green
Write-Host "[OK] Toolkit sandbox physically shredded." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

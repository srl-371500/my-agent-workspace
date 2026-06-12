# setup.ps1 - Agent Sandbox Workspace Setup and Deployment Script
# Subfolder Mode: Deploys to parent directory when running from toolkit subfolder

param(
    [switch]$Sync,
    [string]$CorePath = "D:/AI_Sandbox_Arsenal_Core"
)

$ErrorActionPreference = "Stop"
$ToolkitRoot = $PSScriptRoot
$ParentDir = Split-Path $PSScriptRoot -Parent

$hasToolkitModules = (Test-Path "$ToolkitRoot/01_memory_core") -and (Test-Path "$ToolkitRoot/02_git_defender")
$parentIsDifferent = ($ParentDir -ne $ToolkitRoot)

if ($hasToolkitModules -and $parentIsDifferent) {
    $WorkspaceRoot = $ParentDir
    Write-Host "[MODE] Subfolder toolkit detected." -ForegroundColor Yellow
} else {
    $WorkspaceRoot = $ToolkitRoot
    Write-Host "[MODE] Standalone workspace mode." -ForegroundColor Yellow
}

$ToolkitName = Split-Path $ToolkitRoot -Leaf

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Agent Sandbox Workspace Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Toolkit Root:   $ToolkitRoot" -ForegroundColor Gray
Write-Host "Workspace Root: $WorkspaceRoot" -ForegroundColor Gray
Write-Host ""

if ($Sync) {
    Write-Host "Starting golden base sync upgrade..." -ForegroundColor Yellow
    Write-Host "Golden base path: $CorePath" -ForegroundColor Cyan

    if (-not (Test-Path $CorePath)) {
        Write-Host "[ERROR] Golden base path not found: $CorePath" -ForegroundColor Red
        exit 1
    }

    Write-Host "`n[1/2] Syncing githooks/ latest fixes..." -ForegroundColor Cyan
    if (Test-Path "$CorePath/githooks") {
        Copy-Item -Path "$CorePath/githooks/*" -Destination "$ToolkitRoot/02_git_defender/githooks/" -Recurse -Force
        Write-Host "[SUCCESS] githooks/ synced." -ForegroundColor Green
    }

    Write-Host "`n[2/2] Syncing services/ latest fixes..." -ForegroundColor Cyan
    if (Test-Path "$CorePath/services") {
        Copy-Item -Path "$CorePath/services/*" -Destination "$ToolkitRoot/03_browser_crawler/services/" -Recurse -Force
        Write-Host "[SUCCESS] services/ synced." -ForegroundColor Green
    }

    Write-Host "`n[SUCCESS] Golden base sync completed!" -ForegroundColor Green
    exit 0
}

Write-Host "[1/6] Verifying 01_memory_core..." -ForegroundColor Cyan
if (Test-Path "$ToolkitRoot/01_memory_core") {
    $rulesSource = "$ToolkitRoot/01_memory_core/.trae/rules"
    if (Test-Path $rulesSource) {
        if (-not (Test-Path "$WorkspaceRoot/.trae/rules")) {
            New-Item -ItemType Directory -Force -Path "$WorkspaceRoot/.trae/rules" | Out-Null
        }
        Copy-Item -Path "$rulesSource/*" -Destination "$WorkspaceRoot/.trae/rules/" -Recurse -Force
        Write-Host "[SUCCESS] Trae native rules loaded." -ForegroundColor Green
    }

    if (-not (Test-Path "$WorkspaceRoot/MEMORY.md")) {
        if (Test-Path "$ToolkitRoot/01_memory_core/MEMORY_TEMPLATE.md") {
            Copy-Item -Path "$ToolkitRoot/01_memory_core/MEMORY_TEMPLATE.md" -Destination "$WorkspaceRoot/MEMORY.md" -Force
            Write-Host "[SUCCESS] Memory template generated as MEMORY.md." -ForegroundColor Green
        } else {
            New-Item -Path "$WorkspaceRoot/MEMORY.md" -ItemType File | Out-Null
            Write-Host "[SUCCESS] Empty MEMORY.md created." -ForegroundColor Green
        }
    } else {
        Write-Host "[INFO] MEMORY.md already exists, skipping." -ForegroundColor Gray
    }
}

Write-Host "`n[2/6] Verifying 02_git_defender..." -ForegroundColor Cyan
if (Test-Path "$ToolkitRoot/02_git_defender") {
    Write-Host "[SUCCESS] 02_git_defender module verified." -ForegroundColor Green

    if ((Test-Path "$ToolkitRoot/.gitignore") -and (-not (Test-Path "$WorkspaceRoot/.gitignore"))) {
        Copy-Item -Path "$ToolkitRoot/.gitignore" -Destination "$WorkspaceRoot/.gitignore" -Force
        Write-Host "[SUCCESS] .gitignore deployed." -ForegroundColor Green
    }

    if (-not (Test-Path "$WorkspaceRoot/.git")) {
        Push-Location $WorkspaceRoot
        git init 2>&1 | Out-Null
        Pop-Location
        Write-Host "[SUCCESS] Git repository initialized." -ForegroundColor Green
    }

    Push-Location $WorkspaceRoot
    $hooksPath = "$ToolkitName/02_git_defender/githooks"
    git config core.hooksPath $hooksPath
    Pop-Location
    Write-Host "[SUCCESS] Git hooks bound to $hooksPath." -ForegroundColor Green
}

Write-Host "`n[3/6] Verifying 03_browser_crawler..." -ForegroundColor Cyan
if (Test-Path "$ToolkitRoot/03_browser_crawler") {
    Write-Host "[SUCCESS] 03_browser_crawler module verified." -ForegroundColor Green
}

Write-Host "`n[4/6] Creating .env configuration..." -ForegroundColor Cyan
if (-not (Test-Path "$WorkspaceRoot/.env")) {
    $envExamplePath = "$ToolkitRoot/.env.example"
    if (Test-Path $envExamplePath) {
        $envContent = Get-Content $envExamplePath -Raw -Encoding UTF8
        $existingBrowserPath = "$ToolkitRoot/.playwright-browsers"
        if (Test-Path $existingBrowserPath) {
            $envContent = $envContent -replace 'PLAYWRIGHT_BROWSERS_PATH="[^"]*"', "PLAYWRIGHT_BROWSERS_PATH=`"$existingBrowserPath`""
        }
        Set-Content -Path "$WorkspaceRoot/.env" -Value $envContent -Encoding UTF8
        Write-Host "[SUCCESS] .env created at workspace root." -ForegroundColor Green
    }
} else {
    Write-Host "[INFO] .env already exists, skipping." -ForegroundColor Gray
}

Write-Host "`n[5/6] Setting up Python virtual environment..." -ForegroundColor Cyan
$venvPath = "$WorkspaceRoot/.venv"
$requirementsPath = "$WorkspaceRoot/requirements.txt"

$requirementsContent = @"
browser-use>=0.1.0
playwright>=1.40.0
openai>=1.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0
pyyaml>=6.0
beautifulsoup4>=4.12.0
markdown>=3.5.0
httpx>=0.25.0
"@

if (-not (Test-Path $requirementsPath)) {
    Set-Content -Path $requirementsPath -Value $requirementsContent -Encoding UTF8
    Write-Host "[INFO] Created requirements.txt." -ForegroundColor Gray
}

if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $venvPath
    Write-Host "[SUCCESS] Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "[INFO] Virtual environment already exists." -ForegroundColor Gray
}

Write-Host "Installing dependencies (Tsinghua mirror)..." -ForegroundColor Yellow
$pythonExe = "$venvPath/Scripts/python.exe"
& $pythonExe -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn --timeout 60 -r $requirementsPath --quiet 2>&1 | Out-Null
Write-Host "[SUCCESS] Python dependencies configured." -ForegroundColor Green

Write-Host "`n[6/6] Verifying Playwright browsers..." -ForegroundColor Cyan
$browsersPath = "$ToolkitRoot/.playwright-browsers"
$env:PLAYWRIGHT_BROWSERS_PATH = $browsersPath

if (Test-Path "$browsersPath/chromium-1223") {
    Write-Host "[SUCCESS] Chromium found at: $browsersPath" -ForegroundColor Green
} else {
    if (-not (Test-Path $browsersPath)) {
        New-Item -ItemType Directory -Force -Path $browsersPath | Out-Null
    }
    & $pythonExe -m playwright install chromium
    Write-Host "[SUCCESS] Chromium installed to: $browsersPath" -ForegroundColor Green
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

# setup.ps1 - Agent Sandbox Workspace Setup and Deployment Script
# D-Drive Absolute Isolation: All files must be saved under D:\my-agent-workspace
# No-Admin Required: All operations work without administrator privileges
# Suitcase Architecture: All business files stay inside 01/02/03 modules

param(
    [switch]$Sync,
    [string]$CorePath = "D:/AI_Sandbox_Arsenal_Core"
)

$ErrorActionPreference = "Stop"
$WorkspaceRoot = $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Agent Sandbox Workspace Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Workspace Root: $WorkspaceRoot" -ForegroundColor Gray
Write-Host ""

if ($Sync) {
    Write-Host "Starting golden base sync upgrade..." -ForegroundColor Yellow
    Write-Host "Golden base path: $CorePath" -ForegroundColor Cyan
    
    if (-not (Test-Path $CorePath)) {
        Write-Host "[ERROR] Golden base path not found: $CorePath" -ForegroundColor Red
        Write-Host "Please ensure the golden base is deployed to the specified path." -ForegroundColor Red
        exit 1
    }
    
    Write-Host "`n[1/2] Syncing githooks/ latest fixes..." -ForegroundColor Cyan
    if (Test-Path "$CorePath/githooks") {
        Copy-Item -Path "$CorePath/githooks/*" -Destination "$WorkspaceRoot/02_git_defender/githooks/" -Recurse -Force
        Write-Host "[SUCCESS] githooks/ synced to 02_git_defender/githooks/." -ForegroundColor Green
    } else {
        Write-Host "[WARNING] githooks/ not found in golden base, skipping." -ForegroundColor Yellow
    }
    
    Write-Host "`n[2/2] Syncing services/ latest fixes..." -ForegroundColor Cyan
    if (Test-Path "$CorePath/services") {
        Copy-Item -Path "$CorePath/services/*" -Destination "$WorkspaceRoot/03_browser_crawler/services/" -Recurse -Force
        Write-Host "[SUCCESS] services/ synced to 03_browser_crawler/services/." -ForegroundColor Green
    } else {
        Write-Host "[WARNING] services/ not found in golden base, skipping." -ForegroundColor Yellow
    }
    
    Write-Host "`n[SUCCESS] Golden base sync completed!" -ForegroundColor Green
    Write-Host "All files synced to suitcase modules (01/02/03)." -ForegroundColor Cyan
    exit 0
}

Write-Host "[1/4] Verifying 01_memory_core..." -ForegroundColor Cyan
if (Test-Path "$WorkspaceRoot/01_memory_core") {
    if (-not (Test-Path "$WorkspaceRoot/.trae/rules")) {
        New-Item -ItemType Directory -Force -Path "$WorkspaceRoot/.trae/rules" | Out-Null
    }
    Copy-Item -Path "$WorkspaceRoot/01_memory_core/.trae/rules/*" -Destination "$WorkspaceRoot/.trae/rules/" -Recurse -Force
    Write-Host "[SUCCESS] Trae native rules loaded." -ForegroundColor Green

    if (-not (Test-Path "$WorkspaceRoot/MEMORY.md")) {
        if (Test-Path "$WorkspaceRoot/01_memory_core/MEMORY_TEMPLATE.md") {
            Copy-Item -Path "$WorkspaceRoot/01_memory_core/MEMORY_TEMPLATE.md" -Destination "$WorkspaceRoot/MEMORY.md" -Force
            Write-Host "[SUCCESS] Memory template generated as MEMORY.md." -ForegroundColor Green
        } else {
            New-Item -Path "$WorkspaceRoot/MEMORY.md" -ItemType File | Out-Null
            Write-Host "[SUCCESS] Empty MEMORY.md created." -ForegroundColor Green
        }
    }
}

Write-Host "`n[2/4] Verifying 02_git_defender..." -ForegroundColor Cyan
if (Test-Path "$WorkspaceRoot/02_git_defender") {
    Write-Host "[SUCCESS] 02_git_defender module verified." -ForegroundColor Green
    if (Test-Path "$WorkspaceRoot/.git") {
        Set-Location $WorkspaceRoot
        git config core.hooksPath 02_git_defender/githooks
        Write-Host "[SUCCESS] Git hooks bound to 02_git_defender/githooks/." -ForegroundColor Green
    } else {
        Write-Host "[WARNING] Not a git repository. Run 'git init' first." -ForegroundColor Yellow
    }
}

Write-Host "`n[3/4] Verifying 03_browser_crawler..." -ForegroundColor Cyan
if (Test-Path "$WorkspaceRoot/03_browser_crawler") {
    Write-Host "[SUCCESS] 03_browser_crawler module verified." -ForegroundColor Green
}

Write-Host "`n[4/4] Setting up Python virtual environment..." -ForegroundColor Cyan
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
    Write-Host "[INFO] Created requirements.txt with all dependencies." -ForegroundColor Gray
}

if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment at $venvPath..." -ForegroundColor Yellow
    python -m venv $venvPath
    Write-Host "[SUCCESS] Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "[INFO] Virtual environment already exists." -ForegroundColor Gray
}

Write-Host "Installing dependencies into virtual environment (using Tsinghua mirror)..." -ForegroundColor Yellow
$pythonExe = "$venvPath/Scripts/python.exe"
$mirrorArgs = @("-i", "https://pypi.tuna.tsinghua.edu.cn/simple", "--trusted-host", "pypi.tuna.tsinghua.edu.cn", "--timeout", "60")

& $pythonExe -m pip install @mirrorArgs -r $requirementsPath --quiet
Write-Host "[SUCCESS] Python dependencies configured in .venv." -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Suitcase Architecture:" -ForegroundColor Gray
Write-Host "  01_memory_core/    - Memory and config" -ForegroundColor Gray
Write-Host "  02_git_defender/   - Git hooks and security" -ForegroundColor Gray
Write-Host "  03_browser_crawler/ - Crawler and services" -ForegroundColor Gray
Write-Host ""
Write-Host "Virtual environment: $venvPath" -ForegroundColor Gray
Write-Host "To activate manually: .\.venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "You can now start working in Trae." -ForegroundColor Green
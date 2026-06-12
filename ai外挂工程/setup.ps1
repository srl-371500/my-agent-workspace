# setup.ps1 - Agent Sandbox Workspace Setup and Deployment Script
# Subfolder Mode: Deploys to parent directory when running from toolkit subfolder

param(
    [switch]$Sync,
    [string]$CorePath = "D:/AI_Sandbox_Arsenal_Core"
)

$ErrorActionPreference = "Stop"

function Find-ProjectRoot {
    param([string]$StartDir)
    $markers = @(".git", "package.json", ".trae", ".vscode")
    $current = (Resolve-Path $StartDir).Path
    while ($true) {
        foreach ($m in $markers) {
            if (Test-Path (Join-Path $current $m)) {
                return $current
            }
        }
        $parent = Split-Path $current -Parent
        if (-not $parent -or $parent -eq $current) {
            return $current
        }
        $current = $parent
    }
}

$ToolkitRoot = $PSScriptRoot
$WorkspaceRoot = Find-ProjectRoot (Split-Path $ToolkitRoot -Parent)

if ($WorkspaceRoot -eq $ToolkitRoot) {
    Write-Host "[MODE] Standalone workspace mode." -ForegroundColor Yellow
    $WorkspaceRoot = $ToolkitRoot
} else {
    Write-Host "[MODE] Subfolder toolkit detected. Host root: $WorkspaceRoot" -ForegroundColor Yellow
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

    Write-Host "`n[SUCCESS] Golden base sync completed!" -ForegroundColor Green
    exit 0
}

Write-Host "[1/5] Meta-Rule Adaptive Injector..." -ForegroundColor Cyan
$rulesSource = "$ToolkitRoot/01_memory_core/.trae/rules"
if (-not (Test-Path $rulesSource)) { Write-Host "  [WARN] No rules source." -ForegroundColor Yellow }
else {
    $combined = @(); foreach ($f in Get-ChildItem "$rulesSource/*.md") { $combined += (Get-Content $f.FullName -Raw -Encoding UTF8) }
    $merged = $combined -join "`n`n---`n`n"

    $archCmd = "python ai外挂工程/01_memory_core/archive_chronicle.py"
    $toolkitName = Split-Path $ToolkitRoot -Leaf
    $claudeContent = @"
# Project Rules — Agent Sandbox Toolkit

## Development
- Toolkit: $toolkitName/
- Memory Core: $toolkitName/01_memory_core/
- Git Defender: $toolkitName/02_git_defender/githooks/

## Testing
- ``python -m py_compile $toolkitName/01_memory_core/utils.py``
- ``python -m py_compile $toolkitName/01_memory_core/archive_chronicle.py``
- ``python -m py_compile $toolkitName/02_git_defender/githooks/pre-commit-audit.py``

## Memory Management
- MEMORY.md is the active log. When entries > 5, run:
  ``$archCmd``
- LLM summarization requires .env with LLM_API_KEY configured.
"@

    $ruleMatrix = @(
        @{ Name="Trae";    Type="file"; Target="$WorkspaceRoot/.trae/rules/memory-agent.md"; Content=$merged },
        @{ Name="VS Code"; Type="file"; Target="$WorkspaceRoot/.vscode/copilot-instructions.md"; Content=$merged },
        @{ Name="Cursor";  Type="file"; Target="$WorkspaceRoot/.cursorrules"; Content=$merged },
        @{ Name="Claude";  Type="file"; Target="$WorkspaceRoot/CLAUDE.md"; Content=$claudeContent }
    )

    $deployed = @()
    foreach ($r in $ruleMatrix) {
        $dir = Split-Path $r.Target -Parent
        if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
        Set-Content -Path $r.Target -Value $r.Content -Encoding UTF8
        $deployed += "  [OK] $($r.Name): $(Split-Path $r.Target -Leaf)"
    }

    $futureTargets = @()
    Get-ChildItem $WorkspaceRoot -Force -ErrorAction SilentlyContinue | ForEach-Object {
        $name = $_.Name.ToLower()
        if ($name -match 'claude|cursor|vscode|copilot|agent|codex') {
            if ($_.PSIsContainer) {
                $cfg = Get-ChildItem $_.FullName -File -Recurse -Depth 1 -ErrorAction SilentlyContinue |
                    Where-Object { $_.Name -match '\.(md|txt|rules|json)$' -and $_.Length -lt 512000 }
                foreach ($c in $cfg) { $futureTargets += $c.FullName }
            } elseif ($_.Name -match '\.(md|txt|rules)$') {
                $futureTargets += $_.FullName
            }
        }
    }
    foreach ($ft in $futureTargets) {
        $existing = Get-Content $ft -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
        if ($existing -and $existing -notmatch "Agent Sandbox Toolkit") {
            Add-Content -Path $ft -Value "`n`n---`n`n$merged" -Encoding UTF8
            $deployed += "  [INJECT] $(Split-Path $ft -Leaf)"
        }
    }
    $deployed | ForEach-Object { Write-Host $_ -ForegroundColor Green }
}

if (-not (Test-Path "$WorkspaceRoot/MEMORY.md")) {
    New-Item -Path "$WorkspaceRoot/MEMORY.md" -ItemType File -Force | Out-Null
    Write-Host "  [OK] MEMORY.md" -ForegroundColor Green
}

Write-Host "`n[2/5] Verifying 02_git_defender..." -ForegroundColor Cyan
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

Write-Host "`n[3/5] Creating .env configuration..." -ForegroundColor Cyan
$absBrowsersPath = "$ToolkitRoot/.playwright-browsers"
$absPipCachePath = "$ToolkitRoot/.pip-cache"
if (-not (Test-Path "$WorkspaceRoot/.env")) {
    $envExamplePath = "$ToolkitRoot/.env.example"
    if (Test-Path $envExamplePath) {
        Copy-Item -Path $envExamplePath -Destination "$WorkspaceRoot/.env" -Force
        Write-Host "[SUCCESS] .env created from template at $WorkspaceRoot\.env" -ForegroundColor Green
    }
}
if (Test-Path "$WorkspaceRoot/.env") {
    $envContent = Get-Content "$WorkspaceRoot/.env" -Raw -Encoding UTF8
    $envContent = $envContent -replace '(?m)^PLAYWRIGHT_BROWSERS_PATH=.*$', "PLAYWRIGHT_BROWSERS_PATH=`"$absBrowsersPath`""
    $envContent = $envContent -replace '(?m)^PIP_CACHE_DIR=.*$', "PIP_CACHE_DIR=`"$absPipCachePath`""
    Set-Content -Path "$WorkspaceRoot/.env" -Value $envContent -Encoding UTF8 -NoNewline
    Write-Host "[SUCCESS] .env paths normalized to absolute." -ForegroundColor Green
} else {
    Write-Host "[WARN] .env not found, skipping path normalization." -ForegroundColor Yellow
}

Write-Host "`n[4/5] Setting up Python virtual environment..." -ForegroundColor Cyan
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

Write-Host "`n[5/5] Verifying Playwright browsers..." -ForegroundColor Cyan
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

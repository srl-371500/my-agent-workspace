#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Register a daily scheduled task for Browser Distillation Service.
.DESCRIPTION
    This script registers a Windows Task Scheduler task that runs
    analyze_portfolio.py daily at 9:00 AM using the local .venv Python.
.NOTES
    Run this script as Administrator:
    Right-click PowerShell -> Run as Administrator
    Then execute: .\register_cron.ps1
#>

$TaskName = "BrowserDistillation_DailyAnalysis"
$TaskDescription = "Daily portfolio analysis using MiMo-V2.5 + browser-use"

$ScriptDir = $PSScriptRoot
$CrawlerRoot = Split-Path (Split-Path $ScriptDir)
$WorkspaceRoot = Split-Path $CrawlerRoot
$PythonExe = "$WorkspaceRoot\.venv\Scripts\python.exe"
$ScriptPath = "$ScriptDir\analyze_portfolio.py"
$LogDir = "$CrawlerRoot\logs"
$LogFile = "$LogDir\scheduled_task.log"

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

Write-Host "=" * 60
Write-Host "Browser Distillation - Task Scheduler Registration"
Write-Host "=" * 60
Write-Host ""
Write-Host "Crawler Root: $CrawlerRoot"
Write-Host "Python:       $PythonExe"
Write-Host "Script:       $ScriptPath"
Write-Host "Log File:     $LogFile"
Write-Host ""

if (-not (Test-Path $PythonExe)) {
    Write-Host "[ERROR] Python not found at: $PythonExe" -ForegroundColor Red
    Write-Host "Please ensure the virtual environment exists." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $ScriptPath)) {
    Write-Host "[ERROR] Script not found at: $ScriptPath" -ForegroundColor Red
    exit 1
}

$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($ExistingTask) {
    Write-Host "[INFO] Task '$TaskName' already exists. Removing..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

$Action = New-ScheduledTaskAction `
    -Execute $PythonExe `
    -Argument $ScriptPath `
    -WorkingDirectory $ScriptDir

$Trigger = New-ScheduledTaskTrigger `
    -Daily `
    -At "09:00AM"

$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
    -RestartCount 2 `
    -RestartInterval (New-TimeSpan -Minutes 5)

$Principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Highest

$Task = Register-ScheduledTask `
    -TaskName $TaskName `
    -Description $TaskDescription `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal

if ($Task) {
    Write-Host ""
    Write-Host "[SUCCESS] Task registered successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:" -ForegroundColor Cyan
    Write-Host "  Name:        $TaskName"
    Write-Host "  Schedule:    Daily at 09:00 AM"
    Write-Host "  Python:      $PythonExe"
    Write-Host "  Script:      $ScriptPath"
    Write-Host "  Working Dir: $ScriptDir"
    Write-Host ""
    Write-Host "To test the task manually:" -ForegroundColor Yellow
    Write-Host "  Start-ScheduledTask -TaskName '$TaskName'"
    Write-Host ""
    Write-Host "To remove the task:" -ForegroundColor Yellow
    Write-Host "  Unregister-ScheduledTask -TaskName '$TaskName'"
    Write-Host ""
    Write-Host "To view task status:" -ForegroundColor Yellow
    Write-Host "  Get-ScheduledTask -TaskName '$TaskName'"
    Write-Host ""
    Write-Host "=" * 60
} else {
    Write-Host "[ERROR] Failed to register task." -ForegroundColor Red
    exit 1
}
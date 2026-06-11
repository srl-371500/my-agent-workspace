@echo off
REM Browser Distillation Service - One-Click Launcher
REM This script can be used with Windows Task Scheduler for automated runs

REM Force working directory to this script's location (prevents C:\Windows\system32 issue)
cd /d "%~dp0"

echo ========================================
echo Browser Distillation Service
echo ========================================
echo.
echo Working directory: %CD%
echo.

REM Set environment variables
set BROWSER_USE_DISABLE_EXTENSIONS=true

REM Use unified virtual environment from workspace root
set PYTHON_EXE=..\..\..\.venv\Scripts\python.exe

REM Verify Python executable exists
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python virtual environment not found at: %PYTHON_EXE%
    echo Please run setup.ps1 first to create the virtual environment.
    pause
    exit /b 1
)

REM Run the analysis
echo Starting portfolio analysis...
echo.
"%PYTHON_EXE%" analyze_portfolio.py

echo.
echo ========================================
echo Analysis complete!
echo Report saved to: ..\..\reports\portfolio_inspiration_report.md
echo ========================================

pause
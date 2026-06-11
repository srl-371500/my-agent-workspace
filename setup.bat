@echo off
REM Agent Sandbox Workspace Setup Launcher
REM Usage:
REM   Double-click: One-click deployment
REM   Command line: setup.bat -Sync  Golden base sync upgrade

if "%1"=="-Sync" (
    echo Starting golden base sync upgrade...
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1" -Sync
) else (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
)
pause
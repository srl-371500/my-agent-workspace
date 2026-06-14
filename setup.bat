@echo off
REM Agent Sandbox Workspace Setup Launcher
REM Double-click to run one-click deployment.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
pause

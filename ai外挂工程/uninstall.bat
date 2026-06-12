@echo off
REM Traceless Uninstaller Launcher
REM Double-click to run: restores Git, removes IDE rules, self-destructs toolkit.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0uninstall.ps1"
pause

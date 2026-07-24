@echo off

net session >nul 2>&1

if %errorlevel% == 0 (
    echo Running as admin
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
    pause
)
if %errorlevel% neq 0 (
     powershell -Command "Start-Process '%~f0' -Verb RunAs"
     echo Not running as admin
)
@echo off
title MongoDB Lab 7 Interactive Dashboard
cd /d "%~dp0"
echo ============================================================
echo   Starting MongoDB Lab 7 Interactive Web Platform...
echo ============================================================
echo.
py website\server.py 8000
if %errorlevel% neq 0 (
    python website\server.py 8000
)
pause

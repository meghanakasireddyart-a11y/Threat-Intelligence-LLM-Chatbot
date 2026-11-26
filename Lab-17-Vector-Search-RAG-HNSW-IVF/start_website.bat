@echo off
title MongoDB NoSQL Lab 17 Interactive Dashboard
cd /d "%~dp0"
echo ============================================================
echo   Starting NoSQL Lab 17 Interactive Web Platform...
echo ============================================================
echo.
py website\server.py 8017
if %errorlevel% neq 0 (
    python website\server.py 8017
)
pause

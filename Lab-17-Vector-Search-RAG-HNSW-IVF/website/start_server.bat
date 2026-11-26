@echo off
title MongoDB Lab 7 Interactive Dashboard
cd /d "%~dp0"
echo Starting MongoDB Lab 7 Web Server on port 8000...
py server.py 8000
if %errorlevel% neq 0 (
    python server.py 8000
)
pause

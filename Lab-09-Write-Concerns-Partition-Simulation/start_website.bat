@echo off
echo Starting NoSQL Lab 9 Interactive Web Platform...
cd /d "%~dp0"
start http://localhost:8009/index.html
py -3 website\server.py
pause

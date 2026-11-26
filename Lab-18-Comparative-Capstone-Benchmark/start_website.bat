@echo off
echo ========================================================
echo  Starting NoSQL Lab 18 Comparative Capstone Platform
echo  Running on http://localhost:8018
echo ========================================================
start "" http://localhost:8018
py -3 website/server.py 8018
if %ERRORLEVEL% NEQ 0 (
  python website/server.py 8018
)
pause

@echo off
title Threat Intelligence Platform
cd /d "%~dp0"
echo ======================================================================
echo  Launching Threat Intelligence AI Platform on http://localhost:5000
echo ======================================================================
echo Opening default web browser...
start "" "http://localhost:5000"
echo Starting web server...
"C:\Users\Prajwal\AppData\Local\Programs\Python\Python313\python.exe" web_ui.py
pause

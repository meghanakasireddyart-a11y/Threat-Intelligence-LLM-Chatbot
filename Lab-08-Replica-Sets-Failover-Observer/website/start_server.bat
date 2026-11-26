@echo off
title NoSQL Lab 8 - MongoDB Replication Web Portal
cd /d "%~dp0"

set PY_EXE=python
if exist "C:\Users\Prajwal\AppData\Local\Programs\Python\Python313\python.exe" (
    set PY_EXE="C:\Users\Prajwal\AppData\Local\Programs\Python\Python313\python.exe"
)

%PY_EXE% server.py
pause

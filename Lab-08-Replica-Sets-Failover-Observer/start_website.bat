@echo off
title NoSQL Lab 8 - MongoDB Replication Web Portal
cd /d "%~dp0"

echo ======================================================================
echo    Starting NoSQL Lab 8: MongoDB Replication & Failover Web Portal
echo    Student: Kasireddy Meghana (24BTRCL119)
echo ======================================================================

set PY_EXE=python
if exist "C:\Users\Prajwal\AppData\Local\Programs\Python\Python313\python.exe" (
    set PY_EXE="C:\Users\Prajwal\AppData\Local\Programs\Python\Python313\python.exe"
)

echo Starting HTTP Server with %PY_EXE%...
%PY_EXE% website\server.py

pause

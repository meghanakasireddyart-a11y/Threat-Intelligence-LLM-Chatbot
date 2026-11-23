$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptPath

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " Launching Threat Intelligence AI Platform on http://localhost:5000" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan

Start-Process "http://localhost:5000"
& "C:\Users\Prajwal\AppData\Local\Programs\Python\Python313\python.exe" web_ui.py

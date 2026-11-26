@echo off
echo ========================================================================
echo   NoSQL Lab 9: Docker Build & Push Helper
echo   Student: Kasireddy Meghana (24BTRCL119)
echo ========================================================================
echo.

set IMAGE_NAME=kasireddymeghana/nosql-lab09:latest

echo Step 1: Building Docker Image %IMAGE_NAME%...
docker build -t %IMAGE_NAME% .
if %errorlevel% neq 0 (
    echo [ERROR] Docker build failed. Please make sure Docker Desktop is running.
    pause
    exit /b %errorlevel%
)

echo.
echo Step 2: Pushing to Docker Hub...
docker push %IMAGE_NAME%
if %errorlevel% neq 0 (
    echo [WARNING] Docker push requires prior 'docker login'.
    echo Please run 'docker login' and try again.
    pause
    exit /b %errorlevel%
)

echo.
echo [SUCCESS] Successfully deployed to Docker Hub: https://hub.docker.com/r/kasireddymeghana/nosql-lab09
pause

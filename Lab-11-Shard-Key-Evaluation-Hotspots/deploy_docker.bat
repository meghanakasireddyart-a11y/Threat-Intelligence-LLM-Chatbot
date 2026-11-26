@echo off
REM ==============================================================================
REM Build and Push Docker Demonstration Image for NoSQL Lab 11
REM Student: Kasireddy Meghana (24BTRCL119)
REM Course: NoSQL Databases Using MongoDB
REM Docker Hub Image: kasireddymeghana/nosql-lab11:latest
REM ==============================================================================

echo [1/3] Building Docker image for Lab 11...
docker build -t kasireddymeghana/nosql-lab11:latest .

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker build failed.
    pause
    exit /b %ERRORLEVEL%
)

echo [2/3] Logging into Docker Hub (ensure credentials are configured)...
docker login

echo [3/3] Pushing image to Docker Hub...
docker push kasireddymeghana/nosql-lab11:latest

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==============================================================================
    echo [SUCCESS] Lab 11 Docker image successfully published to:
    echo           https://hub.docker.com/r/kasireddymeghana/nosql-lab11
    echo ==============================================================================
) else (
    echo [ERROR] Docker push encountered an error.
)

pause

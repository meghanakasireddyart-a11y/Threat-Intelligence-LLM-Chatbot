@echo off
echo ========================================
echo  Lab 15 Docker Build and Push Script
echo ========================================

REM Configuration
set DOCKER_USER=meghanakasireddy
set IMAGE_NAME=nosql-lab15
set TAG=latest
set FULL_IMAGE=%DOCKER_USER%/%IMAGE_NAME%:%TAG%
set PORT=8015
set DOCKER_EXE=C:\Users\Prajwal\AppData\Local\Programs\DockerDesktop\resources\bin\docker.exe
set LAB15_DIR=c:\Users\Prajwal\OneDrive\Desktop\NoSQL LAB 15
set LAB7_DIR=c:\Users\Prajwal\OneDrive\Desktop\NoSQL LAB 7

REM Add Docker bin to PATH
set PATH=C:\Users\Prajwal\AppData\Local\Programs\DockerDesktop\resources\bin;%PATH%

echo.
echo [1] Syncing Lab 7 website into Lab 15 context...
if not exist "%LAB15_DIR%\website" mkdir "%LAB15_DIR%\website"
if not exist "%LAB15_DIR%\config" mkdir "%LAB15_DIR%\config"
xcopy /E /Y /Q "%LAB7_DIR%\website\*" "%LAB15_DIR%\website\"
xcopy /E /Y /Q "%LAB7_DIR%\config\*" "%LAB15_DIR%\config\"
echo [OK] Synced website/ and config/ into Lab 15.

echo.
echo [2] Building Docker image: %FULL_IMAGE%
echo     Context: %LAB15_DIR%
echo.

docker build -t %FULL_IMAGE% "%LAB15_DIR%"

if %ERRORLEVEL% NEQ 0 (
  echo [ERROR] Docker build failed!
  pause
  exit /b 1
)

echo [OK] Image built successfully: %FULL_IMAGE%
echo.

echo [3] Testing image locally on port %PORT%...
docker run -d --name nosql-lab15-test -p %PORT%:8000 %FULL_IMAGE%
timeout /t 3 /nobreak > NUL
docker ps --filter "name=nosql-lab15-test"
echo     Open: http://localhost:%PORT%
echo.
echo     Stopping test container and proceeding with push...
docker stop nosql-lab15-test
docker rm nosql-lab15-test

echo.
echo [4] Pushing to Docker Hub: %FULL_IMAGE%
echo.
docker push %FULL_IMAGE%

if %ERRORLEVEL% NEQ 0 (
  echo [ERROR] Push failed! Make sure you are logged in: docker login
  pause
  exit /b 1
)

echo.
echo ========================================
echo [OK] Successfully pushed to Docker Hub!
echo      https://hub.docker.com/r/%DOCKER_USER%/%IMAGE_NAME%
echo ========================================
echo.
echo Pull and run commands:
echo   docker pull %FULL_IMAGE%
echo   docker run -d -p %PORT%:8000 --name nosql-lab15 %FULL_IMAGE%
echo   # Open: http://localhost:%PORT%
echo.
pause

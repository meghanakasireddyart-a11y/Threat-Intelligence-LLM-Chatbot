@echo off
echo ========================================
echo  Lab 13 Docker Build and Push Script
echo ========================================

REM Configuration
set DOCKER_USER=kasireddymeghana
set IMAGE_NAME=nosql-lab13
set TAG=latest
set FULL_IMAGE=%DOCKER_USER%/%IMAGE_NAME%:%TAG%
set PORT=8013
set DOCKER_EXE=C:\Users\Prajwal\AppData\Local\Programs\DockerDesktop\resources\bin\docker.exe
set LAB13_DIR=c:\Users\Prajwal\OneDrive\Desktop\NoSQL LAB 13
set LAB7_DIR=c:\Users\Prajwal\OneDrive\Desktop\NoSQL LAB 7

REM Add Docker bin to PATH
set PATH=C:\Users\Prajwal\AppData\Local\Programs\DockerDesktop\resources\bin;%PATH%

echo.
echo [1] Copying Lab 7 website and config into Lab 13 build context...
if not exist "%LAB13_DIR%\website" mkdir "%LAB13_DIR%\website"
if not exist "%LAB13_DIR%\config" mkdir "%LAB13_DIR%\config"

xcopy /E /Y /Q "%LAB7_DIR%\website\*" "%LAB13_DIR%\website\"
xcopy /E /Y /Q "%LAB7_DIR%\config\*" "%LAB13_DIR%\config\"
echo [OK] Copied website/ and config/ from Lab 7 to Lab 13.

echo.
echo [2] Building Docker image: %FULL_IMAGE%
echo     Context: %LAB13_DIR%
echo.

docker build ^
  -t %FULL_IMAGE% ^
  "%LAB13_DIR%"

if %ERRORLEVEL% NEQ 0 (
  echo [ERROR] Docker build failed!
  pause
  exit /b 1
)

echo [OK] Image built successfully: %FULL_IMAGE%
echo.

echo [3] Testing image locally on port %PORT%...
docker run -d --name nosql-lab13-test -p %PORT%:8000 %FULL_IMAGE%
timeout /t 3 /nobreak > NUL
docker ps --filter "name=nosql-lab13-test"
echo     Open: http://localhost:%PORT%
echo.
echo     Press any key to stop test container and proceed with push...
pause > NUL
docker stop nosql-lab13-test
docker rm nosql-lab13-test

echo.
echo [4] Pushing to Docker Hub: %FULL_IMAGE%
echo     Make sure you are logged in: docker login
echo.
docker push %FULL_IMAGE%

if %ERRORLEVEL% NEQ 0 (
  echo [ERROR] Push failed! Run: docker login
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
echo   docker run -d -p %PORT%:8000 --name nosql-lab13 %FULL_IMAGE%
echo   # Open: http://localhost:%PORT%
echo.
pause

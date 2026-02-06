echo.
echo ========================================
echo %INFO% Docker Deployment Started
echo ========================================
echo.
echo %INFO% Changing directory to: %DEPLOY_DIR%
echo.
echo %INFO% Checking Docker version...
docker --version
echo.
echo.
echo %INFO% Removing old image: %IMAGE_NAME%
docker rmi %IMAGE_NAME% -f
echo.
echo %INFO% Pulling latest image from Docker Hub...
docker pull %IMAGE_NAME%
echo.
echo %INFO% Docker containers before deployment:
echo.
echo %INFO% Starting new containers with docker-compose...
echo.
echo %SUCCESS% Docker containers after deployment:
echo.
echo %INFO% Verifying deployed image:
docker images %IMAGE_NAME%
echo.
echo %INFO% Container logs:
docker-compose logs --tail=20
echo.
echo ========================================
echo %SUCCESS% Docker Deployment Completed Successfully
echo ========================================
echo.
@echo off
REM ========================================
REM Docker Deployment Script for Windows
REM ========================================

setlocal enabledelayedexpansion

REM 배포 설정
set DEPLOY_DIR=C:\Users\kth08\Desktop\soncoding-web
set CONTAINER_NAME=soncoding-app

REM Docker Hub 사용자명: 환경변수 DOCKER_HUB_USER로 오버라이드 가능
if "%DOCKER_HUB_USER%"=="" (
    set DOCKER_HUB_USER=leejinhyuck
)
set IMAGE_REPO=soncoding-server
set IMAGE_TAG=latest
set IMAGE_NAME=%DOCKER_HUB_USER%/%IMAGE_REPO%:%IMAGE_TAG%

REM 색상 정의 (Windows 10 이상)
set "INFO=[INFO]"
set "SUCCESS=[SUCCESS]"
set "ERROR=[ERROR]"
set "WARNING=[WARNING]"

REM ===== 시작 로그 =====
echo.
echo ========================================
echo %INFO% Docker Deployment Started
echo ========================================
echo.

REM ===== 디렉토리 확인 및 이동 =====
echo %INFO% Changing directory to: %DEPLOY_DIR%
if exist "%DEPLOY_DIR%" (
    cd /d %DEPLOY_DIR%
) else (
    echo %WARNING% Deploy directory not found: %DEPLOY_DIR% (continuing)
)

REM ===== Docker 버전 확인 =====
echo.
echo %INFO% Checking Docker version...
docker --version >nul 2>&1
if errorlevel 1 (
    echo %ERROR% Docker is not installed or not running
    pause
    exit /b 1
)

REM ===== 기존 컨테이너 중지 및 제거 (컨테이너명이 'soncoding-app'인 경우) =====
echo.
echo %INFO% Stopping and removing old container: %CONTAINER_NAME%
docker stop %CONTAINER_NAME% >nul 2>&1 || echo %WARNING% No running container to stop
docker rm %CONTAINER_NAME% -f >nul 2>&1 || echo %WARNING% No container to remove

REM ===== 기존 이미지 제거 (선택사항) =====
echo.
echo %INFO% Removing old image: %IMAGE_NAME%
docker rmi %IMAGE_NAME% -f >nul 2>&1 || echo %WARNING% Old image not found or already removed

REM ===== 최신 이미지 풀 =====
echo.
echo %INFO% Pulling latest image from Docker Hub: %IMAGE_NAME%
docker pull %IMAGE_NAME%
if errorlevel 1 (
    echo %ERROR% Failed to pull image from Docker Hub
    pause
    exit /b 1
)

REM ===== 새 컨테이너 실행 =====
echo.
echo %INFO% Running new container: %CONTAINER_NAME%
docker run -d --name %CONTAINER_NAME% --restart unless-stopped -p 80:8000 %IMAGE_NAME%
if errorlevel 1 (
    echo %ERROR% Failed to start container via docker run
    pause
    exit /b 1
)

REM ===== 배포 후 컨테이너 상태 확인 =====
echo.
echo %SUCCESS% Docker containers after deployment:
docker ps

REM ===== 이미지 확인 =====
echo.
echo %INFO% Verifying deployed image:
docker images %IMAGE_NAME%

REM ===== 컨테이너 로그 확인 (선택사항) =====
echo.
echo %INFO% Container logs (last 20 lines):
docker logs %CONTAINER_NAME% --tail 20

REM ===== 배포 완료 =====
echo.
echo ========================================
echo %SUCCESS% Docker Deployment Completed Successfully
echo ========================================
echo.

REM 성공 코드 반환
exit /b 0

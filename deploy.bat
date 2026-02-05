@echo off
REM ========================================
REM Docker Deployment Script for Windows
REM ========================================

setlocal enabledelayedexpansion

REM 배포 설정
set DEPLOY_DIR=C:\Users\kth08\Desktop\soncoding-web
set IMAGE_NAME=thkim0812/soncoding-web:latest
set CONTAINER_NAME=soncoding-app
set DOCKER_HUB_USER=thkim0812

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
cd /d %DEPLOY_DIR%

if errorlevel 1 (
    echo %ERROR% Failed to change directory to %DEPLOY_DIR%
    pause
    exit /b 1
)

echo %SUCCESS% Current directory: 
cd

REM ===== Docker 버전 확인 =====
echo.
echo %INFO% Checking Docker version...
docker --version
if errorlevel 1 (
    echo %ERROR% Docker is not installed or not running
    pause
    exit /b 1
)

REM ===== 기존 컨테이너 중지 및 제거 =====
echo.
echo %INFO% Stopping and removing old containers...
docker-compose down -f --remove-orphans
if errorlevel 1 (
    echo %WARNING% Failed to stop containers (may not exist)
)

REM ===== 기존 이미지 제거 =====
echo.
echo %INFO% Removing old image: %IMAGE_NAME%
docker rmi %IMAGE_NAME% -f
if errorlevel 1 (
    echo %WARNING% Old image not found or already removed
)

REM ===== 최신 이미지 풀 =====
echo.
echo %INFO% Pulling latest image from Docker Hub...
docker pull %IMAGE_NAME%
if errorlevel 1 (
    echo %ERROR% Failed to pull image from Docker Hub
    pause
    exit /b 1
)

REM ===== 배포 전 컨테이너 상태 확인 =====
echo.
echo %INFO% Docker containers before deployment:
docker ps -a

REM ===== 새 컨테이너 실행 =====
echo.
echo %INFO% Starting new containers with docker-compose...
docker-compose up -d
if errorlevel 1 (
    echo %ERROR% Failed to start containers
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
echo %INFO% Container logs:
docker-compose logs --tail=20

REM ===== 배포 완료 =====
echo.
echo ========================================
echo %SUCCESS% Docker Deployment Completed Successfully
echo ========================================
echo.

REM 성공 코드 반환
exit /b 0

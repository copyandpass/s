@echo off
REM ========================================
REM Quick Test Deployment Script
REM ========================================

setlocal enabledelayedexpansion

echo.
echo ========================================
echo Docker Deployment Quick Test
echo ========================================
echo.

REM 현재 디렉토리 확인
echo [INFO] Current Directory:
cd

REM Docker 상태 확인
echo.
echo [INFO] Docker Status:
docker ps

REM 이미지 확인
echo.
echo [INFO] Available Images:
docker images | findstr "soncoding-web" || echo No soncoding-web images found

REM 네트워크 확인
echo.
echo [INFO] Docker Networks:
docker network ls

REM 볼륨 확인
echo.
echo [INFO] Docker Volumes:
docker volume ls | findstr "soncoding" || echo No soncoding volumes found

echo.
echo ========================================
echo End of Quick Test
echo ========================================
echo.

@echo off
REM ========================================
REM Manual Deployment Rollback Script
REM ========================================

setlocal enabledelayedexpansion

set DEPLOY_DIR=C:\Users\kth08\Desktop\soncoding-web
set IMAGE_NAME=thkim0812/soncoding-web:latest

echo.
echo ========================================
echo Docker Rollback Script
echo ========================================
echo.

cd /d %DEPLOY_DIR%

echo [INFO] Stopping containers...
docker-compose down

echo.
echo [INFO] Available image history:
docker images thkim0812/soncoding-web

echo.
echo [INFO] All containers:
docker ps -a

echo.
echo ========================================
echo Manual rollback completed
echo You can manually select which image to run
echo ========================================
echo.

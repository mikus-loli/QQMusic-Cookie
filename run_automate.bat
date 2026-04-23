@echo off
chcp 65001 >nul
title QQ Music Cookie Manager - Automation

echo ============================================
echo QQ Music Cookie Manager - Automation Mode
echo ============================================
echo.

if not exist .env (
    echo [Error] .env file not found!
    echo Please copy .env.example to .env and configure it.
    pause
    exit /b 1
)

echo Starting automation...
echo.

python automate.py --interval 24

pause

@echo off
chcp 65001 >nul
title QQ Music Cookie Manager - Run Once

echo ============================================
echo QQ Music Cookie Manager - Run Once
echo ============================================
echo.

if not exist .env (
    echo [Error] .env file not found!
    echo Please copy .env.example to .env and configure it.
    pause
    exit /b 1
)

echo Running single cycle...
echo.

python automate.py --once

pause

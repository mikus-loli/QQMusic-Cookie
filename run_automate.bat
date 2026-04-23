@echo off
chcp 65001 >nul
title QQ Music Cookie Manager - Automation

echo ============================================
echo QQ Music Cookie Manager - Automation Mode
echo ============================================
echo.

REM 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo [Info] Found virtual environment, activating...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo [Info] Found virtual environment, activating...
    call .venv\Scripts\activate.bat
) else (
    echo [Info] No virtual environment found, using system Python
)

REM 检查.env文件
if not exist .env (
    echo [Error] .env file not found!
    echo Please copy .env.example to .env and configure it.
    pause
    exit /b 1
)

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [Error] Python not found!
    echo Please install Python or activate virtual environment.
    pause
    exit /b 1
)

echo.
echo Starting automation...
echo.

python automate.py --interval 24

pause

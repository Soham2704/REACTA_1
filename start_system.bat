@echo off
setlocal
echo Starting Multi-Agent Compliance System...

:: CRITICAL: Use the venv python explicitly.
set "VENV_PYTHON=%~dp0.venv\Scripts\python.exe"

if not exist "%VENV_PYTHON%" (
    echo [ERROR] Virtual environment not found at: %VENV_PYTHON%
    echo Please run 'install_fix.bat' first to set up the system.
    pause
    exit /b
)

echo 1. Launching Backend API (FastAPI)...
:: Start backend in a new window, keep it open if it crashes (/k)
start "Backend API - FASTAPI" cmd /k "%VENV_PYTHON% main.py"

echo Waiting for backend to initialize (5s)...
timeout /t 5 >nul

echo 2. Launching Frontend (React)...
cd frontend
if %errorlevel% neq 0 (
    echo [ERROR] Could not find 'frontend' directory!
    pause
    exit /b
)

:: Start frontend in a new window
echo Starting npm run dev...
start "Frontend - REACT" cmd /k "npm run dev"

echo.
echo ==================================================
echo System Started!
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8000
echo ==================================================
echo.
echo Press any key to close this launcher (Backend/Frontend windows will stay open)...
pause >nul

@echo off
echo Starting Multi-Agent Compliance System (React Edition)...

:: CRITICAL: Use the venv python explicitly.
set VENV_PYTHON=.venv\Scripts\python.exe

if not exist %VENV_PYTHON% (
    echo ERROR: Virtual environment not found! 
    echo Please run 'install_fix.bat' first to set up the system.
    pause
    exit /b
)

echo 1. Starting Backend API (FastAPI)...
:: We assume main.py is in the current directory
start "Backend API" cmd /k "%VENV_PYTHON% main.py"
timeout /t 5

echo 2. Starting Frontend (React)...
cd frontend
start "Frontend" cmd /k "npm run dev"

echo System started! Access Frontend at http://localhost:5173
echo Backend API at http://localhost:8000
pause

@echo off
echo ===================================================
echo     MULTI-AGENT SYSTEM - ONE-TIME SETUP FIX
echo ===================================================

echo [1/4] Setting up Backend Virtual Environment (.venv)...
if exist .venv (
    echo Existing venv found.
) else (
    echo Creating new venv...
    python -m venv .venv
)

echo [2/4] Installing Backend Dependencies into .venv...
:: FORCE install packages using the specific venv python
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install fastapi uvicorn python-multipart

echo [3/4] Cleaning Frontend Dependencies (to fix Tailwind)...
cd frontend
if exist node_modules rd /s /q node_modules
if exist package-lock.json del package-lock.json

echo [4/4] Installing Frontend Dependencies (Stable Versions)...
call npm install
call npm install -D tailwindcss@3.4.1 postcss@8.4.35 autoprefixer@10.4.17
call npx tailwindcss init -p

echo ===================================================
echo      SETUP COMPLETE! YOU CAN NOW START.
echo ===================================================
pause

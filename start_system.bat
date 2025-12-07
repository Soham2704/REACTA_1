@echo off
echo Starting Multi-Agent Compliance System...
echo Note: Ensure you have run 'pip install -r requirements.txt' if you haven't already.

echo 1. Starting Backend API (FastAPI)...
start "Backend API" cmd /k "py main.py"
timeout /t 5

echo 2. Starting Frontend (Streamlit)...
start "Frontend" cmd /k "py -m streamlit run app.py"

echo System started! Access Frontend at http://localhost:8501
pause

@echo off
echo ===================================================
echo     FINAL PATCH: CHROME & PYDANTIC
echo ===================================================
set VENV_PYTHON=.venv\Scripts\python.exe

if not exist %VENV_PYTHON% (
    echo Virtual environment missing. Running install_fix...
    call install_fix.bat
    exit /b
)

echo Force installing clean versions...
%VENV_PYTHON% -m pip install chromadb pydantic>=2.0
echo.
echo ===================================================
echo     PATCH COMPLETE. PLASE START SYSTEM.
echo ===================================================
pause

@echo off
echo ===================================================
echo     FIXING LANGCHAIN COMPATIBILITY (V0.2.x)
echo ===================================================

:: Ensure we use the venv python
set VENV_PYTHON=.venv\Scripts\python.exe

if not exist %VENV_PYTHON% (
    echo ERROR: Virtual environment not found! Run install_fix.bat first.
    pause
    exit /b
)

echo Uninstalling conflicting versions...
%VENV_PYTHON% -m pip uninstall -y langchain langchain-core langchain-community langchain-google-genai

echo Installing stable compatible versions...
:: Pinning to <0.3.0 to ensure pydantic_v1 shim exists
%VENV_PYTHON% -m pip install "langchain<0.3.0" "langchain-core<0.3.0" "langchain-community<0.3.0" "langchain-google-genai" "pydantic<2.0.0"

echo ===================================================
echo      DEPENDENCIES FIXED. RESTART THE SYSTEM.
echo ===================================================
pause

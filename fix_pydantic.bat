@echo off
echo ===================================================
echo     FIXING PYDANTIC / CHROMA CONFLICT
echo ===================================================

set VENV_PYTHON=.venv\Scripts\python.exe

echo [1/3] Uninstalling Pydantic V1...
%VENV_PYTHON% -m pip uninstall -y pydantic

echo [2/3] Installing Pydantic V2 (Required by ChromaDB)...
%VENV_PYTHON% -m pip install "pydantic>=2.0"

echo [3/3] Re-verifying LangChain (Must be v0.2.x to support Pydantic V2 Shim)...
%VENV_PYTHON% -m pip install "langchain<0.3.0" "langchain-core<0.3.0" "langchain-community<0.3.0"

echo ===================================================
echo      CONFLICT RESOLVED. RESTART SYSTEM.
echo ===================================================
pause

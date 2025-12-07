@echo off
echo --- Starting Comprehensive Dependency Repair ---
echo.
echo 1. Upgrading pip...
py -m pip install --upgrade pip

echo.
echo 2. Installing PyTorch (CPU version) explicitly...
py -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

echo.
echo 3. Installing remaining requirements...
py -m pip install -r requirements.txt

echo.
echo 4. Verifying critical packages...
py -c "import fastapi; print('FastAPI: OK')"
py -c "import chromadb; print('ChromaDB: OK')"
py -c "import torch; print('PyTorch: OK')"
py -c "import uvicorn; print('Uvicorn: OK')"
py -c "import numpy; print('Numpy: OK')"

echo.
echo --- Repair Complete. You can now run start_system.bat ---
pause

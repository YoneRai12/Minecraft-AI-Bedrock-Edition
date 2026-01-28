@echo off
echo ===================================================
echo [GPU Fix] Installing PyTorch Nightly for RTX 5090
echo ===================================================
echo This will uninstall current torch packages and install 
echo the latest nightly build (CUDA 12.4 compatible).

echo.
echo Step 1: Uninstalling existing PyTorch...
pip uninstall -y torch torchvision torchaudio ultralytics

echo.
echo Step 2: Installing Nightly PyTorch (CUDA 12.8, Blackwell Support)...
pip install --pre --no-cache-dir --force-reinstall torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

echo.
echo Step 3: Re-installing Ultralytics (without overwriting torch)...
pip install ultralytics --no-deps

echo.
echo ===================================================
echo Done! Please restart MainkurafutoAI.
echo If it still crashes, edit .env and set YOLO_DEVICE=cpu
echo ===================================================
pause

@echo off
setlocal

:: Get Current Directory
set "PROJECT_DIR=%~dp0"
:: Remove trailing backslash
set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"

echo Installing MainkurafutoAI Context Menu...
echo Project Directory: %PROJECT_DIR%

:: 1. Add Key to Directory Background (Right click on empty space in folder)
reg add "HKCU\Software\Classes\Directory\Background\shell\MainkurafutoAI" /ve /d "Run MainkurafutoAI" /f
reg add "HKCU\Software\Classes\Directory\Background\shell\MainkurafutoAI" /v "Icon" /d "cmd.exe" /f
reg add "HKCU\Software\Classes\Directory\Background\shell\MainkurafutoAI\command" /ve /d "cmd.exe /k cd /d \"%PROJECT_DIR%\" && python main.py" /f

:: 2. Add Key to Desktop Background (Desktop is also a directory background usually, but ensuring)
:: The above key covers Directory\Background which includes Desktop.

echo.
echo ========================================================
echo Done! 
echo Right-click on your Desktop or inside any folder to see
echo "Run MainkurafutoAI".
echo ========================================================
pause

@echo off
REM Office AI Add-in - One-Click Build Script for Windows
REM Run this after installing Python and dependencies

echo.
echo ========================================
echo Office AI Add-in - Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Building executable with PyInstaller...
pyinstaller office-ai-addin.spec
if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)

echo.
echo [3/4] Build complete!
echo.
echo SUCCESS: Your .exe is ready at:
echo   dist\OfficeAI\OfficeAI.exe
echo.

REM Check if user wants to create installer
set /p CREATE_INSTALLER="Create NSIS installer? (y/n): "
if /i "%CREATE_INSTALLER%"=="y" (
    echo.
    echo [4/4] Creating installer...
    
    REM Check if NSIS is installed
    "C:\Program Files (x86)\NSIS\makensis.exe" office-ai-addin.nsi
    if errorlevel 1 (
        echo.
        echo NOTE: NSIS not found at default location
        echo Download NSIS from: https://nsis.sourceforge.io/Download
        echo Then run: makensis office-ai-addin.nsi
        pause
        exit /b 0
    )
    
    echo.
    echo SUCCESS: Installer created: OfficeAI-Installer.exe
) else (
    echo.
    echo You can create installer later by running:
    echo   makensis office-ai-addin.nsi
    echo (Install NSIS first from https://nsis.sourceforge.io/)
)

echo.
echo Next steps:
echo   1. Test: run dist\OfficeAI\OfficeAI.exe
echo   2. Zip folder: dist\OfficeAI or use OfficeAI-Installer.exe
echo   3. Upload to your website
echo.
echo Documentation: See BUILD_EXE.md for detailed instructions
echo.
pause

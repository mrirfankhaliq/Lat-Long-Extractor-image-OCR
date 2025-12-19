@echo off
echo ========================================
echo Building Portable Executable
echo OCR Coordinates Extractor
echo ========================================
echo.

REM Check if PyInstaller is installed
py -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    py -m pip install pyinstaller
    echo.
)

echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist OCR_Coordinates_Extractor.spec del OCR_Coordinates_Extractor.spec

echo.
echo Building executable (this may take a few minutes)...
echo.

py -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name "OCR_Coordinates_Extractor" ^
    --clean ^
    --noconfirm ^
    --hidden-import=pytesseract ^
    --hidden-import=PIL ^
    --hidden-import=tkinter ^
    --hidden-import=PIL._tkinter_finder ^
    ocr_coordinates.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Build failed!
    echo ========================================
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Executable location: dist\OCR_Coordinates_Extractor.exe
echo.
echo The executable is portable and can be copied anywhere.
echo.
echo IMPORTANT: Tesseract OCR must be installed on the target system
echo or placed in the same folder as the executable.
echo.
echo You can now:
echo 1. Copy dist\OCR_Coordinates_Extractor.exe to any location
echo 2. Run it directly (double-click)
echo.
pause

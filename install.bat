@echo off
echo Installing Latitude & Longitude OCR Extractor...
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.7 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo.
echo Installing Python dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo Installation complete!
echo.
echo IMPORTANT: Make sure Tesseract OCR is installed:
echo Download from: https://github.com/UB-Mannheim/tesseract/wiki
echo.
echo After installing Tesseract, you can run the tool using:
echo   python ocr_coordinates.py
echo   OR
echo   run_ocr_tool.bat
echo.
pause



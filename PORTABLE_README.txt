========================================
OCR Coordinates Extractor - Portable Version
========================================

EXECUTABLE: OCR_Coordinates_Extractor.exe

This is a portable executable that can be run on any Windows computer
without requiring Python installation.

========================================
HOW TO USE:
========================================

1. Copy OCR_Coordinates_Extractor.exe to any folder on your computer
2. Double-click the .exe file to run it
3. The GUI will open automatically

========================================
IMPORTANT - TESSERACT OCR REQUIREMENT:
========================================

The executable requires Tesseract OCR to be installed on the system.

Option 1: Install Tesseract OCR (Recommended)
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install it on your system
- The app will automatically find it

Option 2: Portable Tesseract (Advanced)
- Place Tesseract-OCR folder in the same directory as the .exe
- The app will try to find it automatically

========================================
FEATURES:
========================================

✓ Extract latitude and longitude from images using OCR
✓ Single image processing with preview
✓ Batch processing for multiple images
✓ Supports multiple coordinate formats
✓ Saves results in CSV format: serial no, Img name, lat, long

========================================
SUPPORTED IMAGE FORMATS:
========================================

- PNG
- JPG/JPEG
- BMP
- TIFF
- GIF

========================================
OUTPUT FORMAT:
========================================

The tool saves coordinates in a text file with format:
serial no, Img name, lat, long

Example:
1, image1, 30.172773, 73.665911
2, image2, 30.173000, 73.666000

========================================
TROUBLESHOOTING:
========================================

If you get "Tesseract OCR Not Found" error:
1. Install Tesseract OCR from the link above
2. Make sure it's added to your system PATH
3. Restart the application

If coordinates are not detected:
- Check the OCR text output in the results area
- Make sure the image is clear and coordinates are visible
- Try different image formats or improve image quality

========================================
For support or issues, check the main README.md file
========================================


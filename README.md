# 📍 Lat Long Extractor by Irfan Khaliq

A powerful and user-friendly desktop application that extracts latitude and longitude coordinates from images using OCR (Optical Character Recognition) technology. Perfect for processing GPS coordinates from photos, screenshots, or scanned documents.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

## ✨ Features

### 🎯 Core Functionality
- **OCR-Based Coordinate Extraction**: Automatically extracts latitude and longitude from images using advanced OCR technology
- **Multiple Format Support**: Recognizes various coordinate formats including:
  - Decimal degrees (e.g., `30.172773, 73.665911`)
  - Degrees, Minutes, Seconds (DMS)
  - Degrees and Decimal Minutes (DDM)
  - Labeled coordinates (e.g., `Lat 30.172773° Long 73.665911°`)

### 🖼️ Single Image Processing
- **Image Preview**: View selected image before processing
- **Real-time Processing**: Fast OCR extraction with progress feedback
- **Detailed Results**: View extracted coordinates with format information

### 📦 Batch Processing
- **Multiple Image Processing**: Process hundreds of images at once
- **Pause/Resume**: Control processing with pause and resume functionality
- **Incremental Processing**: Add more images without losing previous results
- **Progress Tracking**: Real-time progress bar and status updates
- **Image Verification**: Double-click any row to view the original image

### 🔧 Advanced Features
- **Duplicate Detection**: Find and remove duplicate entries based on complete row data
- **Smart Image Preprocessing**: Automatic image enhancement for better OCR accuracy
- **Multiple OCR Attempts**: Tries different OCR configurations for maximum accuracy
- **Export to CSV**: Save results in standard CSV format (`serial no, Img name, lat, long`)

### 💻 User Experience
- **Modern GUI**: Clean, intuitive interface built with Tkinter
- **Non-blocking Processing**: UI remains responsive during OCR operations
- **Error Handling**: Comprehensive error messages and debugging information
- **Portable Executable**: Standalone .exe file available (no Python installation required)

## 📋 Requirements

### Software Requirements
- **Python 3.7 or higher** (for running from source)
- **Tesseract OCR** - Must be installed separately
  - Download: [Tesseract OCR for Windows](https://github.com/UB-Mannheim/tesseract/wiki)
  - Or use portable version in the same folder as executable

### Python Dependencies
```
pytesseract>=0.3.10
Pillow>=10.0.0
```

## 🚀 Installation

### Option 1: Portable Executable (Recommended)
1. Download `OCR_Coordinates_Extractor.exe` from the releases
2. Install Tesseract OCR on your system
3. Run the executable - no Python installation needed!

### Option 2: From Source
1. Clone the repository:
```bash
git clone https://github.com/yourusername/lat-long-extractor.git
cd lat-long-extractor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Tesseract OCR (see Requirements section)

4. Run the application:
```bash
python ocr_coordinates.py
```

## 📖 Usage

### Single Image Processing
1. Click **"Select Image"** to choose an image file
2. Preview the image in the left panel
3. Click **"Extract Coordinates"** to process
4. Review extracted coordinates in the results area
5. Click **"Save to Text File"** to export results

### Batch Processing
1. Switch to **"Batch Processing"** tab
2. Click **"Select Multiple Images"** to choose images
3. Click **"Process All Images"** to start batch processing
4. Use **"Pause"** button to pause/resume processing
5. Double-click any row in **"View Image"** column to verify the image
6. Click **"Remove Duplicates"** to clean up duplicate entries
7. Click **"Save All Results"** to export all coordinates

### Adding More Images
- Simply select more images and process again
- New results will be appended to existing ones
- Serial numbers continue sequentially

## 📤 Output Format

The application saves coordinates in a simple CSV format:

```
serial no, Img name, lat, long
1, image1, 30.172773, 73.665911
2, image2, 30.173000, 73.666000
3, image3, 30.174500, 73.667500
```

## 🖼️ Supported Image Formats

- PNG
- JPG/JPEG
- BMP
- TIFF
- GIF

## 🔍 How It Works

1. **Image Preprocessing**: Enhances image quality (contrast, sharpness, noise reduction)
2. **OCR Processing**: Uses Tesseract OCR with multiple configuration modes
3. **Pattern Matching**: Applies regex patterns to extract coordinates from OCR text
4. **Validation**: Validates coordinates (latitude: -90 to 90, longitude: -180 to 180)
5. **Deduplication**: Removes duplicate coordinates automatically

## 🛠️ Building Executable

To create a portable executable:

```bash
python build_exe.bat
```

Or manually:
```bash
pyinstaller --onefile --windowed --name "OCR_Coordinates_Extractor" ocr_coordinates.py
```

## 🐛 Troubleshooting

### "Tesseract OCR Not Found" Error
- **Solution**: Install Tesseract OCR and add it to your system PATH
- Or place Tesseract-OCR folder in the same directory as the executable

### No Coordinates Found
- **Check Image Quality**: Ensure coordinates are clearly visible
- **Review OCR Text**: The app shows extracted text for debugging
- **Try Different Formats**: Some formats work better than others
- **Improve Image**: Increase resolution or contrast if needed

### App Not Responding
- The app uses threading to prevent freezing
- If issues persist, try processing fewer images at once
- Check system resources (CPU/Memory)

## 📝 Notes

- OCR accuracy depends on image quality - clearer images produce better results
- Coordinates are automatically validated for correct ranges
- Duplicate coordinates are removed based on complete row matching
- The app supports incremental processing - add images anytime

## 👤 Author

**Irfan Khaliq**

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

## ⭐ Acknowledgments

- Built with [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- Uses [Pillow](https://python-pillow.org/) for image processing
- GUI built with [Tkinter](https://docs.python.org/3/library/tkinter.html)

## 📧 Support

For support, please open an issue on the GitHub repository.

---

**Made with ❤️ by Irfan Khaliq**

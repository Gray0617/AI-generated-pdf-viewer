# PDF Reader

A GUI-based PDF reader written in Python that displays PDF files visually with page navigation, drag-and-drop support, and zoom functionality.

## Installation

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

   Note: pdf2image requires Poppler. On Windows, it should install automatically. If not, you may need to install Poppler separately.

## Usage

Run the script:

```
python pdf_reader.py
```

A GUI window will open.

- **Open PDF**: Use File > Open to select a PDF file, or drag and drop a PDF file into the window.
- **Navigate Pages**: Use the Previous/Next buttons.
- **Zoom**: Use mouse scroll wheel to zoom in/out (middle button scroll).
- **Resize**: Resize the window to adjust the view.

## Features

- Visual PDF rendering with aspect ratio preservation
- Drag and drop file loading
- Mouse wheel zoom (0.1x to 5x) towards cursor position
- Mouse left-click drag to pan (only when image exceeds display area, separately for width/height)
- Resizable window with dynamic rendering
- Page navigation

## Requirements

- Python 3.6+
- PyPDF2
- pdf2image
- Pillow
- tkinterdnd2# AI-generated-pdf-viewer
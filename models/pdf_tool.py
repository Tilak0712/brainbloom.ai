from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import pytesseract
import os
from tempfile import TemporaryDirectory

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

        if text.strip():
            return {
                "mode": "digital",
                "text": text.strip()
            }

        with TemporaryDirectory() as tempdir:
            images = convert_from_path(file_path, output_folder=tempdir, fmt='png')
            ocr_text = ""
            for img in images:
                ocr_text += pytesseract.image_to_string(img)

        if ocr_text.strip():
            return {
                "mode": "ocr",
                "text": ocr_text.strip()
            }

        return {
            "mode": "none",
            "text": "❌ Could not extract any text, even with OCR."
        }

    except Exception as e:
        return {
            "mode": "error",
            "text": f"❌ Error reading PDF: {str(e)}"
        }

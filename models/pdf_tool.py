from PyPDF2 import PdfReader

def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content
        return {"mode": "text", "text": text.strip()}
    except Exception as e:
        return {"mode": "error", "text": f"❌ Error reading PDF: {e}"}

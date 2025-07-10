import fitz  # PyMuPDF

def handle_uploaded_file(file, question):
    try:
        if file.type == "application/pdf":
            # Read the bytes once
            file_bytes = file.read()
            text = extract_text_from_pdf(file_bytes)
        else:
            text = file.read().decode("utf-8")

        if question.lower() in text.lower():
            return f" Found relevant info:\n\n{text[:1000]}..."
        else:
            return " Sorry, I couldn't find an answer in the file."
    except Exception as e:
        return f" Error processing file: {str(e)}"

def extract_text_from_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

import PyPDF2

def extract_text_from_pdf(f):
    reader = PyPDF2.PdfReader(f)
    text = ""
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text += t + "\n"
    return text


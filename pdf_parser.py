import pdfplumber

def extract_text_from_pdf(file):
    try:
        with pdfplumber.open(file) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
    except Exception as exc:
        raise ValueError("Could not read PDF") from exc
    return "\n".join(pages).strip()

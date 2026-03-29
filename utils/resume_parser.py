import io
from pdf2image import convert_from_bytes
import pytesseract

def extract_resume_text(pdf_bytes):
    text = ""

    try:
        # Convert PDF → images
        images = convert_from_bytes(pdf_bytes)

        for img in images:
            page_text = pytesseract.image_to_string(img)
            text += page_text + "\n"

    except Exception as e:
        print("[OCR ERROR]", e)

    return text.strip()
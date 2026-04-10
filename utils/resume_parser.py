"""
Resume parser module — extracts text from PDF files
"""

from pypdf import PdfReader
from io import BytesIO


def extract_resume_text(pdf_bytes):
    """
    Extract text from PDF bytes.
    
    Args:
        pdf_bytes: Raw PDF file bytes
        
    Returns:
        str: Extracted text from PDF, or empty string if extraction fails
    """
    try:
        pdf_file = BytesIO(pdf_bytes)
        reader = PdfReader(pdf_file)
        
        text = ""
        for page_num, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            except Exception as e:
                print(f"[PDF] Warning: Could not extract text from page {page_num + 1}: {e}")
                continue
        
        if text.strip():
            print(f"[RESUME_PARSER] Successfully extracted {len(text)} characters from PDF")
            return text
        else:
            print("[RESUME_PARSER] PDF is empty or contains only images (scanned document)")
            return ""
            
    except Exception as e:
        print(f"[RESUME_PARSER ERROR] Failed to extract PDF: {e}")
        return ""

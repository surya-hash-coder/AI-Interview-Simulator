"""
utils/resume_parser.py
Extracts text from PDF resume files.
"""

import io
import re


def extract_resume_text(pdf_bytes):
    """Extract all text from a PDF file given as bytes."""
    text = ""

    # Try pypdf first
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        parts = []
        for page in reader.pages:
            t = page.extract_text()
            if t and t.strip():
                parts.append(t.strip())
        text = "\n".join(parts)
        print("[PARSER] pypdf extracted " + str(len(text)) + " chars")
        if len(text.strip()) > 30:
            return clean(text)
    except ImportError:
        pass
    except Exception as e:
        print("[PARSER] pypdf error: " + str(e))

    # Try PyPDF2
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        parts = []
        for page in reader.pages:
            t = page.extract_text()
            if t and t.strip():
                parts.append(t.strip())
        text = "\n".join(parts)
        print("[PARSER] PyPDF2 extracted " + str(len(text)) + " chars")
        if len(text.strip()) > 30:
            return clean(text)
    except ImportError:
        pass
    except Exception as e:
        print("[PARSER] PyPDF2 error: " + str(e))

    print("[PARSER] All methods failed or returned empty text")
    return text.strip()


def clean(text):
    """Clean extracted PDF text."""
    if not text:
        return ""
    text = re.sub(r'[^\x09\x0a\x0d\x20-\x7e\u00a0-\ufffd]', ' ', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    lines = [l.strip() for l in text.split('\n')]
    lines = [l for l in lines if len(l) > 1 or l == '']
    return '\n'.join(lines).strip()

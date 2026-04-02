"""
utils/resume_parser.py
Extracts text from PDF resumes.
Tries multiple libraries — prints exactly what it finds.
"""

import io
import re


def extract_resume_text(pdf_bytes):
    """
    Try every available method to extract text from the PDF.
    Returns the best result found.
    """
    print(f"\n[PARSER] PDF size: {len(pdf_bytes)} bytes")
    print("[PARSER] Trying all extraction methods...")

    results = []

    # ── Method 1: pypdf ──────────────────────────────────────
    try:
        import pypdf
        print(f"[PARSER] pypdf version: {pypdf.__version__}")
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        print(f"[PARSER] pypdf: {len(reader.pages)} pages found")
        parts = []
        for i, page in enumerate(reader.pages):
            t = page.extract_text()
            if t:
                parts.append(t)
                print(f"[PARSER] pypdf page {i+1}: {len(t)} chars")
            else:
                print(f"[PARSER] pypdf page {i+1}: empty")
        text = "\n".join(parts).strip()
        print(f"[PARSER] pypdf total: {len(text)} chars")
        if len(text) > 50:
            results.append(("pypdf", text))
    except ImportError:
        print("[PARSER] pypdf not installed")
    except Exception as e:
        print(f"[PARSER] pypdf error: {e}")

    # ── Method 2: PyPDF2 ─────────────────────────────────────
    try:
        import PyPDF2
        print(f"[PARSER] PyPDF2 version: {PyPDF2.__version__}")
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        print(f"[PARSER] PyPDF2: {len(reader.pages)} pages")
        parts = []
        for i, page in enumerate(reader.pages):
            t = page.extract_text()
            if t:
                parts.append(t)
                print(f"[PARSER] PyPDF2 page {i+1}: {len(t)} chars")
        text = "\n".join(parts).strip()
        print(f"[PARSER] PyPDF2 total: {len(text)} chars")
        if len(text) > 50:
            results.append(("PyPDF2", text))
    except ImportError:
        print("[PARSER] PyPDF2 not installed")
    except Exception as e:
        print(f"[PARSER] PyPDF2 error: {e}")

    # ── Method 3: pdfminer ───────────────────────────────────
    try:
        from pdfminer.high_level import extract_text as pdfminer_extract
        text = pdfminer_extract(io.BytesIO(pdf_bytes))
        text = (text or "").strip()
        print(f"[PARSER] pdfminer total: {len(text)} chars")
        if len(text) > 50:
            results.append(("pdfminer", text))
    except ImportError:
        print("[PARSER] pdfminer not installed")
    except Exception as e:
        print(f"[PARSER] pdfminer error: {e}")

    # ── Pick the best result ──────────────────────────────────
    if not results:
        print("[PARSER] ERROR: No method extracted any text!")
        print("[PARSER] This usually means:")
        print("  1. The PDF is a scanned image (not text-based)")
        print("  2. The PDF is encrypted/password protected")
        print("  3. pypdf/PyPDF2 not installed in venv")
        print("[PARSER] Fix: run: .\\venv\\Scripts\\python.exe -m pip install pypdf PyPDF2")
        return ""

    # Use the result with the most text
    results.sort(key=lambda x: len(x[1]), reverse=True)
    best_method, best_text = results[0]
    print(f"[PARSER] Best result: {best_method} ({len(best_text)} chars)")
    print(f"[PARSER] Text preview:\n{best_text[:300]}")

    return clean_text(best_text)


def clean_text(text):
    """Clean up extracted PDF text."""
    if not text:
        return ""
    # Remove non-printable characters
    text = re.sub(r'[^\x09\x0a\x0d\x20-\x7e\u00a0-\ufffd]', ' ', text)
    # Collapse multiple spaces
    text = re.sub(r'[ \t]{2,}', ' ', text)
    # Collapse multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Strip each line
    lines = [l.strip() for l in text.split('\n')]
    # Remove lines that are just 1 char or empty (but keep blank lines for structure)
    lines = [l for l in lines if len(l) != 1]
    result = '\n'.join(lines).strip()
    return result

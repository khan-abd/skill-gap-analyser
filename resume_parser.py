"""
resume_parser.py
Thin wrapper: extracts raw text from a PDF for the LLM to parse holistically.
All downstream extraction (CGPA, skills, leadership, etc.) is done by the LLM agent.
"""

import io
import pypdf


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Read all pages of a PDF and return the raw text as a single string."""
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)

"""Extract raw text from PDF / DOCX resumes. Claude does the structured parsing."""

from __future__ import annotations

import io
import logging

import fitz  # pymupdf
from docx import Document

log = logging.getLogger(__name__)


def extract_text_from_pdf(data: bytes) -> str:
    doc = fitz.open(stream=data, filetype="pdf")
    try:
        chunks = [page.get_text("text") for page in doc]
    finally:
        doc.close()
    return "\n".join(chunks).strip()


def extract_text_from_docx(data: bytes) -> str:
    doc = Document(io.BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs).strip()


def extract_text(filename: str, data: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return extract_text_from_pdf(data)
    if lower.endswith((".docx", ".doc")):
        return extract_text_from_docx(data)
    raise ValueError(f"Unsupported file type: {filename}")

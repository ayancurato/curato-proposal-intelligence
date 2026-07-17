"""
Curato Proposal Intelligence — PDF Service

Extracts text from PDF files using PyMuPDF (primary) with pdfplumber fallback.
Single responsibility: converting PDF bytes into clean text.
"""

from pathlib import Path

from app.utils.text_utils import clean_text


class PDFService:
    """Extracts and cleans text from PDF files."""

    @staticmethod
    async def extract_text(file_path: str) -> tuple[str, int]:
        """
        Extract text from a PDF file.

        Uses PyMuPDF (fitz) as primary extractor.
        Falls back to pdfplumber if PyMuPDF fails.

        Returns:
            tuple: (cleaned_text, page_count)
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        # ── Primary: PyMuPDF ──────────────────────────────────────
        try:
            text, page_count = PDFService._extract_with_pymupdf(str(path))
            if text.strip():
                return clean_text(text), page_count
        except Exception as e:
            print(f"⚠ PyMuPDF extraction failed for {path.name}: {e}")

        # ── Fallback: pdfplumber ──────────────────────────────────
        try:
            text, page_count = PDFService._extract_with_pdfplumber(str(path))
            if text.strip():
                return clean_text(text), page_count
        except Exception as e:
            print(f"⚠ pdfplumber extraction failed for {path.name}: {e}")

        raise ValueError(f"Failed to extract text from {path.name}. The PDF may be image-based or corrupted.")

    @staticmethod
    def _extract_with_pymupdf(file_path: str) -> tuple[str, int]:
        """Extract text using PyMuPDF (fitz)."""
        import fitz  # PyMuPDF

        doc = fitz.open(file_path)
        page_count = len(doc)
        text_parts = []

        for page_num in range(page_count):
            page = doc[page_num]

            # Extract text preserving layout structure
            text = page.get_text("text")

            if text.strip():
                text_parts.append(f"--- Page {page_num + 1} ---\n{text}")

        doc.close()
        return "\n\n".join(text_parts), page_count

    @staticmethod
    def _extract_with_pdfplumber(file_path: str) -> tuple[str, int]:
        """Extract text using pdfplumber as fallback."""
        import pdfplumber

        text_parts = []

        with pdfplumber.open(file_path) as pdf:
            page_count = len(pdf.pages)

            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text and text.strip():
                    text_parts.append(f"--- Page {i + 1} ---\n{text}")

        return "\n\n".join(text_parts), page_count

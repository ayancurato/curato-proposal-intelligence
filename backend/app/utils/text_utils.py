"""
Curato Proposal Intelligence — Text Utilities

Helpers for cleaning and normalizing extracted PDF text.
"""

import re


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text by normalizing whitespace and removing artifacts.
    Preserves paragraph structure and meaningful line breaks.
    """
    if not text:
        return ""

    # Remove null bytes and control characters (except newlines and tabs)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Normalize Unicode whitespace to regular spaces
    text = re.sub(r"[\u00a0\u2000-\u200b\u2028\u2029\u202f\u205f\u3000]", " ", text)

    # Remove excessive spaces within lines (keep single spaces)
    text = re.sub(r"[ \t]+", " ", text)

    # Remove trailing spaces on each line
    text = re.sub(r" +\n", "\n", text)

    # Collapse 3+ consecutive newlines into 2 (preserve paragraph breaks)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


def extract_headings(text: str) -> list[str]:
    """
    Attempt to identify section headings from the text.
    Looks for common heading patterns in proposals.
    """
    headings = []
    lines = text.split("\n")

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # All caps lines that are short enough to be headings
        if stripped.isupper() and 3 <= len(stripped) <= 80:
            headings.append(stripped)
            continue

        # Lines ending with colon that are short
        if stripped.endswith(":") and len(stripped) <= 60:
            headings.append(stripped.rstrip(":"))
            continue

        # Numbered sections like "1. Introduction" or "1.1 Overview"
        if re.match(r"^\d+\.?\d*\.?\s+[A-Z]", stripped) and len(stripped) <= 80:
            headings.append(stripped)
            continue

    return headings


def truncate_text(text: str, max_chars: int = 100_000) -> str:
    """
    Truncate text to a maximum character count.
    Used to ensure we don't exceed AI model context limits.
    Truncates at the nearest paragraph break.
    """
    if len(text) <= max_chars:
        return text

    # Try to truncate at a paragraph boundary
    truncated = text[:max_chars]
    last_para_break = truncated.rfind("\n\n")

    if last_para_break > max_chars * 0.8:  # Only use para break if not too far back
        truncated = truncated[:last_para_break]

    return truncated + "\n\n[... content truncated due to length ...]"


def estimate_word_count(text: str) -> int:
    """Estimate the word count of a text."""
    return len(text.split())

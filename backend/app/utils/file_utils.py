"""
Curato Proposal Intelligence — File Utilities

Helpers for safe filename generation, file validation, and directory management.
"""

import uuid
from pathlib import Path

ALLOWED_EXTENSIONS = {".pdf"}
ALLOWED_MIME_TYPES = {"application/pdf"}


def generate_safe_filename(original_name: str) -> str:
    """
    Generate a UUID-based filename while preserving the extension.
    Prevents path traversal and filename collisions.
    """
    ext = Path(original_name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        ext = ".pdf"
    return f"{uuid.uuid4().hex}{ext}"


def validate_file_extension(filename: str) -> bool:
    """Check if a file has an allowed extension."""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def validate_file_size(file_size: int, max_size_bytes: int) -> bool:
    """Check if a file is within the allowed size limit."""
    return 0 < file_size <= max_size_bytes


def ensure_directory(path: Path) -> Path:
    """Create a directory if it doesn't exist and return the path."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_size_display(size_bytes: int) -> str:
    """Convert bytes to a human-readable size string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

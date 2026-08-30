"""Input validation utilities."""
import os
from typing import Tuple
from werkzeug.datastructures import FileStorage

from config.settings import (
    ALLOWED_EXTENSIONS,
    MAX_UPLOAD_SIZE_BYTES,
    MAX_UPLOAD_SIZE_MB,
)


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def validate_upload(file: FileStorage) -> Tuple[bool, str]:
    """Validate uploaded file."""
    if not file or not file.filename:
        return False, "No file provided."

    if not allowed_file(file.filename):
        return False, f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"

    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)

    if size == 0:
        return False, "The uploaded file is empty."

    if size > MAX_UPLOAD_SIZE_BYTES:
        return False, f"File too large. Maximum size is {MAX_UPLOAD_SIZE_MB} MB."

    return True, ""


def validate_text(text: str, field_name: str = "Text", min_length: int = 10) -> Tuple[bool, str]:
    """Validate text input."""
    if not text or not text.strip():
        return False, f"{field_name} is required."
    if len(text.strip()) < min_length:
        return False, f"{field_name} must be at least {min_length} characters."
    return True, ""

from pathlib import Path
from typing import Optional

from langchain_core.tools import tool


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".pptx",
    ".txt",
    ".csv",
    ".xlsx",
    ".json",
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".html",
    ".css",
    ".md",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
}

MAX_FILE_SIZE_MB = 25
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


def validate_file(file_path: str) -> dict:
    path = Path(file_path).resolve()

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not path.is_file():
        raise ValueError(f"Provided path is not a file: {path}")

    extension = path.suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension or 'no extension'}"
        )

    file_size = path.stat().st_size

    if file_size > MAX_FILE_SIZE_BYTES:
        raise ValueError(
            f"File size exceeds the maximum limit of "
            f"{MAX_FILE_SIZE_MB} MB."
        )

    return {
        "file_name": path.name,
        "file_path": str(path),
        "extension": extension,
        "size_bytes": file_size,
        "size_mb": round(file_size / (1024 * 1024), 2),
        "status": "valid",
    }


@tool
def file_tool(file_path: str) -> str:
    """
    Validate an uploaded file and return its metadata.
    """

    if not file_path or not file_path.strip():
        return "File validation failed: file path cannot be empty."

    try:
        metadata = validate_file(file_path)

        return (
            "File validated successfully.\n"
            f"Name: {metadata['file_name']}\n"
            f"Path: {metadata['file_path']}\n"
            f"Type: {metadata['extension']}\n"
            f"Size: {metadata['size_mb']} MB\n"
            f"Status: {metadata['status']}"
        )

    except FileNotFoundError as exc:
        return f"File validation failed: {str(exc)}"

    except ValueError as exc:
        return f"File validation failed: {str(exc)}"

    except Exception as exc:
        return f"Unexpected file validation error: {str(exc)}"
    
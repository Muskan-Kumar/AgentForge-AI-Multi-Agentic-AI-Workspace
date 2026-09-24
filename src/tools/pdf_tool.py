from pathlib import Path

import fitz
from langchain_core.tools import tool


@tool
def pdf_tool(file_path: str) -> str:
    """
    Extract structured text and metadata from a PDF document.

    Args:
        file_path: Path to the PDF file.

    Returns:
        Extracted document content with page-level information and metadata.
    """

    try:
        path = Path(file_path).resolve()

        if not path.exists():
            return f"PDF file not found: {file_path}"

        if not path.is_file():
            return f"Provided path is not a file: {file_path}"

        if path.suffix.lower() != ".pdf":
            return "Invalid file type. Only PDF documents are supported."

        document = fitz.open(path)

        if document.is_encrypted:
            document.close()
            return "The PDF is encrypted and cannot be processed."

        if len(document) == 0:
            document.close()
            return "The PDF contains no pages."

        metadata = document.metadata

        output = [
            f"Document: {path.name}",
            f"Pages: {len(document)}",
            f"Title: {metadata.get('title') or 'Unknown'}",
            f"Author: {metadata.get('author') or 'Unknown'}",
            "",
            "DOCUMENT CONTENT",
            "=" * 60,
        ]

        extracted_pages = 0

        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            if not text:
                continue

            extracted_pages += 1

            output.extend(
                [
                    "",
                    f"--- Page {page_number} ---",
                    text,
                ]
            )

        document.close()

        if extracted_pages == 0:
            return (
                "The PDF was opened successfully, but no extractable text "
                "was found. It may be a scanned/image-only document."
            )

        return "\n".join(output)

    except fitz.FileDataError:
        return "The PDF appears to be corrupted or invalid."

    except PermissionError:
        return "Permission denied while accessing the PDF file."

    except Exception as exc:
        return f"Unexpected PDF processing error: {str(exc)}"

    
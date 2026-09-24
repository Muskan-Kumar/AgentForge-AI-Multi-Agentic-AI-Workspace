from pathlib import Path

from src.rag.document_loader import load_pdf
from src.rag.chunker import chunk_documents
from src.rag.vector_store import index_documents


class PDFIndexer:
    """
    Handles the complete PDF indexing pipeline.

    Pipeline:
        PDF
        ↓
        Document Loader
        ↓
        Chunker
        ↓
        Embeddings
        ↓
        Pinecone
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def validate_file(self, file_path: str) -> Path:
        path = Path(file_path).resolve()

        if not path.exists():
            raise FileNotFoundError(
                f"PDF file not found: {file_path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Provided path is not a file: {file_path}"
            )

        if path.suffix.lower() != ".pdf":
            raise ValueError(
                "Invalid file type. Only PDF documents are supported."
            )

        return path

    def index(self, file_path: str) -> dict:
        """
        Load, chunk and index a PDF into Pinecone.

        Returns:
            Dictionary containing indexing information.
        """

        path = self.validate_file(file_path)

        documents = load_pdf(str(path))

        chunks = chunk_documents(
            documents=documents,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

        vector_ids = index_documents(chunks)

        return {
            "file_name": path.name,
            "file_path": str(path),
            "pages": len(documents),
            "chunks": len(chunks),
            "vectors": len(vector_ids),
            "status": "indexed",
        }


def index_pdf(
    file_path: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> dict:
    """
    Index a PDF document into Pinecone.
    """

    indexer = PDFIndexer(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    return indexer.index(file_path)

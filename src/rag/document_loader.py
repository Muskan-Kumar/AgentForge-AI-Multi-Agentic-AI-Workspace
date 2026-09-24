from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import PyMuPDFLoader


class PDFDocumentLoader:
    """
    Professional PDF document loader for the AgentForge RAG pipeline.

    Responsibilities:
    - Validate PDF files
    - Load PDF pages
    - Preserve page-level metadata
    - Return LangChain Document objects
    """

    def __init__(self, file_path: str):
        self.file_path = Path(file_path).resolve()

    def validate(self)->None:
        if not self.file_path.exists():
            raise FileNotFoundError(
                f"PDF file not found: {self.file_path}"
            )

        if not self.file_path.is_file():
            raise ValueError(
                f"Provided path is not a file: {self.file_path}"
            )

        if self.file_path.suffix.lower() != ".pdf":
            raise ValueError(
                f"Invalid file type. Only PDF document are supported."
            )


    def load(self)-> list[Document]:
        self.validate()

        loader = PyMuPDFLoader(
            str(self.file_path)
        )

        documents = loader.load()

        if not documents:
            raise ValueError(
                f"The PDF contains no extractable content."
            )

        for document in documents:
            document.metadata['source'] = self.file_path.name
            document.metadata['file_path'] = str(self.file_path)

        return documents

def load_pdf(file_path: str)->list[Document]:
    """
    Load a PDF and return page-level LangChain documents.
    """

    loader = PyMuPDFLoader(file_path)
    return loader.load()

    
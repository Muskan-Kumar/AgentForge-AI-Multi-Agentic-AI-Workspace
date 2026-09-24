from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentChunker:
    """
    Splits documents into meaningful overlapping chunks
    for embedding and vector-store indexing.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        if chunk_size <= 0:
            raise ValueError("chunk size must be greater than 0")

        if chunk_overlap < 0:
            raise ValueError("chunk overlap cannot be negative")

        if chunk_overlap >= chunk_size:
            raise ValueError("chunk overlap must be smaller than chunk size")


        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n","\n",". ","? ","! "," ","",],
            length_function=len,
        )


    def split_document(self, documents: list[Document])-> list[Document]:
        if not documents:
            raise ValueError("No  documents were provided for chunking.")

        chunks = self.splitter.split_documents(documents)

        if not chunks:
            raise ValueError(
                "Document chunking produced no chunks."
            )

        for index, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = index

        return chunks


def chunk_documents(documents: list[Document],chunk_size: int = 1000,chunk_overlap: int = 200,) -> list[Document]:

    chunker = DocumentChunker(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    return chunker.split_document(documents)

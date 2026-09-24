from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore

from src.core.config import settings
from src.rag.embedding import get_embeddings


class VectorStoreService:
    """
    Manages the Pinecone vector store used by the AgentForge RAG pipeline.
    """

    def __init__(self):
        self.embeddings = get_embeddings()

        self.vector_store = PineconeVectorStore(
            index_name=settings.PINECONE_INDEX_NAME,
            embedding=self.embeddings,
            pinecone_api_key=settings.PINECONE_API_KEY
        )

    def add_documents(self, documents: list[Document])->list[str]:
        """
        Add document chunks to Pinecone.
        """
        if not documents:
            raise ValueError("No documents were provided for vector indexing.")

        return self.vector_store.add_documents(documents)

    def get_vector_store(self)->PineconeVectorStore:
        """
        Return the configured Pinecone vector store.
        """
        return self.vector_store

def get_vector_store()->PineconeVectorStore:
    """
    Return the configured Pinecone vector store.
    """

    return VectorStoreService().get_vector_store()

def index_documents(documents:list[Document],)->list[str]:
    """
    Generate embeddings and index document chunks in Pinecone.
    """
    service = VectorStoreService()
    return service.add_documents(documents)

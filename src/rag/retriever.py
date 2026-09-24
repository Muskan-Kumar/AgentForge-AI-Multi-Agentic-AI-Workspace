from langchain_core.documents import Document
from src.rag.vector_store import get_vector_store


class PDFRetriever:
    """
    Retrieves relevant document chunks from the AgentForge
    Pinecone vector store.
    """
    def __init__(self, top_k:int = 5):
        if top_k <= 0:
            raise ValueError("top k must be greater than 0.")

        self.top_k = top_k
        self.vector_store = get_vector_store()


    def retrieve(self, query: str)-> list[Document]:
        """
        Retrieve the most relevant document chunks
        for the given query.
        """

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        documents = self.vector_store.similarity_search(
            query=query.strip(),
            k=self.top_k
        )

        return documents


def retrieve_documents(query: str, top_k: int = 5,)->list[Document]:
    """
    Retrieve relevant documents from Pinecone.
    """

    retriever = PDFRetriever(top_k=top_k)

    return retriever.retrieve(query)


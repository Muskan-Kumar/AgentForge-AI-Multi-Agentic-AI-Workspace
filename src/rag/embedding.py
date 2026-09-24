from langchain_huggingface import HuggingFaceEmbeddings
from src.core.config import settings


class EmbeddingService:
    """
    Creates and manages the embedding model used by the
    AgentForge RAG pipeline.
    """

    def __init__(self):
        self.model = HuggingFaceEmbeddings(
            model_name = settings.EMBEDDING_MODEL,
            model_kwargs = {"device": "cpu"},
            encode_kwargs = {"normalize_embeddings":True},
        )

    def get_model(self)->HuggingFaceEmbeddings:
        return self.model


def get_embeddings()->HuggingFaceEmbeddings:
    """
    Return the configured embedding model.
    """

    return EmbeddingService().get_model()

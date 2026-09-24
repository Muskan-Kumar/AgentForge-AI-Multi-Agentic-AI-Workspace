from langchain_core.tools import tool
from src.rag.retriever import retrieve_documents

@tool
def rag_tool(query: str, top_k: int = 5)-> str:
    """
    Retrieve relevant information from indexed PDF documents.

    Args:
        query: User's question about the uploaded documents.
        top_k: Number of relevant document chunks to retrieve.

    Returns:
        Relevant document context with source and page metadata.
    """

    try:
        documents = retrieve_documents(
            query=query,
            top_k=top_k
        )

        if not documents:
            return(
                "No relevant information was found "
                "in the indexed documents."
            )

        results = []

        for index, document in enumerate(documents, start=1):
            metadata = document.metadata

            source = metadata.get("source","Unknown source")
            page = metadata.get("page","Unknown source")

            results.append(
                f"--- Retrieved Context {index} ---\n"
                f"Source: {source}\n"
                f"Page: {page}\n"
                f"Content:\n{document.page_content.strip()}"
            )
        return "\n\n".join(results)

    except ValueError as exc:
        return f"RAG validation error: {str(exc)}"

    except Exception as exc:
        return f"RAG retrieval error: {str(exc)}"

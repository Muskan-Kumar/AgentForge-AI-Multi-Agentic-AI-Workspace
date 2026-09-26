from langchain_core.tools import tool
from tavily import TavilyClient

from src.core.config import settings


@tool
def web_search(query: str) -> str:
    """
    Search the web using Tavily for current, recent, factual,
    and web-based information.

    The query must be a plain natural-language search query.
    """

    query = query.strip()

    if not query:
        return "Search query cannot be empty."

    client = TavilyClient(
        api_key=settings.TAVILY_API_KEY
    )

    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=5,
    )

    results = []

    for result in response.get("results", []):
        title = result.get("title", "")
        url = result.get("url", "")
        content = result.get("content", "")

        results.append(
            f"Title: {title}\n"
            f"URL: {url}\n"
            f"Content: {content}"
        )

    if not results:
        return "No relevant search results were found."

    return "\n\n".join(results)

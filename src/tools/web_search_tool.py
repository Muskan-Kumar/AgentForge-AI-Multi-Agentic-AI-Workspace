from langchain_core.tools import tool
from tavily import TavilyClient

from src.core.config import settings

def web_search(query: str)->str:
    """Search the web for current and relevant information."""

    client = TavilyClient(
        api_key=settings.TAVILY_API_KEY
    )

    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=5
    )

    results = []

    for result in response.get("results",[]):
        results.append(
            f"Title: {result.get('title','')}\n",
            f"URL: {result.get('url','')}\n",
            f"Content: {result.get('content','')}\n"
        )

    return "\n\n".join(results)


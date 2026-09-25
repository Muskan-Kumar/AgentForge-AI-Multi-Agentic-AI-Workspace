from typing import TypedDict, Any, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict, total=False):
    messages: Annotated[list, add_messages]

    user_query: str

    agent_mode: str
    selected_agents: list[str]

    uploaded_files: list[str]

    chat_result: str
    coding_result: str
    search_results: str
    pdf_context: str
    rag_context: str
    ppt_result: str
    ppt_file: str
    image_file: str

    final_response: str

    llm_calls: int

from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict, total=False):
    messages: Annotated[list[BaseMessage], add_messages]

    user_query: str
    thread_id:str

    agent_mode: str
    selected_agents: list[str]
    current_agent_index: int

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

    error_message: str
    error_agent: str
    retry_count: int
    execution_status: str
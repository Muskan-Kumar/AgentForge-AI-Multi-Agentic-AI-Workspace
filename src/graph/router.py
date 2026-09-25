from typing import Literal
from langchain_core.messages import AIMessage

from src.state.agent_state import AgentState


AgentRoute = Literal[
    "chat",
    "coding",
    "search",
    "pdf",
    "image",
    "ppt",
]


SUPPORTED_AGENTS: set[str] = {
    "chat",
    "coding",
    "search",
    "pdf",
    "image",
    "ppt",
}


DEFAULT_AGENT: AgentRoute = "chat"


def normalize_agent_mode(agent_mode: str | None) -> str:
    """
    Normalize and validate the requested agent mode.
    """

    if not agent_mode:
        return DEFAULT_AGENT

    return agent_mode.strip().lower()


def route_agent(state: AgentState) -> AgentRoute:
    """
    Determine which agent should handle the current request.

    Manual mode routing is handled here.
    Auto/Supervisor routing will be added separately.
    """

    agent_mode = normalize_agent_mode(
        state.get("agent_mode")
    )

    if agent_mode in SUPPORTED_AGENTS:
        return agent_mode  # type: ignore[return-value]

    return DEFAULT_AGENT


def is_supported_agent(agent_mode: str | None) -> bool:
    """
    Check whether an agent mode is supported.
    """

    normalized_mode = normalize_agent_mode(agent_mode)

    return normalized_mode in SUPPORTED_AGENTS



def route_search_tools(state: AgentState) -> str:
    messages = state.get("messages", [])

    if not messages:
        return "end"

    last_message = messages[-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"

    return "end"


def route_pdf_tools(state: AgentState) -> str:
    messages = state.get("messages", [])

    if not messages:
        return "end"

    last_message = messages[-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"

    return "end"


def route_image_tools(state: AgentState)-> str:
    messages = state.get("messages",[])

    if not messages:
        return "end"

    last_messages = messages[-1]

    if isinstance(last_messages, AIMessage) and last_messages.tool_calls:
        return "tools"

    return "end"


def route_ppt_tools(state: AgentState)->str:
    messages = state.get("messages",[])

    if not messages:
        return "end"

    last_messages = messages[-1]

    if isinstance(last_messages, AIMessage) and last_messages.tool_calls:
        return "tools"

    return "end"

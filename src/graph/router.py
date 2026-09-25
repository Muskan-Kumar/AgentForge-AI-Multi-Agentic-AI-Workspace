from typing import Literal
from langchain_core.messages import AIMessage

from src.state.agent_state import AgentState
from src.graph.supervisor import supervisor_select_agents

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
    agent_mode = normalize_agent_mode(
        state.get("agent_mode")
    )

    if agent_mode == "auto":
        selected_agents = state.get("selected_agents", [])

        if selected_agents:
            current_index = state.get(
                "current_agent_index",
                0
            )

            if current_index < len(selected_agents):
                return selected_agents[current_index]

            
        selected_agents = supervisor_select_agents(
            state.get("user_query", "")
        )

        if selected_agents:
            return selected_agents[0]

        return DEFAULT_AGENT

    if agent_mode in SUPPORTED_AGENTS:
        return agent_mode

    return DEFAULT_AGENT


def is_supported_agent(agent_mode: str | None) -> bool:
    """
    Check whether an agent mode is supported.
    """

    normalized_mode = normalize_agent_mode(agent_mode)

    return (
        normalized_mode == "auto"
        or normalized_mode in SUPPORTED_AGENTS
    )



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

    last_message = messages[-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"

    return "end"


def route_ppt_tools(state: AgentState)->str:
    messages = state.get("messages",[])

    if not messages:
        return "end"

    last_message = messages[-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"

    return "end"


def route_coding_tools(state: AgentState) -> str:
    messages = state.get("messages", [])

    if not messages:
        return "end"

    last_message = messages[-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"

    return "end"



def route_next_agent(state: AgentState) -> str:
    selected_agents = state.get("selected_agents", [])

    current_index = state.get(
        "current_agent_index",
        0
    )


    if current_index >= len(selected_agents):
        return "end"

    return selected_agents[current_index]



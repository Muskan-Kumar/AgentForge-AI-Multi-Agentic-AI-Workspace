from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from src.state.agent_state import AgentState


def _clip(text: str, limit: int = 5000) -> str:
    if not text:
        return ""

    if len(text) <= limit:
        return text

    return text[:limit] + "\n[Context truncated]"


def build_agent_messages(
    state: AgentState,
    agent_name: str,
):
    user_query = state.get("user_query", "")

    messages = [
        HumanMessage(content=user_query)
    ]

    if agent_name == "coding":
        if state.get("search_results"):
            messages.append(
                HumanMessage(
                    content=(
                        "Relevant research from Search Agent:\n"
                        + _clip(state["search_results"], 5000)
                    )
                )
            )

        if state.get("pdf_context"):
            messages.append(
                HumanMessage(
                    content=(
                        "Relevant PDF context:\n"
                        + _clip(state["pdf_context"], 4000)
                    )
                )
            )

    elif agent_name == "image":
        if state.get("search_results"):
            messages.append(
                HumanMessage(
                    content=(
                        "Relevant research:\n"
                        + _clip(state["search_results"], 3000)
                    )
                )
            )

        if state.get("coding_result"):
            messages.append(
                HumanMessage(
                    content=(
                        "Relevant coding result:\n"
                        + _clip(state["coding_result"], 3000)
                    )
                )
            )

    elif agent_name == "ppt":
        if state.get("search_results"):
            messages.append(
                HumanMessage(
                    content=(
                        "Research:\n"
                        + _clip(state["search_results"], 3000)
                    )
                )
            )

        if state.get("coding_result"):
            messages.append(
                HumanMessage(
                    content=(
                        "Coding result:\n"
                        + _clip(state["coding_result"], 3000)
                    )
                )
            )

        if state.get("pdf_context"):
            messages.append(
                HumanMessage(
                    content=(
                        "Document context:\n"
                        + _clip(state["pdf_context"], 3000)
                    )
                )
            )

    last_messages = state.get("messages", [])

    if last_messages and isinstance(last_messages[-1], ToolMessage):
        if len(last_messages) >= 2:
            previous_message = last_messages[-2]

            if isinstance(previous_message, AIMessage):
                messages.append(previous_message)

        messages.append(last_messages[-1])

    return messages

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Literal

from src.auth.dependencies import get_current_user
from src.conversations.service import get_conversation
from src.core.database import get_checkpointer
from src.graph.graph import build_graph

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    ToolMessage,
)

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
    )

    agent_mode: str = "auto"


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatResponse(BaseModel):
    user_id: str
    thread_id: str
    agent_mode: str
    response: str
    agents_executed: list[str]
    execution_status: str



@router.post(
    "/{thread_id}",
    response_model=ChatResponse,
)

def chat(
    thread_id: str,
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    conversation = get_conversation(
        user_id=user_id,
        thread_id=thread_id,
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    with get_checkpointer() as checkpointer:
        graph = build_graph(
            checkpointer=checkpointer
        )

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        result = graph.invoke(
            {
                "user_query": request.message,
                "agent_mode": request.agent_mode,
                "thread_id": user_id,
            },
            config=config,
        )

    return ChatResponse(
        user_id=user_id,
        thread_id=thread_id,
        agent_mode=request.agent_mode,
        response=result.get(
            "final_response",
            "",
        ),
        agents_executed=result.get(
            "agents_executed",
            [],
        ),
        execution_status=result.get(
            "execution_status",
            "completed",
        ),
    )


@router.get("/{thread_id}/history")
def get_chat_history(
    thread_id: str,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    conversation = get_conversation(
        user_id=user_id,
        thread_id=thread_id,
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    with get_checkpointer() as checkpointer:
        graph = build_graph(checkpointer=checkpointer)

        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        state = graph.get_state(config)

    if not state or not state.values:
        return {
            "thread_id": thread_id,
            "messages": [],
        }

    messages = state.values.get("messages", [])

    history = []

    for message in messages:

        if isinstance(message, HumanMessage):
            content = message.content

            if isinstance(content, str) and content.strip():
                history.append(
                    {
                        "role": "user",
                        "content": content,
                    }
                )

        elif isinstance(message, AIMessage):

            if message.tool_calls:
                continue

            content = message.content

            if isinstance(content, str) and content.strip():
                history.append(
                    {
                        "role": "assistant",
                        "content": content,
                    }
                )

        elif isinstance(message, ToolMessage):
            continue

    return {
        "thread_id": thread_id,
        "messages": history,
    }

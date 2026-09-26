from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from src.auth.dependencies import get_current_user
from src.core.database import get_checkpointer
from src.graph.graph import build_graph


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


@router.post("/")
def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    with get_checkpointer() as checkpointer:

        graph = build_graph(
            checkpointer=checkpointer
        )

        config = {
            "configurable": {
                "thread_id": user_id,
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

    return {
        "user_id": user_id,
        "agent_mode": request.agent_mode,
        "response": result.get(
            "final_response",
            "",
        ),
    }

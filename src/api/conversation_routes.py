from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.auth.dependencies import get_current_user
from src.conversations.service import (
    create_conversation,
    get_conversation,
    get_user_conversations,
    delete_conversation,
)


router = APIRouter(
    prefix="/api/conversations",
    tags=["Conversations"],
)


class CreateConversationRequest(BaseModel):
    title: str = Field(
        default="New Chat",
        min_length=1,
        max_length=255,
    )


@router.post("/")
def create_new_conversation(
    request: CreateConversationRequest,
    current_user: dict = Depends(get_current_user),
):
    conversation = create_conversation(
        user_id=current_user["user_id"],
        title=request.title,
    )

    return {
        "thread_id": conversation.thread_id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
    }


@router.get("/")
def list_conversations(
    current_user: dict = Depends(get_current_user),
):
    conversations = get_user_conversations(
        current_user["user_id"]
    )

    return {
        "conversations": [
            {
                "thread_id": conversation.thread_id,
                "title": conversation.title,
                "created_at": conversation.created_at,
                "updated_at": conversation.updated_at,
            }
            for conversation in conversations
        ]
    }


@router.get("/{thread_id}")
def get_single_conversation(
    thread_id: str,
    current_user: dict = Depends(get_current_user),
):
    conversation = get_conversation(
        user_id=current_user["user_id"],
        thread_id=thread_id,
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    return {
        "thread_id": conversation.thread_id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
    }


@router.delete("/{thread_id}")
def remove_conversation(
    thread_id: str,
    current_user: dict = Depends(get_current_user),
):
    deleted = delete_conversation(
        user_id=current_user["user_id"],
        thread_id=thread_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    return {
        "message": "Conversation deleted successfully",
        "thread_id": thread_id,
    }

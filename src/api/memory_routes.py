from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.memory.long_term_memory import long_term_memory


router = APIRouter(
    prefix="/api/memory",
    tags=["Memory"],
)


class MemoryUpdateRequest(BaseModel):
    value: str = Field(
        ...,
        min_length=1,
        max_length=500,
    )


@router.get("/{user_id}")
def get_memories(user_id: str):
    memories = long_term_memory.get_all_memories(user_id)

    return {
        "user_id": user_id,
        "memories": memories,
    }


@router.get("/{user_id}/{memory_key}")
def get_memory(
    user_id: str,
    memory_key: str,
):
    value = long_term_memory.get_memory(
        user_id,
        memory_key,
    )

    if value is None:
        raise HTTPException(
            status_code=404,
            detail="Memory not found",
        )

    return {
        "user_id": user_id,
        "key": memory_key,
        "value": value,
    }


@router.put("/{user_id}/{memory_key}")
def update_memory(
    user_id: str,
    memory_key: str,
    request: MemoryUpdateRequest,
):
    try:
        long_term_memory.update_memory(
            user_id=user_id,
            memory_key=memory_key,
            memory_value=request.value,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return {
        "message": "Memory updated successfully",
        "user_id": user_id,
        "key": memory_key,
        "value": request.value,
    }


@router.delete("/{user_id}/{memory_key}")
def delete_memory(
    user_id: str,
    memory_key: str,
):
    long_term_memory.delete_memory(
        user_id=user_id,
        memory_key=memory_key,
    )

    return {
        "message": "Memory deleted successfully",
        "user_id": user_id,
        "key": memory_key,
    }


@router.delete("/{user_id}")
def clear_memories(user_id: str):
    long_term_memory.clear_memories(user_id)

    return {
        "message": "All memories cleared successfully",
        "user_id": user_id,
    }

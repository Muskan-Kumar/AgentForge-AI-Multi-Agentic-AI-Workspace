from fastapi import FastAPI

from src.api.auth_routes import router as auth_router
from src.api.memory_routes import router as memory_router
from src.api.chat_routes import router as chat_router

app = FastAPI(
    title="AgentForge AI",
    description="Multi-Agentic AI Workspace API",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(memory_router)
app.include_router(chat_router)
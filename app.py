from fastapi import FastAPI

from src.api.auth_routes import router as auth_router
from src.api.memory_routes import router as memory_router
from src.api.chat_routes import router as chat_router
from src.api.conversation_routes import router as conversation_router

from src.api.error_handlers import (
    agentforge_exception_handler,
    unexpected_exception_handler,
)

from src.core.exceptions import AgentForgeException
from src.core.logging_config import setup_logging

setup_logging()


app = FastAPI(
    title="AgentForge AI",
    description="Multi-Agentic AI Workspace API",
    version="1.0.0",
)


app.add_exception_handler(
    AgentForgeException,
    agentforge_exception_handler,
)

app.add_exception_handler(
    Exception,
    unexpected_exception_handler,
)


app.include_router(auth_router)
app.include_router(memory_router)
app.include_router(chat_router)
app.include_router(conversation_router)

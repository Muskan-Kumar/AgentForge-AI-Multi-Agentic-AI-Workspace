from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from src.api.security_middleware import SecurityHeadersMiddleware

from src.api.auth_routes import router as auth_router
from src.api.memory_routes import router as memory_router
from src.api.chat_routes import router as chat_router
from src.api.conversation_routes import router as conversation_router
from src.api.middleware import RequestIDMiddleware

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

app.add_middleware(
    RequestIDMiddleware
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[   ### production me frontend url se change krna h
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
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

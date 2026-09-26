from fastapi import FastAPI

from src.api.memory_routes import router as memory_router


app = FastAPI(
    title="AgentForge AI",
    description="Multi-Agentic AI Workspace API",
    version="1.0.0",
)

app.include_router(memory_router)
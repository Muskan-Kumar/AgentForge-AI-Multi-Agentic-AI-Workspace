import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from src.core.exceptions import AgentForgeException


logger = logging.getLogger(__name__)


async def agentforge_exception_handler(
    request: Request,
    exc: AgentForgeException,
):
    logger.error(
        "AgentForge error: %s | Path: %s",
        exc.message,
        request.url.path,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.message,
        },
    )


async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "Unhandled exception | Path: %s",
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
        },
    )
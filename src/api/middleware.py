import logging
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.request_context import (
    set_request_id,
    reset_request_id,
)


logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        request_id = (
            request.headers.get("X-Request-ID")
            or str(uuid.uuid4())
        )

        request.state.request_id = request_id

        token = set_request_id(request_id)

        logger.info(
            "Request started | method=%s | path=%s",
            request.method,
            request.url.path,
        )

        try:
            response = await call_next(request)

            logger.info(
                "Request completed | status=%s",
                response.status_code,
            )

            response.headers["X-Request-ID"] = request_id

            return response

        except Exception:
            logger.exception(
                "Request failed",
            )
            raise

        finally:
            reset_request_id(token)
            
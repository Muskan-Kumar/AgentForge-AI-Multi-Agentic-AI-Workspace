import logging
import sys

from src.core.request_context import get_request_id


class RequestIDFilter(logging.Filter):

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


def setup_logging():

    handler = logging.StreamHandler(sys.stdout)

    handler.addFilter(
        RequestIDFilter()
    )

    formatter = logging.Formatter(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "request_id=%(request_id)s | "
        "%(message)s"
    )

    handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
        force=True,
    )
    
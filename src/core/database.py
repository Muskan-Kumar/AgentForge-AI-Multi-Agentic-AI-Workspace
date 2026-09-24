from contextlib import contextmanager

from langgraph.checkpoint.postgres import PostgresSaver

from src.core.config import settings


@contextmanager
def get_checkpointer():
    with PostgresSaver.from_conn_string(
        settings.POSTGRES_URL
    ) as checkpointer:
        checkpointer.setup()
        yield checkpointer
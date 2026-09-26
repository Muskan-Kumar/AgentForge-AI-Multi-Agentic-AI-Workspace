import uuid

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from src.auth.user_service import SessionLocal
from src.conversations.models import Conversation, ConversationBase
from src.core.config import settings


engine = create_engine(
    settings.POSTGRES_URL,
    pool_pre_ping=True,
)

ConversationBase.metadata.create_all(engine)


def create_conversation(
    user_id: str,
    title: str = "New Chat",
) -> Conversation:

    thread_id = str(uuid.uuid4())

    with SessionLocal() as session:

        conversation = Conversation(
            thread_id=thread_id,
            user_id=user_id,
            title=title,
        )

        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        return conversation


def get_user_conversations(
    user_id: str,
) -> list[Conversation]:

    with SessionLocal() as session:

        statement = (
            select(Conversation)
            .where(
                Conversation.user_id == user_id
            )
            .order_by(
                Conversation.updated_at.desc()
            )
        )

        return list(
            session.scalars(statement).all()
        )


def get_conversation(
    user_id: str,
    thread_id: str,
) -> Conversation | None:

    with SessionLocal() as session:

        statement = (
            select(Conversation)
            .where(
                Conversation.thread_id == thread_id,
                Conversation.user_id == user_id,
            )
        )

        return session.scalar(statement)


def delete_conversation(
    user_id: str,
    thread_id: str,
) -> bool:

    with SessionLocal() as session:

        statement = (
            select(Conversation)
            .where(
                Conversation.thread_id == thread_id,
                Conversation.user_id == user_id,
            )
        )

        conversation = session.scalar(statement)

        if not conversation:
            return False

        session.delete(conversation)
        session.commit()

        return True
    
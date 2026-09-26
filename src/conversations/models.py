from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.orm import declarative_base


ConversationBase = declarative_base()


class Conversation(ConversationBase):
    __tablename__ = "agentforge_conversations"

    thread_id = Column(
        String(100),
        primary_key=True,
    )

    user_id = Column(
        String(36),
        nullable=False,
        index=True,
    )

    title = Column(
        String(255),
        nullable=False,
        default="New Chat",
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    
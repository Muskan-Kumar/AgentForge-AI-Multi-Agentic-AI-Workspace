from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import declarative_base


UserBase = declarative_base()


class User(UserBase):
    __tablename__ = "agentforge_users"

    user_id = Column(String(36), primary_key=True)

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash = Column(
        String(500),
        nullable=False,
    )

    password_reset_token_hash = Column(
        String(64),
        nullable=True,
        unique=True,
    )

    password_reset_expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

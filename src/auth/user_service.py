import uuid

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from src.auth.user_model import User, UserBase
from src.auth.security import hash_password
from src.core.config import settings

from datetime import datetime, timedelta, timezone

from src.auth.security import (
    hash_password,
    create_password_reset_token,
    hash_reset_token,
)


engine = create_engine(
    settings.POSTGRES_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

UserBase.metadata.create_all(engine)


def create_user(email: str, password: str) -> User:
    with SessionLocal() as session:
        existing_user = session.scalar(
            select(User).where(User.email == email)
        )

        if existing_user:
            raise ValueError(
                "User with this email already exists"
            )

        user = User(
            user_id=str(uuid.uuid4()),
            email=email.lower().strip(),
            password_hash=hash_password(password),
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        return user


def get_user_by_email(email: str) -> User | None:
    with SessionLocal() as session:
        return session.scalar(
            select(User).where(
                User.email == email.lower().strip()
            )
        )


def update_password(
    email: str,
    new_password: str,
) -> bool:
    with SessionLocal() as session:
        user = session.scalar(
            select(User).where(
                User.email == email.lower().strip()
            )
        )

        if not user:
            return False

        user.password_hash = hash_password(new_password)

        session.commit()

        return True



def create_password_reset_request(
    email: str,
) -> str | None:

    with SessionLocal() as session:

        user = session.scalar(
            select(User).where(
                User.email == email.lower().strip()
            )
        )

        if not user:
            return None

        raw_token, token_hash = (
            create_password_reset_token()
        )

        user.password_reset_token_hash = token_hash

        user.password_reset_expires_at = (
            datetime.now(timezone.utc)
            + timedelta(minutes=15)
        )

        session.commit()

        return raw_token


def reset_password(
    token: str,
    new_password: str,
) -> bool:

    token_hash = hash_reset_token(token)

    with SessionLocal() as session:

        user = session.scalar(
            select(User).where(
                User.password_reset_token_hash == token_hash
            )
        )

        if not user:
            return False

        if not user.password_reset_expires_at:
            return False

        expires_at = user.password_reset_expires_at

        if expires_at <= datetime.now(timezone.utc):
            return False

        user.password_hash = hash_password(
            new_password
        )

        user.password_reset_token_hash = None
        user.password_reset_expires_at = None

        session.commit()

        return True
    
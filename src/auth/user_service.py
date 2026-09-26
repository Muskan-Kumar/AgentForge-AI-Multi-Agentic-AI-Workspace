import uuid

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from src.auth.user_model import User, UserBase
from src.core.config import settings
from src.auth.security import hash_password


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


def create_user(
    email: str,
    password: str,
) -> User:

    with SessionLocal() as session:

        existing_user = session.scalar(
            select(User).where(
                User.email == email
            )
        )

        if existing_user:
            raise ValueError(
                "User with this email already exists"
            )

        user = User(
            user_id=str(uuid.uuid4()),
            email=email,
            password_hash=hash_password(password),
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        return user


def get_user_by_email(
    email: str,
) -> User | None:

    with SessionLocal() as session:

        return session.scalar(
            select(User).where(
                User.email == email
            )
        )

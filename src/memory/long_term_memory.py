from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    String,
    Text,
    create_engine,
    select,
)
from sqlalchemy.orm import declarative_base, sessionmaker

from src.core.config import settings


Base = declarative_base()


class AgentMemory(Base):

    __tablename__ = "agentforge_memories"

    user_id = Column(
        String(255),
        primary_key=True,
    )

    memory_key = Column(
        String(255),
        primary_key=True,
    )

    memory_value = Column(
        Text,
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
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


Base.metadata.create_all(engine)


class LongTermMemory:

    def save_memory(
        self,
        user_id: str,
        memory_key: str,
        memory_value: str,
    ) -> None:

        if not user_id:
            raise ValueError("user_id is required")

        if not memory_key:
            raise ValueError("memory_key is required")

        if not memory_value:
            raise ValueError("memory_value is required")

        with SessionLocal() as session:

            memory = session.get(
                AgentMemory,
                (user_id, memory_key),
            )

            if memory:

                memory.memory_value = memory_value
                memory.updated_at = datetime.now(
                    timezone.utc
                )

            else:

                memory = AgentMemory(
                    user_id=user_id,
                    memory_key=memory_key,
                    memory_value=memory_value,
                    updated_at=datetime.now(
                        timezone.utc
                    ),
                )

                session.add(memory)

            session.commit()

    def get_memory(
        self,
        user_id: str,
        memory_key: str,
    ) -> str | None:

        if not user_id:
            raise ValueError("user_id is required")

        with SessionLocal() as session:

            memory = session.get(
                AgentMemory,
                (user_id, memory_key),
            )

            if not memory:
                return None

            return memory.memory_value

    def get_all_memories(
        self,
        user_id: str,
    ) -> dict[str, str]:

        if not user_id:
            raise ValueError("user_id is required")

        with SessionLocal() as session:

            statement = select(AgentMemory).where(
                AgentMemory.user_id == user_id
            )

            memories = session.scalars(
                statement
            ).all()

            return {
                memory.memory_key: memory.memory_value
                for memory in memories
            }

    def get_relevant_memories(
        self,
        user_id: str,
        query: str,
    ) -> dict[str, str]:

        if not user_id:
            raise ValueError("user_id is required")

        if not query:
            return {}

        memories = self.get_all_memories(user_id)

        if not memories:
            return {}

        query_words = {
            word.strip(".,!?").lower()
            for word in query.split()
            if len(word.strip(".,!?")) > 2
        }

        relevant_memories = {}

        for key, value in memories.items():

            memory_text = f"{key} {value}".lower()

            memory_words = {
                word.strip(".,!?").lower()
                for word in memory_text.split()
                if len(word.strip(".,!?")) > 2
            }

            if query_words.intersection(memory_words):
                relevant_memories[key] = value

        return relevant_memories


    def delete_memory(
        self,
        user_id: str,
        memory_key: str,
    ) -> None:

        if not user_id:
            raise ValueError("user_id is required")

        if not memory_key:
            raise ValueError("memory_key is required")

        with SessionLocal() as session:

            memory = session.get(
                AgentMemory,
                (user_id, memory_key),
            )

            if memory:
                session.delete(memory)
                session.commit()


    def update_memory(
        self,
        user_id: str,
        memory_key: str,
        memory_value: str,
    ) -> None:

        if not user_id:
            raise ValueError("user_id is required")

        if not memory_key:
            raise ValueError("memory_key is required")

        if not memory_value:
            raise ValueError("memory_value is required")

        with SessionLocal() as session:

            memory = session.get(
                AgentMemory,
                (user_id, memory_key),
            )

            if not memory:
                raise ValueError(
                    f"Memory '{memory_key}' does not exist"
                )

            memory.memory_value = memory_value
            memory.updated_at = datetime.now(timezone.utc)

            session.commit()

    def clear_memories(self, user_id: str) -> None:

        if not user_id:
            raise ValueError("user_id is required")

        with SessionLocal() as session:

            statement = select(AgentMemory).where(
                AgentMemory.user_id == user_id
            )

            memories = session.scalars(statement).all()

            for memory in memories:
                session.delete(memory)

            session.commit()

long_term_memory = LongTermMemory()

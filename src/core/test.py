from src.core.database import get_checkpointer


checkpointer = get_checkpointer()

print("PostgreSQL connected successfully!")
print("LangGraph checkpointer initialized successfully!")
from src.core.database import get_checkpointer
from src.graph.graph import build_graph
from src.memory.long_term_memory import long_term_memory


USER_ID = "integration-test-user"

with get_checkpointer() as checkpointer:

    agentforge_graph = build_graph(checkpointer)

    config = {
        "configurable": {
            "thread_id": USER_ID
        }
    }

    result = agentforge_graph.invoke(
    {
        "user_query": "What programming language do I prefer?",
        "agent_mode": "chat",
        "thread_id": USER_ID,
    },
    config=config,
)

print("\nSecond Response:")
print(result["final_response"])


print("\nLong-Term Memories:")

print(
    long_term_memory.get_all_memories(USER_ID)
)
from src.core.database import get_checkpointer
from src.graph.graph import build_graph
from src.memory.long_term_memory import long_term_memory


USER_ID = "agent-memory-test"


with get_checkpointer() as checkpointer:

    agentforge_graph = build_graph(checkpointer)

    config = {
        "configurable": {
            "thread_id": USER_ID
        }
    }

    result = agentforge_graph.invoke(
        {
            "user_query": "Give me a simple Java REST API example.",
            "agent_mode": "coding",
            "thread_id": USER_ID,
        },
        config=config,
    )

    print("\nFinal Response:")
    print(result["final_response"])

    print("\nLoaded Relevant Memory:")
    print(result.get("memory_context", ""))

    print("\nAll Stored Memories:")
    print(
        long_term_memory.get_all_memories(USER_ID)
    )
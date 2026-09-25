from src.core.database import get_checkpointer
from src.graph.graph import build_graph


with get_checkpointer() as checkpointer:

    agentforge_graph = build_graph(checkpointer)

    # User 1
    config_user_1 = {
        "configurable": {
            "thread_id": "user-1"
        }
    }

    result = agentforge_graph.invoke(
        {
            "user_query": "My name is Muskan.",
            "agent_mode": "chat",
        },
        config=config_user_1,
    )

    print("USER 1 - Message 1:")
    print(result["final_response"])


    # User 2
    config_user_2 = {
        "configurable": {
            "thread_id": "user-2"
        }
    }

    result = agentforge_graph.invoke(
        {
            "user_query": "What is my name?",
            "agent_mode": "chat",
        },
        config=config_user_2,
    )

    print("USER 2 - Message 1:")
    print(result["final_response"])


    # User 1 again
    result = agentforge_graph.invoke(
        {
            "user_query": "What is my name?",
            "agent_mode": "chat",
        },
        config=config_user_1,
    )

    print("USER 1 - Message 2:")
    print(result["final_response"])
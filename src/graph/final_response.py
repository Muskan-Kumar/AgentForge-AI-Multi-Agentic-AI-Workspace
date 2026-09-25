from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from src.core.config import settings
from src.state.agent_state import AgentState


final_llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model=settings.GROQ_MODEL,
    temperature=0,
)


FINAL_SYSTEM_PROMPT = """
You are AgentForge Final Response Agent.

Your responsibility is to produce the final response for the user after
one or more specialized agents have completed their tasks.

You receive the user's original request and the results produced by
specialized agents.

Your responsibilities:

1. Combine relevant agent outputs into one coherent response.
2. Do not invent information that is not present in the agent results.
3. Preserve important file paths, generated artifacts and tool results.
4. Clearly state when an artifact such as a PPT, image or file was created.
5. Do not repeat unnecessary intermediate reasoning.
6. Keep the response professional, clear and useful.
7. If multiple agents contributed, present their combined result naturally.
8. If an agent failed, clearly communicate the failure instead of hiding it.
9. Never expose API keys, credentials or internal configuration.
10. Do not claim that an artifact was generated unless the agent result
    confirms it.

Response style:

- Start directly with the result.
- Mention generated files when available.
- Use concise markdown.
- Do not mention internal graph nodes, supervisors or routing logic.
"""


final_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", FINAL_SYSTEM_PROMPT),
        (
            "human",
            """
Original user request:
{user_query}

Agent execution results:

Chat result:
{chat_result}

Coding result:
{coding_result}

Search results:
{search_results}

PDF context:
{pdf_context}

RAG context:
{rag_context}

PPT result:
{ppt_result}

PPT file:
{ppt_file}

Image file:
{image_file}

Return the final user-facing response.
""",
        ),
    ]
)


def final_response_node(state: AgentState) -> dict:
    chain = final_prompt | final_llm

    result = chain.invoke(
        {
            "user_query": state.get("user_query", ""),
            "chat_result": state.get("chat_result", ""),
            "coding_result": state.get("coding_result", ""),
            "search_results": state.get("search_results", ""),
            "pdf_context": state.get("pdf_context", ""),
            "rag_context": state.get("rag_context", ""),
            "ppt_result": state.get("ppt_result", ""),
            "ppt_file": state.get("ppt_file", ""),
            "image_file": state.get("image_file", ""),
        }
    )

    return {
        "final_response": result.content
    }

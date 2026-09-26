from typing import Literal

from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from src.core.config import settings


AgentName = Literal[
    "chat",
    "coding",
    "search",
    "pdf",
    "image",
    "ppt",
]


SUPPORTED_AGENTS: list[str] = [
    "chat",
    "coding",
    "search",
    "pdf",
    "image",
    "ppt",
]


class SupervisorDecision(BaseModel):
    agents: list[AgentName] = Field(
        min_length=1,
        description="Agents required to complete the user's request, in execution order.",
    )


supervisor_llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model=settings.GROQ_MODEL,
    temperature=0,
)


SUPERVISOR_SYSTEM_PROMPT = """
You are AgentForge Supervisor, the central orchestration component of a
professional multi-agent AI workspace.

Analyze the user's request and select the specialized agents required
to complete it.

Available agents:

chat:
General conversation, explanations, brainstorming, writing and
non-specialized assistance.

coding:
Programming, software development, debugging, code review,
refactoring, architecture and code execution.

search:
Current information, web research, latest information and
source-based research.

pdf:
PDF document analysis, document question answering and
retrieval from indexed documents.

image:
Image generation and visual content creation.

ppt:
PowerPoint presentation generation.

Routing rules:

1. Select only agents actually required.
2. Prefer specialized agents when the request clearly matches them.
3. Use multiple agents when multiple capabilities are required.
4. Preserve logical execution order.
5. Use search before ppt when current external information is required.
6. Use search before coding when current external technical information
   is required.
7. Use pdf when information must be obtained from a PDF or indexed
   document.
8. Use image when image generation is requested.
9. Use ppt when PowerPoint generation is requested.
10. Use coding for programming and software engineering tasks.
11. Use chat only when no specialized agent is required.
12. Never select unsupported agents.
13. Never duplicate an agent.
14. If the request explicitly asks for latest, current, recent,
    today's or up-to-date information, select search.
15. If a request combines research with presentation generation,
    select search followed by ppt.

Examples:

Explain what RAG is.
-> ["chat"]

Create a Python REST API.
-> ["coding"]

What are the latest developments in AI?
-> ["search"]

Create a PPT about the latest AI developments.
-> ["search", "ppt"]

Read this PDF and create a presentation from it.
-> ["pdf", "ppt"]

Research the latest Python 3.13 features and create sample code.
-> ["search", "coding"]

Generate an image of a futuristic AI laboratory.
-> ["image"]
"""


supervisor_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SUPERVISOR_SYSTEM_PROMPT),
        ("human", "{user_query}"),
    ]
)


structured_supervisor = supervisor_llm.with_structured_output(
    SupervisorDecision
)

supervisor_chain = supervisor_prompt | structured_supervisor


def supervisor_route(user_query: str) -> str:
    agents = supervisor_select_agents(user_query)

    if not agents:
        return "chat"

    return agents[0]


def supervisor_select_agents(
    user_query: str,
) -> list[str]:

    if not user_query or not user_query.strip():
        return ["chat"]

    try:
        decision = supervisor_chain.invoke(
            {
                "user_query": user_query.strip(),
            }
        )

        valid_agents: list[str] = []

        for agent in decision.agents:
            if (
                agent in SUPPORTED_AGENTS
                and agent not in valid_agents
            ):
                valid_agents.append(agent)

        if not valid_agents:
            return ["chat"]

        specialized_agents = [
            agent
            for agent in valid_agents
            if agent != "chat"
        ]

        if specialized_agents:
            return specialized_agents

        return ["chat"]

    except Exception as e:
        raise RuntimeError(
            f"Supervisor routing failed: {e}"
        ) from e
    
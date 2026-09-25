from typing import Literal

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


supervisor_llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model=settings.GROQ_MODEL,
    temperature=0,
)


SUPERVISOR_SYSTEM_PROMPT = """
You are AgentForge Supervisor, the central orchestration component of a
professional multi-agent AI workspace.

Your responsibility is to analyze the user's request and determine the
most appropriate sequence of specialized agents required to complete it.

Available agents:

- chat:
  General conversation, explanations, brainstorming, writing and
  non-specialized assistance.

- coding:
  Software development, programming, debugging, code review,
  refactoring, architecture and code execution.

- search:
  Current information, web research, latest information and
  source-based research.

- pdf:
  PDF document analysis, document question answering and
  retrieval from indexed documents.

- image:
  Image generation and visual content creation.

- ppt:
  PowerPoint presentation generation.

Routing principles:

1. Select only agents that are actually required.
2. Prefer specialized agents when the request clearly matches their
   capabilities.
3. Use multiple agents when the task contains multiple independent
   requirements.
4. Preserve a logical execution order.
5. Use search before ppt when current external information is required
   for the presentation.
6. Use search before coding when implementation requires current
   external technical information.
7. Use pdf when the task requires information from a PDF or indexed
   document.
8. Use image when visual generation is explicitly requested.
9. Use ppt when a PowerPoint presentation is explicitly requested.
10. Use coding for programming and software engineering tasks.
11. Use chat only when no specialized agent is required.
12. Never select unsupported agents.
13. Never duplicate an agent unnecessarily.

Examples:

User:
"Explain what RAG is."

Output:
chat

User:
"Create a Python REST API."

Output:
coding

User:
"What are the latest developments in AI?"

Output:
search

User:
"Create a PPT about the latest AI developments."

Output:
search,ppt

User:
"Read this PDF and create a presentation from it."

Output:
pdf,ppt

User:
"Research the latest Python 3.13 features and create sample code."

Output:
search,coding

User:
"Generate an image of a futuristic AI laboratory."

Output:
image

Output rules:

- Return ONLY the agent names.
- Separate multiple agents using commas.
- Do not add explanations.
- Do not use spaces around commas.

Valid agent names:

chat
coding
search
pdf
image
ppt
"""


supervisor_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SUPERVISOR_SYSTEM_PROMPT),
        ("human", "{user_query}"),
    ]
)


def supervisor_route(user_query: str) -> str:
    """
    Backward-compatible single-agent routing.
    Returns the first selected agent.
    """
    agents = supervisor_select_agents(user_query)

    if not agents:
        return "chat"

    return agents[0]


def supervisor_select_agents(user_query: str) -> list[str]:
    """
    Select one or more agents and preserve their execution order.
    """

    if not user_query or not user_query.strip():
        return ["chat"]

    chain = supervisor_prompt | supervisor_llm

    result = chain.invoke(
        {
            "user_query": user_query.strip()
        }
    )

    raw_output = result.content.strip().lower()

    selected_agents = [
        agent.strip()
        for agent in raw_output.split(",")
        if agent.strip()
    ]

    valid_agents = []

    for agent in selected_agents:
        if agent in SUPPORTED_AGENTS and agent not in valid_agents:
            valid_agents.append(agent)

    if not valid_agents:
        return ["chat"]

    return valid_agents

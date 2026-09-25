from typing import TypedDict

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from src.core.config import settings
from src.memory.long_term_memory import long_term_memory


class ExtractedMemory(TypedDict):
    key: str
    value: str


ALLOWED_MEMORY_KEYS = {
    "name",
    "education",
    "preferred_language",
    "technical_skills",
    "project",
    "career_goal",
    "response_language",
}


BLOCKED_KEY_WORDS = {
    "password",
    "api_key",
    "apikey",
    "token",
    "secret",
    "credential",
    "otp",
    "phone",
    "address",
    "email",
    "credit_card",
}


memory_llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model=settings.GROQ_MODEL,
    temperature=0,
)


MEMORY_EXTRACTION_PROMPT = """
You are the Memory Extraction component of AgentForge AI.

Your task is to identify durable user-specific information from the
conversation that may be useful in future conversations.

Store only information that is:

- Explicitly stated by the user.
- Stable or likely to remain useful.
- About the user.
- Useful for future personalization.

Allowed memory categories:

- name
- education
- preferred_language
- technical_skills
- project
- career_goal
- response_language

Do NOT store:

- Temporary requests.
- One-time questions.
- API keys.
- Passwords.
- Tokens.
- Secrets.
- Credentials.
- OTPs.
- Phone numbers.
- Addresses.
- Email addresses.
- Credit card or financial information.
- Sensitive personal information.
- Assistant-generated information.
- Information inferred from the user's message.

Return memories using this exact format:

key=value

If there are no useful memories, return:

NONE

Conversation:
{conversation}
"""


memory_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", MEMORY_EXTRACTION_PROMPT),
    ]
)


def _is_valid_memory(
    key: str,
    value: str,
) -> bool:

    if not key or not value:
        return False

    normalized_key = key.strip().lower()

    if normalized_key not in ALLOWED_MEMORY_KEYS:
        return False

    for blocked_word in BLOCKED_KEY_WORDS:
        if blocked_word in normalized_key:
            return False

    if len(value.strip()) > 500:
        return False

    return True


def extract_memories(
    user_id: str,
    conversation: str,
) -> list[ExtractedMemory]:

    if not user_id:
        return []

    if not conversation.strip():
        return []

    chain = memory_prompt | memory_llm

    response = chain.invoke(
        {
            "conversation": conversation,
        }
    )

    content = response.content.strip()

    if content.upper() == "NONE":
        return []

    memories: list[ExtractedMemory] = []

    for line in content.splitlines():

        line = line.strip()

        if not line or "=" not in line:
            continue

        key, value = line.split("=", 1)

        key = key.strip().lower()
        value = value.strip()

        if not _is_valid_memory(key, value):
            continue

        memories.append(
            {
                "key": key,
                "value": value,
            }
        )

    return memories


def extract_and_save_memories(
    user_id: str,
    conversation: str,
) -> list[ExtractedMemory]:

    memories = extract_memories(
        user_id=user_id,
        conversation=conversation,
    )

    for memory in memories:

        long_term_memory.save_memory(
            user_id=user_id,
            memory_key=memory["key"],
            memory_value=memory["value"],
        )

    return memories

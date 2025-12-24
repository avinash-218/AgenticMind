from pydantic import BaseModel, Field
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from server_src.content_creation.utils import initialize_llm

class KeywordList(BaseModel):
    """
    Structured output schema for keyword generation.

    This model enforces that the LLM returns a concise, ordered list of
    high-signal search keywords suitable for web research.
    """
    keywords: List[str] = Field(
        description="A concise, relevance-ordered list of search keywords or phrases."
    )

# LLM initialization and structured output binding
llm = initialize_llm()

# Bind an empty tools list to explicitly disable tool usage
structured_llm = llm.bind_tools([])

# Enforce structured output to match KeywordList schema
structured_llm = structured_llm.with_structured_output(KeywordList)

# System prompt defining keyword generation behavior
SYSTEM_KEYWORD_PROMPT = """
You are a search keyword generator.

TASK:
Generate concise, high-signal search keywords for web research.

RULES:
- Prefer short phrases (2-5 words).
- Avoid filler words.
- Do not repeat similar keywords.
- Focus on entities, concepts, and intent.
- Output only keywords relevant to the TITLE and CONTEXT.
- Limit to at most 5 keywords.
- Order the keywords by relevance (the most relevant first).
"""

# Prompt template combining system rules with runtime inputs
keyword_prompt = ChatPromptTemplate.from_messages(
    [
        # System-level instructions
        ("system", SYSTEM_KEYWORD_PROMPT),

        # Human message carrying runtime inputs
        (
            "human",
            "TITLE:\n{title}\n\nCONTEXT:\n{context}"
        ),
    ]
)

# Final keyword generation chain
keyword_generator = keyword_prompt | structured_llm

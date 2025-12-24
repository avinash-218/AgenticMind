from pydantic import BaseModel, Field
from langchain_groq.chat_models import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

class RelevanceGrade(BaseModel):
    """
    Structured output schema for relevance evaluation.

    This model captures a binary relevance decision along with a short,
    human-readable justification explaining the reasoning behind the verdict.
    """
    relevant: bool = Field(
        description=(
            "Indicates whether the provided content is overall relevant "
            "to the given title."
        )
    )
    reason: str = Field(
        description=(
            "Brief explanation justifying why the content was judged "
            "as relevant or not relevant."
        )
    )

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

# Bind an empty tools list to explicitly disable tool usage
structured_llm = llm.bind_tools([])

# Enforce structured output to match RelevanceGrade schema
structured_llm = structured_llm.with_structured_output(RelevanceGrade)

# System prompt defining relevance grading behavior
SYSTEM_RELEVANCE_PROMPT = """
You are a relevance grader.

TASK:
Determine whether the PROVIDED CONTENT is OVERALL relevant to the TITLE.

RULES:
- Judge overall intent, not individual sentences.
- Minor tangents, stylistic notes, or extra information are acceptable.
- Mark NOT relevant only if the content is clearly about a different topic.
"""

# Prompt template combining system rules with runtime inputs
relevance_prompt = ChatPromptTemplate.from_messages(
    [
        # System-level instructions
        ("system", SYSTEM_RELEVANCE_PROMPT),

        # Human message carrying runtime inputs
        (
            "human",
            "TITLE:\n{title}\n\nCONTENT:\n{content}"
        ),
    ]
)

# Final relevance grading chain
relevance_grader = relevance_prompt | structured_llm

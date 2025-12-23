from pydantic import BaseModel, Field
from langchain_groq.chat_models import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

class RelevanceGrade(BaseModel):
    relevant: bool = Field(
        description="Whether the provided content is overall relevant to the title."
    )
    reason: str = Field(
        description="Brief explanation for the relevance decision."
    )

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

# structured_llm = llm.with_structured_output(RelevanceGrade)
structured_llm = llm.bind_tools([])
structured_llm = structured_llm.with_structured_output(RelevanceGrade)

SYSTEM_RELEVANCE_PROMPT = """
You are a relevance grader.

TASK:
Determine whether the PROVIDED CONTENT is OVERALL relevant to the TITLE.

RULES:
- Judge overall intent, not individual sentences.
- Minor tangents, stylistic notes, or extra information are acceptable.
- Mark NOT relevant only if the content is clearly about a different topic.
"""

relevance_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_RELEVANCE_PROMPT),
        (
            "human",
            "TITLE:\n{title}\n\nCONTENT:\n{content}"
        ),
    ]
)

relevance_grader = relevance_prompt | structured_llm

from pydantic import BaseModel, Field
from typing import List
from langchain_groq.chat_models import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

class KeywordList(BaseModel):
    keywords: List[str] = Field(
        description="A concise list of search keywords or phrases."
    )

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

# structured_llm = llm.with_structured_output(KeywordList)
structured_llm = llm.bind_tools([])
structured_llm = structured_llm.with_structured_output(KeywordList)

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

keyword_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_KEYWORD_PROMPT),
        (
            "human",
            "TITLE:\n{title}\n\nCONTEXT:\n{context}"
        ),
    ]
)

keyword_generator = keyword_prompt | structured_llm


from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq.chat_models import ChatGroq

class BlogContent(BaseModel):
    """
    Structured output schema for blog generation.

    This model enforces that the LLM returns a single, complete blog post
    as Markdown-formatted text, ensuring predictable downstream handling.
    """
    content: str = Field(
        description=(
            "A complete, well-structured blog post written in Markdown, "
            "based on the provided title, context, and images."
        )
    )

def initialize_llm():
    """
    Initialize and return the Groq-backed chat language model.

    The model is configured with deterministic output (temperature = 0)
    to ensure consistent, repeatable blog generation.

    Returns:
        ChatGroq: Initialized language model instance.
    """

    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0
    )

    return llm

# LLM initialization and structured output binding
llm = initialize_llm()

# Bind empty tools list (explicitly disables tool usage)
structured_llm = llm.bind_tools([])

# Enforce structured output to match BlogContent schema
structured_llm = structured_llm.with_structured_output(BlogContent)



# System prompt defining writing style, structure, and constraints
SYSTEM_CONTENT_PROMPT = """
You are an imaginative, world-class blog writer and educator.

TASK:
Write a compelling, well-structured blog post using the provided TITLE, CONTEXT, and IMAGES.

OUTPUT FORMAT (MANDATORY):
- The final output MUST be valid Markdown.
- Use proper Markdown headings, lists, tables, spacing, and images.
- The content should be visually appealing and ready for direct publishing on Hashnode.

STRUCTURE REQUIREMENTS:
- Start with a strong hook.
- Use clear Markdown section headers (##) for major sections.
- Each major section should focus on one core idea.

IMAGE USAGE RULES (VERY IMPORTANT):
- You are given a list of IMAGES with URLs and descriptions.
- You MAY insert at most ONE image per major section.
- Insert images ONLY immediately after a section header (##), never mid-paragraph.
- Use standard Markdown image syntax: ![alt text](image_url)
- Use the provided image description as the alt text.
- DO NOT invent new images.
- DO NOT modify image URLs.
- It is acceptable to not use all images if they don't fit naturally.

WRITING RULES:
- Use a friendly, conversational tone while staying accurate and insightful.
- Explain ideas clearly, as if teaching an intelligent beginner.
- Use vivid examples, analogies, or mini-stories where helpful.
- Prefer bullet points, numbered lists, and tables when useful.
- Integrate the provided context naturally; do not quote it mechanically.
- Avoid generic filler; aim for specific, concrete insights.

CONCLUSION:
- End with a short, punchy conclusion with a practical takeaway.

SOURCE & ATTRIBUTION:
- Add a “References” section at the end.
- Include APA-style citations derived strictly from the provided CONTEXT.
- Do NOT invent sources.

IMPORTANT CONSTRAINTS:
- Do NOT introduce facts outside the provided CONTEXT.
- Do NOT mention that context or images were provided.
"""


# Prompt template combining system instructions and runtime inputs
content_prompt = ChatPromptTemplate.from_messages(
    [
        # System-level instructions defining behavior and constraints
        ("system", SYSTEM_CONTENT_PROMPT),

        # Human message carrying runtime inputs
        (
            "human",
            "TITLE:\n{title}\n\n"
            "CONTEXT:\n{context}\n\n"
            "IMAGES (use selectively):\n{images}"
        ),
    ]
)

# Final content writer chain
# Combines prompt template with structured LLM
content_writer = content_prompt | structured_llm

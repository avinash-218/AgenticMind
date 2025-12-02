import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
load_dotenv()

mcp = FastMCP("Content_Creation_Server")

def initialize_llm() -> ChatGoogleGenerativeAI:
    """Initialize Gemini LLM."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=1.0,
        max_retries=3,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )

@mcp.tool()
async def blog_content_creator(topic: str) -> str:
    """
    Generate informative content about a given topic using LangChain + Gemini.
    """
    llm = initialize_llm()

    prompt = ChatPromptTemplate.from_template(
        (
            "You are an imaginative, world-class blog writer and educator.\n\n"
            "Write a compelling blog post about the topic: '{topic}'.\n\n"
            "Requirements:\n"
            "- Start with a hook that grabs the reader's attention.\n"
            "- Use a friendly, conversational tone while staying accurate and informative.\n"
            "- Explain key concepts clearly, as if teaching an intelligent beginner.\n"
            "- Include vivid examples, mini-stories, or analogies to make ideas memorable.\n"
            "- Organize the content into logical sections with clear transitions.\n"
            "- Where useful, include bullet points or numbered lists instead of long paragraphs.\n"
            "- End with a short, punchy conclusion that reinforces the main takeaway and offers a practical next step.\n"
            "- Avoid generic filler; aim for specific, concrete insights and fresh phrasing.\n"
        )
    )

    messages = prompt.format_messages(topic=topic)
    response = await llm.ainvoke(messages)

    return response.content

if __name__ == "__main__":
    print("Starting Content Creation MCP Server...")
    mcp.run(transport="stdio")

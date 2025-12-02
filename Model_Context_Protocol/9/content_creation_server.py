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
        temperature=0.7,
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
        "You are an expert educator. Write a clear, engaging explanation about the topic: '{topic}'. "
        "Include key concepts, examples, and a short summary at the end."
    )

    messages = prompt.format_messages(topic=topic)
    response = await llm.ainvoke(messages)

    return response.content

if __name__ == "__main__":
    print("Starting Content Creation MCP Server...")
    mcp.run(transport="stdio")

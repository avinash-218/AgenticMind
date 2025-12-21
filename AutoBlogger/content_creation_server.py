from logging_config import logger
from content_creation.graph.graph import content_graph
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
load_dotenv()

mcp = FastMCP("Content_Creation_Server")

@mcp.tool()
async def blog_content_creator(topic: str) -> str:
    """
    Generate informative content about a given topic using LangChain + Gemini.
    """
    logger.info(f"Generating content for topic: {topic}")
    result = await content_graph.ainvoke(input={"title":topic})
    if result['content']:
        output = result['content']
        logger.info(f"Content generated successfully.")
    else:
        output = "Content generation failed."
        logger.info(f"{output}")

    return output

if __name__ == "__main__":
    logger.info("Starting Content Creation MCP Server...")
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 8000
    mcp.run(transport="sse")
import sys
import os

# Add project root to PYTHONPATH to allow absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from logging_config import get_logger

# Initialize logger for the Content Creation MCP server
logger = get_logger("ContentCreatorServer")
logger.info("ContentCreatorServer started")

from server_src.content_creation.graph.graph import content_graph
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables (API keys, configs, etc.)
load_dotenv()

# Initialize MCP server instance
mcp = FastMCP("Content_Creation_Server")

@mcp.tool()
async def blog_content_creator(topic: str) -> str:
    """
    Generate blog-style informational content for a given topic.

    This MCP tool invokes a LangGraph-based content generation pipeline
    to produce structured text output for the requested topic.

    Parameters
    ----------
    topic : str
        The subject for which content should be generated.

    Returns
    -------
    str
        Generated content if successful, otherwise an error message.
    """
    logger.info(f"Generating content for topic: {topic}")

    # Invoke the content generation graph asynchronously
    result = await content_graph.ainvoke(input={"title": topic})

    if result.get("content"):
        output = result["content"]
        logger.info("Content generated successfully.")
    else:
        output = "Content generation failed."
        logger.info(output)

    return output

if __name__ == "__main__":
    """
    Entry point for starting the Content Creation MCP Server.
    """
    logger.info("Starting Content Creation MCP Server...")

    # Configure server network settings
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 8000

    # Start MCP server using SSE transport
    mcp.run(transport="sse")

from logging_config import get_logger

logger = get_logger("MarkdownFileServer")
logger.info("MarkdownFileServer started")

import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Markdown_File_Server")

@mcp.tool()
def save_markdown_file(content: str, filename: str = None) -> str:
    """
    Save the given content into a Markdown (.md) file.
    If no filename is provided, a timestamped one will be generated.
    """
    os.makedirs("outputs", exist_ok=True)

    if not filename:
        filename = f"note_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    filepath = os.path.join("markdowns", filename)

    if not filepath.endswith(".md"):
        filepath += ".md"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info(f"Markdown file saved at: {filepath}")

    return f"Markdown file saved at: {filepath}"

if __name__ == "__main__":
    logger.info("Starting Markdown MCP Server...")
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 8002
    mcp.run(transport="sse")
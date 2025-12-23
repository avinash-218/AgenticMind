import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
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
    """
    os.makedirs("markdowns", exist_ok=True)

    if not filename:
        filename = f"note_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    filepath = os.path.join("markdowns", filename)
    if not filepath.endswith(".md"):
        filepath += ".md"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"Markdown file saved at: {filepath}")
    return f"Markdown file saved at: {filepath}"

@mcp.tool()
def read_markdown_file(filename: str) -> str:
    """
    Read and return the contents of a Markdown (.md) file.
    """
    filepath = os.path.join("markdowns", filename)
    if not filepath.endswith(".md"):
        filepath += ".md"

    if not os.path.exists(filepath):
        error_msg = f"Markdown file not found: {filepath}"
        logger.error(error_msg)
        return error_msg

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    logger.info(f"Markdown file read successfully: {filepath}")
    return content

@mcp.tool()
def list_markdown_files() -> str:
    """
    List all Markdown (.md) files in the markdowns directory.
    """
    directory = "markdowns"
    os.makedirs(directory, exist_ok=True)

    files = [
        f for f in os.listdir(directory)
        if f.lower().endswith(".md")
    ]

    if not files:
        logger.info("No markdown files found.")
        return "No markdown files found."

    files.sort()
    logger.info(f"Found {len(files)} markdown files.")

    return "\n".join(files)

@mcp.tool()
def delete_markdown_file(filename: str) -> str:
    """
    Delete a Markdown (.md) file from the markdowns directory.
    """
    directory = "markdowns"
    filepath = os.path.join(directory, filename)

    if not filepath.lower().endswith(".md"):
        filepath += ".md"

    if not os.path.exists(filepath):
        error_msg = f"Markdown file not found: {filepath}"
        logger.error(error_msg)
        return error_msg

    os.remove(filepath)
    logger.info(f"Markdown file deleted: {filepath}")

    return f"Markdown file deleted: {filepath}"

if __name__ == "__main__":
    logger.info("Starting Markdown MCP Server...")
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 8002
    mcp.run(transport="sse")

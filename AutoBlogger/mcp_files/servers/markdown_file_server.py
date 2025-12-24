import sys
import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Path setup so shared modules (logging_config) can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from logging_config import get_logger

# Logger initialization
logger = get_logger("MarkdownFileServer")
logger.info("MarkdownFileServer started")

# MCP server initialization
mcp = FastMCP("Markdown_File_Server")

MARKDOWN_DIR = "markdowns"

@mcp.tool()
def save_markdown_file(content: str, filename: str = None) -> str:
    """
    Save the provided text content into a Markdown (.md) file.

    If no filename is provided, a timestamp-based filename is generated.
    The file is stored inside the `markdowns/` directory.

    Args:
        content (str): Text content to be saved in the markdown file.
        filename (str, optional): Desired filename (with or without .md).

    Returns:
        str: Success message with the saved file path.
    """
    logger.info("Saving markdown file")

    # Ensure markdown directory exists
    os.makedirs(MARKDOWN_DIR, exist_ok=True)

    # Generate filename if not provided
    if not filename:
        filename = f"note_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        logger.debug(f"Generated filename: {filename}")

    # Ensure .md extension
    if not filename.lower().endswith(".md"):
        filename += ".md"

    filepath = os.path.join(MARKDOWN_DIR, filename)

    # Write content to file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"Markdown file saved successfully: {filepath}")
    return f"Markdown file saved at: {filepath}"

@mcp.tool()
def read_markdown_file(filename: str) -> str:
    """
    Read and return the contents of a Markdown (.md) file.

    Args:
        filename (str): Name of the markdown file (with or without .md).

    Returns:
        str: File content if found, otherwise an error message.
    """
    logger.info(f"Reading markdown file: {filename}")

    # Ensure .md extension
    if not filename.lower().endswith(".md"):
        filename += ".md"

    filepath = os.path.join(MARKDOWN_DIR, filename)

    # Validate file existence
    if not os.path.exists(filepath):
        error_msg = f"Markdown file not found: {filepath}"
        logger.error(error_msg)
        return error_msg

    # Read file content
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    logger.info(f"Markdown file read successfully: {filepath}")
    return content

@mcp.tool()
def list_markdown_files() -> str:
    """
    List all Markdown (.md) files available in the markdowns directory.

    Returns:
        str: Newline-separated list of markdown filenames,
             or a message if no files are found.
    """
    logger.info("Listing markdown files")

    # Ensure directory exists
    os.makedirs(MARKDOWN_DIR, exist_ok=True)

    # Collect markdown files
    files = [
        f for f in os.listdir(MARKDOWN_DIR)
        if f.lower().endswith(".md")
    ]

    if not files:
        logger.info("No markdown files found")
        return "No markdown files found."

    files.sort()
    logger.info(f"Found {len(files)} markdown files")

    return "\n".join(files)

@mcp.tool()
def delete_markdown_file(filename: str) -> str:
    """
    Delete a Markdown (.md) file from the markdowns directory.

    Args:
        filename (str): Name of the markdown file (with or without .md).

    Returns:
        str: Success message if deleted, otherwise an error message.
    """
    logger.info(f"Deleting markdown file: {filename}")

    # Ensure .md extension
    if not filename.lower().endswith(".md"):
        filename += ".md"

    filepath = os.path.join(MARKDOWN_DIR, filename)

    # Validate file existence
    if not os.path.exists(filepath):
        error_msg = f"Markdown file not found: {filepath}"
        logger.error(error_msg)
        return error_msg

    os.remove(filepath)
    logger.info(f"Markdown file deleted successfully: {filepath}")

    return f"Markdown file deleted: {filepath}"

if __name__ == "__main__":
    logger.info("Starting Markdown MCP Server")

    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 8002

    logger.info("Markdown MCP Server running on port 8002")
    mcp.run(transport="sse")

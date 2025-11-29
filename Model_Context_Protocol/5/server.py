import os
import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("terminal_server")



@mcp.tool()
async def greet() -> str:
    """
    Greets
    """
    return "hello as- hi"
    
@mcp.tool()
async def create_file(filename: str, content: str) -> str:
    """
    Create a file with specified content.
    """
    try:
        with open(filename, "w") as f:
            f.write(content)
        return f"File '{filename}' created successfully with provided content."
    except Exception as e:
        return f"Error creating file: {str(e)}"


@mcp.tool()
async def delete_file(filename: str) -> str:
    """
    Delete a file from the current working directory.
    """
    try:
        # Ensure file exists
        if not os.path.exists(filename):
            return f"Error: File '{filename}' does not exist."

        # Delete the file
        os.remove(filename)
        return f"File '{filename}' deleted successfully."

    except PermissionError:
        return f"Error: Permission denied while deleting '{filename}'."
    except Exception as e:
        return f"Error deleting file '{filename}': {str(e)}"
    
if __name__ == "__main__":
    mcp.run(transport='stdio')
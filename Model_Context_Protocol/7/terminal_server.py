import os
import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("terminal_server")
DEFAULT_WORKSPACE = os.getcwd()

@mcp.tool()
async def run_command(command: str) -> str:
    """
    Run a terminal command.

    Args:
        command (str): The shell command to execute.

    Returns:
        str: The output of the command or an error message.
    """
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=DEFAULT_WORKSPACE)
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error: {result.stderr}"
    except Exception as e:
        return f"Error executing command: {str(e)}"


@mcp.tool()
async def greet() -> str:
    """
    Greets
    """
    return "hello as- hi"
    
if __name__ == "__main__":
    # print(DEFAULT_WORKSPACE)
    mcp.run(transport='stdio')
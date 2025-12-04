import os
import subprocess
import argparse
from mcp.server.fastmcp import FastMCP  # MCP wrapper for mcp tools
from mcp.server import Server   # underlying server abstration used by FastMCP
from mcp.server.sse import SseServerTransport   # SSE transport layer (used for HTTP communication)

from starlette.applications import Starlette    # lighweight web framework to define routes
from starlette.routing import Route, Mount  # Routing for HTTP and message endpoints
from starlette.requests import Request  # HTTP request objects

import uvicorn  #ASGI server to run starlette app

mcp = FastMCP("sse_mcp_server")
WORKSPACE = os.path.expanduser("~/mcp/workspace")

print(WORKSPACE)

@mcp.tool()
async def add(a: float, b: float) -> float:
    """
    Adds two numbers and returns the result.
    """
    return a + b

@mcp.tool()
async def sub(a: float, b: float) -> float:
    """
    Subtracts the second number from the first and returns the result.
    """
    return a - b

@mcp.tool()
async def mul(a: float, b: float) -> float:
    """
    Multiplies two numbers and returns the result.
    """
    return a * b

@mcp.tool()
async def div(a: float, b: float) -> float:
    """
    Divides the first number by the second and returns the result.
    Raises an error if division by zero is attempted.
    """
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a / b

@mcp.tool()
async def create_file(filename: str, content: str="Hello World!!!") -> str:
    """
    Creates a file inside the WORKSPACE directory.
    Automatically prevents directory traversal outside the workspace.
    Returns the absolute path of the created file.
    """
    # Sanitize and ensure path is inside workspace
    safe_path = os.path.abspath(os.path.join(WORKSPACE, filename))
    if not safe_path.startswith(WORKSPACE):
        raise ValueError("Invalid path: Cannot create files outside workspace.")

    # Create directories if needed
    os.makedirs(os.path.dirname(safe_path), exist_ok=True)

    with open(safe_path, "w", encoding="utf-8") as f:
        f.write(content)

    return safe_path

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
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=WORKSPACE)
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error: {result.stderr}"
    except Exception as e:
        return f"Error executing command: {str(e)}"

# Create starlette app and expose the tools via HTTP (using Server Sent Events transport)
def create_starlette_app(mcp_server: Server, *, debug: bool = True)-> Starlette:
    """
    Create a starlette app with SSE and message endpoints
    
    Args:
        mcp_server (Server): The MCP server instance
        debug (bool): Debug flag

    Returns:
        Starlette: The starlette app.
    """
    # create SSE transport handler to handle long-lived SSE connections
    sse = SseServerTransport("/messages/")  #/messages/ - base url endpoint

    # triggering function when client connects to sse
    async def handle_sse(request: Request)-> None:
        """
        Handles a new SSE client connection and links it to the MCP server.
        Creates live stream between client and mcp server
        """
        # creates SSE connection and hand over read/write streams to MCP
        # request.scope - HTTP connection metadata - url, header, method etc...
        # request.receive - receive msg from client
        # request._send - send msg to client

        # read_stream - read message from client
        # write_stream - write message to client
        async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
            # instead of configuring stdio transport, now we configure SSE using read and write streams to interact with client
            await mcp_server.run(   
                read_stream=read_stream,
                write_stream=write_stream,
                initialization_options=mcp_server.create_initialization_options()
            )

    # returns starlette app with configs
    # sse.handle_post_message is an ASGI app provided by the SSE transport.
    # It handles POST requests where clients send messages to the MCP server (client → server) on /messages/*.
    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse), # for initializing sse connection
            Mount("/messages/", app=sse.handle_post_message)    # handle_post_message - for post based communications
        ]
    )
    # The client first opens /sse to start listening, 
    # then uses /messages/ for all further communication
    # while all responses stream back via /sse

if __name__ == "__main__":
    mcp_server = mcp._mcp_server    #get the underlying mcp_server

    parser = argparse.ArgumentParser(description="Run MCP SSE-based server")
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', default='8081', help='Port to listen to')

    args = parser.parse_args()

    # build starlette app
    starlette_app = create_starlette_app(mcp_server=mcp_server, debug=True)

    uvicorn.run(starlette_app, host=args.host, port=args.port)  # starting a web server using Uvicorn

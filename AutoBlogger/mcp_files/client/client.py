import sys
import os

# Add project root to PYTHONPATH to allow absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from logging_config import get_logger

# Initialize application logger
logger = get_logger("MCPClient")
logger.info("Client started")

import asyncio
from contextlib import AsyncExitStack
import json
import traceback

from mcp import ClientSession
from mcp.client.sse import sse_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_groq.chat_models import ChatGroq

from dotenv import load_dotenv
load_dotenv()


def load_mcp_config(config_path: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../mcp_config.json"))):
    """
    Load MCP server configuration from a JSON file.

    Parameters
    ----------
    config_path : str
        Absolute path to the MCP configuration JSON file.

    Returns
    -------
    dict
        Parsed configuration containing MCP server definitions.
    """
    with open(config_path, "r") as f:
        return json.load(f)
    
def initialize_llm():
    """
    Initialize and return the LLM used by the agent.

    Returns
    -------
    ChatGroq
        Configured Groq chat model instance.
    """
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0
    )
    return llm


# Instantiate the LLM once for reuse
llm = initialize_llm()

def print_message_contents(response):
    """
    Log only the relevant message contents produced during agent execution.

    This filters and prints:
    - HumanMessage
    - ToolMessage
    - AIMessage

    Parameters
    ----------
    response : dict
        Agent response object containing message history.
    """
    messages = response.get("messages", [])
    for msg in messages:
        if isinstance(msg, HumanMessage):
            logger.info(f"\n[Human]: {msg.content}")
        elif isinstance(msg, ToolMessage):
            logger.info(f"[Tool]: {msg.content}")
        elif isinstance(msg, AIMessage):
            logger.info(f"[AI]: {msg.content}")

async def process_user_query(agent):
    """
    Interactive loop that accepts user queries and invokes the agent.

    Parameters
    ----------
    agent
        LangChain agent instance configured with MCP tools.
    """
    while True:
        query = input("\nEnter your query (or 'exit'): ").strip()
        if query.lower() == "exit":
            logger.info("Exiting agent.")
            break

        try:
            # Invoke agent with proper message structure and thread context
            response = await agent.ainvoke(
                {"messages": [HumanMessage(content=query)]},
                {"configurable": {"thread_id": "1"}}
            )

            # Log only meaningful message outputs
            print_message_contents(response)

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            traceback.print_exc()

async def run_agent():
    """
    Connect to MCP servers via SSE, load available tools,
    initialize the agent, and start the user interaction loop.
    """
    config = load_mcp_config()
    mcp_servers = config.get("mcpServers", {})

    if not mcp_servers:
        logger.info("No MCP servers found in configuration.")
        return

    tools = []

    # Manage multiple async contexts safely
    # Since we are connecting to many servers, this ensures that if something crashes or when we finish, all connections are closed neatly and safely.
    # AsyncExitStack is a container that keeps track of every connection you open
    # If the program crashes, or when the function finishes, the stack automatically closes all servers them in reverse order. 
    # It prevents "memory leaks" or hanging connections.
    async with AsyncExitStack() as stack:
        # Loop through mcp_servers and the stack holds each connection.
        for server_name, server_info in mcp_servers.items():
            url = server_info.get("url")
            if not url:
                logger.error(f"Server {server_name} is missing a 'url' in config.")
                continue

            logger.info(f"Connecting to MCP server via HTTP: {server_name} ({url})")

            try:
                # Establish SSE connection
                # Opens a two-way communication pipe to the server.
                # read is for listening, and write is for talking.
                # enter_async_context - takes an async resource and registers it with the stack so it will be cleaned up later.
                read, write = await stack.enter_async_context(sse_client(url=url))

                # Create MCP client session using the pipes
                session = await stack.enter_async_context(ClientSession(read, write))
                await session.initialize()

                # Load tools exposed by the MCP server
                server_tools = await load_mcp_tools(session)

                for tool in server_tools:
                    tools.append(tool)
                    logger.info(f"Loaded tool: {tool.name} from server: {server_name}")
                
            except Exception as e:
                logger.error(f"Failed to connect to MCP server {server_name}: {e}")
                traceback.print_exc()

        if not tools:
            logger.info("No tools loaded from any MCP server.")
            return

        # Create agent with in-memory checkpointing
        agent = create_agent(llm, tools=tools, checkpointer=InMemorySaver())

        logger.info("Agent initialized with tools.")
        await process_user_query(agent)

async def main():
    """
    Application entry point for running the MCP-powered agent.
    """
    await run_agent()

if __name__ == "__main__":
    # Ensure output directory exists
    os.makedirs("markdowns", exist_ok=True)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nAgent stopped.")

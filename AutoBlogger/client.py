from logging_config import get_logger

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
from langchain_groq.chat_models import ChatGroq

from dotenv import load_dotenv
load_dotenv()

def load_mcp_config(config_path = './mcp_config.json'):
    with open(config_path, 'r') as f:
        return json.load(f)
    
def initialize_llm():
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0
    )
    return llm

llm = initialize_llm()

def print_message_contents(response):
    """
    Print only the content of HumanMessage, ToolMessage, and AIMessage objects.
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
    """Handle user input and display filtered message content."""
    while True:
        query = input("\nEnter your query (or 'exit'): ").strip()
        if query.lower() == "exit":
            logger.info("Exiting agent.")
            break

        try:
            # Run the agent with proper input format
            response = await agent.ainvoke({"messages": [HumanMessage(content=query)]})

            # Show only relevant messages
            print_message_contents(response)

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            traceback.print_exc()

async def run_agent():
    """Connect to MCP servers via SSE, load tools, and run the agent."""
    config = load_mcp_config()
    mcp_servers = config.get('mcpServers', {})
    if not mcp_servers:
        logger.info("No MCP servers found in configuration.")
        return
    
    tools = []

    async with AsyncExitStack() as stack:
        for server_name, server_info in mcp_servers.items():
            # CHANGE: Look for 'url' instead of 'command'
            url = server_info.get('url')
            if not url:
                logger.error(f"Server {server_name} is missing a 'url' in config.")
                continue

            logger.info(f"Connecting to MCP server via HTTP: {server_name} ({url})")

            try:
                # CHANGE: Establish SSE connection
                read, write = await stack.enter_async_context(sse_client(url=url))
                
                # Create and initialize session
                session = await stack.enter_async_context(ClientSession(read, write))
                await session.initialize()

                # Load tools from MCP server
                server_tools = await load_mcp_tools(session)

                for tool in server_tools:
                    tools.append(tool)
                    logger.info(f"Loaded tool: {tool.name} from server: {server_name}")
                
                logger.info(f"Loaded {len(server_tools)} tools from server: {server_name}")
            except Exception as e:
                logger.error(f"Failed to connect to MCP server {server_name}: {e}")
                traceback.print_exc()

        if not tools:
            logger.info("No tools loaded from any MCP server.")
            return

        # CHANGE: Use create_react_agent (modern way to handle tool-calling agents)
        agent = create_agent(llm, tools=tools)

        logger.info("Agent initialized with tools.")
        await process_user_query(agent)

async def main():
    """Initialize MCP client, connect, and run the agent."""
    await run_agent()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nAgent stopped.")
import asyncio
from contextlib import AsyncExitStack
import json
import os
import logging
import traceback

from mcp import ClientSession
from mcp.client.sse import sse_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv
load_dotenv()

def configure_logging():
    """Configure global logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s",
        datefmt="%I:%M:%S",
    )
    return logging.getLogger(__name__)

logger = configure_logging()

def load_mcp_config(config_path='./mcp_config.json'):
    with open(config_path, 'r') as f:
        return json.load(f)

def initialize_llm() -> ChatGoogleGenerativeAI:
    """Initialize Gemini LLM."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0,
        max_retries=3,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )

llm = initialize_llm()

def print_message_contents(response):
    """
    Print only the content of HumanMessage, ToolMessage, and AIMessage objects.
    """
    messages = response.get("messages", [])
    for msg in messages:
        if isinstance(msg, HumanMessage):
            print(f"\n[Human]: {msg.content}")
        elif isinstance(msg, ToolMessage):
            print(f"[Tool]: {msg.content}")
        elif isinstance(msg, AIMessage):
            print(f"[AI]: {msg.content}")

async def process_user_query(agent):
    """Handle user input and display filtered message content."""
    while True:
        query = input("\nEnter your query (or 'exit'): ").strip()
        if query.lower() == "exit":
            logger.info("Exiting agent.")
            break

        try:
            response = await agent.ainvoke({"messages": [HumanMessage(content=query)]})
            print_message_contents(response)
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            traceback.print_exc()

async def run_agent():
    """Connect to MCP server, load tools, create an agent, and handle user queries."""
    config = load_mcp_config()
    mcp_servers = config.get("mcpServers", {})
    if not mcp_servers:
        print("No MCP servers found in configuration.")
        return

    tools = []

    async with AsyncExitStack() as stack:
        for server_name, server_info in mcp_servers.items():
            print(f"Connecting to MCP server: {server_name}")

            # Using SSE client instead of stdio
            sse_url = server_info["sse_url"]  # e.g., http://localhost:8000/sse

            try:
                # Establish SSE connection
                read, write = await stack.enter_async_context(sse_client(url=sse_url))

                # Create MCP client session
                session = await stack.enter_async_context(ClientSession(read, write))
                await session.initialize()

                # Load tools from the MCP server
                server_tools = await load_mcp_tools(session)
                for tool in server_tools:
                    tools.append(tool)
                    print(f"Loaded tool: {tool.name} from server: {server_name}")

                print(f"Loaded {len(server_tools)} tools from server: {server_name}")

            except Exception as e:
                logger.error(f"Failed to connect to MCP server {server_name}: {e}")
                traceback.print_exc()

        if not tools:
            print("No tools loaded from any MCP server.")
            return

        agent = create_agent(llm, tools, debug=False)

        logger.info("Agent is ready to process requests.")
        await process_user_query(agent)

async def main():
    """Initialize MCP client, connect, and run the agent."""
    await run_agent()

if __name__ == "__main__":
    asyncio.run(main())

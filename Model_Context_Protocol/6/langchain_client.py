import asyncio
import os
import logging
import traceback

# === MCP imports ===
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# === LangChain imports ===
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

# === Environment and Logging Setup ===
from dotenv import load_dotenv
load_dotenv()

# ============================================================
# Logging Configuration
# ============================================================
def configure_logging():
    """Configure global logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s",
        datefmt="%I:%M:%S",
    )
    return logging.getLogger(__name__)

logger = configure_logging()

# ============================================================
# LLM Initialization
# ============================================================
def initialize_llm() -> ChatGoogleGenerativeAI:
    """Initialize Gemini LLM."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        max_retries=3,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )

# ============================================================
# MCP Server Configuration
# ============================================================
def get_server_parameters(command='python', server_script = "./server.py") -> StdioServerParameters:
    """Return MCP server configuration."""
    return StdioServerParameters(command=command, args=[server_script])

# ============================================================
# Response Parser
# ============================================================
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

# ============================================================
# Query Processor
# ============================================================
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

# ============================================================
# Agent Runner
# ============================================================
async def run_agent():
    """Connect to MCP server, load tools, create an agent, and handle user queries."""
    llm = initialize_llm()
    server_params = get_server_parameters()

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Load tools from MCP server
            tools = await load_mcp_tools(session)
            agent = create_agent(llm, tools, debug=False)

            logger.info("Agent is ready to process requests.")
            await process_user_query(agent)

# ============================================================
# Main Entrypoint
# ============================================================
async def main():
    """Initialize MCP client, connect, and run the agent."""
    await run_agent()

if __name__ == "__main__":
    asyncio.run(main())

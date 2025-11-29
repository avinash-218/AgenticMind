import asyncio
import os
import logging
import traceback
from typing import Optional
from contextlib import AsyncExitStack   # manage multiple async context managers
from dotenv import load_dotenv

# === MCP imports ===
from mcp import ClientSession, StdioServerParameters    # for MCP communication
from mcp.client.stdio import stdio_client               # stdio-based transport for MCP

# === LangChain imports ===
from langchain_core.messages import HumanMessage        # represents chat messages
from langchain_core.tools import StructuredTool         # tool abstraction in LangChain
from langchain_google_genai import ChatGoogleGenerativeAI  # Gemini model wrapper
from langchain.agents import create_agent               # create an agent that can use tools
from pydantic import BaseModel, Field                   # schema validation

# === Environment and Logging Setup ===
load_dotenv()   # load environment variables from .env file

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s",
    datefmt="%I:%M:%S",
)
logger = logging.getLogger(__name__)

# === Generic Schema for MCP Tools ===
class GenericInput(BaseModel):
    """Flexible input schema used by MCP tools within LangChain."""
    input: Optional[dict] = Field(
        default_factory=dict,
        description="Input arguments for the MCP tool (key-value pairs)."
    )

# === MCP–LangChain Bridge Class ===
class MCPLangChainClient:
    """Connects Gemini (via LangChain) with MCP tool servers."""

    def __init__(self):
        """Initialize Gemini model and prepare for MCP session setup."""
        self.exit_stack = AsyncExitStack()   # manage async contexts for MCP connections
        self.session: Optional[ClientSession] = None
        self.tools = []

        # Retrieve API key from environment
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("Error: GEMINI_API_KEY environment variable not set.")

        # Initialize Gemini model client through LangChain
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-001",
            google_api_key=gemini_api_key,
            temperature=0.7,
        )

    async def connect_to_mcp(self, server_script_path: str):
        """
        Connect to an MCP tool server and load all available tools.
        The MCP server exposes callable tools over stdio.
        """
        # Choose interpreter based on file type
        command = "python" if server_script_path.endswith(".py") else "node"
        params = StdioServerParameters(command=command, args=[server_script_path])

        # Establish stdio connection and create client session
        self.stdio, self.write = await self.exit_stack.enter_async_context(stdio_client(params))
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()   # perform handshake with MCP server

        # Fetch list of available tools
        response = await self.session.list_tools()
        logger.info("Connected to MCP server. Tools available:")
        for tool in response.tools:
            logger.info(f"  - {tool.name}: {tool.description}")

        # Convert each MCP tool into a LangChain StructuredTool
        self.tools = []
        for t in response.tools:
            async_func = self._wrap_mcp_tool(t.name)

            tool = StructuredTool.from_function(
                func=async_func,
                name=t.name,
                description=t.description or "No description provided",
                args_schema=GenericInput,   # ensure Gemini gets valid schema
                coroutine=async_func,       # async function binding
            )
            self.tools.append(tool)

    def _wrap_mcp_tool(self, tool_name: str):
        """
        Wrap an MCP tool in an async function callable by LangChain.
        Handles argument formatting and safe result normalization.
        """
        async def call_tool(*args, **kwargs):
            try:
                # LangChain often passes {"input": {...}}; unwrap it if needed
                if args and not kwargs:
                    if isinstance(args[0], dict):
                        kwargs = args[0]
                    else:
                        kwargs = {"input": args[0]}

                # Flatten "input" dictionary for MCP compatibility
                if "input" in kwargs and isinstance(kwargs["input"], dict):
                    arguments = kwargs["input"]
                else:
                    arguments = kwargs

                logger.info(f"Invoking MCP tool '{tool_name}' with args: {arguments}")
                result = await self.session.call_tool(name=tool_name, arguments=arguments)

                # Safely normalize and extract content from the MCP result
                if hasattr(result, "content"):
                    content_list = []
                    for item in result.content:
                        if hasattr(item, "text"):
                            content_list.append(item.text)
                        elif hasattr(item, "__dict__"):
                            content_list.append(item.__dict__)
                        else:
                            content_list.append(str(item))
                    return "\n".join(map(str, content_list))

                elif hasattr(result, "output"):
                    return str(result.output)

                else:
                    return str(result)

            except Exception as e:
                logger.error(f"Error calling {tool_name}: {e}")
                logger.debug(traceback.format_exc())
                return f"Error invoking tool {tool_name}: {e}"

        return call_tool

    async def run_chat(self):
        """
        Launch interactive chat loop.
        Gemini will respond naturally and invoke MCP tools when needed.
        """
        if not self.tools:
            raise RuntimeError("No MCP tools loaded. Did you call connect_to_mcp()?")

        # System instruction for the AI agent
        system_prompt = "You are an intelligent assistant that uses available tools when helpful."
        agent = create_agent(model=self.llm, tools=self.tools, system_prompt=system_prompt)

        logger.info("Chat started. Type 'exit' to quit.")
        while True:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in {"exit", "quit"}:
                logger.info("Exiting chat.")
                break

            try:
                # Forward user message to Gemini agent
                result = await agent.ainvoke({"messages": [HumanMessage(content=user_input)]})

                # Handle response variants returned by LangChain agent
                if isinstance(result, dict):
                    if "output" in result:
                        print(f"\nAI: {result['output']}")
                    elif "messages" in result and result["messages"]:
                        ai_msg = result["messages"][-1].content
                        print(f"\nAI: {ai_msg}")
                    else:
                        print("\nAI: [No output detected]")
                else:
                    print(f"\nAI: {result}")

            except Exception as e:
                logger.error(f"Error: {e}")
                logger.debug(traceback.format_exc())

    async def cleanup(self):
        """Close all async contexts and free resources."""
        await self.exit_stack.aclose()


# === Main entrypoint ===
async def main(server_script_path="server.py"):
    """Initialize MCP client, connect, run chat, and clean up."""
    client = MCPLangChainClient()
    try:
        await client.connect_to_mcp(server_script_path)
        await client.run_chat()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

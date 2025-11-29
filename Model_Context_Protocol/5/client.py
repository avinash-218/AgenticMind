import asyncio
import os
import sys
import json

import traceback
from typing import Optional
from contextlib import AsyncExitStack   # for managing multiple async context managers

from mcp import ClientSession, StdioServerParameters    # MCP session management
from mcp.client.stdio import stdio_client   # stdio client for MCP

from google import genai
from google.genai import types  # structure AI response
from google.genai.types import Tool, FunctionDeclaration, GenerateContentConfig

from dotenv import load_dotenv
load_dotenv()

import logging
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s",
    datefmt="%I:%M:%S")
logger = logging.getLogger(__name__)

## Helper functions to convert MCP tools to Gemini AI Tool format
def clean_schema(schema):
    """Clean the mcp tool input schema for Gemini compatibility."""
    if isinstance(schema, dict):
        schema.pop("title", None)   # remove title if present

        # recursively clean nested schemas which are dicts of properties
        if "properties" in schema and isinstance(schema["properties"], dict):
            for prop in schema["properties"]:
                schema["properties"][prop] = clean_schema(schema["properties"][prop])

    return schema

def convert_mcp_tools_to_gemini(mcp_tools):
    """Convert MCP tools to Gemini AI Tool format for compatibility."""
    gemini_tools = []

    for mcp_tool in mcp_tools:
        params = clean_schema(mcp_tool.inputSchema)    # clean input schema for Gemini compatibility

        function_declaration = FunctionDeclaration( # create gemini function declaration from MCP tool
            name=mcp_tool.name,
            description=mcp_tool.description,
            parameters=params
        )

        gemini_tools.append(Tool(function_declarations=[function_declaration]))   # create Gemini Tools

    return gemini_tools

## MCP Client class to manage communication with MCP server and Gemini AI
class MCPClient:
    def __init__(self):
        """Initialize MCP client and Gemini AI client."""
        self.session: Optional[ClientSession] = None    # MCP client session for communication
        self.exit_stack = AsyncExitStack()   # manage async resource cleanup

        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("Error: GEMINI_API_KEY environment variable not set.")
        
        self.genai_client = genai.Client(api_key=gemini_api_key)   # Gemini AI client

    async def connect_to_server(self, server_script_path: str):
        """Connect to MCP server and list all available tools."""
        command = "python" if server_script_path.endswith(".py") else "node"

        #define parameters for stdio server
        server_params = StdioServerParameters(command=command, args=[server_script_path])

        # establish communication session with MCP server using stdio and get read and write streams
        self.stdio, self.write = await self.exit_stack.enter_async_context(stdio_client(server_params))

        # create MCP client session
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()   # send initialization request to server

        response = await self.session.list_tools()   # request list of tools from server
        logger.info("Available tools from server:")
        tools = response.tools
        for tool in tools:
            logger.info(f"- {tool.name}")

        # convert the MCP tools in Gemini AI Tool format
        self.gemini_tools = convert_mcp_tools_to_gemini(tools)

    async def process_query(self, query: str)-> str:
        """Process user query using Gemini AI and use MCP tools if needed."""
        # format user prompt for Gemini AI compatibility
        user_prompt_content = types.Content(
            role='user',    # indicate user role
            parts=[types.Part(text=query)] # user query as text part
        )

        # send user prompt to Gemini AI with tool definitions
        response = self.genai_client.models.generate_content(
            model="gemini-2.0-flash-001",   # Gemini model
            contents=[user_prompt_content],   # user prompt
            config=types.GenerateContentConfig(   # generation config
                tools=self.gemini_tools,   # provide tool definitions
            )
        )

        # extract and return the generated text response
        final_text = []

        for candidate in response.candidates:   # process each candidate response
            if candidate.content.parts:  # check if content parts exist
                for part in candidate.content.parts:    # iterate through content parts
                    if isinstance(part, types.Part):    
                        if part.function_call:  # check if part is a function call
                            function_call_part = part
                            tool_name = function_call_part.function_call.name   # extract tool name
                            tool_args = function_call_part.function_call.args   # extract tool arguments

                            logger.info(f"Invoking tool: {tool_name} with args: {tool_args}")

                            try:    # invoke the MCP tool
                                result = await self.session.call_tool(  # invoke MCP tool with extracted name and args
                                    name=tool_name,
                                    arguments=tool_args
                                )
                                logger.info("Raw tool result: %s", result)
                                
                                # Safely extract tool output (handle string, dict, or object)
                                tool_output = (
                                    getattr(result, "content", None)
                                    or getattr(result, "output", None)
                                    or (result if isinstance(result, (str, dict)) else str(result))
                                )

                                function_response = {"result": tool_output}
                                logger.info("Parsed tool output: %s", tool_output)

                            except Exception as e:
                                logger.error("Error invoking tool %s: %s", tool_name, e)
                                logger.debug("Traceback:\n%s", traceback.format_exc())
                                function_response = {"error": f"Error invoking tool {tool_name}: {str(e)}"}

                            # format tool response for Gemini AI compatibility
                            function_response_part = types.Part.from_function_response(
                                name=tool_name,
                                response=function_response
                            )

                            # structure tool response content for Gemini AI
                            function_response_content = types.Content(
                                role='tool',   # indicate function role
                                parts=[function_response_part]  # tool response part
                            )

                            # send tool response back to Gemini AI for final answer generation
                            follow_up_response = self.genai_client.models.generate_content(
                                model="gemini-2.0-flash-001",   # Gemini model
                                contents=[
                                    user_prompt_content,   # original user prompt
                                    function_call_part,   # original function call part
                                    function_response_content   # tool response content
                                ],
                                config=types.GenerateContentConfig(
                                    tools=self.gemini_tools,   # provide tool definitions
                                ),
                            )

                            # extract final answer from follow-up response
                            final_text.append(follow_up_response.candidates[0].content.parts[0].text)
                        else:
                            final_text.append(part.text)  # direct text response (no tool invocation)

        return "\n".join(final_text)  # combine all text parts into final response
    
    async def chat_loop(self):
        """Run chat loop to interact with user."""
        logger.info("You can start chatting with the AI now. Type 'exit' to quit.")
        
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                logger.info("Exiting chat.")
                break
            
            response = await self.process_query(user_input)   # process user query
            logger.info(f"AI: {response}")   # display AI response

    async def cleanup(self):
        """Cleanup resources."""
        await self.exit_stack.aclose()   # close all async context managers

async def main(server_script_path ='server.py'):
    client = MCPClient()
    try:
        await client.connect_to_server(server_script_path)   # connect to MCP server
        await client.chat_loop()   # start chat loop
    finally:
        await client.cleanup()   # cleanup resources

if __name__ == "__main__":
    asyncio.run(main())   # run main function in event loop
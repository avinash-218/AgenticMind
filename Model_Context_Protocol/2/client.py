from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()
import asyncio
import os
os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
    
async def main():
    client = MultiServerMCPClient(
        {
            "math": {
                "command":"python",
                "args":["mathserver.py"],
                "transport":"stdio"
            },
            "weather": {
                "url":"http://localhost:8000/mcp",
                "transport":"streamable_http"
            },
        }
    )
    
    tools = await client.get_tools()
    model = ChatGroq(model='qwen/qwen3-32b')
    agent = create_react_agent(model, tools, debug=True)

    math_response = await agent.ainvoke({
        "messages": [{"role":"user", "content":"What's (3+5) x 12 ?"}]
    })

    print(f"\n\nMath Response: {math_response['messages'][-1].content}")

    weather_response = await agent.ainvoke({
        "messages": [{"role":"user", "content":"What's the weather in madurai?"}]
    })

    print(f"Weather Response: {weather_response['messages'][-1].content}")

if __name__ == "__main__":
    asyncio.run(main())

from pydoc import cli
from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq
from mcp_use import MCPAgent, MCPClient

import asyncio

async def run_memory_chat():
    # Run a chat using MCP Agent's built in conversational memory

    config = 'flight_assistant.json'
    
    print('Initializing chat...')

    # create MCP client
    client = MCPClient.from_config_file(config)
    llm = ChatGroq(model='llama-3.1-8b-instant')

    # create MCP agent
    agent = MCPAgent(
        llm=llm,
        client=client,
        # verbose=True,
        max_steps=15,
        memory_enabled=True # enable built-in conversational memory
    )
    print('\n Interactive MCP Chat')
    print('Type "quit" or "exit" to exit')
    print('Type "clear" to clear the chat history')

    try:
        while True:
            user_input = input('User: ')

            if user_input.lower() in ['quit', 'exit']:
                print('Ending Conversation...')
                break

            if user_input.lower() == 'clear':
                agent.clear_conversation_history()
                print('Conversation history cleared.')
                continue

            # Get response from Agent
            print('\nAssistant: ', end="", flush=True)

            try:
                response = await agent.run(user_input) # run the agent with user input (with memory handling)
                print(response)
            except Exception as e:
                print(f"\nError: {e}")

    finally:
        if client and client.sessions:
            await client.close_all_sessions()

if __name__ == '__main__':
    asyncio.run(run_memory_chat())
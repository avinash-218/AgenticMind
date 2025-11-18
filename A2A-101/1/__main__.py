import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import GreetingAgentExecutor

def main():
    skill = AgentSkill(
        id='hello_world',   # skill id
        name='Greet',   # skill name
        description='Returns a greeting message.',  # skill description
        tags=['greeting', 'hello'], # skill tags
        examples=["Hey", "Hello there!", "Hi"]  # skill examples
    )

    agent_card = AgentCard(
        name="Greeting Agent",  # agent name
        description="A simple agent that returns a greeting message.",  # agent description
        url="localhost:9999/",  # agent URL
        default_input_modes=["text"],   # agent input modes
        default_output_modes=["text"],  # agent output modes
        skills=[skill], # agent skills
        version="1.0.0",    # agent version
        capabilities=AgentCapabilities(), # agent capabilities
    )

    request_handler = DefaultRequestHandler(
        agent_executor=GreetingAgentExecutor(),
        task_store=InMemoryTaskStore()
    )
    
    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card
    )

    uvicorn.run(server.build(), host="0.0.0.0", port=9999)

if __name__ == "__main__":
    main()
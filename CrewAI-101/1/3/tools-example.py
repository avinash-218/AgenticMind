from typing import Type
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool

llm=LLM(model="ollama/llama3:8b", base_url="http://localhost:11434")

# Define the input schema for the calculator tool
class CalculatorInput(BaseModel):
    equation: str = Field(..., description="Mathematical equation to solve.")

# Define the custom calculator tool
class CalculatorTool(BaseTool):
    name: str = "Calculator"
    description: str = "Solves mathematical equations."
    args_schema: Type[BaseModel] = CalculatorInput

    def _run(self, equation: str) -> str:
        try:
            result = eval(equation)
            return str(result)
        except Exception as e:
            return f"Error: {e}"

# Instantiate the custom calculator tool
calc_tool = CalculatorTool()

# User input
math_input = input("Enter math equation: ")

# Define the agent with the custom tool
math_agent = Agent(
    role="Math Wizard",
    goal="Solve any mathematical equation accurately.",
    backstory="You are the best mathematician in the world, capable of solving any equation with precision.",
    verbose=True,
    tools=[calc_tool],
    llm=llm
)

# Writer agent
writer = Agent(
    role="Writer",
    goal="Craft compelling explanations based on the results of math equations.",
    backstory="You are a renowned content strategist, known for your insightful and engaging articles.",
    llm=llm
)

# Define tasks
task1 = Task(
    description=f"Solve: {math_input}",
    expected_output="Provide the correct numerical result.",
    agent=math_agent
)

task2 = Task(
    description="Using the result, explain how the equation was solved step by step.",
    expected_output="Detailed explanation in markdown format.",
    output_file="math.md",
    agent=writer
)

# Create and run the Crew
crew = Crew(
    agents=[math_agent, writer],
    tasks=[task1, task2],
    process=Process.sequential,
    verbose=True
)

results = crew.kickoff()
print(results)
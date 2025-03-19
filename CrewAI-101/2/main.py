from crewai import LLM, Agent, Task, Crew

llm=LLM(model="ollama/llama3:8b", base_url="http://localhost:11434")

info_agent = Agent(
    role="Information Agent",
    goal="Give compelling information about a certain topic",
    backstory="""You love to know information. People love and hate you for it. You win most of the quizzes at your local pub""",
    llm=llm
)

task1 = Task(
    description="Tell me all about the blue-ringed octopus",
    expected_output="Give me a quick summary and then also give me a 7 bullet points descripbing it.",
    agent=info_agent
)

crew = Crew(
    agents=[info_agent],
    tasks=[task1],
    verbose=True
)

result = crew.kickoff()

print('#'*20)
print(result)
from crewai import Crew, Process
from agents import blog_writer, blog_researcher
from tasks import research_task, write_task

crew = Crew(
    agents=[blog_researcher, blog_writer],
    tasks=[research_task, write_task],
    process=Process.sequential, # Sequential task execution
    memory=True,
    cache=True,
    max_rpm=100,
    share_crew=True
)

# Start the task execution process with enhanced feedback
result = crew.kickoff(inputs={'topic':'AI V ML VS DL VS Data Science'})
print(result)
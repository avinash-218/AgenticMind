from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import PDFSearchTool

pdf_search_tool = PDFSearchTool(
    pdf='./Avinash_R_Resume.pdf',
    config=dict(
        llm=dict(
            provider="ollama",
            config=dict(
                model="gpt-oss:latest",
            ),
        ),
        embedder=dict(
            provider="ollama",
            config=dict(
                model="nomic-embed-text:latest",
            ),
        ),
    )
)

@CrewBase
class PdfRag():
    """PdfRag crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    ollama_llm = LLM(
        model='ollama/gpt-oss:latest',
        base_url='http://localhost:11434'
    )

    @agent
    def pdf_rag_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['pdf_rag_agent'],
            verbose=True,
            llm = self.ollama_llm,
            tools=[pdf_search_tool]
        )
    
    @agent
    def pdf_summary_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['pdf_summary_agent'],
            verbose=True,
            llm = self.ollama_llm
        )

    @task
    def pdf_rag_task(self) -> Task:
        return Task(
            config=self.tasks_config['pdf_rag_task'],
        )

    @task
    def pdf_summary_task(self) -> Task:
        return Task(
            config=self.tasks_config['pdf_summary_task'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the PdfRag crew"""

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )

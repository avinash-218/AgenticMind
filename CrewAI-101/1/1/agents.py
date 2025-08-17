from crewai import LLM, Agent
from tools import yt_tool

llm=LLM(model="ollama/llama3:8b", base_url="http://localhost:11434")

# create a senior blog content researcher
blog_researcher = Agent(
    role='Blog Researcher from Youtube videos',
    goal='get the relevant video content for the topic {topic} from the YT channel',
    name='Senior Blog Content Researcher',
    description='A senior blog content researcher from Youtube videos',
    verbose=True,
    memory=True,
    backstory=(
        "Expert in understanding videos in AI, Data Science, Machine Learning and Gen AI and providing suggestion"
    ),
    tools=[yt_tool],
    allow_delegation=True,   #transfer the work done by agent to someone else
    llm=llm
)

# create a senior writer agent with YT tool
blog_writer = Agent(
    role = 'Blog Writer',
    goal='Narrate compelling tech stories about the video {topic} from YT channel',
    verbose=True,
    memory=True,
    backstory=(
        "With a flair for simplifying complex topics you craft"
        "engaging narratives that captivate and educate, bringing new"
        "discoveries to light in an accessible manner."
    ),
    tools=[yt_tool],
    allow_delegation=False,
    llm=llm
)
#!/usr/bin/env python
import sys
import warnings
sys.path.append('.')

from src.news_scrapper.crew import NewsScrapper
from datetime import datetime

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'topic': 'AI LLMs',
        "date": datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    }

    inputs_array = [
        {
            "topic": "AI Agents",
            "date": datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        },
        {
            "topic": "Model Context Protocol",
            "date": datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        },
        {
            "topic": "Agent to Agent Communication",
            "date": datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        }
    ]
    
    NewsScrapper().crew().kickoff(inputs=inputs)

run()
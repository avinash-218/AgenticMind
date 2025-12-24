from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import os
import sys

# Extend Python path to allow absolute imports from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import the LangGraph workflow and visualization utility
from server_src.content_creation.graph.graph import content_graph
from server_src.content_creation.utils import draw_stylish_graph

if __name__ == "__main__":
    # draw_stylish_graph(content_graph, output_name="content_graph")

    # Invoke the content creation graph with input parameters
    result = content_graph.invoke(
        input={"title": "Artificial General Intelligence"}
    )

    # Handle successful content generation
    if result.get("content"):
        print(
            f"Status: Success\n"
            f"Title: {result.get('title')}\n"
            f"Content:\n{result.get('content')}"
        )
    else:
        # Handle failure case with exit reason
        print(
            f"Status: Failed\n"
            f"Reason: {result.get('exit_reason')}"
        )

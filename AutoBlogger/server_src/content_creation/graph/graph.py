"""

# Load environment variables required by downstream nodes (LLMs, APIs, etc.)
Defines and compiles the LangGraph workflow for automated content creation.

This graph orchestrates the full pipeline:
- Hint and link extraction
- Validation steps with conditional routing
- Keyword generation and web search
- Context compilation
- Final content writing
- Graceful exit handling on validation failures
"""

from dotenv import load_dotenv

# Load environment variables required by downstream nodes (LLMs, APIs, etc.)
load_dotenv()

from langgraph.graph import START, END, StateGraph
from server_src.content_creation.graph.state import ContentState
from server_src.content_creation.graph.nodes import *

# Initialize the stateful LangGraph with ContentState
graph = StateGraph(ContentState)

# Register all processing nodes
# Each node represents a discrete step in the content pipeline
graph.add_node("fetch_hints_links", fetch_hints_links)
graph.add_node("validate_hints", validate_title_vs_hints)
graph.add_node("extract_links_content", extract_links_content)
graph.add_node("validate_links", validate_title_vs_links)
graph.add_node("gen_keywords", generate_keywords)
graph.add_node("web_search", web_search)
graph.add_node("compile_context", compile_context)
graph.add_node("write_content", write_content)
graph.add_node("exit", exit_node)

# Define linear execution flow
graph.add_edge(START, "fetch_hints_links")
graph.add_edge("fetch_hints_links", "validate_hints")

# Conditional routing after hint validation
# Either exit early or continue to link extraction
graph.add_conditional_edges(
    "validate_hints",
    route_after_validate_hints,
    {
        "exit": "exit",
        "extract_links_content": "extract_links_content",
    }
)

# Continue flow with link extraction and validation
graph.add_edge("extract_links_content", "validate_links")

# Conditional routing after link validation
# Either exit early or proceed to keyword generation
graph.add_conditional_edges(
    "validate_links",
    route_after_validate_links,
    {
        "exit": "exit",
        "gen_keywords": "gen_keywords",
    }
)

# Final content generation pipeline
graph.add_edge("gen_keywords", "web_search")
graph.add_edge("web_search", "compile_context")
graph.add_edge("compile_context", "write_content")
graph.add_edge("write_content", END)

# Exit node always terminates the graph
graph.add_edge("exit", END)

# Compile the graph into an executable LangGraph object
content_graph = graph.compile()

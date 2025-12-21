from dotenv import load_dotenv
load_dotenv()
from langgraph.graph import START, END, StateGraph
from server_src.content_creation.graph.state import ContentState
from server_src.content_creation.graph.nodes import *

graph = StateGraph(ContentState)

graph.add_node("fetch_hints_links", fetch_hints_links)
graph.add_node("validate_hints", validate_title_vs_hints)
graph.add_node("extract_links_content", extract_links_content)
graph.add_node("validate_links", validate_title_vs_links)
graph.add_node("gen_keywords", generate_keywords)
graph.add_node("web_search", web_search)
graph.add_node("compile_context", compile_context)
graph.add_node("write_content", write_content)
graph.add_node("exit", exit_node)

graph.add_edge(START, "fetch_hints_links")
graph.add_edge("fetch_hints_links", "validate_hints")

graph.add_conditional_edges(
    "validate_hints",
    route_after_validate_hints,
    {
        "exit": "exit",
        "extract_links_content": "extract_links_content",
    }
)
graph.add_edge("extract_links_content", "validate_links")

graph.add_conditional_edges(
    "validate_links",
    route_after_validate_links,
    {
        "exit": "exit",
        "gen_keywords": "gen_keywords",
    }
)

graph.add_edge("gen_keywords", "web_search")
graph.add_edge("web_search", "compile_context")
graph.add_edge("compile_context", "write_content")
graph.add_edge("write_content", END)

graph.add_edge("exit", END)

content_graph = graph.compile()

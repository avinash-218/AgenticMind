from graphviz import Digraph
from langchain_groq.chat_models import ChatGroq
from langchain_ollama.chat_models import ChatOllama
from server_src.content_creation.configs.configs import ConfigLoader

def draw_stylish_graph(langgraph, output_name="content_graph"):
    """
    Render a styled Graphviz visualization for a LangGraph workflow.

    This function converts a LangGraph object into a visually structured
    directed graph with semantic styling applied to different node types
    (start, validation, exit, and regular processing nodes).

    The output is saved as a PNG file using Graphviz.

    Args:
        langgraph: LangGraph instance containing nodes and edges.
        output_name (str): Base filename for the rendered graph output
                           (without extension).

    Returns:
        graphviz.Digraph: The rendered Graphviz Digraph object.
    """
    # Initialize Graphviz directed graph
    dot = Digraph(
        name="ContentCreationGraph",
        format="png",
        engine="dot"
    )

    # Global graph-level styling
    dot.attr(
        rankdir="TB",        # Top-to-bottom layout
        bgcolor="white",
        fontname="Inter",
        fontsize="12",
        labelloc="t",
    )

    # Default node styling
    dot.attr(
        "node",
        shape="rect",
        style="rounded,filled",
        fontname="Inter",
        fontsize="11",
        color="#4B5563",
        fillcolor="#F9FAFB"
    )

    # Default edge styling
    dot.attr(
        "edge",
        color="#6B7280",
        arrowsize="0.7",
        penwidth="1.2"
    )

    # Extract internal graph structure from LangGraph
    g = langgraph.get_graph()

    # Define node categories for semantic styling
    validation_nodes = {"validate_hints", "validate_links"}
    exit_nodes = {"exit"}

    # Add nodes with category-specific styling
    for node in g.nodes:
        # Validation decision nodes
        if node in validation_nodes:
            dot.node(
                node,
                node.replace("_", "\n"),
                shape="diamond",
                fillcolor="#FEF3C7",   # amber
                color="#D97706"
            )

        # Exit / failure node
        elif node in exit_nodes:
            dot.node(
                node,
                "EXIT",
                shape="octagon",
                fillcolor="#FEE2E2",   # red
                color="#DC2626"
            )

        # Graph start node
        elif node == "__start__":
            dot.node(
                node,
                "START",
                shape="oval",
                fillcolor="#DCFCE7",   # green
                color="#16A34A"
            )

        # Standard processing nodes
        else:
            dot.node(
                node,
                node.replace("_", "\n"),
                fillcolor="#E0F2FE",   # blue
                color="#0284C7"
            )

    # Add edges between nodes
    for edge in g.edges:
        src = edge.source
        dst = edge.target

        # Highlight failure paths leading to exit
        if dst == "exit":
            dot.edge(src, dst, label="fail", color="#DC2626")
        else:
            dot.edge(src, dst)

    # Render graph to disk and clean up intermediate files
    dot.render(output_name, cleanup=True)

    return dot

def initialize_llm():
    """
    Initialize and return the chat language model.

    The model is configured with deterministic output (temperature = 0)
    to ensure consistent, repeatable blog generation.

    Returns:
        Chat Model: Initialized language model instance.
    """
    config_data = ConfigLoader()    # load config yaml file

    # create llm instance as per configuration
    if config_data['LLM_PROVIDER'] == 'groq':
        llm = ChatGroq(
            model=config_data['LLM_NAME'],
            temperature=0
        )
    elif config_data['LLM_PROVIDER'] == 'ollama':
        llm = ChatOllama(
            model=config_data['LLM_NAME'],
            temperature=0
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {config_data['LLM_PROVIDER']} and / or name: {config_data['LLM_NAME']}")

    return llm

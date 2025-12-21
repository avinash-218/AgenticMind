from graphviz import Digraph

def draw_stylish_graph(langgraph, output_name="content_graph"):
    dot = Digraph(
        name="ContentCreationGraph",
        format="png",
        engine="dot"
    )

    # Global graph styling
    dot.attr(
        rankdir="TB",
        bgcolor="white",
        fontname="Inter",
        fontsize="12",
        labelloc="t",
    )

    # Default node style
    dot.attr(
        "node",
        shape="rect",
        style="rounded,filled",
        fontname="Inter",
        fontsize="11",
        color="#4B5563",
        fillcolor="#F9FAFB"
    )

    # Default edge style
    dot.attr(
        "edge",
        color="#6B7280",
        arrowsize="0.7",
        penwidth="1.2"
    )

    g = langgraph.get_graph()

    # ---- Node categories ----
    validation_nodes = {"validate_hints", "validate_links"}
    exit_nodes = {"exit"}

    # ---- Add nodes ----
    for node in g.nodes:
        if node in validation_nodes:
            dot.node(
                node,
                node.replace("_", "\n"),
                shape="diamond",
                fillcolor="#FEF3C7",   # amber
                color="#D97706"
            )

        elif node in exit_nodes:
            dot.node(
                node,
                "EXIT",
                shape="octagon",
                fillcolor="#FEE2E2",   # red
                color="#DC2626"
            )

        elif node == "__start__":
            dot.node(
                node,
                "START",
                shape="oval",
                fillcolor="#DCFCE7",   # green
                color="#16A34A"
            )

        else:
            dot.node(
                node,
                node.replace("_", "\n"),
                fillcolor="#E0F2FE",   # blue
                color="#0284C7"
            )

    for edge in g.edges:
        src = edge.source
        dst = edge.target

        if dst == "exit":
            dot.edge(src, dst, label="fail", color="#DC2626")
        else:
            dot.edge(src, dst)

    dot.render(output_name, cleanup=True)
    return dot


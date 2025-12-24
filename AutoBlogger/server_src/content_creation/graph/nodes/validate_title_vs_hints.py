from logging_config import get_logger

logger = get_logger("ContentCreationServer")
from server_src.content_creation.graph.state import ContentState
from server_src.content_creation.graph.chains.relevancy_grader_chain import relevance_grader

def validate_title_vs_hints(state: ContentState):
    """
    Validate semantic relevance between the title and user-provided hints.

    This node checks whether the optional user hints are overall relevant
    to the requested title using an LLM-based relevance grader.

    Behavior:
    - If no hints are provided, the validation is skipped and treated as valid.
    - If hints are provided and deemed irrelevant, the graph exits early.
    - If relevant, execution continues to the next node.

    Args:
        state (ContentState): Current graph state containing the title
                              and optional user hints.

    Returns:
        dict:
            - {"title_hints_relevant": True} if validation passes
            - {"title_hints_relevant": False, "exit_reason": str} if validation fails
    """
    logger.info("--- VALIDATE TITLE VS HINTS ---")

    # Guard: no hints provided (hints are optional)
    if not state.user_hints:
        logger.info("No user hints provided; skipping relevance check")
        return {"title_hints_relevant": True}

    # Combine hints into a single block for relevance grading
    combined_hints = "\n".join(f"- {h}" for h in state.user_hints)

    # Invoke relevance grader
    decision = relevance_grader.invoke(
        {
            "title": state.title,
            "content": combined_hints
        }
    )

    logger.info(
        f"Relevance decision for title vs hints: "
        f"relevant={decision.relevant}, reason={decision.reason}"
    )

    # Handle relevance decision
    if not decision.relevant:
        logger.warning("User hints are not relevant to the title")
        return {
            "title_hints_relevant": False,
            "exit_reason": decision.reason
        }

    logger.info("User hints are relevant to the title")
    return {
        "title_hints_relevant": True
    }

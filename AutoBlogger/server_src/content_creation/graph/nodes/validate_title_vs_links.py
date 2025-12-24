from logging_config import get_logger
logger = get_logger("ContentCreationServer")

from server_src.content_creation.graph.state import ContentState
from server_src.content_creation.graph.chains.relevancy_grader_chain import relevance_grader

def validate_title_vs_links(state: ContentState):
    """
    Validate semantic relevance between the title and extracted link contents.

    This node evaluates whether the content extracted from user-provided
    links is overall relevant to the requested title using an LLM-based
    relevance grader.

    Behavior:
    - If no link content is available, validation is skipped and treated as valid.
    - If link content is present and deemed irrelevant, the graph exits early.
    - If relevant, execution continues to the next stage.

    Args:
        state (ContentState): Current graph state containing the title
                              and extracted link content.

    Returns:
        dict:
            - {"title_links_relevant": True} if validation passes
            - {"title_links_relevant": False, "exit_reason": str} if validation fails
    """
    logger.info("--- VALIDATE TITLE VS LINKS ---")

    # Guard: no link content extracted (links are optional)
    if not state.link_contents:
        logger.info("No link contents available; skipping relevance check")
        return {"title_links_relevant": True}

    # Invoke relevance grader
    decision = relevance_grader.invoke(
        {
            "title": state.title,
            "content": state.link_contents
        }
    )

    logger.info(
        f"Relevance decision for title vs links: "
        f"relevant={decision.relevant}, reason={decision.reason}"
    )

    # Handle relevance decision
    if not decision.relevant:
        logger.warning("Extracted link contents are not relevant to the title")
        return {
            "title_links_relevant": False,
            "exit_reason": decision.reason
        }

    logger.info("Extracted link contents are relevant to the title")
    return {
        "title_links_relevant": True
    }

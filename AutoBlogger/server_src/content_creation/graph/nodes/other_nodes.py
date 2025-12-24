from logging_config import get_logger

logger = get_logger("ContentCreationServer")
from server_src.content_creation.graph.state import ContentState

def route_after_validate_hints(state: ContentState) -> str:
    """
    Determine the next graph node after title ↔ user hints validation.

    If the hints are deemed irrelevant to the title, the graph exits early.
    Otherwise, execution continues to link content extraction.

    Args:
        state (ContentState): Current graph state containing the
                              title-hints relevance flag.

    Returns:
        str: Name of the next node to execute ("exit" or "extract_links_content").
    """
    logger.info("--- ROUTING AFTER HINTS VALIDATION ---")

    if state.title_hints_relevant is False:
        logger.warning("Title and user hints are not relevant; routing to exit")
        return "exit"

    logger.info("Hints are relevant; continuing to link content extraction")
    return "extract_links_content"

def route_after_validate_links(state: ContentState) -> str:
    """
    Determine the next graph node after title ↔ link content validation.

    If the extracted link content is deemed irrelevant to the title,
    the graph exits early. Otherwise, execution proceeds to keyword
    generation.

    Args:
        state (ContentState): Current graph state containing the
                              title–link relevance flag.

    Returns:
        str: Name of the next node to execute ("exit" or "gen_keywords").
    """
    logger.info("--- ROUTING AFTER LINK CONTENT VALIDATION ---")

    if state.title_links_relevant is False:
        logger.warning("Title and link contents are not relevant; routing to exit")
        return "exit"

    logger.info("Link contents are relevant; continuing to keyword generation")
    return "gen_keywords"

def exit_node(state: ContentState):
    """
    Terminal node for early graph termination.

    This node is invoked when a validation step fails. It ensures the
    graph exits cleanly and returns a standardized failure response
    containing a human-readable reason.

    Args:
        state (ContentState): Current graph state containing an optional
                              exit reason.

    Returns:
        dict:
            - content: None
            - exit_reason: Explanation for termination
    """
    logger.info("--- EXIT NODE ---")

    return {
        "content": None,
        "exit_reason": state.exit_reason or "Validation failed",
    }

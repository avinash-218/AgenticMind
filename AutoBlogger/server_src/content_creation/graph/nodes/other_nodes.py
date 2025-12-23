from logging_config import get_logger

logger = get_logger("ContentCreationServer")
from server_src.content_creation.graph.state import ContentState

def route_after_validate_hints(state: ContentState) -> str:
    """
    Routing after title ↔ hints validation.
    """
    logger.info('---Routing after Hints Validation---')
    if state.title_hints_relevant is False:
        return "exit"
    return "extract_links_content"

def route_after_validate_links(state: ContentState) -> str:
    """
    Routing after title ↔ link contents validation.
    """
    logger.info('---Routing after Link Content Validation---')
    if state.title_links_relevant is False:
        return "exit"
    return "gen_keywords"


def exit_node(state: ContentState):
    logger.info('--- Exit Node ---')
    return {
        "content": None,
        "exit_reason": state.exit_reason or "Validation failed",
    }

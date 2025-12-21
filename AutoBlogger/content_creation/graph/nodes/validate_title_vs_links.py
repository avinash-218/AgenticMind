from logging_config import get_logger

logger = get_logger("ContentCreationServer")
from content_creation.graph.state import ContentState
from content_creation.graph.chains.relevancy_grader_chain import relevance_grader

def validate_title_vs_links(state: ContentState):
    logger.info('--- Validate Title vs LINKS ---')

    # No link content extracted → consider relevant by default
    # (links are optional and extraction may fail gracefully)
    if not state.link_contents:
        return {"title_links_relevant": True}

    decision = relevance_grader.invoke(
        {
            "title": state.title,
            "content": state.link_contents
        }
    )

    logger.info("Relevance decision:", decision)

    if not decision.relevant:
        return {
            "title_links_relevant": False,
            "exit_reason": decision.reason
        }

    return {
        "title_links_relevant": True
    }

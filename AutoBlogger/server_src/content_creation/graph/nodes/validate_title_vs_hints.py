from logging_config import get_logger

logger = get_logger("ContentCreationServer")
from server_src.content_creation.graph.state import ContentState
from server_src.content_creation.graph.chains.relevancy_grader_chain import relevance_grader

def validate_title_vs_hints(state: ContentState):
    logger.info('---Validate Title vs HINTS---')

    if not state.user_hints:    # No hints provided, so we consider it relevant by default since hints are optional
        logger.info("No user hints provided; skipping relevance check.")
        return {"title_hints_relevant": True}

    combined_hints = "\n".join(f"- {h}" for h in state.user_hints)

    decision = relevance_grader.invoke(
        {
            "title": state.title,
            "content": combined_hints
        }
    )

    logger.info(f"Relevance decision: {decision}")

    if not decision.relevant:
        return {
            "title_hints_relevant": False,
            "exit_reason": decision.reason
        }

    return {
        "title_hints_relevant": True
    }
from logging_config import get_logger

logger = get_logger("ContentCreationServer")
from server_src.content_creation.graph.state import ContentState
from server_src.content_creation.graph.chains.keyword_generator_chain import keyword_generator

def generate_keywords(state: ContentState):
    """
    Generate high-signal search keywords from the available context.

    This node constructs a prioritized context using:
    1. User-provided hints (highest priority)
    2. Extracted link contents
    3. Title (fallback)

    The combined context is passed to the keyword generation LLM chain.
    The resulting keywords are deduplicated, normalized, and stored
    in the graph state for downstream web search.

    Args:
        state (ContentState): Current graph state containing title,
                              hints, and extracted link content.

    Returns:
        dict:
            - {"search_keywords": List[str]} containing cleaned keywords
    """
    logger.info("--- GENERATE KEYWORDS ---")

    # Build context with clear priority:
    # user_hints > link_contents > title
    context_parts = []

    if state.user_hints:
        logger.info(f"Adding {len(state.user_hints)} user hints to keyword context")
        context_parts.append(
            "USER HINTS:\n" + "\n".join(f"- {h}" for h in state.user_hints)
        )

    if state.link_contents:
        logger.info("Adding extracted link contents to keyword context")
        context_parts.append(
            "LINK CONTENTS:\n" + state.link_contents
        )

    # Fallback: use title alone if no other context is available
    if not context_parts:
        logger.info("No hints or link contents found; falling back to title only")
        context_parts.append(state.title)

    combined_context = "\n\n".join(context_parts)
    logger.info("Combined context prepared for keyword generation")

    # Invoke keyword generation chain
    result = keyword_generator.invoke(
        {
            "title": state.title,
            "context": combined_context
        }
    )

    # Safety: normalize, deduplicate, and clean keywords
    keywords = []
    seen = set()

    for k in result.keywords:
        k = k.strip()
        if k and k.lower() not in seen:
            keywords.append(k)
            seen.add(k.lower())

    logger.info(f"Generated {len(keywords)} keywords: {keywords}")

    return {
        "search_keywords": keywords
    }

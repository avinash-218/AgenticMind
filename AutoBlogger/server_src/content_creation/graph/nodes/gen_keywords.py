from logging_config import get_logger

logger = get_logger("ContentCreationServer")
from server_src.content_creation.graph.state import ContentState
from server_src.content_creation.graph.chains.keyword_generator_chain import keyword_generator

def generate_keywords(state: ContentState):
    logger.info("\n--- Generate Keywords ---")
    # Build context with clear priority:
    # user_hints > link_contents > title
    context_parts = []

    if state.user_hints:
        logger.info(f"Compiling {len(state.user_hints)} user hints into context.")
        context_parts.append(
            "USER HINTS:\n" + "\n".join(f"- {h}" for h in state.user_hints)
        )

    if state.link_contents:
        logger.info("Adding link contents to context.")
        context_parts.append(
            "LINK CONTENTS:\n" + state.link_contents
        )

    if not context_parts:
        context_parts.append(state.title)

    combined_context = "\n\n".join(context_parts)
    logger.info("Combined context for keyword generation.")

    result = keyword_generator.invoke(
        {
            "title": state.title,
            "context": combined_context
        }
    )

    # Safety: ensure unique + trimmed keywords
    keywords = []
    seen = set()
    for k in result.keywords:
        k = k.strip()
        if k and k.lower() not in seen:
            keywords.append(k)
            seen.add(k.lower())

    logger.info(f"Generated keywords: {keywords}")

    return {
        "search_keywords": keywords
    }

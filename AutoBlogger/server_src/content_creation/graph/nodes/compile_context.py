from logging_config import get_logger
logger = get_logger("ContentCreationServer")

from server_src.content_creation.graph.state import ContentState

def compile_context(state: ContentState):
    """
    Assemble a unified textual context from all available information sources.

    This node consolidates user hints, extracted link summaries, and web
    search results into a single, well-structured context block. The
    resulting context is used as the primary input for content generation.

    Priority order:
    1. User-provided hints (highest priority)
    2. Extracted link contents
    3. Web search (Tavily) results

    Args:
        state (ContentState): Current graph state containing intermediate
                              artifacts required for context compilation.

    Returns:
        dict:
            - {"compiled_context": str} on success
            - {"exit_reason": str} if no usable context is available
    """
    logger.info("--- COMPILE CONTEXT ---")

    context_sections = []

    # User hints (highest priority)
    if state.user_hints:
        logger.info(f"Compiling {len(state.user_hints)} user hints into context")
        hints_block = "\n".join(f"- {h}" for h in state.user_hints)
        context_sections.append(
            "### USER HINTS\n" + hints_block
        )

    # Extracted link contents
    if state.link_contents:
        logger.info("Compiling extracted link contents into context")
        context_sections.append(
            "### LINK CONTENTS\n" + state.link_contents
        )

    # Tavily / web search results
    if state.tavily_results:
        logger.info("Compiling web search results into context")
        context_sections.append(
            "### WEB SEARCH RESULTS\n" + state.tavily_results
        )

    # Guard: no context available
    if not context_sections:
        logger.warning("No context sections available; exiting graph early")
        return {
            "exit_reason": "No context available to compile."
        }

    # Join sections with clear visual separators
    compiled_context = "\n\n---\n\n".join(context_sections)

    logger.info("Context compilation completed successfully")

    return {
        "compiled_context": compiled_context
    }

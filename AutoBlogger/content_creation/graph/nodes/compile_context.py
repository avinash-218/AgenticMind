from logging_config import logger
from content_creation.graph.state import ContentState

def compile_context(state: ContentState):
    logger.info('--- COMPILE CONTEXT ---')

    context_sections = []

    # User hints (highest priority)
    if state.user_hints:
        logger.info(f"Compiling {len(state.user_hints)} user hints into context.")
        hints_block = "\n".join(f"- {h}" for h in state.user_hints)
        context_sections.append(
            "### USER HINTS\n" + hints_block
        )

    # Extracted link contents
    if state.link_contents:
        logger.info("Compiling link contents into context.")
        context_sections.append(
            "### LINK CONTENTS\n" + state.link_contents
        )

    # Tavily search results
    if state.tavily_results:
        logger.info("Compiling Tavily search results into context.")
        context_sections.append(
            "### WEB SEARCH RESULTS\n" + state.tavily_results
        )

    if not context_sections:
        logger.info("No context sections available to compile.")
        return {
            "exit_reason": "No context available to compile."
        }

    compiled_context = "\n\n---\n\n".join(context_sections)
    logger.info("Context compilation completed.")

    return {
        "compiled_context": compiled_context
    }
